"""Forms for the MANA module."""

from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from communities.models import OBCCommunity, ProvinceCoverage, Municipality, Barangay
from common.models import Province, Region

from .models import (
    Assessment,
    AssessmentCategory,
    WorkshopActivity,
    WorkshopParticipantAccount,
    WorkshopResponse,
)


INPUT_CLASS = (
    "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none "
    "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
)

SELECT_CLASS = (
    "block w-full py-3 px-4 text-base rounded-lg border border-gray-300 shadow-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
    "min-h-[48px] transition-all duration-200 bg-white"
)
TEXTAREA_CLASS = (
    "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none "
    "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
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


class AssessmentUpdateForm(forms.ModelForm):
    """Model form used for updating existing assessments via the frontend UI."""

    planned_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )
    planned_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=True,
    )
    actual_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=False,
    )
    actual_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        required=False,
    )

    class Meta:
        model = Assessment
        fields = [
            "title",
            "category",
            "assessment_level",
            "primary_methodology",
            "status",
            "priority",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "community",
            "province",
            "location_details",
            "description",
            "objectives",
            "lead_assessor",
            "estimated_budget",
            "actual_budget",
            "impact_level",
            "key_findings",
            "recommendations",
            "progress_percentage",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "category": forms.Select(attrs={"class": SELECT_CLASS}),
            "assessment_level": forms.Select(attrs={"class": SELECT_CLASS}),
            "primary_methodology": forms.Select(attrs={"class": SELECT_CLASS}),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "priority": forms.Select(attrs={"class": SELECT_CLASS}),
            "community": forms.Select(attrs={"class": SELECT_CLASS}),
            "province": forms.Select(attrs={"class": SELECT_CLASS}),
            "lead_assessor": forms.Select(attrs={"class": SELECT_CLASS}),
            "impact_level": forms.Select(attrs={"class": SELECT_CLASS}),
            "progress_percentage": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "min": 0, "max": 100}
            ),
            "estimated_budget": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "step": "0.01", "min": 0}
            ),
            "actual_budget": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "step": "0.01", "min": 0}
            ),
            "location_details": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
            "description": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "objectives": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "key_findings": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "recommendations": forms.Textarea(
                attrs={"class": TEXTAREA_CLASS, "rows": 4}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        user_model = get_user_model()

        self.fields["category"].queryset = AssessmentCategory.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["community"].queryset = (
            OBCCommunity.objects.filter(is_active=True)
            .select_related("barangay__municipality__province")
            .order_by(
                "barangay__municipality__province__name",
                "barangay__municipality__name",
                "barangay__name",
            )
        )
        self.fields["province"].queryset = Province.objects.filter(is_active=True).order_by(
            "region__name",
            "name",
        )
        self.fields["lead_assessor"].queryset = user_model.objects.filter(
            is_active=True
        ).order_by("first_name", "last_name")

        self.fields["community"].required = False
        self.fields["province"].required = False
        self.fields["impact_level"].required = False
        self.fields["estimated_budget"].required = False
        self.fields["actual_budget"].required = False

        if not self.instance.pk and user and user.is_authenticated:
            self.fields["lead_assessor"].initial = user.pk

        if self.instance and self.instance.community:
            self.fields["community"].initial = self.instance.community_id
        if self.instance and self.instance.province:
            self.fields["province"].initial = self.instance.province_id

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("planned_start_date")
        end = cleaned_data.get("planned_end_date")
        if start and end and end < start:
            self.add_error(
                "planned_end_date",
                "Planned end date cannot be earlier than the start date.",
            )

        actual_start = cleaned_data.get("actual_start_date")
        actual_end = cleaned_data.get("actual_end_date")
        if actual_start and actual_end and actual_end < actual_start:
            self.add_error(
                "actual_end_date",
                "Actual end date cannot be earlier than the start date.",
            )

        level = cleaned_data.get("assessment_level")
        community = cleaned_data.get("community")
        province = cleaned_data.get("province")

        if community and province:
            self.add_error(
                "community",
                "Select either a community or a province, not both.",
            )
            self.add_error(
                "province",
                "Select either a community or a province, not both.",
            )

        if level in {"regional", "provincial"}:
            if not province:
                self.add_error(
                    "province",
                    "Regional and provincial assessments must be linked to a province.",
                )
            cleaned_data["community"] = None
            self.instance.community = None
        else:
            if not community:
                self.add_error(
                    "community",
                    "Community, barangay, and city/municipal assessments must be linked to a community.",
                )
            cleaned_data["province"] = None
            self.instance.province = None

        return cleaned_data

    def save(self, user=None, commit=True):
        instance = super().save(commit=False)

        # Ensure the instance relation matches cleaned data
        instance.community = self.cleaned_data.get("community")
        instance.province = self.cleaned_data.get("province")

        if user is not None and not instance.lead_assessor_id:
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


class RegionalWorkshopSetupForm(forms.ModelForm):
    """Form to launch a regional-level workshop assessment using Region/Province selection."""

    # Region selection field
    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=True,
        label="Region",
        widget=forms.Select(attrs={
            "class": SELECT_CLASS,
            "data-level": "region"
        }),
        help_text="Region where the assessment will be conducted"
    )

    # Province selection field (will be populated via JavaScript)
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),  # Empty initially
        required=True,
        label="Province",
        widget=forms.Select(attrs={
            "class": SELECT_CLASS,
            "data-level": "province"
        }),
        help_text="Province being assessed"
    )

    # Date fields
    planned_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        label="Planned Start Date",
        help_text="When the regional workshop will begin"
    )
    planned_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        label="Planned End Date",
        help_text="When the regional workshop will end"
    )

    # Optional target participants
    target_participants = forms.IntegerField(
        required=False,
        min_value=1,
        initial=30,
        label="Target Participants",
        widget=forms.NumberInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Number of expected participants (default: 30)",
            }
        ),
        help_text="Expected number of participants for the workshops"
    )

    class Meta:
        model = Assessment
        fields = [
            "title",
            "planned_start_date",
            "planned_end_date",
            "objectives",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "e.g., Regional Workshop Cycle - SOCCSKSARGEN 2025",
                }
            ),
            "objectives": forms.Textarea(
                attrs={
                    "class": INPUT_CLASS,
                    "rows": 3,
                    "placeholder": "Key objectives for the regional workshop cycle",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": INPUT_CLASS,
                    "rows": 3,
                    "placeholder": "Brief description of the regional MANA deployment and coverage",
                }
            ),
        }

    def __init__(self, *args, regions=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure the underlying Assessment instance carries the regional defaults
        if not self.instance.pk:
            # New assessments start as regional workshop entries
            self.instance.assessment_level = "regional"
            self.instance.primary_methodology = "workshop"
        else:
            # Preserve existing values but never fall back to community-level defaults
            self.instance.assessment_level = (
                self.instance.assessment_level or "regional"
            )
            self.instance.primary_methodology = (
                self.instance.primary_methodology or "workshop"
            )
        self.instance.community = None

        # Set up region queryset (optionally filter by provided regions)
        region_qs = Region.objects.filter(is_active=True).order_by("code", "name")
        if regions is not None:
            region_qs = region_qs.filter(id__in=[r.id for r in regions])
        self.fields["region"].queryset = region_qs

        # If editing existing assessment, populate province choices
        if self.instance and self.instance.pk and self.instance.province:
            selected_region = self.instance.province.region
            self.fields["region"].initial = selected_region.id
            self.fields["province"].queryset = Province.objects.filter(
                region=selected_region, is_active=True
            ).order_by("name")
            self.fields["province"].initial = self.instance.province.id
        # If form is bound (POST data), populate province choices based on submitted region
        elif self.is_bound and self.data.get('region'):
            try:
                region_id = int(self.data.get('region'))
                self.fields["province"].queryset = Province.objects.filter(
                    region_id=region_id, is_active=True
                ).order_by("name")
                # Add data attribute to preserve selected province value in JavaScript
                province_id = self.data.get('province')
                if province_id:
                    self.fields["province"].widget.attrs['data-initial'] = province_id
            except (ValueError, TypeError):
                pass
        else:
            # If no region is selected yet, allow all active provinces
            # This ensures the form doesn't fail validation if JavaScript hasn't run yet
            self.fields["province"].queryset = Province.objects.filter(
                is_active=True
            ).order_by("name")

        # Set default values
        today = timezone.now().date()
        self.fields["planned_start_date"].initial = self.fields["planned_start_date"].initial or today
        self.fields["planned_end_date"].initial = self.fields["planned_end_date"].initial or (today + timedelta(days=4))
        self.fields["target_participants"].initial = 30
        self.fields["title"].initial = (
            self.fields["title"].initial
            or f"Regional Workshop Cycle - {today.year}"
        )
        self.fields["objectives"].initial = self.fields["objectives"].initial or (
            "Coordinate the regional workshop cycle and document core outputs across the mandated sessions."
        )
        self.fields["description"].initial = self.fields["description"].initial or (
            "Regional-level facilitation of the five-day MANA workshop structure, covering context, aspirations, collaboration, feedback, and action planning."
        )

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()

        # Validate dates
        start_date = cleaned_data.get('planned_start_date')
        end_date = cleaned_data.get('planned_end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "Planned end date cannot be earlier than start date."
            )

        # Validate that the province belongs to the selected region
        region = cleaned_data.get('region')
        province = cleaned_data.get('province')

        if region and province and province.region != region:
            raise forms.ValidationError(
                "The selected province does not belong to the selected region."
            )

        # Carry over relational defaults so model-level validation passes
        if province:
            self.instance.province = province
            self.instance.community = None

        self.instance.assessment_level = "regional"
        self.instance.primary_methodology = "workshop"

        return cleaned_data

    def save(self, user=None, commit=True):
        """Save the assessment with proper defaults for regional workshop."""
        assessment = super().save(commit=False)

        # Create or get the assessment category
        category, _ = AssessmentCategory.objects.get_or_create(
            name="OBC-MANA Workshop",
            defaults={
                "category_type": "needs_assessment",
                "description": "Other Bangsamoro Communities Mapping and Needs Assessment",
                "icon": "fas fa-users",
                "color": "#3B82F6",
            },
        )

        # Set assessment properties for regional workshop
        assessment.category = category
        assessment.assessment_level = "regional"
        assessment.primary_methodology = "workshop"
        assessment.priority = assessment.priority or "medium"

        # Link to province instead of community
        assessment.province = self.cleaned_data['province']
        assessment.community = None  # Regional assessments don't link to specific communities

        # Set user as lead assessor if provided
        if user is not None:
            assessment.created_by = user
            if not assessment.lead_assessor_id:
                assessment.lead_assessor = user

        if commit:
            assessment.save()
            self.save_m2m()

        return assessment


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

class BaseWorkshopForm(forms.ModelForm):
    """Shared helpers for workshop question capture forms."""

    general_fields = ("status", "actual_participants")
    synthesis_fields = ("key_findings", "recommendations")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.question_field_names = [
            name
            for name in self.fields
            if name not in (*self.general_fields, *self.synthesis_fields)
        ]

        if self.instance and self.instance.pk and self.instance.workshop_outputs:
            for key, value in self.instance.workshop_outputs.items():
                if key in self.fields:
                    self.fields[key].initial = value

    def save(self, commit=True):
        instance = super().save(commit=False)

        workshop_outputs = {}
        for key, value in self.cleaned_data.items():
            if key not in (*self.general_fields, *self.synthesis_fields):
                workshop_outputs[key] = value

        instance.workshop_outputs = workshop_outputs or None

        if commit:
            instance.save()

        return instance

    class Meta:
        model = WorkshopActivity
        fields = ["status", "actual_participants", "key_findings", "recommendations"]
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
                    "class": TEXTAREA_CLASS,
                }
            ),
            "recommendations": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Document proposed actions or follow-on steps discussed.",
                    "class": TEXTAREA_CLASS,
                }
            ),
        }

