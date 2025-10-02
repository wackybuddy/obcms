"""Utilities for preparing geographic layers for map rendering."""

from __future__ import annotations

from typing import Iterable, List, Tuple

DEFAULT_CENTER = [7.1907, 124.2197]
DEFAULT_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
DEFAULT_TILE_ATTRIBUTION = (
    '&copy; <a href="https://www.openstreetmap.org/copyright">'
    "OpenStreetMap</a> contributors"
)
DEFAULT_TILE_SUBDOMAINS = ["a", "b", "c"]


def build_map_config(layer_payloads: Iterable[dict]) -> dict:
    """Build aggregate map configuration from serialized layer payloads."""

    payload_list = list(layer_payloads)
    aggregated_bounds: List[float] | None = None
    centers: List[List[float]] = []

    for payload in payload_list:
        center = payload.get("center")
        if center and isinstance(center, (list, tuple)) and len(center) == 2:
            centers.append([center[1], center[0]])

        bounds = payload.get("bounds")
        if bounds and isinstance(bounds, (list, tuple)) and len(bounds) == 4:
            min_lng, min_lat, max_lng, max_lat = bounds
            if aggregated_bounds is None:
                aggregated_bounds = [min_lng, min_lat, max_lng, max_lat]
            else:
                aggregated_bounds[0] = min(aggregated_bounds[0], min_lng)
                aggregated_bounds[1] = min(aggregated_bounds[1], min_lat)
                aggregated_bounds[2] = max(aggregated_bounds[2], max_lng)
                aggregated_bounds[3] = max(aggregated_bounds[3], max_lat)

    config = {
        "tile_url": DEFAULT_TILE_URL,
        "tile_subdomains": DEFAULT_TILE_SUBDOMAINS,
        "tile_attribution": DEFAULT_TILE_ATTRIBUTION,
        "default_center": centers[0] if centers else DEFAULT_CENTER,
        "default_zoom": 7,
        "min_zoom": 4,
        "max_zoom": 18,
        "has_visible_layers": any(
            payload.get("is_visible", False) for payload in payload_list
        ),
        "offline": {
            "max_parallel_downloads": 6,
            "max_zoom": 16,
            "save_what_you_see": True,
        },
    }

    if aggregated_bounds:
        config["bounds"] = [
            [aggregated_bounds[1], aggregated_bounds[0]],
            [aggregated_bounds[3], aggregated_bounds[2]],
        ]
    else:
        config["bounds"] = None

    return config


def serialize_layers_for_map(layers: Iterable) -> Tuple[List[dict], dict]:
    """Helper that serializes layers and returns payload plus config."""

    payloads = [getattr(layer, "to_map_payload")() for layer in layers]
    config = build_map_config(payloads)
    return payloads, config
