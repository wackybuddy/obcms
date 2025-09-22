from django.db.models import Avg, Count, Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import (CommunityInfrastructure, CommunityLivelihood,
                      MunicipalityCoverage, OBCCommunity, Stakeholder,
                      StakeholderEngagement)
from ..serializers import (CommunityInfrastructureSerializer,
                           CommunityLivelihoodSerializer,
                           CommunityStatsSerializer,
                           MunicipalityCoverageSerializer,
                           OBCCommunityListSerializer, OBCCommunitySerializer,
                           StakeholderEngagementSerializer,
                           StakeholderListSerializer, StakeholderSerializer,
                           StakeholderStatsSerializer)


class MunicipalityCoverageViewSet(viewsets.ModelViewSet):
    """API ViewSet for municipalities/cities with Bangsamoro communities."""

    queryset = MunicipalityCoverage.objects.select_related(
        "municipality__province__region",
        "created_by",
        "updated_by",
    )
    serializer_class = MunicipalityCoverageSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = (
        "municipality__province__region",
        "municipality__province",
        "municipality__municipality_type",
    )
    search_fields = (
        "municipality__name",
        "municipality__province__name",
        "municipality__province__region__name",
        "key_barangays",
        "existing_support_programs",
        "notes",
    )
    ordering_fields = (
        "municipality__name",
        "municipality__province__name",
        "municipality__province__region__name",
        "total_obc_communities",
        "estimated_obc_population",
        "created_at",
    )
    ordering = (
        "municipality__province__region__name",
        "municipality__province__name",
        "municipality__name",
    )

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(updated_by=user)


class OBCCommunityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OBC Community model.
    Provides CRUD operations for OBC communities.
    """

    queryset = (
        OBCCommunity.objects.filter(is_active=True)
        .select_related("barangay__municipality__province__region")
        .prefetch_related("livelihoods", "infrastructure")
    )

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "development_status",
        "settlement_type",
        "mosques_count",
        "madrasah_count",
        "barangay__municipality__province__region",
        "barangay__municipality__province",
        "barangay__municipality",
        "barangay",
        "primary_language",
    ]
    search_fields = [
        "name",
        "specific_location",
        "primary_language",
        "community_leader",
        "cultural_background",
        "priority_needs",
        "notes",
        "barangay__name",
        "barangay__municipality__name",
        "barangay__municipality__province__name",
    ]
    ordering_fields = [
        "name",
        "population",
        "households",
        "established_year",
        "development_status",
        "created_at",
        "updated_at",
    ]
    ordering = [
        "barangay__municipality__province__region__code",
        "barangay__municipality__province__name",
        "barangay__municipality__name",
        "barangay__name",
        "name",
    ]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return OBCCommunityListSerializer
        return OBCCommunitySerializer

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get comprehensive statistics about OBC communities."""
        communities = self.get_queryset()

        # Basic counts
        total_communities = communities.count()
        total_population = (
            communities.aggregate(Sum("population"))["population__sum"] or 0
        )
        total_households = (
            communities.aggregate(Sum("households"))["households__sum"] or 0
        )

        # Average household size
        avg_household_size = (
            communities.exclude(
                households__isnull=True, population__isnull=True
            ).aggregate(
                avg_size=(
                    Avg("population") / Avg("households")
                    if communities.exclude(
                        households__isnull=True, population__isnull=True
                    ).exists()
                    else 0
                )
            )[
                "avg_size"
            ]
            or 0
        )

        # By region
        by_region = dict(
            communities.values("barangay__municipality__province__region__name")
            .annotate(count=Count("id"), population=Sum("population"))
            .values_list("barangay__municipality__province__region__name", "count")
        )

        # By development status
        by_development_status = dict(
            communities.values("development_status")
            .annotate(count=Count("id"))
            .values_list("development_status", "count")
        )

        # By settlement type
        by_settlement_type = dict(
            communities.values("settlement_type")
            .annotate(count=Count("id"))
            .values_list("settlement_type", "count")
        )

        # Religious facilities
        religious_facilities = {
            "communities_with_mosque": communities.filter(mosques_count__gt=0).count(),
            "communities_with_madrasah": communities.filter(madrasah_count__gt=0).count(),
            "communities_with_both": communities.filter(
                mosques_count__gt=0, madrasah_count__gt=0
            ).count(),
            "total_religious_leaders": communities.aggregate(
                Sum("religious_leaders_count")
            )["religious_leaders_count__sum"]
            or 0,
        }

        # Language distribution
        language_distribution = {}
        for community in communities:
            if community.primary_language:
                lang = community.primary_language
                language_distribution[lang] = language_distribution.get(lang, 0) + 1

        stats_data = {
            "total_communities": total_communities,
            "total_population": total_population,
            "total_households": total_households,
            "by_region": by_region,
            "by_development_status": by_development_status,
            "by_settlement_type": by_settlement_type,
            "religious_facilities": religious_facilities,
            "average_household_size": (
                round(avg_household_size, 1) if avg_household_size else 0
            ),
            "language_distribution": language_distribution,
        }

        serializer = CommunityStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def livelihoods(self, request, pk=None):
        """Get all livelihoods for this community."""
        community = self.get_object()
        livelihoods = community.livelihoods.all()
        serializer = CommunityLivelihoodSerializer(livelihoods, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def infrastructure(self, request, pk=None):
        """Get all infrastructure for this community."""
        community = self.get_object()
        infrastructure = community.infrastructure.all()
        serializer = CommunityInfrastructureSerializer(infrastructure, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_region(self, request):
        """Get communities grouped by region."""
        region_param = request.query_params.get("region")
        if region_param:
            communities = self.get_queryset().filter(
                barangay__municipality__province__region__code=region_param
            )
        else:
            communities = self.get_queryset()

        serializer = self.get_serializer(communities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def vulnerable(self, request):
        """Get communities with vulnerable or at-risk status."""
        communities = self.get_queryset().filter(
            development_status__in=["vulnerable", "at_risk"]
        )
        serializer = self.get_serializer(communities, many=True)
        return Response(serializer.data)


class CommunityLivelihoodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Community Livelihood model.
    """

    queryset = CommunityLivelihood.objects.all().select_related("community")
    serializer_class = CommunityLivelihoodSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "livelihood_type",
        "is_primary_livelihood",
        "seasonal",
        "income_level",
        "community",
        "community__development_status",
        "community__barangay__municipality__province__region",
    ]
    search_fields = ["specific_activity", "description", "challenges", "opportunities"]
    ordering_fields = [
        "livelihood_type",
        "percentage_of_community",
        "households_involved",
    ]
    ordering = ["community__name", "-is_primary_livelihood", "livelihood_type"]


class CommunityInfrastructureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Community Infrastructure model.
    """

    queryset = CommunityInfrastructure.objects.all().select_related("community")
    serializer_class = CommunityInfrastructureSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "infrastructure_type",
        "availability_status",
        "condition",
        "priority_for_improvement",
        "community",
        "community__development_status",
        "community__barangay__municipality__province__region",
    ]
    search_fields = ["description", "notes"]
    ordering_fields = [
        "infrastructure_type",
        "coverage_percentage",
        "priority_for_improvement",
    ]
    ordering = ["community__name", "infrastructure_type"]

    @action(detail=False, methods=["get"])
    def critical_needs(self, request):
        """Get infrastructure with critical priority."""
        infrastructure = self.get_queryset().filter(priority_for_improvement="critical")
        serializer = self.get_serializer(infrastructure, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get infrastructure grouped by type."""
        infra_type = request.query_params.get("type")
        if infra_type:
            infrastructure = self.get_queryset().filter(infrastructure_type=infra_type)
        else:
            infrastructure = self.get_queryset()

        serializer = self.get_serializer(infrastructure, many=True)
        return Response(serializer.data)


class StakeholderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Stakeholder model.
    Provides CRUD operations for community stakeholders.
    """

    queryset = Stakeholder.objects.select_related(
        "community__barangay__municipality__province__region"
    ).prefetch_related("engagements")

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "stakeholder_type",
        "influence_level",
        "engagement_level",
        "is_active",
        "is_verified",
        "community",
        "community__development_status",
        "community__barangay__municipality__province__region",
    ]
    search_fields = [
        "full_name",
        "nickname",
        "position",
        "organization",
        "contact_number",
        "email",
        "areas_of_influence",
        "special_skills",
        "community__name",
    ]
    ordering_fields = [
        "full_name",
        "stakeholder_type",
        "influence_level",
        "engagement_level",
        "since_year",
        "created_at",
    ]
    ordering = ["community__name", "stakeholder_type", "full_name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return StakeholderListSerializer
        return StakeholderSerializer

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get comprehensive statistics about stakeholders."""
        from datetime import timedelta

        from django.utils import timezone

        stakeholders = self.get_queryset()

        # Basic counts
        total_stakeholders = stakeholders.count()
        active_stakeholders = stakeholders.filter(is_active=True).count()
        verified_stakeholders = stakeholders.filter(is_verified=True).count()

        # By type
        by_type = dict(
            stakeholders.values("stakeholder_type")
            .annotate(count=Count("id"))
            .values_list("stakeholder_type", "count")
        )

        # By influence level
        by_influence_level = dict(
            stakeholders.values("influence_level")
            .annotate(count=Count("id"))
            .values_list("influence_level", "count")
        )

        # By engagement level
        by_engagement_level = dict(
            stakeholders.values("engagement_level")
            .annotate(count=Count("id"))
            .values_list("engagement_level", "count")
        )

        # By community
        by_community = dict(
            stakeholders.values("community__name")
            .annotate(count=Count("id"))
            .values_list("community__name", "count")
        )

        # Recent engagements (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_engagements = StakeholderEngagement.objects.filter(
            stakeholder__in=stakeholders, date__gte=thirty_days_ago
        ).count()

        stats_data = {
            "total_stakeholders": total_stakeholders,
            "active_stakeholders": active_stakeholders,
            "verified_stakeholders": verified_stakeholders,
            "by_type": by_type,
            "by_influence_level": by_influence_level,
            "by_engagement_level": by_engagement_level,
            "by_community": by_community,
            "recent_engagements": recent_engagements,
        }

        serializer = StakeholderStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Verify a stakeholder."""
        from django.utils import timezone

        stakeholder = self.get_object()
        stakeholder.is_verified = True
        stakeholder.verification_date = timezone.now().date()
        stakeholder.save()

        serializer = self.get_serializer(stakeholder)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def unverify(self, request, pk=None):
        """Unverify a stakeholder."""
        stakeholder = self.get_object()
        stakeholder.is_verified = False
        stakeholder.verification_date = None
        stakeholder.save()

        serializer = self.get_serializer(stakeholder)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def engagements(self, request, pk=None):
        """Get all engagements for this stakeholder."""
        stakeholder = self.get_object()
        engagements = stakeholder.engagements.all().order_by("-date")
        serializer = StakeholderEngagementSerializer(engagements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get stakeholders filtered by type."""
        stakeholder_type = request.query_params.get("type")
        if stakeholder_type:
            stakeholders = self.get_queryset().filter(stakeholder_type=stakeholder_type)
        else:
            stakeholders = self.get_queryset()

        serializer = self.get_serializer(stakeholders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def religious_leaders(self, request):
        """Get religious leaders (Ulama, Imam, Ustadz, etc.)."""
        stakeholders = self.get_queryset().filter(
            stakeholder_type__in=["ulama", "imam", "ustadz", "madrasa_teacher"]
        )
        serializer = self.get_serializer(stakeholders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def community_leaders(self, request):
        """Get community leaders (including tribal leaders)."""
        stakeholders = self.get_queryset().filter(
            stakeholder_type__in=[
                "community_leader",
                "barangay_captain",
                "tribal_leader",
            ]
        )
        serializer = self.get_serializer(stakeholders, many=True)
        return Response(serializer.data)


class StakeholderEngagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Stakeholder Engagement model.
    """

    queryset = StakeholderEngagement.objects.select_related(
        "stakeholder", "stakeholder__community"
    ).all()
    serializer_class = StakeholderEngagementSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "engagement_type",
        "outcome",
        "follow_up_needed",
        "stakeholder",
        "stakeholder__stakeholder_type",
        "stakeholder__community",
        "stakeholder__community__development_status",
    ]
    search_fields = [
        "title",
        "description",
        "key_points",
        "action_items",
        "stakeholder__full_name",
        "stakeholder__nickname",
        "documented_by",
        "location",
    ]
    ordering_fields = ["date", "engagement_type", "outcome", "participants_count"]
    ordering = ["-date", "stakeholder__full_name"]

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent engagements (last 30 days)."""
        from datetime import timedelta

        from django.utils import timezone

        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        engagements = self.get_queryset().filter(date__gte=thirty_days_ago)
        serializer = self.get_serializer(engagements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def follow_up_needed(self, request):
        """Get engagements that need follow-up."""
        engagements = self.get_queryset().filter(follow_up_needed=True)
        serializer = self.get_serializer(engagements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_outcome(self, request):
        """Get engagements filtered by outcome."""
        outcome = request.query_params.get("outcome")
        if outcome:
            engagements = self.get_queryset().filter(outcome=outcome)
        else:
            engagements = self.get_queryset()

        serializer = self.get_serializer(engagements, many=True)
        return Response(serializer.data)
