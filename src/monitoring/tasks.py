"""Celery tasks for Monitoring & Evaluation background jobs."""

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from common.models import StaffTask

from .models import MonitoringEntryWorkflowStage


@shared_task(name="monitoring.send_workflow_deadline_reminders")
def send_workflow_deadline_reminders():
    """
    Send reminders for upcoming workflow stage deadlines.

    Runs daily to notify stakeholders of:
    - Deadlines in 3 days
    - Deadlines in 7 days
    - Overdue stages
    """
    today = timezone.now().date()
    three_days = today + timedelta(days=3)
    seven_days = today + timedelta(days=7)

    # Find stages approaching deadline
    upcoming_3_days = MonitoringEntryWorkflowStage.objects.filter(
        due_date=three_days,
        status__in=[
            MonitoringEntryWorkflowStage.STATUS_NOT_STARTED,
            MonitoringEntryWorkflowStage.STATUS_IN_PROGRESS,
        ],
    ).select_related("entry", "owner_team", "owner_organization")

    upcoming_7_days = MonitoringEntryWorkflowStage.objects.filter(
        due_date=seven_days,
        status__in=[
            MonitoringEntryWorkflowStage.STATUS_NOT_STARTED,
            MonitoringEntryWorkflowStage.STATUS_IN_PROGRESS,
        ],
    ).select_related("entry", "owner_team", "owner_organization")

    # Find overdue stages
    overdue_stages = MonitoringEntryWorkflowStage.objects.filter(
        due_date__lt=today,
        status__in=[
            MonitoringEntryWorkflowStage.STATUS_NOT_STARTED,
            MonitoringEntryWorkflowStage.STATUS_IN_PROGRESS,
        ],
    ).select_related("entry", "owner_team", "owner_organization")

    reminder_count = 0

    # Process 3-day reminders
    for stage in upcoming_3_days:
        _send_workflow_reminder(
            stage,
            urgency="high",
            message=f"Deadline in 3 days: {stage.get_stage_display()} for {stage.entry.title}",
        )
        reminder_count += 1

    # Process 7-day reminders
    for stage in upcoming_7_days:
        _send_workflow_reminder(
            stage,
            urgency="medium",
            message=f"Deadline in 7 days: {stage.get_stage_display()} for {stage.entry.title}",
        )
        reminder_count += 1

    # Process overdue reminders
    for stage in overdue_stages:
        days_overdue = (today - stage.due_date).days
        _send_workflow_reminder(
            stage,
            urgency="critical",
            message=f"OVERDUE ({days_overdue} days): {stage.get_stage_display()} for {stage.entry.title}",
        )
        reminder_count += 1

    return {
        "status": "completed",
        "reminders_sent": reminder_count,
        "three_day_count": upcoming_3_days.count(),
        "seven_day_count": upcoming_7_days.count(),
        "overdue_count": overdue_stages.count(),
    }


