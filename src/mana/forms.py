"""Forms for the MANA module."""

from django import forms
from django.contrib.auth import get_user_model

from communities.models import OBCCommunity

from .models import Assessment, AssessmentCategory, WorkshopActivity


INPUT_CLASS = (
    "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none "
    "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
)

SELECT_CLASS = (
    "block w-full py-3 px-4 text-base rounded-lg border border-gray-300 shadow-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
    "min-h-[48px] transition-all duration-200 bg-white"
)


class DeskReviewQuickEntryForm(forms.ModelForm):
    """Quick entry form for logging desk review assessments."""

    planned_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )
    planned_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )

    class Meta:
        model = Assessment
        fields = [
            "title",
            "category",
            "community",
            "assessment_level",
            "status",
            "priority",
            "planned_start_date",
            "planned_end_date",
            "description",
            "objectives",
            "location_details",
            "lead_assessor",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "e.g., Desk Review for OBC Community",
                    "class": INPUT_CLASS,
                }
            ),
            "category": forms.Select(attrs={"class": SELECT_CLASS}),
            "community": forms.Select(attrs={"class": SELECT_CLASS}),
            "assessment_level": forms.Select(attrs={"class": SELECT_CLASS}),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "priority": forms.Select(attrs={"class": SELECT_CLASS}),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Summarize scope and references to be reviewed",
                    "class": INPUT_CLASS,
                }
            ),
            "objectives": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Outline objectives guiding the desk review",
                    "class": INPUT_CLASS,
                }
            ),
            "location_details": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Optional: list barangays/areas covered",
                    "class": INPUT_CLASS,
                }
            ),
            "lead_assessor": forms.Select(attrs={"class": SELECT_CLASS}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.request_user = user
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = AssessmentCategory.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["community"].queryset = (
            OBCCommunity.objects.filter(is_active=True)
            .select_related("barangay__municipality__province")
            .order_by("barangay__name")
        )
        self.fields["lead_assessor"].queryset = get_user_model().objects.filter(
            is_active=True
        ).order_by("first_name", "last_name")

        self.fields["lead_assessor"].required = False
        self.fields["status"].initial = "planning"
        self.fields["priority"].initial = "medium"
        self.fields["assessment_level"].initial = "community"

        if user and user.is_authenticated:
            self.fields["lead_assessor"].initial = user.pk

    def clean(self):
        data = super().clean()
        start = data.get("planned_start_date")
        end = data.get("planned_end_date")
        if start and end and end < start:
            raise forms.ValidationError("End date must be on or after the start date.")
        return data

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        instance.primary_methodology = "desk_review"
        if user is not None:
            instance.created_by = user
            if not instance.lead_assessor_id:
                instance.lead_assessor = user
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class SurveyQuickEntryForm(forms.ModelForm):
    """Quick entry form for rolling survey assessments."""

    planned_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )
    planned_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )

    class Meta:
        model = Assessment
        fields = [
            "title",
            "category",
            "community",
            "assessment_level",
            "status",
            "priority",
            "planned_start_date",
            "planned_end_date",
            "description",
            "objectives",
            "location_details",
            "lead_assessor",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "e.g., Rolling Survey Cycle for Region/Province",
                    "class": INPUT_CLASS,
                }
            ),
            "category": forms.Select(attrs={"class": SELECT_CLASS}),
            "community": forms.Select(attrs={"class": SELECT_CLASS}),
            "assessment_level": forms.Select(attrs={"class": SELECT_CLASS}),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "priority": forms.Select(attrs={"class": SELECT_CLASS}),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Outline scope, target population, and sampling cadence.",
                    "class": INPUT_CLASS,
                }
            ),
            "objectives": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Document indicators and decision points supported by this survey cycle.",
                    "class": INPUT_CLASS,
                }
            ),
            "location_details": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "List provinces/municipalities covered by focal persons.",
                    "class": INPUT_CLASS,
                }
            ),
            "lead_assessor": forms.Select(attrs={"class": SELECT_CLASS}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.request_user = user
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = AssessmentCategory.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["community"].queryset = (
            OBCCommunity.objects.filter(is_active=True)
            .select_related("barangay__municipality__province")
            .order_by("barangay__name")
        )
        self.fields["lead_assessor"].queryset = get_user_model().objects.filter(
            is_active=True
        ).order_by("first_name", "last_name")

        self.fields["lead_assessor"].required = False
        self.fields["status"].initial = "data_collection"
        self.fields["priority"].initial = "high"
        self.fields["assessment_level"].initial = "community"

        if user and user.is_authenticated:
            self.fields["lead_assessor"].initial = user.pk

    def clean(self):
        data = super().clean()
        start = data.get("planned_start_date")
        end = data.get("planned_end_date")
        if start and end and end < start:
            raise forms.ValidationError("End date must be on or after the start date.")
        return data

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        instance.primary_methodology = "survey"
        if user is not None:
            instance.created_by = user
            if not instance.lead_assessor_id:
                instance.lead_assessor = user
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class WorkshopActivityProgressForm(forms.ModelForm):
    """Update actual results for a pre-created workshop activity."""

    class Meta:
        model = WorkshopActivity
        fields = [
            "status",
            "actual_participants",
            "key_findings",
            "recommendations",
            "challenges_encountered",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "actual_participants": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASS,
                    "min": 0,
                }
            ),
            "key_findings": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Summarize the key insights generated during this workshop.",
                    "class": INPUT_CLASS,
                }
            ),
            "recommendations": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Document proposed actions or follow-on steps discussed.",
                    "class": INPUT_CLASS,
                }
            ),
            "challenges_encountered": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Note logistical issues, participation gaps, or risks encountered.",
                    "class": INPUT_CLASS,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["actual_participants"].required = False
        self.fields["key_findings"].required = False
        self.fields["recommendations"].required = False
        self.fields["challenges_encountered"].required = False



