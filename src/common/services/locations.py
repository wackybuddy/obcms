"""Location-related services shared across modules."""

from typing import Dict, List

from ..models import Barangay, Municipality, Province, Region


def build_location_data(include_barangays: bool = True) -> Dict[str, List[dict]]:
    """Return hierarchical location data for cascading selects."""

    regions = Region.objects.filter(is_active=True).order_by("code", "name")
    provinces = (
        Province.objects.filter(is_active=True, region__is_active=True)
        .select_related("region")
        .order_by("name")
    )
    municipalities = (
        Municipality.objects.filter(
            is_active=True,
            province__is_active=True,
            province__region__is_active=True,
        )
        .select_related("province__region")
        .order_by("name")
    )

    data = {
        "regions": [
            {
                "id": region.id,
                "name": region.name,
                "code": region.code,
            }
            for region in regions
        ],
        "provinces": [
            {
                "id": province.id,
                "name": province.name,
                "region_id": province.region_id,
                "population": province.population_total,
            }
            for province in provinces
        ],
        "municipalities": [
            {
                "id": municipality.id,
                "name": municipality.name,
                "province_id": municipality.province_id,
                "population": municipality.population_total,
                "code": municipality.code,
            }
            for municipality in municipalities
        ],
    }

    if include_barangays:
        barangays = (
            Barangay.objects.filter(
                is_active=True,
                municipality__is_active=True,
                municipality__province__is_active=True,
                municipality__province__region__is_active=True,
            )
            .select_related("municipality__province__region")
            .order_by("name")
        )
        data["barangays"] = [
            {
                "id": barangay.id,
                "name": barangay.name,
                "municipality_id": barangay.municipality_id,
                "population": barangay.population_total,
                "code": barangay.code,
            }
            for barangay in barangays
        ]

    return data
