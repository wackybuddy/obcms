from __future__ import annotations

from django.db import migrations
from django.utils import timezone


def populate_milestones(apps, schema_editor):
    MonitoringEntry = apps.get_model("monitoring", "MonitoringEntry")
    WorkflowStage = apps.get_model("monitoring", "MonitoringEntryWorkflowStage")

    today = timezone.now().date()

    stage_title_map = dict(getattr(WorkflowStage, "STAGE_CHOICES", []))

    status_completed = getattr(WorkflowStage, "STATUS_COMPLETED", "completed")
    status_blocked = getattr(WorkflowStage, "STATUS_BLOCKED", "blocked")

    entries = MonitoringEntry.objects.all().iterator()

    for entry in entries:
        milestones_raw = entry.milestone_dates or []

        if isinstance(milestones_raw, dict):
            milestones = [milestones_raw]
        elif isinstance(milestones_raw, (list, tuple)):
            milestones = list(milestones_raw)
        else:
            milestones = []

        def already_recorded(date_str: str | None, title: str) -> bool:
            return any(
                isinstance(existing, dict)
                and existing.get("date") == date_str
                and existing.get("title") == title
                for existing in milestones
            )

        def append_milestone(date_value, title: str, status: str, category: str) -> None:
            if not date_value:
                return

            date_str = date_value.isoformat()
            if already_recorded(date_str, title):
                return

            milestones.append(
                {
                    "date": date_str,
                    "title": title,
                    "status": status,
                    "category": category,
                }
            )

        # Entry-level fields -------------------------------------------------
        start_status = "completed" if entry.status == "completed" or (
            entry.start_date and entry.start_date < today
        ) else "upcoming"
        append_milestone(entry.start_date, "Start", start_status, "start")

        if entry.next_milestone_date:
            if entry.status == "completed":
                next_status = "completed"
            elif entry.next_milestone_date < today:
                next_status = "overdue"
            elif entry.next_milestone_date == today:
                next_status = "due_today"
            else:
                next_status = "upcoming"
            append_milestone(entry.next_milestone_date, "Next Milestone", next_status, "next_milestone")

        if entry.target_end_date:
            if entry.status == "completed":
                target_status = "completed"
            elif entry.target_end_date < today:
                target_status = "overdue"
            else:
                target_status = "planned"
            append_milestone(entry.target_end_date, "Target Completion", target_status, "target_end")

        # Workflow stages ----------------------------------------------------
        stage_qs = WorkflowStage.objects.filter(entry_id=entry.pk).exclude(due_date__isnull=True)
        stage_qs = stage_qs.only("stage", "status", "due_date")

        for stage in stage_qs.iterator():
            stage_title = stage_title_map.get(stage.stage, stage.stage)
            if stage.status == status_completed:
                stage_status = "completed"
            elif stage.status == status_blocked:
                stage_status = "blocked"
            elif stage.due_date and stage.due_date < today:
                stage_status = "overdue"
            else:
                stage_status = stage.status or "not_started"

            append_milestone(stage.due_date, stage_title, stage_status, f"stage:{stage.stage}")

        if milestones != list(milestones_raw) and milestones:
            entry.milestone_dates = milestones
            entry.save(update_fields=["milestone_dates"])


def remove_milestones(apps, schema_editor):
    MonitoringEntry = apps.get_model("monitoring", "MonitoringEntry")
    MonitoringEntry.objects.update(milestone_dates=[])


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0012_monitoringentry_milestone_dates"),
    ]

    operations = [
        migrations.RunPython(populate_milestones, remove_milestones),
    ]
