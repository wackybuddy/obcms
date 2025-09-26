"""Enhanced geocoding service with Google Maps API + Nominatim fallback for maximum accuracy."""

from __future__ import annotations

import logging
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Configuration with fallbacks
GOOGLE_API_KEY = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
ARCGIS_GEOCODING_URL = (
    "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
)
NOMINATIM_URL = getattr(
    settings, "GEOCODING_NOMINATIM_URL", "https://nominatim.openstreetmap.org/search"
)
USER_AGENT = getattr(settings, "GEOCODING_USER_AGENT", "OOBC-OBCMS/2.0 (+https://oobc.gov.ph)")
TIMEOUT_SECONDS = getattr(settings, "GEOCODING_TIMEOUT", 15)
CACHE_DURATION = 86400 * 7  # Cache geocoding results for 7 days

# Rate limiting
GOOGLE_RATE_LIMIT_DELAY = 0.1  # 100ms delay between Google requests
ARCGIS_RATE_LIMIT_DELAY = getattr(settings, "GEOCODING_ARCGIS_DELAY", 0.2)
NOMINATIM_RATE_LIMIT_DELAY = 1.0  # 1 second delay between Nominatim requests


@dataclass
class GeocodeResult:
    """Structured geocoding result."""
    latitude: Optional[float]
    longitude: Optional[float]
    accuracy: str  # 'high', 'medium', 'low'
    source: str  # 'google', 'nominatim', 'cache'
    formatted_address: Optional[str] = None
    confidence: Optional[float] = None
    bounding_box: Optional[list] = None


def _to_float(value: Any) -> Optional[float]:
    """Convert value to float safely."""
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError, OverflowError):
        return None


def _format_query_for_google(obj) -> Optional[str]:
    """Format query optimized for Google Maps Geocoding API."""
    from common.models import Barangay, Municipality, Province, Region

    if isinstance(obj, Barangay):
        # Google works better with "Barangay Name, Municipality, Province, Philippines"
        parts = [
            f"Barangay {obj.name}",
            obj.municipality.name if obj.municipality_id else "",
            obj.municipality.province.name if obj.municipality_id else "",
        ]
    elif isinstance(obj, Municipality):
        # For municipalities: "Municipality/City Name, Province, Philippines"
        type_prefix = obj.get_municipality_type_display() if hasattr(obj, 'get_municipality_type_display') else ""
        if type_prefix and type_prefix != "Municipality":
            name_part = f"{type_prefix} of {obj.name}"
        else:
            name_part = obj.name

        parts = [
            name_part,
            obj.province.name if obj.province_id else "",
        ]
    elif isinstance(obj, Province):
        parts = [obj.name, "Province"]
    elif isinstance(obj, Region):
        parts = [f"Region {obj.code}", obj.name]
    else:
        return None

    parts.append("Philippines")
    return ", ".join(part for part in parts if part)


def _format_query_for_nominatim(obj) -> Optional[str]:
    """Format query optimized for Nominatim/OpenStreetMap."""
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


def _geocode_with_google(query: str) -> GeocodeResult:
    """Geocode using Google Maps Geocoding API."""
    if not GOOGLE_API_KEY:
        logger.debug("Google Maps API key not configured, skipping Google geocoding")
        return GeocodeResult(None, None, 'low', 'google')

    cache_key = f"geocode_google_{hash(query)}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return GeocodeResult(
            cached_result['lat'], cached_result['lng'],
            cached_result['accuracy'], 'cache',
            cached_result.get('formatted_address'),
            cached_result.get('confidence'),
            cached_result.get('bounding_box')
        )

    params = {
        'address': query,
        'key': GOOGLE_API_KEY,
        'components': 'country:PH',  # Restrict to Philippines
        'region': 'ph'  # Bias results to Philippines
    }

    headers = {'User-Agent': USER_AGENT}

    try:
        time.sleep(GOOGLE_RATE_LIMIT_DELAY)  # Rate limiting

        response = requests.get(
            GOOGLE_GEOCODING_URL,
            params=params,
            headers=headers,
            timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()

        data = response.json()

        if data['status'] != 'OK' or not data.get('results'):
            logger.warning(f"Google geocoding failed for '{query}': {data.get('status', 'Unknown error')}")
            return GeocodeResult(None, None, 'low', 'google')

        result = data['results'][0]
        location = result['geometry']['location']

        lat = _to_float(location['lat'])
        lng = _to_float(location['lng'])

        # Determine accuracy based on geometry location_type
        location_type = result['geometry'].get('location_type', 'APPROXIMATE')
        if location_type in ['ROOFTOP', 'RANGE_INTERPOLATED']:
            accuracy = 'high'
        elif location_type == 'GEOMETRIC_CENTER':
            accuracy = 'medium'
        else:
            accuracy = 'medium'  # Google is generally quite accurate

        # Extract additional information
        formatted_address = result.get('formatted_address')

        # Calculate bounding box if viewport is available
        bounding_box = None
        if 'viewport' in result['geometry']:
            viewport = result['geometry']['viewport']
            bounding_box = [
                viewport['southwest']['lng'],  # west
                viewport['southwest']['lat'],  # south
                viewport['northeast']['lng'],  # east
                viewport['northeast']['lat'],  # north
            ]

        geocode_result = GeocodeResult(
            lat, lng, accuracy, 'google',
            formatted_address, None, bounding_box
        )

        # Cache the result
        cache.set(cache_key, {
            'lat': lat, 'lng': lng, 'accuracy': accuracy,
            'formatted_address': formatted_address,
            'bounding_box': bounding_box
        }, CACHE_DURATION)

        logger.info(f"Google geocoded '{query}' -> ({lat}, {lng}) with {accuracy} accuracy")
        return geocode_result

    except requests.RequestException as e:
        logger.warning(f"Google geocoding network error for '{query}': {e}")
        return GeocodeResult(None, None, 'low', 'google')
    except Exception as e:
        logger.error(f"Google geocoding unexpected error for '{query}': {e}")
        return GeocodeResult(None, None, 'low', 'google')


def _geocode_with_arcgis(query: str) -> GeocodeResult:
    """Geocode using Esri's ArcGIS World Geocoding service."""

    cache_key = f"geocode_arcgis_{hash(query)}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return GeocodeResult(
            cached_result['lat'],
            cached_result['lng'],
            cached_result['accuracy'],
            'cache',
            cached_result.get('formatted_address'),
            cached_result.get('confidence'),
            cached_result.get('bounding_box'),
        )

    params = {
        'f': 'pjson',
        'SingleLine': query,
        'maxLocations': 5,
        'outFields': 'Match_addr,Addr_type',
        'forStorage': 'false',
        'countryCode': 'PHL',
    }

    headers = {'User-Agent': USER_AGENT}

    try:
        time.sleep(max(0.0, ARCGIS_RATE_LIMIT_DELAY))

        response = requests.get(
            ARCGIS_GEOCODING_URL,
            params=params,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        payload = response.json()
        candidates = payload.get('candidates') or []
        if not candidates:
            logger.info("ArcGIS returned no candidates for '%s'", query)
            return GeocodeResult(None, None, 'low', 'arcgis')

        best_candidate = max(candidates, key=lambda cand: cand.get('score', 0) or 0)
        location = best_candidate.get('location') or {}
        lat = _to_float(location.get('y'))
        lng = _to_float(location.get('x'))

        if lat is None or lng is None:
            return GeocodeResult(None, None, 'low', 'arcgis')

        score = _to_float(best_candidate.get('score')) or 0.0
        if score >= 95:
            accuracy = 'high'
        elif score >= 80:
            accuracy = 'medium'
        else:
            accuracy = 'low'

        extent = best_candidate.get('extent') or {}
        xmin = _to_float(extent.get('xmin'))
        ymin = _to_float(extent.get('ymin'))
        xmax = _to_float(extent.get('xmax'))
        ymax = _to_float(extent.get('ymax'))
        bounding_box = None
        if None not in {xmin, ymin, xmax, ymax}:
            bounding_box = [xmin, ymin, xmax, ymax]

        formatted_address = best_candidate.get('address')

        geocode_result = GeocodeResult(
            lat,
            lng,
            accuracy,
            'arcgis',
            formatted_address,
            score,
            bounding_box,
        )

        cache.set(
            cache_key,
            {
                'lat': lat,
                'lng': lng,
                'accuracy': accuracy,
                'formatted_address': formatted_address,
                'confidence': score,
                'bounding_box': bounding_box,
            },
            CACHE_DURATION,
        )

        logger.info(
            "ArcGIS geocoded '%s' -> (%s, %s) with %s accuracy (score %.2f)",
            query,
            lat,
            lng,
            accuracy,
            score,
        )
        return geocode_result

    except requests.RequestException as exc:
        logger.warning("ArcGIS geocoding network error for '%s': %s", query, exc)
        return GeocodeResult(None, None, 'low', 'arcgis')
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("ArcGIS geocoding unexpected error for '%s': %s", query, exc)
        return GeocodeResult(None, None, 'low', 'arcgis')


def _geocode_with_nominatim(query: str) -> GeocodeResult:
    """Geocode using Nominatim/OpenStreetMap as fallback."""
    cache_key = f"geocode_nominatim_{hash(query)}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return GeocodeResult(
            cached_result['lat'], cached_result['lng'],
            cached_result['accuracy'], 'cache',
            cached_result.get('formatted_address'),
            cached_result.get('confidence'),
            cached_result.get('bounding_box')
        )

    params = {
        'q': query,
        'format': 'jsonv2',
        'limit': 1,
        'countrycodes': 'ph',  # Philippines only
        'addressdetails': 1
    }

    headers = {'User-Agent': USER_AGENT}

    try:
        time.sleep(NOMINATIM_RATE_LIMIT_DELAY)  # Rate limiting

        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=headers,
            timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()

        data = response.json()
        if not data:
            logger.info(f"Nominatim found no results for '{query}'")
            return GeocodeResult(None, None, 'low', 'nominatim')

        result = data[0]
        lat = _to_float(result.get('lat'))
        lng = _to_float(result.get('lon'))

        # Nominatim accuracy is generally medium for Philippines
        accuracy = 'medium'

        # Extract additional information
        formatted_address = result.get('display_name')
        confidence = _to_float(result.get('importance', 0.5))

        # Extract bounding box
        bounding_box = None
        bbox_data = result.get('boundingbox')
        if bbox_data and len(bbox_data) == 4:
            south = _to_float(bbox_data[0])
            north = _to_float(bbox_data[1])
            west = _to_float(bbox_data[2])
            east = _to_float(bbox_data[3])
            if all(val is not None for val in [south, north, west, east]):
                bounding_box = [west, south, east, north]

        geocode_result = GeocodeResult(
            lat, lng, accuracy, 'nominatim',
            formatted_address, confidence, bounding_box
        )

        # Cache the result
        cache.set(cache_key, {
            'lat': lat, 'lng': lng, 'accuracy': accuracy,
            'formatted_address': formatted_address,
            'confidence': confidence,
            'bounding_box': bounding_box
        }, CACHE_DURATION)

        logger.info(f"Nominatim geocoded '{query}' -> ({lat}, {lng}) with {accuracy} accuracy")
        return geocode_result

    except requests.RequestException as e:
        logger.warning(f"Nominatim geocoding network error for '{query}': {e}")
        return GeocodeResult(None, None, 'low', 'nominatim')
    except Exception as e:
        logger.error(f"Nominatim geocoding unexpected error for '{query}': {e}")
        return GeocodeResult(None, None, 'low', 'nominatim')


