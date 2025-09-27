"""Form classes for staff operations and management workflows."""

from django import forms
from django.utils import timezone

from common.constants import STAFF_COMPETENCY_CATEGORIES, STAFF_USER_TYPES
from common.models import (
    PerformanceTarget,
    StaffDevelopmentPlan,
    StaffProfile,
    StaffTask,
    StaffTeam,
    StaffTeamMembership,
    TrainingEnrollment,
    TrainingProgram,
    User,
)


def _apply_form_field_styles(form, mode: str = "default"):
    """Attach consistent Tailwind styles to form widgets."""

    table_mode = mode == "table"

    if table_mode:
        base_input_class = (
            "block w-full px-3 py-2 text-sm rounded-lg border border-transparent "
            "bg-white/70 hover:bg-white focus:bg-white focus:border-emerald-400 "
            "focus:ring-emerald-400 placeholder-gray-400 text-slate-900 font-sans "
            "transition-colors duration-150"
        )
        select_input_class = (
            "block w-full px-3 py-2 text-sm font-medium rounded-lg border border-transparent "
            "bg-white/80 hover:bg-white focus:bg-white appearance-none pr-9 font-sans "
            "focus:border-emerald-400 focus:ring-emerald-400 transition-colors duration-150"
        )
        textarea_class = (
            "block w-full px-3 py-2 text-sm rounded-lg border border-transparent "
            "bg-white/70 hover:bg-white focus:bg-white focus:border-emerald-400 "
            "focus:ring-emerald-400 font-sans"
        )
    else:
        base_input_class = (
            "block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm "
            "focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white "
            "transition-all duration-200"
        )
        select_input_class = base_input_class + " appearance-none pr-12"
        textarea_class = (
            "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm "
            "focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200"
        )
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault(
                "class",
                "h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500",
            )
        elif isinstance(widget, (forms.Textarea,)):
            widget.attrs.setdefault("class", textarea_class)
            widget.attrs.setdefault("rows", 3)
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs.setdefault("class", select_input_class)
        elif isinstance(
            widget,
            (
                forms.DateInput,
                forms.NumberInput,
                forms.EmailInput,
                forms.URLInput,
                forms.TimeInput,
                forms.TextInput,
            ),
        ):
            widget.attrs.setdefault("class", base_input_class)
        else:
            widget.attrs.setdefault("class", base_input_class)

        if isinstance(widget, forms.DateInput):
            widget.attrs.setdefault("type", "date")

        if table_mode:
            widget.attrs.setdefault("data-base-class", widget.attrs.get("class", ""))


class FocusAreasTextarea(forms.Textarea):
    """Textarea widget optimised for newline-delimited focus areas."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("rows", 3)
        kwargs["attrs"].setdefault(
            "placeholder", "e.g. Field coordination\nData integration\nReporting"
        )
        super().__init__(*args, **kwargs)


class CompetenciesTextarea(forms.Textarea):
    """Textarea widget for newline-delimited competency inputs."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("rows", 3)
        kwargs["attrs"].setdefault(
            "placeholder",
            "e.g. Moral Governance\nService Orientation\nCommunity Mapping",
        )
        super().__init__(*args, **kwargs)


def _newline_to_list(value: str) -> list[str]:
    """Convert newline-delimited text into a cleaned list."""

    if not value:
        return []
    return [item.strip() for item in value.splitlines() if item.strip()]


def _list_to_newline(value: list[str]) -> str:
    """Convert a stored list back into newline text for display."""

    return "\n".join(value or [])


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


