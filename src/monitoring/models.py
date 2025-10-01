"""Monitoring and Evaluation domain models."""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

ZERO_DECIMAL = Decimal("0.00")


class MonitoringEntry(models.Model):
    """Track M&E records covering PPAs and community requests."""

    CATEGORY_CHOICES = [
        ("moa_ppa", "MOA Project / Program / Activity"),
        ("oobc_ppa", "OOBC Project / Program / Activity"),
        ("obc_request", "OBC Request or Proposal"),
    ]

    APPROPRIATION_CLASS_PS = "ps"
    APPROPRIATION_CLASS_MOOE = "mooe"
    APPROPRIATION_CLASS_CO = "co"
    APPROPRIATION_CLASS_CHOICES = [
        (APPROPRIATION_CLASS_PS, "Personnel Services"),
        (APPROPRIATION_CLASS_MOOE, "Maintenance and Other Operating Expenses"),
        (APPROPRIATION_CLASS_CO, "Capital Outlay"),
    ]

    FUNDING_SOURCE_GAA = "gaa"
    FUNDING_SOURCE_BLOCK_GRANT = "block_grant"
    FUNDING_SOURCE_LGU = "lgu_counterpart"
    FUNDING_SOURCE_DONOR = "donor"
    FUNDING_SOURCE_INTERNAL = "internal"
    FUNDING_SOURCE_OTHERS = "others"
    FUNDING_SOURCE_CHOICES = [
        (FUNDING_SOURCE_GAA, "General Appropriations Act"),
        (FUNDING_SOURCE_BLOCK_GRANT, "BARMM Block Grant"),
        (FUNDING_SOURCE_LGU, "LGU Counterpart"),
        (FUNDING_SOURCE_DONOR, "Donor / Development Partner"),
        (FUNDING_SOURCE_INTERNAL, "OOBC / BARMM Internal"),
        (FUNDING_SOURCE_OTHERS, "Others"),
    ]

    SECTOR_ECONOMIC = "economic"
    SECTOR_SOCIAL = "social"
    SECTOR_INFRASTRUCTURE = "infrastructure"
    SECTOR_ENVIRONMENT = "environment"
    SECTOR_GOVERNANCE = "governance"
    SECTOR_PEACE = "peace_security"
    SECTOR_CHOICES = [
        (SECTOR_ECONOMIC, "Economic Development"),
        (SECTOR_SOCIAL, "Social Development"),
        (SECTOR_INFRASTRUCTURE, "Infrastructure"),
        (SECTOR_ENVIRONMENT, "Environment & DRRM"),
        (SECTOR_GOVERNANCE, "Governance & Institution Building"),
        (SECTOR_PEACE, "Peace, Security & Reconciliation"),
    ]

    COST_EFFECTIVENESS_CHOICES = [
        ("very_high", "Very High"),
        ("high", "High"),
        ("moderate", "Moderate"),
        ("low", "Low"),
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
        help_text="Policy recommendation informing this entry (DEPRECATED: use implementing_policies instead)",
    )

    # ==========================================
    # PHASE 1 INTEGRATION: NEEDS & POLICY LINKAGE
    # (Added for evidence-based budgeting)
    # ==========================================

    # MANY-TO-MANY: Multiple needs can be addressed by one PPA
    needs_addressed = models.ManyToManyField(
        "mana.Need",
        blank=True,
        related_name="implementing_ppas",
        help_text="Community needs this PPA addresses",
    )

    # MANY-TO-MANY: One PPA can implement multiple policies
    implementing_policies = models.ManyToManyField(
        "policy_tracking.PolicyRecommendation",
        blank=True,
        related_name="implementing_ppas",
        help_text="Policy recommendations this PPA implements",
    )

    plan_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        help_text="Planning reference year (e.g., AIP year)",
    )
    fiscal_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        help_text="Fiscal year the budget is intended for",
    )
    sector = models.CharField(
        max_length=32,
        choices=SECTOR_CHOICES,
        blank=True,
        help_text="Primary sector alignment for the PPA",
    )
    appropriation_class = models.CharField(
        max_length=8,
        choices=APPROPRIATION_CLASS_CHOICES,
        blank=True,
        help_text="Appropriation class (PS/MOOE/CO)",
    )
    funding_source = models.CharField(
        max_length=32,
        choices=FUNDING_SOURCE_CHOICES,
        blank=True,
        help_text="Primary funding source",
    )
    funding_source_other = models.CharField(
        max_length=255,
        blank=True,
        help_text="Specify funding source when tagged as Others",
    )
    program_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="DBM/BARMM program or objective code",
    )
    plan_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference to PDP/PIP/AIP or local investment plan",
    )
    goal_alignment = models.JSONField(
        default=list,
        blank=True,
        help_text="List of strategic alignment tags (e.g., PDP, SDG, Moral Governance)",
    )
    moral_governance_pillar = models.CharField(
        max_length=100,
        blank=True,
        help_text="Key Moral Governance pillar supported",
    )
    compliance_gad = models.BooleanField(
        default=False,
        help_text="Flag if expenditure is tagged under GAD",
    )
    compliance_ccet = models.BooleanField(
        default=False,
        help_text="Flag if expenditure is tagged under Climate Change Expenditure",
    )
    benefits_indigenous_peoples = models.BooleanField(
        default=False,
        help_text="Flag if initiative primarily benefits Indigenous Peoples communities",
    )
    supports_peace_agenda = models.BooleanField(
        default=False,
        help_text="Flag if initiative supports peacebuilding or security agenda",
    )
    supports_sdg = models.BooleanField(
        default=False,
        help_text="Flag if initiative contributes to SDG tracking",
    )
    budget_ceiling = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ceiling allocated for budgeting scenarios",
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
    cost_per_beneficiary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Computed or reported cost per beneficiary",
    )
    cost_effectiveness_rating = models.CharField(
        max_length=12,
        choices=COST_EFFECTIVENESS_CHOICES,
        blank=True,
        help_text="Qualitative cost-effectiveness rating",
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
    outcome_framework = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured outcome framework including outputs, outcomes, and impacts",
    )
    outcome_indicators = models.TextField(
        blank=True,
        help_text="Legacy narrative field for outcome indicators (to be migrated to outcome framework)",
    )
    standard_outcome_indicators = models.ManyToManyField(
        "monitoring.OutcomeIndicator",
        blank=True,
        related_name="monitoring_entries",
        help_text="Standard outcome indicators referenced by this entry",
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

    def funding_total(self, tranche_type: str) -> float:
        """Return total amount recorded for a funding tranche type."""

        return (
            self.funding_flows.filter(tranche_type=tranche_type)
            .aggregate(total=models.Sum("amount"))
            .get("total")
            or 0
        )

    @property
    def is_request(self) -> bool:
        """Convenience flag identifying OBC requests."""

        return self.category == "obc_request"

    @property
    def total_allocations(self) -> Decimal:
        """Total allocation tranches recorded."""
        return Decimal(str(self.funding_total(MonitoringEntryFunding.TRANCHE_ALLOCATION)))

    @property
    def total_obligations(self) -> Decimal:
        """Total obligation tranches recorded."""
        return Decimal(str(self.funding_total(MonitoringEntryFunding.TRANCHE_OBLIGATION)))

    @property
    def total_disbursements(self) -> Decimal:
        """Total disbursement tranches recorded."""
        return Decimal(str(self.funding_total(MonitoringEntryFunding.TRANCHE_DISBURSEMENT)))

    @property
    def allocation_variance(self) -> Decimal:
        """Variance between budget allocation and recorded allocation tranches."""
        budget = self.budget_allocation or ZERO_DECIMAL
        actual = self.total_allocations
        return actual - budget

    @property
    def allocation_variance_pct(self) -> float:
        """Percentage variance for allocations."""
        budget = self.budget_allocation or ZERO_DECIMAL
        if budget == 0:
            return 0.0
        variance = self.allocation_variance
        return float((variance / budget) * 100)

    @property
    def obligation_rate(self) -> float:
        """Obligation rate as percentage of allocations."""
        allocations = self.total_allocations
        if allocations == 0:
            return 0.0
        obligations = self.total_obligations
        return float((obligations / allocations) * 100)

    @property
    def disbursement_rate(self) -> float:
        """Disbursement rate as percentage of obligations."""
        obligations = self.total_obligations
        if obligations == 0:
            return 0.0
        disbursements = self.total_disbursements
        return float((disbursements / obligations) * 100)

    @property
    def budget_utilization_rate(self) -> float:
        """Overall budget utilization (disbursements vs budget allocation)."""
        budget = self.budget_allocation or ZERO_DECIMAL
        if budget == 0:
            return 0.0
        disbursements = self.total_disbursements
        return float((disbursements / budget) * 100)

    @property
    def is_over_budget(self) -> bool:
        """Flag if allocations exceed budget."""
        return self.allocation_variance > 0

    @property
    def is_under_obligated(self) -> bool:
        """Flag if obligation rate is below 75%."""
        return self.obligation_rate < 75.0


class OutcomeIndicator(models.Model):
    """Catalogue of standard outcome indicators for PPAs."""

    CATEGORY_CHOICES = [
        ("education", "Education"),
        ("health", "Health"),
        ("livelihood", "Livelihood"),
        ("governance", "Governance"),
        ("infrastructure", "Infrastructure"),
        ("social_protection", "Social Protection"),
        ("environment", "Environment"),
        ("peace_security", "Peace & Security"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(
        max_length=64,
        choices=CATEGORY_CHOICES,
        help_text="Domain classification for the indicator",
    )
    indicator_name = models.CharField(
        max_length=255,
        help_text="Name of the indicator",
    )
    definition = models.TextField(
        help_text="How the indicator is defined and interpreted",
    )
    measurement_method = models.TextField(
        blank=True,
        help_text="Methodology for measuring the indicator",
    )
    data_source = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary data source (e.g., survey, administrative records)",
    )
    frequency = models.CharField(
        max_length=100,
        blank=True,
        help_text="Collection frequency (e.g., quarterly, annual)",
    )
    unit_of_measure = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unit of measure (e.g., percent, households)",
    )
    related_sdg = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional SDG reference",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the indicator is available for selection",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "indicator_name"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["indicator_name"]),
        ]

    def __str__(self):
        return f"{self.indicator_name}"


