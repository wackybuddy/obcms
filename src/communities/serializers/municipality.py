"""Municipality coverage serializers."""

from rest_framework import serializers

from ..models import MunicipalityCoverage
from .base import COMMUNITY_PROFILE_SERIALIZER_FIELDS


class MunicipalityCoverageSerializer(serializers.ModelSerializer):
    """Serializer for municipality Bangsamoro coverage records."""

    municipality_name = serializers.CharField(
        source="municipality.name", read_only=True
    )
    municipality_type = serializers.CharField(
        source="municipality.get_municipality_type_display", read_only=True
    )
    province_name = serializers.CharField(source="province.name", read_only=True)
    province_code = serializers.CharField(source="province.code", read_only=True)
    region_name = serializers.CharField(source="region.name", read_only=True)
    region_code = serializers.CharField(source="region.code", read_only=True)
    full_location = serializers.ReadOnlyField()
    total_age_demographics = serializers.ReadOnlyField()
    average_household_size = serializers.ReadOnlyField()
    percentage_obc_in_barangay = serializers.ReadOnlyField()
    coordinates = serializers.ReadOnlyField()

    class Meta:
        model = MunicipalityCoverage
        fields = [
            "id",
            "municipality",
            "municipality_name",
            "municipality_type",
            "province_name",
            "province_code",
            "region_name",
            "region_code",
            "full_location",
            "total_obc_communities",
            "auto_sync",
            "existing_support_programs",
            *COMMUNITY_PROFILE_SERIALIZER_FIELDS,
            "total_age_demographics",
            "average_household_size",
            "percentage_obc_in_barangay",
            "coordinates",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


__all__ = ["MunicipalityCoverageSerializer"]
