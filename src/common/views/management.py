"""OOBC management module views."""

import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import OperationalError, transaction
from django.db.models import Avg, Count, DecimalField, FloatField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from common.constants import (
    CALENDAR_MODULE_COLORS,
    CALENDAR_MODULE_DESCRIPTIONS,
    CALENDAR_MODULE_LABELS,
    CALENDAR_MODULE_ORDER,
    STAFF_COMPETENCY_CATEGORIES,
    STAFF_COMPETENCY_PROFICIENCY_LEVELS,
    STAFF_USER_TYPES,
)
from common.forms import (
    PerformanceTargetForm,
    StaffDevelopmentPlanForm,
    StaffProfileForm,
    StaffTaskForm,
    StaffTeamForm,
    StaffTeamMembershipForm,
    TrainingEnrollmentForm,
    TrainingProgramForm,
)
from common.models import (
    PerformanceTarget,
    StaffDevelopmentPlan,
    StaffProfile,
    StaffTask,
    StaffTeam,
    StaffTeamMembership,
    TrainingEnrollment,
    TrainingProgram,
    User,
)
from common.services.staff import (
    assign_board_position,
    ensure_default_staff_teams,
    ensure_membership,
    ensure_staff_profiles_for_users,
)
from common.services.calendar import build_calendar_payload
from monitoring.models import (
    MonitoringEntry,
    MonitoringEntryFunding,
    MonitoringEntryWorkflowStage,
)


PERFORMANCE_STATUS_WEIGHTS = {
    StaffTask.STATUS_COMPLETED: 1.0,
    StaffTask.STATUS_IN_PROGRESS: 0.6,
    StaffTask.STATUS_NOT_STARTED: 0.2,
    StaffTask.STATUS_AT_RISK: 0.1,
}

# Positions authorized to approve user accounts
USER_APPROVAL_AUTHORIZED_POSITIONS = [
    "Executive Director",
    "Deputy Executive Director",
    "DMO IV",
    "DMO III",
    "Information System Analyst",
    "Information System Analyst II",
    "Planning Officer I",
    "Planning Officer II",
    "Community Development Officer I",
]


def _can_approve_users(user):
    """
    Check if a user has authorization to approve user accounts.

    Authorized roles:
    - Superusers
    - Users with user_type="admin" (OBCMS System Administrators)
    - OOBC Staff with specific positions: Executive Director, Deputy Executive Director,
      DMO IV, DMO III, Information System Analyst, Planning Officers, Community Development Officer I

    Args:
        user: User instance to check

    Returns:
        bool: True if user can approve accounts, False otherwise
    """
    # Superusers always have approval authority
    if user.is_superuser:
        return True

    # System administrators (user_type="admin") can approve
    if user.user_type == "admin":
        return True

    # OOBC staff with authorized positions can approve
    if user.user_type == "oobc_staff" and user.position in USER_APPROVAL_AUTHORIZED_POSITIONS:
        return True

    return False


def _parse_module_filters(request):
    """Return a sanitized list of module filters from query params."""

    modules_param = request.GET.get("modules")
    if not modules_param:
        return None
    requested = [module.strip() for module in modules_param.split(",") if module.strip()]
    valid = [module for module in requested if module in CALENDAR_MODULE_ORDER]
    return valid or None


def _parse_iso_datetime(value):
    """Convert ISO format string to aware datetime in local timezone."""

    if not value:
        return None
    try:
        dt_value = datetime.fromisoformat(value)
    except ValueError:
        return None
    if timezone.is_naive(dt_value):
        return timezone.make_aware(dt_value, timezone.get_current_timezone())
    return timezone.localtime(dt_value)


def _format_ics_datetime(dt_value: datetime, *, all_day: bool) -> str:
    """Format datetime for ICS feeds."""

    if all_day:
        return dt_value.date().strftime("%Y%m%d")
    return dt_value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def staff_queryset():
    """Return the base queryset for OOBC staff users."""

    return User.objects.filter(user_type__in=STAFF_USER_TYPES)


@login_required
def oobc_management_home(request):
    """Surface OOBC management overview data for internal operations."""
    # Restrict access for MANA participants
    user = request.user
    if (
        not user.is_staff
        and not user.is_superuser
        and user.has_perm("mana.can_access_regional_mana")
        and not user.has_perm("mana.can_facilitate_workshop")
    ):
        return redirect("common:page_restricted")

    staff_qs = staff_queryset().order_by("-date_joined")
    pending_qs = User.objects.filter(is_approved=False).order_by("-date_joined")

    context = {
        "metrics": {
            "staff_total": staff_qs.count(),
            "active_staff": staff_qs.filter(is_active=True).count(),
            "pending_approvals": pending_qs.count(),
            "pending_staff": pending_qs.filter(user_type__in=STAFF_USER_TYPES).count(),
        },
        "recent_staff": staff_qs[:8],
        "pending_users": pending_qs[:8],
    }
    return render(request, "common/oobc_management_home.html", context)


@login_required
def oobc_calendar(request):
    """Present the organization-wide calendar workspace."""

    modules_filter = _parse_module_filters(request)
    payload = build_calendar_payload(filter_modules=modules_filter)
    module_stats = payload["module_stats"]

    module_cards = []
    for module in CALENDAR_MODULE_ORDER:
        stats = module_stats.get(
            module,
            {"total": 0, "upcoming": 0, "completed": 0},
        )
        module_cards.append(
            {
                "key": module,
                "label": CALENDAR_MODULE_LABELS.get(module, module.title()),
                "description": CALENDAR_MODULE_DESCRIPTIONS.get(module, ""),
                "color": CALENDAR_MODULE_COLORS.get(module, "bg-slate-500"),
                "stats": stats,
            }
        )

    module_filters = [
        {
            "key": module,
            "label": CALENDAR_MODULE_LABELS.get(module, module.title()),
            "color": CALENDAR_MODULE_COLORS.get(module, "bg-slate-500"),
            "count": module_stats.get(module, {}).get("total", 0),
        }
        for module in CALENDAR_MODULE_ORDER
    ]

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek",
        },
        "height": "auto",
        "eventTimeFormat": {
            "hour": "numeric",
            "minute": "2-digit",
            "meridiem": "short",
        },
    }

    upcoming_highlights = [
        {
            **item,
            "module_label": CALENDAR_MODULE_LABELS.get(
                item.get("module", ""), item.get("module", "").title()
            ),
        }
        for item in payload.get("upcoming_highlights", [])
    ]

    conflicts = [
        {
            **item,
            "module_label": CALENDAR_MODULE_LABELS.get(
                item.get("module", ""), item.get("module", "").title()
            ),
        }
        for item in payload.get("conflicts", [])
    ]

    analytics = payload.get("analytics", {})
    heatmap = analytics.get("heatmap", {})
    heatmap_dates = heatmap.get("dates", [])
    heatmap_rows = []
    for module in heatmap.get("modules", []):
        counts = heatmap.get("matrix", {}).get(module, [])
        paired_counts = list(zip(heatmap_dates, counts))
        heatmap_rows.append(
            {
                "module": module,
                "module_label": CALENDAR_MODULE_LABELS.get(module, module.title()),
                "counts": paired_counts,
            }
        )

    status_counts = analytics.get("status_counts", {})
    status_rows = []
    for module, counts in status_counts.items():
        ordered_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        status_rows.append(
            {
                "module": module,
                "module_label": CALENDAR_MODULE_LABELS.get(module, module.title()),
                "counts": [
                    {
                        "status": key.replace("_", " ").title(),
                        "count": value,
                    }
                    for key, value in ordered_counts
                ],
            }
        )

    workflow_summary = analytics.get("workflow_summary", {})

    compliance = analytics.get("compliance", {})
    compliance_rows = []
    for module, metrics in compliance.get("modules", {}).items():
        compliance_rows.append(
            {
                "module": module,
                "module_label": CALENDAR_MODULE_LABELS.get(module, module.title()),
                "overdue": metrics.get("overdue", 0),
                "pending_approvals": metrics.get("pending_approvals", 0),
                "escalations": metrics.get("escalations", 0),
                "follow_up": metrics.get("follow_up", 0),
            }
        )
    compliance_rows.sort(
        key=lambda item: (
            item["overdue"],
            item["pending_approvals"],
            item["escalations"],
        ),
        reverse=True,
    )
    compliance_totals = compliance.get("totals", {})

    workflow_actions = payload.get("workflow_actions", [])
    now = timezone.now()

    def _sort_actions(actions, limit=5):
        sorted_actions = sorted(
            actions,
            key=lambda item: item.get("due") or now + timedelta(days=365),
        )
        return [
            {
                **action,
                "module_label": CALENDAR_MODULE_LABELS.get(
                    action.get("module", ""), action.get("module", "").title()
                ),
            }
            for action in sorted_actions[:limit]
        ]

    approval_actions = [
        action for action in workflow_actions if action.get("type") == "approval"
    ]
    escalation_actions = [
        action
        for action in workflow_actions
        if action.get("type") in {"escalation", "workflow"}
    ]

    workflow_approvals = _sort_actions(approval_actions)
    workflow_escalations = _sort_actions(escalation_actions)

    follow_up_items = [
        {
            **item,
            "module_label": CALENDAR_MODULE_LABELS.get(
                item.get("module", ""), item.get("module", "").title()
            ),
        }
        for item in payload.get("follow_up_items", [])
    ]

    context = {
        "page_title": "OOBC Calendar Management",
        "active_modules": modules_filter or CALENDAR_MODULE_ORDER,
        "module_cards": module_cards,
        "module_filters": module_filters,
        "upcoming_highlights": upcoming_highlights,
        "conflicts": conflicts,
        "follow_up_items": follow_up_items,
        "module_labels": CALENDAR_MODULE_LABELS,
        "calendar_events_json": json.dumps(payload["entries"], default=str),
        "calendar_options_json": json.dumps(calendar_options),
        "analytics_heatmap_dates": heatmap_dates,
        "analytics_heatmap_rows": heatmap_rows,
        "analytics_status_rows": status_rows,
        "analytics_workflow_summary": workflow_summary,
        "analytics_compliance_rows": compliance_rows,
        "analytics_compliance_totals": compliance_totals,
        "workflow_approvals": workflow_approvals,
        "workflow_escalations": workflow_escalations,
    }
    return render(request, "common/oobc_calendar.html", context)


@login_required
def oobc_calendar_feed_json(request):
    """Return calendar events as JSON for integrations."""

    modules_filter = _parse_module_filters(request)
    payload = build_calendar_payload(filter_modules=modules_filter)

    follow_up_export = [
        {
            **item,
            "due": item["due"].isoformat() if item.get("due") else None,
        }
        for item in payload.get("follow_up_items", [])
    ]

    analytics = payload.get("analytics", {})
    heatmap = analytics.get("heatmap", {})
    analytics_payload = {
        "heatmap": {
            "dates": [date.isoformat() for date in heatmap.get("dates", [])],
            "modules": heatmap.get("modules", []),
            "matrix": heatmap.get("matrix", {}),
        },
        "status_counts": analytics.get("status_counts", {}),
        "workflow_summary": analytics.get("workflow_summary", {}),
        "compliance": analytics.get("compliance", {}),
    }

    workflow_actions_export = []
    for action in payload.get("workflow_actions", []):
        action_copy = dict(action)
        if action_copy.get("due"):
            action_copy["due"] = action_copy["due"].isoformat()
        workflow_actions_export.append(action_copy)

    data = {
        "generated_at": timezone.now().isoformat(),
        "modules": modules_filter or CALENDAR_MODULE_ORDER,
        "events": payload["entries"],
        "module_stats": payload["module_stats"],
        "follow_up_items": follow_up_export,
        "workflow_actions": workflow_actions_export,
        "workflow_summary": analytics.get("workflow_summary", {}),
        "analytics": analytics_payload,
    }
    return JsonResponse(data)


