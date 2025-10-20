from decimal import Decimal
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Allotment(models.Model):
    """
    Quarterly budget allotments released from an approved ProgramBudget.
    """

    QUARTER_CHOICES = [
        ("Q1", "Q1 (Jan–Mar)"),
        ("Q2", "Q2 (Apr–Jun)"),
        ("Q3", "Q3 (Jul–Sep)"),
        ("Q4", "Q4 (Oct–Dec)"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("released", "Released"),
        ("partially_utilized", "Partially Utilized"),
        ("fully_utilized", "Fully Utilized"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_budget = models.ForeignKey(
        "budget_preparation.ProgramBudget",
        on_delete=models.CASCADE,
        related_name="allotments",
        help_text="Program budget this allotment is released from",
    )
    quarter = models.CharField(
        max_length=2,
        choices=QUARTER_CHOICES,
        help_text="Quarter identifier (Q1–Q4)",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Allotment amount (₱)",
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Allotment release status",
    )
    released_by = models.ForeignKey(
        "common.User",
        on_delete=models.PROTECT,
        related_name="allotments_released",
        help_text="Budget execution user who released the allotment",
    )
    released_at = models.DateField(
        default=timezone.now,
        help_text="Date the allotment was released",
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional release notes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["program_budget", "quarter"]
        verbose_name = "Allotment"
        verbose_name_plural = "Allotments"
        unique_together = [["program_budget", "quarter"]]
        indexes = [
            models.Index(fields=["program_budget", "status"]),
            models.Index(fields=["quarter"]),
        ]

    def __str__(self) -> str:
        return f"{self.program_budget} - {self.get_quarter_display()} (₱{self.amount:,.2f})"

    def clean(self) -> None:
        """
        Ensure the total released allotments do not exceed the approved program budget.
        """
        approved_amount = self.program_budget.approved_amount
        if approved_amount is None:
            # Allow allotments even if approval not yet recorded to support draft flows.
            return

        total_other = (
            self.program_budget.allotments.exclude(pk=self.pk).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        if total_other + self.amount > approved_amount:
            raise ValidationError(
                f"Total allotments (₱{total_other + self.amount:,.2f}) would exceed "
                f"the approved program budget (₱{approved_amount:,.2f})."
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------
    def get_obligated_amount(self) -> Decimal:
        """Return total obligations charged against this allotment."""
        return self.obligations.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    def get_remaining_balance(self) -> Decimal:
        """Return remaining balance after obligations."""
        return self.amount - self.get_obligated_amount()
