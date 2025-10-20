from decimal import Decimal
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class WorkItem(models.Model):
    """
    Execution work item for a program budget.

    Represents a unit of work (project, activity, milestone) that receives funds
    through obligations and disbursements.
    """

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    monitoring_entry = models.ForeignKey(
        "monitoring.MonitoringEntry",
        on_delete=models.PROTECT,
        related_name="execution_work_items",
        help_text="Linked monitoring entry (PPA)",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    estimated_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"
        indexes = [
            models.Index(fields=["monitoring_entry"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        """Enforce validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------
    def total_obligations(self) -> Decimal:
        """Total obligated amount tied to this work item."""
        return self.obligations.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    def total_disbursements(self) -> Decimal:
        """Total disbursed amount tied to this work item."""
        from budget_execution.models import Disbursement

        return (
            Disbursement.objects.filter(obligation__work_item=self).aggregate(total=Sum("amount"))[
                "total"
            ]
            or Decimal("0.00")
        )


class DisbursementLineItem(models.Model):
    """
    Detailed breakdown of disbursement spending (formerly WorkItem).

    Retained for backward compatibility with legacy reports.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disbursement = models.ForeignKey(
        "Disbursement",
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    monitoring_entry = models.ForeignKey(
        "monitoring.MonitoringEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="disbursement_line_items",
    )
    cost_center = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "budget_execution_disbursement_line_item"
        ordering = ["-created_at"]
        verbose_name = "Disbursement Line Item"
        verbose_name_plural = "Disbursement Line Items"
        indexes = [
            models.Index(fields=["disbursement"]),
            models.Index(fields=["monitoring_entry"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=Decimal("0.01")),
                name="disbursement_line_item_positive_amount",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.description} - ₱{self.amount:,.2f}"