@login_required
def oobc_calendar_feed_ics(request):
    """Provide an ICS feed of calendar events."""

    modules_filter = _parse_module_filters(request)
    payload = build_calendar_payload(filter_modules=modules_filter)

    def ics_escape(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OOBC Management//Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:OOBC Integrated Calendar",
    ]

    for entry in payload["entries"]:
        start_iso = entry.get("start")
        if not start_iso:
            continue
        start_dt = _parse_iso_datetime(start_iso)
        if not start_dt:
            continue
        end_iso = entry.get("end")
        end_dt = _parse_iso_datetime(end_iso) if end_iso else None
        all_day = bool(entry.get("allDay"))

        extended = entry.get("extendedProps", {})
        description_lines = []
        for key in ("module", "status", "category"):
            value = extended.get(key)
            if value:
                description_lines.append(f"{key.title()}: {value}")

        workflow_actions = extended.get("workflowActions", [])
        for action in workflow_actions:
            due_value = action.get("due")
            if isinstance(due_value, datetime):
                due_display = due_value.strftime("%Y-%m-%d")
            else:
                due_display = str(due_value)
            description_lines.append(
                f"Action - {action.get('label', 'Workflow')}: {due_display}"
            )
        description = "\n".join(description_lines)

        sanitized_title = entry.get("title", "").replace("\n", " ")

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{ics_escape(entry.get('id', ''))}@oobcms",
                f"SUMMARY:{ics_escape(sanitized_title)}",
            ]
        )

        lines.append(
            "DTSTART;VALUE=DATE:" + _format_ics_datetime(start_dt, all_day=True)
            if all_day
            else "DTSTART:" + _format_ics_datetime(start_dt, all_day=False)
        )

        if end_dt:
            lines.append(
                "DTEND;VALUE=DATE:" + _format_ics_datetime(end_dt, all_day=True)
                if all_day
                else "DTEND:" + _format_ics_datetime(end_dt, all_day=False)
            )

        if description:
            lines.append(f"DESCRIPTION:{ics_escape(description)}")

        for action in workflow_actions:
            due_value = action.get("due")
            if isinstance(due_value, datetime):
                due_display = due_value.strftime("%Y-%m-%d")
            else:
                due_display = str(due_value)
            action_text = f"{action.get('label', 'Workflow')} ({due_display})"
            lines.append(f"X-OOBC-ACTION:{ics_escape(action_text)}")

        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    content = "\r\n".join(lines)
    response = HttpResponse(content, content_type="text/calendar")
    response["Content-Disposition"] = "attachment; filename=OOBC-calendar.ics"
    return response


@login_required
def oobc_calendar_brief(request):
    """Render a printable brief summarising upcoming events and tasks."""

    modules_filter = _parse_module_filters(request)
    window_days = max(1, min(int(request.GET.get("days", 14)), 60))
    payload = build_calendar_payload(filter_modules=modules_filter)

    now = timezone.now()
    window_end = now + timedelta(days=window_days)

    upcoming_events = []
    for entry in payload["entries"]:
        start_dt = _parse_iso_datetime(entry.get("start"))
        if not start_dt:
            continue
        if not (now <= start_dt <= window_end):
            continue
        module = entry.get("extendedProps", {}).get("module", "")
        upcoming_events.append(
            {
                "title": entry.get("title", ""),
                "start": start_dt,
                "module": module,
                "module_label": CALENDAR_MODULE_LABELS.get(module, module.title()),
                "status": entry.get("extendedProps", {}).get("status"),
                "category": entry.get("extendedProps", {}).get("category"),
            }
        )

    upcoming_events.sort(key=lambda item: item["start"])

    follow_up_items = [
        item
        for item in payload.get("follow_up_items", [])
        if item.get("due") and now <= item["due"] <= window_end
    ]

    context = {
        "generated_at": now,
        "window_days": window_days,
        "module_labels": CALENDAR_MODULE_LABELS,
        "upcoming_events": upcoming_events,
        "follow_up_items": [
            {
                **item,
                "module_label": CALENDAR_MODULE_LABELS.get(
                    item.get("module", ""), item.get("module", "").title()
                ),
            }
            for item in follow_up_items
        ],
    }
    return render(request, "common/oobc_calendar_brief.html", context)


@login_required
def staff_management(request):
    """Detailed staffing dashboard for OOBC administrators."""

    ensure_default_staff_teams()

    staff_qs = staff_queryset().order_by("last_name", "first_name")
    pending_staff_qs = staff_qs.filter(is_approved=False)
    inactive_staff_qs = staff_qs.filter(is_active=False)
    today = timezone.now().date()

    role_breakdown = [
        {
            "key": row["user_type"],
            "label": dict(User.USER_TYPES).get(
                row["user_type"], row["user_type"].replace("_", " ").title()
            ),
            "total": row["total"],
        }
        for row in staff_qs.values("user_type").annotate(total=Count("id"))
    ]

    task_qs = (
        StaffTask.objects.select_related("linked_event")
        .prefetch_related("teams", "assignees")
        .order_by("due_date", "-priority")
    )
    task_list = list(task_qs)

    tasks_by_status = defaultdict(list)
    tasks_by_staff = defaultdict(list)
    for task in task_list:
        tasks_by_status[task.status].append(task)
        for member in task.assignees.all():
            tasks_by_staff[member.pk].append(task)

    completed_tasks = len(tasks_by_status.get(StaffTask.STATUS_COMPLETED, []))
    total_tasks = len(task_list)
    upcoming_tasks = [
        task
        for task in task_list
        if task.due_date
        and today <= task.due_date <= today + timedelta(days=7)
    ]
    performance_snapshot = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": round((completed_tasks / total_tasks) * 100)
        if total_tasks
        else 0,
        "at_risk": len(tasks_by_status.get(StaffTask.STATUS_AT_RISK, [])),
        "upcoming": len(upcoming_tasks),
    }

    memberships = (
        StaffTeamMembership.objects.select_related("team", "user")
        .filter(user__in=staff_qs)
        .order_by("team__name")
    )
    team_assignments = defaultdict(list)
    for membership in memberships:
        if membership.is_active:
            team_assignments[membership.user_id].append(membership.team)

    staff_profiles_data = []
    for staff in staff_qs:
        staff_tasks = sorted(
            tasks_by_staff.get(staff.id, []),
            key=lambda item: (item.due_date or today, item.title),
        )
        total_for_staff = len(staff_tasks)
        status_counts = defaultdict(int)
        for task in staff_tasks:
            status_counts[task.status] += 1
        next_due = staff_tasks[0].due_date if staff_tasks and staff_tasks[0].due_date else None
        contact_fields = [staff.email, staff.position, staff.organization, staff.contact_number]
        filled_fields = sum(1 for value in contact_fields if value)
        profile_completion = (
            int(round((filled_fields / len(contact_fields)) * 100))
            if contact_fields
            else 0
        )
        performance_score = 0
        if total_for_staff:
            performance_score = int(
                round(
                    sum(
                        PERFORMANCE_STATUS_WEIGHTS.get(task.status, 0)
                        for task in staff_tasks
                    )
                    / total_for_staff
                    * 100
                )
            )
        completion_rate = (
            round((status_counts.get(StaffTask.STATUS_COMPLETED, 0) / total_for_staff) * 100)
            if total_for_staff
            else 0
        )
        availability = (
            "Available"
            if total_for_staff <= 1
            else "Focused"
            if total_for_staff <= 2
            else "At Capacity"
        )
        status_label = (
            "Active"
            if staff.is_active and staff.is_approved
            else "Pending"
            if not staff.is_approved
            else "Inactive"
        )
        staff_profiles_data.append(
            {
                "staff": staff,
                "teams": [team.name for team in team_assignments.get(staff.id, [])],
                "status": status_label,
                "contact": staff.contact_number or staff.email,
                "availability": availability,
                "profile_completion": profile_completion,
                "next_due": next_due,
                "tasks": staff_tasks[:3],
                "task_summary": {
                    "total": total_for_staff,
                    "completed": status_counts.get(StaffTask.STATUS_COMPLETED, 0),
                    "in_progress": status_counts.get(StaffTask.STATUS_IN_PROGRESS, 0),
                    "at_risk": status_counts.get(StaffTask.STATUS_AT_RISK, 0),
                    "not_started": status_counts.get(StaffTask.STATUS_NOT_STARTED, 0),
                    "next_due": next_due,
                    "completion_rate": completion_rate,
                    "performance_score": performance_score,
                },
            }
        )

    individual_performance = [
        {
            "staff": profile["staff"],
            "total": profile["task_summary"]["total"],
            "completed": profile["task_summary"]["completed"],
            "at_risk": profile["task_summary"]["at_risk"],
            "in_progress": profile["task_summary"]["in_progress"],
            "not_started": profile["task_summary"]["not_started"],
            "completion_rate": profile["task_summary"]["completion_rate"],
            "score": profile["task_summary"]["performance_score"],
        }
        for profile in staff_profiles_data
        if profile["task_summary"]["total"]
    ]
    individual_performance.sort(
        key=lambda item: (item["score"], item["completion_rate"]), reverse=True
    )

    teams_qs = StaffTeam.objects.prefetch_related(
        "tasks__assignees", "memberships__user"
    ).order_by("name")
    team_overview = []
    team_performance = []
    for team in teams_qs:
        members = [
            membership.user
            for membership in team.memberships.all()
            if membership.is_active
        ]
        tasks = list(team.tasks.all())
        total_team_tasks = len(tasks)
        status_counts = defaultdict(int)
        for task in tasks:
            status_counts[task.status] += 1
        completed_team_tasks = status_counts.get(StaffTask.STATUS_COMPLETED, 0)
        avg_progress_team = (
            round(sum(task.progress for task in tasks) / total_team_tasks)
            if total_team_tasks
            else 0
        )
        completion_rate_team = (
            round((completed_team_tasks / total_team_tasks) * 100)
            if total_team_tasks
            else 0
        )
        team_overview.append(
            {
                "team": team,
                "name": team.name,
                "description": team.description,
                "mission": team.mission,
                "focus": team.focus_areas,
                "members": members,
                "member_count": len(members),
                "active_tasks": total_team_tasks - completed_team_tasks,
                "completion_rate": completion_rate_team,
                "avg_progress": avg_progress_team,
                "extra_members": max(len(members) - 3, 0),
                "tasks": sorted(
                    tasks,
                    key=lambda task: (task.due_date or today, task.title),
                )[:3],
            }
        )
        team_performance.append(
            {
                "team": team.name,
                "total": total_team_tasks,
                "completed": completed_team_tasks,
                "at_risk": status_counts.get(StaffTask.STATUS_AT_RISK, 0),
                "in_progress": status_counts.get(StaffTask.STATUS_IN_PROGRESS, 0),
                "not_started": status_counts.get(StaffTask.STATUS_NOT_STARTED, 0),
                "completion_rate": completion_rate_team,
                "avg_progress": avg_progress_team,
                "member_count": len(members),
            }
        )

    staff_profiles = sorted(
        staff_profiles_data,
        key=lambda profile: (
            profile["task_summary"]["performance_score"],
            profile["task_summary"]["total"],
        ),
        reverse=True,
    )[:6]

    context = {
        "metrics": {
            "total": staff_qs.count(),
            "active": staff_qs.filter(is_active=True, is_approved=True).count(),
            "inactive": inactive_staff_qs.count(),
            "pending": pending_staff_qs.count(),
            "recent": staff_qs.filter(
                date_joined__gte=timezone.now() - timedelta(days=30)
            ).count(),
        },
        "role_breakdown": role_breakdown,
        "pending_staff": pending_staff_qs.order_by("-date_joined")[:10],
        "recent_staff": staff_qs.order_by("-last_login")[:10],
        "inactive_staff": inactive_staff_qs.order_by("last_name", "first_name")[:10],
        "staff_list": staff_qs,
        "staff_profiles": staff_profiles,
        "team_overview": team_overview,
        "individual_performance": individual_performance,
        "team_performance": sorted(
            team_performance,
            key=lambda item: (item["completion_rate"], item["avg_progress"]),
            reverse=True,
        ),
        "performance_snapshot": performance_snapshot,
    }
    return render(request, "common/oobc_staff_management.html", context)


