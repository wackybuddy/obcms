"""Views for the MANA (Mapping and Needs Assessment) module."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Barangay, Municipality, Province, Region
from ..services.locations import build_location_data


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
    """MANA geographic data and mapping page with location-aware filters."""
    from django.db.models import Count

    from communities.models import GeographicDataLayer, MapVisualization, OBCCommunity

    def parse_identifier(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    region_id = parse_identifier(request.GET.get("region"))
    province_id = parse_identifier(request.GET.get("province"))
    municipality_id = parse_identifier(request.GET.get("municipality"))
    barangay_id = parse_identifier(request.GET.get("barangay"))

    selected_region = (
        Region.objects.filter(pk=region_id, is_active=True).first() if region_id else None
    )

    selected_province = None
    if province_id:
        selected_province = (
            Province.objects.filter(pk=province_id, is_active=True)
            .select_related("region")
            .first()
        )
        if not selected_province:
            province_id = None
        else:
            region_id = selected_province.region_id
            if not selected_region or selected_region.pk != region_id:
                selected_region = selected_province.region

    selected_municipality = None
    if municipality_id:
        selected_municipality = (
            Municipality.objects.filter(pk=municipality_id, is_active=True)
            .select_related("province__region")
            .first()
        )
        if not selected_municipality:
            municipality_id = None
        else:
            province_id = selected_municipality.province_id
            selected_province = selected_municipality.province
            region_id = selected_province.region_id
            selected_region = selected_province.region

    selected_barangay = None
    if barangay_id:
        selected_barangay = (
            Barangay.objects.filter(pk=barangay_id, is_active=True)
            .select_related("municipality__province__region")
            .first()
        )
        if not selected_barangay:
            barangay_id = None
        else:
            municipality_id = selected_barangay.municipality_id
            selected_municipality = selected_barangay.municipality
            province_id = selected_municipality.province_id
            selected_province = selected_municipality.province
            region_id = selected_province.region_id
            selected_region = selected_province.region

    layer_filters = {}
    visualization_filters = {}
    community_filters = {}

    if barangay_id:
        layer_filters["community__barangay_id"] = barangay_id
        visualization_filters["community__barangay_id"] = barangay_id
        community_filters["barangay_id"] = barangay_id
    elif municipality_id:
        layer_filters["community__barangay__municipality_id"] = municipality_id
        visualization_filters["community__barangay__municipality_id"] = municipality_id
        community_filters["barangay__municipality_id"] = municipality_id
    elif province_id:
        layer_filters["community__barangay__municipality__province_id"] = province_id
        visualization_filters[
            "community__barangay__municipality__province_id"
        ] = province_id
        community_filters["barangay__municipality__province_id"] = province_id
    elif region_id:
        layer_filters[
            "community__barangay__municipality__province__region_id"
        ] = region_id
        visualization_filters[
            "community__barangay__municipality__province__region_id"
        ] = region_id
        community_filters["barangay__municipality__province__region_id"] = region_id

    data_layers_qs = GeographicDataLayer.objects.all().order_by("name")
    if layer_filters:
        data_layers_qs = data_layers_qs.filter(**layer_filters)

    visualizations_qs = MapVisualization.objects.select_related("community").order_by(
        "-created_at"
    )
    if visualization_filters:
        visualizations_qs = visualizations_qs.filter(**visualization_filters)

    communities_qs = (
        OBCCommunity.objects.annotate(
            visualizations_count=Count("community_map_visualizations")
        )
        .filter(visualizations_count__gt=0)
        .order_by("barangay__name")
    )
    if community_filters:
        communities_qs = communities_qs.filter(**community_filters)

    stats = {
        "total_layers": data_layers_qs.count(),
        "total_visualizations": visualizations_qs.count(),
        "communities_mapped": communities_qs.count(),
        "active_layers": (
            data_layers_qs.filter(is_active=True).count()
            if hasattr(GeographicDataLayer, "is_active")
            else data_layers_qs.count()
        ),
    }

    # Limit visualizations display but keep counts accurate.
    visualizations = visualizations_qs[:10]

    filter_summary_parts = []
    if selected_barangay:
        filter_summary_parts.append(
            f"Barangay {selected_barangay.name}, {selected_municipality.name}"
        )
    elif selected_municipality:
        filter_summary_parts.append(
            f"{selected_municipality.name}, {selected_province.name}"
        )
    elif selected_province:
        filter_summary_parts.append(f"Province {selected_province.name}")
    elif selected_region:
        filter_summary_parts.append(f"Region {selected_region.code} - {selected_region.name}")

    context = {
        "data_layers": data_layers_qs,
        "visualizations": visualizations,
        "communities": communities_qs,
        "stats": stats,
        "location_data": build_location_data(),
        "current_region": str(region_id or ""),
        "current_province": str(province_id or ""),
        "current_municipality": str(municipality_id or ""),
        "current_barangay": str(barangay_id or ""),
        "selected_region": selected_region,
        "selected_province": selected_province,
        "selected_municipality": selected_municipality,
        "selected_barangay": selected_barangay,
        "filter_summary": ", ".join(filter_summary_parts),
        "filters_applied": any(
            identifier for identifier in [region_id, province_id, municipality_id, barangay_id]
        ),
    }
    return render(request, "mana/mana_geographic_data.html", context)


__all__ = [
    "mana_home",
    "mana_new_assessment",
    "mana_manage_assessments",
    "mana_geographic_data",
]
