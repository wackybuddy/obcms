import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from communities.models import OBCCommunity

User = get_user_model()


class AssessmentCategory(models.Model):
    """Categories for different types of assessments."""

    CATEGORY_TYPES = [
        ("needs_assessment", "Needs Assessment"),
        ("baseline_study", "Baseline Study"),
        ("impact_assessment", "Impact Assessment"),
        ("situational_analysis", "Situational Analysis"),
        ("community_mapping", "Community Mapping"),
    ]

    name = models.CharField(
        max_length=100, unique=True, help_text="Name of the assessment category"
    )

    category_type = models.CharField(
        max_length=50, choices=CATEGORY_TYPES, help_text="Type of assessment category"
    )

    description = models.TextField(
        blank=True, help_text="Description of the assessment category"
    )

    icon = models.CharField(
        max_length=50, blank=True, help_text="CSS icon class for this category"
    )

    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Color code for this category (hex format)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this category is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Assessment Categories"

    def __str__(self):
        return self.name


class Assessment(models.Model):
    """Core model for managing mapping and needs assessments."""

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("preparation", "Preparation"),
        ("data_collection", "Data Collection"),
        ("analysis", "Analysis"),
        ("reporting", "Reporting"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    ASSESSMENT_LEVELS = [
        ("regional", "Regional Level"),
        ("provincial", "Provincial Level"),
        ("city_municipal", "City/Municipal Level"),
        ("barangay", "Barangay Level"),
        ("community", "Community Level"),
    ]

    ASSESSMENT_METHODOLOGIES = [
        ("desk_review", "Desk Review/Research"),
        ("survey", "Survey"),
        ("kii", "Key Informant Interview (KII)"),
        ("workshop", "FGD/Workshops"),
        ("participatory", "Participatory Assessment"),
        ("observation", "Direct Observation"),
        ("mixed", "Mixed Methods"),
        ("other", "Other Methodologies"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=200, help_text="Title of the assessment")

    category = models.ForeignKey(
        AssessmentCategory, on_delete=models.PROTECT, help_text="Category of assessment"
    )

    description = models.TextField(help_text="Detailed description of the assessment")

    objectives = models.TextField(help_text="Objectives and goals of the assessment")

    # Assessment level and methodology
    assessment_level = models.CharField(
        max_length=20,
        choices=ASSESSMENT_LEVELS,
        default="community",
        help_text="Level at which the assessment is conducted",
    )

    primary_methodology = models.CharField(
        max_length=20,
        choices=ASSESSMENT_METHODOLOGIES,
        default="survey",
        help_text="Primary methodology used in the assessment",
    )

    secondary_methodologies = models.JSONField(
        null=True, blank=True, help_text="List of secondary methodologies used"
    )

    # Community and Location
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="assessments",
        help_text="Community being assessed",
    )

    location_details = models.TextField(
        blank=True, help_text="Additional location details and coverage area"
    )

    # Assessment Management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Current status of the assessment",
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level of the assessment",
    )

    # Timeline
    planned_start_date = models.DateField(
        help_text="Planned start date for the assessment"
    )

    planned_end_date = models.DateField(
        help_text="Planned completion date for the assessment"
    )

    actual_start_date = models.DateField(
        null=True, blank=True, help_text="Actual start date of the assessment"
    )

    actual_end_date = models.DateField(
        null=True, blank=True, help_text="Actual completion date of the assessment"
    )

    # Team and Stakeholders
    lead_assessor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="led_assessments",
        help_text="Lead person responsible for the assessment",
    )

    team_members = models.ManyToManyField(
        User,
        through="AssessmentTeamMember",
        related_name="assessment_teams",
        blank=True,
        help_text="Team members involved in the assessment",
    )

    # Budget and Resources
    estimated_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated budget for the assessment",
    )

    actual_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual budget spent on the assessment",
    )

    # Results and Impact
    key_findings = models.TextField(
        blank=True, help_text="Key findings from the assessment"
    )

    recommendations = models.TextField(
        blank=True, help_text="Recommendations based on assessment results"
    )

    impact_level = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        null=True,
        blank=True,
        help_text="Level of impact identified",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_assessments",
        help_text="User who created this assessment",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Completion tracking
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Completion percentage (0-100)",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["community", "status"]),
            models.Index(fields=["category", "priority"]),
            models.Index(fields=["planned_start_date", "planned_end_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.community.barangay.name}"

    def clean(self):
        if self.planned_end_date and self.planned_start_date:
            if self.planned_end_date < self.planned_start_date:
                raise ValidationError(
                    "Planned end date cannot be earlier than start date"
                )

        if self.actual_end_date and self.actual_start_date:
            if self.actual_end_date < self.actual_start_date:
                raise ValidationError(
                    "Actual end date cannot be earlier than start date"
                )

    @property
    def duration_days(self):
        """Calculate planned duration in days."""
        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days
        return None

    @property
    def is_overdue(self):
        """Check if assessment is overdue."""
        if self.status not in ["completed", "cancelled"] and self.planned_end_date:
            return timezone.now().date() > self.planned_end_date
        return False


class AssessmentTeamMember(models.Model):
    """Through model for assessment team members with roles."""

    ROLE_CHOICES = [
        ("team_leader", "Team Leader/Executive Director"),
        ("deputy_leader", "Deputy Team Leader/DMO IV"),
        ("facilitator", "Facilitator (DMO/CDO)"),
        ("documenter", "Documenter"),
        ("info_analyst", "Information System Analyst"),
        ("secretariat", "Secretariat/Admin Support"),
        ("data_collector", "Data Collector"),
        ("technical_expert", "Technical Expert"),
        ("observer", "Observer"),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="Role of the team member in this assessment",
    )

    assigned_date = models.DateField(
        default=timezone.now, help_text="Date when assigned to the assessment"
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this team member is currently active"
    )

    notes = models.TextField(
        blank=True, help_text="Additional notes about this team member's involvement"
    )

    class Meta:
        unique_together = ["assessment", "user", "role"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} ({self.assessment.title})"


class Survey(models.Model):
    """Model for managing surveys within assessments."""

    SURVEY_TYPES = [
        ("household", "Household Survey"),
        ("community_leader", "Community Leader Interview"),
        ("focus_group", "Focus Group Discussion"),
        ("key_informant", "Key Informant Interview"),
        ("observation", "Direct Observation"),
        ("document_review", "Document Review"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="surveys",
        help_text="Assessment this survey belongs to",
    )

    title = models.CharField(max_length=150, help_text="Title of the survey")

    survey_type = models.CharField(
        max_length=20, choices=SURVEY_TYPES, help_text="Type of survey"
    )

    description = models.TextField(help_text="Description of the survey")

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of the survey",
    )

    target_respondents = models.IntegerField(help_text="Target number of respondents")

    actual_respondents = models.IntegerField(
        default=0, help_text="Actual number of respondents"
    )

    # Timeline
    start_date = models.DateField(help_text="Survey start date")

    end_date = models.DateField(help_text="Survey end date")

    # Survey Configuration
    questions_count = models.IntegerField(
        default=0, help_text="Number of questions in the survey"
    )

    estimated_duration_minutes = models.IntegerField(
        help_text="Estimated duration to complete survey (in minutes)"
    )

    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who created this survey"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["assessment", "title"]

    def __str__(self):
        return f"{self.title} ({self.assessment.title})"

    @property
    def completion_rate(self):
        """Calculate completion rate as percentage."""
        if self.target_respondents > 0:
            return (self.actual_respondents / self.target_respondents) * 100
        return 0

    @property
    def is_complete(self):
        """Check if survey has reached target respondents."""
        return self.actual_respondents >= self.target_respondents


class SurveyQuestion(models.Model):
    """Model for survey questions."""

    QUESTION_TYPES = [
        ("text", "Text Response"),
        ("number", "Numeric Response"),
        ("single_choice", "Single Choice"),
        ("multiple_choice", "Multiple Choice"),
        ("scale", "Rating Scale"),
        ("yes_no", "Yes/No"),
        ("date", "Date"),
        ("location", "Geographic Location"),
    ]

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="Survey this question belongs to",
    )

    question_text = models.TextField(help_text="The question text")

    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, help_text="Type of question"
    )

    order = models.IntegerField(help_text="Order of the question in the survey")

    is_required = models.BooleanField(
        default=False, help_text="Whether this question is required"
    )

    choices = models.JSONField(
        null=True,
        blank=True,
        help_text="Choices for single/multiple choice questions (JSON format)",
    )

    scale_min = models.IntegerField(
        null=True, blank=True, help_text="Minimum value for scale questions"
    )

    scale_max = models.IntegerField(
        null=True, blank=True, help_text="Maximum value for scale questions"
    )

    help_text = models.TextField(
        blank=True, help_text="Additional help text for respondents"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["survey", "order"]
        unique_together = ["survey", "order"]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class SurveyResponse(models.Model):
    """Model for survey responses."""

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="responses",
        help_text="Survey this response belongs to",
    )

    respondent_name = models.CharField(
        max_length=100, blank=True, help_text="Name of the respondent (optional)"
    )

    respondent_contact = models.CharField(
        max_length=50,
        blank=True,
        help_text="Contact information of respondent (optional)",
    )

    demographic_info = models.JSONField(
        null=True, blank=True, help_text="Demographic information (JSON format)"
    )

    responses = models.JSONField(help_text="Survey responses (JSON format)")

    # Collection metadata
    collected_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who collected this response"
    )

    collection_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time when response was collected"
    )

    collection_location = models.CharField(
        max_length=200, blank=True, help_text="Location where response was collected"
    )

    # Quality control
    is_validated = models.BooleanField(
        default=False, help_text="Whether this response has been validated"
    )

    validation_notes = models.TextField(
        blank=True, help_text="Notes from validation process"
    )

    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_responses",
        help_text="User who validated this response",
    )

    validation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when response was validated"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-collection_date"]

    def __str__(self):
        return f"Response to {self.survey.title} - {self.collection_date.strftime('%Y-%m-%d')}"


