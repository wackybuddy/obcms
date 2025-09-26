"""OOBC management module views."""

from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, DecimalField, FloatField, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from common.constants import STAFF_USER_TYPES
from common.forms import StaffTaskForm, StaffTeamForm, StaffTeamMembershipForm
from common.models import StaffTask, StaffTeam, StaffTeamMembership, User
from common.services.staff import ensure_default_staff_teams, ensure_membership
from monitoring.models import MonitoringEntry


PERFORMANCE_STATUS_WEIGHTS = {
    StaffTask.STATUS_COMPLETED: 1.0,
    StaffTask.STATUS_IN_PROGRESS: 0.6,
    StaffTask.STATUS_NOT_STARTED: 0.2,
    StaffTask.STATUS_AT_RISK: 0.1,
}


def staff_queryset():
    """Return the base queryset for OOBC staff users."""

    return User.objects.filter(user_type__in=STAFF_USER_TYPES)


@login_required
def oobc_management_home(request):
    """Surface OOBC management overview data for internal operations."""
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

    status_labels = dict(StaffTask.STATUS_CHOICES)

    if request.method == "POST":
        handled_post = False
        with transaction.atomic():
            if request.POST.get("form_name") == "task_status":
                task_id = request.POST.get("task_id")
                status = request.POST.get("status")
                progress_value = request.POST.get("progress")
                if task_id and status in status_labels:
                    try:
                        task = StaffTask.objects.select_for_update().get(pk=task_id)
                    except StaffTask.DoesNotExist:
                        messages.error(request, "Task could not be found.")
                    else:
                        task.status = status
                        update_fields = ["status", "updated_at"]
                        if status == StaffTask.STATUS_COMPLETED:
                            task.completed_at = timezone.now()
                            task.progress = 100
                            update_fields.extend(["completed_at", "progress"])
                        elif progress_value:
                            try:
                                progress_int = max(0, min(100, int(progress_value)))
                            except (TypeError, ValueError):
                                progress_int = task.progress
                            task.progress = progress_int
                            update_fields.append("progress")
                        task.save(update_fields=update_fields)
                        messages.success(
                            request,
                            f"Task \"{task.title}\" updated to {status_labels[status]}.",
                        )
                        handled_post = True
        if handled_post:
            return redirect("common:staff_management")

    task_qs = (
        StaffTask.objects.select_related("team", "assignee", "linked_event")
        .order_by("due_date", "-priority")
    )
    task_list = list(task_qs)

    tasks_by_status = defaultdict(list)
    tasks_by_staff = defaultdict(list)
    for task in task_list:
        tasks_by_status[task.status].append(task)
        if task.assignee_id:
            tasks_by_staff[task.assignee_id].append(task)

    pipeline_statuses = [
        StaffTask.STATUS_NOT_STARTED,
        StaffTask.STATUS_IN_PROGRESS,
        StaffTask.STATUS_AT_RISK,
        StaffTask.STATUS_COMPLETED,
    ]
    task_pipeline = [
        {
            "status_key": status,
            "status_label": status_labels[status],
            "tasks": sorted(
                tasks_by_status.get(status, []),
                key=lambda item: (item.due_date or today, item.title),
            ),
            "total": len(tasks_by_status.get(status, [])),
        }
        for status in pipeline_statuses
    ]

    task_status_totals = {
        status_labels[status]: len(tasks_by_status.get(status, []))
        for status in pipeline_statuses
    }

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

    calendar_events = [
        {
            "task": task,
            "title": task.title,
            "team": task.team,
            "assignee": task.assignee,
            "start": task.start_date or task.due_date,
            "end": task.due_date,
            "status_key": task.status,
            "status_label": status_labels[task.status],
            "priority": task.get_priority_display(),
            "linked_event": task.linked_event,
        }
        for task in task_list
        if task.due_date
    ]
    calendar_events.sort(key=lambda item: (item["end"], item["title"]))
    calendar_events = calendar_events[:8]

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
        "tasks__assignee", "memberships__user"
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
        "task_pipeline": task_pipeline,
        "task_status_totals": task_status_totals,
        "calendar_events": calendar_events,
        "team_overview": team_overview,
        "individual_performance": individual_performance,
        "team_performance": sorted(
            team_performance,
            key=lambda item: (item["completion_rate"], item["avg_progress"]),
            reverse=True,
        ),
        "performance_snapshot": performance_snapshot,
        "status_labels": status_labels,
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
        if task.assignee:
            ensure_membership(task.team, task.assignee, request.user)
        messages.success(request, f"Task \"{task.title}\" saved successfully.")
        return redirect("common:staff_management")

    recent_tasks = (
        StaffTask.objects.select_related("team", "assignee")
        .order_by("-created_at")[:10]
    )

    context = {
        "form": form,
        "recent_tasks": recent_tasks,
    }
    return render(request, "common/staff_task_create.html", context)


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

    form = StaffTeamForm(request.POST or None, instance=team)
    if request.method == "POST" and form.is_valid():
        saved_team = form.save()
        action = "updated" if team else "created"
        messages.success(request, f"Team \"{saved_team.name}\" {action} successfully.")
        return redirect("common:staff_team_manage")

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

    context = {
        "form": form,
        "teams": team_metrics,
        "selected_team": team,
        "wide_fields": {"description", "mission", "focus_areas"},
    }
    return render(request, "common/staff_team_manage.html", context)


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
    entries = MonitoringEntry.objects.all()
    today = timezone.now().date()

    totals = entries.aggregate(
        budget_total=Coalesce(Sum("budget_allocation"), ZERO_DECIMAL),
        budget_obc_total=Coalesce(Sum("budget_obc_allocation"), ZERO_DECIMAL),
        projects=Count("id"),
        avg_progress=Coalesce(Avg("progress"), ZERO_FLOAT),
    )

    category_labels = dict(MonitoringEntry.CATEGORY_CHOICES)
    status_labels = dict(MonitoringEntry.STATUS_CHOICES)

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

    context = {
        "totals": totals,
        "category_breakdown": category_breakdown,
        "status_breakdown": status_breakdown,
        "top_allocations": top_allocations,
        "upcoming_milestones": upcoming_milestones,
        "today": today,
    }
    return render(request, "common/oobc_planning_budgeting.html", context)


__all__ = [
    "oobc_management_home",
    "staff_management",
    "staff_task_create",
    "staff_team_assign",
    "staff_team_manage",
    "planning_budgeting",
]