class KIIQuickEntryForm(forms.ModelForm):
    """Quick entry form for key informant interview-driven assessments."""

    planned_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )
    planned_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )

    class Meta:
        model = Assessment
        fields = [
            "title",
            "category",
            "community",
            "assessment_level",
            "status",
            "priority",
            "planned_start_date",
            "planned_end_date",
            "description",
            "objectives",
            "location_details",
            "lead_assessor",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "e.g., KII Roundtable for [Province/Theme]",
                    "class": INPUT_CLASS,
                }
            ),
            "category": forms.Select(attrs={"class": SELECT_CLASS}),
            "community": forms.Select(attrs={"class": SELECT_CLASS}),
            "assessment_level": forms.Select(attrs={"class": SELECT_CLASS}),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "priority": forms.Select(attrs={"class": SELECT_CLASS}),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Summarize informant profiles, focus themes, and intended outputs.",
                    "class": INPUT_CLASS,
                }
            ),
            "objectives": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "List guiding questions, policy hooks, and decisions supported by KIIs.",
                    "class": INPUT_CLASS,
                }
            ),
            "location_details": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Note interview venues, virtual platforms, or LGU partners involved.",
                    "class": INPUT_CLASS,
                }
            ),
            "lead_assessor": forms.Select(attrs={"class": SELECT_CLASS}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.request_user = user
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = AssessmentCategory.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["community"].queryset = (
            OBCCommunity.objects.filter(is_active=True)
            .select_related("barangay__municipality__province")
            .order_by("barangay__name")
        )
        self.fields["lead_assessor"].queryset = get_user_model().objects.filter(
            is_active=True
        ).order_by("first_name", "last_name")

        self.fields["lead_assessor"].required = False
        self.fields["status"].initial = "preparation"
        self.fields["priority"].initial = "high"
        self.fields["assessment_level"].initial = "community"

        if user and user.is_authenticated:
            self.fields["lead_assessor"].initial = user.pk

    def clean(self):
        data = super().clean()
        start = data.get("planned_start_date")
        end = data.get("planned_end_date")
        if start and end and end < start:
            raise forms.ValidationError("End date must be on or after the start date.")
        return data

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)
        instance.primary_methodology = "kii"
        if user is not None:
            instance.created_by = user
            if not instance.lead_assessor_id:
                instance.lead_assessor = user
        if commit:
            instance.save()
            self.save_m2m()
        return instance
