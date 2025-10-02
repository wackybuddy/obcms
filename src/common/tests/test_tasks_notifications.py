"""Tests for calendar notification Celery tasks."""

from datetime import timedelta
from unittest.mock import patch

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