class Workshop1Form(BaseWorkshopForm):
    """Workshop 1: Understanding the Community Context"""
    community_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': TEXTAREA_CLASS}), label="Describe the OBCs in your region/province. What is their estimated total population? Are they mostly living in urban or rural areas? What sectors do they represent (farmers, business, laborers, traders, fisherfolk, etc.)?", required=False)
    quality_of_life = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': TEXTAREA_CLASS}), label="How would you describe their general quality of life? How is their access to government services such as education, health, and social protection? What are their main sources of livelihood and income?", required=False)
    socio_economic_issues = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': TEXTAREA_CLASS}), label="What are the most pressing socio-economic issues they face today? What is their level of access to infrastructure (roads, utilities, communication, housing) and financial or business services? Has it improved, worsened, or remained the same in recent years?", required=False)
    cultural_preservation = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': TEXTAREA_CLASS}), label="How are OBCs preserving and promoting their culture, religion, and identity? What cultural issues and challenges do they face?", required=False)

class Workshop2Form(BaseWorkshopForm):
    """Workshop 2: Community Aspirations and Priorities"""
    vulnerable_areas = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Which OBC municipalities or barangays in your area are most vulnerable? Please identify up to three and explain why.", required=False)
    vulnerable_sectors = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Which sectors of the OBCs (farmers, women, youth, workers, PWDs, IPs, IDPs, business owners, etc.) are most vulnerable? How are these groups coping or responding to these vulnerabilities?", required=False)
    long_term_aspirations = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="What are the common long-term aspirations of OBCs for development, identity, and well-being? Which of these should be achieved in the short term (1–3 years) and which in the long term (5–10 years)?", required=False)
    top_three_issues = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="In your opinion, what are the top three issues that must be addressed immediately to improve the quality of life of OBCs?", required=False)
    prioritized_programs = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="What economic, social, and cultural development programs should be prioritized for OBCs in your area?", required=False)
    rights_issues = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="What rights issues are most prevalent in OBCs (e.g., access to services, non-discrimination, representation, land, peace and security)? How are the rights of OBCs currently being protected and promoted? What more needs to be done?", required=False)

