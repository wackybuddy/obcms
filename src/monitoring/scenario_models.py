"""
Budget Scenario Planning Models for What-If Analysis and Optimization.

Part of Phase 6: Scenario Planning & Budget Optimization.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class BudgetScenario(models.Model):
    """
    Budget scenario for what-if analysis and comparative planning.

    Allows planners to create multiple budget allocation scenarios,
    compare outcomes, and optimize resource distribution.
    """

    SCENARIO_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented'),
        ('archived', 'Archived'),
    ]

    SCENARIO_TYPE_CHOICES = [
        ('baseline', 'Baseline (Current Budget)'),
        ('optimistic', 'Optimistic (Increased Budget)'),
        ('conservative', 'Conservative (Reduced Budget)'),
        ('needs_based', 'Needs-Based Allocation'),
        ('equity_focused', 'Equity-Focused'),
        ('custom', 'Custom Scenario'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic Information
    name = models.CharField(
        max_length=300,
        help_text="Scenario name (e.g., 'FY 2026 Baseline', 'Increased Education Focus')"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of this scenario's priorities and assumptions"
    )

    scenario_type = models.CharField(
        max_length=30,
        choices=SCENARIO_TYPE_CHOICES,
        default='custom',
        help_text="Type of scenario"
    )

    # Budget
    total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total budget available in this scenario"
    )

    allocated_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount allocated to PPAs (auto-calculated)"
    )

    # Baseline flag
    is_baseline = models.BooleanField(
        default=False,
        help_text="Mark as baseline scenario (only one baseline per fiscal year)"
    )

    # Planning Cycle Link
    planning_cycle = models.ForeignKey(
        'monitoring.AnnualPlanningCycle',
        on_delete=models.CASCADE,
        related_name='scenarios',
        null=True,
        blank=True,
        help_text="Associated annual planning cycle"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=SCENARIO_STATUS_CHOICES,
        default='draft',
        help_text="Current status of the scenario"
    )

    # Optimization Criteria (weights for multi-objective optimization)
    weight_needs_coverage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.40'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Weight for maximizing needs coverage (0.00-1.00)"
    )

    weight_equity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.30'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Weight for geographic/demographic equity (0.00-1.00)"
    )

    weight_strategic_alignment = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.30'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Weight for strategic goal alignment (0.00-1.00)"
    )

    # Optimization Results
    optimization_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Overall optimization score (higher is better)"
    )

    estimated_beneficiaries = models.PositiveIntegerField(
        default=0,
        help_text="Estimated number of beneficiaries under this scenario"
    )

    estimated_needs_addressed = models.PositiveIntegerField(
        default=0,
        help_text="Number of community needs addressed"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scenarios'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    notes = models.TextField(
        blank=True,
        help_text="Additional notes, assumptions, or context"
    )

    class Meta:
        verbose_name = "Budget Scenario"
        verbose_name_plural = "Budget Scenarios"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['planning_cycle', 'status']),
            models.Index(fields=['scenario_type']),
            models.Index(fields=['is_baseline']),
        ]

    def __str__(self):
        baseline_tag = " [BASELINE]" if self.is_baseline else ""
        return f"{self.name}{baseline_tag}"

    @property
    def budget_utilization_rate(self):
        """Calculate percentage of budget allocated."""
        if self.total_budget > 0:
            return (self.allocated_budget / self.total_budget) * 100
        return Decimal('0.00')

    @property
    def unallocated_budget(self):
        """Calculate remaining unallocated budget."""
        return self.total_budget - self.allocated_budget

    @property
    def is_fully_allocated(self):
        """Check if budget is fully allocated."""
        return self.allocated_budget >= self.total_budget

    @property
    def optimization_weights_sum(self):
        """Verify optimization weights sum to approximately 1.00."""
        return self.weight_needs_coverage + self.weight_equity + self.weight_strategic_alignment

    def recalculate_totals(self):
        """Recalculate allocated budget and metrics from allocations."""
        allocations = self.allocations.all()

        self.allocated_budget = sum(
            alloc.allocated_amount for alloc in allocations
        )

        self.estimated_beneficiaries = sum(
            alloc.ppa.target_beneficiaries or 0 for alloc in allocations
        )

        # Count distinct needs addressed across all PPAs
        needs_ids = set()
        for alloc in allocations:
            needs_ids.update(alloc.ppa.addresses_needs.values_list('id', flat=True))
        self.estimated_needs_addressed = len(needs_ids)

        self.save(update_fields=['allocated_budget', 'estimated_beneficiaries',
                                 'estimated_needs_addressed'])

    def save(self, *args, **kwargs):
        """Ensure only one baseline per planning cycle."""
        if self.is_baseline and self.planning_cycle:
            # Remove baseline flag from other scenarios in same cycle
            BudgetScenario.objects.filter(
                planning_cycle=self.planning_cycle,
                is_baseline=True
            ).exclude(pk=self.pk).update(is_baseline=False)

        super().save(*args, **kwargs)


class ScenarioAllocation(models.Model):
    """
    Budget allocation to a specific PPA within a scenario.

    Links scenarios to PPAs with specific funding amounts,
    allowing comparison of different allocation strategies.
    """

    ALLOCATION_STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending_review', 'Pending Review'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relationships
    scenario = models.ForeignKey(
        BudgetScenario,
        on_delete=models.CASCADE,
        related_name='allocations',
        help_text="Budget scenario"
    )

    ppa = models.ForeignKey(
        'monitoring.MonitoringEntry',
        on_delete=models.CASCADE,
        related_name='scenario_allocations',
        help_text="PPA (Program/Project/Activity) to fund"
    )

    # Allocation Details
    allocated_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount allocated to this PPA in this scenario"
    )

    priority_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Priority ranking within scenario (1=highest)"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=ALLOCATION_STATUS_CHOICES,
        default='proposed',
        help_text="Allocation status"
    )

    # Rationale
    allocation_rationale = models.TextField(
        blank=True,
        help_text="Justification for this allocation amount"
    )

    # Impact Metrics
    cost_per_beneficiary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost per beneficiary (auto-calculated)"
    )

    needs_coverage_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score based on number of needs addressed"
    )

    equity_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score based on equity considerations"
    )

    strategic_alignment_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score based on strategic goal alignment"
    )

    overall_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weighted overall score"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Scenario Allocation"
        verbose_name_plural = "Scenario Allocations"
        ordering = ['scenario', 'priority_rank', '-allocated_amount']
        unique_together = [['scenario', 'ppa']]
        indexes = [
            models.Index(fields=['scenario', 'status']),
            models.Index(fields=['priority_rank']),
            models.Index(fields=['-overall_score']),
        ]

    def __str__(self):
        return f"{self.scenario.name} → {self.ppa.title} (₱{self.allocated_amount:,.2f})"

    def calculate_metrics(self):
        """Calculate impact metrics for this allocation."""
        # Cost per beneficiary
        if self.ppa.target_beneficiaries and self.ppa.target_beneficiaries > 0:
            self.cost_per_beneficiary = self.allocated_amount / self.ppa.target_beneficiaries
        else:
            self.cost_per_beneficiary = None

        # Needs coverage score (more needs = higher score)
        needs_count = self.ppa.addresses_needs.count()
        self.needs_coverage_score = Decimal(str(needs_count * 10))  # 10 points per need

        # Equity score (based on underserved communities)
        # Simplified: if PPA covers multiple provinces/municipalities
        coverage_count = self.ppa.municipality_coverage.count() + self.ppa.province_coverage.count()
        self.equity_score = Decimal(str(coverage_count * 5))  # 5 points per coverage unit

        # Strategic alignment score
        strategic_goals_count = self.ppa.contributing_strategic_goals.count()
        self.strategic_alignment_score = Decimal(str(strategic_goals_count * 15))  # 15 points per goal

        # Overall weighted score
        weights = self.scenario
        self.overall_score = (
            (self.needs_coverage_score * weights.weight_needs_coverage) +
            (self.equity_score * weights.weight_equity) +
            (self.strategic_alignment_score * weights.weight_strategic_alignment)
        )

        self.save(update_fields=['cost_per_beneficiary', 'needs_coverage_score',
                                 'equity_score', 'strategic_alignment_score', 'overall_score'])

    def save(self, *args, **kwargs):
        """Update scenario totals on save."""
        super().save(*args, **kwargs)
        self.scenario.recalculate_totals()

    def delete(self, *args, **kwargs):
        """Update scenario totals on delete."""
        scenario = self.scenario
        super().delete(*args, **kwargs)
        scenario.recalculate_totals()


class CeilingManagement(models.Model):
    """Track planning ceilings by funding source and sector."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    fiscal_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2000)],
        help_text="Fiscal year for the ceiling",
    )
    funding_source = models.CharField(
        max_length=50,
        help_text="Funding source (e.g., BARMM Block Grant, GAA)",
    )
    sector = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional sector breakdown",
    )

    ceiling_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Ceiling amount for the funding source",
    )
    allocated_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Total allocated amount against the ceiling",
    )
    remaining_ceiling = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Remaining amount available under the ceiling",
    )
    threshold_warning = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.90"),
        validators=[MinValueValidator(Decimal("0.10"))],
        help_text="Trigger warning when allocation reaches this proportion of the ceiling",
    )
    is_exceeded = models.BooleanField(
        default=False,
        help_text="Flag when allocations exceed the ceiling",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional context or actions required",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ceiling Management Record"
        verbose_name_plural = "Ceiling Management Records"
        ordering = ["-fiscal_year", "funding_source", "sector"]
        indexes = [
            models.Index(fields=["fiscal_year", "funding_source"]),
            models.Index(fields=["funding_source", "sector"]),
        ]

    def __str__(self):
        sector_label = f" – {self.sector}" if self.sector else ""
        return f"{self.fiscal_year} {self.funding_source}{sector_label}"

    def recalculate(self):
        """Recompute remaining ceiling and threshold flag."""

        self.remaining_ceiling = self.ceiling_amount - self.allocated_amount
        self.is_exceeded = self.allocated_amount > self.ceiling_amount
        if self.ceiling_amount > 0:
            utilization = self.allocated_amount / self.ceiling_amount
            if utilization >= self.threshold_warning:
                self.is_exceeded = utilization >= 1
        self.save(update_fields=["remaining_ceiling", "is_exceeded"])