class MonitoringEntryFunding(models.Model):
    """Track detailed allocations, obligations, and disbursements per entry."""

    TRANCHE_ALLOCATION = "allocation"
    TRANCHE_OBLIGATION = "obligation"
    TRANCHE_DISBURSEMENT = "disbursement"
    TRANCHE_ADJUSTMENT = "adjustment"
    TRANCHE_CHOICES = [
        (TRANCHE_ALLOCATION, "Allocation"),
        (TRANCHE_OBLIGATION, "Obligation"),
        (TRANCHE_DISBURSEMENT, "Disbursement"),
        (TRANCHE_ADJUSTMENT, "Adjustment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry = models.ForeignKey(
        MonitoringEntry,
        related_name="funding_flows",
        on_delete=models.CASCADE,
    )
    tranche_type = models.CharField(max_length=20, choices=TRANCHE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    funding_source = models.CharField(
        max_length=32,
        choices=MonitoringEntry.FUNDING_SOURCE_CHOICES,
        blank=True,
        help_text="Override funding source for this tranche",
    )
    funding_source_other = models.CharField(
        max_length=255,
        blank=True,
        help_text="Specify the funding source when using Others",
    )
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        help_text="When the tranche is scheduled or recorded",
    )
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_funding_flows",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_funding_flows",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "-created_at"]
        verbose_name = "Funding Flow"
        verbose_name_plural = "Funding Flows"

    def __str__(self):
        return f"{self.get_tranche_type_display()} - {self.amount}"