class Workshop3Form(BaseWorkshopForm):
    """Workshop 3: Community Collaboration and Empowerment"""
    representation_in_governance = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="How are OBCs currently represented in local governance and development processes (barangay, municipal, city, provincial)? Which groups or leaders usually participate, and which sectors are left out?", required=False)
    obc_organizations = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Are there OBC organizations in your area—such as youth groups, women’s associations, religious or traditional councils—that significantly contribute to local governance and development?", required=False)
    improving_representation = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="How can the representation and participation of OBCs in governance and development be improved? What specific measures should be taken to strengthen the voices of OBCs?", required=False)
    collaboration_mechanisms = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="What collaboration mechanisms could be established or improved to ensure the protection of rights and promotion of welfare and development of OBCs?", required=False)
    transparency_and_equity = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="How can transparency, accountability, and equity be ensured so that the benefits of development initiatives by government and partners are inclusive and reach all sectors of the OBCs?", required=False)

class Workshop4Form(BaseWorkshopForm):
    """Workshop 4: Community Feedback on Existing Initiatives"""
    existing_programs = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="What existing programs, projects, and services for OBCs are provided by: LGUs, NGAs, BARMM, Other stakeholders?", required=False)
    access_to_programs = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="How are OBCs currently accessing these programs and services? Which groups (women, youth, PWDs, IPs, IDPs) benefit most, and who is being left behind?", required=False)
    effectiveness_of_initiatives = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="How effective are these initiatives? Which ones have succeeded, which ones have failed or faced significant challenges, and why? What improvements would you recommend to ensure quality delivery and inclusivity?", required=False)
    online_access = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="How are LGUs, NGAs, and the Bangsamoro Government providing virtual or online access to these services? How is technology and digital connectivity being used to improve access for OBCs?", required=False)
    untapped_resources = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="What other resources or support are available in your area that OBCs have not yet tapped or optimized (such as scholarships, livelihood programs, ICT hubs, partnerships, or local initiatives)?", required=False)

