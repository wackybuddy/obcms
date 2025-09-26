"""Forms for Monitoring & Evaluation operations."""

from django import forms

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity

from .models import MonitoringEntry, MonitoringUpdate


class BaseMonitoringEntryForm(forms.ModelForm):
    """Base form helpers shared across entry quick-create forms."""

    class Meta:
        model = MonitoringEntry
        fields: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        queryset_fields = {
            "lead_organization",
            "supporting_organizations",
            "submitted_by_community",
            "communities",
            "submitted_to_organization",
            "implementing_moa",
            "coverage_region",
            "coverage_province",
            "coverage_municipality",
            "coverage_barangay",
        }

        for field_name in queryset_fields.intersection(self.fields.keys()):
            field = self.fields[field_name]
            field.queryset = field.queryset.order_by("name")

        tailwind_input = (
            "block w-full px-4 py-3 rounded-xl border border-neutral-200 "
            "bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
            "text-sm transition"
        )
        coverage_placeholders = {
            "coverage_region": "Select region...",
            "coverage_province": "Select province...",
            "coverage_municipality": "Select municipality / city...",
            "coverage_barangay": "Select barangay...",
        }

        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {tailwind_input}".strip()
            placeholder_source = field.help_text or field.label
            if placeholder_source:
                field.widget.attrs.setdefault("placeholder", placeholder_source)
            widget_input_type = getattr(field.widget, "input_type", None)
            if widget_input_type == "select-multiple":
                field.widget.attrs.setdefault("size", 4)
            if name in coverage_placeholders:
                field.widget.attrs.setdefault("data-placeholder", coverage_placeholders[name])
                initial_value = (
                    self.initial.get(name)
                    if name in self.initial
                    else (
                        getattr(self.instance, name + "_id", "")
                        if getattr(self.instance, "pk", None)
                        else ""
                    )
                )
                if isinstance(initial_value, (Region, Province, Municipality, Barangay)):
                    initial_value = initial_value.pk
                if initial_value:
                    field.widget.attrs.setdefault("data-initial", str(initial_value))

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance = self._apply_category_defaults(instance)
        if commit:
            instance.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
            self._post_save(instance)
        return instance

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        """Allow subclasses to enforce category-specific defaults."""

        return instance

    def _post_save(self, instance: MonitoringEntry) -> None:  # pragma: no cover - default no-op
        """Hook for subclasses to mutate m2m relations after save."""

        return None


