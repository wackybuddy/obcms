from __future__ import annotations

from django.conf import settings
from django.db import migrations


STATUS_MAP = {
    "pending": "not_started",
    "in_progress": "in_progress",
    "completed": "completed",
    "blocked": "at_risk",
    "cancelled": "not_started",
}

PRIORITY_FALLBACK = "medium"


def migrate_assignments(apps, schema_editor):
    MonitoringEntryTaskAssignment = apps.get_model(
        "monitoring", "MonitoringEntryTaskAssignment"
    )
    StaffTask = apps.get_model("common", "StaffTask")
    User = apps.get_model(settings.AUTH_USER_MODEL.split(".")[0], settings.AUTH_USER_MODEL.split(".")[1])

    assignments = MonitoringEntryTaskAssignment.objects.select_related(
        "entry", "assigned_to", "assigned_by"
    ).iterator()

    for assignment in assignments:
        title = assignment.task_title or assignment.notes or "Monitoring Task"
        description_parts = []
        if assignment.task_description:
            description_parts.append(assignment.task_description)
        if assignment.notes:
            description_parts.append(assignment.notes)
        description = "\n\n".join(description_parts)

        status = STATUS_MAP.get(assignment.status, "not_started")
        priority = assignment.priority or PRIORITY_FALLBACK

        existing_qs = StaffTask.objects.filter(
            domain="monitoring",
            task_category="monitoring_assignment",
            related_ppa_id=assignment.entry_id,
            title=title,
            due_date=assignment.due_date,
        )
        if existing_qs.exists():
            continue

        task = StaffTask.objects.create(
            title=title,
            description=description,
            status=status,
            priority=priority if priority in dict(StaffTask.PRIORITY_CHOICES) else PRIORITY_FALLBACK,
            domain=StaffTask.DOMAIN_MONITORING,
            task_role=assignment.role,
            estimated_hours=assignment.estimated_hours,
            actual_hours=assignment.actual_hours,
            due_date=assignment.due_date,
            completed_at=assignment.completed_at,
            progress=100 if status == StaffTask.STATUS_COMPLETED else 0,
            related_ppa_id=assignment.entry_id,
            created_by=assignment.assigned_by or assignment.assigned_to,
            task_category="monitoring_assignment",
            auto_generated=True,
        )

        if assignment.assigned_to_id:
            task.assignees.add(assignment.assigned_to_id)

        StaffTask.objects.filter(pk=task.pk).update(
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )


def reverse_assignments(apps, schema_editor):
    StaffTask = apps.get_model("common", "StaffTask")
    StaffTask.objects.filter(
        domain="monitoring",
        task_category="monitoring_assignment",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0013_backfill_milestone_dates"),
        ("common", "0014_tasktemplate_tasktemplateitem_stafftask_actual_hours_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_assignments, reverse_assignments),
    ]