class MappingActivity(models.Model):
    """Model for community mapping activities."""

    MAPPING_TYPES = [
        ("resource_mapping", "Resource Mapping"),
        ("infrastructure_mapping", "Infrastructure Mapping"),
        ("hazard_mapping", "Hazard and Risk Mapping"),
        ("social_mapping", "Social Mapping"),
        ("economic_mapping", "Economic Activity Mapping"),
        ("cultural_mapping", "Cultural Site Mapping"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("review", "Under Review"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="mapping_activities",
        help_text="Assessment this mapping activity belongs to",
    )

    title = models.CharField(max_length=150, help_text="Title of the mapping activity")

    mapping_type = models.CharField(
        max_length=25, choices=MAPPING_TYPES, help_text="Type of mapping activity"
    )

    description = models.TextField(help_text="Description of the mapping activity")

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Current status of the mapping activity",
    )

    # Geographic coverage
    coverage_area = models.TextField(
        help_text="Description of the geographic area covered"
    )

    coordinates = models.JSONField(
        null=True, blank=True, help_text="Geographic coordinates (GeoJSON format)"
    )

    # Timeline
    start_date = models.DateField(help_text="Start date of mapping activity")

    end_date = models.DateField(help_text="End date of mapping activity")

    # Team and methodology
    mapping_team = models.ManyToManyField(
        User,
        related_name="mapping_activities",
        help_text="Team members involved in mapping",
    )

    methodology = models.TextField(help_text="Methodology used for mapping")

    tools_used = models.TextField(
        blank=True, help_text="Tools and equipment used for mapping"
    )

    # Results
    findings = models.TextField(
        blank=True, help_text="Key findings from the mapping activity"
    )

    map_outputs = models.JSONField(
        null=True, blank=True, help_text="References to map outputs and visualizations"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="User who created this mapping activity",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["assessment", "start_date"]
        verbose_name_plural = "Mapping Activities"

    def __str__(self):
        return f"{self.title} ({self.assessment.title})"


class NeedsCategory(models.Model):
    """Categories for different types of community needs."""

    SECTOR_TYPES = [
        ("education", "Education"),
        ("economic_development", "Economic Development"),
        ("social_development", "Social Development"),
        ("cultural_development", "Cultural Development"),
        ("infrastructure", "Infrastructure"),
        ("health", "Health"),
        ("governance", "Governance"),
        ("environment", "Environment"),
        ("security", "Peace and Security"),
    ]

    name = models.CharField(
        max_length=100, unique=True, help_text="Name of the needs category"
    )

    sector = models.CharField(
        max_length=25,
        choices=SECTOR_TYPES,
        help_text="Development sector this category belongs to",
    )

    description = models.TextField(help_text="Description of this needs category")

    icon = models.CharField(
        max_length=50, blank=True, help_text="CSS icon class for this category"
    )

    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Color code for this category (hex format)",
    )

    weight_factor = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        help_text="Weight factor for prioritization (0.1 to 2.0)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this category is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sector", "name"]
        verbose_name_plural = "Needs Categories"

    def __str__(self):
        return f"{self.name} ({self.get_sector_display()})"


