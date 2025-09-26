"""Form classes for staff operations and management workflows."""

from django import forms
from django.utils import timezone

from common.constants import STAFF_USER_TYPES
from common.models import StaffTask, StaffTeam, StaffTeamMembership, User


def _apply_form_field_styles(form):
    """Attach consistent Tailwind styles to form widgets."""

    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault(
                "class", "rounded text-emerald-600 focus:ring-emerald-500"
            )
        else:
            widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm",
            )


class FocusAreasTextarea(forms.Textarea):
    """Textarea widget optimised for newline-delimited focus areas."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("rows", 3)
        kwargs["attrs"].setdefault(
            "placeholder", "e.g. Field coordination\nData integration\nReporting"
        )
        super().__init__(*args, **kwargs)


class StaffTeamForm(forms.ModelForm):
    """Create or update staff teams."""

    focus_areas = forms.CharField(
        label="Focus areas",
        required=False,
        help_text="List key focus areas (one per line).",
        widget=FocusAreasTextarea(),
    )

    class Meta:
        model = StaffTeam
        fields = ["name", "description", "mission", "focus_areas", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        focus = self.instance.focus_areas if self.instance and self.instance.focus_areas else []
        if isinstance(focus, list):
            self.initial.setdefault("focus_areas", "\n".join(focus))
        _apply_form_field_styles(self)

    def clean_focus_areas(self):
        """Normalise newline-delimited focus areas into a list."""
        value = self.cleaned_data.get("focus_areas", "")
        if not value:
            return []
        return [item.strip() for item in value.splitlines() if item.strip()]


class StaffTeamMembershipForm(forms.ModelForm):
    """Assign staff to teams with specific roles."""

    class Meta:
        model = StaffTeamMembership
        fields = ["team", "user", "role", "is_active", "notes"]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        user_qs = User.objects.filter(user_type__in=STAFF_USER_TYPES)
        self.fields["user"].queryset = user_qs.order_by("last_name", "first_name")
        self.fields["team"].queryset = StaffTeam.objects.filter(is_active=True).order_by(
            "name"
        )
        if request:
            self.fields["team"].empty_label = "Select team"
            self.fields["user"].empty_label = "Select staff"
        _apply_form_field_styles(self)


class StaffTaskForm(forms.ModelForm):
    """Create or update staff tasks."""

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = StaffTask
        fields = [
            "title",
            "team",
            "assignee",
            "priority",
            "status",
            "impact",
            "description",
            "start_date",
            "due_date",
            "progress",
            "linked_event",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "impact": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields["team"].queryset = StaffTeam.objects.filter(is_active=True).order_by(
            "name"
        )
        staff_qs = User.objects.filter(user_type__in=STAFF_USER_TYPES, is_active=True)
        self.fields["assignee"].queryset = staff_qs.order_by("last_name", "first_name")
        if request:
            self.fields["team"].empty_label = "Select team"
            self.fields["assignee"].empty_label = "Assign to (optional)"
        if not self.initial.get("start_date"):
            self.initial.setdefault("start_date", timezone.now().date())
        _apply_form_field_styles(self)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        due = cleaned_data.get("due_date")
        if start and due and due < start:
            self.add_error("due_date", "Due date cannot be earlier than the start date.")
        return cleaned_data
