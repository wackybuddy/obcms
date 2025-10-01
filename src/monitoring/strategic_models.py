"""
Strategic Planning Models for Multi-Year Goal Tracking and Annual Planning Cycles.

Part of Phase 5: Strategic Planning Integration.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class StrategicGoal(models.Model):
    """
    Long-term strategic goals (typically 3-5 years) that guide annual planning.
    
    Strategic goals align with regional development plans and national frameworks.
    PPAs and policies are linked to show how they contribute to achieving these goals.
    """
    
    GOAL_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('achieved', 'Achieved'),
        ('revised', 'Revised'),
        ('discontinued', 'Discontinued'),
    ]
    
    PRIORITY_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    title = models.CharField(
        max_length=500,
        help_text="Strategic goal title (e.g., 'Achieve 100% access to quality education for Bangsamoro communities')"
    )
    
    description = models.TextField(
        help_text="Detailed description of the strategic goal and its importance"
    )
    
    goal_statement = models.TextField(
        blank=True,
        help_text="SMART goal statement (Specific, Measurable, Achievable, Relevant, Time-bound)"
    )
    
    # Categorization
    sector = models.CharField(
        max_length=100,
        choices=[
            ('education', 'Education'),
            ('health', 'Health'),
            ('livelihood', 'Livelihood & Economic Development'),
            ('infrastructure', 'Infrastructure'),
            ('governance', 'Governance & Institutional Development'),
            ('social_protection', 'Social Protection'),
            ('cultural', 'Cultural Development'),
            ('peace', 'Peace & Security'),
            ('environment', 'Environment & Natural Resources'),
        ],
        help_text="Primary sector this goal addresses"
    )
    
    priority_level = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='medium',
        help_text="Priority level of this strategic goal"
    )
    
    # Alignment
    aligns_with_rdp = models.BooleanField(
        default=False,
        verbose_name="Aligns with Regional Development Plan",
        help_text="Check if this goal aligns with the Regional Development Plan"
    )
    
    rdp_reference = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="RDP Reference",
        help_text="Reference to specific RDP section/chapter (e.g., 'Chapter 3.2: Education')"
    )
    
    aligns_with_national_framework = models.BooleanField(
        default=False,
        help_text="Check if aligned with national development framework (e.g., Philippine Development Plan)"
    )
    
    # Timeline
    start_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2050)],
        help_text="Year this goal period starts"
    )
    
    target_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2050)],
        help_text="Year this goal should be achieved"
    )
    
    # Targets & Indicators
    target_outcome = models.TextField(
        blank=True,
        help_text="Specific, measurable outcome expected by target year"
    )
    
    baseline_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Baseline value/indicator at start (e.g., current enrollment rate: 65%)"
    )
    
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target value/indicator at completion (e.g., target enrollment rate: 100%)"
    )
    
    unit_of_measure = models.CharField(
        max_length=100,
        blank=True,
        help_text="Unit of measurement (e.g., '% of population', 'number of beneficiaries')"
    )
    
    # Budget
    estimated_total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated total budget needed to achieve this goal"
    )
    
    # Relationships
    lead_agency = models.ForeignKey(
        'coordination.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_strategic_goals',
        limit_choices_to={'organization_type__in': ['oobc', 'bmoa']},
        help_text="Lead agency responsible for this strategic goal"
    )
    
    supporting_agencies = models.ManyToManyField(
        'coordination.Organization',
        blank=True,
        related_name='supported_strategic_goals',
        help_text="Supporting agencies/partners"
    )
    
    linked_ppas = models.ManyToManyField(
        'monitoring.MonitoringEntry',
        blank=True,
        related_name='contributing_strategic_goals',
        help_text="PPAs that contribute to achieving this goal"
    )
    
    linked_policies = models.ManyToManyField(
        'policy_tracking.PolicyRecommendation',
        blank=True,
        related_name='supporting_strategic_goals',
        help_text="Policy recommendations that support this goal"
    )
    
    # Status & Progress
    status = models.CharField(
        max_length=20,
        choices=GOAL_STATUS_CHOICES,
        default='draft',
        help_text="Current status of the strategic goal"
    )
    
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall progress towards achieving this goal (0-100%)"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_strategic_goals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Strategic Goal"
        verbose_name_plural = "Strategic Goals"
        ordering = ['-priority_level', 'target_year', 'title']
        indexes = [
            models.Index(fields=['sector', 'status']),
            models.Index(fields=['target_year', 'status']),
            models.Index(fields=['priority_level', 'status']),
            models.Index(fields=['start_year', 'target_year']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.start_year}-{self.target_year})"
    
    @property
    def duration_years(self):
        """Calculate duration of the goal period."""
        return self.target_year - self.start_year
    
    @property
    def is_active(self):
        """Check if goal is currently active."""
        from django.utils import timezone
        current_year = timezone.now().year
        return (
            self.status == 'active' and
            self.start_year <= current_year <= self.target_year
        )
    
    @property
    def achievement_rate(self):
        """Calculate achievement rate based on baseline and current progress."""
        if self.baseline_value is not None and self.target_value is not None:
            if self.target_value == self.baseline_value:
                return 100.0 if self.status == 'achieved' else 0.0
            
            # This would need current value from monitoring
            # For now, use progress_percentage as proxy
            return float(self.progress_percentage)
        return float(self.progress_percentage)


class AnnualPlanningCycle(models.Model):
    """
    Annual planning and budgeting cycle tracking.
    
    Links strategic goals to annual PPAs and budget allocations.
    Tracks planning milestones, budget approval, and execution.
    """
    
    CYCLE_STATUS_CHOICES = [
        ('planning', 'Planning Phase'),
        ('budget_preparation', 'Budget Preparation'),
        ('budget_approval', 'Budget Approval'),
        ('execution', 'Execution'),
        ('monitoring', 'Monitoring & Evaluation'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Fiscal Year
    fiscal_year = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(2020), MaxValueValidator(2050)],
        help_text="Fiscal year for this planning cycle (e.g., 2026)"
    )
    
    cycle_name = models.CharField(
        max_length=200,
        help_text="Name of the planning cycle (e.g., 'FY 2026 Annual Investment Plan')"
    )
    
    # Timeline
    planning_start_date = models.DateField(
        help_text="Date when planning activities begin"
    )
    
    planning_end_date = models.DateField(
        help_text="Deadline for completing planning"
    )
    
    budget_submission_date = models.DateField(
        help_text="Date when budget proposals are due"
    )
    
    budget_approval_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when budget was approved"
    )
    
    execution_start_date = models.DateField(
        help_text="Date when execution/implementation begins (usually Jan 1)"
    )
    
    execution_end_date = models.DateField(
        help_text="Date when fiscal year ends (usually Dec 31)"
    )
    
    # Budget
    total_budget_envelope = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total budget available for this fiscal year"
    )
    
    allocated_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total budget allocated to PPAs"
    )
    
    # Strategic Alignment
    strategic_goals = models.ManyToManyField(
        StrategicGoal,
        blank=True,
        related_name='annual_cycles',
        help_text="Strategic goals addressed in this annual cycle"
    )
    
    # PPAs
    monitoring_entries = models.ManyToManyField(
        'monitoring.MonitoringEntry',
        blank=True,
        related_name='planning_cycles',
        help_text="PPAs included in this annual cycle"
    )
    
    # Needs
    needs_addressed = models.ManyToManyField(
        'mana.Need',
        blank=True,
        related_name='planning_cycles',
        help_text="Community needs addressed in this cycle"
    )
    
    # Status
    status = models.CharField(
        max_length=30,
        choices=CYCLE_STATUS_CHOICES,
        default='planning',
        help_text="Current phase of the planning cycle"
    )
    
    # Documentation
    plan_document_url = models.URLField(
        blank=True,
        help_text="Link to the annual plan document"
    )
    
    budget_document_url = models.URLField(
        blank=True,
        help_text="Link to the approved budget document"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes, decisions, or context for this planning cycle"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_planning_cycles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Annual Planning Cycle"
        verbose_name_plural = "Annual Planning Cycles"
        ordering = ['-fiscal_year']
        indexes = [
            models.Index(fields=['-fiscal_year']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"FY {self.fiscal_year} - {self.cycle_name}"
    
    @property
    def budget_utilization_rate(self):
        """Calculate budget utilization rate."""
        if self.total_budget_envelope and self.total_budget_envelope > 0:
            return (self.allocated_budget / self.total_budget_envelope) * 100
        return 0.0
    
    @property
    def is_current_cycle(self):
        """Check if this is the current fiscal year cycle."""
        from django.utils import timezone
        current_year = timezone.now().year
        return self.fiscal_year == current_year
    
    @property
    def days_until_budget_submission(self):
        """Calculate days until budget submission deadline."""
        from django.utils import timezone
        today = timezone.now().date()
        if today <= self.budget_submission_date:
            return (self.budget_submission_date - today).days
        return 0