class StaffProfileForm(forms.ModelForm):
    """Manage staff profile metadata and competencies."""

    core_competencies = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        help_text="List core competencies, one per line.",
    )
    leadership_competencies = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        help_text="Leadership competencies, one per line.",
    )
    functional_competencies = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        help_text="Functional competencies, one per line.",
    )
    date_joined_organization = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    position_classification = forms.CharField(
        required=False,
        label="Position classification",
        help_text="E.g., Supervisory, Support, Technical (refer to plantilla)",
    )
    plantilla_item_number = forms.CharField(
        required=False,
        label="Plantilla / item number",
        help_text="Reference the plantilla or job order number if applicable.",
    )
    salary_grade = forms.CharField(
        required=False,
        label="Salary grade",
        help_text="Philippine government salary grade (e.g., SG 18).",
    )
    salary_step = forms.CharField(
        required=False,
        label="Step",
        help_text="Indicate step within the salary grade if known.",
    )
    reports_to = forms.CharField(
        required=False,
        label="Reports to",
        help_text="Name or position of the immediate supervisor.",
    )
    job_purpose = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Job purpose / mandate",
        help_text="Summarize why the role exists and how it supports Bangsamoro governance.",
    )
    key_result_areas = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        label="Key result areas",
        help_text="Outline primary KRAs or strategic themes; one per line.",
    )
    major_functions = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        label="Major functions / tasks",
        help_text="List core functions or duties (use action verbs); one per line.",
    )
    deliverables = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        label="Deliverables / outputs",
        help_text="Expected outputs or means of verification; one per line.",
    )
    supervision_lines = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        label="Supervision & coordination",
        help_text="Document supervisory relationships, meeting cadences, or coordination notes; one per line.",
    )
    cross_functional_partners = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        label="Cross-functional partners",
        help_text="Name offices/teams frequently coordinated with; one per line.",
    )
    qualification_education = forms.CharField(
        required=False,
        label="Qualification – education",
        help_text="Highest education requirement per plantilla or internal standards.",
    )
    qualification_training = forms.CharField(
        required=False,
        label="Qualification – training",
        help_text="Formal trainings required (hours / topics).",
    )
    qualification_experience = forms.CharField(
        required=False,
        label="Qualification – experience",
        help_text="Years and type of relevant experience.",
    )
    qualification_eligibility = forms.CharField(
        required=False,
        label="Qualification – eligibility",
        help_text="Specify civil service or BARMM eligibility / licensure.",
    )
    qualification_competency = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Competency standards / proficiency",
        help_text="Summarize expected proficiency levels (e.g., Critical Thinking – Proficient).",
    )
    job_documents_url = forms.URLField(
        required=False,
        label="Reference documents URL",
        help_text="Link to job description, competency rubric, or supporting files.",
    )

    class Meta:
        model = StaffProfile
        fields = [
            "user",
            "employment_status",
            "employment_type",
            "position_classification",
            "plantilla_item_number",
            "salary_grade",
            "salary_step",
            "reports_to",
            "date_joined_organization",
            "primary_location",
            "job_purpose",
            "key_result_areas",
            "major_functions",
            "deliverables",
            "supervision_lines",
            "cross_functional_partners",
            "core_competencies",
            "leadership_competencies",
            "functional_competencies",
            "qualification_education",
            "qualification_training",
            "qualification_experience",
            "qualification_eligibility",
            "qualification_competency",
            "job_documents_url",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        staff_qs = (
            User.objects.filter(user_type__in=STAFF_USER_TYPES)
            .order_by("last_name", "first_name")
            .distinct()
        )
        self.fields["user"].queryset = staff_qs
        if request:
            self.fields["user"].empty_label = "Select staff member"

        list_fields = (
            "core_competencies",
            "leadership_competencies",
            "functional_competencies",
            "key_result_areas",
            "major_functions",
            "deliverables",
            "supervision_lines",
            "cross_functional_partners",
        )

        for field_name in list_fields:
            current = getattr(self.instance, field_name, None)
            if isinstance(current, list) and current and not self.initial.get(field_name):
                self.initial[field_name] = _list_to_newline(current)
            elif not current and field_name not in self.initial:
                suggested = []
                if field_name in {"core_competencies", "leadership_competencies", "functional_competencies"}:
                    suggested = STAFF_COMPETENCY_CATEGORIES.get(field_name.split("_")[0], [])
                self.initial[field_name] = _list_to_newline(suggested)

        _apply_form_field_styles(self)

    def clean_core_competencies(self):
        return _newline_to_list(self.cleaned_data.get("core_competencies", ""))

    def clean_leadership_competencies(self):
        return _newline_to_list(self.cleaned_data.get("leadership_competencies", ""))

    def clean_functional_competencies(self):
        return _newline_to_list(self.cleaned_data.get("functional_competencies", ""))

    def clean_key_result_areas(self):
        return _newline_to_list(self.cleaned_data.get("key_result_areas", ""))

    def clean_major_functions(self):
        return _newline_to_list(self.cleaned_data.get("major_functions", ""))

    def clean_deliverables(self):
        return _newline_to_list(self.cleaned_data.get("deliverables", ""))

    def clean_supervision_lines(self):
        return _newline_to_list(self.cleaned_data.get("supervision_lines", ""))

    def clean_cross_functional_partners(self):
        return _newline_to_list(self.cleaned_data.get("cross_functional_partners", ""))

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
        table_mode = kwargs.pop("table_mode", False)
        super().__init__(*args, **kwargs)
        self.table_mode = table_mode
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
        _apply_form_field_styles(self, mode="table" if table_mode else "default")

        title_widget = self.fields["title"].widget
        title_class = title_widget.attrs.get("class", "")
        if table_mode:
            emphasis_classes = (
                " font-semibold text-slate-900 tracking-tight border border-slate-200/60 "
                "shadow-sm bg-white focus:border-emerald-400 focus:ring-emerald-400 "
                "focus:outline-none"
            )
        else:
            emphasis_classes = (
                " font-semibold text-blue-700 border-blue-200 focus:border-blue-400 "
                "focus:ring-blue-400"
            )
        title_widget.attrs["class"] = (title_class + emphasis_classes).strip()

        if table_mode:
            title_widget.attrs.setdefault("placeholder", "Task name")
            title_widget.attrs.setdefault("data-notion-control", "title")
            title_widget.attrs["data-base-class"] = title_widget.attrs.get("class", "")

            def _configure_select(field_name: str, control_name: str):
                widget = self.fields[field_name].widget
                widget.attrs.setdefault("data-notion-control", control_name)
                base_class = widget.attrs.get("class", "")
                widget.attrs["class"] = (
                    base_class
                    + " font-sans text-sm font-medium bg-white/80 hover:bg-white border "
                    "border-slate-200/70 cursor-pointer"
                ).strip()
                if getattr(widget, "allow_multiple_selected", False):
                    widget.attrs["class"] += " min-h-[2.75rem]"
                    widget.attrs.setdefault("size", 3)
                    widget.attrs.setdefault("data-multiple", "true")
                existing_style = widget.attrs.get("style", "").strip()
                style_parts = [fragment for fragment in existing_style.rstrip(";").split(";") if fragment]
                style_parts.append("font-family:inherit")
                widget.attrs["style"] = ";".join(style_parts)
                widget.attrs["data-base-class"] = widget.attrs.get("class", "")

            _configure_select("assignee", "assignee")
            _configure_select("team", "team")
            _configure_select("status", "status")
            _configure_select("priority", "priority")

            progress_widget = self.fields["progress"].widget
            progress_widget.attrs.setdefault("min", 0)
            progress_widget.attrs.setdefault("max", 100)
            progress_widget.attrs.setdefault("step", 10)
            progress_widget.attrs.setdefault("data-notion-control", "progress")
            progress_widget.attrs["class"] = (
                progress_widget.attrs.get("class", "")
                + " text-sm font-semibold text-slate-700 font-sans"
            ).strip()
            progress_widget.attrs["data-base-class"] = progress_widget.attrs.get(
                "class", ""
            )

            start_widget = self.fields["start_date"].widget
            start_widget.attrs.setdefault("data-notion-control", "start-date")
            start_widget.attrs["class"] = (
                start_widget.attrs.get("class", "") + " text-sm font-sans"
            ).strip()
            start_widget.attrs["data-base-class"] = start_widget.attrs.get("class", "")

            due_widget = self.fields["due_date"].widget
            due_widget.attrs.setdefault("placeholder", "No due date")
            due_widget.attrs.setdefault("data-notion-control", "due-date")
            due_widget.attrs["class"] = (
                due_widget.attrs.get("class", "") + " text-sm font-sans"
            ).strip()
            due_widget.attrs["data-base-class"] = due_widget.attrs.get("class", "")

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        due = cleaned_data.get("due_date")
        if start and due and due < start:
            self.add_error("due_date", "Due date cannot be earlier than the start date.")
        return cleaned_data


class PerformanceTargetForm(forms.ModelForm):
    """Capture or update staff/team performance targets."""

    period_start = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    period_end = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = PerformanceTarget
        fields = [
            "scope",
            "staff_profile",
            "team",
            "metric_name",
            "performance_standard",
            "target_value",
            "actual_value",
            "unit",
            "status",
            "period_start",
            "period_end",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["staff_profile"].queryset = (
            StaffProfile.objects.select_related("user")
            .order_by("user__last_name", "user__first_name")
        )
        self.fields["team"].queryset = StaffTeam.objects.order_by("name")
        self.fields["staff_profile"].required = False
        self.fields["team"].required = False
        _apply_form_field_styles(self)


class TrainingProgramForm(forms.ModelForm):
    """Create or edit training programme records."""

    competency_focus = forms.CharField(
        required=False,
        widget=CompetenciesTextarea(),
        help_text="Competencies supported (one per line).",
    )

    class Meta:
        model = TrainingProgram
        fields = [
            "title",
            "category",
            "description",
            "delivery_mode",
            "competency_focus",
            "duration_days",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.instance.competency_focus, list) and not self.initial.get(
            "competency_focus"
        ):
            self.initial["competency_focus"] = _list_to_newline(
                self.instance.competency_focus
            )
        _apply_form_field_styles(self)

    def clean_competency_focus(self):
        value = self.cleaned_data.get("competency_focus", "")
        if isinstance(value, list):
            return value
        return _newline_to_list(value)


class TrainingEnrollmentForm(forms.ModelForm):
    """Assign staff to training programmes."""

    scheduled_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    completion_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = TrainingEnrollment
        fields = [
            "staff_profile",
            "program",
            "status",
            "scheduled_date",
            "completion_date",
            "evidence_url",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["staff_profile"].queryset = (
            StaffProfile.objects.select_related("user")
            .order_by("user__last_name", "user__first_name")
        )
        self.fields["program"].queryset = TrainingProgram.objects.filter(is_active=True).order_by(
            "title"
        )
        _apply_form_field_styles(self)


class StaffDevelopmentPlanForm(forms.ModelForm):
    """Maintain staff development plan entries."""

    target_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = StaffDevelopmentPlan
        fields = [
            "staff_profile",
            "title",
            "competency_focus",
            "target_date",
            "status",
            "support_needed",
            "notes",
        ]
        widgets = {
            "support_needed": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["staff_profile"].queryset = (
            StaffProfile.objects.select_related("user")
            .order_by("user__last_name", "user__first_name")
        )
        _apply_form_field_styles(self)