@login_required
def staff_task_create(request):
    """Dedicated interface for creating staff tasks."""

    ensure_default_staff_teams()
    form = StaffTaskForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        if not task.created_by:
            task.created_by = request.user
        if task.status == StaffTask.STATUS_COMPLETED and not task.completed_at:
            task.completed_at = timezone.now()
            task.progress = 100
        task.save()
        form.save_m2m()
        assign_board_position(task)
        for member in task.assignees.all():
            for team in task.teams.all():
                ensure_membership(team, member, request.user)
        messages.success(request, f"Task \"{task.title}\" saved successfully.")
        return redirect("common:staff_management")

    recent_tasks = (
        StaffTask.objects.prefetch_related("teams", "assignees")
        .order_by("-created_at")[:10]
    )

    context = {
        "form": form,
        "recent_tasks": recent_tasks,
    }
    return render(request, "common/staff_task_create.html", context)


@login_required
def staff_task_modal_create(request):
    """Render the new-task modal and process submissions from the board."""

    if not request.headers.get("HX-Request") and request.method == "GET":
        return redirect("common:staff_task_create")

    ensure_default_staff_teams()

    initial: dict[str, object] = {}
    status_value = request.GET.get("status")
    if status_value in dict(StaffTask.STATUS_CHOICES):
        initial["status"] = status_value

    priority_value = request.GET.get("priority")
    if priority_value in dict(StaffTask.PRIORITY_CHOICES):
        initial["priority"] = priority_value

    team_slug = request.GET.get("team")
    if team_slug:
        try:
            team_obj = StaffTeam.objects.get(slug=team_slug)
        except StaffTeam.DoesNotExist:
            team_obj = None
        else:
            # StaffTaskForm expects a list of team ids for the many-to-many field
            initial["teams"] = [team_obj.pk]

    form_kwargs = {"request": request}

    if request.method == "POST":
        form = StaffTaskForm(request.POST, **form_kwargs)
        if form.is_valid():
            try:
                with transaction.atomic():
                    task = form.save(commit=False)
                    if not task.created_by:
                        task.created_by = request.user
                    if (
                        task.status == StaffTask.STATUS_COMPLETED
                        and not task.completed_at
                    ):
                        task.completed_at = timezone.now()
                        task.progress = 100
                    task.save()
                    form.save_m2m()
                    try:
                        assign_board_position(task)
                    except OperationalError:
                        pass
                    for member in task.assignees.all():
                        for team in task.teams.all():
                            ensure_membership(team, member, request.user)
            except OperationalError:
                pass

            headers = {
                "HX-Trigger": json.dumps(
                    {
                        "task-board-refresh": True,
                        "task-modal-close": True,
                    }
                )
            }
            if request.headers.get("HX-Request"):
                return HttpResponse(status=204, headers=headers)
            messages.success(request, f"Task \"{task.title}\" saved successfully.")
            return redirect("common:staff_management")
    else:
        form = StaffTaskForm(initial=initial, **form_kwargs)

    status_labels = dict(StaffTask.STATUS_CHOICES)
    priority_labels = dict(StaffTask.PRIORITY_CHOICES)

    status_value = form["status"].value() or StaffTask.STATUS_NOT_STARTED
    priority_value = form["priority"].value() or StaffTask.PRIORITY_MEDIUM
    try:
        progress_value = int(form["progress"].value() or 0)
    except (TypeError, ValueError):
        progress_value = 0
    progress_value = max(0, min(100, progress_value))

    due_value = form["due_date"].value()
    if isinstance(due_value, date):
        due_date_display = formats.date_format(due_value, "M d, Y")
    elif due_value:
        try:
            parsed_due = datetime.strptime(due_value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            due_date_display = None
        else:
            due_date_display = formats.date_format(parsed_due, "M d, Y")
    else:
        due_date_display = None

    team_values = form["teams"].value()
    if isinstance(team_values, str):
        team_values = [team_values] if team_values else []
    team_queryset = form.fields["teams"].queryset
    selected_teams = list(team_queryset.filter(pk__in=team_values or []))
    team_label = ", ".join(team.name for team in selected_teams if team)
    if not team_label:
        team_label = "No team selected"

    assignee_values = form["assignees"].value()
    assignee_queryset = form.fields["assignees"].queryset
    if isinstance(assignee_values, str):
        assignee_values = [assignee_values]
    selected_assignees = list(
        assignee_queryset.filter(pk__in=assignee_values or [])
    )
    assignee_label = "Assign to staff (optional)"
    assignee_names = [
        member.get_full_name() or member.username
        for member in selected_assignees
        if member
    ]
    if assignee_names:
        assignee_label = ", ".join(assignee_names)

    title_preview = form["title"].value() or "New staff task"

    context = {
        "form": form,
        "status_labels": status_labels,
        "priority_labels": priority_labels,
        "status_value": status_value,
        "status_label": status_labels.get(
            status_value, status_labels.get(StaffTask.STATUS_NOT_STARTED)
        ),
        "priority_value": priority_value,
        "priority_label": priority_labels.get(
            priority_value, priority_labels.get(StaffTask.PRIORITY_MEDIUM)
        ),
        "progress_value": progress_value,
        "due_date_display": due_date_display,
        "team_label": team_label,
        "assignee_label": assignee_label,
        "title_preview": title_preview,
    }
    template_name = "common/partials/staff_task_create_modal.html"
    if not request.headers.get("HX-Request"):
        return render(request, "common/staff_task_create.html", context)
    return render(request, template_name, context)


def _task_relation_tokens(task: StaffTask) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Return display-ready assignee and team tokens for table rendering."""

    def _display_name(user_obj):
        if not user_obj:
            return ""
        if hasattr(user_obj, "get_full_name"):
            full_name = (user_obj.get_full_name() or "").strip()
            if full_name:
                return full_name
        username = getattr(user_obj, "username", "")
        return username

    assignee_tokens: list[dict[str, object]] = []
    if hasattr(task, "assignees"):
        try:
            iterator = task.assignees.all()
        except Exception:  # pragma: no cover - defensive for optional relation
            iterator = []
        for member in iterator:
            assignee_tokens.append(
                {
                    "id": getattr(member, "pk", None),
                    "label": _display_name(member) or "Unassigned",
                }
            )
    team_tokens: list[dict[str, object]] = []
    try:
        team_iter = task.teams.all()
    except Exception:  # pragma: no cover - gracefully handle missing relation
        team_iter = []
    for team in team_iter:
        team_tokens.append(
            {
                "id": getattr(team, "pk", None),
                "label": getattr(team, "name", "Unnamed team"),
            }
        )

    return assignee_tokens, team_tokens


@login_required
def staff_task_board(request):
    """Task workspace with Kanban-style grouping and filters."""

    ensure_default_staff_teams()

    status_labels = dict(StaffTask.STATUS_CHOICES)
    priority_labels = dict(StaffTask.PRIORITY_CHOICES)

    new_task_form: StaffTaskForm | None = None

    if request.method == "POST":
        form_name = request.POST.get("form_name")

        if form_name == "create_task":
            # Debug: Log received POST data
            print("DEBUG: Received POST data for create_task:")
            for key, value in request.POST.items():
                if key != 'csrfmiddlewaretoken':
                    print(f"  {key} = {value}")

            new_task_form = StaffTaskForm(
                request.POST,
                request=request,
                table_mode=True,
            )

            # Debug: Log form errors if any
            if not new_task_form.is_valid():
                print("DEBUG: Form validation errors:")
                for field, errors in new_task_form.errors.items():
                    print(f"  {field}: {errors}")

            is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

            if new_task_form.is_valid():
                try:
                    with transaction.atomic():
                        task = new_task_form.save(commit=False)
                        if not task.created_by:
                            task.created_by = request.user
                        if (
                            task.status == StaffTask.STATUS_COMPLETED
                            and not task.completed_at
                        ):
                            task.completed_at = timezone.now()
                            task.progress = 100
                        task.save()
                        new_task_form.save_m2m()
                        try:
                            assign_board_position(task)
                        except OperationalError:
                            pass
                        for member in task.assignees.all():
                            for team in task.teams.all():
                                ensure_membership(team, member, request.user)
                except OperationalError:
                    pass

                redirect_target = request.POST.get("next")
                if redirect_target and not url_has_allowed_host_and_scheme(
                    redirect_target,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    redirect_target = None

                messages.success(request, f"Task \"{task.title}\" created.")

                if request.headers.get("HX-Request") or is_ajax:
                    assignee_tokens, team_tokens = _task_relation_tokens(task)
                    new_row_context = {
                        "task": task,
                        "form": StaffTaskForm(instance=task, request=request, table_mode=True),
                        "assignees": assignee_tokens,
                        "assignee_ids": [token["id"] for token in assignee_tokens if token.get("id") is not None],
                        "assignee_display": ", ".join(token["label"] for token in assignee_tokens if token.get("label")) or "Unassigned",
                        "teams": team_tokens,
                    }
                    return render(request, "common/partials/staff_task_table_row.html", new_row_context)

                if redirect_target:
                    return redirect(redirect_target)

                redirect_params = request.GET.copy()
                redirect_params["view"] = "table"
                redirect_url = reverse("common:staff_task_board")
                if redirect_params:
                    redirect_url = f"{redirect_url}?{redirect_params.urlencode()}"
                return redirect(redirect_url)
            else:
                # Handle AJAX validation errors
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': new_task_form.errors,
                        'message': 'Please correct the errors below.'
                    }, status=400)

        elif form_name == "update_task":
            redirect_target = request.POST.get("next")
            if redirect_target and not url_has_allowed_host_and_scheme(
                redirect_target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                redirect_target = None
            task_id = request.POST.get("task_id")
            status = request.POST.get("status")
            progress = request.POST.get("progress")
            if task_id and status in status_labels:
                try:
                    task = StaffTask.objects.select_for_update().get(pk=task_id)
                except StaffTask.DoesNotExist:
                    messages.error(request, "Task could not be found.")
                else:
                    task.status = status
                    update_fields = ["status", "updated_at"]
                    if progress:
                        try:
                            progress_int = max(0, min(100, int(progress)))
                        except (TypeError, ValueError):
                            progress_int = task.progress
                        task.progress = progress_int
                        update_fields.append("progress")
                    if status == StaffTask.STATUS_COMPLETED and not task.completed_at:
                        task.completed_at = timezone.now()
                        task.progress = 100
                        update_fields.extend(["completed_at", "progress"])
                    task.save(update_fields=update_fields)
                    messages.success(
                        request,
                        f"Task \"{task.title}\" updated to {status_labels[status]}.",
                    )
            if redirect_target:
                return redirect(redirect_target)
            return redirect("common:staff_task_board")

    view_mode = request.GET.get("view", "board")
    valid_views = {"board", "table"}
    if view_mode not in valid_views:
        view_mode = "board"

    hx_board_partial = (
        request.headers.get("HX-Request") and request.GET.get("partial") == "board"
    )
    if hx_board_partial:
        view_mode = "board"

    group_by = request.GET.get("group", "status")
    valid_groupings = {"status", "priority", "team"}
    if group_by not in valid_groupings:
        group_by = "status"

    sort_field = request.GET.get("sort", "due_date")
    sort_order = request.GET.get("order", "asc")
    if sort_order not in {"asc", "desc"}:
        sort_order = "asc"

    try:
        tasks_qs = (
            StaffTask.objects.prefetch_related("teams", "assignees")
            .order_by("board_position", "due_date", "-priority", "title")
        )
        board_ordering_enabled = True
    except OperationalError:
        tasks_qs = (
            StaffTask.objects.prefetch_related("teams", "assignees")
            .order_by("due_date", "-priority", "title")
        )
        board_ordering_enabled = False

    status_filter = request.GET.get("status", "")
    team_filter = request.GET.get("team", "")
    assignee_filter = request.GET.get("assignee", "")
    priority_filter = request.GET.get("priority", "")
    search_query = request.GET.get("q", "")

    if status_filter in status_labels:
        tasks_qs = tasks_qs.filter(status=status_filter)
    if team_filter:
        if team_filter == "unassigned":
            tasks_qs = tasks_qs.filter(teams__isnull=True)
        else:
            tasks_qs = tasks_qs.filter(teams__slug=team_filter)
        tasks_qs = tasks_qs.distinct()
    if assignee_filter:
        tasks_qs = tasks_qs.filter(assignees__id=assignee_filter)
    if priority_filter in priority_labels:
        tasks_qs = tasks_qs.filter(priority=priority_filter)
    if search_query:
        tasks_qs = tasks_qs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(impact__icontains=search_query)
        )

    tasks_list = list(tasks_qs)

    if board_ordering_enabled:
        try:
            def ensure_status_positions(task_records):
                groups: dict[str, list[StaffTask]] = defaultdict(list)
                for item in task_records:
                    groups[item.status].append(item)
                recalculated: list[StaffTask] = []
                timestamp = timezone.now()
                for items in groups.values():
                    items.sort(key=lambda task: (task.board_position or 0, task.created_at))
                    for index, task in enumerate(items, start=1):
                        if task.board_position != index:
                            task.board_position = index
                            task.updated_at = timestamp
                            recalculated.append(task)
                if recalculated:
                    StaffTask.objects.bulk_update(
                        recalculated, ["board_position", "updated_at"]
                    )

            ensure_status_positions(tasks_list)
        except OperationalError:
            board_ordering_enabled = False

    priority_rank = {
        value: index for index, (value, _label) in enumerate(StaffTask.PRIORITY_CHOICES)
    }
    status_rank = {
        value: index for index, (value, _label) in enumerate(StaffTask.STATUS_CHOICES)
    }

    def assignee_sort_key(task):
        names = [
            (member.get_full_name() or member.username).strip().lower()
            for member in task.assignees.all()
            if member
        ]
        if not names:
            return (1, "")
        return (0, sorted(name for name in names if name)[0])

    sort_key_map = {
        "due_date": lambda task: task.due_date or date.max,
        "priority": lambda task: priority_rank.get(task.priority, len(priority_rank)),
        "status": lambda task: status_rank.get(task.status, len(status_rank)),
        "progress": lambda task: task.progress,
        "created": lambda task: task.created_at,
        "assignee": assignee_sort_key,
        "team": lambda task: (", ".join(team.name.lower() for team in task.teams.all()) if task.teams.exists() else ""),
        "title": lambda task: task.title.lower(),
    }

    if sort_field not in sort_key_map:
        sort_field = "due_date"

    if view_mode == "table" or request.GET.get("sort"):
        descending = sort_order == "desc"
        tasks_list.sort(key=sort_key_map[sort_field], reverse=descending)

    def build_board_columns(tasks, grouping):
        columns = []
        if grouping == "priority":
            for value, label in StaffTask.PRIORITY_CHOICES:
                grouped_tasks = [task for task in tasks if task.priority == value]
                columns.append(
                    {
                        "status_key": value,
                        "status_label": label,
                        "tasks": grouped_tasks,
                        "count": len(grouped_tasks),
                    }
                )
        elif grouping == "team":
            team_lookup = {}
            unassigned_tasks = []

            for task in tasks:
                task_teams = list(task.teams.all())
                if task_teams:
                    for team in task_teams:
                        if team.id not in team_lookup:
                            team_lookup[team.id] = {"team": team, "tasks": []}
                        team_lookup[team.id]["tasks"].append(task)
                else:
                    unassigned_tasks.append(task)

            # Sort teams by name
            teams = sorted(team_lookup.values(), key=lambda item: item["team"].name.lower())
            for team_data in teams:
                team = team_data["team"]
                team_tasks = team_data["tasks"]
                columns.append(
                    {
                        "status_key": team.slug,
                        "status_label": team.name,
                        "tasks": team_tasks,
                        "count": len(team_tasks),
                    }
                )

            # Always show unassigned column when grouping by team
            columns.append(
                {
                    "status_key": "unassigned",
                    "status_label": "Unassigned",
                    "tasks": unassigned_tasks,
                    "count": len(unassigned_tasks),
                }
            )
        else:  # default to status grouping
            for status, label in StaffTask.STATUS_CHOICES:
                grouped_tasks = [task for task in tasks if task.status == status]
                columns.append(
                    {
                        "status_key": status,
                        "status_label": label,
                        "tasks": grouped_tasks,
                        "count": len(grouped_tasks),
                    }
                )
        return columns

    board_columns = build_board_columns(tasks_list, group_by) if view_mode == "board" else []

    metrics = {
        "total": len(tasks_list),
        "completed": len([task for task in tasks_list if task.status == StaffTask.STATUS_COMPLETED]),
        "at_risk": len([task for task in tasks_list if task.status == StaffTask.STATUS_AT_RISK]),
        "upcoming": len(
            [
                task
                for task in tasks_list
                if task.due_date and task.due_date >= timezone.now().date()
                and task.due_date <= timezone.now().date() + timedelta(days=7)
            ]
        ),
    }
    metrics["completion_rate"] = (
        round((metrics["completed"] / metrics["total"]) * 100)
        if metrics["total"]
        else 0
    )

    team_options = StaffTeam.objects.filter(is_active=True).order_by("name")
    assignee_options = staff_queryset().order_by("last_name", "first_name")

    view_options = [
        {"value": "board", "label": "Board", "icon": "fa-columns"},
        {"value": "table", "label": "Table", "icon": "fa-table"},
    ]
    group_options = [
        {"value": "status", "label": "Status"},
        {"value": "priority", "label": "Priority"},
        {"value": "team", "label": "Team"},
    ]
    sort_options = [
        {"value": "due_date", "label": "Due date"},
        {"value": "priority", "label": "Priority"},
        {"value": "status", "label": "Status"},
        {"value": "progress", "label": "Progress"},
        {"value": "created", "label": "Created"},
        {"value": "assignee", "label": "Assignee"},
        {"value": "team", "label": "Team"},
    ]
    table_columns = [
        {"key": "title", "label": "Task"},
        {"key": "assignee", "label": "Assignees"},
        {"key": "team", "label": "Teams"},
        {"key": "start_date", "label": "Start date"},
        {"key": "due_date", "label": "Due date"},
        {"key": "status", "label": "Status"},
        {"key": "priority", "label": "Priority"},
        {"key": "progress", "label": "Progress"},
        {"key": "actions", "label": "Actions"},
    ]

    table_rows = []
    for task in tasks_list:
        assignee_tokens, team_tokens = _task_relation_tokens(task)

        table_rows.append(
            {
                "task": task,
                "form": StaffTaskForm(
                    instance=task,
                    request=request,
                    table_mode=True,
                ),
                "assignees": assignee_tokens,
                "assignee_ids": [
                    token["id"]
                    for token in assignee_tokens
                    if token.get("id") is not None
                ],
                "assignee_display": ", ".join(
                    token["label"] for token in assignee_tokens if token.get("label")
                )
                or "Unassigned",
                "teams": team_tokens,
            }
        )

    if new_task_form is None:
        new_task_form = StaffTaskForm(
            request=request,
            table_mode=True,
        )

    update_url = reverse("common:staff_task_update")

    refresh_params = request.GET.copy()
    refresh_params["view"] = "board"
    refresh_params["group"] = group_by
    refresh_params["partial"] = "board"
    refresh_query = refresh_params.urlencode()
    if refresh_query:
        board_refresh_url = f"{reverse('common:staff_task_board')}?{refresh_query}"
    else:
        board_refresh_url = reverse("common:staff_task_board")

    context = {
        "pipeline": board_columns,
        "metrics": metrics,
        "status_labels": status_labels,
        "priority_labels": priority_labels,
        "team_options": team_options,
        "assignee_options": assignee_options,
        "view_mode": view_mode,
        "view_options": view_options,
        "group_by": group_by,
        "group_options": group_options,
        "sort_field": sort_field,
        "sort_order": sort_order,
        "sort_options": sort_options,
        "table_columns": table_columns,
        "table_rows": table_rows,
        "new_task_form": new_task_form,
        "tasks": tasks_list,
        "update_url": update_url,
        "board_refresh_url": board_refresh_url,
        "filters": {
            "status": status_filter,
            "team": team_filter,
            "assignee": assignee_filter,
            "priority": priority_filter,
            "q": search_query,
            "view": view_mode,
            "group": group_by,
            "sort": sort_field,
            "order": sort_order,
        },
    }
    if request.headers.get("HX-Request"):
        if view_mode == 'board':
            return render(request, "common/partials/staff_task_board_wrapper.html", context)
        else:
            return render(request, "common/partials/staff_task_table_wrapper.html", context)
    return render(request, "common/staff_task_board.html", context)


@login_required
@require_POST
def staff_task_update(request):
    """Handle inline updates from the drag-and-drop task board."""

    status_labels = dict(StaffTask.STATUS_CHOICES)
    priority_labels = dict(StaffTask.PRIORITY_CHOICES)
    valid_groups = {"status", "priority", "team"}

    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
    else:
        payload = request.POST

    task_id = payload.get("task_id")
    group = payload.get("group")
    value = payload.get("value")
    progress_value = payload.get("progress")
    source_value = payload.get("source_value")

    def parse_id_list(raw_value):
        if not raw_value:
            return []
        if isinstance(raw_value, str):
            raw_value = [item for item in raw_value.split(",") if item]
        try:
            return [int(item) for item in raw_value]
        except (TypeError, ValueError):
            raise ValueError

    try:
        target_order = parse_id_list(payload.get("order"))
        source_order = parse_id_list(payload.get("source_order"))
    except ValueError:
        return JsonResponse({"error": "Invalid ordering payload."}, status=400)

    try:
        task_id = int(task_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Missing or invalid task id."}, status=400)

    if group not in valid_groups:
        return JsonResponse({"error": "Unsupported update group."}, status=400)

    def normalised_group_value(task_obj, grouping):
        if grouping == "status":
            return task_obj.status
        if grouping == "priority":
            return task_obj.priority
        if grouping == "team":
            team_slugs = [team.slug for team in task_obj.teams.all()]
            return team_slugs[0] if team_slugs else "unassigned"
        return ""

    def resequence(order_ids, grouping, grouping_value):
        if not order_ids:
            return
        tasks = (
            StaffTask.objects.select_for_update()
            .prefetch_related("teams")
            .filter(pk__in=order_ids)
        )
        task_lookup = {task.pk: task for task in tasks}
        timestamp = timezone.now()
        updated = []
        for position, identifier in enumerate(order_ids, start=1):
            task_obj = task_lookup.get(identifier)
            if not task_obj:
                continue
            if normalised_group_value(task_obj, grouping) != grouping_value:
                continue
            if task_obj.board_position != position:
                task_obj.board_position = position
                task_obj.updated_at = timestamp
                updated.append(task_obj)
        if updated:
            StaffTask.objects.bulk_update(updated, ["board_position", "updated_at"])

    board_position_value = None
    try:
        with transaction.atomic():
            task = StaffTask.objects.select_for_update().get(pk=task_id)
            update_fields = ["updated_at"]

            if group == "status":
                if value not in status_labels:
                    return JsonResponse({"error": "Unknown status."}, status=400)
                task.status = value
                update_fields.append("status")
                progress_override = None
                if progress_value not in (None, ""):
                    try:
                        progress_override = max(0, min(100, int(progress_value)))
                    except (TypeError, ValueError):
                        progress_override = None
                if value == StaffTask.STATUS_COMPLETED:
                    if not task.completed_at:
                        task.completed_at = timezone.now()
                        update_fields.append("completed_at")
                    task.progress = 100
                    update_fields.append("progress")
                elif progress_override is not None:
                    task.progress = progress_override
                    update_fields.append("progress")
            elif group == "priority":
                if value not in priority_labels:
                    return JsonResponse({"error": "Unknown priority."}, status=400)
                task.priority = value
                update_fields.append("priority")
            else:  # team grouping
                if value == "unassigned":
                    task.teams.clear()
                else:
                    try:
                        team = StaffTeam.objects.get(slug=value)
                    except StaffTeam.DoesNotExist:
                        return JsonResponse({"error": "Team not found."}, status=404)
                    # Add team if not already present
                    if not task.teams.filter(id=team.id).exists():
                        task.teams.add(team)
                    for member in task.assignees.all():
                        ensure_membership(team, member, request.user)

            task.save(update_fields=update_fields)

            target_group_value = normalised_group_value(task, group)
            try:
                resequence(target_order, group, target_group_value)
                if target_order and task.id in target_order:
                    task.board_position = target_order.index(task.id) + 1
                elif not task.board_position:
                    assign_board_position(task)

                if source_order:
                    if group == "team":
                        source_group_value = source_value or "unassigned"
                    else:
                        source_group_value = source_value or target_group_value
                    if source_group_value != target_group_value:
                        resequence(source_order, group, source_group_value)
            except OperationalError:
                pass

            board_position_value = getattr(task, "board_position", None)

    except StaffTask.DoesNotExist:
        return JsonResponse({"error": "Task not found."}, status=404)
    except OperationalError:
        board_position_value = None

    teams = list(task.teams.all())
    first_team = teams[0] if teams else None
    return JsonResponse(
        {
            "ok": True,
            "group": group,
            "value": value if group != "team" else (first_team.slug if first_team else "unassigned"),
            "task": {
                "id": task.id,
                "status": task.status,
                "status_label": status_labels[task.status],
                "priority": task.priority,
                "priority_label": priority_labels[task.priority],
                "progress": task.progress,
                "team": first_team.name if first_team else None,
                "team_slug": first_team.slug if first_team else "unassigned",
                "board_position": board_position_value,
            },
        }
    )


@login_required
def staff_task_modal(request, task_id: int):
    """Render or process the task modal for view/edit flows."""

    ensure_default_staff_teams()
    task = get_object_or_404(
        StaffTask.objects.select_related("created_by").prefetch_related("teams", "assignees"),
        pk=task_id,
    )

    if request.method == "POST":
        form = StaffTaskForm(request.POST, instance=task, request=request)
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_task = form.save(commit=False)
                    if (
                        updated_task.status == StaffTask.STATUS_COMPLETED
                        and not updated_task.completed_at
                    ):
                        updated_task.completed_at = timezone.now()
                        updated_task.progress = 100
                    elif (
                        updated_task.status != StaffTask.STATUS_COMPLETED
                        and updated_task.completed_at
                    ):
                        updated_task.completed_at = None
                    updated_task.save()
                    form.save_m2m()
                    try:
                        assign_board_position(updated_task)
                    except OperationalError:
                        pass
                    for member in updated_task.assignees.all():
                        for team in updated_task.teams.all():
                            ensure_membership(team, member, request.user)
            except OperationalError:
                pass

            headers = {
                "HX-Trigger": json.dumps(
                    {
                        "task-board-refresh": True,
                        "task-modal-close": True,
                    }
                )
            }
            return HttpResponse(status=204, headers=headers)
    else:
        form = StaffTaskForm(instance=task, request=request)

    context = {
        "task": task,
        "form": form,
        "status_labels": dict(StaffTask.STATUS_CHOICES),
        "priority_labels": dict(StaffTask.PRIORITY_CHOICES),
    }
    return render(request, "common/partials/staff_task_modal.html", context)


@login_required
@require_POST
def staff_task_delete(request, task_id: int):
    """Delete a staff task after explicit confirmation."""

    task = get_object_or_404(StaffTask, pk=task_id)
    if request.POST.get("confirm") != "yes":
        return JsonResponse({"error": "Confirmation required."}, status=400)

    task.delete()
    headers = {
        "HX-Trigger": json.dumps(
            {
                "task-board-refresh": True,
                "task-modal-close": True,
            }
        )
    }
    return HttpResponse(status=204, headers=headers)


@login_required
@require_POST
def staff_task_update_field(request, task_id: int):
    """Update a single field of a task via AJAX for Notion-style inline editing."""

    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)

    if not field or value is None:
        return JsonResponse({'success': False, 'error': 'Field and value required'}, status=400)

    try:
        task = StaffTask.objects.select_for_update().get(pk=task_id)
    except StaffTask.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

    # Validate and update the field
    try:
        with transaction.atomic():
            update_fields = ['updated_at']

            if field == 'title':
                task.title = value.strip()
                update_fields.append('title')

            elif field == 'progress':
                try:
                    progress_value = int(value)
                    if 0 <= progress_value <= 100:
                        task.progress = progress_value
                        update_fields.append('progress')

                        # Auto-complete task if progress is 100%
                        if progress_value == 100 and task.status != StaffTask.STATUS_COMPLETED:
                            task.status = StaffTask.STATUS_COMPLETED
                            task.completed_at = timezone.now()
                            update_fields.extend(['status', 'completed_at'])
                    else:
                        return JsonResponse({'success': False, 'error': 'Progress must be between 0 and 100'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'success': False, 'error': 'Invalid progress value'}, status=400)

            elif field == 'status':
                status_choices = [choice[0] for choice in StaffTask.STATUS_CHOICES]
                if value in status_choices:
                    task.status = value
                    update_fields.append('status')

                    # Set completed_at when marking as completed
                    if value == StaffTask.STATUS_COMPLETED and not task.completed_at:
                        task.completed_at = timezone.now()
                        update_fields.append('completed_at')
                        task.progress = 100
                        update_fields.append('progress')
                    elif value != StaffTask.STATUS_COMPLETED:
                        task.completed_at = None
                        update_fields.append('completed_at')
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid status value'}, status=400)

            elif field == 'priority':
                priority_choices = [choice[0] for choice in StaffTask.PRIORITY_CHOICES]
                if value in priority_choices:
                    task.priority = value
                    update_fields.append('priority')
                else:
                    return JsonResponse({'success': False, 'error': 'Invalid priority value'}, status=400)

            elif field == 'start_date':
                if value:
                    try:
                        parsed_date = timezone.datetime.strptime(value, '%Y-%m-%d').date()
                        task.start_date = parsed_date
                        update_fields.append('start_date')
                    except ValueError:
                        return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)
                else:
                    task.start_date = None
                    update_fields.append('start_date')

            elif field == 'due_date':
                if value:
                    try:
                        parsed_date = timezone.datetime.strptime(value, '%Y-%m-%d').date()
                        task.due_date = parsed_date
                        update_fields.append('due_date')
                    except ValueError:
                        return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)
                else:
                    task.due_date = None
                    update_fields.append('due_date')

            elif field == 'assignees':
                # Handle assignees as comma-separated IDs
                if value:
                    assignee_ids = [int(id.strip()) for id in value.split(',') if id.strip()]
                    try:
                        assignees = User.objects.filter(id__in=assignee_ids)
                        task.assignees.set(assignees)
                        # Ensure team membership for all assignees
                        for member in assignees:
                            for team in task.teams.all():
                                ensure_membership(team, member, request.user)
                    except (ValueError, TypeError):
                        return JsonResponse({'success': False, 'error': 'Invalid assignee IDs'}, status=400)
                else:
                    task.assignees.clear()

            elif field == 'teams':
                # Handle teams as comma-separated IDs
                if value:
                    team_ids = [int(id.strip()) for id in value.split(',') if id.strip()]
                    try:
                        teams = StaffTeam.objects.filter(id__in=team_ids)
                        task.teams.set(teams)
                        # Ensure team membership for all assignees
                        for member in task.assignees.all():
                            for team in teams:
                                ensure_membership(team, member, request.user)
                    except (ValueError, TypeError):
                        return JsonResponse({'success': False, 'error': 'Invalid team IDs'}, status=400)
                else:
                    task.teams.clear()

            else:
                return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

            # Save the task
            task.save(update_fields=update_fields)

            # Try to update board position
            try:
                assign_board_position(task)
            except OperationalError:
                pass

        return JsonResponse({
            'success': True,
            'field': field,
            'value': value,
            'task_id': task.id
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def staff_api_assignees(request):
    """API endpoint to get staff members for assignee dropdown."""
    # Define staff user types
    STAFF_USER_TYPES = ["admin", "oobc_staff"]

    staff_members = User.objects.filter(
        user_type__in=STAFF_USER_TYPES,
        is_active=True
    ).order_by('last_name', 'first_name')

    data = []
    for member in staff_members:
        initials = ""
        if member.first_name and member.last_name:
            initials = f"{member.first_name[0]}{member.last_name[0]}".upper()
        elif member.first_name:
            initials = member.first_name[0].upper()
        elif member.last_name:
            initials = member.last_name[0].upper()
        else:
            initials = member.username[0].upper() if member.username else "?"

        full_name = f"{member.first_name} {member.last_name}".strip()
        if not full_name:
            full_name = member.username

        data.append({
            'id': member.id,
            'name': full_name,
            'initials': initials,
            'username': member.username
        })

    return JsonResponse({'staff': data})


@login_required
def staff_api_teams(request):
    """API endpoint to get teams for team dropdown."""
    teams = StaffTeam.objects.filter(is_active=True).order_by('name')

    # Color mapping for teams
    team_colors = [
        'bg-blue-100 text-blue-800',
        'bg-green-100 text-green-800',
        'bg-purple-100 text-purple-800',
        'bg-orange-100 text-orange-800',
        'bg-pink-100 text-pink-800',
        'bg-yellow-100 text-yellow-800',
        'bg-red-100 text-red-800',
        'bg-indigo-100 text-indigo-800'
    ]

    data = []
    for i, team in enumerate(teams):
        data.append({
            'id': team.id,
            'name': team.name,
            'slug': team.slug,
            'color': team_colors[i % len(team_colors)]
        })

    return JsonResponse({'teams': data})


@login_required
def staff_task_inline_update(request, task_id: int):
    """Inline edit handler for the table view."""

    task = get_object_or_404(
        StaffTask.objects.prefetch_related("teams", "assignees"), pk=task_id
    )

    if request.method != "POST":
        return redirect("common:staff_task_board")

    form = StaffTaskForm(
        request.POST,
        instance=task,
        request=request,
        table_mode=True,
    )
    if form.is_valid():
        try:
            with transaction.atomic():
                updated_task = form.save(commit=False)
                if (
                    updated_task.status == StaffTask.STATUS_COMPLETED
                    and not updated_task.completed_at
                ):
                    updated_task.completed_at = timezone.now()
                    updated_task.progress = 100
                elif (
                    updated_task.status != StaffTask.STATUS_COMPLETED
                    and updated_task.completed_at
                ):
                    updated_task.completed_at = None
                updated_task.save()
                form.save_m2m()
                try:
                    assign_board_position(updated_task)
                except OperationalError:
                    pass
                for member in updated_task.assignees.all():
                    for team in updated_task.teams.all():
                        ensure_membership(team, member, request.user)
        except OperationalError:
            pass

        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect("common:staff_task_board")

    assignee_tokens, team_tokens = _task_relation_tokens(task)

    context = {
        "task": task,
        "form": form,
        "status_labels": dict(StaffTask.STATUS_CHOICES),
        "priority_labels": dict(StaffTask.PRIORITY_CHOICES),
        "assignee_tokens": assignee_tokens,
        "team_tokens": team_tokens,
    }
    return render(request, "common/partials/staff_task_table_row.html", context)


@login_required
def staff_team_assign(request):
    """Dedicated interface for mapping staff members to teams."""

    ensure_default_staff_teams()
    form = StaffTeamMembershipForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        membership = form.save(commit=False)
        if not membership.assigned_by:
            membership.assigned_by = request.user
        membership.save()
        messages.success(
            request,
            f"{membership.user.get_full_name()} linked to {membership.team.name}.",
        )
        return redirect("common:staff_team_assign")

    assignments = (
        StaffTeamMembership.objects.select_related("team", "user")
        .order_by("team__name", "user__last_name")
    )

    context = {
        "form": form,
        "assignments": assignments,
    }
    return render(request, "common/staff_team_assign.html", context)


@login_required
def staff_team_manage(request):
    """Dedicated interface for creating or updating staff teams."""

    ensure_default_staff_teams()
    team = None
    team_id = request.GET.get("team_id")
    if team_id:
        team = get_object_or_404(StaffTeam, pk=team_id)

    form_name = request.POST.get("form_name") if request.method == "POST" else None
    is_team_form = request.method == "POST" and form_name in (None, "", "team")
    team_form_kwargs = {"instance": team}
    if is_team_form:
        form = StaffTeamForm(request.POST, **team_form_kwargs)
    else:
        form = StaffTeamForm(**team_form_kwargs)

    if is_team_form and form.is_valid():
        saved_team = form.save()
        action = "updated" if team else "created"
        messages.success(request, f"Team \"{saved_team.name}\" {action} successfully.")
        redirect_url = reverse("common:staff_team_manage")
        if saved_team.pk:
            redirect_url = f"{redirect_url}?team_id={saved_team.pk}"
        return redirect(redirect_url)

    membership_form_initial: dict[str, object] = {}
    if team:
        membership_form_initial["team"] = team

    is_membership_form = request.method == "POST" and form_name == "membership"
    membership_form_kwargs = {"request": request, "initial": membership_form_initial}
    if is_membership_form:
        membership_form = StaffTeamMembershipForm(request.POST, **membership_form_kwargs)
        if membership_form.is_valid():
            membership = membership_form.save(commit=False)
            if not membership.assigned_by:
                membership.assigned_by = request.user
            membership.save()
            messages.success(
                request,
                f"{membership.user.get_full_name()} linked to {membership.team.name}.",
            )
            redirect_url = reverse("common:staff_team_manage")
            if membership.team_id:
                redirect_url = f"{redirect_url}?team_id={membership.team_id}"
            return redirect(redirect_url)
    else:
        membership_form = StaffTeamMembershipForm(**membership_form_kwargs)

    teams = StaffTeam.objects.all().order_by("name")
    team_metrics = [
        {
            "team": record,
            "member_count": record.memberships.filter(is_active=True).count(),
            "active_tasks": record.tasks.exclude(status=StaffTask.STATUS_COMPLETED).count(),
            "completion_rate": _completion_rate(record.tasks.all()),
        }
        for record in teams
    ]

    assignments = (
        StaffTeamMembership.objects.select_related("team", "user")
        .order_by("team__name", "user__last_name", "user__first_name")
    )
    if team:
        assignments = assignments.filter(team=team)

    team_research_snapshot = None
    if team:
        focus_values = team.focus_areas if isinstance(team.focus_areas, list) else list(team.focus_areas or [])
        focus_tags = [value for value in focus_values if value]
        active_memberships = team.memberships.filter(is_active=True)
        role_labels = dict(StaffTeamMembership.ROLE_CHOICES)
        role_breakdown = (
            active_memberships.values("role")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        team_research_snapshot = {
            "description": (team.description or "").strip(),
            "mission": (team.mission or "").strip(),
            "focus_areas": focus_tags,
            "active_members": active_memberships.count(),
            "role_breakdown": [
                {
                    "label": role_labels.get(row["role"], row["role"]),
                    "total": row["total"],
                }
                for row in role_breakdown
            ],
        }

    context = {
        "form": form,
        "membership_form": membership_form,
        "assignments": assignments,
        "teams": team_metrics,
        "selected_team": team,
        "team_research_snapshot": team_research_snapshot,
        "wide_fields": {"description", "mission", "focus_areas"},
    }
    return render(request, "common/staff_team_manage.html", context)


@login_required
def staff_profiles_list(request):
    """List and filter staff profiles with quick insights."""

    ensure_default_staff_teams()

    staff_users_qs = staff_queryset().order_by("last_name", "first_name")
    ensure_staff_profiles_for_users(staff_users_qs)

    profiles_qs = (
        StaffProfile.objects.select_related("user")
        .prefetch_related("user__team_memberships__team")
        .order_by("user__last_name", "user__first_name")
    )

    status_filter = request.GET.get("status", "")
    team_filter = request.GET.get("team", "")
    search_query = request.GET.get("q", "")

    status_choices = dict(StaffProfile.EMPLOYMENT_STATUS_CHOICES)

    if status_filter in status_choices:
        profiles_qs = profiles_qs.filter(employment_status=status_filter)

    if team_filter:
        profiles_qs = profiles_qs.filter(
            user__team_memberships__team__slug=team_filter,
            user__team_memberships__is_active=True,
        )

    if search_query:
        profiles_qs = profiles_qs.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(user__position__icontains=search_query)
            | Q(primary_location__icontains=search_query)
        )

    profiles_qs = profiles_qs.distinct()

    profiles: list[StaffProfile] = list(profiles_qs)

    for profile in profiles:
        raw_name = profile.user.get_full_name() or profile.user.username
        profile.directory_display_name = (raw_name or "").replace("staff", "Staff")
        username_value = profile.user.username or ""
        profile.directory_username_display = username_value.replace("staff", "Staff")
        raw_position = (profile.user.position or "").strip()
        if raw_position:
            display_name = (profile.directory_display_name or "").strip()
            normalized_position = re.sub(r"\s+", " ", raw_position).strip()
            normalized_display = re.sub(r"\s+", " ", display_name).strip()
            if normalized_position.lower() == normalized_display.lower():
                profile.directory_position_display = ""
            elif normalized_display and normalized_position.lower().startswith(normalized_display.lower()):
                suffix = raw_position[len(display_name) :]
                profile.directory_position_display = suffix.lstrip(" -–—:|,.").strip()
            else:
                profile.directory_position_display = raw_position
        else:
            profile.directory_position_display = None

    status_totals = (
        StaffProfile.objects.values("employment_status")
        .annotate(total=Count("id"))
        .order_by()
    )
    status_totals_map = {row["employment_status"]: row["total"] for row in status_totals}
    total_profiles = StaffProfile.objects.count()
    available_staff = (
        User.objects.filter(user_type__in=STAFF_USER_TYPES)
        .filter(staff_profile__isnull=True)
        .count()
    )

    team_options = StaffTeam.objects.filter(is_active=True).order_by("name")

    stats_payload = {
        "total": total_profiles,
        "active": status_totals_map.get(StaffProfile.STATUS_ACTIVE, 0),
        "on_leave": status_totals_map.get(StaffProfile.STATUS_ON_LEAVE, 0),
        "inactive": status_totals_map.get(StaffProfile.STATUS_INACTIVE, 0),
        "unassigned": available_staff,
    }

    stat_cards = [
        {
            "title": "Total staff profiles",
            "value": stats_payload["total"],
            "icon": "fas fa-id-card-alt",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "text_color": "text-emerald-100",
        },
        {
            "title": "Active staff",
            "value": stats_payload["active"],
            "icon": "fas fa-user-check",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "text_color": "text-blue-100",
        },
        {
            "title": "On leave",
            "value": stats_payload["on_leave"],
            "icon": "fas fa-plane-departure",
            "gradient": "from-amber-500 via-amber-600 to-amber-700",
            "text_color": "text-amber-100",
        },
        {
            "title": "Inactive or archived",
            "value": stats_payload["inactive"],
            "icon": "fas fa-user-slash",
            "gradient": "from-rose-500 via-rose-600 to-rose-700",
            "text_color": "text-rose-100",
        },
        {
            "title": "Staff without profiles",
            "value": stats_payload["unassigned"],
            "icon": "fas fa-user-plus",
            "gradient": "from-sky-500 via-sky-600 to-sky-700",
            "text_color": "text-sky-100",
        },
    ]

    if len(stat_cards) >= 5:
        stat_cards_grid_class = "mb-8 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6"
    elif len(stat_cards) == 4:
        stat_cards_grid_class = "mb-8 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6"
    else:
        stat_cards_grid_class = "mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"

    context = {
        "profiles": profiles,
        "status_filter": status_filter,
        "team_filter": team_filter,
        "search_query": search_query,
        "status_choices": StaffProfile.EMPLOYMENT_STATUS_CHOICES,
        "team_options": team_options,
        "stats": stats_payload,
        "stat_cards": stat_cards,
        "stat_cards_grid_class": stat_cards_grid_class,
    }
    return render(request, "common/staff_profiles_list.html", context)


@login_required
def staff_profile_create(request):
    """Create a staff profile entry."""

    available_staff = (
        User.objects.filter(user_type__in=STAFF_USER_TYPES)
        .filter(staff_profile__isnull=True)
        .order_by("last_name", "first_name")
    )

    form = StaffProfileForm(request.POST or None, request=request)
    form.fields["user"].queryset = available_staff

    if request.method == "POST" and form.is_valid():
        profile = form.save()
        messages.success(
            request,
            f"Profile for {profile.user.get_full_name()} created successfully.",
        )
        return redirect("common:staff_profiles_list")

    context = {
        "form": form,
        "form_title": "Add Staff Profile",
        "available_staff_count": available_staff.count(),
    }
    return render(request, "common/staff_profile_form.html", context)


@login_required
def staff_profile_update(request, pk):
    """Update an existing staff profile."""

    profile = get_object_or_404(
        StaffProfile.objects.select_related("user"), pk=pk
    )
    form = StaffProfileForm(request.POST or None, instance=profile, request=request)
    form.fields["user"].queryset = User.objects.filter(pk=profile.user_id)
    form.fields["user"].widget = forms.HiddenInput()
    form.fields["user"].initial = profile.user

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            f"Profile for {profile.user.get_full_name()} updated successfully.",
        )
        return redirect("common:staff_profiles_detail", pk=profile.pk)

    context = {
        "form": form,
        "form_title": f"Edit Profile · {profile.user.get_full_name()}",
        "profile": profile,
        "available_staff_count": None,
    }
    return render(request, "common/staff_profile_form.html", context)


@login_required
def staff_profiles_detail(request, pk):
    """Display staff profile information organised into tabs."""

    profile = get_object_or_404(
        StaffProfile.objects.select_related("user"), pk=pk
    )

    tab_definitions = (
        {
            "key": "overview",
            "label": "Overview",
            "icon": "fas fa-layer-group",
        },
        {
            "key": "job",
            "label": "Job Description",
            "icon": "fas fa-briefcase",
        },
        {
            "key": "competency",
            "label": "Competency Framework",
            "icon": "fas fa-lightbulb",
        },
        {
            "key": "performance",
            "label": "Performance Dashboard",
            "icon": "fas fa-chart-line",
        },
        {
            "key": "tasks",
            "label": "Assigned Tasks",
            "icon": "fas fa-tasks",
        },
    )

    requested_tab = (request.GET.get("tab") or "overview").lower()
    allowed_tab_keys = {tab["key"] for tab in tab_definitions}
    active_tab = requested_tab if requested_tab in allowed_tab_keys else "overview"

    detail_url = reverse("common:staff_profiles_detail", args=[profile.pk])
    tabs = [
        {
            **tab,
            "url": detail_url
            if tab["key"] == "overview"
            else f"{detail_url}?tab={tab['key']}",
            "is_active": tab["key"] == active_tab,
        }
        for tab in tab_definitions
    ]

    active_memberships = (
        profile.user.team_memberships.select_related("team")
        .filter(is_active=True)
        .order_by("team__name")
    )

    recent_tasks = (
        StaffTask.objects.filter(assignees=profile.user)
        .prefetch_related("teams", "assignees")
        .order_by("-updated_at")[:10]
    )
    trainings = profile.training_enrollments.select_related("program")
    development_plans = profile.development_plans.all()
    performance_targets = profile.performance_targets.select_related("team")

    tasks_by_status = {
        label: profile.user.assigned_staff_tasks.filter(status=status).count()
        for status, label in StaffTask.STATUS_CHOICES
    }

    context = {
        "profile": profile,
        "memberships": active_memberships,
        "recent_tasks": recent_tasks,
        "trainings": trainings,
        "development_plans": development_plans,
        "performance_targets": performance_targets,
        "competency_categories": STAFF_COMPETENCY_CATEGORIES,
        "competency_levels": STAFF_COMPETENCY_PROFICIENCY_LEVELS,
        "tasks_by_status": tasks_by_status,
        "tabs": tabs,
        "active_tab": active_tab,
    }
    return render(request, "common/staff_profile_detail.html", context)


@login_required
def staff_profile_delete(request, pk):
    """Delete a staff profile after confirmation."""

    profile = get_object_or_404(
        StaffProfile.objects.select_related("user"), pk=pk
    )

    if request.method == "POST":
        staff_name = profile.user.get_full_name()
        profile.delete()
        messages.success(request, f"Profile for {staff_name} removed.")
        return redirect("common:staff_profiles_list")

    context = {
        "profile": profile,
    }
    return render(request, "common/staff_profile_confirm_delete.html", context)


@login_required
def staff_performance_dashboard(request):
    """Dashboard for staff and team performance targets."""

    ensure_default_staff_teams()

    form = PerformanceTargetForm()
    if request.method == "POST" and request.POST.get("form_name") == "performance_target":
        form = PerformanceTargetForm(request.POST)
        if form.is_valid():
            target = form.save()
            messages.success(
                request,
                f"Performance target for {target.metric_name} saved successfully.",
            )
            return redirect("common:staff_performance_dashboard")

    targets_qs = PerformanceTarget.objects.select_related(
        "staff_profile__user", "team"
    ).order_by("-updated_at")

    scope_filter = request.GET.get("scope", "")
    status_filter = request.GET.get("status", "")
    team_filter = request.GET.get("team", "")
    staff_filter = request.GET.get("staff", "")

    if scope_filter in dict(PerformanceTarget.SCOPE_CHOICES):
        targets_qs = targets_qs.filter(scope=scope_filter)
    if status_filter in dict(PerformanceTarget.STATUS_CHOICES):
        targets_qs = targets_qs.filter(status=status_filter)
    if team_filter:
        targets_qs = targets_qs.filter(team__slug=team_filter)
    if staff_filter:
        targets_qs = targets_qs.filter(staff_profile_id=staff_filter)

    metrics = {
        "total": targets_qs.count(),
        "on_track": targets_qs.filter(status=PerformanceTarget.STATUS_ON_TRACK).count(),
        "at_risk": targets_qs.filter(status=PerformanceTarget.STATUS_AT_RISK).count(),
        "off_track": targets_qs.filter(status=PerformanceTarget.STATUS_OFF_TRACK).count(),
    }

    staff_map: dict[int, dict] = {}
    team_map: dict[int, dict] = {}

    for target in targets_qs:
        if target.scope == PerformanceTarget.SCOPE_STAFF and target.staff_profile_id:
            entry = staff_map.setdefault(
                target.staff_profile_id,
                {
                    "profile": target.staff_profile,
                    "targets": [],
                    "target_total": 0.0,
                    "actual_total": 0.0,
                    "on_track": 0,
                    "at_risk": 0,
                    "off_track": 0,
                },
            )
            entry["targets"].append(target)
            entry["target_total"] += float(target.target_value)
            entry["actual_total"] += float(target.actual_value)
            entry[target.status] += 1
        elif target.scope == PerformanceTarget.SCOPE_TEAM and target.team_id:
            entry = team_map.setdefault(
                target.team_id,
                {
                    "team": target.team,
                    "targets": [],
                    "target_total": 0.0,
                    "actual_total": 0.0,
                    "on_track": 0,
                    "at_risk": 0,
                    "off_track": 0,
                },
            )
            entry["targets"].append(target)
            entry["target_total"] += float(target.target_value)
            entry["actual_total"] += float(target.actual_value)
            entry[target.status] += 1

    staff_rows = sorted(
        staff_map.values(),
        key=lambda item: item["profile"].user.get_full_name().lower(),
    )
    team_rows = sorted(
        team_map.values(), key=lambda item: item["team"].name.lower()
    )

    context = {
        "form": form,
        "targets": targets_qs,
        "metrics": metrics,
        "staff_rows": staff_rows,
        "team_rows": team_rows,
        "filters": {
            "scope": scope_filter,
            "status": status_filter,
            "team": team_filter,
            "staff": staff_filter,
        },
        "scope_choices": PerformanceTarget.SCOPE_CHOICES,
        "status_choices": PerformanceTarget.STATUS_CHOICES,
        "teams": StaffTeam.objects.order_by("name"),
        "staff_profiles": StaffProfile.objects.select_related("user").order_by(
            "user__last_name", "user__first_name"
        ),
    }
    return render(request, "common/staff_performance_dashboard.html", context)


@login_required
def staff_training_development(request):
    """Training catalogue, enrollments, and development plans."""

    ensure_default_staff_teams()

    program_form = TrainingProgramForm(prefix="program")
    enrollment_form = TrainingEnrollmentForm(prefix="enroll")
    development_form = StaffDevelopmentPlanForm(prefix="plan")

    if request.method == "POST":
        form_name = request.POST.get("form_name")
        if form_name == "program":
            program_form = TrainingProgramForm(request.POST, prefix="program")
            if program_form.is_valid():
                program = program_form.save()
                messages.success(
                    request,
                    f"Training programme \"{program.title}\" saved successfully.",
                )
                return redirect("common:staff_training_development")
        elif form_name == "enrollment":
            enrollment_form = TrainingEnrollmentForm(
                request.POST, prefix="enroll"
            )
            if enrollment_form.is_valid():
                enrollment = enrollment_form.save()
                messages.success(
                    request,
                    f"Enrollment for {enrollment.staff_profile.user.get_full_name()} saved successfully.",
                )
                return redirect("common:staff_training_development")
        elif form_name == "plan":
            development_form = StaffDevelopmentPlanForm(
                request.POST, prefix="plan"
            )
            if development_form.is_valid():
                plan = development_form.save()
                messages.success(
                    request,
                    f"Development plan \"{plan.title}\" captured.",
                )
                return redirect("common:staff_training_development")

    programs = TrainingProgram.objects.order_by("title")
    enrollments = TrainingEnrollment.objects.select_related(
        "staff_profile__user", "program"
    ).order_by("scheduled_date")
    development_plans = StaffDevelopmentPlan.objects.select_related(
        "staff_profile__user"
    ).order_by("status", "target_date")

    status_totals = enrollments.values("status").annotate(total=Count("id"))
    status_map = {row["status"]: row["total"] for row in status_totals}

    context = {
        "program_form": program_form,
        "enrollment_form": enrollment_form,
        "development_form": development_form,
        "programs": programs,
        "enrollments": enrollments,
        "development_plans": development_plans,
        "enrollment_status_totals": status_map,
        "competency_categories": STAFF_COMPETENCY_CATEGORIES,
    }
    return render(request, "common/staff_training_development.html", context)


def _completion_rate(tasks):
    total = tasks.count()
    if not total:
        return 0
    completed = tasks.filter(status=StaffTask.STATUS_COMPLETED).count()
    return round((completed / total) * 100)


ZERO_DECIMAL = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
ZERO_FLOAT = Value(0, output_field=FloatField())


@login_required
def planning_budgeting(request):
    """Planning and budgeting dashboard summarising PPAs and allocations."""
    entries = MonitoringEntry.objects.select_related(
        "lead_organization",
        "submitted_by_community",
    ).prefetch_related("funding_flows", "workflow_stages")
    today = timezone.now().date()

    totals = entries.aggregate(
        budget_total=Coalesce(Sum("budget_allocation"), ZERO_DECIMAL),
        budget_obc_total=Coalesce(Sum("budget_obc_allocation"), ZERO_DECIMAL),
        budget_ceiling_total=Coalesce(Sum("budget_ceiling"), ZERO_DECIMAL),
        projects=Count("id"),
        avg_progress=Coalesce(Avg("progress"), ZERO_FLOAT),
    )

    funding_totals = MonitoringEntryFunding.objects.aggregate(
        allocation_total=Coalesce(
            Sum(
                "amount",
                filter=Q(
                    tranche_type=MonitoringEntryFunding.TRANCHE_ALLOCATION
                ),
            ),
            ZERO_DECIMAL,
        ),
        obligation_total=Coalesce(
            Sum(
                "amount",
                filter=Q(
                    tranche_type=MonitoringEntryFunding.TRANCHE_OBLIGATION
                ),
            ),
            ZERO_DECIMAL,
        ),
        disbursement_total=Coalesce(
            Sum(
                "amount",
                filter=Q(
                    tranche_type=MonitoringEntryFunding.TRANCHE_DISBURSEMENT
                ),
            ),
            ZERO_DECIMAL,
        ),
    )

    totals.update(funding_totals)

    is_empty_state = totals["projects"] == 0

    category_labels = dict(MonitoringEntry.CATEGORY_CHOICES)
    status_labels = dict(MonitoringEntry.STATUS_CHOICES)
    sector_labels = dict(MonitoringEntry.SECTOR_CHOICES)
    appropriation_labels = dict(MonitoringEntry.APPROPRIATION_CLASS_CHOICES)
    funding_labels = dict(MonitoringEntry.FUNDING_SOURCE_CHOICES)

    category_breakdown = [
        {
            "key": row["category"],
            "label": category_labels.get(row["category"], row["category"]),
            "projects": row["projects"],
            "total_budget": row["total_budget"],
            "avg_progress": row["avg_progress"],
        }
        for row in entries.values("category")
        .annotate(
            projects=Count("id"),
            total_budget=Coalesce(Sum("budget_allocation"), ZERO_DECIMAL),
            avg_progress=Coalesce(Avg("progress"), ZERO_FLOAT),
        )
        .order_by("category")
    ]

    status_breakdown = [
        {
            "key": row["status"],
            "label": status_labels.get(row["status"], row["status"]),
            "projects": row["projects"],
            "budget": row["budget"],
        }
        for row in entries.values("status")
        .annotate(
            projects=Count("id"),
            budget=Coalesce(Sum("budget_allocation"), ZERO_DECIMAL),
        )
        .order_by("status")
    ]

    sector_breakdown = [
        {
            "key": row["sector"],
            "label": sector_labels.get(row["sector"], "Unspecified"),
            "projects": row["projects"],
            "budget": row["budget"],
            "ceiling": row["ceiling"],
        }
        for row in entries.values("sector")
        .annotate(
            projects=Count("id"),
            budget=Coalesce(Sum("budget_allocation"), ZERO_DECIMAL),
            ceiling=Coalesce(Sum("budget_ceiling"), ZERO_DECIMAL),
        )
        .order_by("sector")
    ]

    appropriation_breakdown = [
        {
            "key": row["appropriation_class"],
            "label": appropriation_labels.get(
                row["appropriation_class"], "Unspecified"
            ),
            "projects": row["projects"],
            "budget": row["budget"],
        }
        for row in entries.values("appropriation_class")
        .annotate(
            projects=Count("id"),
            budget=Coalesce(Sum("budget_allocation"), ZERO_DECIMAL),
        )
        .order_by("appropriation_class")
    ]

    funding_breakdown = [
        {
            "key": row["funding_source"],
            "label": funding_labels.get(row["funding_source"], "Unspecified"),
            "projects": row["projects"],
            "budget": row["budget"],
        }
        for row in entries.values("funding_source")
        .annotate(
            projects=Count("id"),
            budget=Coalesce(Sum("budget_allocation"), ZERO_DECIMAL),
        )
        .order_by("funding_source")
    ]

    compliance_summary = {
        "total": totals["projects"],
        "gad": entries.filter(compliance_gad=True).count(),
        "ccet": entries.filter(compliance_ccet=True).count(),
        "ip": entries.filter(benefits_indigenous_peoples=True).count(),
        "peace": entries.filter(supports_peace_agenda=True).count(),
        "sdg": entries.filter(supports_sdg=True).count(),
    }
    total_projects = compliance_summary["total"] or 0

    def _pct(count: int) -> float:
        if not total_projects:
            return 0
        return round((count / total_projects) * 100, 1)

    compliance_summary.update(
        {
            "gad_pct": _pct(compliance_summary["gad"]),
            "ccet_pct": _pct(compliance_summary["ccet"]),
            "ip_pct": _pct(compliance_summary["ip"]),
            "peace_pct": _pct(compliance_summary["peace"]),
            "sdg_pct": _pct(compliance_summary["sdg"]),
        }
    )

    top_allocations = (
        entries.select_related("lead_organization", "submitted_by_community")
        .exclude(budget_allocation__isnull=True)
        .exclude(budget_allocation=0)
        .order_by("-budget_allocation")[:10]
    )

    upcoming_milestones = (
        entries.filter(next_milestone_date__isnull=False, next_milestone_date__gte=today)
        .order_by("next_milestone_date")[:10]
    )

    workflow_stage_labels = dict(MonitoringEntryWorkflowStage.STAGE_CHOICES)
    workflow_status_labels = dict(MonitoringEntryWorkflowStage.STATUS_CHOICES)

    workflow_summary_raw = (
        MonitoringEntryWorkflowStage.objects.values("stage", "status")
        .annotate(total=Count("id"))
        .order_by("stage", "status")
    )

    workflow_summary_map = defaultdict(lambda: {"total": 0, "statuses": {}})
    for row in workflow_summary_raw:
        stage_key = row["stage"]
        status_key = row["status"]
        stage_record = workflow_summary_map[stage_key]
        stage_record["label"] = workflow_stage_labels.get(stage_key, stage_key)
        stage_record["total"] += row["total"]
        stage_record["statuses"][status_key] = {
            "label": workflow_status_labels.get(status_key, status_key),
            "count": row["total"],
        }

    stage_order = [stage for stage, _label in MonitoringEntryWorkflowStage.STAGE_CHOICES]
    status_order = [status for status, _label in MonitoringEntryWorkflowStage.STATUS_CHOICES]

    workflow_summary = [
        {
            "stage": stage,
            "label": workflow_summary_map[stage].get("label", stage),
            "total": workflow_summary_map[stage]["total"],
            "statuses": [
                {
                    "key": status,
                    "label": workflow_summary_map[stage]["statuses"][status]["label"],
                    "count": workflow_summary_map[stage]["statuses"][status]["count"],
                }
                for status in status_order
                if status in workflow_summary_map[stage]["statuses"]
            ],
        }
        for stage in stage_order
        if stage in workflow_summary_map
    ]

    funding_timeline = (
        MonitoringEntryFunding.objects.select_related("entry")
        .exclude(scheduled_date__isnull=True)
        .order_by("scheduled_date")[:20]
    )

    gap_candidates = list(
        entries.filter(priority__in=["high", "urgent"]).order_by("-priority", "-updated_at")
    )
    needs_gap_entries = []
    for item in gap_candidates:
        alignment = item.goal_alignment or []
        if not item.related_assessment or not alignment:
            needs_gap_entries.append(item)
        if len(needs_gap_entries) >= 5:
            break

    empty_state_links = []
    if is_empty_state:
        empty_state_links = [
            {
                "label": "Encode MOA Project",
                "description": "Capture BARMM ministry PPAs funded through MOAs.",
                "url": reverse("monitoring:create_moa"),
                "icon": "fa-handshake",
            },
            {
                "label": "Log OOBC Initiative",
                "description": "Track internal OOBC-led programmes and budgets.",
                "url": reverse("monitoring:create_oobc"),
                "icon": "fa-seedling",
            },
            {
                "label": "Record Community Request",
                "description": "Document proposals directly raised by Other Bangsamoro Communities.",
                "url": reverse("monitoring:create_request"),
                "icon": "fa-people-carry-box",
            },
        ]

    context = {
        "totals": totals,
        "category_breakdown": category_breakdown,
        "status_breakdown": status_breakdown,
        "sector_breakdown": sector_breakdown,
        "appropriation_breakdown": appropriation_breakdown,
        "funding_breakdown": funding_breakdown,
        "compliance_summary": compliance_summary,
        "top_allocations": top_allocations,
        "upcoming_milestones": upcoming_milestones,
        "workflow_summary": workflow_summary,
        "funding_timeline": funding_timeline,
        "needs_gap_entries": needs_gap_entries,
        "today": today,
        "is_empty_state": is_empty_state,
        "empty_state_links": empty_state_links,
    }
    return render(request, "common/oobc_planning_budgeting.html", context)


@login_required
@require_POST
def staff_task_delete(request, task_id):
    """Delete a staff task."""
    task = get_object_or_404(StaffTask, pk=task_id)

    # Check if this is a confirmation request
    if request.POST.get('confirm') == 'yes':
        task_title = task.title
        task.delete()

        # For HTMX requests, return 204 response to trigger delete swap and close modal
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                'task-board-refresh': True,
                'task-modal-close': True,
                'show-toast': f'Task "{task_title}" deleted successfully'
            })
            return response

        # For regular requests, add Django message and redirect to the task board
        messages.success(request, f'Task "{task_title}" has been deleted.')
        return redirect('common:staff_task_board')

    # If not confirmed, return an error or redirect
    if request.headers.get('HX-Request'):
        return JsonResponse({"error": "Confirmation required."}, status=400)

    messages.error(request, 'Task deletion was not confirmed.')
    return redirect('common:staff_task_board')


@login_required
@require_POST
def staff_task_create_api(request):
    """API endpoint for creating tasks via AJAX - returns JSON."""

    ensure_default_staff_teams()

    if request.content_type == 'application/json':
        data = json.loads(request.body.decode('utf-8'))
        form_data = data
    else:
        form_data = request.POST

    form = StaffTaskForm(form_data, request=request, table_mode=True)

    if form.is_valid():
        try:
            with transaction.atomic():
                task = form.save(commit=False)
                if not task.created_by:
                    task.created_by = request.user
                if (
                    task.status == StaffTask.STATUS_COMPLETED
                    and not task.completed_at
                ):
                    task.completed_at = timezone.now()
                    task.progress = 100
                task.save()
                form.save_m2m()
                try:
                    assign_board_position(task)
                except OperationalError:
                    pass
                for member in task.assignees.all():
                    for team in task.teams.all():
                        ensure_membership(team, member, request.user)

                # Prepare task data for JSON response
                assignee_tokens, team_tokens = _task_relation_tokens(task)
                task_data = {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'priority': task.priority,
                    'progress': task.progress,
                    'start_date': task.start_date.isoformat() if task.start_date else None,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'assignees': [{'id': token['id'], 'label': token['label']} for token in assignee_tokens],
                    'teams': [{'id': token['id'], 'label': token['label']} for token in team_tokens],
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat(),
                }

                return JsonResponse({
                    'success': True,
                    'task': task_data,
                    'message': f'Task "{task.title}" created successfully.'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'error': 'Form validation failed',
            'errors': form.errors
        }, status=400)


@login_required
def user_approvals(request):
    """User approval management page - review and approve pending user accounts."""

    # Restrict to authorized approvers only
    if not _can_approve_users(request.user):
        return redirect("common:page_restricted")

    # Get all pending users ordered by registration date
    pending_users = User.objects.filter(is_approved=False).order_by("-date_joined")

    # Get recently approved users for reference
    recently_approved = User.objects.filter(is_approved=True).order_by("-approved_at")[:10]

    context = {
        "pending_users": pending_users,
        "recently_approved": recently_approved,
        "pending_count": pending_users.count(),
    }

    return render(request, "common/user_approvals.html", context)


@login_required
@require_POST
def user_approval_action(request, user_id: int):
    """Process user approval/rejection action."""

    # Restrict to authorized approvers only
    if not _can_approve_users(request.user):
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    user_to_process = get_object_or_404(User, id=user_id, is_approved=False)
    action = request.POST.get("action")

    if action == "approve":
        user_to_process.is_approved = True
        user_to_process.approved_by = request.user
        user_to_process.approved_at = timezone.now()
        user_to_process.save()

        messages.success(
            request,
            f"✓ {user_to_process.get_full_name() or user_to_process.username} has been approved."
        )

        # Return HTMX response to refresh the page
        if request.headers.get("HX-Request"):
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps({
                        "user-approved": {"id": user_id},
                        "refresh-page": True,
                    })
                }
            )
        return redirect("common:user_approvals")

    elif action == "reject":
        # For rejection, we could either delete or mark inactive
        # For safety, we'll just mark inactive but keep the record
        user_to_process.is_active = False
        user_to_process.save()

        messages.warning(
            request,
            f"✗ {user_to_process.get_full_name() or user_to_process.username} has been rejected and marked inactive."
        )

        # Return HTMX response to refresh the page
        if request.headers.get("HX-Request"):
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps({
                        "user-rejected": {"id": user_id},
                        "refresh-page": True,
                    })
                }
            )
        return redirect("common:user_approvals")

    messages.error(request, "Invalid action specified.")
    return redirect("common:user_approvals")


__all__ = [
    "oobc_management_home",
    "oobc_calendar",
    "oobc_calendar_feed_json",
    "oobc_calendar_feed_ics",
    "oobc_calendar_brief",
    "planning_budgeting",
    "staff_management",
    "staff_task_board",
    "staff_task_modal_create",
    "staff_task_modal",
    "staff_task_delete",
    "staff_task_inline_update",
    "staff_task_update",
    "staff_task_update_field",
    "staff_task_create",
    "staff_task_create_api",
    "staff_api_assignees",
    "staff_api_teams",
    "staff_profiles_list",
    "staff_profile_create",
    "staff_profile_update",
    "staff_profiles_detail",
    "staff_profile_delete",
    "staff_performance_dashboard",
    "staff_training_development",
    "staff_team_assign",
    "staff_team_manage",
    "user_approvals",
    "user_approval_action",
]
