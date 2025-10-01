"""Dashboard landing views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone


@login_required
def dashboard(request):
    """Main dashboard view after login."""

    # Redirect MANA Participants and Facilitators to their respective dashboards
    if not request.user.is_staff and not request.user.is_superuser:
        if request.user.has_perm("mana.can_access_regional_mana"):
            # Facilitators go to Manage Assessments dashboard
            if request.user.has_perm("mana.can_facilitate_workshop"):
                return redirect("common:mana_manage_assessments")
            # Participants go to their participant dashboard
            else:
                # Get participant's assessment
                try:
                    from mana.models import WorkshopParticipantAccount
                    participant = WorkshopParticipantAccount.objects.get(user=request.user)
                    # Redirect to participant dashboard for their assessment
                    return redirect("mana:participant_dashboard", assessment_id=str(participant.assessment.id))
                except WorkshopParticipantAccount.DoesNotExist:
                    # No participant account - redirect to regional overview
                    return redirect("common:mana_regional_overview")

    from django.db.models import Avg, Count

    from communities.models import (
        MunicipalityCoverage,
        OBCCommunity,
        Stakeholder,
    )
    from coordination.models import Event, Partnership
    from mana.models import Assessment, Need
    from monitoring.models import MonitoringEntry
    from recommendations.policy_tracking.models import PolicyRecommendation
    from common.models import User

    communities_qs = OBCCommunity.objects.all()
    barangay_total = communities_qs.count()
    municipal_total = MunicipalityCoverage.objects.count()
    combined_total = barangay_total + municipal_total

    oobc_staff_qs = User.objects.filter(user_type__in=["oobc_staff", "admin"])

    stats = {
        "communities": {
            "total": barangay_total,
            "combined_total": combined_total,
            "barangay_total": barangay_total,
            "municipal_total": municipal_total,
            "active": communities_qs.filter(is_active=True).count(),
            "by_region": communities_qs.values(
                "barangay__municipality__province__region__name"
            ).annotate(count=Count("id"))[:5],
            "recent": communities_qs.order_by("-created_at")[:5],
        },
        "mana": {
            "total_assessments": Assessment.objects.count(),
            "completed": Assessment.objects.filter(status="completed").count(),
            "in_progress": Assessment.objects.filter(
                status__in=["data_collection", "analysis"]
            ).count(),
            "high_priority": Need.objects.filter(impact_severity=5).count(),
        },
        "monitoring": {
            "total": MonitoringEntry.objects.count(),
            "moa_ppa": MonitoringEntry.objects.filter(category="moa_ppa").count(),
            "oobc_ppa": MonitoringEntry.objects.filter(category="oobc_ppa").count(),
            "obc_requests": MonitoringEntry.objects.filter(category="obc_request").count(),
            "pending_requests": MonitoringEntry.objects.filter(
                category="obc_request",
                request_status__in=[
                    "submitted",
                    "under_review",
                    "clarification",
                    "endorsed",
                ],
            ).count(),
            "avg_progress": MonitoringEntry.objects.aggregate(avg=Avg("progress"))["avg"]
            or 0,
            "linked_assessments": MonitoringEntry.objects.filter(
                related_assessment__isnull=False
            ).count(),
            "linked_events": MonitoringEntry.objects.filter(
                related_event__isnull=False
            ).count(),
            "linked_policies": MonitoringEntry.objects.filter(
                related_policy__isnull=False
            ).count(),
        },
        "coordination": {
            "total_events": Event.objects.count(),
            "active_partnerships": Partnership.objects.filter(status="active").count(),
            "upcoming_events": Event.objects.filter(
                start_date__gte=timezone.now().date(), status="planned"
            ).count(),
            "pending_actions": 0,
            "bmoas": Partnership.objects.filter(
                status="active", lead_organization__organization_type="bmoa"
            ).count(),
            "ngas": Partnership.objects.filter(
                status="active", lead_organization__organization_type="nga"
            ).count(),
            "lgus": Partnership.objects.filter(
                status="active", lead_organization__organization_type="lgu"
            ).count(),
        },
        "policy_tracking": {
            "total_policies": PolicyRecommendation.objects.count(),
            "implemented": PolicyRecommendation.objects.filter(
                status="implemented"
            ).count(),
            "under_review": PolicyRecommendation.objects.filter(
                status="under_review"
            ).count(),
            "high_priority": PolicyRecommendation.objects.filter(
                priority__in=["high", "urgent", "critical"]
            ).count(),
            "total_recommendations": PolicyRecommendation.objects.count(),
            "policies": PolicyRecommendation.objects.filter(
                category__in=["governance", "legal_framework", "administrative"]
            ).count(),
            "programs": PolicyRecommendation.objects.filter(
                category__in=[
                    "education",
                    "economic_development",
                    "social_development",
                    "cultural_development",
                ]
            ).count(),
            "services": PolicyRecommendation.objects.filter(
                category__in=[
                    "healthcare",
                    "infrastructure",
                    "environment",
                    "human_rights",
                ]
            ).count(),
        },
        "oobc_management": {
            "total_staff": oobc_staff_qs.count(),
            "active_staff": oobc_staff_qs.filter(is_active=True).count(),
            "pending_approvals": User.objects.filter(is_approved=False).count(),
        },
    }

    context = {
        "user": request.user,
        "user_type_display": request.user.get_user_type_display(),
        "is_approved": request.user.is_approved,
        "stats": stats,
    }
    return render(request, "common/dashboard.html", context)


__all__ = ["dashboard"]
