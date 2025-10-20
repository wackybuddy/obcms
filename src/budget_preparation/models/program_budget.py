"""
Program Budget Model

Links approved BMMS programs (MonitoringEntry) to annual budget proposals.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class ProgramBudget(models.Model):
    """
    Budget allocation for a specific program within a budget proposal.

    Each record maps a MonitoringEntry (PPA) to the requesting organization and
    allows tracking of requested vs. approved amounts.
    """

    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    budget_proposal = models.ForeignKey(
        "BudgetProposal",
        on_delete=models.CASCADE,
        related_name="program_budgets",
        help_text="Parent budget proposal",
    )
    monitoring_entry = models.ForeignKey(
        "monitoring.MonitoringEntry",
        on_delete=models.PROTECT,
        related_name="program_budgets",
        help_text="Linked monitoring entry (PPA)",
        null=True,
        blank=True,
    )
    strategic_goal = models.ForeignKey(
        "planning.StrategicGoal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="program_budgets",
        help_text="Strategic goal supported by this budget",
    )
    annual_work_plan = models.ForeignKey(
        "planning.AnnualWorkPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="program_budgets",
        help_text="Annual work plan reference for this program",
    )
    requested_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Amount requested for this program (₱)",
    )
    approved_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Amount approved for this program (₱)",
    )
    justification = models.TextField(
        blank=True,
        help_text="Justification for the requested amount",
    )
    expected_outcomes = models.TextField(
        blank=True,
        help_text="Expected outcomes and beneficiaries",
    )
    priority_rank = models.PositiveIntegerField(
        default=1,
        help_text="Priority ranking within the proposal (1 = highest)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority_rank", "monitoring_entry__title"]
        verbose_name = "Program Budget"
        verbose_name_plural = "Program Budgets"
        unique_together = [["budget_proposal", "monitoring_entry"]]
        indexes = [
            models.Index(fields=["budget_proposal", "priority_rank"]),
            models.Index(fields=["monitoring_entry"]),
        ]

    def __str__(self) -> str:
        return f"{self.monitoring_entry.title} ({self.budget_proposal.fiscal_year})"

    # ------------------------------------------------------------------
    # Financial helpers
    # ------------------------------------------------------------------
    def line_items_total(self) -> Decimal:
        """Aggregate total cost of all line items."""
        return self.line_items.aggregate(total=Sum("total_cost"))["total"] or Decimal(
            "0.00"
        )

    def get_variance(self) -> Decimal | None:
        """
        Difference between approved and requested amounts.

        Returns None when the program has not been approved yet.
        """
        if self.approved_amount is None:
            return None
        return self.approved_amount - self.requested_amount

    def get_variance_percentage(self) -> Decimal | None:
        """
        Percentage variance relative to the requested amount.

        Returns None if approved_amount is not set or requested_amount is zero.
        """
        variance = self.get_variance()
        if variance is None or self.requested_amount == 0:
            return None
        return (variance / self.requested_amount * Decimal("100.00")).quantize(
            Decimal("0.01")
        )