class MonitoringMOAEntryForm(BaseMonitoringEntryForm):
    """Quick-create form for MOA PPAs accessible by OBCs."""

    class Meta(BaseMonitoringEntryForm.Meta):
        fields = [
            "implementing_moa",
            "title",
            "summary",
            "budget_allocation",
            "budget_obc_allocation",
            "total_slots",
            "obc_slots",
            "coverage_region",
            "coverage_province",
            "coverage_municipality",
            "coverage_barangay",
            "communities",
            "obcs_benefited",
            "status",
            "progress",
            "start_date",
            "target_end_date",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "obcs_benefited": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        coverage_region = cleaned_data.get("coverage_region")
        coverage_province = cleaned_data.get("coverage_province")
        coverage_municipality = cleaned_data.get("coverage_municipality")
        coverage_barangay = cleaned_data.get("coverage_barangay")

        if not cleaned_data.get("implementing_moa"):
            self.add_error(
                "implementing_moa",
                "Select the implementing MOA for this PPA.",
            )
        if cleaned_data.get("progress") is None:
            cleaned_data["progress"] = 0

        if coverage_province and coverage_province.region_id != getattr(
            coverage_region, "id", None
        ):
            self.add_error(
                "coverage_province",
                "Selected province does not belong to the chosen region.",
            )
        if coverage_municipality and coverage_municipality.province_id != getattr(
            coverage_province, "id", None
        ):
            self.add_error(
                "coverage_municipality",
                "Municipality must belong to the selected province.",
            )
        if coverage_barangay and coverage_barangay.municipality_id != getattr(
            coverage_municipality, "id", None
        ):
            self.add_error(
                "coverage_barangay",
                "Barangay must belong to the selected municipality.",
            )
        return cleaned_data

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        instance.category = "moa_ppa"
        instance.request_status = ""
        if instance.progress is None:
            instance.progress = 0
        return instance


class MonitoringOOBCEntryForm(BaseMonitoringEntryForm):
    """Quick-create form for OOBC-led initiatives."""

    class Meta(BaseMonitoringEntryForm.Meta):
        fields = [
            "title",
            "summary",
            "oobc_unit",
            "communities",
            "supporting_organizations",
            "status",
            "progress",
            "start_date",
            "target_end_date",
            "budget_allocation",
            "budget_currency",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("oobc_unit"):
            self.add_error(
                "oobc_unit",
                "Identify the OOBC unit responsible for this initiative.",
            )
        if cleaned_data.get("progress") is None:
            cleaned_data["progress"] = 0
        return cleaned_data

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        instance.category = "oobc_ppa"
        instance.request_status = ""
        if instance.progress is None:
            instance.progress = 0
        return instance


class MonitoringRequestEntryForm(BaseMonitoringEntryForm):
    """Quick-create form for OBC requests and proposals."""

    class Meta(BaseMonitoringEntryForm.Meta):
        fields = [
            "title",
            "summary",
            "submitted_by_community",
            "submitted_to_organization",
            "lead_organization",
            "communities",
            "supporting_organizations",
            "priority",
            "support_required",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "support_required": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("submitted_by_community"):
            self.add_error(
                "submitted_by_community",
                "Identify the requesting OBC community.",
            )
        if not cleaned_data.get("submitted_to_organization") and not cleaned_data.get(
            "lead_organization"
        ):
            self.add_error(
                "submitted_to_organization",
                "Provide the receiving OOBC unit or external MOA for the request.",
            )
        return cleaned_data

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        instance.category = "obc_request"
        instance.status = "planning"
        instance.request_status = "submitted"
        instance.progress = 0
        return instance

    def _post_save(self, instance: MonitoringEntry) -> None:
        if (
            instance.submitted_by_community
            and not instance.communities.filter(pk=instance.submitted_by_community.pk).exists()
        ):
            instance.communities.add(instance.submitted_by_community)


class MonitoringOBCQuickCreateForm(forms.ModelForm):
    """Minimal form for inline creation of barangay-level OBC communities."""

    region = forms.ModelChoiceField(
        queryset=Region.objects.none(),
        required=True,
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        label="Province",
    )
    municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),
        required=True,
        label="Municipality / City",
    )

    class Meta:
        model = OBCCommunity
        fields = ["name", "community_names", "barangay", "obc_id"]
        labels = {
            "name": "OBC Name",
            "community_names": "Alternate Names (optional)",
            "barangay": "Barangay",
            "obc_id": "OBC ID (optional)",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "placeholder": "e.g., Purok Maharlika Muslim Community",
                }
            ),
            "community_names": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "placeholder": "Other known names (comma-separated)",
                }
            ),
            "obc_id": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "placeholder": "Registry identifier (optional)",
                }
            ),
            "barangay": forms.Select(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def resolve(model, value):
            if not value:
                return None
            if isinstance(value, model):
                return value
            try:
                return model.objects.get(pk=value)
            except model.DoesNotExist:
                return None

        select_attrs = {
            "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
        }

        region_field = self.fields["region"]
        province_field = self.fields["province"]
        municipality_field = self.fields["municipality"]
        barangay_field = self.fields["barangay"]
        name_field = self.fields.get("name")

        if name_field:
            name_field.required = True
        if self.fields.get("community_names"):
            self.fields["community_names"].required = False
        if self.fields.get("obc_id"):
            self.fields["obc_id"].required = False

        region_field.queryset = Region.objects.filter(is_active=True).order_by("code", "name")
        region_field.empty_label = "Select region..."
        region_field.widget.attrs.update(select_attrs)
        region_field.widget.attrs.setdefault("data-placeholder", "Select region...")

        province_field.empty_label = "Select province..."
        province_field.widget.attrs.update(select_attrs)
        province_field.widget.attrs.setdefault("data-placeholder", "Select province...")

        municipality_field.empty_label = "Select municipality / city..."
        municipality_field.widget.attrs.update(select_attrs)
        municipality_field.widget.attrs.setdefault(
            "data-placeholder", "Select municipality / city..."
        )

        barangay_field.empty_label = "Select barangay..."
        barangay_field.widget.attrs.update(select_attrs)
        barangay_field.widget.attrs.setdefault("data-placeholder", "Select barangay...")

        selected_region = None
        selected_province = None
        selected_municipality = None
        selected_barangay = None

        if self.instance and getattr(self.instance, "barangay", None):
            selected_barangay = self.instance.barangay
            selected_municipality = selected_barangay.municipality
            selected_province = selected_municipality.province
            selected_region = selected_province.region

        if self.initial.get("region"):
            selected_region = resolve(Region, self.initial.get("region"))
        if self.initial.get("province"):
            selected_province = resolve(Province, self.initial.get("province"))
        if self.initial.get("municipality"):
            selected_municipality = resolve(Municipality, self.initial.get("municipality"))
        if self.initial.get("barangay"):
            selected_barangay = resolve(Barangay, self.initial.get("barangay"))

        if self.is_bound:
            selected_region = resolve(Region, self.data.get("region")) or selected_region
            selected_province = resolve(Province, self.data.get("province")) or selected_province
            selected_municipality = resolve(Municipality, self.data.get("municipality")) or selected_municipality
            selected_barangay = resolve(Barangay, self.data.get("barangay")) or selected_barangay

        if selected_region:
            province_field.queryset = (
                Province.objects.filter(region=selected_region, is_active=True).order_by("name")
            )
        else:
            province_field.queryset = Province.objects.none()

        if selected_province:
            municipality_field.queryset = (
                Municipality.objects.filter(province=selected_province, is_active=True).order_by("name")
            )
        elif selected_region:
            municipality_field.queryset = (
                Municipality.objects.filter(province__region=selected_region, is_active=True).order_by("name")
            )
        else:
            municipality_field.queryset = Municipality.objects.none()

        if selected_municipality:
            barangay_field.queryset = (
                Barangay.objects.filter(municipality=selected_municipality, is_active=True).order_by("name")
            )
        elif selected_province:
            barangay_field.queryset = (
                Barangay.objects.filter(municipality__province=selected_province, is_active=True).order_by("name")
            )
        elif selected_region:
            barangay_field.queryset = (
                Barangay.objects.filter(municipality__province__region=selected_region, is_active=True).order_by("name")
            )
        else:
            barangay_field.queryset = Barangay.objects.none()

        if not self.is_bound:
            if selected_region:
                region_field.initial = selected_region
            if selected_province:
                province_field.initial = selected_province
            if selected_municipality:
                municipality_field.initial = selected_municipality
            if selected_barangay:
                barangay_field.initial = selected_barangay

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get("region")
        province = cleaned_data.get("province")
        municipality = cleaned_data.get("municipality")
        barangay = cleaned_data.get("barangay")

        if province and region and province.region_id != region.id:
            self.add_error("province", "Selected province does not belong to the chosen region.")

        if municipality and province and municipality.province_id != province.id:
            self.add_error(
                "municipality",
                "Selected municipality/city does not belong to the chosen province.",
            )

        if barangay and municipality and barangay.municipality_id != municipality.id:
            self.add_error(
                "barangay",
                "Selected barangay does not belong to the chosen municipality/city.",
            )

        return cleaned_data

class MonitoringUpdateForm(forms.ModelForm):
    """Form for recording monitoring updates."""

    class Meta:
        model = MonitoringUpdate
        fields = [
            "update_type",
            "status",
            "request_status",
            "progress",
            "notes",
            "next_steps",
            "follow_up_date",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "next_steps": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        update_type = cleaned_data.get("update_type")

        if update_type == "status" and not cleaned_data.get("status"):
            self.add_error("status", "Provide the updated implementation status.")

        if update_type == "progress" and cleaned_data.get("progress") is None:
            self.add_error("progress", "Capture the new progress percentage.")

        if update_type == "milestone" and not cleaned_data.get("follow_up_date"):
            self.add_error("follow_up_date", "Set the follow-up date for the milestone.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_input = (
            "block w-full px-4 py-3 rounded-xl border border-neutral-200 "
            "bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
            "text-sm transition"
        )
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {tailwind_input}".strip()
            placeholder_source = field.help_text or field.label
            if placeholder_source:
                field.widget.attrs.setdefault("placeholder", placeholder_source)
            widget_input_type = getattr(field.widget, "input_type", None)
            if widget_input_type == "select-multiple":
                field.widget.attrs.setdefault("size", 4)