class MonitoringEntryWorkflowStage(models.Model):
    """Represent budget workflow milestones per monitoring entry."""

    STAGE_BUDGET_CALL = "budget_call"
    STAGE_FORMULATION = "formulation"
    STAGE_TECHNICAL = "technical_hearing"
    STAGE_LEGISLATION = "legislation"
    STAGE_EXECUTION = "execution"
    STAGE_ACCOUNTABILITY = "accountability"
    STAGE_CHOICES = [
        (STAGE_BUDGET_CALL, "Budget Call"),
        (STAGE_FORMULATION, "Formulation"),
        (STAGE_TECHNICAL, "Technical Budget Hearing"),
        (STAGE_LEGISLATION, "Budget Legislation"),
        (STAGE_EXECUTION, "Program Execution"),
        (STAGE_ACCOUNTABILITY, "Accountability"),
    ]

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_BLOCKED = "blocked"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not Started"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_BLOCKED, "Blocked"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry = models.ForeignKey(
        MonitoringEntry,
        related_name="workflow_stages",
        on_delete=models.CASCADE,
    )
    stage = models.CharField(max_length=40, choices=STAGE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
    )
    owner_team = models.ForeignKey(
        "common.StaffTeam",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="budget_workflow_stages",
    )
    owner_organization = models.ForeignKey(
        "coordination.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="budget_workflow_stages",
    )
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_budget_workflow_stages",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("entry", "stage")
        ordering = ["entry", "stage"]
        verbose_name = "Budget Workflow Stage"
        verbose_name_plural = "Budget Workflow Stages"

    def __str__(self):
        return f"{self.entry.title} - {self.get_stage_display()}"

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