class Need(models.Model):
    """Individual community needs identified through assessments."""

    URGENCY_LEVELS = [
        ("immediate", "Immediate (Within 1 month)"),
        ("short_term", "Short-term (1-6 months)"),
        ("medium_term", "Medium-term (6-12 months)"),
        ("long_term", "Long-term (1+ years)"),
    ]

    FEASIBILITY_LEVELS = [
        ("very_low", "Very Low"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("very_high", "Very High"),
    ]

    STATUS_CHOICES = [
        ("identified", "Identified"),
        ("validated", "Validated"),
        ("prioritized", "Prioritized"),
        ("planned", "Planned for Implementation"),
        ("in_progress", "Implementation in Progress"),
        ("completed", "Completed"),
        ("deferred", "Deferred"),
        ("rejected", "Rejected"),
    ]

    # Basic Information
    title = models.CharField(
        max_length=200, help_text="Title/name of the identified need"
    )

    description = models.TextField(help_text="Detailed description of the need")

    category = models.ForeignKey(
        NeedsCategory,
        on_delete=models.PROTECT,
        related_name="needs",
        help_text="Category this need belongs to",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="identified_needs",
        help_text="Assessment that identified this need",
    )

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="community_needs",
        help_text="Community that has this need",
    )

    # Impact and Scope
    affected_population = models.IntegerField(
        help_text="Number of people affected by this need"
    )

    affected_households = models.IntegerField(
        null=True, blank=True, help_text="Number of households affected"
    )

    geographic_scope = models.TextField(help_text="Geographic scope/area affected")

    # Prioritization Factors
    urgency_level = models.CharField(
        max_length=15, choices=URGENCY_LEVELS, help_text="How urgent is this need"
    )

    impact_severity = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Impact severity on community (1=Low, 5=High)",
    )

    feasibility = models.CharField(
        max_length=10,
        choices=FEASIBILITY_LEVELS,
        help_text="Feasibility of addressing this need",
    )

    estimated_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated cost to address this need",
    )

    # Status and Progress
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="identified",
        help_text="Current status of this need",
    )

    priority_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calculated priority score",
    )

    priority_rank = models.IntegerField(
        null=True, blank=True, help_text="Priority ranking within community"
    )

    # Validation and Evidence
    evidence_sources = models.TextField(help_text="Sources of evidence for this need")

    validation_method = models.CharField(
        max_length=100, blank=True, help_text="Method used to validate this need"
    )

    is_validated = models.BooleanField(
        default=False, help_text="Whether this need has been validated"
    )

    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_needs",
        help_text="User who validated this need",
    )

    validation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when need was validated"
    )

    # Metadata
    identified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="identified_needs",
        help_text="User who identified this need",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority_score", "-impact_severity", "title"]
        indexes = [
            models.Index(fields=["community", "category"]),
            models.Index(fields=["status", "priority_score"]),
            models.Index(fields=["urgency_level", "impact_severity"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.community.barangay.name}"

    def calculate_priority_score(self):
        """Calculate priority score based on various factors."""
        # Base score factors
        urgency_weights = {
            "immediate": 4.0,
            "short_term": 3.0,
            "medium_term": 2.0,
            "long_term": 1.0,
        }

        feasibility_weights = {
            "very_high": 2.0,
            "high": 1.5,
            "medium": 1.0,
            "low": 0.5,
            "very_low": 0.25,
        }

        # Calculate base score
        urgency_weight = urgency_weights.get(self.urgency_level, 1.0)
        impact_weight = self.impact_severity / 5.0 * 2.0  # Normalize to 0-2
        feasibility_weight = feasibility_weights.get(self.feasibility, 1.0)

        # Population impact factor
        population_factor = min(self.affected_population / 1000, 2.0)  # Cap at 2.0

        # Category weight factor
        category_weight = float(self.category.weight_factor) if self.category else 1.0

        # Calculate final score
        base_score = (
            urgency_weight + impact_weight + feasibility_weight + population_factor
        ) / 4
        final_score = base_score * category_weight

        return round(final_score, 2)

    def save(self, *args, **kwargs):
        """Override save to calculate priority score."""
        self.priority_score = self.calculate_priority_score()
        super().save(*args, **kwargs)


class NeedsPrioritization(models.Model):
    """Model for tracking needs prioritization exercises."""

    PRIORITIZATION_METHODS = [
        ("scoring_matrix", "Scoring Matrix"),
        ("pairwise_comparison", "Pairwise Comparison"),
        ("ranking", "Simple Ranking"),
        ("mca", "Multi-Criteria Analysis"),
        ("community_voting", "Community Voting"),
        ("expert_panel", "Expert Panel Review"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(
        max_length=200, help_text="Title of the prioritization exercise"
    )

    description = models.TextField(
        help_text="Description of the prioritization exercise"
    )

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="prioritization_exercises",
        help_text="Community for which needs are being prioritized",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="prioritization_exercises",
        help_text="Assessment this prioritization belongs to",
    )

    method = models.CharField(
        max_length=20,
        choices=PRIORITIZATION_METHODS,
        help_text="Method used for prioritization",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Status of the prioritization exercise",
    )

    # Participants
    facilitators = models.ManyToManyField(
        User,
        related_name="facilitated_prioritizations",
        help_text="Users who facilitated this prioritization",
    )

    participant_count = models.IntegerField(
        help_text="Number of community participants"
    )

    stakeholder_groups = models.TextField(
        help_text="Description of stakeholder groups involved"
    )

    # Timeline
    start_date = models.DateField(help_text="Start date of prioritization exercise")

    end_date = models.DateField(help_text="End date of prioritization exercise")

    # Criteria and Results
    prioritization_criteria = models.JSONField(
        help_text="Criteria used for prioritization (JSON format)"
    )

    results = models.JSONField(
        null=True, blank=True, help_text="Prioritization results (JSON format)"
    )

    top_priorities = models.TextField(
        blank=True, help_text="Summary of top priority needs identified"
    )

    recommendations = models.TextField(
        blank=True, help_text="Recommendations based on prioritization"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_prioritizations",
        help_text="User who created this prioritization",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} - {self.community.barangay.name}"


class NeedsPrioritizationItem(models.Model):
    """Individual items in a prioritization exercise."""

    prioritization = models.ForeignKey(
        NeedsPrioritization,
        on_delete=models.CASCADE,
        related_name="prioritization_items",
        help_text="Prioritization exercise this item belongs to",
    )

    need = models.ForeignKey(
        Need,
        on_delete=models.CASCADE,
        related_name="prioritization_items",
        help_text="Need being prioritized",
    )

    rank = models.IntegerField(help_text="Rank assigned in this prioritization")

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score assigned in this prioritization",
    )

    criteria_scores = models.JSONField(
        null=True, blank=True, help_text="Scores for individual criteria (JSON format)"
    )

    justification = models.TextField(
        blank=True, help_text="Justification for the ranking/scoring"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["prioritization", "rank"]
        unique_together = ["prioritization", "need"]

    def __str__(self):
        return f"Rank {self.rank}: {self.need.title}"


class GeographicDataLayer(models.Model):
    """Model for managing geographic data layers for mapping and visualization."""

    LAYER_TYPES = [
        ("point", "Point Data"),
        ("line", "Line/Route Data"),
        ("polygon", "Polygon/Area Data"),
        ("raster", "Raster/Satellite Data"),
        ("heatmap", "Heatmap Data"),
        ("cluster", "Clustered Data"),
    ]

    DATA_SOURCES = [
        ("field_survey", "Field Survey"),
        ("satellite_imagery", "Satellite Imagery"),
        ("government_data", "Government Dataset"),
        ("community_mapping", "Community Mapping"),
        ("third_party", "Third Party Source"),
        ("mobile_app", "Mobile Application"),
        ("gps_tracking", "GPS Tracking"),
    ]

    name = models.CharField(
        max_length=150, help_text="Name of the geographic data layer"
    )

    description = models.TextField(
        help_text="Description of the data layer and its purpose"
    )

    layer_type = models.CharField(
        max_length=15, choices=LAYER_TYPES, help_text="Type of geographic data"
    )

    data_source = models.CharField(
        max_length=20, choices=DATA_SOURCES, help_text="Source of the geographic data"
    )

    # Community and Assessment Relations
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Community this layer relates to (if applicable)",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Assessment this layer was created for (if applicable)",
    )

    # Geographic Data
    geojson_data = models.JSONField(help_text="GeoJSON data for the layer")

    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box coordinates [min_lng, min_lat, max_lng, max_lat]",
    )

    center_point = models.JSONField(
        null=True,
        blank=True,
        help_text="Center point coordinates [longitude, latitude]",
    )

    # Styling and Display
    style_properties = models.JSONField(
        null=True,
        blank=True,
        help_text="Styling properties for map display (colors, symbols, etc.)",
    )

    zoom_level_min = models.IntegerField(
        default=1, help_text="Minimum zoom level for layer visibility"
    )

    zoom_level_max = models.IntegerField(
        default=18, help_text="Maximum zoom level for layer visibility"
    )

    is_visible = models.BooleanField(
        default=True, help_text="Whether the layer is visible by default"
    )

    opacity = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Layer opacity (0.0 to 1.0)",
    )

    # Metadata and Attribution
    data_collection_date = models.DateField(
        null=True, blank=True, help_text="Date when the data was collected"
    )

    accuracy_meters = models.FloatField(
        null=True, blank=True, help_text="Estimated accuracy in meters"
    )

    coordinate_system = models.CharField(
        max_length=50,
        default="EPSG:4326",
        help_text="Coordinate reference system (e.g., EPSG:4326)",
    )

    attribution = models.TextField(
        blank=True, help_text="Data attribution and source credits"
    )

    license_info = models.CharField(
        max_length=100, blank=True, help_text="License information for the data"
    )

    # Access Control
    is_public = models.BooleanField(
        default=False, help_text="Whether this layer is publicly accessible"
    )

    access_groups = models.JSONField(
        null=True, blank=True, help_text="User groups that have access to this layer"
    )

    # Technical Properties
    feature_count = models.IntegerField(
        default=0, help_text="Number of features in the layer"
    )

    file_size_bytes = models.BigIntegerField(
        null=True, blank=True, help_text="Size of the data in bytes"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_geo_layers",
        help_text="User who created this layer",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["community", "layer_type"]),
            models.Index(fields=["assessment", "data_source"]),
            models.Index(fields=["is_public", "is_visible"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_layer_type_display()})"


