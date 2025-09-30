"""Success metrics tracking models for Regional MANA workshops.

As defined in the regional_mana_workshop_redesign_plan.md, we track:
- ≥90% of invited participants complete onboarding before Workshop 1
- ≥85% of participants submit responses for each workshop on schedule
- ≥40% reduction in facilitator review time via aggregation and AI synthesis
- Export generation succeeds in under 10 seconds for 100 responses
- Synthesis completes within 30 seconds average
- 100% of actions captured in audit logs
"""

from decimal import Decimal
from django.db import models
from django.utils import timezone

from .models import Assessment, WorkshopActivity, WorkshopParticipantAccount


class WorkshopMetricsSnapshot(models.Model):
    """Periodic snapshot of workshop metrics for tracking success criteria."""

    # Relations
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="metrics_snapshots",
        help_text="Assessment being measured",
    )

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="metrics_snapshots",
        null=True,
        blank=True,
        help_text="Specific workshop (null for assessment-wide metrics)",
    )

    # Snapshot metadata
    snapshot_date = models.DateTimeField(
        default=timezone.now, help_text="When this snapshot was taken"
    )

    metric_type = models.CharField(
        max_length=50,
        choices=[
            ("onboarding", "Onboarding Completion Rate"),
            ("submission", "On-Schedule Submission Rate"),
            ("review_time", "Facilitator Review Time"),
            ("export_performance", "Export Performance"),
            ("synthesis_performance", "Synthesis Performance"),
            ("audit_coverage", "Audit Log Coverage"),
        ],
        help_text="Type of metric",
    )

    # Metric values
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Target value for this metric (e.g., 90.00 for 90%)",
    )

    actual_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Actual measured value",
    )

    meets_target = models.BooleanField(
        default=False, help_text="Whether actual meets or exceeds target"
    )

    # Supporting data
    sample_size = models.IntegerField(
        null=True, blank=True, help_text="Number of items measured"
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context (timings, counts, breakdowns)",
    )

    notes = models.TextField(
        blank=True, help_text="Facilitator notes or observations"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-snapshot_date"]
        indexes = [
            models.Index(fields=["assessment", "metric_type", "-snapshot_date"]),
            models.Index(fields=["workshop", "metric_type"]),
        ]
        verbose_name = "Workshop Metrics Snapshot"
        verbose_name_plural = "Workshop Metrics Snapshots"

    def __str__(self):
        target_met = "✓" if self.meets_target else "✗"
        return f"{target_met} {self.get_metric_type_display()}: {self.actual_value}/{self.target_value} ({self.snapshot_date.date()})"

    def save(self, *args, **kwargs):
        """Auto-calculate meets_target on save."""
        self.meets_target = self.actual_value >= self.target_value
        super().save(*args, **kwargs)


class PerformanceLog(models.Model):
    """Log individual operation performance for metrics calculation."""

    # Operation metadata
    operation_type = models.CharField(
        max_length=50,
        choices=[
            ("export", "Export Generation"),
            ("synthesis", "AI Synthesis"),
            ("review", "Facilitator Review"),
        ],
        help_text="Type of operation",
    )

    # Relations
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="performance_logs",
        help_text="Related assessment",
    )

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="performance_logs",
        null=True,
        blank=True,
        help_text="Related workshop if applicable",
    )

    # Performance metrics
    start_time = models.DateTimeField(help_text="Operation start time")

    end_time = models.DateTimeField(
        null=True, blank=True, help_text="Operation end time"
    )

    duration_seconds = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Operation duration in seconds",
    )

    item_count = models.IntegerField(
        default=0, help_text="Number of items processed (responses, rows, etc.)"
    )

    success = models.BooleanField(default=True, help_text="Whether operation succeeded")

    # Additional context
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional details (format, filters, provider, etc.)",
    )

    error_message = models.TextField(
        blank=True, help_text="Error details if operation failed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["operation_type", "-start_time"]),
            models.Index(fields=["assessment", "success"]),
        ]
        verbose_name = "Performance Log"
        verbose_name_plural = "Performance Logs"

    def __str__(self):
        status = "✓" if self.success else "✗"
        duration = f"{self.duration_seconds}s" if self.duration_seconds else "—"
        return f"{status} {self.get_operation_type_display()}: {duration} ({self.item_count} items)"

    def save(self, *args, **kwargs):
        """Auto-calculate duration if end_time is set."""
        if self.end_time and self.start_time and not self.duration_seconds:
            delta = self.end_time - self.start_time
            self.duration_seconds = Decimal(str(delta.total_seconds()))
        super().save(*args, **kwargs)


class OnboardingTracker(models.Model):
    """Track onboarding completion for success metrics."""

    # Relations
    participant = models.OneToOneField(
        WorkshopParticipantAccount,
        on_delete=models.CASCADE,
        related_name="onboarding_tracker",
        help_text="Participant being tracked",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="onboarding_trackers",
        help_text="Assessment",
    )

    # Key timestamps
    invited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When participant was invited (account created)",
    )

    first_login_at = models.DateTimeField(
        null=True, blank=True, help_text="First successful login"
    )

    consent_given_at = models.DateTimeField(
        null=True, blank=True, help_text="When consent was given"
    )

    profile_completed_at = models.DateTimeField(
        null=True, blank=True, help_text="When profile was completed"
    )

    onboarding_completed_at = models.DateTimeField(
        null=True, blank=True, help_text="When fully onboarded"
    )

    # Workshop 1 deadline
    workshop_1_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When Workshop 1 starts (deadline for onboarding)",
    )

    # Status
    completed_before_deadline = models.BooleanField(
        default=False, help_text="Completed onboarding before Workshop 1"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["assessment", "completed_before_deadline"]),
        ]
        verbose_name = "Onboarding Tracker"
        verbose_name_plural = "Onboarding Trackers"

    def __str__(self):
        status = "✓" if self.completed_before_deadline else "✗"
        return f"{status} {self.participant.user.get_full_name()} onboarding"

    def update_completion_status(self):
        """Update onboarding completion status."""
        if (
            self.participant.consent_given
            and self.participant.profile_completed
            and not self.onboarding_completed_at
        ):
            self.onboarding_completed_at = timezone.now()

        if self.onboarding_completed_at and self.workshop_1_start:
            self.completed_before_deadline = (
                self.onboarding_completed_at <= self.workshop_1_start
            )

        self.save()