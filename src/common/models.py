from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class User(AbstractUser):
    """
    Custom User model for the OBC Management System.
    Extends Django's AbstractUser to include OBC-specific fields and roles.
    """

    USER_TYPES = (
        ("admin", "Administrator"),
        ("oobc_staff", "OOBC Staff"),
        ("cm_office", "Chief Minister Office"),
        ("bmoa", "BARMM Ministry/Agency/Office"),
        ("lgu", "Local Government Unit"),
        ("nga", "National Government Agency"),
        ("community_leader", "Community Leader"),
        ("researcher", "Assessment Coordinator/Researcher"),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        help_text="Type of user based on organization role",
    )
    organization = models.CharField(
        max_length=255, blank=True, help_text="Name of the organization or agency"
    )
    position = models.CharField(
        max_length=255,
        blank=True,
        help_text="Position or title within the organization",
    )
    contact_number = models.CharField(
        max_length=20, blank=True, help_text="Contact phone number"
    )
    is_approved = models.BooleanField(
        default=False, help_text="Whether the user account has been approved for access"
    )
    approved_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_users",
        help_text="Admin user who approved this account",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="When the account was approved"
    )

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def get_full_name(self):
        """Return the full name of the user."""
        return super().get_full_name() or self.username

    @property
    def is_oobc_staff(self):
        """Check if user is OOBC staff."""
        return self.user_type == "oobc_staff"

    @property
    def is_community_leader(self):
        """Check if user is a community leader."""
        return self.user_type == "community_leader"

    @property
    def can_approve_users(self):
        """Check if user can approve other users."""
        return self.user_type in ["admin", "oobc_staff"] and self.is_superuser


