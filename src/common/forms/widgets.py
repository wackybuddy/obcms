"""
Custom form widgets for the OOBC system.

This module provides specialized widgets for handling location selection,
coordinates, and other OOBC-specific form inputs.
"""

import json
from typing import Dict, Any, Optional
from django import forms
from django.forms.utils import flatatt
from django.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from ..models import Region, Province, Municipality, Barangay
from ..services.locations import build_location_data


class LocationHierarchyWidget(forms.MultiWidget):
    """
    A widget that handles the complete location hierarchy: region → province → municipality → barangay.

    Provides:
    - Cascading dropdown selection
    - Automatic coordinate resolution
    - Integrated map display
    - Consistent styling and behavior

    Usage:
        class MyForm(forms.Form):
            location = forms.MultiValueField(
                fields=[
                    forms.ModelChoiceField(queryset=Region.objects.all()),
                    forms.ModelChoiceField(queryset=Province.objects.all()),
                    forms.ModelChoiceField(queryset=Municipality.objects.all()),
                    forms.ModelChoiceField(queryset=Barangay.objects.all(), required=False),
                ],
                widget=LocationHierarchyWidget(
                    include_barangay=True,
                    include_coordinates=True,
                    include_map=True
                )
            )
    """

    template_name = "components/location_hierarchy_widget.html"

    def __init__(
        self,
        include_barangay=True,
        include_coordinates=True,
        include_map=True,
        attrs=None,
    ):
        self.include_barangay = include_barangay
        self.include_coordinates = include_coordinates
        self.include_map = include_map

        # Define the child widgets based on configuration
        widgets = [
            forms.Select(attrs={"class": "location-select region-select"}),  # Region
            forms.Select(
                attrs={"class": "location-select province-select"}
            ),  # Province
            forms.Select(
                attrs={"class": "location-select municipality-select"}
            ),  # Municipality
        ]

        if include_barangay:
            widgets.append(
                forms.Select(attrs={"class": "location-select barangay-select"})
            )

        if include_coordinates:
            widgets.extend(
                [
                    forms.NumberInput(
                        attrs={
                            "class": "coordinate-input latitude-input",
                            "step": "any",
                        }
                    ),  # Latitude
                    forms.NumberInput(
                        attrs={
                            "class": "coordinate-input longitude-input",
                            "step": "any",
                        }
                    ),  # Longitude
                ]
            )

        super().__init__(widgets, attrs)

    def decompress(self, value):
        """Decompress a location value into component parts."""
        if not value:
            return [None] * len(self.widgets)

        result = [None] * len(self.widgets)

        # Handle different input types
        if isinstance(value, dict):
            result[0] = value.get("region")
            result[1] = value.get("province")
            result[2] = value.get("municipality")
            if self.include_barangay:
                result[3] = value.get("barangay")
                if self.include_coordinates:
                    result[4] = value.get("latitude")
                    result[5] = value.get("longitude")
            elif self.include_coordinates:
                result[3] = value.get("latitude")
                result[4] = value.get("longitude")

        elif isinstance(value, (list, tuple)):
            for i, val in enumerate(value):
                if i < len(result):
                    result[i] = val

        return result

    def format_output(self, rendered_widgets):
        """Format the widget output using a template."""
        return format_html(
            '<div class="location-hierarchy-widget" data-widget-config="{config}">'
            '<div class="location-selects">'
            '<div class="location-field region-field">'
            '<label class="location-label">Region</label>'
            "{region}"
            "</div>"
            '<div class="location-field province-field">'
            '<label class="location-label">Province</label>'
            "{province}"
            "</div>"
            '<div class="location-field municipality-field">'
            '<label class="location-label">Municipality/City</label>'
            "{municipality}"
            "</div>"
            "{barangay_field}"
            "</div>"
            "{coordinate_fields}"
            "{map_widget}"
            "</div>",
            config=json.dumps(
                {
                    "include_barangay": self.include_barangay,
                    "include_coordinates": self.include_coordinates,
                    "include_map": self.include_map,
                    "centroid_url": reverse("common:location_centroid"),
                }
            ),
            region=rendered_widgets[0],
            province=rendered_widgets[1],
            municipality=rendered_widgets[2],
            barangay_field=(
                format_html(
                    '<div class="location-field barangay-field">'
                    '<label class="location-label">Barangay</label>'
                    "{}</div>",
                    rendered_widgets[3],
                )
                if self.include_barangay
                else ""
            ),
            coordinate_fields=(
                self._render_coordinate_fields(rendered_widgets)
                if self.include_coordinates
                else ""
            ),
            map_widget=self._render_map_widget() if self.include_map else "",
        )

    def _render_coordinate_fields(self, rendered_widgets):
        """Render the coordinate input fields."""
        lat_index = 4 if self.include_barangay else 3
        lng_index = lat_index + 1

        return format_html(
            '<div class="coordinate-fields">'
            '<div class="coordinate-field latitude-field">'
            '<label class="coordinate-label">Latitude</label>'
            "{latitude}"
            '<small class="coordinate-help">Decimal degrees (e.g., 7.0858)</small>'
            "</div>"
            '<div class="coordinate-field longitude-field">'
            '<label class="coordinate-label">Longitude</label>'
            "{longitude}"
            '<small class="coordinate-help">Decimal degrees (e.g., 125.6161)</small>'
            "</div>"
            "</div>",
            latitude=(
                rendered_widgets[lat_index] if lat_index < len(rendered_widgets) else ""
            ),
            longitude=(
                rendered_widgets[lng_index] if lng_index < len(rendered_widgets) else ""
            ),
        )

    def _render_map_widget(self):
        """Render the interactive map widget."""
        return format_html(
            '<div class="map-widget">'
            '<div class="obc-map-container" data-obc-map data-mode="form">'
            '<div class="obc-map-header">'
            '<h4 class="map-title">Location Map</h4>'
            '<span class="obc-map-status">Select location to pin coordinates</span>'
            "</div>"
            '<div class="obc-map-canvas" data-obc-map-target></div>'
            '<div class="obc-map-footer">'
            '<small class="map-help">Click map to manually set coordinates</small>'
            "</div>"
            "</div>"
            "</div>"
        )

    def get_context(self, name, value, attrs):
        """Get template context for widget rendering."""
        context = super().get_context(name, value, attrs)
        context["widget"].update(
            {
                "include_barangay": self.include_barangay,
                "include_coordinates": self.include_coordinates,
                "include_map": self.include_map,
                "location_data": build_location_data(
                    include_barangays=self.include_barangay
                ),
                "centroid_url": reverse("common:location_centroid"),
            }
        )
        return context

    class Media:
        css = {
            "all": (
                "common/css/obc_location_map.css",
                "common/css/location_hierarchy_widget.css",
            )
        }
        js = ("common/js/obc_location_map.js", "common/js/location_hierarchy_widget.js")


