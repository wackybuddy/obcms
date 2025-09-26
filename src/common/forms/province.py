"""Forms for managing province records used across modules."""

from django import forms

from common.models import Province


class ProvinceForm(forms.ModelForm):
    """Minimal province editor for MANA provincial management."""

    class Meta:
        model = Province
        fields = [
            "code",
            "name",
            "capital",
            "population_total",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "e.g., R11-DDS",
            }),
            "name": forms.TextInput(attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500",
            }),
            "capital": forms.TextInput(attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500",
            }),
            "population_total": forms.NumberInput(attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500",
                "min": 0,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500",
            }),
        }

    def clean_code(self):
        code = self.cleaned_data.get("code", "").strip()
        if not code:
            raise forms.ValidationError("Province code is required.")
        return code

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Province name is required.")
        return name