def enhanced_geocode_location(obj) -> GeocodeResult:
    """
    Enhanced geocoding with multiple providers and intelligent fallbacks.

    Order of preference:
    1. Google Maps Geocoding API (highest accuracy, requires API key)
    2. ArcGIS World Geocoding service (excellent coverage for PH)
    3. Nominatim/OpenStreetMap (community data, good fallback)
    """

    google_query = _format_query_for_google(obj)
    if google_query and GOOGLE_API_KEY:
        google_result = _geocode_with_google(google_query)
        if google_result.latitude is not None and google_result.longitude is not None:
            return google_result

    arcgis_query = google_query or _format_query_for_nominatim(obj)
    if arcgis_query:
        arcgis_result = _geocode_with_arcgis(arcgis_query)
        if arcgis_result.latitude is not None and arcgis_result.longitude is not None:
            return arcgis_result

    nominatim_query = _format_query_for_nominatim(obj)
    if nominatim_query:
        return _geocode_with_nominatim(nominatim_query)

    logger.warning("Could not form valid geocoding query for object: %s", obj)
    return GeocodeResult(None, None, 'low', 'error')


def enhanced_ensure_location_coordinates(obj) -> Tuple[Optional[float], Optional[float], bool, str]:
    """
    Enhanced version of ensure_location_coordinates with Google Maps integration.

    Returns (lat, lng, updated, source) where:
    - lat, lng: Coordinates or None if not found
    - updated: Whether the object was updated with new coordinates
    - source: 'cached', 'google', 'arcgis', 'nominatim', or 'unavailable'
    """
    from common.services.locations import get_object_centroid

    # First check if we already have coordinates
    lat, lng = get_object_centroid(obj)
    if lat is not None and lng is not None:
        return lat, lng, False, 'cached'

    # Use enhanced geocoding
    result = enhanced_geocode_location(obj)

    if result.latitude is None or result.longitude is None:
        return None, None, False, 'unavailable'

    # Update the object with the new coordinates
    update_fields = []

    if hasattr(obj, "center_coordinates"):
        obj.center_coordinates = [result.longitude, result.latitude]  # GeoJSON format
        update_fields.append("center_coordinates")

    if result.bounding_box and hasattr(obj, "bounding_box"):
        obj.bounding_box = result.bounding_box
        update_fields.append("bounding_box")

    if update_fields:
        try:
            obj.save(update_fields=update_fields)
            logger.info(f"Updated {obj.__class__.__name__} {obj.pk} coordinates from {result.source}")
        except Exception as e:
            logger.error(f"Failed to save coordinates for {obj}: {e}")
            return result.latitude, result.longitude, False, result.source

    return result.latitude, result.longitude, True, result.source