class CoordinateWidget(forms.MultiWidget):
    """
    A widget for latitude/longitude coordinate input with map integration.

    Provides:
    - Separate latitude and longitude inputs
    - Input validation and formatting
    - Optional map integration for coordinate selection
    - Coordinate accuracy indicators
    """

    def __init__(self, include_map=True, attrs=None):
        self.include_map = include_map

        widgets = [
            forms.NumberInput(
                attrs={
                    "class": "coordinate-input latitude-input",
                    "step": "any",
                    "placeholder": "Latitude (e.g., 7.0858)",
                }
            ),
            forms.NumberInput(
                attrs={
                    "class": "coordinate-input longitude-input",
                    "step": "any",
                    "placeholder": "Longitude (e.g., 125.6161)",
                }
            ),
        ]

        super().__init__(widgets, attrs)

    def decompress(self, value):
        """Decompress coordinate value into lat/lng components."""
        if not value:
            return [None, None]

        if isinstance(value, dict):
            return [value.get("lat"), value.get("lng")]
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            return [value[0], value[1]]
        elif hasattr(value, "latitude") and hasattr(value, "longitude"):
            return [value.latitude, value.longitude]

        return [None, None]

    def format_output(self, rendered_widgets):
        """Format the coordinate widget output."""
        return format_html(
            '<div class="coordinate-widget" data-coordinate-widget>'
            '<div class="coordinate-inputs">'
            '<div class="coordinate-field latitude-field">'
            '<label class="coordinate-label">Latitude</label>'
            "{latitude}"
            '<small class="coordinate-help">Decimal degrees</small>'
            "</div>"
            '<div class="coordinate-field longitude-field">'
            '<label class="coordinate-label">Longitude</label>'
            "{longitude}"
            '<small class="coordinate-help">Decimal degrees</small>'
            "</div>"
            "</div>"
            "{map_widget}"
            "</div>",
            latitude=rendered_widgets[0],
            longitude=rendered_widgets[1],
            map_widget=self._render_coordinate_map() if self.include_map else "",
        )

    def _render_coordinate_map(self):
        """Render the coordinate selection map."""
        return format_html(
            '<div class="coordinate-map">'
            '<div class="obc-map-container" data-obc-map data-mode="coordinate">'
            '<div class="obc-map-canvas" data-obc-map-target></div>'
            '<div class="coordinate-map-help">'
            "<small>Click map to set coordinates</small>"
            "</div>"
            "</div>"
            "</div>"
        )

    class Media:
        css = {"all": ("common/css/obc_location_map.css",)}
        js = ("common/js/obc_location_map.js",)


class LocationSelectWidget(forms.Select):
    """
    Enhanced select widget for location fields with additional metadata.

    Provides:
    - Location-specific styling
    - Population and coordinate metadata
    - Geocoding status indicators
    """

    def __init__(self, location_level="municipality", show_metadata=True, attrs=None):
        self.location_level = location_level
        self.show_metadata = show_metadata

        default_attrs = {
            "class": f"location-select {location_level}-select",
            "data-location-level": location_level,
        }

        if attrs:
            default_attrs.update(attrs)

        super().__init__(attrs=default_attrs)

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        """Create option with additional metadata."""
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )

        if self.show_metadata and value:
            # Add metadata attributes to option
            try:
                if self.location_level == "region":
                    obj = Region.objects.get(pk=value)
                elif self.location_level == "province":
                    obj = Province.objects.get(pk=value)
                elif self.location_level == "municipality":
                    obj = Municipality.objects.get(pk=value)
                elif self.location_level == "barangay":
                    obj = Barangay.objects.get(pk=value)
                else:
                    obj = None

                if obj:
                    option["attrs"].update(
                        {
                            "data-population": getattr(obj, "population_total", ""),
                            "data-has-coordinates": (
                                "true"
                                if getattr(obj, "center_coordinates", None)
                                else "false"
                            ),
                            "data-code": getattr(obj, "code", ""),
                        }
                    )

            except (
                Region.DoesNotExist,
                Province.DoesNotExist,
                Municipality.DoesNotExist,
                Barangay.DoesNotExist,
            ):
                pass

        return option

    class Media:
        css = {"all": ("common/css/location_select_widget.css",)}
        js = ("common/js/location_select_widget.js",)


__all__ = [
    "LocationHierarchyWidget",
    "CoordinateWidget",
    "LocationSelectWidget",
]
