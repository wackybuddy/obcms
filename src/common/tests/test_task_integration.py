"""
Task Integration Tests for WorkItem

Integration tests for task management workflows using the unified WorkItem model.

Test Coverage:
- Task creation and management workflows
- Task assignment and team collaboration
- Task status transitions
- Task querying and filtering
- Task analytics and reporting
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


@pytest.mark.django_db
class TestTaskCreationWorkflow:
    """Test task creation workflows."""

    def test_create_standalone_task(self):
        """Test creating a standalone task."""
        user = User.objects.create_user(
            username="task_creator",
            password="pass1234",
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Review documentation",
            description="Review and update project documentation",
            status=WorkItem.STATUS_NOT_STARTED,
            priority=WorkItem.PRIORITY_HIGH,
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
            created_by=user,
        )

        assert task.work_type == WorkItem.WORK_TYPE_TASK
        assert task.status == WorkItem.STATUS_NOT_STARTED
        assert task.priority == WorkItem.PRIORITY_HIGH
        assert task.created_by == user

    def test_create_task_under_project(self):
        """Test creating a task under a project."""
        user = User.objects.create_user(username="pm", password="pass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Software Development Project",
            created_by=user,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Setup development environment",
            parent=project,
            priority=WorkItem.PRIORITY_HIGH,
            created_by=user,
        )

        assert task.parent == project
        assert task.get_ancestors().first() == project
        assert project.get_children().filter(id=task.id).exists()

    def test_create_task_under_activity(self):
        """Test creating a task under an activity."""
        user = User.objects.create_user(username="facilitator", password="pass")

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Workshop Preparation",
            created_by=user,
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Prepare materials",
            parent=activity,
            created_by=user,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Send invitations",
            parent=activity,
            created_by=user,
        )

        assert activity.get_children().count() == 2
        assert task1 in activity.get_children()
        assert task2 in activity.get_children()

    def test_create_subtask(self):
        """Test creating a subtask under a task."""
        user = User.objects.create_user(username="user", password="pass")

        parent_task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Implement feature X",
            created_by=user,
        )

        subtask1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title="Write unit tests",
            parent=parent_task,
            created_by=user,
        )

        subtask2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title="Update documentation",
            parent=parent_task,
            created_by=user,
        )

        assert parent_task.get_children().count() == 2
        assert subtask1.work_type == WorkItem.WORK_TYPE_SUBTASK
        assert subtask2.work_type == WorkItem.WORK_TYPE_SUBTASK


@pytest.mark.django_db
class TestTaskAssignment:
    """Test task assignment workflows."""

    def test_assign_task_to_user(self):
        """Test assigning a task to a user."""
        creator = User.objects.create_user(username="creator", password="pass")
        assignee = User.objects.create_user(
            username="assignee",
            first_name="John",
            last_name="Doe",
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Conduct user research",
            created_by=creator,
        )

        task.assignees.add(assignee)

        assert assignee in task.assignees.all()
        assert task in assignee.assigned_work_items.all()

    def test_assign_task_to_team(self):
        """Test assigning a task to a team."""
        user = User.objects.create_user(username="user", password="pass")
        team = StaffTeam.objects.create(name="Development Team", is_active=True)

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Code review",
            created_by=user,
        )

        task.teams.add(team)

        assert team in task.teams.all()
        assert task in team.work_items.all()

    def test_assign_task_to_multiple_users(self):
        """Test assigning a task to multiple users."""
        creator = User.objects.create_user(username="creator", password="pass")
        user1 = User.objects.create_user(username="user1", password="pass")
        user2 = User.objects.create_user(username="user2", password="pass")
        user3 = User.objects.create_user(username="user3", password="pass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Collaborative task",
            created_by=creator,
        )

        task.assignees.add(user1, user2, user3)

        assert task.assignees.count() == 3
        assert user1 in task.assignees.all()
        assert user2 in task.assignees.all()
        assert user3 in task.assignees.all()


@pytest.mark.django_db
class TestTaskStatusTransitions:
    """Test task status transition workflows."""

    def test_task_status_transitions(self):
        """Test transitioning task through different statuses."""
        user = User.objects.create_user(username="user", password="pass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Status transition test",
            status=WorkItem.STATUS_NOT_STARTED,
            created_by=user,
        )

        # Not started -> In progress
        task.status = WorkItem.STATUS_IN_PROGRESS
        task.progress = 30
        task.save()
        task.refresh_from_db()
        assert task.status == WorkItem.STATUS_IN_PROGRESS
        assert task.progress == 30

        # In progress -> At risk
        task.status = WorkItem.STATUS_AT_RISK
        task.progress = 45
        task.save()
        task.refresh_from_db()
        assert task.status == WorkItem.STATUS_AT_RISK

        # At risk -> Completed
        task.status = WorkItem.STATUS_COMPLETED
        task.progress = 100
        task.completed_at = timezone.now()
        task.save()
        task.refresh_from_db()
        assert task.status == WorkItem.STATUS_COMPLETED
        assert task.progress == 100
        assert task.completed_at is not None

    def test_task_can_be_blocked(self):
        """Test marking a task as blocked."""
        user = User.objects.create_user(username="user", password="pass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Blocked task test",
            status=WorkItem.STATUS_IN_PROGRESS,
            created_by=user,
        )

        task.status = WorkItem.STATUS_BLOCKED
        task.save()
        task.refresh_from_db()
        assert task.status == WorkItem.STATUS_BLOCKED

    def test_task_can_be_cancelled(self):
        """Test cancelling a task."""
        user = User.objects.create_user(username="user", password="pass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Cancelled task test",
            status=WorkItem.STATUS_IN_PROGRESS,
            created_by=user,
        )

        task.status = WorkItem.STATUS_CANCELLED
        task.save()
        task.refresh_from_db()
        assert task.status == WorkItem.STATUS_CANCELLED


@pytest.mark.django_db
class TestTaskQuerying:
    """Test querying and filtering tasks."""

    def test_query_tasks_by_status(self):
        """Test querying tasks by status."""
        user = User.objects.create_user(username="user", password="pass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Not started task",
            status=WorkItem.STATUS_NOT_STARTED,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="In progress task",
            status=WorkItem.STATUS_IN_PROGRESS,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Completed task",
            status=WorkItem.STATUS_COMPLETED,
            created_by=user,
        )

        not_started = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            status=WorkItem.STATUS_NOT_STARTED,
        )
        in_progress = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            status=WorkItem.STATUS_IN_PROGRESS,
        )
        completed = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            status=WorkItem.STATUS_COMPLETED,
        )

        assert not_started.count() == 1
        assert in_progress.count() == 1
        assert completed.count() == 1

    def test_query_tasks_by_priority(self):
        """Test querying tasks by priority."""
        user = User.objects.create_user(username="user", password="pass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Low priority",
            priority=WorkItem.PRIORITY_LOW,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="High priority",
            priority=WorkItem.PRIORITY_HIGH,
            created_by=user,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Critical priority",
            priority=WorkItem.PRIORITY_CRITICAL,
            created_by=user,
        )

        high_priority_tasks = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            priority__in=[WorkItem.PRIORITY_HIGH, WorkItem.PRIORITY_URGENT, WorkItem.PRIORITY_CRITICAL],
        )

        assert high_priority_tasks.count() == 2

    def test_query_tasks_by_assignee(self):
        """Test querying tasks by assignee."""
        creator = User.objects.create_user(username="creator", password="pass")
        user1 = User.objects.create_user(username="user1", password="pass")
        user2 = User.objects.create_user(username="user2", password="pass")

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task for user1",
            created_by=creator,
        )
        task1.assignees.add(user1)

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task for user2",
            created_by=creator,
        )
        task2.assignees.add(user2)

        task3 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task for both",
            created_by=creator,
        )
        task3.assignees.add(user1, user2)

        user1_tasks = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            assignees=user1,
        )
        user2_tasks = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            assignees=user2,
        )

        assert user1_tasks.count() == 2  # task1 and task3
        assert user2_tasks.count() == 2  # task2 and task3

    def test_query_overdue_tasks(self):
        """Test querying overdue tasks."""
        user = User.objects.create_user(username="user", password="pass")

        # Overdue task
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Overdue task",
            due_date=date.today() - timedelta(days=5),
            status=WorkItem.STATUS_IN_PROGRESS,
            created_by=user,
        )

        # Not overdue task
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Future task",
            due_date=date.today() + timedelta(days=5),
            status=WorkItem.STATUS_IN_PROGRESS,
            created_by=user,
        )

        # Completed task (not overdue)
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Completed late",
            due_date=date.today() - timedelta(days=3),
            status=WorkItem.STATUS_COMPLETED,
            created_by=user,
        )

        overdue_tasks = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            due_date__lt=date.today(),
            status__in=[
                WorkItem.STATUS_NOT_STARTED,
                WorkItem.STATUS_IN_PROGRESS,
                WorkItem.STATUS_AT_RISK,
                WorkItem.STATUS_BLOCKED,
            ],
        )

        assert overdue_tasks.count() == 1


@pytest.mark.django_db
class TestTaskAnalytics:
    """Test task analytics and reporting."""

    def test_task_completion_statistics(self):
        """Test calculating task completion statistics."""
        user = User.objects.create_user(username="user", password="pass")
        team = StaffTeam.objects.create(name="Analytics Team")

        # Create tasks with different statuses
        for i in range(5):
            task = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
                status=WorkItem.STATUS_COMPLETED,
                created_by=user,
            )
            task.teams.add(team)

        for i in range(3):
            task = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task in progress {i}",
                status=WorkItem.STATUS_IN_PROGRESS,
                created_by=user,
            )
            task.teams.add(team)

        for i in range(2):
            task = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task not started {i}",
                status=WorkItem.STATUS_NOT_STARTED,
                created_by=user,
            )
            task.teams.add(team)

        # Calculate statistics
        team_tasks = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            teams=team,
        )
        total_tasks = team_tasks.count()
        completed_tasks = team_tasks.filter(status=WorkItem.STATUS_COMPLETED).count()
        in_progress_tasks = team_tasks.filter(status=WorkItem.STATUS_IN_PROGRESS).count()
        not_started_tasks = team_tasks.filter(status=WorkItem.STATUS_NOT_STARTED).count()

        assert total_tasks == 10
        assert completed_tasks == 5
        assert in_progress_tasks == 3
        assert not_started_tasks == 2

        completion_rate = (completed_tasks / total_tasks) * 100
        assert completion_rate == 50.0


@pytest.mark.django_db
class TestTaskDataFields:
    """Test task-specific JSON data fields."""

    def test_task_with_domain_data(self):
        """Test storing domain-specific data in task_data."""
        user = User.objects.create_user(username="user", password="pass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="MANA assessment task",
            created_by=user,
            task_data={
                "domain": "mana",
                "assessment_phase": "data_collection",
                "deliverable_type": "survey_data",
                "estimated_hours": 8,
            },
        )

        assert task.task_data["domain"] == "mana"
        assert task.task_data["assessment_phase"] == "data_collection"
        assert task.task_data["estimated_hours"] == 8

    def test_task_with_custom_fields(self):
        """Test storing custom fields in task_data."""
        user = User.objects.create_user(username="user", password="pass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Custom task",
            created_by=user,
            task_data={
                "custom_field_1": "value1",
                "custom_field_2": 123,
                "custom_field_3": ["item1", "item2", "item3"],
            },
        )

        assert task.task_data["custom_field_1"] == "value1"
        assert task.task_data["custom_field_2"] == 123
        assert len(task.task_data["custom_field_3"]) == 3


@pytest.mark.django_db
class TestTaskHierarchyIntegration:
    """Test task hierarchy integration with projects and activities."""

    def test_complete_task_hierarchy(self):
        """Test creating complete task hierarchy."""
        user = User.objects.create_user(username="pm", password="pass")

        # Project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Software Release",
            created_by=user,
        )

        # Activities under project
        planning = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Release Planning",
            parent=project,
            created_by=user,
        )

        development = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Development Phase",
            parent=project,
            created_by=user,
        )

        # Tasks under activities
        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Define release scope",
            parent=planning,
            created_by=user,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Implement feature A",
            parent=development,
            created_by=user,
        )

        # Subtasks under tasks
        subtask1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title="Write unit tests",
            parent=task2,
            created_by=user,
        )

        subtask2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title="Code review",
            parent=task2,
            created_by=user,
        )

        # Verify hierarchy - refresh objects to ensure tree is updated
        project.refresh_from_db()
        planning.refresh_from_db()
        development.refresh_from_db()
        task2.refresh_from_db()

        # Count all descendants and verify structure
        descendants = list(project.get_descendants())
        assert len(descendants) == 6  # 2 activities + 2 tasks + 2 subtasks
        assert planning.get_children().count() == 1  # 1 task
        assert development.get_children().count() == 1  # 1 task
        assert task2.get_children().count() == 2  # 2 subtasks

        # Verify all descendants of project
        all_tasks = project.get_descendants().filter(
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
        )
        assert all_tasks.count() == 4  # 2 tasks + 2 subtasks
