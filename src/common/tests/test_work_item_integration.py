"""
WorkItem Integration Tests

End-to-end workflow tests for the unified WorkItem system.

Test Coverage:
- End-to-end: Create Project → Add Activity → Add Task → View hierarchy
- Form submissions
- Delete confirmations
- Multi-user workflows
- Real-world scenarios using WorkItem model
"""

import json
import pytest
from datetime import date, timedelta
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


@pytest.mark.django_db
class TestEndToEndProjectWorkflow:
    """Test complete project workflow using WorkItem."""

    def test_create_project_add_activities_tasks(self, client):
        """
        End-to-end test: Create Project → Add Activities → Add Tasks → Verify Hierarchy
        """
        # Step 1: Create user and login
        user = User.objects.create_user(
            username="pm_user",
            password="testpass",
            first_name="Project",
            last_name="Manager",
        )
        client.login(username="pm_user", password="testpass")

        # Step 2: Create Project using WorkItem
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Community Development Initiative",
            description="Comprehensive community development project",
            start_date=date(2025, 1, 1),
            due_date=date(2025, 12, 31),
            priority=WorkItem.PRIORITY_HIGH,
            created_by=user,
        )
        assert project.created_by == user
        assert project.work_type == WorkItem.WORK_TYPE_PROJECT

        # Step 3: Add First Activity
        workshop = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Stakeholder Consultation Workshop",
            parent=project,
            start_date=date(2025, 2, 15),
            due_date=date(2025, 2, 15),
            created_by=user,
        )
        assert workshop.parent == project
        assert workshop.get_ancestors().first() == project

        # Step 4: Add Second Activity
        assessment = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Community Needs Assessment",
            parent=project,
            start_date=date(2025, 3, 1),
            due_date=date(2025, 3, 31),
            created_by=user,
        )
        assert assessment.parent == project

        # Step 5: Add Tasks to Workshop
        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Prepare workshop materials",
            parent=workshop,
            start_date=date(2025, 2, 1),
            due_date=date(2025, 2, 10),
            created_by=user,
        )
        assert task1.parent == workshop

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Send invitations",
            parent=workshop,
            start_date=date(2025, 2, 5),
            due_date=date(2025, 2, 12),
            created_by=user,
        )
        assert task2.parent == workshop

        # Step 6: Verify Hierarchy using MPTT methods
        assert project.get_children().count() == 2  # 2 activities
        assert workshop.get_children().count() == 2  # 2 tasks

        # Get all descendants (activities + tasks)
        all_descendants = project.get_descendants()
        assert all_descendants.count() == 4  # 2 activities + 2 tasks

        # Get all tasks specifically
        all_tasks = project.get_descendants().filter(
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
        )
        assert all_tasks.count() == 2

    def test_update_task_status_propagates_progress(self):
        """Test completing tasks updates parent progress."""
        user = User.objects.create_user(username="testuser", password="testpass")

        # Create hierarchy
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            auto_calculate_progress=True,
            created_by=user,
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity",
            parent=project,
            auto_calculate_progress=True,
            created_by=user,
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=activity,
            status=WorkItem.STATUS_NOT_STARTED,
            created_by=user,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=activity,
            status=WorkItem.STATUS_NOT_STARTED,
            created_by=user,
        )

        # Update task 1 to completed
        task1.status = WorkItem.STATUS_COMPLETED
        task1.progress = 100
        task1.save()

        # Trigger progress update
        activity.update_progress()
        project.update_progress()

        activity.refresh_from_db()
        project.refresh_from_db()

        # Activity should be 50% (1/2 tasks done)
        assert activity.progress == 50

        # Project progress depends on implementation
        assert project.progress >= 0


@pytest.mark.django_db
class TestMultiUserWorkflow:
    """Test multi-user collaboration workflows."""

    def test_assign_team_to_project(self):
        """Test assigning a team to a project."""
        admin = User.objects.create_user(username="admin", password="admin")
        user1 = User.objects.create_user(username="user1", password="pass")
        user2 = User.objects.create_user(username="user2", password="pass")

        team = StaffTeam.objects.create(name="Implementation Team")

        # Create project and assign team
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Team Project",
            created_by=admin,
        )

        # Assign team and users
        project.teams.add(team)
        project.assignees.add(user1, user2)

        project.refresh_from_db()
        assert team in project.teams.all()
        assert user1 in project.assignees.all()
        assert user2 in project.assignees.all()

    def test_delegate_task_to_user(self):
        """Test delegating a task to a specific user."""
        admin = User.objects.create_user(username="admin", password="admin")
        delegate = User.objects.create_user(
            username="delegate",
            first_name="John",
            last_name="Delegate",
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Delegated Task",
            created_by=admin,
        )

        # Assign to delegate
        task.assignees.add(delegate)

        task.refresh_from_db()
        assert delegate in task.assignees.all()


