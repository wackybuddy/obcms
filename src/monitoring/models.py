"""Monitoring and Evaluation domain models."""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class MonitoringEntry(models.Model):
    """Track M&E records covering PPAs and community requests."""

    CATEGORY_CHOICES = [
        ("moa_ppa", "MOA Project / Program / Activity"),
        ("oobc_ppa", "OOBC Project / Program / Activity"),
        ("obc_request", "OBC Request or Proposal"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
    ]

    REQUEST_STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("clarification", "For Clarification"),
        ("endorsed", "Endorsed"),
        ("approved", "Approved"),
        ("in_progress", "In Implementation"),
        ("completed", "Completed"),
        ("deferred", "Deferred"),
        ("declined", "Declined"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Name of the project, activity, or request")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    summary = models.TextField(blank=True, help_text="Overview of objectives, beneficiaries, and scope")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Implementation status for PPAs",
    )
    request_status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        blank=True,
        help_text="Lifecycle state applicable to community requests",
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level for follow-ups and support",
    )
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall completion percentage",
    )
    lead_organization = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Primary implementing or receiving organization",
    )
    supporting_organizations = models.ManyToManyField(
        "coordination.Organization",
        blank=True,
        related_name="supporting_monitoring_entries",
        help_text="Supporting partner organizations",
    )
    implementing_moa = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="implemented_monitoring_entries",
        verbose_name="Implementing MOA",
        help_text="Primary MOA implementing the project",
    )
    oobc_unit = models.CharField(
        max_length=255,
        blank=True,
        help_text="OOBC unit or team responsible for follow-through",
    )
    submitted_by_community = models.ForeignKey(
        "communities.OBCCommunity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submitted_monitoring_entries",
        help_text="Origin OBC community for requests or proposals",
    )
    communities = models.ManyToManyField(
        "communities.OBCCommunity",
        blank=True,
        related_name="monitoring_entries",
        help_text="Targeted or benefiting OBC communities",
    )
    submitted_to_organization = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="received_monitoring_requests",
        help_text="Receiving MOA or office for requests",
    )
    related_assessment = models.ForeignKey(
        "mana.Assessment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Linked OBC-MANA assessment, if any",
    )
    related_event = models.ForeignKey(
        "coordination.Event",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Related coordination activity or event",
    )
    related_policy = models.ForeignKey(
        "policy_tracking.PolicyRecommendation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Policy recommendation informing this entry",
    )
    start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    next_milestone_date = models.DateField(null=True, blank=True)
    budget_allocation = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Budget allocation supporting the activity",
    )
    budget_currency = models.CharField(
        max_length=10,
        default="PHP",
        help_text="Currency of the recorded budget",
    )
    budget_obc_allocation = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Portion of the budget allocated specifically for OBCs",
    )
    total_slots = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total number of beneficiary slots",
    )
    obc_slots = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of slots reserved for OBCs",
    )
    coverage_region = models.ForeignKey(
        "common.Region",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Region covered by the PPA",
    )
    coverage_province = models.ForeignKey(
        "common.Province",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Province covered by the PPA",
    )
    coverage_municipality = models.ForeignKey(
        "common.Municipality",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Municipality covered by the PPA",
    )
    coverage_barangay = models.ForeignKey(
        "common.Barangay",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_entries",
        help_text="Barangay covered by the PPA",
    )
    outcome_indicators = models.TextField(
        blank=True, help_text="Key indicators and expected outcomes"
    )
    accomplishments = models.TextField(
        blank=True, help_text="Documented accomplishments and outputs"
    )
    challenges = models.TextField(
        blank=True, help_text="Challenges, risks, and mitigation notes"
    )
    support_required = models.TextField(
        blank=True, help_text="Support requested from OOBC or partners"
    )
    follow_up_actions = models.TextField(
        blank=True, help_text="Immediate next steps and focal assignments"
    )
    obcs_benefited = models.TextField(
        blank=True,
        help_text="Narrative describing OBC groups that have benefited",
    )
    last_status_update = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the most recent status update",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_monitoring_entries",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_monitoring_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        verbose_name = "Monitoring Entry"
        verbose_name_plural = "Monitoring Entries"

    def __str__(self):
        return self.title

    @property
    def is_request(self):
        """Convenience flag for request-specific handling."""

        return self.category == "obc_request"


class MonitoringUpdate(models.Model):
    """Log granular progress updates for a monitoring entry."""

    UPDATE_TYPES = [
        ("status", "Status Update"),
        ("progress", "Progress Update"),
        ("milestone", "Milestone"),
        ("communication", "Communication"),
        ("note", "General Note"),
    ]

    entry = models.ForeignKey(
        MonitoringEntry,
        on_delete=models.CASCADE,
        related_name="updates",
        help_text="Parent monitoring entry",
    )
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES, default="note")
    status = models.CharField(
        max_length=20,
        choices=MonitoringEntry.STATUS_CHOICES,
        blank=True,
        help_text="Updated PPA implementation status",
    )
    request_status = models.CharField(
        max_length=20,
        choices=MonitoringEntry.REQUEST_STATUS_CHOICES,
        blank=True,
        help_text="Updated request lifecycle state",
    )
    progress = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="New completion percentage",
    )
    notes = models.TextField(help_text="Narrative update or decisions recorded")
    next_steps = models.TextField(
        blank=True,
        help_text="Follow-up actions to undertake after this update",
    )
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date for the next follow-up or coordination",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monitoring_updates",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Monitoring Update"
        verbose_name_plural = "Monitoring Updates"

    def __str__(self):
        return f"Update for {self.entry.title} ({self.get_update_type_display()})"
