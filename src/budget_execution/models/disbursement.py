from decimal import Decimal
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Disbursement(models.Model):
    """
    Payment disbursement linked to an obligation.
    """

    PAYMENT_METHOD_CHOICES = [
        ("check", "Check"),
        ("bank_transfer", "Bank Transfer"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("paid", "Paid"),
        ("void", "Void"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    obligation = models.ForeignKey(
        "Obligation",
        on_delete=models.CASCADE,
        related_name="disbursements",
        help_text="Obligation this disbursement fulfills",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Amount disbursed (₱)",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="check",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing",
    )
    disbursed_by = models.ForeignKey(
        "common.User",
        on_delete=models.PROTECT,
        related_name="disbursements_processed",
        help_text="User who processed the disbursement",
        null=True,
        blank=True,
    )
    disbursed_at = models.DateField(
        default=timezone.now,
        help_text="Date the disbursement was made",
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional reference (check/voucher number)",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-disbursed_at"]
        verbose_name = "Disbursement"
        verbose_name_plural = "Disbursements"
        indexes = [
            models.Index(fields=["obligation"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_payment_method_display()} - ₱{self.amount:,.2f}"

    def clean(self) -> None:
        """Ensure disbursements do not exceed the obligation."""
        total_other = (
            self.obligation.disbursements.exclude(pk=self.pk).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        if total_other + self.amount > self.obligation.amount:
            raise ValidationError(
                f"Total disbursements (₱{total_other + self.amount:,.2f}) would exceed "
                f"obligation amount (₱{self.obligation.amount:,.2f})."
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