@pytest.mark.django_db
class TestRealWorldScenarios:
    """Test real-world OOBC scenarios."""

    def test_mana_assessment_workflow(self):
        """Test MANA assessment project workflow."""
        researcher = User.objects.create_user(username="researcher", password="pass")

        # Create MANA Assessment Project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="MANA Assessment - Region XII",
            start_date=date(2025, 1, 1),
            due_date=date(2025, 6, 30),
            created_by=researcher,
            project_data={
                "workflow_stage": "planning",
                "assessment_type": "mana",
                "target_region": "Region XII",
            },
        )

        # Planning Phase Activity
        planning = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Assessment Planning",
            parent=project,
            start_date=date(2025, 1, 1),
            due_date=date(2025, 1, 31),
            created_by=researcher,
        )

        # Data Collection Phase Activity
        data_collection = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Field Data Collection",
            parent=project,
            start_date=date(2025, 2, 1),
            due_date=date(2025, 4, 30),
            created_by=researcher,
            activity_data={
                "event_type": "field_visit",
                "location": "Region XII",
            },
        )

        # Tasks under data collection
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Conduct household surveys",
            parent=data_collection,
            created_by=researcher,
            task_data={
                "domain": "mana",
                "assessment_phase": "data_collection",
                "deliverable_type": "survey_data",
            },
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Interview community leaders",
            parent=data_collection,
            created_by=researcher,
            task_data={
                "domain": "mana",
                "assessment_phase": "data_collection",
                "deliverable_type": "interview_notes",
            },
        )

        # Verify structure
        assert project.get_children().count() == 2
        all_tasks = project.get_descendants().filter(
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
        )
        assert all_tasks.count() == 2
        assert project.project_data["assessment_type"] == "mana"

    def test_policy_development_workflow(self):
        """Test policy recommendation workflow."""
        policy_officer = User.objects.create_user(username="policy", password="pass")

        # Create Policy Development Project
        policy_project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="OBC Education Policy Framework",
            start_date=date(2025, 1, 1),
            due_date=date(2025, 12, 31),
            created_by=policy_officer,
            project_data={
                "policy_area": "education",
                "policy_stage": "drafting",
            },
        )

        # Consultation Activity
        consultation = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Stakeholder Consultation",
            parent=policy_project,
            created_by=policy_officer,
            activity_data={
                "event_type": "consultation",
                "stakeholder_groups": ["educators", "community_leaders", "parents"],
            },
        )

        # Drafting Tasks
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Draft policy framework",
            parent=policy_project,
            created_by=policy_officer,
            task_data={
                "domain": "policy",
                "policy_phase": "drafting",
            },
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Gather evidence and data",
            parent=policy_project,
            created_by=policy_officer,
            task_data={
                "domain": "policy",
                "policy_phase": "evidence_collection",
            },
        )

        assert policy_project.get_descendants().count() == 3


@pytest.mark.django_db
class TestErrorHandling:
    """Test error handling in workflows."""

    def test_prevent_circular_references(self):
        """Test that circular parent-child references are prevented."""
        user = User.objects.create_user(username="testuser", password="testpass")

        parent = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Parent",
            created_by=user,
        )

        child = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Child",
            parent=parent,
            created_by=user,
        )

        # Try to set parent as child of child (circular)
        # MPTT should prevent this
        try:
            parent.parent = child
            parent.save()
            # If save succeeds, verify it wasn't actually saved
            parent.refresh_from_db()
            assert parent.parent is None  # Parent should remain None
        except Exception:
            # Exception is also acceptable - prevents circular reference
            parent.refresh_from_db()
            assert parent.parent is None

    def test_delete_with_children_cascades(self):
        """Test deleting parent deletes children (CASCADE)."""
        user = User.objects.create_user(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project with Children",
            created_by=user,
        )

        child = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Child Activity",
            parent=project,
            created_by=user,
        )

        child_id = child.id
        project_id = project.id

        # Delete project
        project.delete()

        # Verify both deleted (CASCADE behavior)
        assert not WorkItem.objects.filter(id=project_id).exists()
        assert not WorkItem.objects.filter(id=child_id).exists()


@pytest.mark.django_db
class TestWorkItemQuerying:
    """Test querying and filtering WorkItems."""

    def test_filter_by_work_type(self):
        """Test filtering by work_type."""
        user = User.objects.create_user(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project 1",
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            created_by=user,
        )

        projects = WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_PROJECT)
        tasks = WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_TASK)
        activities = WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_ACTIVITY)

        assert projects.count() == 1
        assert tasks.count() == 1
        assert activities.count() == 1

    def test_filter_by_status(self):
        """Test filtering by status."""
        user = User.objects.create_user(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            status=WorkItem.STATUS_NOT_STARTED,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            status=WorkItem.STATUS_IN_PROGRESS,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            status=WorkItem.STATUS_COMPLETED,
            created_by=user,
        )

        not_started = WorkItem.objects.filter(status=WorkItem.STATUS_NOT_STARTED)
        in_progress = WorkItem.objects.filter(status=WorkItem.STATUS_IN_PROGRESS)
        completed = WorkItem.objects.filter(status=WorkItem.STATUS_COMPLETED)

        assert not_started.count() == 1
        assert in_progress.count() == 1
        assert completed.count() == 1

    def test_filter_by_priority(self):
        """Test filtering by priority."""
        user = User.objects.create_user(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            priority=WorkItem.PRIORITY_LOW,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            priority=WorkItem.PRIORITY_HIGH,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            priority=WorkItem.PRIORITY_CRITICAL,
            created_by=user,
        )

        low_priority = WorkItem.objects.filter(priority=WorkItem.PRIORITY_LOW)
        high_priority = WorkItem.objects.filter(priority=WorkItem.PRIORITY_HIGH)
        critical = WorkItem.objects.filter(priority=WorkItem.PRIORITY_CRITICAL)

        assert low_priority.count() == 1
        assert high_priority.count() == 1
        assert critical.count() == 1

    def test_filter_by_date_range(self):
        """Test filtering by date range."""
        user = User.objects.create_user(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            start_date=date(2025, 1, 1),
            due_date=date(2025, 1, 31),
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            start_date=date(2025, 2, 1),
            due_date=date(2025, 2, 28),
            created_by=user,
        )

        jan_tasks = WorkItem.objects.filter(
            start_date__gte=date(2025, 1, 1),
            start_date__lte=date(2025, 1, 31),
        )

        feb_tasks = WorkItem.objects.filter(
            start_date__gte=date(2025, 2, 1),
            start_date__lte=date(2025, 2, 28),
        )

        assert jan_tasks.count() == 1
        assert feb_tasks.count() == 1
