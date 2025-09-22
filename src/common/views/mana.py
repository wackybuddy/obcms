"""Views for the MANA (Mapping and Needs Assessment) module."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def mana_home(request):
    """MANA module home page."""
    from django.db.models import Count, Q

    from mana.models import Assessment, BaselineStudy, Need

    assessments = Assessment.objects.select_related("community", "category")
    needs = Need.objects.select_related("category", "assessment")
    baseline_studies = BaselineStudy.objects.select_related("community")

    total_assessments = assessments.count()
    completed_assessments = assessments.filter(status="completed").count()
    in_progress_assessments = assessments.filter(
        status__in=["data_collection", "analysis"]
    ).count()
    planned_assessments = assessments.filter(
        status__in=["planning", "preparation"]
    ).count()

    education_assessments = assessments.filter(
        Q(category__name__icontains="education")
        | Q(category__category_type__icontains="education")
    ).count()
    economic_assessments = assessments.filter(
        Q(category__name__icontains="economic")
        | Q(category__category_type__icontains="economic")
    ).count()
    social_assessments = assessments.filter(
        Q(category__name__icontains="social")
        | Q(category__category_type__icontains="social")
    ).count()
    cultural_assessments = assessments.filter(
        Q(category__name__icontains="cultural")
        | Q(category__category_type__icontains="cultural")
    ).count()
    infrastructure_assessments = assessments.filter(
        Q(category__name__icontains="infrastructure")
        | Q(category__category_type__icontains="infrastructure")
    ).count()

    stats = {
        "mana": {
            "total_assessments": total_assessments,
            "completed": completed_assessments,
            "in_progress": in_progress_assessments,
            "planned": planned_assessments,
            "by_area": {
                "education": education_assessments,
                "economic": economic_assessments,
                "social": social_assessments,
                "cultural": cultural_assessments,
                "infrastructure": infrastructure_assessments,
            },
        },
        "assessments": {
            "total": total_assessments,
            "completed": completed_assessments,
            "ongoing": in_progress_assessments,
            "by_status": assessments.values("status").annotate(count=Count("id")),
            "recent": assessments.order_by("-created_at")[:10],
        },
        "needs": {
            "total": needs.count(),
            "critical": needs.filter(urgency_level="immediate").count(),
            "by_category": needs.values("category__name").annotate(count=Count("id"))[
                :10
            ],
            "recent": needs.order_by("-created_at")[:10],
        },
        "baseline_studies": {
            "total": baseline_studies.count(),
            "completed": baseline_studies.filter(status="completed").count(),
            "ongoing": baseline_studies.filter(
                status__in=["data_collection", "analysis"]
            ).count(),
        },
    }

    return render(request, "mana/mana_home.html", {"stats": stats})


@login_required
def mana_new_assessment(request):
    """New MANA assessment page."""
    from communities.models import OBCCommunity
    from mana.models import Assessment, NeedsCategory

    recent_assessments = Assessment.objects.order_by("-created_at")[:5]
    communities = OBCCommunity.objects.filter(is_active=True).order_by("barangay__name")
    categories = NeedsCategory.objects.all().order_by("name")

    context = {
        "recent_assessments": recent_assessments,
        "communities": communities,
        "categories": categories,
    }
    return render(request, "mana/mana_new_assessment.html", context)


@login_required
def mana_manage_assessments(request):
    """Manage MANA assessments page."""
    from django.db.models import Count

    from communities.models import OBCCommunity
    from mana.models import Assessment, Need

    assessments = (
        Assessment.objects.select_related("community", "category", "lead_assessor")
        .annotate(needs_count=Count("identified_needs"))
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status")
    community_filter = request.GET.get("community")

    if status_filter:
        assessments = assessments.filter(status=status_filter)

    if community_filter:
        assessments = assessments.filter(community__id=community_filter)

    communities = OBCCommunity.objects.order_by("barangay__name")
    status_choices = (
        Assessment.STATUS_CHOICES if hasattr(Assessment, "STATUS_CHOICES") else []
    )

    stats = {
        "total_assessments": assessments.count(),
        "completed": assessments.filter(status="completed").count(),
        "in_progress": assessments.filter(
            status__in=["data_collection", "analysis"]
        ).count(),
        "pending": assessments.filter(status="pending").count(),
    }

    context = {
        "assessments": assessments,
        "communities": communities,
        "status_choices": status_choices,
        "current_status": status_filter,
        "current_community": community_filter,
        "stats": stats,
    }
    return render(request, "mana/mana_manage_assessments.html", context)


@login_required
def mana_geographic_data(request):
    """MANA geographic data and mapping page."""
    from django.db.models import Count

    from communities.models import OBCCommunity
    from mana.models import GeographicDataLayer, MapVisualization

    data_layers = GeographicDataLayer.objects.all().order_by("name")
    visualizations = MapVisualization.objects.select_related("community").order_by(
        "-created_at"
    )[:10]

    communities = OBCCommunity.objects.annotate(
        visualizations_count=Count("map_visualizations")
    ).filter(visualizations_count__gt=0)

    stats = {
        "total_layers": data_layers.count(),
        "total_visualizations": visualizations.count(),
        "communities_mapped": communities.count(),
        "active_layers": (
            data_layers.filter(is_active=True).count()
            if hasattr(GeographicDataLayer, "is_active")
            else data_layers.count()
        ),
    }

    context = {
        "data_layers": data_layers,
        "visualizations": visualizations,
        "communities": communities,
        "stats": stats,
    }
    return render(request, "mana/mana_geographic_data.html", context)


__all__ = [
    "mana_home",
    "mana_new_assessment",
    "mana_manage_assessments",
    "mana_geographic_data",
]
