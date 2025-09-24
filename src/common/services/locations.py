"""Location-related services shared across modules."""

from collections import defaultdict
from typing import Dict, List

from django.db.models import Count

from ..models import Barangay, Municipality, Province, Region


def build_location_data(include_barangays: bool = True) -> Dict[str, List[dict]]:
    """Return hierarchical location data for cascading selects with geo metadata."""

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

    # Aggregate geographic-data availability per administrative level.
    geodata_by_region = defaultdict(int)
    geodata_communities_by_region = defaultdict(int)
    geodata_by_province = defaultdict(int)
    geodata_communities_by_province = defaultdict(int)
    geodata_by_municipality = defaultdict(int)
    geodata_communities_by_municipality = defaultdict(int)
    geodata_by_barangay = {}

    try:
        from communities.models import OBCCommunity
    except ImportError:  # pragma: no cover - defensive fallback during migrations
        community_records = []
    else:
        community_records = (
            OBCCommunity.objects.filter(is_active=True)
            .annotate(
                geo_layers_count=Count("geographic_layers", distinct=True),
                map_visualizations_count=Count("community_map_visualizations", distinct=True),
                spatial_points_count=Count("spatial_points", distinct=True),
            )
            .values(
                "barangay_id",
                "barangay__municipality_id",
                "barangay__municipality__province_id",
                "barangay__municipality__province__region_id",
                "geo_layers_count",
                "map_visualizations_count",
                "spatial_points_count",
            )
        )

    for record in community_records:
        total_geodata = (
            int(record["geo_layers_count"])
            + int(record["map_visualizations_count"])
            + int(record["spatial_points_count"])
        )
        if total_geodata <= 0:
            continue

        barangay_id = record["barangay_id"]
        municipality_id = record["barangay__municipality_id"]
        province_id = record["barangay__municipality__province_id"]
        region_id = record["barangay__municipality__province__region_id"]

        geodata_by_barangay[barangay_id] = {
            "total": total_geodata,
            "layers": int(record["geo_layers_count"]),
            "visualizations": int(record["map_visualizations_count"]),
            "points": int(record["spatial_points_count"]),
        }

        geodata_by_municipality[municipality_id] += total_geodata
        geodata_communities_by_municipality[municipality_id] += 1

        geodata_by_province[province_id] += total_geodata
        geodata_communities_by_province[province_id] += 1

        geodata_by_region[region_id] += total_geodata
        geodata_communities_by_region[region_id] += 1

    data = {
        "regions": [
            {
                "id": region.id,
                "name": region.name,
                "code": region.code,
                "geodata_count": int(geodata_by_region.get(region.id, 0)),
                "geodata_communities": int(
                    geodata_communities_by_region.get(region.id, 0)
                ),
                "has_geodata": geodata_by_region.get(region.id, 0) > 0,
            }
            for region in regions
        ],
        "provinces": [
            {
                "id": province.id,
                "name": province.name,
                "region_id": province.region_id,
                "population": province.population_total,
                "geodata_count": int(geodata_by_province.get(province.id, 0)),
                "geodata_communities": int(
                    geodata_communities_by_province.get(province.id, 0)
                ),
                "has_geodata": geodata_by_province.get(province.id, 0) > 0,
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
                "geodata_count": int(geodata_by_municipality.get(municipality.id, 0)),
                "geodata_communities": int(
                    geodata_communities_by_municipality.get(municipality.id, 0)
                ),
                "has_geodata": geodata_by_municipality.get(municipality.id, 0) > 0,
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
                "geodata_count": int(
                    geodata_by_barangay.get(barangay.id, {}).get("total", 0)
                ),
                "geodata_layers": int(
                    geodata_by_barangay.get(barangay.id, {}).get("layers", 0)
                ),
                "geodata_visualizations": int(
                    geodata_by_barangay.get(barangay.id, {}).get("visualizations", 0)
                ),
                "geodata_points": int(
                    geodata_by_barangay.get(barangay.id, {}).get("points", 0)
                ),
                "has_geodata": barangay.id in geodata_by_barangay,
            }
            for barangay in barangays
        ]

    return data
