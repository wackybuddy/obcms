"""
Project Central Forms

Forms for workflow management, budget approval, and alert handling.
"""

from django import forms
from django.contrib.auth import get_user_model

from .models import ProjectWorkflow, Alert, BudgetCeiling, BudgetScenario
from mana.models import Need
from monitoring.models import MonitoringEntry
from coordination.models import MAOFocalPerson


def _tailwind_select_attrs():
    """Return base Tailwind classes for select widgets."""
    return (
        "block w-full rounded-xl border border-gray-200 bg-white py-3 px-4 text-sm "
        "focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200"
    )

User = get_user_model()


class ProjectWorkflowForm(forms.ModelForm):
    """Form for creating and editing project workflows."""

    class Meta:
        model = ProjectWorkflow
        fields = [
            'primary_need',
            'ppa',
            'project_lead',
            'mao_focal_person',
            'priority_level',
            'estimated_budget',
            'target_completion_date',
            'notes',
        ]
        widgets = {
            'primary_need': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'ppa': forms.Select(attrs={
                'class': 'form-select',
            }),
            'project_lead': forms.Select(attrs={
                'class': 'form-select',
            }),
            'mao_focal_person': forms.Select(attrs={
                'class': 'form-select',
            }),
            'priority_level': forms.Select(attrs={
                'class': 'form-select',
            }),
            'estimated_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'target_completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional notes about this workflow...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter needs to show only unfunded high-priority needs
        self.fields['primary_need'].queryset = Need.objects.filter(
            priority_score__gte=4.0
        ).order_by('-priority_score', '-created_at')

        # Filter PPAs
        self.fields['ppa'].queryset = MonitoringEntry.objects.filter(
            status__in=['planning', 'ongoing']
        ).order_by('-created_at')
        self.fields['ppa'].required = False

        # Filter users for project lead
        self.fields['project_lead'].queryset = User.objects.filter(
            is_staff=True, is_active=True
        ).order_by('first_name', 'last_name')
        self.fields['project_lead'].required = False

        # Filter MAOs
        self.fields['mao_focal_person'].queryset = MAOFocalPerson.objects.select_related(
            'mao', 'user'
        ).filter(
            is_active=True
        ).order_by('mao__name', 'user__first_name', 'user__last_name')
        self.fields['mao_focal_person'].required = False


class AdvanceWorkflowStageForm(forms.Form):
    """Form for advancing workflow to next stage."""

    new_stage = forms.ChoiceField(
        choices=ProjectWorkflow.WORKFLOW_STAGES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes about this stage transition...',
        })
    )

    def __init__(self, workflow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workflow = workflow

        # Filter choices to show only valid next stages
        current_stage_index = None
        for i, (code, label) in enumerate(ProjectWorkflow.WORKFLOW_STAGES):
            if code == workflow.current_stage:
                current_stage_index = i
                break

        if current_stage_index is not None:
            # Can only advance to next stages
            self.fields['new_stage'].choices = ProjectWorkflow.WORKFLOW_STAGES[current_stage_index + 1:]


class BudgetApprovalForm(forms.Form):
    """Form for budget approval actions."""

    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Comments about this approval decision...',
        })
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Required if rejecting - explain the reason...',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')

        if action == 'reject' and not rejection_reason:
            raise forms.ValidationError(
                'Rejection reason is required when rejecting a budget.'
            )

        return cleaned_data


class AcknowledgeAlertForm(forms.Form):
    """Form for acknowledging alerts."""

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes about this acknowledgment...',
        }),
        label='Acknowledgment Notes'
    )


class AlertFilterForm(forms.Form):
    """Filter form for alert listing."""

    alert_type = forms.ChoiceField(required=False)
    severity = forms.ChoiceField(required=False)
    active = forms.ChoiceField(
        required=False,
        choices=[
            ('true', 'Active Only'),
            ('false', 'All Alerts'),
        ],
        initial='true',
    )
    acknowledgment = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Alerts'),
            ('pending', 'Unacknowledged Only'),
        ],
        initial='',
        label='Acknowledgment Status',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['alert_type'].choices = [('', 'All Types')] + list(Alert.ALERT_TYPES)
        self.fields['severity'].choices = [('', 'All Severities')] + list(Alert.SEVERITY_LEVELS)

        select_class = _tailwind_select_attrs()
        for field_name in ['alert_type', 'severity', 'active', 'acknowledgment']:
            widget = self.fields[field_name].widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f"{existing} {select_class}".strip()

class BudgetCeilingForm(forms.ModelForm):
    """Form for creating and editing budget ceilings."""

    class Meta:
        model = BudgetCeiling
        fields = [
            'name',
            'fiscal_year',
            'sector',
            'funding_source',
            'ceiling_amount',
            'enforcement_level',
            'is_active',
            'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Education Sector FY2025',
            }),
            'fiscal_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2025',
            }),
            'sector': forms.Select(attrs={'class': 'form-select'}),
            'funding_source': forms.Select(attrs={'class': 'form-select'}),
            'ceiling_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'enforcement_level': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes or context for this budget ceiling...',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BudgetScenarioForm(forms.ModelForm):
    """Form for creating budget scenarios."""

    class Meta:
        model = BudgetScenario
        fields = [
            'name',
            'fiscal_year',
            'description',
            'is_baseline',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Baseline Scenario 2025',
            }),
            'fiscal_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2025',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe this budget scenario...',
            }),
            'is_baseline': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class WorkflowBlockerForm(forms.Form):
    """Form for reporting workflow blockers."""

    blocker_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe the blocker preventing progress...',
        }),
        label='Blocker Description'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['blocker_description'].help_text = (
            'Provide a clear description of what is blocking this workflow. '
            'This will set the workflow status to "blocked" and generate alerts.'
        )