class MapVisualization(models.Model):
    """Model for managing map visualizations and configurations."""

    VISUALIZATION_TYPES = [
        ("basic_map", "Basic Map"),
        ("choropleth", "Choropleth Map"),
        ("heat_map", "Heat Map"),
        ("cluster_map", "Cluster Map"),
        ("timeline_map", "Timeline Map"),
        ("comparison_map", "Comparison Map"),
        ("story_map", "Story Map"),
    ]

    MAP_PROVIDERS = [
        ("openstreetmap", "OpenStreetMap"),
        ("satellite", "Satellite Imagery"),
        ("terrain", "Terrain Map"),
        ("dark", "Dark Theme"),
        ("light", "Light Theme"),
        ("custom", "Custom Basemap"),
    ]

    title = models.CharField(max_length=200, help_text="Title of the map visualization")

    description = models.TextField(
        help_text="Description and purpose of the visualization"
    )

    visualization_type = models.CharField(
        max_length=20,
        choices=VISUALIZATION_TYPES,
        help_text="Type of map visualization",
    )

    # Relations
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="map_visualizations",
        null=True,
        blank=True,
        help_text="Community this visualization focuses on",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="map_visualizations",
        null=True,
        blank=True,
        help_text="Assessment this visualization was created for",
    )

    layers = models.ManyToManyField(
        GeographicDataLayer,
        related_name="visualizations",
        help_text="Geographic layers included in this visualization",
    )

    # Map Configuration
    basemap_provider = models.CharField(
        max_length=20,
        choices=MAP_PROVIDERS,
        default="openstreetmap",
        help_text="Base map provider",
    )

    initial_zoom = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(18)],
        help_text="Initial zoom level",
    )

    initial_center = models.JSONField(
        help_text="Initial center point [longitude, latitude]"
    )

    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Map bounding box [min_lng, min_lat, max_lng, max_lat]",
    )

    # Visualization Settings
    color_scheme = models.JSONField(
        null=True, blank=True, help_text="Color scheme configuration"
    )

    legend_configuration = models.JSONField(
        null=True, blank=True, help_text="Legend display configuration"
    )

    popup_template = models.TextField(
        blank=True, help_text="HTML template for feature popups"
    )

    filters_configuration = models.JSONField(
        null=True, blank=True, help_text="Interactive filters configuration"
    )

    # Interactivity
    is_interactive = models.BooleanField(
        default=True, help_text="Whether the map allows user interaction"
    )

    enable_clustering = models.BooleanField(
        default=False, help_text="Whether to enable point clustering"
    )

    enable_search = models.BooleanField(
        default=False, help_text="Whether to enable location search"
    )

    enable_drawing = models.BooleanField(
        default=False, help_text="Whether to enable drawing tools"
    )

    # Sharing and Access
    is_public = models.BooleanField(
        default=False, help_text="Whether this visualization is publicly accessible"
    )

    is_embedded = models.BooleanField(
        default=False, help_text="Whether this visualization can be embedded"
    )

    share_token = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique token for sharing the visualization",
    )

    # Analytics
    view_count = models.IntegerField(
        default=0, help_text="Number of times this visualization has been viewed"
    )

    last_viewed = models.DateTimeField(
        null=True, blank=True, help_text="Last time this visualization was viewed"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_visualizations",
        help_text="User who created this visualization",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_visualization_type_display()})"

    def save(self, *args, **kwargs):
        """Generate share token if needed."""
        if not self.share_token:
            import secrets

            self.share_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class SpatialDataPoint(models.Model):
    """Model for individual spatial data points with attributes."""

    POINT_TYPES = [
        ("community_center", "Community Center"),
        ("health_facility", "Health Facility"),
        ("school", "Educational Facility"),
        ("mosque", "Mosque/Religious Site"),
        ("government_office", "Government Office"),
        ("market", "Market/Commerce"),
        ("infrastructure", "Infrastructure"),
        ("natural_resource", "Natural Resource"),
        ("cultural_site", "Cultural Site"),
        ("hazard_area", "Hazard/Risk Area"),
        ("project_site", "Project Location"),
        ("assessment_point", "Assessment Point"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("planned", "Planned"),
        ("under_construction", "Under Construction"),
        ("abandoned", "Abandoned"),
        ("needs_verification", "Needs Verification"),
    ]

    # Basic Information
    name = models.CharField(max_length=200, help_text="Name or identifier of the point")

    description = models.TextField(blank=True, help_text="Description of the point")

    point_type = models.CharField(
        max_length=25, choices=POINT_TYPES, help_text="Type of spatial point"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current status of the point",
    )

    # Geographic Information
    latitude = models.FloatField(help_text="Latitude coordinate")

    longitude = models.FloatField(help_text="Longitude coordinate")

    elevation = models.FloatField(
        null=True, blank=True, help_text="Elevation in meters above sea level"
    )

    accuracy_meters = models.FloatField(
        null=True, blank=True, help_text="GPS accuracy in meters"
    )

    # Relations
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="spatial_points",
        help_text="Community this point belongs to",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spatial_points",
        help_text="Assessment that identified this point",
    )

    data_layer = models.ForeignKey(
        GeographicDataLayer,
        on_delete=models.CASCADE,
        related_name="data_points",
        help_text="Geographic layer this point belongs to",
    )

    # Attributes
    attributes = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional attributes and properties (JSON format)",
    )

    # Data Collection Information
    collected_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time when point was collected"
    )

    collection_method = models.CharField(
        max_length=50, blank=True, help_text="Method used to collect this point"
    )

    is_verified = models.BooleanField(
        default=False, help_text="Whether this point has been verified"
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_points",
        help_text="User who verified this point",
    )

    verification_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when point was verified"
    )

    # Photo and Media
    photo_url = models.URLField(blank=True, help_text="URL to photo of the location")

    media_files = models.JSONField(
        null=True, blank=True, help_text="References to associated media files"
    )

    # Metadata
    collected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="collected_points",
        help_text="User who collected this point",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-collected_date"]
        indexes = [
            models.Index(fields=["community", "point_type"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["data_layer", "status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_point_type_display()})"

    @property
    def coordinates(self):
        """Return coordinates as [longitude, latitude] for GeoJSON."""
        return [self.longitude, self.latitude]


class WorkshopActivity(models.Model):
    """Model for managing MANA workshop activities following OBC-MANA guidelines."""

    WORKSHOP_TYPES = [
        ("workshop_1", "Workshop 1: Understanding the Community Context"),
        ("workshop_2", "Workshop 2: Community Aspirations and Priorities"),
        ("workshop_3", "Workshop 3: Community Collaboration and Empowerment"),
        ("workshop_4", "Workshop 4: Community Feedback on Existing Initiatives"),
        ("workshop_5", "Workshop 5: OBCs Needs, Challenges, Factors, and Outcomes"),
        ("workshop_6", "Workshop 6: Ways Forward and Action Planning"),
    ]

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    DAYS_MAPPING = [
        ("day_1", "Day 1: Arrival and Registration"),
        ("day_2", "Day 2: Opening and Understanding Community Context"),
        ("day_3", "Day 3: Aspirations, Priorities, Collaboration & Empowerment"),
        ("day_4", "Day 4: Feedback, Challenges, Ways Forward & Closing"),
        ("day_5", "Day 5: Departure"),
    ]

    # Basic Information
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="workshop_activities",
        help_text="Assessment this workshop belongs to",
    )

    workshop_type = models.CharField(
        max_length=15, choices=WORKSHOP_TYPES, help_text="Type of workshop activity"
    )

    title = models.CharField(max_length=250, help_text="Workshop title")

    description = models.TextField(
        help_text="Detailed description of workshop objectives"
    )

    workshop_day = models.CharField(
        max_length=10, choices=DAYS_MAPPING, help_text="Day of the 5-day MANA schedule"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planned",
        help_text="Current status of the workshop",
    )

    # Timing
    scheduled_date = models.DateField(help_text="Scheduled date for the workshop")

    start_time = models.TimeField(help_text="Start time of the workshop")

    end_time = models.TimeField(help_text="End time of the workshop")

    duration_hours = models.FloatField(help_text="Duration in hours")

    # Participants and Facilitation
    target_participants = models.IntegerField(help_text="Target number of participants")

    actual_participants = models.IntegerField(
        default=0, help_text="Actual number of participants"
    )

    facilitators = models.ManyToManyField(
        User, related_name="facilitated_workshops", help_text="Workshop facilitators"
    )

    # Workshop Content and Methodology
    methodology = models.TextField(help_text="Workshop methodology and approach")

    materials_needed = models.TextField(
        blank=True, help_text="Materials and supplies needed"
    )

    # Expected Outputs
    expected_outputs = models.TextField(
        help_text="Expected workshop outputs and deliverables"
    )

    # Results
    key_findings = models.TextField(
        blank=True, help_text="Key findings from the workshop"
    )

    recommendations = models.TextField(
        blank=True, help_text="Recommendations emerging from workshop"
    )

    challenges_encountered = models.TextField(
        blank=True, help_text="Challenges encountered during workshop"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_workshops",
        help_text="User who created this workshop",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop_day", "start_time"]
        unique_together = ["assessment", "workshop_type"]

    def __str__(self):
        return f"{self.get_workshop_type_display()} - {self.assessment.title}"


class WorkshopSession(models.Model):
    """Model for individual workshop sessions within a workshop activity."""

    SESSION_TYPES = [
        ("opening", "Opening Session"),
        ("presentation", "Presentation"),
        ("group_work", "Group Work"),
        ("plenary", "Plenary Discussion"),
        ("breakout", "Breakout Session"),
        ("synthesis", "Synthesis Session"),
        ("closing", "Closing Session"),
    ]

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="Workshop this session belongs to",
    )

    session_title = models.CharField(max_length=200, help_text="Title of the session")

    session_type = models.CharField(
        max_length=15, choices=SESSION_TYPES, help_text="Type of session"
    )

    session_order = models.IntegerField(help_text="Order of session within workshop")

    start_time = models.TimeField(help_text="Session start time")

    end_time = models.TimeField(help_text="Session end time")

    facilitator = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="Primary facilitator for this session"
    )

    objectives = models.TextField(help_text="Session objectives")

    methodology = models.TextField(help_text="Session methodology and activities")

    outputs = models.TextField(blank=True, help_text="Session outputs and results")

    notes = models.TextField(blank=True, help_text="Session notes and observations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop", "session_order"]
        unique_together = ["workshop", "session_order"]

    def __str__(self):
        return f"Session {self.session_order}: {self.session_title}"


class WorkshopParticipant(models.Model):
    """Model for tracking workshop participants."""

    PARTICIPANT_TYPES = [
        ("elder", "Community Elder"),
        ("women_leader", "Women Leader"),
        ("youth_leader", "Youth Leader"),
        ("farmer", "Farmer"),
        ("fisherfolk", "Fisherfolk"),
        ("religious_leader", "Religious Leader"),
        ("traditional_leader", "Traditional Leader"),
        ("milf_representative", "MILF Representative"),
        ("mnlf_representative", "MNLF Representative"),
        ("business_leader", "Business Leader"),
        ("teacher", "Teacher/Educator"),
        ("health_worker", "Health Worker"),
        ("other", "Other"),
    ]

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="participants",
        help_text="Workshop this participant attended",
    )

    name = models.CharField(max_length=100, help_text="Participant name")

    participant_type = models.CharField(
        max_length=20, choices=PARTICIPANT_TYPES, help_text="Type/role of participant"
    )

    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        help_text="Gender of participant",
    )

    age_group = models.CharField(
        max_length=15,
        choices=[
            ("18-30", "18-30 years"),
            ("31-45", "31-45 years"),
            ("46-60", "46-60 years"),
            ("60+", "60+ years"),
        ],
        help_text="Age group of participant",
    )

    contact_info = models.CharField(
        max_length=100, blank=True, help_text="Contact information"
    )

    organization = models.CharField(
        max_length=150, blank=True, help_text="Organization or group represented"
    )

    attendance_status = models.CharField(
        max_length=15,
        choices=[
            ("attended", "Attended"),
            ("partial", "Partial Attendance"),
            ("absent", "Absent"),
        ],
        default="attended",
        help_text="Attendance status",
    )

    participation_notes = models.TextField(
        blank=True, help_text="Notes on participant contributions"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["participant_type", "name"]
        unique_together = ["workshop", "name", "participant_type"]

    def __str__(self):
        return f"{self.name} ({self.get_participant_type_display()})"


class WorkshopOutput(models.Model):
    """Model for tracking workshop outputs and deliverables."""

    OUTPUT_TYPES = [
        ("community_map", "Community Map"),
        ("timeline", "Historical Timeline"),
        ("asset_inventory", "Asset Inventory"),
        ("stakeholder_map", "Stakeholder Map"),
        ("vision_statement", "Vision Statement"),
        ("needs_assessment", "Needs Assessment"),
        ("priority_list", "Priority List"),
        ("organization_map", "Organization Map"),
        ("collaboration_strategy", "Collaboration Strategy"),
        ("program_feedback", "Program Feedback"),
        ("problem_tree", "Problem Tree"),
        ("solution_inventory", "Solution Inventory"),
        ("action_plan", "Action Plan"),
        ("meta_cards", "Meta Cards"),
        ("flip_charts", "Flip Charts"),
        ("photos", "Photo Documentation"),
        ("audio_recording", "Audio Recording"),
        ("other", "Other Output"),
    ]

    workshop = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name="outputs",
        help_text="Workshop that produced this output",
    )

    output_type = models.CharField(
        max_length=30, choices=OUTPUT_TYPES, help_text="Type of workshop output"
    )

    title = models.CharField(max_length=200, help_text="Title or name of the output")

    description = models.TextField(help_text="Description of the output")

    content = models.TextField(help_text="Content or details of the output")

    file_path = models.CharField(
        max_length=500, blank=True, help_text="Path to associated file (if any)"
    )

    created_by_session = models.ForeignKey(
        WorkshopSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Session that created this output",
    )

    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who documented this output"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["workshop", "output_type"]

    def __str__(self):
        return f"{self.title} ({self.get_output_type_display()})"


