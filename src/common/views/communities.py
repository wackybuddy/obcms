"""Views for OBC communities management screens."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import MunicipalityCoverageForm, OBCCommunityForm
from ..models import Barangay, Region
from ..services.locations import build_location_data


@login_required
def communities_home(request):
    """OBC Communities module home page."""
    from django.db.models import Avg, Count, Q

    from communities.models import (
        CommunityInfrastructure,
        MunicipalityCoverage,
        OBCCommunity,
        Stakeholder,
    )

    communities = OBCCommunity.objects.select_related(
        "barangay__municipality__province__region"
    ).annotate(stakeholder_count=Count("stakeholders"))

    municipality_coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region"
    )

    vulnerable_sectors = communities.aggregate(
        total_women=Sum("women_count"),
        total_solo_parents=Sum("solo_parents_count"),
        total_pwd=Sum("pwd_count"),
        total_farmers=Sum("farmers_count"),
        total_fisherfolk=Sum("fisherfolk_count"),
        total_unemployed=Sum("unemployed_count"),
        total_indigenous_peoples=Sum("indigenous_peoples_count"),
        total_idps=Sum("idps_count"),
        total_migrants_transients=Sum("migrants_transients_count"),
        total_csos=Sum("csos_count"),
        total_associations=Sum("associations_count"),
        total_cooperatives=Sum("number_of_cooperatives"),
    )

    infrastructure_stats = (
        CommunityInfrastructure.objects.filter(
            availability_status__in=["limited", "poor", "none"]
        )
        .values("infrastructure_type")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    development_status = (
        communities.values("development_status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    ethnolinguistic_groups = (
        communities.exclude(primary_ethnolinguistic_group__isnull=True)
        .exclude(primary_ethnolinguistic_group="")
        .values("primary_ethnolinguistic_group")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    stakeholder_stats = Stakeholder.objects.values("stakeholder_type").annotate(
        count=Count("id")
    )

    province_performance = (
        municipality_coverages.values("municipality__province__name")
        .annotate(
            communities_count=Sum("total_obc_communities"),
            population=Sum("estimated_obc_population"),
        )
        .order_by("-communities_count")[:5]
    )

    stats = {
        "communities": {
            "total": communities.count(),
            "active": communities.filter(is_active=True).count(),
            "total_population": communities.aggregate(
                total=Sum("estimated_obc_population")
            )["total"]
            or 0,
            "total_households": communities.aggregate(total=Sum("households"))["total"]
            or 0,
            "by_region": communities.values(
                "barangay__municipality__province__region__name"
            )
            .annotate(count=Count("id"))
            .order_by("-count"),
            "recent": communities.order_by("-created_at")[:10],
            "development_status": development_status,
            "with_madrasah": communities.filter(madrasah_count__gt=0).count(),
            "with_mosque": communities.filter(mosques_count__gt=0).count(),
        },
        "vulnerable_sectors": vulnerable_sectors,
        "infrastructure_needs": infrastructure_stats,
        "ethnolinguistic_groups": ethnolinguistic_groups,
        "poverty_levels": communities.values("estimated_poverty_incidence")
        .annotate(count=Count("id"))
        .exclude(estimated_poverty_incidence="")
        .order_by("estimated_poverty_incidence"),
        "municipalities": {
            "total": municipality_coverages.count(),
            "total_population": municipality_coverages.aggregate(
                total=Sum("estimated_obc_population")
            )["total"]
            or 0,
            "total_obc_communities": municipality_coverages.aggregate(
                total=Sum("total_obc_communities")
            )["total"]
            or 0,
            "by_region": municipality_coverages.values(
                "municipality__province__region__name"
            )
            .annotate(count=Count("id"))
            .order_by("-count"),
            "recent": municipality_coverages.order_by("-created_at")[:5],
            "top_performers": province_performance,
        },
        "stakeholders": stakeholder_stats,
    }

    context = {
        "stats": stats,
        "communities": communities[:20],
        "municipality_coverages": municipality_coverages[:20],
    }
    return render(request, "communities/communities_home.html", context)


@login_required
def communities_add(request):
    """Add new community page."""
    from communities.models import MunicipalityCoverage, OBCCommunity

    if request.method == "POST":
        form = OBCCommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.save()
            MunicipalityCoverage.sync_for_municipality(community.barangay.municipality)
            messages.success(
                request,
                f'Community "{community.barangay.name}" has been successfully added.',
            )
            return redirect("common:communities_manage")
    else:
        form = OBCCommunityForm()

    recent_communities = OBCCommunity.objects.order_by("-created_at")[:5]
    barangays = Barangay.objects.select_related(
        "municipality__province__region"
    ).order_by("municipality__province__region__name", "municipality__name", "name")

    context = {
        "form": form,
        "recent_communities": recent_communities,
        "barangays": barangays,
        "location_data": build_location_data(),
        "show_barangay_field": True,
        "page_title": "Add Barangay OBC",
        "breadcrumb_label": "Add Barangay OBC",
        "page_subtitle": "Register a barangay-level OBC profile with detailed demographic, socio-economic, and services data.",
        "form_heading": "Barangay OBC Form",
    }
    return render(request, "communities/communities_add.html", context)


@login_required
def communities_add_municipality(request):
    """Record a municipality or city with Bangsamoro communities."""
    from communities.models import MunicipalityCoverage

    if request.method == "POST":
        form = MunicipalityCoverageForm(request.POST)
        if form.is_valid():
            coverage = form.save(commit=False)
            coverage.created_by = request.user if request.user.is_authenticated else None
            coverage.updated_by = coverage.created_by
            coverage.save()
            coverage.refresh_from_communities()
            messages.success(
                request,
                f'Municipality/City "{coverage.municipality.name}" has been added to the Bangsamoro coverage map.',
            )
            return redirect("common:communities_manage")
    else:
        form = MunicipalityCoverageForm()

    recent_coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region"
    ).order_by("-created_at")[:5]

    context = {
        "form": form,
        "recent_communities": [],
        "location_data": build_location_data(include_barangays=False),
        "show_barangay_field": False,
        "page_title": "Add Municipal / City OBC",
        "breadcrumb_label": "Add Municipal / City OBC",
        "page_subtitle": "Capture municipality- or city-wide OBC data that can be disaggregated to barangays later.",
        "form_heading": "Municipality OBC Form",
        "recent_coverages": recent_coverages,
    }
    return render(request, "communities/communities_add.html", context)


@login_required
def communities_manage(request):
    """Manage communities page."""
    from django.db.models import Count, Q

    from communities.models import MunicipalityCoverage, OBCCommunity

    communities = (
        OBCCommunity.objects.select_related("barangay__municipality__province__region")
        .annotate(stakeholder_count=Count("stakeholders"))
        .order_by("barangay__name")
    )

    municipality_coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region"
    ).order_by(
        "municipality__province__region__name",
        "municipality__province__name",
        "municipality__name",
    )

    region_filter = request.GET.get("region")
    status_filter = request.GET.get("status")
    search_query = request.GET.get("search")

    if region_filter:
        communities = communities.filter(
            barangay__municipality__province__region__id=region_filter
        )
        municipality_coverages = municipality_coverages.filter(
            municipality__province__region__id=region_filter
        )

    if status_filter:
        if status_filter == "active":
            communities = communities.filter(is_active=True)
        elif status_filter == "inactive":
            communities = communities.filter(is_active=False)

    if search_query:
        communities = communities.filter(
            Q(barangay__name__icontains=search_query)
            | Q(barangay__municipality__name__icontains=search_query)
            | Q(barangay__municipality__province__name__icontains=search_query)
            | Q(barangay__municipality__province__region__name__icontains=search_query)
        )
        municipality_coverages = municipality_coverages.filter(
            Q(municipality__name__icontains=search_query)
            | Q(municipality__province__name__icontains=search_query)
            | Q(municipality__province__region__name__icontains=search_query)
            | Q(key_barangays__icontains=search_query)
        )

    regions = Region.objects.all().order_by("name")

    total_barangay_obcs = communities.count()
    total_barangay_population = (
        communities.aggregate(total=Sum("estimated_obc_population"))["total"] or 0
    )
    total_municipality_obcs = municipality_coverages.count()
    total_municipality_population = (
        municipality_coverages.aggregate(total=Sum("estimated_obc_population"))["total"]
        or 0
    )
    total_municipality_communities = (
        municipality_coverages.aggregate(total=Sum("total_obc_communities"))["total"]
        or 0
    )

    stat_cards = [
        {
            "title": "Total Barangay OBCs in the Database",
            "value": total_barangay_obcs,
            "icon": "fas fa-users",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "text_color": "text-blue-100",
        },
        {
            "title": "Total OBC Population from Barangays",
            "value": total_barangay_population,
            "icon": "fas fa-user-friends",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "text_color": "text-emerald-100",
        },
        {
            "title": "Total Municipalities OBCs in the Database",
            "value": total_municipality_obcs,
            "icon": "fas fa-city",
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "text_color": "text-purple-100",
        },
    ]

    lg_columns = 4 if len(stat_cards) >= 4 else 3
    stat_cards_grid_class = (
        f"mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-{lg_columns} gap-6"
    )

    context = {
        "communities": communities,
        "regions": regions,
        "current_region": region_filter,
        "current_status": status_filter,
        "search_query": search_query,
        "total_communities": total_barangay_obcs,
        "total_population": total_barangay_population,
        "municipality_coverages": municipality_coverages,
        "total_municipality_coverages": total_municipality_obcs,
        "total_municipality_population": total_municipality_population,
        "total_municipality_communities": total_municipality_communities,
        "stat_cards": stat_cards,
        "stat_cards_grid_class": stat_cards_grid_class,
    }
    return render(request, "communities/communities_manage.html", context)


@login_required
def communities_manage_municipal(request):
    """Manage municipality-level OBC coverage."""
    from django.db.models import Count, Q

    from communities.models import MunicipalityCoverage

    coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region",
        "created_by",
        "updated_by",
    ).order_by(
        "municipality__province__region__name",
        "municipality__province__name",
        "municipality__name",
    )

    region_filter = request.GET.get("region")
    status_filter = request.GET.get("status")
    search_query = request.GET.get("search")

    if region_filter:
        coverages = coverages.filter(
            municipality__province__region__id=region_filter
        )

    if status_filter == "auto":
        coverages = coverages.filter(auto_sync=True)
    elif status_filter == "manual":
        coverages = coverages.filter(auto_sync=False)

    if search_query:
        coverages = coverages.filter(
            Q(municipality__name__icontains=search_query)
            | Q(municipality__province__name__icontains=search_query)
            | Q(municipality__province__region__name__icontains=search_query)
            | Q(key_barangays__icontains=search_query)
        )

    regions = Region.objects.all().order_by("name")

    total_coverages = coverages.count()
    total_population = (
        coverages.aggregate(total=Sum("estimated_obc_population"))["total"] or 0
    )
    total_communities = (
        coverages.aggregate(total=Sum("total_obc_communities"))["total"] or 0
    )
    auto_synced = coverages.filter(auto_sync=True).count()
    manual_updates = coverages.filter(auto_sync=False).count()

    stats = {
        "total_coverages": total_coverages,
        "total_population": total_population,
        "total_communities": total_communities,
        "auto_synced": auto_synced,
        "manual": manual_updates,
    }

    stat_cards = [
        {
            "title": "Total Municipal OBCs in the Database",
            "value": total_coverages,
            "icon": "fas fa-city",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "text_color": "text-blue-100",
        },
        {
            "title": "Total OBC Population from the Municipalities",
            "value": total_population,
            "icon": "fas fa-users",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "text_color": "text-emerald-100",
        },
        {
            "title": "Auto-Synced Municipalities",
            "value": auto_synced,
            "icon": "fas fa-sync-alt",
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "text_color": "text-purple-100",
        },
        {
            "title": "Manually Updated Municipalities",
            "value": manual_updates,
            "icon": "fas fa-edit",
            "gradient": "from-orange-500 via-orange-600 to-orange-700",
            "text_color": "text-orange-100",
        },
    ]

    stat_cards_grid_class = "mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"

    context = {
        "coverages": coverages,
        "regions": regions,
        "current_region": region_filter,
        "current_status": status_filter,
        "search_query": search_query,
        "stats": stats,
        "stat_cards": stat_cards,
        "stat_cards_grid_class": stat_cards_grid_class,
    }
    return render(request, "communities/municipal_manage.html", context)


@login_required
def communities_edit(request, community_id):
    """Edit an existing barangay-level community."""
    from communities.models import MunicipalityCoverage, OBCCommunity

    community = get_object_or_404(
        OBCCommunity.objects.select_related(
            "barangay__municipality__province__region"
        ),
        pk=community_id,
    )

    if request.method == "POST":
        form = OBCCommunityForm(request.POST, instance=community)
        if form.is_valid():
            community = form.save()
            MunicipalityCoverage.sync_for_municipality(
                community.barangay.municipality
            )
            messages.success(
                request,
                f'Barangay OBC "{community.display_name}" has been updated successfully.',
            )
            return redirect("common:communities_manage")
    else:
        form = OBCCommunityForm(instance=community)

    recent_communities = (
        OBCCommunity.objects.exclude(pk=community.pk).order_by("-created_at")[:5]
    )

    context = {
        "form": form,
        "community": community,
        "page_title": "Edit Barangay OBC",
        "breadcrumb_label": "Edit Barangay OBC",
        "page_subtitle": "Update barangay-level community information.",
        "form_heading": "Barangay OBC Form",
        "location_data": build_location_data(),
        "show_barangay_field": True,
        "recent_communities": recent_communities,
    }
    return render(request, "communities/communities_add.html", context)


@login_required
@require_POST
def communities_delete(request, community_id):
    """Delete an existing barangay-level community."""
    from communities.models import MunicipalityCoverage, OBCCommunity

    community = get_object_or_404(
        OBCCommunity.objects.select_related(
            "barangay__municipality__province__region"
        ),
        pk=community_id,
    )
    municipality = community.barangay.municipality if community.barangay else None
    community_name = community.display_name
    community.delete()

    if municipality:
        MunicipalityCoverage.sync_for_municipality(municipality)

    messages.success(
        request,
        f'Barangay OBC "{community_name}" has been removed from the registry.',
    )
    return redirect("common:communities_manage")


@login_required
def communities_stakeholders(request):
    """Manage stakeholders page."""
    from django.db.models import Count

    from communities.models import OBCCommunity, Stakeholder

    stakeholders = Stakeholder.objects.select_related(
        "community", "community__barangay__municipality__province__region"
    ).prefetch_related("engagements")

    community_filter = request.GET.get("community")
    type_filter = request.GET.get("type")
    status_filter = request.GET.get("status")

    if community_filter:
        stakeholders = stakeholders.filter(community__id=community_filter)

    if type_filter:
        stakeholders = stakeholders.filter(stakeholder_type=type_filter)

    if status_filter:
        if status_filter == "active":
            stakeholders = stakeholders.filter(is_active=True)
        elif status_filter == "verified":
            stakeholders = stakeholders.filter(is_verified=True)

    communities = OBCCommunity.objects.order_by("barangay__name")
    stakeholder_types = Stakeholder.STAKEHOLDER_TYPES

    stats = {
        "total_stakeholders": stakeholders.count(),
        "active_stakeholders": stakeholders.filter(is_active=True).count(),
        "verified_stakeholders": stakeholders.filter(is_verified=True).count(),
        "by_type": stakeholders.values("stakeholder_type").annotate(count=Count("id")),
    }

    context = {
        "stakeholders": stakeholders.order_by("full_name"),
        "communities": communities,
        "stakeholder_types": stakeholder_types,
        "current_community": community_filter,
        "current_type": type_filter,
        "current_status": status_filter,
        "stats": stats,
    }
    return render(request, "communities/communities_stakeholders.html", context)


@login_required
def communities_edit_municipal(request, coverage_id):
    """Edit an existing municipality coverage record."""
    from communities.models import MunicipalityCoverage

    coverage = get_object_or_404(
        MunicipalityCoverage.objects.select_related("municipality__province__region"),
        pk=coverage_id,
    )

    if request.method == "POST":
        form = MunicipalityCoverageForm(request.POST, instance=coverage)
        if form.is_valid():
            coverage = form.save()
            coverage.refresh_from_communities()
            messages.success(
                request,
                f"Municipal OBC coverage for {coverage.municipality.name} has been updated.",
            )
            return redirect("common:communities_manage_municipal")
    else:
        form = MunicipalityCoverageForm(instance=coverage)

    recent_coverages = (
        MunicipalityCoverage.objects.exclude(pk=coverage.pk)
        .select_related("municipality__province__region")
        .order_by("-created_at")[:5]
    )

    context = {
        "form": form,
        "coverage": coverage,
        "page_title": "Edit Municipal OBC",
        "breadcrumb_label": "Edit Municipal OBC",
        "page_subtitle": "Update municipality-level Bangsamoro coverage data.",
        "form_heading": "Municipal OBC Form",
        "location_data": build_location_data(include_barangays=False),
        "show_barangay_field": False,
        "recent_coverages": recent_coverages,
    }
    return render(request, "communities/communities_add.html", context)


@login_required
@require_POST
def communities_delete_municipal(request, coverage_id):
    """Delete a municipality coverage record."""
    from communities.models import MunicipalityCoverage

    coverage = get_object_or_404(
        MunicipalityCoverage.objects.select_related("municipality__province__region"),
        pk=coverage_id,
    )
    municipality_name = coverage.municipality.name
    coverage.delete()

    messages.success(
        request,
        f"Municipal OBC coverage for {municipality_name} has been removed.",
    )
    return redirect("common:communities_manage_municipal")


__all__ = [
    "communities_home",
    "communities_add",
    "communities_add_municipality",
    "communities_manage",
    "communities_manage_municipal",
    "communities_edit",
    "communities_delete",
    "communities_edit_municipal",
    "communities_delete_municipal",
    "communities_stakeholders"
]
