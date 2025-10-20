"""Minimal calendar test to verify WorkItem calendar integration."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from common.models import WorkItem
from common.services.calendar import build_calendar_payload

User = get_user_model()


class MinimalCalendarTest(TestCase):
    """Minimal test to verify calendar system works."""

    def test_workitem_appears_in_calendar(self):
        """Verify that a WorkItem appears in the calendar payload."""
        user = User.objects.create_user(
            username="test_user", email="test@test.com", password="changeme"
        )

        start_date = timezone.now().date() + timedelta(days=1)

        # Create WorkItem
        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Test Activity",
            description="Test description",
            start_date=start_date,
            start_time=timezone.now().time().replace(microsecond=0),
            due_date=start_date,
            status=WorkItem.STATUS_NOT_STARTED,
            created_by=user,
        )

        # Build calendar payload
        payload = build_calendar_payload()

        # Verify work item appears
        entry_ids = {entry["id"] for entry in payload["entries"]}
        expected_id = f"coordination-event-{work_item.pk}"

        self.assertIn(expected_id, entry_ids, f"WorkItem {work_item.pk} not found in calendar. Found: {entry_ids}")