class MonitoringEntryWorkflowDocument(models.Model):
    """Store documents and attachments for budget workflow stages."""

    DOCUMENT_TYPE_BUDGET_CALL = "budget_call"
    DOCUMENT_TYPE_SUBMISSION = "submission"
    DOCUMENT_TYPE_HEARING_NOTES = "hearing_notes"
    DOCUMENT_TYPE_APPROVAL = "approval"
    DOCUMENT_TYPE_AIP_FORM = "aip_form"
    DOCUMENT_TYPE_SUPPORTING = "supporting"
    DOCUMENT_TYPE_OTHER = "other"
    DOCUMENT_TYPE_CHOICES = [
        (DOCUMENT_TYPE_BUDGET_CALL, "Budget Call Memorandum"),
        (DOCUMENT_TYPE_SUBMISSION, "Submission Form"),
        (DOCUMENT_TYPE_HEARING_NOTES, "Technical Hearing Notes"),
        (DOCUMENT_TYPE_APPROVAL, "Approval Letter"),
        (DOCUMENT_TYPE_AIP_FORM, "AIP Form / Template"),
        (DOCUMENT_TYPE_SUPPORTING, "Supporting Document"),
        (DOCUMENT_TYPE_OTHER, "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_stage = models.ForeignKey(
        MonitoringEntryWorkflowStage,
        related_name="documents",
        on_delete=models.CASCADE,
        help_text="Parent workflow stage",
    )
    title = models.CharField(
        max_length=255,
        help_text="Document title or description",
    )
    document_type = models.CharField(
        max_length=32,
        choices=DOCUMENT_TYPE_CHOICES,
        default=DOCUMENT_TYPE_SUPPORTING,
        help_text="Type of document for categorization",
    )
    file = models.FileField(
        upload_to="monitoring/workflow_documents/%Y/%m/",
        help_text="Upload document file (PDF, Word, Excel, etc.)",
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes (auto-populated)",
    )
    description = models.TextField(
        blank=True,
        help_text="Additional notes or context for this document",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_workflow_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Workflow Document"
        verbose_name_plural = "Workflow Documents"

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    def save(self, *args, **kwargs):
        """Auto-populate file size before saving."""
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class MonitoringEntryTaskAssignment(models.Model):
    """Track task assignments for collaborative PPA management."""

    ROLE_LEAD = "lead"
    ROLE_CONTRIBUTOR = "contributor"
    ROLE_REVIEWER = "reviewer"
    ROLE_APPROVER = "approver"
    ROLE_MONITOR = "monitor"
    ROLE_CHOICES = [
        (ROLE_LEAD, "Lead / Primary Responsible"),
        (ROLE_CONTRIBUTOR, "Contributor / Supporting"),
        (ROLE_REVIEWER, "Reviewer / Quality Check"),
        (ROLE_APPROVER, "Approver / Decision Maker"),
        (ROLE_MONITOR, "Monitor / Observer"),
    ]

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_BLOCKED = "blocked"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending / Not Started"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_BLOCKED, "Blocked / Needs Input"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry = models.ForeignKey(
        MonitoringEntry,
        related_name="task_assignments",
        on_delete=models.CASCADE,
        help_text="Parent monitoring entry / PPA",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="monitoring_task_assignments",
        on_delete=models.CASCADE,
        help_text="Staff member assigned to this task",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CONTRIBUTOR,
        help_text="Role in this assignment",
    )
    task_title = models.CharField(
        max_length=255,
        help_text="Specific task or responsibility",
    )
    task_description = models.TextField(
        blank=True,
        help_text="Detailed instructions or context",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Current status of this assignment",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expected completion date",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual completion timestamp",
    )
    priority = models.CharField(
        max_length=10,
        choices=MonitoringEntry.PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level for this task",
    )
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated effort in hours",
    )
    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual effort expended",
    )
    notes = models.TextField(
        blank=True,
        help_text="Progress notes or blockers",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_monitoring_tasks",
        help_text="Who created this assignment",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "-priority", "-created_at"]
        verbose_name = "Task Assignment"
        verbose_name_plural = "Task Assignments"
        indexes = [
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["entry", "role"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"{self.task_title} → {self.assigned_to.get_full_name() or self.assigned_to.username}"

    @property
    def is_overdue(self) -> bool:
        """Check if task is past due date and not completed."""
        if not self.due_date or self.status == self.STATUS_COMPLETED:
            return False
        from django.utils import timezone
        return timezone.now().date() > self.due_date

    @property
    def days_until_due(self) -> int:
        """Days until due date (negative if overdue)."""
        if not self.due_date:
            return 999
        from django.utils import timezone
        delta = self.due_date - timezone.now().date()
        return delta.days


# Import strategic planning models
from .strategic_models import StrategicGoal, AnnualPlanningCycle

# Import scenario planning models
from .scenario_models import BudgetScenario, ScenarioAllocation, CeilingManagement
