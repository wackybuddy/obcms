import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class ServiceOffering(models.Model):
    """
    Service catalog - programs and services offered by MAOs to OBCs.

    Part of Phase 3 implementation for service delivery tracking.
    Enables MAOs to publish their services and OBCs to discover/apply.
    """

    SERVICE_TYPES = [
        ("financial", "Financial Assistance"),
        ("training", "Training & Capacity Building"),
        ("livelihood", "Livelihood Program"),
        ("education", "Educational Support"),
        ("health", "Health Services"),
        ("infrastructure", "Infrastructure Support"),
        ("legal", "Legal Assistance"),
        ("social", "Social Services"),
        ("technical", "Technical Assistance"),
        ("other", "Other Services"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active - Accepting Applications"),
        ("paused", "Paused - Temporarily Closed"),
        ("closed", "Closed - No Longer Available"),
        ("archived", "Archived"),
    ]

    ELIGIBILITY_LEVELS = [
        ("individual", "Individual Beneficiaries"),
        ("household", "Household Level"),
        ("community", "Community/Barangay Level"),
        ("organization", "Organization/Cooperative"),
        ("lgu", "LGU Partnership"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, help_text="Service/Program name")

    service_type = models.CharField(
        max_length=20, choices=SERVICE_TYPES, help_text="Type of service"
    )

    description = models.TextField(help_text="Detailed description of the service")

    objectives = models.TextField(
        blank=True, help_text="Objectives and expected outcomes"
    )

    # Offering Organization
    offering_mao = models.ForeignKey(
        "coordination.Organization",
        on_delete=models.CASCADE,
        related_name="service_offerings",
        limit_choices_to={"organization_type": "bmoa"},
        help_text="MAO offering this service",
    )

    focal_person = models.ForeignKey(
        "coordination.MAOFocalPerson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_services",
        help_text="MAO focal person managing this service",
    )

    # Eligibility
    eligibility_level = models.CharField(
        max_length=15,
        choices=ELIGIBILITY_LEVELS,
        help_text="Who can apply for this service",
    )

    eligibility_criteria = models.TextField(
        help_text="Detailed eligibility requirements"
    )

    required_documents = models.TextField(
        blank=True, help_text="List of required documents for application"
    )

    # Funding & Capacity
    budget_allocated = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total budget allocated for this service",
    )

    budget_utilized = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Amount already utilized",
    )

    total_slots = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total number of beneficiary slots (if applicable)",
    )

    slots_filled = models.PositiveIntegerField(
        default=0, help_text="Number of slots already filled"
    )

    # Timeline
    application_start_date = models.DateField(
        null=True, blank=True, help_text="When applications open"
    )

    application_deadline = models.DateField(
        null=True, blank=True, help_text="Application deadline"
    )

    service_start_date = models.DateField(
        null=True, blank=True, help_text="When service delivery begins"
    )

    service_end_date = models.DateField(
        null=True, blank=True, help_text="Expected service completion date"
    )

    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of this service offering",
    )

    # Application Process
    application_process = models.TextField(
        blank=True, help_text="Step-by-step application process"
    )

    contact_information = models.TextField(
        blank=True, help_text="How to contact for inquiries"
    )

    # Linkage to Budget
    linked_ppas = models.ManyToManyField(
        "monitoring.MonitoringEntry",
        blank=True,
        related_name="service_offerings",
        help_text="PPAs funding this service",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_services",
        help_text="User who created this service offering",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Service Offering"
        verbose_name_plural = "Service Offerings"
        indexes = [
            models.Index(fields=["offering_mao", "status"]),
            models.Index(fields=["service_type", "status"]),
            models.Index(fields=["application_deadline"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.offering_mao.acronym or self.offering_mao.name}"

    @property
    def is_accepting_applications(self):
        """Check if currently accepting applications."""
        if self.status != "active":
            return False
        if not self.application_start_date or not self.application_deadline:
            return True  # Always open if no dates set
        today = timezone.now().date()
        return self.application_start_date <= today <= self.application_deadline

    @property
    def budget_utilization_rate(self):
        """Calculate budget utilization percentage."""
        if not self.budget_allocated or self.budget_allocated == 0:
            return 0
        return (self.budget_utilized / self.budget_allocated) * 100

    @property
    def slots_utilization_rate(self):
        """Calculate slots utilization percentage."""
        if not self.total_slots or self.total_slots == 0:
            return 0
        return (self.slots_filled / self.total_slots) * 100


class ServiceApplication(models.Model):
    """
    Applications from OBCs for services offered by MAOs.

    Part of Phase 3 implementation for service delivery tracking.
    """

    APPLICATION_STATUS = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("additional_info_required", "Additional Information Required"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("waitlisted", "Waitlisted"),
        ("in_progress", "Service Being Delivered"),
        ("completed", "Service Completed"),
        ("cancelled", "Cancelled"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    service = models.ForeignKey(
        ServiceOffering,
        on_delete=models.CASCADE,
        related_name="applications",
        help_text="Service being applied for",
    )

    # Applicant Information
    applicant_community = models.ForeignKey(
        "communities.OBCCommunity",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="service_applications",
        help_text="OBC community applying (for community-level services)",
    )

    applicant_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submitted_service_applications",
        help_text="User who submitted the application",
    )

    applicant_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Applicant name (for individual/household applications)",
    )

    applicant_contact = models.CharField(
        max_length=100, blank=True, help_text="Contact information"
    )

    # Application Details
    application_details = models.TextField(
        help_text="Detailed application narrative/justification"
    )

    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount requested (if applicable)",
    )

    beneficiary_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of beneficiaries (if applicable)",
    )

    # Status Tracking
    status = models.CharField(
        max_length=30,
        choices=APPLICATION_STATUS,
        default="draft",
        help_text="Current application status",
    )

    submission_date = models.DateTimeField(
        null=True, blank=True, help_text="When application was submitted"
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
        help_text="MAO staff who reviewed",
    )

    review_date = models.DateTimeField(
        null=True, blank=True, help_text="When application was reviewed"
    )

    review_notes = models.TextField(blank=True, help_text="Review comments and notes")

    approval_date = models.DateTimeField(
        null=True, blank=True, help_text="When application was approved"
    )

    rejection_reason = models.TextField(
        blank=True, help_text="Reason for rejection (if applicable)"
    )

    # Service Delivery Tracking
    service_start_date = models.DateField(
        null=True, blank=True, help_text="When service delivery started"
    )

    service_completion_date = models.DateField(
        null=True, blank=True, help_text="When service was completed"
    )

    actual_amount_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual amount received/disbursed",
    )

    # Feedback
    satisfaction_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Satisfaction rating (1-5 stars)",
    )

    feedback = models.TextField(blank=True, help_text="Applicant feedback")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submission_date", "-created_at"]
        verbose_name = "Service Application"
        verbose_name_plural = "Service Applications"
        indexes = [
            models.Index(fields=["service", "status"]),
            models.Index(fields=["applicant_community", "status"]),
            models.Index(fields=["applicant_user", "status"]),
            models.Index(fields=["submission_date"]),
        ]

    def __str__(self):
        applicant = (
            self.applicant_name
            or str(self.applicant_community)
            or self.applicant_user.username
        )
        return f"{self.service.title} - {applicant}"

    @property
    def processing_time_days(self):
        """Calculate processing time in days."""
        if not self.submission_date:
            return None
        end_date = self.review_date or timezone.now()
        delta = end_date - self.submission_date
        return delta.days
