"""Utilities for geocoding administrative locations when centroid data is missing."""

from __future__ import annotations

import logging
from typing import Optional, Tuple

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

NOMINATIM_URL = getattr(
    settings,
    "GEOCODING_NOMINATIM_URL",
    "https://nominatim.openstreetmap.org/search",
)
USER_AGENT = getattr(
    settings, "GEOCODING_USER_AGENT", "OBCMS/1.0 (+https://obcms.local)"
)
TIMEOUT_SECONDS = getattr(settings, "GEOCODING_TIMEOUT", 10)


def _to_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return None


def _format_query(obj) -> Optional[str]:
    from common.models import Barangay, Municipality, Province, Region

    if isinstance(obj, Barangay):
        parts = [
            f"Barangay {obj.name}",
            obj.municipality.name if obj.municipality_id else "",
            obj.municipality.province.name if obj.municipality_id else "",
        ]
    elif isinstance(obj, Municipality):
        parts = [
            obj.name,
            obj.province.name if obj.province_id else "",
        ]
    elif isinstance(obj, Province):
        parts = [obj.name]
    elif isinstance(obj, Region):
        parts = [f"Region {obj.code}", obj.name]
    else:
        return None

    parts.append("Philippines")
    return ", ".join(part for part in parts if part)


def _request_geocode(
    query: str,
) -> Tuple[Optional[float], Optional[float], Optional[list]]:
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(
            NOMINATIM_URL, params=params, headers=headers, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network errors
        logger.warning("Geocoding failed for query '%s': %s", query, exc)
        return None, None, None

    payload = response.json()
    if not payload:
        return None, None, None

    item = payload[0]
    lat = _to_float(item.get("lat"))
    lng = _to_float(item.get("lon"))
    bounding_box = item.get("boundingbox")

    if bounding_box and len(bounding_box) == 4:
        south = _to_float(bounding_box[0])
        north = _to_float(bounding_box[1])
        west = _to_float(bounding_box[2])
        east = _to_float(bounding_box[3])
        if None not in {south, north, west, east}:
            bbox = [west, south, east, north]
        else:
            bbox = None
    else:
        bbox = None

    return lat, lng, bbox


def ensure_location_coordinates(obj) -> Tuple[Optional[float], Optional[float], bool]:
    """Ensure the given location-aware object has centroid coordinates.

    Returns (lat, lng, updated) where ``updated`` indicates whether a geocode
    lookup was performed and saved.
    """

    from common.services.locations import get_object_centroid

    lat, lng = get_object_centroid(obj)
    if lat is not None and lng is not None:
        return lat, lng, False

    query = _format_query(obj)
    if not query:
        return None, None, False

    lat, lng, bbox = _request_geocode(query)
    if lat is None or lng is None:
        return None, None, False

    update_fields = []
    if hasattr(obj, "center_coordinates"):
        obj.center_coordinates = [lng, lat]
        update_fields.append("center_coordinates")
    if bbox and hasattr(obj, "bounding_box"):
        obj.bounding_box = bbox
        update_fields.append("bounding_box")

    if update_fields:
        obj.save(update_fields=update_fields)

    return lat, lng, True