class Workshop5Form(BaseWorkshopForm):
    """Workshop 5: OBCs Needs, Challenges, Factors, and Outcomes"""
    critical_challenges = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Challenges – What are the most critical challenges faced by OBCs in your area (education, health, livelihood, governance, infrastructure, peace and security)? Who are the most affected (women, youth, PWDs, IPs, IDPs, elders)?", required=False)
    challenge_factors = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Factors – What are the main causes or factors behind each challenge? Are these related to policies, lack of resources, discrimination, geography, or governance gaps? And are these factors internal to the community, external (from government or other stakeholders), or both?", required=False)
    specific_needs = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Needs – Based on these challenges and factors, what specific needs must be addressed to improve the OBCs’ situation (e.g., livelihood programs, schools, health facilities, roads, scholarships, justice access, inclusion mechanisms)?", required=False)
    expected_outcomes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Outcomes – If these needs are addressed, what positive outcomes or changes do you expect for the OBC? How would these outcomes affect vulnerable groups specifically?", required=False)
    prioritization = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CLASS}), label="Prioritization – Of the challenges and needs identified, which should be addressed first? Why? How are these challenges connected to each other?", required=False)


# Regional MANA Workshop Redesign Forms


class ParticipantOnboardingForm(forms.ModelForm):
    """Form for participant onboarding and profile completion."""

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS}),
        label="Temporary Password",
        help_text="You will be able to change this after first login",
        required=True,
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS}),
        label="Confirm Password",
        required=True,
    )

    consent = forms.BooleanField(
        required=True,
        label="I consent to participate in this workshop and allow my responses to be used for assessment purposes",
    )

    class Meta:
        model = WorkshopParticipantAccount
        fields = [
            "stakeholder_type",
            "organization",
            "province",
            "municipality",
            "barangay",
        ]
        widgets = {
            "stakeholder_type": forms.Select(attrs={"class": SELECT_CLASS}),
            "organization": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Organization or community you represent",
                }
            ),
            "province": forms.Select(attrs={"class": SELECT_CLASS}),
            "municipality": forms.Select(attrs={"class": SELECT_CLASS}),
            "barangay": forms.Select(attrs={"class": SELECT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["municipality"].required = False
        self.fields["barangay"].required = False

        instance = self.instance
        province = getattr(instance, "province", None)

        if province:
            self.fields["province"].queryset = Province.objects.filter(pk=province.pk)
            self.fields["province"].initial = province
            self.fields["province"].widget = forms.HiddenInput()
            self.fields["province"].required = False
            self.fields["municipality"].queryset = (
                Municipality.objects.filter(province=province).order_by("name")
            )
            self.fields["barangay"].queryset = (
                Barangay.objects.filter(municipality__province=province).order_by("name")
            )
        else:
            self.fields["province"].queryset = Province.objects.none()
            self.fields["municipality"].queryset = Municipality.objects.none()
            self.fields["barangay"].queryset = Barangay.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        province = getattr(self.instance, "province", None)
        cleaned_data["province"] = province

        municipality = cleaned_data.get("municipality")
        if municipality and province and municipality.province_id != province.id:
            self.add_error("municipality", "Select a municipality within your province.")
            cleaned_data["municipality"] = None

        barangay = cleaned_data.get("barangay")
        if barangay and province and barangay.municipality.province_id != province.id:
            self.add_error("barangay", "Select a barangay within your province.")
            cleaned_data["barangay"] = None

        return cleaned_data

        instance = self.instance
        province = getattr(instance, "province", None)

        if province:
            self.fields["province"].queryset = Province.objects.filter(pk=province.pk)
            self.fields["province"].initial = province
            self.fields["province"].widget = forms.HiddenInput()
            self.fields["province"].required = False
            self.fields["municipality"].queryset = (
                Municipality.objects.filter(province=province).order_by("name")
            )
            self.fields["barangay"].queryset = (
                Barangay.objects.filter(municipality__province=province).order_by("name")
            )
        else:
            self.fields["province"].queryset = Province.objects.none()
            self.fields["municipality"].queryset = Municipality.objects.none()
            self.fields["barangay"].queryset = Barangay.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")

        province = getattr(self.instance, "province", None)
        cleaned_data["province"] = province

        municipality = cleaned_data.get("municipality")
        if municipality and province and municipality.province_id != province.id:
            self.add_error("municipality", "Select a municipality within your province.")
            cleaned_data["municipality"] = None

        barangay = cleaned_data.get("barangay")
        if barangay and province and barangay.municipality.province_id != province.id:
            self.add_error("barangay", "Select a barangay within your province.")
            cleaned_data["barangay"] = None

        return cleaned_data


class ParticipantProfileForm(forms.ModelForm):
    """Form for editing participant profile after onboarding."""

    class Meta:
        model = WorkshopParticipantAccount
        fields = [
            "stakeholder_type",
            "organization",
            "province",
            "municipality",
            "barangay",
        ]
        widgets = {
            "stakeholder_type": forms.Select(attrs={"class": SELECT_CLASS}),
            "organization": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "province": forms.Select(attrs={"class": SELECT_CLASS}),
            "municipality": forms.Select(attrs={"class": SELECT_CLASS}),
            "barangay": forms.Select(attrs={"class": SELECT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["municipality"].required = False
        self.fields["barangay"].required = False

        instance = self.instance
        province = getattr(instance, "province", None)

        if province:
            self.fields["province"].queryset = Province.objects.filter(pk=province.pk)
            self.fields["province"].initial = province
            self.fields["province"].widget = forms.HiddenInput()
            self.fields["province"].required = False
            self.fields["municipality"].queryset = (
                Municipality.objects.filter(province=province).order_by("name")
            )
            self.fields["barangay"].queryset = (
                Barangay.objects.filter(municipality__province=province).order_by("name")
            )
        else:
            self.fields["province"].queryset = Province.objects.none()
            self.fields["municipality"].queryset = Municipality.objects.none()
            self.fields["barangay"].queryset = Barangay.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        province = getattr(self.instance, "province", None)
        cleaned_data["province"] = province

        municipality = cleaned_data.get("municipality")
        if municipality and province and municipality.province_id != province.id:
            self.add_error("municipality", "Select a municipality within your province.")
            cleaned_data["municipality"] = None

        barangay = cleaned_data.get("barangay")
        if barangay and province and barangay.municipality.province_id != province.id:
            self.add_error("barangay", "Select a barangay within your province.")
            cleaned_data["barangay"] = None

        return cleaned_data


class FacilitatorParticipantForm(forms.ModelForm):
    """Form for facilitators to register new participants."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": INPUT_CLASS}),
        help_text="Participant email (used as username)",
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
        required=False,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
        required=False,
    )
    temp_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS}),
        required=False,
        help_text="Leave blank to generate an automatic temporary password.",
    )

    class Meta:
        model = WorkshopParticipantAccount
        fields = [
            "stakeholder_type",
            "organization",
            "province",
            "municipality",
            "barangay",
        ]
        widgets = {
            "stakeholder_type": forms.Select(attrs={"class": SELECT_CLASS}),
            "organization": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "province": forms.Select(attrs={"class": SELECT_CLASS}),
            "municipality": forms.Select(attrs={"class": SELECT_CLASS}),
            "barangay": forms.Select(attrs={"class": SELECT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["municipality"].required = False
        self.fields["barangay"].required = False

        instance = self.instance
        province = getattr(instance, "province", None)

        if province:
            self.fields["province"].queryset = Province.objects.filter(pk=province.pk)
            self.fields["province"].initial = province
            self.fields["province"].widget = forms.HiddenInput()
            self.fields["province"].required = False
            self.fields["municipality"].queryset = (
                Municipality.objects.filter(province=province).order_by("name")
            )
            self.fields["barangay"].queryset = (
                Barangay.objects.filter(municipality__province=province).order_by("name")
            )
        else:
            self.fields["province"].queryset = Province.objects.none()
            self.fields["municipality"].queryset = Municipality.objects.none()
            self.fields["barangay"].queryset = Barangay.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        province = getattr(self.instance, "province", None)
        cleaned_data["province"] = province

        municipality = cleaned_data.get("municipality")
        if municipality and province and municipality.province_id != province.id:
            self.add_error("municipality", "Select a municipality within your province.")
            cleaned_data["municipality"] = None

        barangay = cleaned_data.get("barangay")
        if barangay and province and barangay.municipality.province_id != province.id:
            self.add_error("barangay", "Select a barangay within your province.")
            cleaned_data["barangay"] = None

        return cleaned_data



class WorkshopResponseForm(forms.Form):
    """Dynamic form for workshop responses based on question schema."""

    def __init__(self, *args, questions_schema=None, existing_responses=None, **kwargs):
        """
        Initialize form with dynamic fields based on question schema.

        Args:
            questions_schema: List of question definitions from JSON schema
            existing_responses: Dict of existing responses keyed by question_id
        """
        super().__init__(*args, **kwargs)

        if not questions_schema:
            return

        existing_responses = existing_responses or {}

        for question in questions_schema:
            field = self._create_field_for_question(question)
            self.fields[question["id"]] = field

            # Populate initial data from existing responses
            if question["id"] in existing_responses:
                self.initial[question["id"]] = existing_responses[question["id"]]

    def _create_field_for_question(self, question):
        """Create appropriate form field based on question type."""
        field_type = question.get("type")
        required = question.get("required", False)
        help_text = question.get("help_text", "")

        if field_type == "long_text":
            return forms.CharField(
                widget=forms.Textarea(
                    attrs={
                        "class": f"{TEXTAREA_CLASS} hx-field",
                        "rows": 4,
                        "placeholder": help_text,
                        "data-autosave": "true",
                    }
                ),
                label=question["text"],
                required=required,
                help_text=help_text,
            )

        elif field_type == "text":
            return forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        "class": f"{INPUT_CLASS} hx-field",
                        "placeholder": help_text,
                        "data-autosave": "true",
                    }
                ),
                label=question["text"],
                required=required,
                help_text=help_text,
            )

        elif field_type == "number":
            return forms.IntegerField(
                widget=forms.NumberInput(
                    attrs={
                        "class": f"{INPUT_CLASS} hx-field",
                        "data-autosave": "true",
                        "min": question.get("min", 0),
                        "max": question.get("max", ""),
                    }
                ),
                label=question["text"],
                required=required,
                help_text=help_text,
            )

        elif field_type == "select":
            choices = [(opt, opt) for opt in question.get("options", [])]
            return forms.ChoiceField(
                widget=forms.Select(
                    attrs={
                        "class": f"{SELECT_CLASS} hx-field",
                        "data-autosave": "true",
                    }
                ),
                choices=[("", "-- Select --")] + choices,
                label=question["text"],
                required=required,
                help_text=help_text,
            )

        elif field_type == "repeater":
            # Repeater fields are handled as JSON data
            # The frontend will render dynamic add/remove UI
            return forms.CharField(
                widget=forms.HiddenInput(
                    attrs={
                        "data-type": "repeater",
                        "data-repeater-storage": "true",
                    }
                ),
                label=question["text"],
                required=False,
                help_text=help_text,
            )

        elif field_type == "structured":
            # Structured fields are also JSON
            return forms.CharField(
                widget=forms.HiddenInput(
                    attrs={
                        "data-type": "structured",
                        "data-repeater-storage": "true",
                    }
                ),
                label=question["text"],
                required=False,
                help_text=help_text,
            )

        else:
            # Default to text field
            return forms.CharField(
                widget=forms.TextInput(
                    attrs={"class": f"{INPUT_CLASS} hx-field"}
                ),
                label=question["text"],
                required=required,
                help_text=help_text,
            )


class FacilitatorBulkImportForm(forms.Form):
    """Form for facilitators to bulk import participants via CSV."""

    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file with columns: first_name, last_name, email, stakeholder_type, province, organization",
        widget=forms.FileInput(attrs={"class": INPUT_CLASS, "accept": ".csv"}),
    )

    send_emails = forms.BooleanField(
        required=False,
        initial=True,
        label="Send welcome emails with login credentials",
    )

    def clean_csv_file(self):
        """Validate CSV file format."""
        csv_file = self.cleaned_data.get("csv_file")

        if not csv_file:
            return csv_file

        # Check file extension
        if not csv_file.name.endswith(".csv"):
            raise forms.ValidationError("File must be a CSV file")

        # Check file size (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File size must be less than 5MB")

        return csv_file


class WorkshopSynthesisRequestForm(forms.Form):
    """Form for facilitators to request AI synthesis of workshop responses."""

    workshop = forms.ModelChoiceField(
        queryset=WorkshopActivity.objects.none(),
        label="Workshop",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
        required=True,
    )

    filter_province = forms.ModelChoiceField(
        queryset=Province.objects.filter(is_active=True),
        label="Filter by Province (optional)",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
        required=False,
    )

    filter_stakeholder_type = forms.ChoiceField(
        choices=[("", "All Stakeholder Types")]
        + WorkshopParticipantAccount.STAKEHOLDER_TYPES,
        label="Filter by Stakeholder Type (optional)",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
        required=False,
    )

    provider = forms.ChoiceField(
        choices=[
            ("anthropic", "Anthropic Claude"),
            ("openai", "OpenAI GPT-4"),
        ],
        initial="anthropic",
        label="AI Provider",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
        required=True,
    )

    custom_prompt = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": TEXTAREA_CLASS,
                "rows": 6,
                "placeholder": "Optional: Provide custom synthesis prompt. Leave blank to use default template.",
            }
        ),
        label="Custom Prompt (optional)",
        required=False,
    )

    def __init__(self, *args, assessment=None, **kwargs):
        super().__init__(*args, **kwargs)

        if assessment:
            self.fields["workshop"].queryset = WorkshopActivity.objects.filter(
                assessment=assessment
            ).order_by("workshop_day", "start_time")
