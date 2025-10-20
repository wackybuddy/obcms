"""Tests for calendar notification Celery tasks.

Component tests for the notification messaging interface:
- Message payload validation
- Delivery method handling (email)
- Notification scheduling and retry logic
- Error handling for failed deliveries
"""

import json
import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from common.models import CalendarNotification
from common.tasks import (
    send_calendar_notifications_batch,
    send_single_calendar_notification,
)

User = get_user_model()


@pytest.mark.component
class CalendarNotificationTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="calendar_user",
            email="calendar@example.com",
            password="pass1234",
        )

    def create_notification(self, **overrides):
        defaults = {
            "recipient": self.user,
            "notification_type": CalendarNotification.NOTIFICATION_REMINDER,
            "delivery_method": CalendarNotification.DELIVERY_EMAIL,
            "scheduled_for": timezone.now() - timedelta(minutes=1),
        }
        defaults.update(overrides)
        return CalendarNotification.objects.create(**defaults)

    @patch("common.tasks.group")
    def test_batch_dispatches_group(self, mock_group):
        notification = self.create_notification()

        result = send_calendar_notifications_batch(batch_size=10)

        self.assertEqual(result["queued"], 1)
        mock_group.assert_called_once()
        mock_group.return_value.apply_async.assert_called_once()

        notification.refresh_from_db()
        self.assertGreater(notification.scheduled_for, timezone.now())

    @patch("common.tasks.send_mail")
    def test_send_single_success(self, mock_send_mail):
        notification = self.create_notification()

        send_single_calendar_notification(notification.id)

        mock_send_mail.assert_called_once()
        notification.refresh_from_db()
        self.assertEqual(notification.status, CalendarNotification.STATUS_SENT)
        self.assertIsNotNone(notification.sent_at)
        self.assertEqual(len(mail.outbox), 0)

    @patch("common.tasks.send_mail", side_effect=RuntimeError("Mail error"))
    def test_send_single_records_failure(self, mock_send_mail):
        notification = self.create_notification()

        with self.assertRaises(RuntimeError):
            send_single_calendar_notification(notification.id)

        notification.refresh_from_db()
        self.assertEqual(notification.status, CalendarNotification.STATUS_FAILED)
        self.assertTrue(notification.error_message)

    def test_notification_payload_validation(self):
        """Test that notification payloads are correctly validated."""
        notification = self.create_notification(
            notification_type=CalendarNotification.NOTIFICATION_REMINDER,
            delivery_method=CalendarNotification.DELIVERY_EMAIL,
        )

        # Verify required fields are present
        self.assertIsNotNone(notification.recipient)
        self.assertEqual(notification.recipient.email, "calendar@example.com")
        self.assertIsNotNone(notification.notification_type)
        self.assertIsNotNone(notification.delivery_method)
        self.assertIsNotNone(notification.scheduled_for)

    def test_notification_delivery_method_email(self):
        """Test email delivery method is properly set."""
        notification = self.create_notification(
            delivery_method=CalendarNotification.DELIVERY_EMAIL
        )
        self.assertEqual(notification.delivery_method, CalendarNotification.DELIVERY_EMAIL)

    def test_notification_scheduling_reschedules_on_batch(self):
        """Test that scheduled_for is updated after batch processing."""
        now = timezone.now()
        notification = self.create_notification(scheduled_for=now - timedelta(minutes=5))

        with patch("common.tasks.group"):
            send_calendar_notifications_batch(batch_size=10)

        notification.refresh_from_db()
        # Verify scheduled_for moved to future (reschedule occurred)
        self.assertGreater(notification.scheduled_for, now)

    @patch("common.tasks.send_mail")
    def test_notification_marks_sent_timestamp(self, mock_send_mail):
        """Test that sent_at timestamp is recorded on successful send."""
        notification = self.create_notification()
        before_send = timezone.now()

        send_single_calendar_notification(notification.id)

        notification.refresh_from_db()
        self.assertIsNotNone(notification.sent_at)
        self.assertGreaterEqual(notification.sent_at, before_send)

    def test_multiple_notifications_for_same_user(self):
        """Test handling multiple notifications for the same user."""
        notif1 = self.create_notification(
            notification_type=CalendarNotification.NOTIFICATION_REMINDER
        )
        notif2 = self.create_notification(
            notification_type=CalendarNotification.NOTIFICATION_ALERT,
            scheduled_for=timezone.now() - timedelta(minutes=2),
        )

        with patch("common.tasks.group") as mock_group:
            result = send_calendar_notifications_batch(batch_size=10)

        # Both should be queued
        self.assertEqual(result["queued"], 2)

    def test_notification_status_transitions(self):
        """Test notification status transitions through delivery lifecycle."""
        notification = self.create_notification()

        # Initial status should be pending
        initial_status = notification.status
        self.assertIn(initial_status, [CalendarNotification.STATUS_PENDING])

        # After successful send, status should be SENT
        with patch("common.tasks.send_mail"):
            send_single_calendar_notification(notification.id)

        notification.refresh_from_db()
        self.assertEqual(notification.status, CalendarNotification.STATUS_SENT)
