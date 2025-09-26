"""Location-related services shared across modules."""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from django.db.models import Avg, Count

from ..models import Barangay, Municipality, Province, Region


def _normalise_float(value: object) -> Optional[float]:
    """Best-effort conversion to float, returning ``None`` on failure."""

    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_lat_lng(center) -> Tuple[Optional[float], Optional[float]]:
    """Return lat/lng floats from stored center coordinate structures."""

    if not center:
        return None, None

    lat = None
    lng = None

    if isinstance(center, dict):
        lat = center.get("lat") or center.get("latitude")
        lng = center.get("lng") or center.get("lon") or center.get("longitude")
    elif isinstance(center, (list, tuple)) and len(center) == 2:
        # Some sources store [lng, lat], others [lat, lng] – try both.
        first = _normalise_float(center[0])
        second = _normalise_float(center[1])
        # Prefer treating the structure as [lng, lat] unless that yields
        # impossible latitude values.
        if first is not None and second is not None and -90 <= second <= 90:
            lng, lat = first, second
        else:  # fallback to assuming [lat, lng]
            lat, lng = first, second

    lat = _normalise_float(lat)
    lng = _normalise_float(lng)

    if lat is None or lng is None:
        return None, None

    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return None, None

    return lat, lng


def _extract_bbox_center(bounding_box) -> Tuple[Optional[float], Optional[float]]:
    """Compute the centroid of a bounding box."""

    if not bounding_box:
        return None, None

    if isinstance(bounding_box, dict):
        min_lng = bounding_box.get("min_lng") or bounding_box.get("min_lon")
        max_lng = bounding_box.get("max_lng") or bounding_box.get("max_lon")
        min_lat = bounding_box.get("min_lat")
        max_lat = bounding_box.get("max_lat")
    elif isinstance(bounding_box, (list, tuple)) and len(bounding_box) == 4:
        min_lng, min_lat, max_lng, max_lat = bounding_box
    else:
        return None, None

    min_lat = _normalise_float(min_lat)
    max_lat = _normalise_float(max_lat)
    min_lng = _normalise_float(min_lng)
    max_lng = _normalise_float(max_lng)

    if None in {min_lat, max_lat, min_lng, max_lng}:
        return None, None

    lat = (min_lat + max_lat) / 2
    lng = (min_lng + max_lng) / 2

    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return None, None

    return lat, lng


def get_object_centroid(obj) -> Tuple[Optional[float], Optional[float]]:
    """Best available centroid for a location-aware model instance."""

    if obj is None:
        return None, None

    lat = _normalise_float(getattr(obj, "latitude", None))
    lng = _normalise_float(getattr(obj, "longitude", None))
    if lat is not None and lng is not None:
        return lat, lng

    lat_lng = _extract_lat_lng(getattr(obj, "center_coordinates", None))
    if all(value is not None for value in lat_lng):
        return lat_lng

    return _extract_bbox_center(getattr(obj, "bounding_box", None))


def _centroid_metadata(obj) -> Dict[str, Optional[float]]:
    lat, lng = get_object_centroid(obj)
    return {"center_lat": lat, "center_lng": lng}