class MANAReport(models.Model):
    """Model for managing OBC-MANA reports following the prescribed format."""

    REPORT_STATUS = [
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("validation", "Validation"),
        ("final", "Final Report"),
        ("submitted", "Submitted"),
    ]

    REPORT_SECTIONS = [
        ("executive_summary", "Executive Summary"),
        ("context_background", "Context and Background"),
        ("methodology", "Methodology"),
        ("findings_analysis", "Findings and Analysis"),
        ("priority_recommendations", "Priority Issues and Recommendations"),
        ("implementation_framework", "Implementation Framework"),
        ("annexes", "Annexes"),
    ]

    # Basic Information
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name="mana_report",
        help_text="Assessment this report belongs to",
    )

    title = models.CharField(max_length=300, help_text="Report title")

    report_status = models.CharField(
        max_length=15,
        choices=REPORT_STATUS,
        default="draft",
        help_text="Current status of the report",
    )

    # Report Content
    executive_summary = models.TextField(
        blank=True,
        help_text="Executive summary including key findings and recommendations",
    )

    context_background = models.TextField(
        blank=True, help_text="Legal/policy frameworks and community profile"
    )

    methodology = models.TextField(
        blank=True, help_text="Data collection methods and analytical framework"
    )

    # Findings and Analysis sections
    social_development_findings = models.TextField(
        blank=True, help_text="Education, health, social protection findings"
    )

    economic_development_findings = models.TextField(
        blank=True,
        help_text="Livelihoods, infrastructure, financial inclusion findings",
    )

    cultural_development_findings = models.TextField(
        blank=True,
        help_text="Cultural practices, religious institutions, arts findings",
    )

    rights_protection_findings = models.TextField(
        blank=True, help_text="Governance, access to justice, land rights findings"
    )

    # Priority Issues and Recommendations
    priority_issues = models.TextField(
        blank=True, help_text="Prioritized needs and justification"
    )

    policy_recommendations = models.TextField(
        blank=True, help_text="Policy recommendations for each priority"
    )

    program_development_opportunities = models.TextField(
        blank=True, help_text="Program development opportunities"
    )

    # Implementation Framework
    strategic_approaches = models.TextField(
        blank=True, help_text="Strategic approaches and timeframes"
    )

    stakeholder_roles = models.TextField(
        blank=True, help_text="Stakeholder roles and responsibilities"
    )

    resource_requirements = models.TextField(
        blank=True, help_text="Resource requirements and sources"
    )

    monitoring_evaluation = models.TextField(
        blank=True, help_text="Monitoring and evaluation mechanisms"
    )

    # Validation and Review
    validation_date = models.DateField(
        null=True, blank=True, help_text="Date of validation workshop"
    )

    validation_participants = models.TextField(
        blank=True, help_text="Validation workshop participants"
    )

    validation_feedback = models.TextField(
        blank=True, help_text="Feedback from validation workshop"
    )

    # Submission
    submission_date = models.DateField(
        null=True, blank=True, help_text="Date submitted to Office of Chief Minister"
    )

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="submitted_reports",
        help_text="User who submitted the report",
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_reports",
        help_text="User who created this report",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "MANA Report"
        verbose_name_plural = "MANA Reports"

    def __str__(self):
        return f"{self.title} - {self.get_report_status_display()}"


