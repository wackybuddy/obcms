"""
Reusable form mixins for common functionality across the OOBC system.

This module provides mixins that can be used to add consistent behavior
to forms throughout the system.
"""

from typing import Optional, Dict, Any
from django import forms
from django.core.exceptions import ValidationError

from ..models import Region, Province, Municipality, Barangay
from ..services.enhanced_geocoding import enhanced_ensure_location_coordinates
from ..services.locations import get_object_centroid


def _resolve_coordinates(*objects):
    """Return the first available (lat, lng) pair from the provided objects."""
    for obj in objects:
        if not obj:
            continue
        lat, lng = get_object_centroid(obj)
        if lat is None or lng is None:
            lat, lng, _, _ = enhanced_ensure_location_coordinates(obj)
        if lat is not None and lng is not None:
            return float(lat), float(lng)
    return None, None


def _is_blank(value) -> bool:
    """Return True when form field value should be treated as empty."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


class LocationSelectionMixin:
    """
    Mixin for forms that include location selection (region, province, municipality, barangay).

    Provides:
    - Automatic queryset management for hierarchical location selection
    - Coordinate auto-resolution from selected locations
    - Validation of location hierarchy consistency
    - Consistent styling and behavior across forms

    Usage:
        class MyForm(LocationSelectionMixin, forms.ModelForm):
            # Define location fields that should be handled
            location_fields_config = {
                'region': {'required': True, 'level': 'region'},
                'province': {'required': True, 'level': 'province'},
                'municipality': {'required': True, 'level': 'municipality'},
                'barangay': {'required': False, 'level': 'barangay'},
            }

            class Meta:
                model = MyModel
                fields = ['region', 'province', 'municipality', 'barangay', ...]
    """

    # Configuration for location fields - override in subclasses
    location_fields_config = {
        'region': {'required': True, 'level': 'region'},
        'province': {'required': True, 'level': 'province'},
        'municipality': {'required': True, 'level': 'municipality'},
        'barangay': {'required': False, 'level': 'barangay'},
    }

    # Default CSS classes for location fields
    location_field_css_classes = "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"

    def _resolve_model_instance(self, model, value):
        """Helper to resolve a model instance from various input types."""
        if not value:
            return None
        if isinstance(value, model):
            return value
        try:
            return model.objects.get(pk=value)
        except model.DoesNotExist:
            return None

    def _get_location_instance(self, field_name: str):
        """Get the current instance for a location field from various sources."""
        # Try to get from instance first (for editing existing records)
        if hasattr(self, 'instance') and self.instance and hasattr(self.instance, field_name):
            value = getattr(self.instance, field_name)
            if value:
                return value

        # Try to get from initial data
        if hasattr(self, 'initial') and self.initial.get(field_name):
            model_map = {
                'region': Region,
                'province': Province,
                'municipality': Municipality,
                'barangay': Barangay
            }
            model = model_map.get(field_name)
            if model:
                return self._resolve_model_instance(model, self.initial.get(field_name))

        # Try to get from bound data
        if hasattr(self, 'is_bound') and self.is_bound and hasattr(self, 'data'):
            model_map = {
                'region': Region,
                'province': Province,
                'municipality': Municipality,
                'barangay': Barangay
            }
            model = model_map.get(field_name)
            if model:
                return self._resolve_model_instance(model, self.data.get(field_name))

        return None

    def _setup_location_fields(self):
        """Setup location fields with proper querysets and styling."""

        # Get current selections for all location levels
        selected_region = self._get_location_instance('region')
        selected_province = self._get_location_instance('province')
        selected_municipality = self._get_location_instance('municipality')
        selected_barangay = self._get_location_instance('barangay')

        # Also try to derive selections from relationships
        if not selected_region and selected_province:
            selected_region = selected_province.region
        if not selected_province and selected_municipality:
            selected_province = selected_municipality.province
            if not selected_region:
                selected_region = selected_province.region
        if not selected_municipality and selected_barangay:
            selected_municipality = selected_barangay.municipality
            if not selected_province:
                selected_province = selected_municipality.province
            if not selected_region:
                selected_region = selected_province.region

        # Setup region field
        if 'region' in self.fields and 'region' in self.location_fields_config:
            region_field = self.fields['region']
            region_field.queryset = Region.objects.filter(is_active=True).order_by('code', 'name')
            region_field.empty_label = "Select region..."
            region_field.widget.attrs.update({'class': self.location_field_css_classes})

        # Setup province field
        if 'province' in self.fields and 'province' in self.location_fields_config:
            province_field = self.fields['province']
            province_field.empty_label = "Select province..."
            province_field.widget.attrs.update({'class': self.location_field_css_classes})

            if selected_region:
                province_field.queryset = Province.objects.filter(
                    region=selected_region, is_active=True
                ).order_by('name')
            else:
                province_field.queryset = Province.objects.none()

        # Setup municipality field
        if 'municipality' in self.fields and 'municipality' in self.location_fields_config:
            municipality_field = self.fields['municipality']
            municipality_field.empty_label = "Select municipality/city..."
            municipality_field.widget.attrs.update({'class': self.location_field_css_classes})

            municipality_queryset = Municipality.objects.filter(is_active=True).select_related(
                'province__region'
            ).order_by('province__region__name', 'province__name', 'name')

            if selected_province:
                municipality_queryset = municipality_queryset.filter(province=selected_province)
            elif selected_region:
                municipality_queryset = municipality_queryset.filter(province__region=selected_region)
            else:
                municipality_queryset = Municipality.objects.none()

            municipality_field.queryset = municipality_queryset

        # Setup barangay field
        if 'barangay' in self.fields and 'barangay' in self.location_fields_config:
            barangay_field = self.fields['barangay']
            barangay_field.empty_label = "Select barangay..."
            barangay_field.widget.attrs.update({'class': self.location_field_css_classes})

            barangay_queryset = Barangay.objects.filter(is_active=True).select_related(
                'municipality__province__region'
            ).order_by('name')

            if selected_municipality:
                barangay_queryset = barangay_queryset.filter(municipality=selected_municipality)
            elif selected_province:
                barangay_queryset = barangay_queryset.filter(municipality__province=selected_province)
            elif selected_region:
                barangay_queryset = barangay_queryset.filter(municipality__province__region=selected_region)
            else:
                barangay_queryset = Barangay.objects.none()

            barangay_field.queryset = barangay_queryset

        # Set initial values if not bound
        if not getattr(self, 'is_bound', False):
            if 'region' in self.fields and selected_region:
                self.fields['region'].initial = selected_region
            if 'province' in self.fields and selected_province:
                self.fields['province'].initial = selected_province
            if 'municipality' in self.fields and selected_municipality:
                self.fields['municipality'].initial = selected_municipality
            if 'barangay' in self.fields and selected_barangay:
                self.fields['barangay'].initial = selected_barangay

    def __init__(self, *args, **kwargs):
        """Initialize the form with location selection setup."""
        super().__init__(*args, **kwargs)
        self._setup_location_fields()

    def clean(self):
        """Validate location hierarchy and auto-resolve coordinates."""
        cleaned_data = super().clean()

        # Validate location hierarchy consistency
        region = cleaned_data.get('region')
        province = cleaned_data.get('province')
        municipality = cleaned_data.get('municipality')
        barangay = cleaned_data.get('barangay')

        # Check region-province consistency
        if province and region and province.region_id != region.id:
            self.add_error('province', 'Selected province does not belong to the chosen region.')

        # Check province-municipality consistency
        if municipality and province and municipality.province_id != province.id:
            self.add_error('municipality', 'Selected municipality/city does not belong to the chosen province.')

        # Check municipality-barangay consistency
        if barangay and municipality and barangay.municipality_id != municipality.id:
            self.add_error('barangay', 'Selected barangay does not belong to the chosen municipality/city.')

        # Auto-resolve coordinates if latitude/longitude fields exist and are empty
        if 'latitude' in cleaned_data and 'longitude' in cleaned_data:
            lat = cleaned_data.get('latitude')
            lng = cleaned_data.get('longitude')

            if _is_blank(lat) or _is_blank(lng):
                # Try to resolve from most specific to least specific location
                resolved_lat, resolved_lng = _resolve_coordinates(
                    barangay, municipality, province, region
                )
                if resolved_lat is not None and resolved_lng is not None:
                    cleaned_data['latitude'] = resolved_lat
                    cleaned_data['longitude'] = resolved_lng

        return cleaned_data


class LocationDataMixin:
    """
    Mixin for views that need to provide location data to templates.

    Provides consistent location data structure and context variables
    for forms that use location selection.
    """

    def get_location_context_data(self, **kwargs):
        """Add location data to template context."""
        from ..services.locations import build_location_data

        context = kwargs
        context['location_data'] = build_location_data(include_barangays=True)
        return context

    def get_context_data(self, **kwargs):
        """Override to include location data in context."""
        context = super().get_context_data(**kwargs) if hasattr(super(), 'get_context_data') else kwargs
        return self.get_location_context_data(**context)


__all__ = [
    'LocationSelectionMixin',
    'LocationDataMixin',
]