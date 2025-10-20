"""
Budget Preparation Forms

ModelForms for budget proposal creation and management.
Implements Tailwind CSS styling per OBCMS UI standards.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from .models import BudgetProposal, ProgramBudget, BudgetLineItem, BudgetJustification
from monitoring.models import MonitoringEntry
from planning.models import StrategicGoal, AnnualWorkPlan


class BudgetProposalForm(forms.ModelForm):
    """
    Form for creating and editing budget proposals.
    """

    class Meta:
        model = BudgetProposal
        fields = ['fiscal_year', 'title', 'description']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'placeholder': 'Enter budget proposal title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 4,
                'placeholder': 'Provide an overview of this budget proposal',
            }),
        }

        labels = {
            'fiscal_year': 'Fiscal Year',
            'title': 'Proposal Title',
            'description': 'Description',
        }

        help_texts = {
            'fiscal_year': 'Budget year (current year or future)',
            'title': 'Brief title describing this budget proposal',
            'description': 'Overview of objectives and scope',
        }

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)

        # Mark required fields
        for field_name in ['fiscal_year', 'title']:
            self.fields[field_name].required = True

        # Configure fiscal year choices (current year + next 5 years)
        current_year = timezone.now().year
        fiscal_year_field = self.fields['fiscal_year']
        fiscal_year_field.widget = forms.Select(attrs={
            'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
        })
        fiscal_year_field.choices = [
            (year, year) for year in range(current_year, current_year + 6)
        ]

    def clean_fiscal_year(self):
        """Validate fiscal year is current or future."""
        fiscal_year = self.cleaned_data.get('fiscal_year')
        current_year = timezone.now().year

        if fiscal_year < current_year:
            raise ValidationError(
                f"Fiscal year must be {current_year} or later."
            )

        # Check for duplicate proposal for this organization/fiscal year
        if self.organization:
            existing = BudgetProposal.objects.filter(
                organization=self.organization,
                fiscal_year=fiscal_year
            )

            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    f"Budget proposal for FY {fiscal_year} already exists."
                )

        return fiscal_year


class ProgramBudgetForm(forms.ModelForm):
    """
    Form for adding/editing program budgets within a proposal.
    """

    class Meta:
        model = ProgramBudget
        fields = [
            'monitoring_entry',
            'requested_amount',
            'approved_amount',
            'priority_rank',
            'strategic_goal',
            'annual_work_plan',
            'justification',
            'expected_outcomes'
        ]

        widgets = {
            'monitoring_entry': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'requested_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'approved_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'priority_rank': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'min': '1',
            }),
            'strategic_goal': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'annual_work_plan': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'justification': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 3,
                'placeholder': 'Explain why this budget allocation is necessary',
            }),
            'expected_outcomes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 3,
                'placeholder': 'Describe expected deliverables and outcomes',
            }),
        }

        labels = {
            'monitoring_entry': 'Monitoring Entry (PPA)',
            'requested_amount': 'Requested Amount (₱)',
            'approved_amount': 'Approved Amount (₱)',
            'priority_rank': 'Priority Rank',
            'strategic_goal': 'Strategic Goal',
            'annual_work_plan': 'Annual Work Plan',
            'justification': 'Justification',
            'expected_outcomes': 'Expected Outcomes',
        }

    def __init__(self, *args, **kwargs):
        self.proposal = kwargs.pop('proposal', None)
        super().__init__(*args, **kwargs)

        # Limit selectable records for contextual relevance
        if self.proposal:
            fiscal_year = self.proposal.fiscal_year
            self.fields['monitoring_entry'].queryset = MonitoringEntry.objects.filter(
                fiscal_year=fiscal_year
            ).order_by("title")
            self.fields['strategic_goal'].queryset = StrategicGoal.objects.filter(
                strategic_plan__start_year__lte=fiscal_year,
                strategic_plan__end_year__gte=fiscal_year,
            )
            self.fields['annual_work_plan'].queryset = AnnualWorkPlan.objects.filter(
                year=fiscal_year
            )
        else:
            self.fields['monitoring_entry'].queryset = MonitoringEntry.objects.none()
            self.fields['strategic_goal'].queryset = StrategicGoal.objects.none()
            self.fields['annual_work_plan'].queryset = AnnualWorkPlan.objects.none()

        # Mark required fields
        for field_name in self.fields:
            self.fields[field_name].required = True

    def clean(self):
        """Validate program budget."""
        cleaned_data = super().clean()
        monitoring_entry = cleaned_data.get('monitoring_entry')
        requested_amount = cleaned_data.get('requested_amount')

        if requested_amount and requested_amount <= 0:
            raise ValidationError({
                'requested_amount': 'Budget amount must be greater than zero.'
            })

        # Check for duplicate program in proposal
        if self.proposal and monitoring_entry:
            existing = ProgramBudget.objects.filter(
                budget_proposal=self.proposal,
                monitoring_entry=monitoring_entry
            )

            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError({
                    'monitoring_entry': 'This monitoring entry is already included in the proposal.'
                })

        return cleaned_data


class BudgetLineItemForm(forms.ModelForm):
    """
    Form for individual budget line items.
    """

    class Meta:
        model = BudgetLineItem
        fields = ['category', 'sub_category', 'description', 'unit_cost', 'quantity', 'justification', 'notes']

        widgets = {
            'category': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'sub_category': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'placeholder': 'e.g., Salaries, Supplies (optional)',
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'placeholder': 'e.g., Office Supplies, Training Materials',
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200',
                'placeholder': '1',
                'min': '1',
            }),
            'justification': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 2,
                'placeholder': 'Explain why this line item is needed (optional)',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 2,
                'placeholder': 'Additional notes or specifications',
            }),
        }

        labels = {
            'category': 'Category',
            'description': 'Description',
            'unit_cost': 'Unit Cost (₱)',
            'quantity': 'Quantity',
            'justification': 'Justification',
            'notes': 'Notes',
        }

    def clean(self):
        """Validate line item data."""
        cleaned_data = super().clean()
        unit_cost = cleaned_data.get('unit_cost')
        quantity = cleaned_data.get('quantity')

        if unit_cost and unit_cost <= 0:
            raise ValidationError({
                'unit_cost': 'Unit cost must be greater than zero.'
            })

        if quantity and quantity < 1:
            raise ValidationError({
                'quantity': 'Quantity must be at least 1.'
            })

        return cleaned_data


# Formset for managing multiple line items
BudgetLineItemFormSet = forms.inlineformset_factory(
    ProgramBudget,
    BudgetLineItem,
    form=BudgetLineItemForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class BudgetJustificationForm(forms.ModelForm):
    """
    Form for evidence-based budget justification linking to MANA/M&E.
    """

    class Meta:
        model = BudgetJustification
        fields = [
            'rationale',
            'alignment_with_priorities',
            'expected_impact',
            'needs_assessment_reference',
            'monitoring_entry_reference',
        ]

        widgets = {
            'rationale': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 3,
                'placeholder': 'Explain the rationale for this budget allocation',
            }),
            'alignment_with_priorities': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 3,
                'placeholder': 'Describe alignment with strategic priorities',
            }),
            'expected_impact': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200',
                'rows': 3,
                'placeholder': 'Describe expected impact and outcomes',
            }),
            'needs_assessment_reference': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'monitoring_entry_reference': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
        }

        labels = {
            'rationale': 'Rationale',
            'alignment_with_priorities': 'Alignment with Priorities',
            'expected_impact': 'Expected Impact',
            'needs_assessment_reference': 'MANA Assessment Reference',
            'monitoring_entry_reference': 'M&E Entry Reference',
        }

        help_texts = {
            'needs_assessment_reference': 'Optional: Link to needs assessment',
            'monitoring_entry_reference': 'Optional: Link to monitoring entry',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mark required fields (references are optional)
        for field_name in ['rationale', 'alignment_with_priorities', 'expected_impact']:
            self.fields[field_name].required = True

        self.fields['needs_assessment_reference'].required = False
        self.fields['monitoring_entry_reference'].required = False

        # Add empty option for optional fields
        self.fields['needs_assessment_reference'].empty_label = 'None (optional)'
        self.fields['monitoring_entry_reference'].empty_label = 'None (optional)'