class Region(models.Model):
    """
    Administrative region model representing Philippine regions.
    Focus on Regions IX (Zamboanga Peninsula), XII (SOCCSKSARGEN), and others.
    """

    code = models.CharField(
        max_length=10, unique=True, help_text="Official region code (e.g., IX, XII)"
    )
    name = models.CharField(max_length=255, help_text="Official region name")
    description = models.TextField(
        blank=True, help_text="Additional region description or notes"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this region is active in the system"
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON polygon defining the region boundary"
    )
    center_coordinates = models.JSONField(
        null=True,
        blank=True,
        help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_region"
        ordering = ["code"]
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"Region {self.code} - {self.name}"

    @property
    def province_count(self):
        """Return the number of provinces in this region."""
        return self.provinces.filter(is_active=True).count()

    @property
    def has_geographic_boundary(self):
        """Check if this region has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this region."""
        return self.geographic_layers.count()

    def get_contained_coordinates(self, coordinates):
        """Check if given coordinates [lng, lat] are within region boundary."""
        if not self.boundary_geojson:
            return False
        # Placeholder for actual geometric containment check
        # In production, this would use proper GIS libraries like Shapely
        return True

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer
        return GeographicDataLayer.objects.filter(
            models.Q(region=self) |
            models.Q(province__region=self) |
            models.Q(municipality__province__region=self) |
            models.Q(barangay__municipality__province__region=self) |
            models.Q(community__barangay__municipality__province__region=self)
        )


class Province(models.Model):
    """
    Administrative province model under regions.
    """

    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="provinces",
        help_text="Parent region",
    )
    code = models.CharField(
        max_length=64, unique=True, help_text="Official province code"
    )
    name = models.CharField(max_length=255, help_text="Official province name")
    capital = models.CharField(
        max_length=255, blank=True, help_text="Provincial capital city"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this province is active in the system"
    )
    population_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total population based on latest PSA census",
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON polygon defining the province boundary"
    )
    center_coordinates = models.JSONField(
        null=True,
        blank=True,
        help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_province"
        ordering = ["region__code", "name"]
        verbose_name = "Province"
        verbose_name_plural = "Provinces"

    def __str__(self):
        return f"{self.name}, {self.region.name}"

    @property
    def municipality_count(self):
        """Return the number of municipalities in this province."""
        return self.municipalities.filter(is_active=True).count()

    @property
    def full_path(self):
        """Return the full administrative path."""
        return f"Region {self.region.code} > {self.name}"

    @property
    def has_geographic_boundary(self):
        """Check if this province has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this province."""
        return self.geographic_layers.count()

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer
        return GeographicDataLayer.objects.filter(
            models.Q(province=self) |
            models.Q(municipality__province=self) |
            models.Q(barangay__municipality__province=self) |
            models.Q(community__barangay__municipality__province=self)
        )


class Municipality(models.Model):
    """
    Administrative municipality/city model under provinces.
    """

    MUNICIPALITY_TYPES = (
        ("municipality", "Municipality"),
        ("city", "City"),
        ("component_city", "Component City"),
        ("independent_city", "Independent City"),
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="municipalities",
        help_text="Parent province",
    )
    code = models.CharField(
        max_length=64, unique=True, help_text="Official municipality/city code"
    )
    name = models.CharField(max_length=255, help_text="Official municipality/city name")
    municipality_type = models.CharField(
        max_length=20,
        choices=MUNICIPALITY_TYPES,
        default="municipality",
        help_text="Type of local government unit",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this municipality is active in the system"
    )
    population_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total population based on latest PSA census",
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON polygon defining the municipality boundary"
    )
    center_coordinates = models.JSONField(
        null=True,
        blank=True,
        help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_municipality"
        ordering = ["province__name", "name"]
        verbose_name = "Municipality"
        verbose_name_plural = "Municipalities"

    def __str__(self):
        type_display = self.get_municipality_type_display()
        return f"{type_display} of {self.name}, {self.province.name}"

    @property
    def barangay_count(self):
        """Return the number of barangays in this municipality."""
        return self.barangays.filter(is_active=True).count()

    @property
    def full_path(self):
        """Return the full administrative path."""
        return (
            f"Region {self.province.region.code} > {self.province.name} > {self.name}"
        )

    @property
    def has_geographic_boundary(self):
        """Check if this municipality has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this municipality."""
        return self.geographic_layers.count()

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer
        return GeographicDataLayer.objects.filter(
            models.Q(municipality=self) |
            models.Q(barangay__municipality=self) |
            models.Q(community__barangay__municipality=self)
        )


class Barangay(models.Model):
    """
    Administrative barangay model under municipalities.
    Barangay is the smallest administrative unit in the Philippines.
    """

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name="barangays",
        help_text="Parent municipality",
    )
    code = models.CharField(
        max_length=64, unique=True, help_text="Official barangay code"
    )
    name = models.CharField(max_length=255, help_text="Official barangay name")
    is_urban = models.BooleanField(
        default=False, help_text="Whether this barangay is classified as urban"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this barangay is active in the system"
    )
    population_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total population based on latest PSA census",
    )

    # Geographic boundary information
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON polygon defining the barangay boundary"
    )
    center_coordinates = models.JSONField(
        null=True,
        blank=True,
        help_text="Geographic center point [longitude, latitude]"
    )
    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box [min_lng, min_lat, max_lng, max_lat]"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_barangay"
        ordering = ["municipality__name", "name"]
        verbose_name = "Barangay"
        verbose_name_plural = "Barangays"

    def __str__(self):
        return f"Barangay {self.name}, {self.municipality.name}"

    @property
    def full_path(self):
        """Return the full administrative path."""
        return (
            f"Region {self.municipality.province.region.code} > "
            f"{self.municipality.province.name} > "
            f"{self.municipality.name} > "
            f"Barangay {self.name}"
        )

    @property
    def region(self):
        """Return the region this barangay belongs to."""
        return self.municipality.province.region

    @property
    def province(self):
        """Return the province this barangay belongs to."""
        return self.municipality.province

    @property
    def has_geographic_boundary(self):
        """Check if this barangay has geographic boundary data."""
        return bool(self.boundary_geojson)

    @property
    def geographic_layers_count(self):
        """Return the number of geographic layers associated with this barangay."""
        return self.geographic_layers.count()

    def get_all_geographic_layers(self):
        """Get all geographic layers at this level and below."""
        from mana.models import GeographicDataLayer
        return GeographicDataLayer.objects.filter(
            models.Q(barangay=self) |
            models.Q(community__barangay=self)
        )


