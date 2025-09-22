"""Community-centric serializers."""

from rest_framework import serializers

from ..models import CommunityInfrastructure, CommunityLivelihood, OBCCommunity
from .base import COMMUNITY_PROFILE_SERIALIZER_FIELDS


class CommunityLivelihoodSerializer(serializers.ModelSerializer):
    """Serializer for Community Livelihood model."""

    livelihood_type_display = serializers.CharField(
        source="get_livelihood_type_display", read_only=True
    )
    income_level_display = serializers.CharField(
        source="get_income_level_display", read_only=True
    )

    class Meta:
        model = CommunityLivelihood
        fields = [
            "id",
            "livelihood_type",
            "livelihood_type_display",
            "specific_activity",
            "description",
            "households_involved",
            "percentage_of_community",
            "is_primary_livelihood",
            "seasonal",
            "income_level",
            "income_level_display",
            "challenges",
            "opportunities",
        ]


class CommunityInfrastructureSerializer(serializers.ModelSerializer):
    """Serializer for Community Infrastructure model."""

    infrastructure_type_display = serializers.CharField(
        source="get_infrastructure_type_display", read_only=True
    )
    availability_status_display = serializers.CharField(
        source="get_availability_status_display", read_only=True
    )
    condition_display = serializers.CharField(
        source="get_condition_display", read_only=True
    )
    priority_display = serializers.CharField(
        source="get_priority_for_improvement_display", read_only=True
    )

    class Meta:
        model = CommunityInfrastructure
        fields = [
            "id",
            "infrastructure_type",
            "infrastructure_type_display",
            "availability_status",
            "availability_status_display",
            "description",
            "coverage_percentage",
            "condition",
            "condition_display",
            "priority_for_improvement",
            "priority_display",
            "notes",
            "last_assessed",
        ]


class OBCCommunitySerializer(serializers.ModelSerializer):
    """Full serializer for OBC Community model."""

    region_name = serializers.CharField(
        source="barangay.municipality.province.region.name", read_only=True
    )
    province_name = serializers.CharField(
        source="barangay.municipality.province.name", read_only=True
    )
    municipality_name = serializers.CharField(
        source="barangay.municipality.name", read_only=True
    )
    barangay_name = serializers.CharField(source="barangay.name", read_only=True)
    livelihoods = CommunityLivelihoodSerializer(many=True, read_only=True)
    infrastructure = CommunityInfrastructureSerializer(many=True, read_only=True)

    class Meta:
        model = OBCCommunity
        fields = [
            "id",
            "community_reference",
            "community_names",
            "display_name",
            "region_name",
            "province_name",
            "municipality_name",
            "barangay",
            "barangay_name",
            "obc_id",
            "community_type",
            "settlement_type",
            "development_status",
            "specific_location",
            "latitude",
            "longitude",
            "population",
            "households",
            "families",
            "established_year",
            "primary_language",
            "other_languages",
            "primary_ethnolinguistic_group",
            "other_ethnolinguistic_groups",
            "religious_affiliation",
            "community_leader",
            "leader_contact",
            "notes",
            *COMMUNITY_PROFILE_SERIALIZER_FIELDS,
            "livelihoods",
            "infrastructure",
            "created_at",
            "updated_at",
        ]


class OBCCommunityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for community list views."""

    region_name = serializers.CharField(
        source="barangay.municipality.province.region.name", read_only=True
    )
    province_name = serializers.CharField(
        source="barangay.municipality.province.name", read_only=True
    )
    municipality_name = serializers.CharField(
        source="barangay.municipality.name", read_only=True
    )
    barangay_name = serializers.CharField(source="barangay.name", read_only=True)

    class Meta:
        model = OBCCommunity
        fields = [
            "id",
            "display_name",
            "community_names",
            "community_type",
            "settlement_type",
            "development_status",
            "population",
            "households",
            "region_name",
            "province_name",
            "municipality_name",
            "barangay_name",
            "created_at",
            "updated_at",
        ]


class CommunityStatsSerializer(serializers.Serializer):
    """Serializer for aggregated community statistics."""

    total_communities = serializers.IntegerField()
    total_population = serializers.IntegerField()
    total_households = serializers.IntegerField()
    average_household_size = serializers.FloatField()
    development_status_distribution = serializers.DictField()
    settlement_type_distribution = serializers.DictField()
    communities_by_region = serializers.DictField()
    infrastructure_gaps = serializers.DictField()
    livelihood_distribution = serializers.DictField()


__all__ = [
    "CommunityLivelihoodSerializer",
    "CommunityInfrastructureSerializer",
    "OBCCommunitySerializer",
    "OBCCommunityListSerializer",
    "CommunityStatsSerializer",
]
