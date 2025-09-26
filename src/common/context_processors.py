"""Common template context helpers."""

from django.urls import NoReverseMatch, reverse


def location_api(request):
    """Expose the location-data API endpoint to templates."""

    try:
        api_url = reverse("common_api:location-data")
    except NoReverseMatch:
        api_url = ""
    return {
        "LOCATION_DATA_API_URL": api_url,
    }