class BaselineStudy(models.Model):
    """Model for managing socio-economic baseline studies for OBC communities."""

    STUDY_TYPES = [
        ("comprehensive", "Comprehensive Baseline"),
        ("socio_economic", "Socio-Economic Study"),
        ("demographic", "Demographic Study"),
        ("livelihood", "Livelihood Assessment"),
        ("infrastructure", "Infrastructure Assessment"),
        ("service_delivery", "Service Delivery Assessment"),
        ("governance", "Governance Assessment"),
        ("cultural", "Cultural Assessment"),
        ("environmental", "Environmental Assessment"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("design", "Study Design"),
        ("data_collection", "Data Collection"),
        ("analysis", "Data Analysis"),
        ("reporting", "Report Writing"),
        ("review", "Under Review"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    METHODOLOGIES = [
        ("quantitative", "Quantitative"),
        ("qualitative", "Qualitative"),
        ("mixed_methods", "Mixed Methods"),
        ("participatory", "Participatory Research"),
        ("rapid_assessment", "Rapid Assessment"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=250, help_text="Title of the baseline study")

    study_type = models.CharField(
        max_length=20, choices=STUDY_TYPES, help_text="Type of baseline study"
    )

    description = models.TextField(help_text="Detailed description of the study")

    objectives = models.TextField(help_text="Study objectives and research questions")

    # Relations
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="baseline_studies",
        help_text="Community being studied",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="baseline_studies",
        help_text="Parent assessment this baseline study belongs to",
    )

    # Study Management
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planning",
        help_text="Current status of the study",
    )

    methodology = models.CharField(
        max_length=20, choices=METHODOLOGIES, help_text="Research methodology used"
    )

    # Timeline
    planned_start_date = models.DateField(help_text="Planned start date for the study")

    planned_end_date = models.DateField(
        help_text="Planned completion date for the study"
    )

    actual_start_date = models.DateField(
        null=True, blank=True, help_text="Actual start date of the study"
    )

    actual_end_date = models.DateField(
        null=True, blank=True, help_text="Actual completion date of the study"
    )

    # Team and Participants
    principal_investigator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="led_baseline_studies",
        help_text="Principal investigator for the study",
    )

    research_team = models.ManyToManyField(
        User,
        through="BaselineStudyTeamMember",
        related_name="baseline_study_teams",
        help_text="Research team members",
    )

    # Study Design
    sample_size_target = models.IntegerField(
        null=True, blank=True, help_text="Target sample size for the study"
    )

    sample_size_actual = models.IntegerField(
        default=0, help_text="Actual sample size achieved"
    )

    sampling_method = models.CharField(
        max_length=100, blank=True, help_text="Sampling method used"
    )

    data_collection_methods = models.TextField(
        help_text="Description of data collection methods"
    )

    # Study Areas and Indicators
    study_domains = models.JSONField(
        help_text="Study domains and indicators (JSON format)"
    )

    geographic_coverage = models.TextField(help_text="Geographic coverage of the study")

    target_population = models.TextField(help_text="Description of target population")

    # Budget and Resources
    estimated_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated budget for the study",
    )

    actual_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual budget spent",
    )

    funding_source = models.CharField(
        max_length=150, blank=True, help_text="Funding source for the study"
    )

    # Results and Outputs
    key_findings = models.TextField(blank=True, help_text="Summary of key findings")

    baseline_indicators = models.JSONField(
        null=True, blank=True, help_text="Baseline indicator values (JSON format)"
    )

    recommendations = models.TextField(blank=True, help_text="Study recommendations")

    limitations = models.TextField(
        blank=True, help_text="Study limitations and constraints"
    )

    # Data Quality
    response_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Response rate percentage",
    )

    data_quality_score = models.IntegerField(
        choices=[(i, f"{i}/10") for i in range(1, 11)],
        null=True,
        blank=True,
        help_text="Data quality score (1-10)",
    )

    # Documentation
    study_protocol = models.TextField(
        blank=True, help_text="Study protocol and procedures"
    )

    data_analysis_plan = models.TextField(
        blank=True, help_text="Data analysis plan and methods"
    )

    # Ethical Considerations
    ethics_approval = models.BooleanField(
        default=False, help_text="Whether ethics approval was obtained"
    )

    ethics_approval_number = models.CharField(
        max_length=50, blank=True, help_text="Ethics approval reference number"
    )

    consent_procedures = models.TextField(
        blank=True, help_text="Informed consent procedures"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_baseline_studies",
        help_text="User who created this study",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["community", "study_type"]),
            models.Index(fields=["status", "planned_start_date"]),
            models.Index(fields=["assessment", "status"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.community.barangay.name}"

    def clean(self):
        if self.planned_end_date and self.planned_start_date:
            if self.planned_end_date < self.planned_start_date:
                raise ValidationError(
                    "Planned end date cannot be earlier than start date"
                )

        if self.actual_end_date and self.actual_start_date:
            if self.actual_end_date < self.actual_start_date:
                raise ValidationError(
                    "Actual end date cannot be earlier than start date"
                )

    @property
    def duration_days(self):
        """Calculate planned duration in days."""
        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days
        return None

    @property
    def is_overdue(self):
        """Check if study is overdue."""
        if self.status not in ["completed", "cancelled"] and self.planned_end_date:
            return timezone.now().date() > self.planned_end_date
        return False

    @property
    def completion_rate(self):
        """Calculate sample completion rate."""
        if self.sample_size_target and self.sample_size_target > 0:
            return (self.sample_size_actual / self.sample_size_target) * 100
        return 0


class BaselineStudyTeamMember(models.Model):
    """Through model for baseline study team members with roles."""

    TEAM_ROLES = [
        ("principal_investigator", "Principal Investigator"),
        ("co_investigator", "Co-Investigator"),
        ("field_coordinator", "Field Coordinator"),
        ("data_collector", "Data Collector"),
        ("data_analyst", "Data Analyst"),
        ("community_liaison", "Community Liaison"),
        ("translator", "Translator/Interpreter"),
        ("quality_assurance", "Quality Assurance"),
        ("supervisor", "Field Supervisor"),
    ]

    study = models.ForeignKey(BaselineStudy, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=25,
        choices=TEAM_ROLES,
        help_text="Role of the team member in this study",
    )

    assigned_date = models.DateField(
        default=timezone.now, help_text="Date when assigned to the study"
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this team member is currently active"
    )

    responsibilities = models.TextField(
        blank=True, help_text="Specific responsibilities and tasks"
    )

    class Meta:
        unique_together = ["study", "user", "role"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


class BaselineDataCollection(models.Model):
    """Model for tracking baseline data collection activities."""

    COLLECTION_METHODS = [
        ("household_survey", "Household Survey"),
        ("key_informant_interview", "Key Informant Interview"),
        ("focus_group_discussion", "Focus Group Discussion"),
        ("community_meeting", "Community Meeting"),
        ("observation", "Direct Observation"),
        ("document_review", "Document Review"),
        ("secondary_data", "Secondary Data Collection"),
    ]

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("quality_check", "Quality Check"),
        ("validated", "Validated"),
        ("rejected", "Rejected"),
    ]

    study = models.ForeignKey(
        BaselineStudy,
        on_delete=models.CASCADE,
        related_name="data_collection_activities",
        help_text="Baseline study this data collection belongs to",
    )

    collection_method = models.CharField(
        max_length=25,
        choices=COLLECTION_METHODS,
        help_text="Data collection method used",
    )

    description = models.TextField(
        help_text="Description of the data collection activity"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="planned",
        help_text="Status of the data collection",
    )

    # Timeline
    planned_date = models.DateField(help_text="Planned date for data collection")

    actual_date = models.DateField(
        null=True, blank=True, help_text="Actual date of data collection"
    )

    duration_hours = models.FloatField(
        null=True, blank=True, help_text="Duration of data collection in hours"
    )

    # Location and Participants
    location = models.CharField(
        max_length=200, help_text="Location where data was collected"
    )

    coordinates = models.JSONField(
        null=True, blank=True, help_text="GPS coordinates of collection location"
    )

    target_participants = models.IntegerField(help_text="Target number of participants")

    actual_participants = models.IntegerField(
        default=0, help_text="Actual number of participants"
    )

    participant_demographics = models.JSONField(
        null=True, blank=True, help_text="Demographic breakdown of participants"
    )

    # Data Collection Team
    data_collectors = models.ManyToManyField(
        User,
        related_name="baseline_data_collections",
        help_text="Team members who collected the data",
    )

    supervisor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="supervised_baseline_collections",
        help_text="Supervisor for this data collection",
    )

    # Data and Quality
    data_collected = models.JSONField(
        null=True, blank=True, help_text="Collected data (JSON format)"
    )

    data_quality_notes = models.TextField(
        blank=True, help_text="Notes on data quality and issues"
    )

    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Completion rate percentage",
    )

    # Validation
    is_validated = models.BooleanField(
        default=False, help_text="Whether the data has been validated"
    )

    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_baseline_data",
        help_text="User who validated the data",
    )

    validation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when data was validated"
    )

    validation_notes = models.TextField(
        blank=True, help_text="Validation notes and feedback"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_baseline_collections",
        help_text="User who created this data collection record",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-planned_date"]
        indexes = [
            models.Index(fields=["study", "collection_method"]),
            models.Index(fields=["status", "planned_date"]),
        ]

    def __str__(self):
        return f"{self.get_collection_method_display()} - {self.study.title}"

    @property
    def participation_rate(self):
        """Calculate participation rate."""
        if self.target_participants > 0:
            return (self.actual_participants / self.target_participants) * 100
        return 0


class BaselineIndicator(models.Model):
    """Model for baseline indicators and their values."""

    INDICATOR_TYPES = [
        ("demographic", "Demographic"),
        ("economic", "Economic"),
        ("social", "Social"),
        ("infrastructure", "Infrastructure"),
        ("health", "Health"),
        ("education", "Education"),
        ("governance", "Governance"),
        ("environment", "Environment"),
        ("cultural", "Cultural"),
    ]

    DATA_TYPES = [
        ("percentage", "Percentage"),
        ("count", "Count/Number"),
        ("currency", "Currency Value"),
        ("rate", "Rate"),
        ("index", "Index Score"),
        ("binary", "Yes/No"),
        ("categorical", "Categorical"),
        ("text", "Text/Qualitative"),
    ]

    study = models.ForeignKey(
        BaselineStudy,
        on_delete=models.CASCADE,
        related_name="indicators",
        help_text="Baseline study this indicator belongs to",
    )

    name = models.CharField(max_length=200, help_text="Name of the indicator")

    description = models.TextField(
        help_text="Description and definition of the indicator"
    )

    indicator_type = models.CharField(
        max_length=15, choices=INDICATOR_TYPES, help_text="Type/category of indicator"
    )

    data_type = models.CharField(
        max_length=15, choices=DATA_TYPES, help_text="Data type of the indicator value"
    )

    # Measurement
    unit_of_measurement = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unit of measurement (e.g., %, PHP, persons)",
    )

    baseline_value = models.TextField(help_text="Baseline value of the indicator")

    target_value = models.TextField(
        blank=True, help_text="Target value for this indicator"
    )

    # Calculation and Data Source
    calculation_method = models.TextField(
        blank=True, help_text="How the indicator is calculated"
    )

    data_source = models.CharField(
        max_length=100, help_text="Source of data for this indicator"
    )

    collection_frequency = models.CharField(
        max_length=50,
        blank=True,
        help_text="How frequently this indicator should be collected",
    )

    # Quality and Reliability
    confidence_level = models.CharField(
        max_length=20, blank=True, help_text="Statistical confidence level"
    )

    margin_of_error = models.CharField(
        max_length=20, blank=True, help_text="Margin of error for the indicator"
    )

    data_quality_notes = models.TextField(
        blank=True, help_text="Notes on data quality and reliability"
    )

    # Disaggregation
    disaggregation_categories = models.JSONField(
        null=True, blank=True, help_text="Categories for disaggregating the indicator"
    )

    disaggregated_values = models.JSONField(
        null=True, blank=True, help_text="Disaggregated values (JSON format)"
    )

    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, help_text="User who created this indicator"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["indicator_type", "name"]
        unique_together = ["study", "name"]

    def __str__(self):
        return f"{self.name} - {self.study.title}"


