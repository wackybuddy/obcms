"""Tests for the OOBC staff management dashboard."""

from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from common.constants import STAFF_TEAM_DEFINITIONS
from common.models import StaffTask, StaffTeam, StaffTeamMembership, User


class StaffManagementViewTests(TestCase):
    """Validate staff management flows for profiles, tasks, and teams."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_superuser=True,
            is_approved=True,
        )
        self.staff_member = User.objects.create_user(
            username="staff",
            password="pass1234",
            user_type="oobc_staff",
            is_approved=True,
        )
        self.url = reverse("common:staff_management")
        self.task_create_url = reverse("common:staff_task_create")
        self.team_assign_url = reverse("common:staff_team_assign")
        self.team_manage_url = reverse("common:staff_team_manage")
        self.client.force_login(self.admin)

    def test_default_teams_are_seeded(self):
        """The dashboard seeds the configured default teams when missing."""

        StaffTeam.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(
            StaffTeam.objects.count(), len(STAFF_TEAM_DEFINITIONS)
        )

    def test_create_task_and_auto_membership(self):
        """Submitting the task form creates a task and links assignee to the team."""

        self.client.get(self.task_create_url)  # ensure default teams exist
        team = StaffTeam.objects.first()
        post_data = {
            "title": "Draft provincial coordination brief",
            "team": str(team.id),
            "assignee": str(self.staff_member.id),
            "priority": "high",
            "status": "in_progress",
            "impact": "Aligns inter-agency inputs ahead of the coordination call.",
            "description": "Collect partner notes and draft talking points.",
            "start_date": timezone.now().date().isoformat(),
            "due_date": (timezone.now().date() + timedelta(days=3)).isoformat(),
            "progress": "40",
        }

        response = self.client.post(self.task_create_url, post_data)

        if response.status_code == 200:
            form_errors = response.context["form"].errors.as_json()
            self.fail(f"Task form validation errors: {form_errors}")
        self.assertEqual(response.status_code, 302)
        task = StaffTask.objects.get(title="Draft provincial coordination brief")
        self.assertEqual(task.team, team)
        self.assertEqual(task.assignee, self.staff_member)
        self.assertEqual(task.created_by, self.admin)
        self.assertEqual(task.status, StaffTask.STATUS_IN_PROGRESS)
        self.assertTrue(
            StaffTeamMembership.objects.filter(
                team=team, user=self.staff_member, is_active=True
            ).exists()
        )

    def test_update_task_status(self):
        """The lightweight status form updates task progress and status."""

        team = StaffTeam.objects.create(name="Research Unit")
        task = StaffTask.objects.create(
            title="Compile field notes",
            team=team,
            assignee=self.staff_member,
            created_by=self.admin,
        )

        post_data = {
            "form_name": "task_status",
            "task_id": str(task.id),
            "status": "completed",
            "progress": "100",
        }

        response = self.client.post(self.url, post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, StaffTask.STATUS_COMPLETED)
        self.assertEqual(task.progress, 100)
        self.assertIsNotNone(task.completed_at)

    def test_assign_staff_to_team_view(self):
        """Submission on the team assignment page activates membership."""

        self.client.get(self.team_assign_url)
        team = StaffTeam.objects.first()
        post_data = {
            "team": str(team.id),
            "user": str(self.staff_member.id),
            "role": StaffTeamMembership.ROLE_COORDINATOR,
            "is_active": "on",
            "notes": "Oversees inter-agency updates.",
        }

        response = self.client.post(self.team_assign_url, post_data)

        if response.status_code == 200:
            errors = response.context["form"].errors.as_json()
            self.fail(f"Assignment form errors: {errors}")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            StaffTeamMembership.objects.filter(
                team=team, user=self.staff_member, role=StaffTeamMembership.ROLE_COORDINATOR
            ).exists()
        )

    def test_manage_team_create_view(self):
        """Team management page persists new teams."""

        response = self.client.post(
            self.team_manage_url,
            {
                "name": "Innovation Unit",
                "description": "Drives experimentation across programmes.",
                "mission": "Surface prototypes into scalable interventions.",
                "focus_areas": "Pilot design\nKnowledge exchange",
                "is_active": "on",
            },
        )

        if response.status_code == 200:
            errors = response.context["form"].errors.as_json()
            self.fail(f"Team form errors: {errors}")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(StaffTeam.objects.filter(name="Innovation Unit").exists())

    def test_seed_staff_workflows_command(self):
        """Management command seeds demo tasks and memberships."""

        StaffTeam.objects.all().delete()
        StaffTask.objects.all().delete()

        call_command("seed_staff_workflows")

        self.assertGreater(StaffTeam.objects.count(), 0)
        self.assertGreater(StaffTask.objects.count(), 0)
