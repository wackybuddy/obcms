from django import forms
from django.contrib.auth import get_user_model

from .models import GeographicDataLayer, MapVisualization, OBCCommunity

User = get_user_model()


class GeographicDataLayerForm(forms.ModelForm):
    """Form for creating and editing Geographic Data Layers."""

    class Meta:
        model = GeographicDataLayer
        fields = [
            "name",
            "description",
            "layer_type",
            "data_source",
            "geojson_data",
            "community",
            "region",
            "province",
            "municipality",
            "barangay",
            "bounding_box",
            "center_point",
            "style_properties",
            "zoom_level_min",
            "zoom_level_max",
            "is_visible",
            "opacity",
            "data_collection_date",
            "accuracy_meters",
            "coordinate_system",
            "attribution",
            "license_info",
            "is_public",
            "access_groups",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "placeholder": "Enter layer name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "rows": 4,
                    "placeholder": "Describe the purpose and content of this data layer",
                }
            ),
            "layer_type": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500"
                }
            ),
            "data_source": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500"
                }
            ),
            "geojson_data": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500 font-mono text-sm",
                    "rows": 8,
                    "placeholder": "Enter valid GeoJSON data here",
                }
            ),
            "community": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500"
                }
            ),
            "region": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500"
                }
            ),
            "province": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500"
                }
            ),
            "municipality": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500"
                }
            ),
            "barangay": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500"
                }
            ),
            "bounding_box": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500 font-mono text-sm",
                    "rows": 2,
                    "placeholder": "[min_lng, min_lat, max_lng, max_lat]",
                }
            ),
            "center_point": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500 font-mono text-sm",
                    "rows": 2,
                    "placeholder": "[longitude, latitude]",
                }
            ),
            "style_properties": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500 font-mono text-sm",
                    "rows": 4,
                    "placeholder": "JSON styling properties (colors, symbols, etc.)",
                }
            ),
            "zoom_level_min": forms.NumberInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "min": 1,
                    "max": 18,
                }
            ),
            "zoom_level_max": forms.NumberInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "min": 1,
                    "max": 18,
                }
            ),
            "is_visible": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-purple-600 shadow-sm focus:border-purple-300 focus:ring focus:ring-purple-200 focus:ring-opacity-50"
                }
            ),
            "opacity": forms.NumberInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                }
            ),
            "data_collection_date": forms.DateInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "type": "date",
                }
            ),
            "accuracy_meters": forms.NumberInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "step": 0.1,
                }
            ),
            "coordinate_system": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "placeholder": "e.g., EPSG:4326",
                }
            ),
            "attribution": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "rows": 3,
                    "placeholder": "Data attribution and source credits",
                }
            ),
            "license_info": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500",
                    "placeholder": "License information",
                }
            ),
            "is_public": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-purple-600 shadow-sm focus:border-purple-300 focus:ring focus:ring-purple-200 focus:ring-opacity-50"
                }
            ),
            "access_groups": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-purple-500 focus:border-purple-500 font-mono text-sm",
                    "rows": 3,
                    "placeholder": "JSON array of user groups that have access",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Make community field optional for some layer types
        self.fields["community"].required = False

        # Set default values
        self.fields["zoom_level_min"].initial = 1
        self.fields["zoom_level_max"].initial = 18
        self.fields["opacity"].initial = 1.0
        self.fields["coordinate_system"].initial = "EPSG:4326"
        self.fields["is_visible"].initial = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class MapVisualizationForm(forms.ModelForm):
    """Form for creating and editing Map Visualizations."""

    class Meta:
        model = MapVisualization
        fields = [
            "title",
            "description",
            "visualization_type",
            "community",
            "assessment",
            "basemap_provider",
            "initial_zoom",
            "initial_center",
            "bounding_box",
            "color_scheme",
            "legend_configuration",
            "popup_template",
            "filters_configuration",
            "is_interactive",
            "enable_clustering",
            "enable_search",
            "enable_drawing",
            "is_public",
            "is_embedded",
            "layers",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Enter visualization title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "rows": 4,
                    "placeholder": "Describe the purpose and content of this visualization",
                }
            ),
            "visualization_type": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "community": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "assessment": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "basemap_provider": forms.Select(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "initial_zoom": forms.NumberInput(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "min": 1,
                    "max": 18,
                }
            ),
            "initial_center": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm",
                    "rows": 2,
                    "placeholder": "[longitude, latitude]",
                }
            ),
            "bounding_box": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm",
                    "rows": 2,
                    "placeholder": "[min_lng, min_lat, max_lng, max_lat]",
                }
            ),
            "color_scheme": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm",
                    "rows": 4,
                    "placeholder": "JSON color scheme configuration",
                }
            ),
            "legend_configuration": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm",
                    "rows": 4,
                    "placeholder": "JSON legend display configuration",
                }
            ),
            "popup_template": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm",
                    "rows": 6,
                    "placeholder": "HTML template for feature popups",
                }
            ),
            "filters_configuration": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm",
                    "rows": 4,
                    "placeholder": "JSON interactive filters configuration",
                }
            ),
            "is_interactive": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                }
            ),
            "enable_clustering": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                }
            ),
            "enable_search": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                }
            ),
            "enable_drawing": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                }
            ),
            "is_public": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                }
            ),
            "is_embedded": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                }
            ),
            "layers": forms.CheckboxSelectMultiple(attrs={"class": "space-y-2"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Make some fields optional
        self.fields["community"].required = False
        self.fields["assessment"].required = False

        # Set default values
        self.fields["initial_zoom"].initial = 10
        self.fields["basemap_provider"].initial = "openstreetmap"
        self.fields["is_interactive"].initial = True

        # Filter layers queryset to only show available ones
        if hasattr(self.fields["layers"], "queryset"):
            self.fields["layers"].queryset = GeographicDataLayer.objects.filter(
                is_public=True
            ).order_by("name")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance
