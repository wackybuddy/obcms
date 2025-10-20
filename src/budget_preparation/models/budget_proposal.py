"""
Budget Proposal Model

Implements the budgeting foundation for BMMS Phase 1.
Aligns with integration tests that exercise multi-tenant budgeting workflows.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class BudgetProposal(models.Model):
    """
    Budget proposal submitted by a BMMS organization for a fiscal year.

    This model replaces the legacy coordination.Organization dependency with the
    BMMS multi-tenant organizations app. Each proposal is isolated per MOA and
    tracks both requested and approved budget amounts.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="budget_proposals",
        help_text="MOA submitting this budget proposal (BMMS multi-tenant organization)",
    )
    fiscal_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2024)],
        help_text="Fiscal year this budget proposal covers",
    )
    title = models.CharField(
        max_length=255,
        help_text="Budget proposal title",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Overview of budget proposal objectives and scope",
    )
    total_requested_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Total budget amount requested (₱)",
    )
    total_approved_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Total budget amount approved (₱)",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current review status of the proposal",
    )

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_budget_proposals",
        help_text="User who submitted this proposal",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the proposal was submitted",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_budget_proposals",
        help_text="Approving authority",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the proposal was approved",
    )
    approval_notes = models.TextField(
        blank=True,
        help_text="Approval or rejection notes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fiscal_year", "organization"]
        verbose_name = "Budget Proposal"
        verbose_name_plural = "Budget Proposals"
        unique_together = [["organization", "fiscal_year"]]
        indexes = [
            models.Index(fields=["organization", "fiscal_year"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        code = getattr(self.organization, "code", None) or self.organization.name
        return f"{code} - FY{self.fiscal_year}"

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def mark_submitted(self, user: User | None = None) -> None:
        """
        Transition the proposal to the submitted state.

        Parameters:
            user: Optional user performing the submission.
        """
        self.status = "submitted"
        self.submitted_at = timezone.now()
        if user is not None:
            self.submitted_by = user
        self.save(update_fields=["status", "submitted_at", "submitted_by", "updated_at"])

    def mark_approved(self, user: User | None = None, notes: str = "") -> None:
        """
        Transition the proposal to the approved state.

        Parameters:
            user: Optional approving user.
            notes: Approval notes recorded with the decision.
        """
        self.status = "approved"
        self.approved_at = timezone.now()
        self.approval_notes = notes
        if user is not None:
            self.approved_by = user
        self.save(
            update_fields=[
                "status",
                "approved_at",
                "approved_by",
                "approval_notes",
                "updated_at",
            ]
        )

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------
    @property
    def total_program_requested(self) -> Decimal:
        """Sum of requested amounts across related program budgets."""
        from django.db.models import Sum

        return (
            self.program_budgets.aggregate(total=Sum("requested_amount"))["total"]
            or Decimal("0.00")
        )

    @property
    def total_program_approved(self) -> Decimal:
        """Sum of approved amounts across related program budgets."""
        from django.db.models import Sum

        return (
            self.program_budgets.aggregate(total=Sum("approved_amount"))["total"]
            or Decimal("0.00")
        )

    # ------------------------------------------------------------------
    # Backwards compatibility aliases
    # ------------------------------------------------------------------
    @property
    def is_editable(self) -> bool:
        """
        Determine if the proposal can be modified.

        Draft and rejected proposals remain editable; submitted/approved
        proposals are locked for audit integrity.
        """
        return self.status in {"draft", "rejected"}

    @property
    def total_proposed_budget(self) -> Decimal:
        """Legacy alias for total_requested_budget (pre-BMMS naming)."""
        return self.total_requested_budget

    @total_proposed_budget.setter
    def total_proposed_budget(self, value: Decimal) -> None:
        self.total_requested_budget = value

    @property
    def reviewed_by(self):
        """Legacy alias mapping to approved_by."""
        return self.approved_by

    @reviewed_by.setter
    def reviewed_by(self, value) -> None:
        self.approved_by = value

    @property
    def reviewed_at(self):
        """Legacy alias mapping to approved_at."""
        return self.approved_at

    @reviewed_at.setter
    def reviewed_at(self, value) -> None:
        self.approved_at = value
