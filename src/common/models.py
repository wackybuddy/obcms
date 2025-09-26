from django.conf import settings
from django.contrib.auth.models import AbstractUser
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
    team = models.ForeignKey(
        StaffTeam,
        related_name="tasks",
        on_delete=models.PROTECT,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_staff_tasks",
        on_delete=models.SET_NULL,
        null=True,
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
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "due_date"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Return True if the task is overdue."""
        if self.status == self.STATUS_COMPLETED or not self.due_date:
            return False
        return self.due_date < timezone.now().date()

    def mark_completed(self, user=None):
        """Mark task as completed and update progress."""
        self.status = self.STATUS_COMPLETED
        self.progress = 100
        self.completed_at = timezone.now()
        update_fields = ["status", "progress", "completed_at", "updated_at"]
        if user and not self.created_by:
            self.created_by = user
            update_fields.append("created_by")
        self.save(update_fields=update_fields)
