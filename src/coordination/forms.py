"""Forms for coordination module frontend interactions."""

from django import forms
from django.contrib.auth import get_user_model
from django.forms import BaseInlineFormSet, inlineformset_factory

from communities.models import OBCCommunity

from .models import (Organization, OrganizationContact, Partnership,
                     PartnershipDocument, PartnershipMilestone,
                     PartnershipSignatory)

INPUT_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
)
TEXTAREA_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
)
CHECKBOX_CLASS = "h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"

DATE_WIDGET = forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS})

MULTISELECT_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
)

User = get_user_model()


def _apply_field_styles(fields):
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
            widget.attrs.setdefault("class", CHECKBOX_CLASS)
        elif isinstance(widget, forms.SelectMultiple):
            widget.attrs.setdefault("class", MULTISELECT_CLASS)
        elif isinstance(widget, (forms.Textarea,)):
            widget.attrs.setdefault("class", TEXTAREA_CLASS)
        else:
            widget.attrs.setdefault("class", INPUT_CLASS)


class OrganizationForm(forms.ModelForm):
    """Collect organization metadata outside the admin interface."""

    social_media = forms.JSONField(
        required=False, widget=forms.Textarea(attrs={"rows": 3})
    )

    class Meta:
        model = Organization
        exclude = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
        widgets = {
            "partnership_start_date": DATE_WIDGET,
            "last_engagement_date": DATE_WIDGET,
        }

    def clean_social_media(self):
        social_media = self.cleaned_data.get("social_media")
        if not social_media:
            return None
        return social_media

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        if isinstance(self.fields.get("social_media").widget, forms.Textarea):
            self.fields["social_media"].widget.attrs.setdefault(
                "placeholder", '{"facebook": "https://facebook.com/..."}'
            )


class OrganizationContactForm(forms.ModelForm):
    """Inline form for creating organization contacts."""

    class Meta:
        model = OrganizationContact
        exclude = ["organization", "created_at", "updated_at"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)


class BaseOrganizationContactFormSet(BaseInlineFormSet):
    """Ensure only one primary contact is marked and ignore empty rows."""

    def clean(self):
        super().clean()
        primary_count = 0
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            if not form.cleaned_data or not form.has_changed():
                continue
            if form.cleaned_data.get("is_primary"):
                primary_count += 1
        if primary_count > 1:
            raise forms.ValidationError("Please mark only one contact as primary.")


OrganizationContactFormSet = inlineformset_factory(
    Organization,
    OrganizationContact,
    form=OrganizationContactForm,
    formset=BaseOrganizationContactFormSet,
    extra=1,
    can_delete=True,
)


class PartnershipForm(forms.ModelForm):
    """Frontend form mirroring the admin partnership configuration."""

    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": MULTISELECT_CLASS}),
    )
    communities = forms.ModelMultipleChoiceField(
        queryset=OBCCommunity.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": MULTISELECT_CLASS}),
        required=False,
    )

    class Meta:
        model = Partnership
        exclude = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
        widgets = {
            "concept_date": DATE_WIDGET,
            "negotiation_start_date": DATE_WIDGET,
            "signing_date": DATE_WIDGET,
            "start_date": DATE_WIDGET,
            "end_date": DATE_WIDGET,
            "renewal_date": DATE_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        self.fields["organizations"].queryset = Organization.objects.order_by("name")
        self.fields["communities"].queryset = OBCCommunity.objects.order_by("name")
        self.fields["focal_person"].queryset = User.objects.order_by(
            "first_name", "last_name"
        )
        self.fields["backup_focal_person"].queryset = User.objects.order_by(
            "first_name", "last_name"
        )
        self.fields["focal_person"].required = False
        self.fields["backup_focal_person"].required = False


class PartnershipSignatoryForm(forms.ModelForm):
    """Inline form for partnership signatories."""

    class Meta:
        model = PartnershipSignatory
        fields = ["organization", "name", "position", "signature_date"]
        widgets = {
            "signature_date": DATE_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        self.fields["organization"].queryset = Organization.objects.order_by("name")


class PartnershipMilestoneForm(forms.ModelForm):
    """Inline form for partnership milestones."""

    class Meta:
        model = PartnershipMilestone
        fields = ["title", "due_date", "status", "progress_percentage"]
        widgets = {
            "due_date": DATE_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)


class PartnershipDocumentForm(forms.ModelForm):
    """Inline form for partnership documents."""

    class Meta:
        model = PartnershipDocument
        fields = ["document_type", "title", "file", "is_confidential"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)


PartnershipSignatoryFormSet = inlineformset_factory(
    Partnership,
    PartnershipSignatory,
    form=PartnershipSignatoryForm,
    extra=1,
    can_delete=True,
)


PartnershipMilestoneFormSet = inlineformset_factory(
    Partnership,
    PartnershipMilestone,
    form=PartnershipMilestoneForm,
    extra=1,
    can_delete=True,
)


PartnershipDocumentFormSet = inlineformset_factory(
    Partnership,
    PartnershipDocument,
    form=PartnershipDocumentForm,
    extra=1,
    can_delete=True,
)