class StaffProfile(models.Model):
    """Extended profile metadata for OOBC staff members."""

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_ON_LEAVE = "on_leave"
    EMPLOYMENT_STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_ON_LEAVE, "On Leave"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    TYPE_REGULAR = "regular"
    TYPE_CONTRACTUAL = "contractual"
    TYPE_CONSULTANT = "consultant"
    TYPE_VOLUNTEER = "volunteer"
    EMPLOYMENT_TYPE_CHOICES = [
        (TYPE_REGULAR, "Regular"),
        (TYPE_CONTRACTUAL, "Contractual"),
        (TYPE_CONSULTANT, "Consultant"),
        (TYPE_VOLUNTEER, "Volunteer"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="staff_profile",
        on_delete=models.CASCADE,
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        blank=True,
    )
    position_classification = models.CharField(max_length=150, blank=True)
    plantilla_item_number = models.CharField(max_length=100, blank=True)
    salary_grade = models.CharField(max_length=50, blank=True)
    salary_step = models.CharField(max_length=20, blank=True)
    reports_to = models.CharField(max_length=255, blank=True)
    date_joined_organization = models.DateField(null=True, blank=True)
    primary_location = models.CharField(max_length=255, blank=True)
    job_purpose = models.TextField(blank=True)
    key_result_areas = models.JSONField(default=list, blank=True)
    major_functions = models.JSONField(default=list, blank=True)
    deliverables = models.JSONField(default=list, blank=True)
    supervision_lines = models.JSONField(default=list, blank=True)
    cross_functional_partners = models.JSONField(default=list, blank=True)
    core_competencies = models.JSONField(default=list, blank=True)
    leadership_competencies = models.JSONField(default=list, blank=True)
    functional_competencies = models.JSONField(default=list, blank=True)
    qualification_education = models.CharField(max_length=255, blank=True)
    qualification_training = models.CharField(max_length=255, blank=True)
    qualification_experience = models.CharField(max_length=255, blank=True)
    qualification_eligibility = models.CharField(max_length=255, blank=True)
    qualification_competency = models.TextField(blank=True)
    job_documents_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"Staff Profile: {self.user.get_full_name()}"

    def get_competencies(self, category: str) -> list[str]:
        """Return the stored competencies for a given category."""

        mapping = {
            "core": self.core_competencies,
            "leadership": self.leadership_competencies,
            "functional": self.functional_competencies,
        }
        return mapping.get(category, [])


class StaffTeam(models.Model):
    """Operational teams coordinating OOBC staff and task workflows."""

    ROLE_FOCUS_DEFAULT = [
        "strategy",
        "implementation",
        "monitoring",
        "coordination",
    ]

    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    focus_areas = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "team"
            slug = base_slug
            index = 1
            while StaffTeam.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{index}"
                index += 1
            self.slug = slug
        if not self.focus_areas:
            self.focus_areas = self.ROLE_FOCUS_DEFAULT
        super().save(*args, **kwargs)

    @property
    def active_memberships(self):
        """Return active memberships for this team."""
        return self.memberships.filter(is_active=True)


class StaffTeamMembership(models.Model):
    """Link OOBC staff to operational teams with roles."""

    ROLE_MEMBER = "member"
    ROLE_LEAD = "lead"
    ROLE_COORDINATOR = "coordinator"
    ROLE_CHOICES = [
        (ROLE_LEAD, "Team Lead"),
        (ROLE_COORDINATOR, "Coordinator"),
        (ROLE_MEMBER, "Member"),
    ]

    team = models.ForeignKey(
        StaffTeam, related_name="memberships", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="team_memberships",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_team_memberships",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("team", "user")
        ordering = ["team__name", "user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"

    def deactivate(self, save=True):
        """Mark the membership as inactive."""
        self.is_active = False
        if save:
            self.save(update_fields=["is_active", "updated_at"])


class StaffTask(models.Model):
    """Task records connected to staff profiles, teams, and calendar events."""

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_AT_RISK = "at_risk"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not Started"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_AT_RISK, "At Risk"),
        (STATUS_COMPLETED, "Completed"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CRITICAL = "critical"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_CRITICAL, "Critical"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    impact = models.CharField(max_length=255, blank=True)
    teams = models.ManyToManyField(
        StaffTeam,
        related_name="tasks",
        blank=True,
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_staff_tasks",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_staff_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    linked_event = models.ForeignKey(
        "coordination.Event",
        related_name="staff_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED
    )
    priority = models.CharField(
        max_length=12, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )
    progress = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    board_position = models.PositiveIntegerField(
        default=0,
        help_text="Relative ordering for Kanban board presentation.",
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["board_position", "due_date", "-priority", "title"]

    def __init__(self, *args, **kwargs):
        self._pending_team_assignment = kwargs.pop("team", None)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        pending_team = getattr(self, "_pending_team_assignment", None)
        super().save(*args, **kwargs)

        if pending_team is not None:
            resolved_teams = self._resolve_team_values(pending_team)
            if resolved_teams:
                self.teams.set(resolved_teams)
            else:
                self.teams.clear()
            self._pending_team_assignment = None

    def _resolve_team_values(self, value):
        """Normalize team inputs into iterable of StaffTeam instances."""

        if value is None:
            return []
        if isinstance(value, StaffTeam):
            return [value]
        if isinstance(value, (list, tuple, set)):
            resolved = []
            for item in value:
                resolved.extend(self._resolve_team_values(item))
            return resolved
        if isinstance(value, int):
            try:
                return [StaffTeam.objects.get(pk=value)]
            except StaffTeam.DoesNotExist:
                return []
        raise ValueError("Unsupported team assignment value.")

    @property
    def is_overdue(self):
        """Return True if the task is overdue."""
        if self.status == self.STATUS_COMPLETED or not self.due_date:
            return False
        return self.due_date < timezone.now().date()

    @property
    def assignee_display_name(self):
        """Return a human-friendly assignee label, handling missing data."""

        members = []
        if hasattr(self, "assignees"):
            try:
                members = list(self.assignees.all())
            except Exception:
                members = []
        if not members:
            return "Unassigned"

        def _display_name(user_obj):
            if not user_obj:
                return ""
            if hasattr(user_obj, "get_full_name"):
                full_name = (user_obj.get_full_name() or "").strip()
                if full_name:
                    return full_name
            username = getattr(user_obj, "username", "")
            return username

        labels = [label for label in (_display_name(member) for member in members) if label]
        if not labels:
            return "Unassigned"
        return ", ".join(labels)

    @property
    def team(self):
        """Return the first associated team for legacy access patterns."""

        if not hasattr(self, "teams"):
            return None
        try:
            return self.teams.all().first()
        except Exception:  # pragma: no cover - defensive fallback
            return None

    @team.setter
    def team(self, value):
        self._pending_team_assignment = value


class TrainingProgram(models.Model):
    """Catalogue of training opportunities for OOBC staff."""

    MODE_IN_PERSON = "in_person"
    MODE_VIRTUAL = "virtual"
    MODE_HYBRID = "hybrid"
    DELIVERY_MODE_CHOICES = [
        (MODE_IN_PERSON, "In Person"),
        (MODE_VIRTUAL, "Virtual"),
        (MODE_HYBRID, "Hybrid"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    delivery_mode = models.CharField(
        max_length=20, choices=DELIVERY_MODE_CHOICES, default=MODE_IN_PERSON
    )
    competency_focus = models.JSONField(default=list, blank=True)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class TrainingEnrollment(models.Model):
    """Link staff to training programmes for development tracking."""

    STATUS_PLANNED = "planned"
    STATUS_ONGOING = "ongoing"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_ONGOING, "Ongoing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    staff_profile = models.ForeignKey(
        "StaffProfile",
        related_name="training_enrollments",
        on_delete=models.CASCADE,
    )
    program = models.ForeignKey(
        "TrainingProgram",
        related_name="enrollments",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED
    )
    scheduled_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    evidence_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date", "program__title"]

    def __str__(self):
        return f"{self.staff_profile.user.get_full_name()} - {self.program.title}"


class StaffDevelopmentPlan(models.Model):
    """Individual development actions per staff member."""

    STATUS_PLANNED = "planned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
    ]

    staff_profile = models.ForeignKey(
        "StaffProfile",
        related_name="development_plans",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    competency_focus = models.CharField(max_length=150, blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED
    )
    support_needed = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["target_date", "title"]

    def __str__(self):
        return f"Development Plan: {self.title} ({self.staff_profile.user.get_full_name()})"


class PerformanceTarget(models.Model):
    """Targets and actuals for staff or team performance dashboards."""

    SCOPE_STAFF = "staff"
    SCOPE_TEAM = "team"
    SCOPE_CHOICES = [
        (SCOPE_STAFF, "Staff"),
        (SCOPE_TEAM, "Team"),
    ]

    STATUS_ON_TRACK = "on_track"
    STATUS_AT_RISK = "at_risk"
    STATUS_OFF_TRACK = "off_track"
    STATUS_CHOICES = [
        (STATUS_ON_TRACK, "On Track"),
        (STATUS_AT_RISK, "At Risk"),
        (STATUS_OFF_TRACK, "Off Track"),
    ]

    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    staff_profile = models.ForeignKey(
        "StaffProfile",
        related_name="performance_targets",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    team = models.ForeignKey(
        "StaffTeam",
        related_name="performance_targets",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    metric_name = models.CharField(max_length=150)
    performance_standard = models.CharField(max_length=255, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_ON_TRACK
    )
    period_start = models.DateField()
    period_end = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_end", "metric_name"]

    def __str__(self):
        scope_label = dict(self.SCOPE_CHOICES).get(self.scope, self.scope)
        return f"{scope_label} Target: {self.metric_name}"

    def clean(self):
        """Ensure the appropriate relation is populated based on scope."""

        if self.scope == self.SCOPE_STAFF and not self.staff_profile:
            raise ValidationError("Staff targets require a staff profile.")
        if self.scope == self.SCOPE_TEAM and not self.team:
            raise ValidationError("Team targets require a team.")
        if self.scope == self.SCOPE_STAFF and self.team:
            raise ValidationError("Staff targets cannot be linked to a team.")
        if self.scope == self.SCOPE_TEAM and self.staff_profile:
            raise ValidationError("Team targets cannot be linked to a staff profile.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