class CommunityProfile(models.Model):
    """Model for comprehensive community cultural and historical profile."""

    # Basic Information
    community = models.OneToOneField(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="community_profile",
        help_text="OBC community this profile belongs to",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="community_profiles",
        help_text="Assessment that created/updated this profile",
    )

    # IV. CULTURAL AND HISTORICAL CONTEXT
    # Historical background
    brief_historical_background = models.TextField(
        blank=True, help_text="Key historical narratives of the community in the area"
    )

    established_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2030)],
        help_text="Year the community was established",
    )

    origin_story = models.TextField(
        blank=True, help_text="Story of how the community was established"
    )

    migration_history = models.TextField(
        blank=True, help_text="Migration history and patterns"
    )

    # Cultural practices and traditions
    cultural_practices_traditions = models.TextField(
        blank=True, help_text="Notable customs, traditions, festivals"
    )

    religious_affiliation = models.TextField(
        blank=True, help_text="Religious affiliation and specific practices"
    )

    traditional_leaders_role = models.TextField(
        blank=True, help_text="Role of traditional leaders (Imams, Elders, Chieftains)"
    )

    cultural_preservation_efforts = models.TextField(
        blank=True, help_text="Existing cultural preservation efforts"
    )

    # X. NEEDS ASSESSMENT DATA
    needs_assessment_date = models.DateField(
        null=True, blank=True, help_text="Date of last needs assessment"
    )

    key_findings_last_assessment = models.TextField(
        blank=True, help_text="Key findings from last needs assessment"
    )

    assessment_data_sources = models.TextField(
        blank=True,
        help_text="Data sources (community consultations, surveys, LGU data)",
    )

    identified_gaps = models.TextField(
        blank=True, help_text="Identified gaps based on assessments"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_community_profiles",
        help_text="User who created this profile",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["community__barangay__name"]
        verbose_name = "Community Cultural Profile"
        verbose_name_plural = "Community Cultural Profiles"

    def __str__(self):
        return f"Cultural Profile - {self.community.barangay.name}"


class CommunityGovernance(models.Model):
    """Model for community governance and leadership information."""

    RELATIONSHIP_LGU_CHOICES = [
        ("collaborative", "Collaborative"),
        ("strained", "Strained"),
        ("minimal", "Minimal"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    ]

    # Basic Information
    community = models.OneToOneField(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="governance_profile",
        help_text="OBC community this governance profile belongs to",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="governance_profiles",
        help_text="Assessment that created/updated this profile",
    )

    # V. GOVERNANCE AND COMMUNITY LEADERSHIP
    # Political representation and leadership
    formal_political_representation = models.TextField(
        blank=True, help_text="Presence in Barangay Council, LGU representation"
    )

    informal_leadership_structures = models.TextField(
        blank=True, help_text="Description of informal leadership structures"
    )

    community_organizations = models.TextField(
        blank=True,
        help_text="Community organizations/associations (name, focus, contact)",
    )

    relationship_with_lgu = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_LGU_CHOICES,
        blank=True,
        help_text="Relationship with LGU",
    )

    participation_local_governance = models.TextField(
        blank=True, help_text="Participation in local governance and planning"
    )

    access_government_info = models.TextField(
        blank=True, help_text="Access to information on government programs"
    )

    # XI. CONTACT INFORMATION
    key_community_leaders = models.TextField(
        blank=True,
        help_text="Key community leader(s)/focal person(s) with contact details",
    )

    relevant_lgu_officials = models.TextField(
        blank=True, help_text="Relevant LGU official(s) and their contact information"
    )

    # Legacy fields for backward compatibility
    community_leader = models.CharField(
        max_length=255, blank=True, help_text="Name of the primary community leader"
    )

    leader_contact = models.CharField(
        max_length=100, blank=True, help_text="Contact information for community leader"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_governance_profiles",
        help_text="User who created this profile",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["community__barangay__name"]
        verbose_name = "Community Governance Profile"
        verbose_name_plural = "Community Governance Profiles"

    def __str__(self):
        return f"Governance Profile - {self.community.barangay.name}"


class CommunityChallenges(models.Model):
    """Model for tracking community challenges and barriers."""

    CHALLENGE_CATEGORIES = [
        ("governance_policy", "Governance and Policy"),
        ("public_services", "Access to Public Services"),
        ("land_ownership", "Land Ownership and Security"),
        ("economic", "Economic Disparities"),
        ("social_conflict", "Social Instability and Conflict"),
        ("cultural", "Cultural Miscommunication"),
        ("gender", "Gender Inequality"),
        ("substance_abuse", "Substance Abuse"),
        ("financial_fraud", "Investment Scams and Fraud"),
        ("environmental", "Environmental Degradation"),
        ("other", "Other Challenges"),
    ]

    # Basic Information
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="challenges",
        help_text="OBC community facing this challenge",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="identified_challenges",
        help_text="Assessment that identified this challenge",
    )

    # Challenge Details
    category = models.CharField(
        max_length=20, choices=CHALLENGE_CATEGORIES, help_text="Category of challenge"
    )

    title = models.CharField(max_length=200, help_text="Brief title of the challenge")

    description = models.TextField(help_text="Detailed description of the challenge")

    impact_description = models.TextField(
        help_text="Impact of this challenge on the community"
    )

    affected_population = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of people affected by this challenge"
    )

    severity_level = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Severity level (1=Low, 5=Critical)",
    )

    # Specific challenge fields from original model
    # VI. CHALLENGES AND BARRIERS
    governance_policy_challenges = models.TextField(
        blank=True, help_text="Marginalization, lack of representation issues"
    )

    access_public_services_challenges = models.TextField(
        blank=True,
        help_text="Challenges in accessing education, health, infrastructure",
    )

    land_ownership_security_issues = models.TextField(
        blank=True, help_text="Land ownership and security challenges"
    )

    economic_disparities = models.TextField(
        blank=True, help_text="Poverty, limited employment, economic challenges"
    )

    social_instability_conflict = models.TextField(
        blank=True, help_text="Rido, security issues, social conflicts"
    )

    cultural_miscommunication = models.TextField(
        blank=True, help_text="Cultural miscommunication challenges"
    )

    gender_inequality_issues = models.TextField(
        blank=True, help_text="Gender inequality, early marriage issues"
    )

    substance_abuse_issues = models.TextField(
        blank=True, help_text="Drug use, substance abuse issues"
    )

    investment_scam_issues = models.TextField(
        blank=True, help_text="Investment scams and financial fraud issues"
    )

    environmental_degradation = models.TextField(
        blank=True, help_text="Mining, illegal fishing, environmental issues"
    )

    other_challenges = models.TextField(
        blank=True,
        help_text="Other specific challenges (ISAL education, Halal industry, etc.)",
    )

    challenges_impact = models.TextField(
        blank=True, help_text="Impact of these challenges on the community"
    )

    # Status and Resolution
    is_active = models.BooleanField(
        default=True, help_text="Whether this challenge is currently active"
    )

    resolution_efforts = models.TextField(
        blank=True, help_text="Efforts being made to address this challenge"
    )

    support_needed = models.TextField(
        blank=True, help_text="Support needed to address this challenge"
    )

    # Metadata
    identified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="identified_challenges",
        help_text="User who identified this challenge",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-severity_level", "category", "title"]
        verbose_name = "Community Challenge"
        verbose_name_plural = "Community Challenges"

    def __str__(self):
        return f"{self.title} - {self.community.barangay.name}"


