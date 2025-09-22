"""Views for Monitoring & Evaluation dashboard and detail pages."""

from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from common.services.locations import build_location_data

from .forms import (
    MonitoringMOAEntryForm,
    MonitoringOOBCEntryForm,
    MonitoringRequestEntryForm,
    MonitoringUpdateForm,
)
from .models import MonitoringEntry, MonitoringUpdate


def _prefetch_entries():
    """Return a queryset with the relations needed across views."""

    return (
        MonitoringEntry.objects.all()
        .select_related(
            "lead_organization",
            "submitted_by_community",
            "submitted_to_organization",
            "related_assessment",
            "related_event",
            "related_policy",
            "created_by",
            "updated_by",
        )
        .prefetch_related("communities", "supporting_organizations", "updates")
    )


@login_required
def monitoring_dashboard(request):
    """Render the consolidated Monitoring & Evaluation workspace."""

    entries = _prefetch_entries()
    base_queryset = MonitoringEntry.objects.all()
    current_year = timezone.now().year

    def filter_for_year(queryset):
        return queryset.filter(
            Q(start_date__year=current_year)
            | Q(start_date__isnull=True, created_at__year=current_year)
        )

    moa_year_qs = filter_for_year(base_queryset.filter(category="moa_ppa"))
    oobc_year_qs = filter_for_year(base_queryset.filter(category="oobc_ppa"))
    request_year_qs = filter_for_year(base_queryset.filter(category="obc_request"))

    moa_stats = {
        "title": "MOA PPAs",
        "subtitle": f"{current_year} Overview",
        "icon": "fas fa-building-columns",
        "gradient": "from-blue-500 via-blue-600 to-blue-700",
        "total": moa_year_qs.count(),
        "metrics": [
            {"label": "Completed", "value": moa_year_qs.filter(status="completed").count()},
            {
                "label": "Ongoing",
                "value": moa_year_qs.filter(status__in=["ongoing", "on_hold"]).count(),
            },
            {
                "label": "Not Started",
                "value": moa_year_qs.filter(status__in=["planning"]).count(),
            },
        ],
    }

    oobc_stats = {
        "title": "OOBC Initiatives",
        "subtitle": f"{current_year} Overview",
        "icon": "fas fa-hand-holding-heart",
        "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
        "total": oobc_year_qs.count(),
        "metrics": [
            {"label": "Completed", "value": oobc_year_qs.filter(status="completed").count()},
            {
                "label": "Ongoing",
                "value": oobc_year_qs.filter(status__in=["ongoing", "on_hold"]).count(),
            },
            {
                "label": "Not Started",
                "value": oobc_year_qs.filter(status__in=["planning"]).count(),
            },
        ],
    }

    request_on_process_statuses = [
        "under_review",
        "clarification",
        "endorsed",
        "approved",
        "in_progress",
    ]

    request_stats = {
        "title": "OBC Requests / Proposals",
        "subtitle": f"{current_year} Overview",
        "icon": "fas fa-file-signature",
        "gradient": "from-cyan-500 via-sky-500 to-indigo-500",
        "total": request_year_qs.count(),
        "metrics": [
            {
                "label": "Completed",
                "value": request_year_qs.filter(request_status="completed").count(),
            },
            {
                "label": "On Process",
                "value": request_year_qs.filter(
                    request_status__in=request_on_process_statuses
                ).count(),
            },
            {
                "label": "Not Started",
                "value": request_year_qs.filter(
                    Q(request_status="submitted") | Q(request_status="") | Q(request_status__isnull=True)
                ).count(),
            },
        ],
    }

    stats_cards = [moa_stats, oobc_stats, request_stats]

    grouped_entries = defaultdict(list)
    for entry in entries:
        grouped_entries[entry.category].append(entry)

    raw_category_summary = (
        entries.order_by()
        .values("category")
        .annotate(
            total=Count("id"),
            completed=Count("id", filter=Q(status="completed")),
        )
    )

    raw_status_breakdown = (
        entries.order_by()
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    linked_counts = {
        "mana_assessments": entries.filter(related_assessment__isnull=False).count(),
        "coordination_events": entries.filter(related_event__isnull=False).count(),
        "policy_recommendations": entries.filter(related_policy__isnull=False).count(),
    }

    progress_snapshot = entries.aggregate(
        avg_progress=Avg("progress"),
        latest_update=Max("updated_at"),
    )

    pending_requests = entries.filter(
        category="obc_request",
        request_status__in=["submitted", *request_on_process_statuses],
    ).count()

    category_labels = dict(MonitoringEntry.CATEGORY_CHOICES)
    status_labels = dict(MonitoringEntry.STATUS_CHOICES)
    request_status_labels = dict(MonitoringEntry.REQUEST_STATUS_CHOICES)

    category_order = {
        key: index for index, (key, _label) in enumerate(MonitoringEntry.CATEGORY_CHOICES)
    }

    category_summary = [
        {
            "key": item["category"],
            "label": category_labels.get(item["category"], item["category"]),
            "total": item["total"],
            "completed": item["completed"],
        }
        for item in raw_category_summary
    ]
    status_breakdown = [
        {
            "key": item["status"],
            "label": status_labels.get(item["status"], item["status"]),
            "total": item["total"],
        }
        for item in raw_status_breakdown
    ]
    request_breakdown = [
        {
            "key": item["request_status"],
            "label": request_status_labels.get(
                item["request_status"], item["request_status"]
            ),
            "total": item["total"],
        }
        for item in (
            entries.filter(category="obc_request")
            .order_by()
            .values("request_status")
            .annotate(total=Count("id"))
            .order_by("request_status")
        )
    ]

    category_sections = [
        {
            "key": key,
            "label": category_labels.get(key, key),
            "entries": value,
        }
        for key, value in grouped_entries.items()
    ]

    category_summary.sort(key=lambda item: category_order.get(item["key"], 99))
    category_sections.sort(key=lambda item: category_order.get(item["key"], 99))

    quick_actions = [
        {
            "title": "Log MOA PPA",
            "description": "Document MOA-led projects accessible to OBC communities.",
            "icon": "fas fa-building-columns",
            "color": "bg-blue-500",
            "url": reverse("monitoring:create_moa"),
        },
        {
            "title": "Log OOBC Initiative",
            "description": "Capture OOBC-led programmes supporting partner communities.",
            "icon": "fas fa-hand-holding-heart",
            "color": "bg-emerald-500",
            "url": reverse("monitoring:create_oobc"),
        },
        {
            "title": "Submit OBC Request",
            "description": "Track requests and proposals submitted by OBC partners.",
            "icon": "fas fa-file-signature",
            "color": "bg-indigo-500",
            "url": reverse("monitoring:create_request"),
        },
    ]

    context = {
        "stats_cards": stats_cards,
        "quick_actions": quick_actions,
        "entries": entries,
        "category_sections": category_sections,
        "category_summary": category_summary,
        "status_breakdown": status_breakdown,
        "request_breakdown": request_breakdown,
        "linked_counts": linked_counts,
        "progress_snapshot": progress_snapshot,
        "pending_requests": pending_requests,
        "category_labels": category_labels,
        "status_labels": status_labels,
        "request_status_labels": request_status_labels,
    }
    return render(request, "monitoring/dashboard.html", context)


@login_required
def monitoring_entry_detail(request, pk):
    """Display a monitoring entry with recent updates and linked data."""

    entry = get_object_or_404(_prefetch_entries(), pk=pk)
    update_form = MonitoringUpdateForm()

    if request.method == "POST" and request.POST.get("action") == "add_update":
        update_form = MonitoringUpdateForm(request.POST)
        if update_form.is_valid():
            update = update_form.save(commit=False)
            update.entry = entry
            update.created_by = request.user
            update.save()

            if update.status:
                entry.status = update.status
            if update.request_status:
                entry.request_status = update.request_status
            if update.progress is not None:
                entry.progress = update.progress
            entry.last_status_update = update.follow_up_date or timezone.now().date()
            entry.updated_by = request.user
            entry.save()

            messages.success(request, "Update logged successfully.")
            return redirect("monitoring:detail", pk=entry.pk)
        messages.error(
            request,
            "Unable to record the update. Please review the highlighted fields.",
        )

    related_entries = (
        MonitoringEntry.objects.filter(
            communities__in=entry.communities.all()
        )
        .exclude(pk=entry.pk)
        .distinct()
        .select_related("lead_organization")
    )

    context = {
        "entry": entry,
        "updates": entry.updates.select_related("created_by"),
        "update_form": update_form,
        "related_entries": related_entries,
    }
    return render(request, "monitoring/detail.html", context)


@login_required
def create_moa_entry(request):
    """Create view for MOA PPAs."""

    form = MonitoringMOAEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.created_by = request.user
        entry.updated_by = request.user
        entry.save()
        form.save_m2m()
        form._post_save(entry)
        messages.success(request, "MOA PPA logged successfully.")
        return redirect("monitoring:detail", pk=entry.pk)

    return render(
        request,
        "monitoring/create_moa.html",
        {
            "form": form,
            "location_data": build_location_data(include_barangays=True),
        },
    )


@login_required
def create_oobc_entry(request):
    """Create view for OOBC initiatives."""

    form = MonitoringOOBCEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.created_by = request.user
        entry.updated_by = request.user
        entry.save()
        form.save_m2m()
        form._post_save(entry)
        messages.success(request, "OOBC initiative recorded successfully.")
        return redirect("monitoring:detail", pk=entry.pk)

    return render(
        request,
        "monitoring/create_oobc.html",
        {
            "form": form,
        },
    )


@login_required
def create_request_entry(request):
    """Create view for OBC requests and proposals."""

    form = MonitoringRequestEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.created_by = request.user
        entry.updated_by = request.user
        entry.save()
        form.save_m2m()
        form._post_save(entry)
        messages.success(request, "OBC request submitted successfully.")
        return redirect("monitoring:detail", pk=entry.pk)

    return render(
        request,
        "monitoring/create_request.html",
        {
            "form": form,
        },
    )
