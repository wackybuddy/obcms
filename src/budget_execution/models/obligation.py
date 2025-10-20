from decimal import Decimal
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Obligation(models.Model):
    """
    Obligation records (contracts, purchase orders) charged against an allotment.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("obligated", "Obligated"),
        ("partially_disbursed", "Partially Disbursed"),
        ("fully_disbursed", "Fully Disbursed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    allotment = models.ForeignKey(
        "Allotment",
        on_delete=models.CASCADE,
        related_name="obligations",
        help_text="Allotment funding this obligation",
    )
    work_item = models.ForeignKey(
        "WorkItem",
        on_delete=models.PROTECT,
        related_name="obligations",
        help_text="Execution work item covered by this obligation",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Obligated amount (₱)",
    )
    payee = models.CharField(
        max_length=255,
        help_text="Payee or supplier name",
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default="obligated",
        help_text="Obligation status",
    )
    obligated_by = models.ForeignKey(
        "common.User",
        on_delete=models.PROTECT,
        related_name="obligations_recorded",
        help_text="User who recorded the obligation",
    )
    obligated_at = models.DateField(
        default=timezone.now,
        help_text="Date the obligation was recorded",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional obligation notes",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-obligated_at"]
        verbose_name = "Obligation"
        verbose_name_plural = "Obligations"
        indexes = [
            models.Index(fields=["allotment", "status"]),
            models.Index(fields=["work_item"]),
        ]

    def __str__(self) -> str:
        return f"{self.payee} - ₱{self.amount:,.2f}"

    def clean(self) -> None:
        """Ensure obligations do not exceed the parent allotment."""
        total_other = (
            self.allotment.obligations.exclude(pk=self.pk).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        if total_other + self.amount > self.allotment.amount:
            raise ValidationError(
                f"Total obligations (₱{total_other + self.amount:,.2f}) would exceed "
                f"allotment amount (₱{self.allotment.amount:,.2f})."
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------
    def get_disbursed_amount(self) -> Decimal:
        """Return the total amount disbursed against this obligation."""
        return self.disbursements.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    def get_remaining_balance(self) -> Decimal:
        """Return the remaining amount available for disbursement."""
        return self.amount - self.get_disbursed_amount()