class CommunityAspirations(models.Model):
    """Model for tracking community aspirations and development priorities."""

    ASPIRATION_CATEGORIES = [
        ("poverty_eradication", "Poverty Eradication"),
        ("infrastructure", "Infrastructure Development"),
        ("livelihood", "Livelihood Programs"),
        ("education", "Education Enhancement"),
        ("healthcare", "Healthcare Access"),
        ("cultural_preservation", "Cultural Preservation"),
        ("peace_security", "Peace and Security"),
        ("governance", "Governance Improvement"),
        ("environment", "Environmental Protection"),
        ("other", "Other Aspirations"),
    ]

    PRIORITY_LEVELS = [
        ("critical", "Critical Priority"),
        ("high", "High Priority"),
        ("medium", "Medium Priority"),
        ("low", "Low Priority"),
    ]

    # Basic Information
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="aspirations",
        help_text="OBC community with this aspiration",
    )

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="community_aspirations",
        help_text="Assessment that captured this aspiration",
    )

    # Aspiration Details
    category = models.CharField(
        max_length=25, choices=ASPIRATION_CATEGORIES, help_text="Category of aspiration"
    )

    title = models.CharField(max_length=200, help_text="Brief title of the aspiration")

    description = models.TextField(help_text="Detailed description of the aspiration")

    priority_level = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Priority level of this aspiration",
    )

    # Specific aspiration fields from original model
    # VII. COMMUNITY ASPIRATIONS AND DEVELOPMENT PRIORITIES
    key_aspirations = models.TextField(
        blank=True,
        help_text="Key community aspirations (poverty eradication, improved services, etc.)",
    )

    infrastructure_priorities = models.TextField(
        blank=True,
        help_text="Infrastructure development priorities (roads, water, health, schools)",
    )

    livelihood_program_priorities = models.TextField(
        blank=True,
        help_text="Livelihood program priorities (agriculture, fisheries, SMEs, Halal, ecotourism)",
    )

    education_priorities = models.TextField(
        blank=True,
        help_text="Education priorities (scholarships, skills training, Madrasah support)",
    )

    healthcare_priorities = models.TextField(
        blank=True, help_text="Healthcare access priorities"
    )

    cultural_preservation_priorities = models.TextField(
        blank=True, help_text="Cultural preservation initiative priorities"
    )

    peace_security_priorities = models.TextField(
        blank=True, help_text="Peace and order/conflict resolution priorities"
    )

    specific_project_proposals = models.TextField(
        blank=True, help_text="Specific project proposals/ideas from the community"
    )

    # Implementation Planning
    estimated_beneficiaries = models.PositiveIntegerField(
        null=True, blank=True, help_text="Estimated number of beneficiaries"
    )

    estimated_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated budget required",
    )

    proposed_timeline = models.CharField(
        max_length=100, blank=True, help_text="Proposed timeline for implementation"
    )

    potential_partners = models.TextField(
        blank=True, help_text="Potential partners for implementation"
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Whether this aspiration is still active/relevant"
    )

    implementation_status = models.CharField(
        max_length=20,
        choices=[
            ("identified", "Identified"),
            ("planning", "Under Planning"),
            ("funded", "Funded"),
            ("implementing", "Being Implemented"),
            ("completed", "Completed"),
            ("deferred", "Deferred"),
        ],
        default="identified",
        help_text="Implementation status",
    )

    # Metadata
    captured_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="captured_aspirations",
        help_text="User who captured this aspiration",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority_level", "category", "title"]
        verbose_name = "Community Aspiration"
        verbose_name_plural = "Community Aspirations"

    def __str__(self):
        return f"{self.title} - {self.community.barangay.name}"