def _apply_centroid_fallback(metadata: Dict[str, Optional[float]], fallback: Optional[Tuple[float, float]]):
    if not fallback:
        return metadata
    fallback_lat, fallback_lng = fallback
    if metadata.get("center_lat") is None and fallback_lat is not None:
        metadata["center_lat"] = fallback_lat
    if metadata.get("center_lng") is None and fallback_lng is not None:
        metadata["center_lng"] = fallback_lng
    return metadata


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

    provinces = list(provinces)
    municipalities = list(municipalities)

    # Aggregate geographic-data availability per administrative level.
    geodata_by_region = defaultdict(int)
    geodata_communities_by_region = defaultdict(int)
    geodata_by_province = defaultdict(int)
    geodata_communities_by_province = defaultdict(int)
    geodata_by_municipality = defaultdict(int)
    geodata_communities_by_municipality = defaultdict(int)
    geodata_by_barangay = defaultdict(
        lambda: {
            "total": 0,
            "layers": 0,
            "visualizations": 0,
            "points": 0,
            "lat": None,
            "lng": None,
        }
    )

    coords_by_barangay: Dict[int, Tuple[float, float]] = {}
    coords_accumulator_by_municipality = defaultdict(lambda: {"lat": 0.0, "lng": 0.0, "count": 0})
    coords_accumulator_by_province = defaultdict(lambda: {"lat": 0.0, "lng": 0.0, "count": 0})
    coords_accumulator_by_region = defaultdict(lambda: {"lat": 0.0, "lng": 0.0, "count": 0})

    direct_layer_records = []

    try:
        from communities.models import GeographicDataLayer, OBCCommunity
    except ImportError:  # pragma: no cover - defensive fallback during migrations
        community_records = []
    else:
        community_records = (
            OBCCommunity.objects.filter(is_active=True)
            .annotate(
                geo_layers_count=Count("geographic_layers", distinct=True),
                map_visualizations_count=Count("community_map_visualizations", distinct=True),
                spatial_points_count=Count("spatial_points", distinct=True),
                communities_count=Count("id"),
                avg_latitude=Avg("latitude"),
                avg_longitude=Avg("longitude"),
            )
            .values(
                "barangay_id",
                "barangay__municipality_id",
                "barangay__municipality__province_id",
                "barangay__municipality__province__region_id",
                "geo_layers_count",
                "map_visualizations_count",
                "spatial_points_count",
                "communities_count",
                "avg_latitude",
                "avg_longitude",
            )
        )

        direct_layer_records = (
            GeographicDataLayer.objects.filter(community__isnull=True)
            .values(
                "id",
                "region_id",
                "province_id",
                "province__region_id",
                "municipality_id",
                "municipality__province_id",
                "municipality__province__region_id",
                "barangay_id",
                "barangay__municipality_id",
                "barangay__municipality__province_id",
                "barangay__municipality__province__region_id",
                "center_point",
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

        barangay_stats = geodata_by_barangay[barangay_id]
        barangay_stats["total"] += total_geodata
        barangay_stats["layers"] += int(record["geo_layers_count"])
        barangay_stats["visualizations"] += int(record["map_visualizations_count"])
        barangay_stats["points"] += int(record["spatial_points_count"])

        avg_lat = _normalise_float(record.get("avg_latitude"))
        avg_lng = _normalise_float(record.get("avg_longitude"))
        if avg_lat is not None and avg_lng is not None:
            barangay_stats["lat"] = avg_lat
            barangay_stats["lng"] = avg_lng
            coords_by_barangay.setdefault(barangay_id, (avg_lat, avg_lng))

            if municipality_id:
                acc = coords_accumulator_by_municipality[municipality_id]
                acc["lat"] += avg_lat
                acc["lng"] += avg_lng
                acc["count"] += 1

            if province_id:
                acc = coords_accumulator_by_province[province_id]
                acc["lat"] += avg_lat
                acc["lng"] += avg_lng
                acc["count"] += 1

            if region_id:
                acc = coords_accumulator_by_region[region_id]
                acc["lat"] += avg_lat
                acc["lng"] += avg_lng
                acc["count"] += 1

        geodata_by_municipality[municipality_id] += total_geodata
        geodata_communities_by_municipality[municipality_id] += 1

        geodata_by_province[province_id] += total_geodata
        geodata_communities_by_province[province_id] += 1

        geodata_by_region[region_id] += total_geodata
        geodata_communities_by_region[region_id] += 1

    for layer in direct_layer_records:
        barangay_id = layer["barangay_id"]
        municipality_id = layer["municipality_id"] or layer["barangay__municipality_id"]
        province_id = (
            layer["province_id"]
            or layer["municipality__province_id"]
            or layer["barangay__municipality__province_id"]
        )
        region_id = (
            layer["region_id"]
            or layer["province__region_id"]
            or layer["municipality__province__region_id"]
            or layer["barangay__municipality__province__region_id"]
        )

        center_lat, center_lng = _extract_lat_lng(layer.get("center_point"))

        if region_id:
            geodata_by_region[region_id] += 1
            if center_lat is not None and center_lng is not None:
                acc = coords_accumulator_by_region[region_id]
                acc["lat"] += center_lat
                acc["lng"] += center_lng
                acc["count"] += 1
        if province_id:
            geodata_by_province[province_id] += 1
            if center_lat is not None and center_lng is not None:
                acc = coords_accumulator_by_province[province_id]
                acc["lat"] += center_lat
                acc["lng"] += center_lng
                acc["count"] += 1
        if municipality_id:
            geodata_by_municipality[municipality_id] += 1
            if center_lat is not None and center_lng is not None:
                acc = coords_accumulator_by_municipality[municipality_id]
                acc["lat"] += center_lat
                acc["lng"] += center_lng
                acc["count"] += 1
        if barangay_id:
            barangay_stats = geodata_by_barangay[barangay_id]
            barangay_stats["total"] += 1
            barangay_stats["layers"] += 1
            if (
                center_lat is not None
                and center_lng is not None
                and barangay_stats["lat"] is None
                and barangay_stats["lng"] is None
            ):
                barangay_stats["lat"] = center_lat
                barangay_stats["lng"] = center_lng
                coords_by_barangay.setdefault(barangay_id, (center_lat, center_lng))

    def _finalise_accumulator(accumulator):
        results = {}
        for key, payload in accumulator.items():
            count = payload.get("count", 0)
            if not count:
                continue
            results[key] = (payload["lat"] / count, payload["lng"] / count)
        return results

    coords_by_municipality = _finalise_accumulator(coords_accumulator_by_municipality)
    coords_by_province = _finalise_accumulator(coords_accumulator_by_province)
    coords_by_region = _finalise_accumulator(coords_accumulator_by_region)

    municipalities_grouped_by_province: Dict[int, List[Municipality]] = defaultdict(list)
    for municipality in municipalities:
        municipalities_grouped_by_province[municipality.province_id].append(
            municipality
        )

    provinces_payload: List[dict] = []
    for province in provinces:
        province_code = getattr(province, "code", None)
        province_code_upper = (province_code or "").upper()
        province_name_lower = (province.name or "").lower()

        grouped_municipalities = municipalities_grouped_by_province.get(
            province.id, []
        )
        auto_municipality_id = None

        if grouped_municipalities:
            independent_city = next(
                (
                    municipality
                    for municipality in grouped_municipalities
                    if getattr(municipality, "municipality_type", "")
                    == "independent_city"
                ),
                None,
            )
            if independent_city is not None:
                auto_municipality_id = independent_city.id
            elif len(grouped_municipalities) == 1:
                single_municipality = grouped_municipalities[0]
                if getattr(single_municipality, "municipality_type", "") in {
                    "city",
                    "independent_city",
                }:
                    auto_municipality_id = single_municipality.id

        is_pseudo_province = bool(
            auto_municipality_id
            or province_code_upper.startswith("HUC_")
            or "CITY-" in province_code_upper
            or province_name_lower.startswith("city ")
            or province_name_lower.endswith(" (huc)")
        )

        provinces_payload.append(
            {
                "id": province.id,
                "name": province.name,
                "code": province_code,
                "is_pseudo_province": is_pseudo_province,
                "auto_municipality_id": auto_municipality_id,
                "region_id": province.region_id,
                **_apply_centroid_fallback(
                    _centroid_metadata(province),
                    coords_by_province.get(province.id),
                ),
                "population": province.population_total,
                "geodata_count": int(geodata_by_province.get(province.id, 0)),
                "geodata_communities": int(
                    geodata_communities_by_province.get(province.id, 0)
                ),
                "has_geodata": geodata_by_province.get(province.id, 0) > 0,
            }
        )

    municipalities_payload = [
        {
            "id": municipality.id,
            "name": municipality.name,
            "province_id": municipality.province_id,
            "population": municipality.population_total,
            "code": municipality.code,
            "municipality_type": getattr(
                municipality, "municipality_type", None
            ),
            **_apply_centroid_fallback(
                _centroid_metadata(municipality),
                coords_by_municipality.get(municipality.id),
            ),
            "geodata_count": int(geodata_by_municipality.get(municipality.id, 0)),
            "geodata_communities": int(
                geodata_communities_by_municipality.get(municipality.id, 0)
            ),
            "has_geodata": geodata_by_municipality.get(municipality.id, 0) > 0,
        }
        for municipality in municipalities
    ]

    data = {
        "regions": [
            {
                "id": region.id,
                "name": region.name,
                "code": region.code,
                **_apply_centroid_fallback(
                    _centroid_metadata(region),
                    coords_by_region.get(region.id),
                ),
                "geodata_count": int(geodata_by_region.get(region.id, 0)),
                "geodata_communities": int(
                    geodata_communities_by_region.get(region.id, 0)
                ),
                "has_geodata": geodata_by_region.get(region.id, 0) > 0,
            }
            for region in regions
        ],
        "provinces": provinces_payload,
        "municipalities": municipalities_payload,
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
                **_apply_centroid_fallback(
                    _centroid_metadata(barangay),
                    coords_by_barangay.get(barangay.id),
                ),
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
