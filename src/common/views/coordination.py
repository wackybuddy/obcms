"""Views for coordination module dashboards and listings."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def coordination_home(request):
    """Coordination module home page - coordination with BMOAs, NGAs, and LGUs."""
    from datetime import timedelta

    from django.db.models import Count, Q
    from django.utils import timezone

    from coordination.models import (
        Event,
        EventParticipant,
        Organization,
        Partnership,
        PartnershipSignatory,
        StakeholderEngagement,
    )

    now = timezone.now()

    mapped_partners = Organization.objects.filter(
        is_active=True, organization_type__in=["bmoa", "nga", "lgu"]
    ).exclude(description="")

    mapped_partners_stats = {
        "total": mapped_partners.count(),
        "bmoa": mapped_partners.filter(organization_type="bmoa").count(),
        "nga": mapped_partners.filter(organization_type="nga").count(),
        "lgu": mapped_partners.filter(organization_type="lgu").count(),
    }

    active_partnerships = Partnership.objects.filter(status="active")
    bmoa_partnerships = (
        active_partnerships.filter(signatories__organization__organization_type="bmoa")
        .distinct()
        .count()
    )
    nga_partnerships = (
        active_partnerships.filter(signatories__organization__organization_type="nga")
        .distinct()
        .count()
    )
    lgu_partnerships = (
        active_partnerships.filter(signatories__organization__organization_type="lgu")
        .distinct()
        .count()
    )

    active_partnerships_stats = {
        "total": active_partnerships.count(),
        "bmoa": bmoa_partnerships,
        "nga": nga_partnerships,
        "lgu": lgu_partnerships,
    }

    completed_events = Event.objects.filter(status="completed")
    completed_engagements = StakeholderEngagement.objects.filter(status="completed")

    total_completed_activities = (
        completed_events.count() + completed_engagements.count()
    )

    bmoa_events = (
        completed_events.filter(participants__organization__organization_type="bmoa")
        .distinct()
        .count()
    )
    nga_events = (
        completed_events.filter(participants__organization__organization_type="nga")
        .distinct()
        .count()
    )
    lgu_events = (
        completed_events.filter(participants__organization__organization_type="lgu")
        .distinct()
        .count()
    )

    coordination_activities_done_stats = {
        "total": total_completed_activities,
        "bmoa": bmoa_events,
        "nga": nga_events,
        "lgu": lgu_events,
    }

    planned_events = Event.objects.filter(
        status__in=["planned", "scheduled"], start_date__gte=now.date()
    )
    planned_engagements = StakeholderEngagement.objects.filter(
        status__in=["planned", "scheduled"], planned_date__gte=now
    )

    total_planned_activities = planned_events.count() + planned_engagements.count()

    bmoa_planned = (
        planned_events.filter(participants__organization__organization_type="bmoa")
        .distinct()
        .count()
    )
    nga_planned = (
        planned_events.filter(participants__organization__organization_type="nga")
        .distinct()
        .count()
    )
    lgu_planned = (
        planned_events.filter(participants__organization__organization_type="lgu")
        .distinct()
        .count()
    )

    planned_coordination_activities_stats = {
        "total": total_planned_activities,
        "bmoa": bmoa_planned,
        "nga": nga_planned,
        "lgu": lgu_planned,
    }

    recent_events = Event.objects.filter(
        start_date__gte=now.date() - timedelta(days=30)
    ).order_by("-start_date")[:5]

    event_by_type = {
        "meeting": Event.objects.filter(event_type="meeting").count(),
        "workshop": Event.objects.filter(event_type="workshop").count(),
        "conference": Event.objects.filter(event_type="conference").count(),
        "consultation": Event.objects.filter(event_type="consultation").count(),
    }

    active_partnerships_list = Partnership.objects.filter(status="active").order_by(
        "-created_at"
    )[:5]

    stats = {
        "mapped_partners": mapped_partners_stats,
        "active_partnerships": active_partnerships_stats,
        "coordination_activities_done": coordination_activities_done_stats,
        "planned_coordination_activities": planned_coordination_activities_stats,
        "recent_events": recent_events,
        "coordination": {
            "active_partnerships": active_partnerships_list,
            "by_type": event_by_type,
        },
    }

    return render(request, "coordination/coordination_home.html", {"stats": stats})


@login_required
def coordination_organizations(request):
    """Manage coordination organizations page."""
    from django.db.models import Count

    from coordination.models import Organization, OrganizationContact

    organizations = Organization.objects.annotate(
        contacts_count=Count("contacts"), partnerships_count=Count("led_partnerships")
    ).order_by("name")

    type_filter = request.GET.get("type")
    status_filter = request.GET.get("status")

    if type_filter:
        organizations = organizations.filter(organization_type=type_filter)

    if status_filter == "active":
        organizations = organizations.filter(is_active=True)
    elif status_filter == "inactive":
        organizations = organizations.filter(is_active=False)

    org_types = (
        Organization.ORGANIZATION_TYPE_CHOICES
        if hasattr(Organization, "ORGANIZATION_TYPE_CHOICES")
        else []
    )

    stats = {
        "total_organizations": organizations.count(),
        "active_organizations": organizations.filter(is_active=True).count(),
        "total_contacts": OrganizationContact.objects.count(),
        "by_type": organizations.values("organization_type").annotate(
            count=Count("id")
        ),
    }

    context = {
        "organizations": organizations,
        "org_types": org_types,
        "current_type": type_filter,
        "current_status": status_filter,
        "stats": stats,
    }
    return render(request, "coordination/coordination_organizations.html", context)


@login_required
def coordination_partnerships(request):
    """Manage coordination partnerships page."""
    from django.db.models import Count

    from coordination.models import Organization, Partnership

    partnerships = (
        Partnership.objects.select_related("lead_organization")
        .annotate(signatories_count=Count("signatories"))
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status")
    type_filter = request.GET.get("type")

    if status_filter:
        partnerships = partnerships.filter(status=status_filter)

    if type_filter:
        partnerships = partnerships.filter(partnership_type=type_filter)

    status_choices = (
        Partnership.STATUS_CHOICES if hasattr(Partnership, "STATUS_CHOICES") else []
    )
    type_choices = (
        Partnership.PARTNERSHIP_TYPE_CHOICES
        if hasattr(Partnership, "PARTNERSHIP_TYPE_CHOICES")
        else []
    )

    stats = {
        "total_partnerships": partnerships.count(),
        "active_partnerships": partnerships.filter(status="active").count(),
        "pending_partnerships": partnerships.filter(status="pending").count(),
        "by_type": partnerships.values("partnership_type").annotate(count=Count("id")),
    }

    context = {
        "partnerships": partnerships,
        "status_choices": status_choices,
        "type_choices": type_choices,
        "current_status": status_filter,
        "current_type": type_filter,
        "stats": stats,
    }
    return render(request, "coordination/coordination_partnerships.html", context)


@login_required
def coordination_events(request):
    """Manage coordination events page."""
    from django.db.models import Count
    from django.utils import timezone

    from coordination.models import Event, EventParticipant

    events = (
        Event.objects.select_related("community", "organizer")
        .annotate(participants_count=Count("participants"))
        .order_by("-start_date")
    )

    status_filter = request.GET.get("status")
    type_filter = request.GET.get("type")

    if status_filter:
        events = events.filter(status=status_filter)

    if type_filter:
        events = events.filter(event_type=type_filter)

    status_choices = Event.STATUS_CHOICES if hasattr(Event, "STATUS_CHOICES") else []
    type_choices = (
        Event.EVENT_TYPE_CHOICES if hasattr(Event, "EVENT_TYPE_CHOICES") else []
    )

    now = timezone.now().date()
    upcoming_events = events.filter(start_date__gte=now)
    past_events = events.filter(start_date__lt=now)

    stats = {
        "total_events": events.count(),
        "upcoming_events": upcoming_events.count(),
        "past_events": past_events.count(),
        "total_participants": EventParticipant.objects.count(),
    }

    context = {
        "events": events,
        "upcoming_events": upcoming_events[:10],
        "past_events": past_events[:10],
        "status_choices": status_choices,
        "type_choices": type_choices,
        "current_status": status_filter,
        "current_type": type_filter,
        "stats": stats,
    }
    return render(request, "coordination/coordination_events.html", context)


@login_required
def coordination_view_all(request):
    """Coordination overview and reports page."""
    from datetime import timedelta

    from django.db.models import Count
    from django.utils import timezone

    from coordination.models import Event, Organization, Partnership

    events = Event.objects.select_related("community", "organizer")
    partnerships = Partnership.objects.select_related("lead_organization")
    organizations = Organization.objects.filter(is_active=True)

    now = timezone.now()
    last_30_days = now.date() - timedelta(days=30)

    stats = {
        "organizations": {
            "total": organizations.count(),
            "by_type": organizations.values("organization_type").annotate(
                count=Count("id")
            )[:5],
        },
        "partnerships": {
            "total": partnerships.count(),
            "active": partnerships.filter(status="active").count(),
            "recent": partnerships.filter(created_at__gte=last_30_days).count(),
            "by_status": partnerships.values("status").annotate(count=Count("id")),
        },
        "events": {
            "total": events.count(),
            "upcoming": events.filter(start_date__gte=now.date()).count(),
            "recent": events.filter(start_date__gte=last_30_days).count(),
            "by_type": events.values("event_type").annotate(count=Count("id"))[:5],
        },
    }

    recent_events = events.order_by("-created_at")[:5]
    recent_partnerships = partnerships.order_by("-created_at")[:5]

    context = {
        "stats": stats,
        "recent_events": recent_events,
        "recent_partnerships": recent_partnerships,
        "organizations": organizations[:10],
    }
    return render(request, "coordination/coordination_view_all.html", context)


__all__ = [
    "coordination_home",
    "coordination_organizations",
    "coordination_partnerships",
    "coordination_events",
    "coordination_view_all",
]
