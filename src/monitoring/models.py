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
