"""
Budget Builder Service

Service layer for building and validating budget proposals.
Implements transaction-wrapped operations for data integrity.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import BudgetProposal, ProgramBudget, BudgetLineItem, BudgetJustification


class BudgetBuilderService:
    """Service for building and validating budget proposals."""

    @transaction.atomic
    def create_proposal(self, organization, fiscal_year, title, description, user):
        """
        Create a new budget proposal.

        Args:
            organization: Organization (MOA) creating the proposal
            fiscal_year: Fiscal year (e.g., 2025)
            title: Proposal title
            description: Proposal description
            user: User creating the proposal

        Returns:
            BudgetProposal: Created proposal instance

        Raises:
            ValidationError: If proposal already exists for org/fiscal_year
        """
        # Check for existing proposal
        existing = BudgetProposal.objects.filter(
            organization=organization,
            fiscal_year=fiscal_year
        ).exists()

        if existing:
            raise ValidationError(
                f"Budget proposal already exists for {organization} FY {fiscal_year}"
            )

        proposal = BudgetProposal.objects.create(
            organization=organization,
            fiscal_year=fiscal_year,
            title=title,
            description=description,
            submitted_by=user,
            total_requested_budget=Decimal('0.00')
        )

        return proposal

    @transaction.atomic
    def add_program_budget(
        self,
        proposal,
        monitoring_entry,
        requested_amount,
        priority_rank,
        justification,
        expected_outcomes='',
        strategic_goal=None,
        annual_work_plan=None,
        approved_amount=None,
    ):
        """
        Add a program budget to a proposal.

        Args:
            proposal: BudgetProposal instance
            monitoring_entry: MonitoringEntry instance (linked PPA)
            requested_amount: Budget amount (Decimal or float)
            priority_rank: Integer priority order (1 = highest)
            justification: Justification text
            expected_outcomes: Expected outcomes text (optional)
            strategic_goal: Optional StrategicGoal instance
            annual_work_plan: Optional AnnualWorkPlan instance
            approved_amount: Optional approved budget amount

        Returns:
            ProgramBudget: Created program budget instance

        Raises:
            ValidationError: If validation fails
        """
        if not proposal.is_editable:
            raise ValidationError("Cannot modify submitted/approved proposals")

        # Check for duplicate program
        if ProgramBudget.objects.filter(
            budget_proposal=proposal,
            monitoring_entry=monitoring_entry,
        ).exists():
            raise ValidationError(
                f"Monitoring entry {monitoring_entry} already exists in this proposal"
            )

        program_budget = ProgramBudget.objects.create(
            budget_proposal=proposal,
            monitoring_entry=monitoring_entry,
            requested_amount=Decimal(str(requested_amount)),
            approved_amount=Decimal(str(approved_amount)) if approved_amount else None,
            strategic_goal=strategic_goal,
            annual_work_plan=annual_work_plan,
            priority_rank=priority_rank,
            justification=justification,
            expected_outcomes=expected_outcomes
            or f"Expected outcomes for {monitoring_entry.title}"
        )

        # Update proposal total
        self._update_proposal_total(proposal)

        return program_budget

    @transaction.atomic
    def add_line_item(self, program_budget, category, description, unit_cost, quantity, notes=''):
        """
        Add a line item to a program budget.

        Args:
            program_budget: ProgramBudget instance
            category: 'personnel', 'operating', or 'capital'
            description: Item description
            unit_cost: Cost per unit (Decimal or float)
            quantity: Number of units (int)
            notes: Additional notes (optional)

        Returns:
            BudgetLineItem: Created line item instance
        """
        if not program_budget.budget_proposal.is_editable:
            raise ValidationError("Cannot modify submitted/approved proposals")

        line_item = BudgetLineItem.objects.create(
            program_budget=program_budget,
            category=category,
            description=description,
            unit_cost=Decimal(str(unit_cost)),
            quantity=quantity,
            notes=notes
        )
        # total_cost is auto-calculated in save() method

        return line_item

    @transaction.atomic
    def submit_proposal(self, proposal, user):
        """
        Submit proposal for review.

        Args:
            proposal: BudgetProposal instance
            user: User submitting the proposal

        Raises:
            ValidationError: If proposal validation fails
        """
        # Validate completeness
        validation_errors = self.validate_proposal(proposal)
        if validation_errors:
            raise ValidationError(validation_errors)

        # Submit
        proposal.mark_submitted(user)

        return proposal

    def validate_proposal(self, proposal):
        """
        Validate budget proposal completeness.

        Args:
            proposal: BudgetProposal instance

        Returns:
            dict: Dictionary of validation errors (empty if valid)
        """
        errors = {}

        # Check if proposal has program budgets
        program_budgets = proposal.program_budgets.all()
        if not program_budgets.exists():
            errors['program_budgets'] = "Proposal must have at least one program budget"

        # Check each program budget has line items
        for pb in program_budgets:
            if not pb.line_items.exists():
                errors[f'program_{pb.id}'] = (
                    f"Program '{pb.monitoring_entry.title}' must have budget line items"
                )

            # Check line items total matches requested amount
            line_items_total = pb.line_items_total()
            requested = pb.requested_amount
            variance = abs(line_items_total - requested)

            if variance > Decimal('0.01'):  # Allow 1 cent tolerance
                errors[f'program_{pb.id}_variance'] = (
                    f"Program '{pb.monitoring_entry.title}': Line items total (₱{line_items_total:,.2f}) "
                    f"does not match requested amount (₱{requested:,.2f})"
                )

        # Check proposal total matches sum of program budgets
        program_total = proposal.total_program_requested
        proposal_total = proposal.total_requested_budget
        variance = abs(program_total - proposal_total)

        if variance > Decimal('0.01'):
            errors['total_variance'] = (
                f"Proposal total (₱{proposal_total:,.2f}) does not match "
                f"sum of program budgets (₱{program_total:,.2f})"
            )

        return errors

    def _update_proposal_total(self, proposal):
        """Update proposal total from program budgets."""
        requested_total = proposal.total_program_requested
        approved_total = proposal.total_program_approved
        proposal.total_proposed_budget = requested_total
        proposal.total_approved_budget = approved_total or proposal.total_approved_budget
        proposal.save(
            update_fields=['total_requested_budget', 'total_approved_budget', 'updated_at']
        )

    @transaction.atomic
    def add_justification(self, program_budget, rationale, alignment, expected_impact,
                         needs_assessment=None, monitoring_entry=None):
        """
        Add evidence-based justification to a program budget.

        Args:
            program_budget: ProgramBudget instance
            rationale: Rationale text
            alignment: Alignment with priorities text
            expected_impact: Expected impact text
            needs_assessment: Optional Assessment FK
            monitoring_entry: Optional MonitoringEntry FK

        Returns:
            BudgetJustification: Created justification instance
        """
        justification = BudgetJustification.objects.create(
            program_budget=program_budget,
            rationale=rationale,
            alignment_with_priorities=alignment,
            expected_impact=expected_impact,
            needs_assessment_reference=needs_assessment,
            monitoring_entry_reference=monitoring_entry
        )

        return justification