@shared_task(name="monitoring.send_task_assignment_reminders")
def send_task_assignment_reminders():
    """
    Send reminders for task assignments.

    Runs daily to notify assignees of:
    - Tasks due in 2 days
    - Tasks due in 5 days
    - Overdue tasks
    """
    today = timezone.now().date()
    two_days = today + timedelta(days=2)
    five_days = today + timedelta(days=5)

    monitoring_statuses = [
        StaffTask.STATUS_NOT_STARTED,
        StaffTask.STATUS_IN_PROGRESS,
        StaffTask.STATUS_AT_RISK,
    ]

    base_queryset = (
        StaffTask.objects.filter(
            domain=StaffTask.DOMAIN_MONITORING,
            related_ppa__isnull=False,
            due_date__isnull=False,
        )
        .select_related("related_ppa", "created_by")
        .prefetch_related("assignees")
    )

    upcoming_2_days = base_queryset.filter(
        due_date=two_days,
        status__in=monitoring_statuses,
    )

    upcoming_5_days = base_queryset.filter(
        due_date=five_days,
        status__in=monitoring_statuses,
    )

    overdue_tasks = base_queryset.filter(
        due_date__lt=today,
        status__in=monitoring_statuses,
    )

    reminder_count = 0

    # Process 2-day reminders
    for task in upcoming_2_days:
        _send_task_reminder(
            task,
            urgency="high",
            message=f"Deadline in 2 days: {task.title} for {getattr(task.related_ppa, 'title', 'Unlinked PPA')}",
        )
        reminder_count += 1

    # Process 5-day reminders
    for task in upcoming_5_days:
        _send_task_reminder(
            task,
            urgency="medium",
            message=f"Deadline in 5 days: {task.title} for {getattr(task.related_ppa, 'title', 'Unlinked PPA')}",
        )
        reminder_count += 1

    # Process overdue reminders
    for task in overdue_tasks:
        days_overdue = (today - task.due_date).days
        _send_task_reminder(
            task,
            urgency="critical",
            message=f"OVERDUE ({days_overdue} days): {task.title} for {getattr(task.related_ppa, 'title', 'Unlinked PPA')}",
        )
        reminder_count += 1

    return {
        "status": "completed",
        "reminders_sent": reminder_count,
        "two_day_count": upcoming_2_days.count(),
        "five_day_count": upcoming_5_days.count(),
        "overdue_count": overdue_tasks.count(),
    }


def _send_workflow_reminder(stage, urgency, message):
    """
    Send email reminder for workflow stage deadline.

    Args:
        stage: MonitoringEntryWorkflowStage instance
        urgency: str - "critical", "high", "medium"
        message: str - notification message
    """
    # Determine recipients
    recipients = []

    # Add owner team members (if available)
    if stage.owner_team:
        team_emails = list(
            stage.owner_team.members.values_list("user__email", flat=True)
        )
        recipients.extend(team_emails)

    # Add organization contacts (if available)
    if stage.owner_organization:
        # Assuming organization has a contact_email field
        if hasattr(stage.owner_organization, "contact_email"):
            recipients.append(stage.owner_organization.contact_email)

    # Filter out None and empty strings
    recipients = [email for email in recipients if email]

    if not recipients:
        # Log if no recipients found
        print(f"[WORKFLOW REMINDER] No recipients for stage {stage.id}: {message}")
        return

    # Construct email
    subject = f"[{urgency.upper()}] Workflow Deadline Reminder"
    email_message = f"""
{message}

Entry: {stage.entry.title}
Stage: {stage.get_stage_display()}
Status: {stage.get_status_display()}
Due Date: {stage.due_date}
Notes: {stage.notes or "No notes"}

Please review and take action as needed.

---
Office for Other Bangsamoro Communities
Planning & Budgeting System
"""

    try:
        send_mail(
            subject=subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        print(f"[WORKFLOW REMINDER] Sent to {', '.join(recipients)}: {message}")
    except Exception as e:
        print(f"[WORKFLOW REMINDER] Failed to send email: {e}")


def _send_task_reminder(task, urgency, message):
    """Send email reminder for monitoring StaffTask deadlines."""

    recipients = [user.email for user in task.assignees.all() if user.email]

    if not recipients and task.created_by and task.created_by.email:
        recipients.append(task.created_by.email)

    if not recipients:
        print(f"[TASK REMINDER] No recipients for task {task.pk}: {message}")
        return

    subject = f"[{urgency.upper()}] Task Deadline Reminder"
    entry_title = getattr(task.related_ppa, "title", "Unlinked PPA")
    email_message = f"""
{message}

PPA: {entry_title}
Task: {task.title}
Role: {task.task_role or 'Not specified'}
Status: {task.get_status_display()}
Priority: {task.get_priority_display()}
Due Date: {task.due_date}

Description:
{task.description or "No description"}

Notes:
{task.notes or "No notes"}

Please complete this task as soon as possible.

---
Office for Other Bangsamoro Communities
Planning & Budgeting System
"""

    try:
        send_mail(
            subject=subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        print(f"[TASK REMINDER] Sent to {', '.join(recipients)}: {message}")
    except Exception as e:
        print(f"[TASK REMINDER] Failed to send email: {e}")
