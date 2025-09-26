"""OOBC management module views."""

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, DecimalField, FloatField, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from common.models import User
from monitoring.models import MonitoringEntry


STAFF_TYPES = ["oobc_staff", "admin"]


@login_required
def oobc_management_home(request):
    """Surface OOBC management overview data for internal operations."""
    staff_qs = User.objects.filter(user_type__in=STAFF_TYPES).order_by("-date_joined")
    pending_qs = User.objects.filter(is_approved=False).order_by("-date_joined")

    context = {
        "metrics": {
            "staff_total": staff_qs.count(),
            "active_staff": staff_qs.filter(is_active=True).count(),
            "pending_approvals": pending_qs.count(),
            "pending_staff": pending_qs.filter(user_type__in=STAFF_TYPES).count(),
        },
        "recent_staff": staff_qs[:8],
        "pending_users": pending_qs[:8],
    }
    return render(request, "common/oobc_management_home.html", context)


@login_required
def staff_management(request):
    """Detailed staffing dashboard for OOBC administrators."""
    staff_qs = User.objects.filter(user_type__in=STAFF_TYPES).order_by("last_name", "first_name")
    pending_staff_qs = staff_qs.filter(is_approved=False)
    inactive_staff_qs = staff_qs.filter(is_active=False)

    user_type_labels = dict(User.USER_TYPES)
    role_breakdown = [
        {
            "key": row["user_type"],
            "label": user_type_labels.get(
                row["user_type"], row["user_type"].replace("_", " ").title()
            ),
            "total": row["total"],
        }
        for row in staff_qs.values("user_type").annotate(total=Count("id")).order_by("user_type")
    ]

    context = {
        "metrics": {
            "total": staff_qs.count(),
            "active": staff_qs.filter(is_active=True, is_approved=True).count(),
            "inactive": inactive_staff_qs.count(),
            "pending": pending_staff_qs.count(),
            "recent": staff_qs.filter(date_joined__gte=timezone.now() - timedelta(days=30)).count(),
        },
        "role_breakdown": role_breakdown,
        "pending_staff": pending_staff_qs.order_by("-date_joined")[:10],
        "recent_staff": staff_qs.order_by("-last_login")[:10],
        "inactive_staff": inactive_staff_qs.order_by("last_name", "first_name")[:10],
        "staff_list": staff_qs,
    }
    return render(request, "common/oobc_staff_management.html", context)


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
    "planning_budgeting",
]
