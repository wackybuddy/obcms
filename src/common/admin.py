from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import (
    Barangay,
    Municipality,
    Province,
    Region,
    StaffTask,
    StaffTeam,
    StaffTeamMembership,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for the custom User model."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "organization",
        "is_approved",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "user_type",
        "is_approved",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    search_fields = ("username", "first_name", "last_name", "email", "organization")
    ordering = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "OBC Information",
            {"fields": ("user_type", "organization", "position", "contact_number")},
        ),
        ("Approval Status", {"fields": ("is_approved", "approved_by", "approved_at")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "OBC Information",
            {"fields": ("user_type", "organization", "position", "contact_number")},
        ),
    )

    readonly_fields = ("approved_at",)

    def save_model(self, request, obj, form, change):
        """Override save to handle approval logic."""
        if change and "is_approved" in form.changed_data and obj.is_approved:
            if not obj.approved_by:
                obj.approved_by = request.user
            if not obj.approved_at:
                obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)

    actions = ["approve_users", "disapprove_users"]

    def approve_users(self, request, queryset):
        """Bulk approve selected users."""
        updated = queryset.filter(is_approved=False).update(
            is_approved=True, approved_by=request.user, approved_at=timezone.now()
        )
        self.message_user(request, f"{updated} users were approved.")

    approve_users.short_description = "Approve selected users"

    def disapprove_users(self, request, queryset):
        """Bulk disapprove selected users."""
        updated = queryset.filter(is_approved=True).update(
            is_approved=False, approved_by=None, approved_at=None
        )
        self.message_user(request, f"{updated} users were disapproved.")

    disapprove_users.short_description = "Disapprove selected users"


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """Admin interface for Region model."""

    list_display = ("code", "name", "province_count", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("code", "name", "description")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at", "province_count")

    fieldsets = (
        (None, {"fields": ("code", "name", "description", "is_active")}),
        ("Statistics", {"fields": ("province_count",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    """Admin interface for Province model."""

    list_display = (
        "name",
        "region",
        "capital",
        "municipality_count",
        "is_active",
        "created_at",
    )
    list_filter = ("region", "is_active", "created_at")
    search_fields = ("code", "name", "capital", "region__name")
    ordering = ("region__code", "name")
    readonly_fields = ("created_at", "updated_at", "municipality_count", "full_path")

    fieldsets = (
        (None, {"fields": ("region", "code", "name", "capital", "is_active")}),
        ("Administrative Path", {"fields": ("full_path",), "classes": ("collapse",)}),
        ("Statistics", {"fields": ("municipality_count",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    """Admin interface for Municipality model."""

    list_display = (
        "name",
        "municipality_type",
        "province",
        "barangay_count",
        "is_active",
        "created_at",
    )
    list_filter = (
        "municipality_type",
        "province__region",
        "province",
        "is_active",
        "created_at",
    )
    search_fields = ("code", "name", "province__name", "province__region__name")
    ordering = ("province__region__code", "province__name", "name")
    readonly_fields = ("created_at", "updated_at", "barangay_count", "full_path")

    fieldsets = (
        (
            None,
            {"fields": ("province", "code", "name", "municipality_type", "is_active")},
        ),
        ("Administrative Path", {"fields": ("full_path",), "classes": ("collapse",)}),
        ("Statistics", {"fields": ("barangay_count",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    """Admin interface for Barangay model."""

    list_display = (
        "name",
        "municipality",
        "province",
        "region",
        "is_urban",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_urban",
        "is_active",
        "municipality__province__region",
        "municipality__province",
        "municipality",
        "created_at",
    )
    search_fields = (
        "code",
        "name",
        "municipality__name",
        "municipality__province__name",
        "municipality__province__region__name",
    )
    ordering = (
        "municipality__province__region__code",
        "municipality__province__name",
        "municipality__name",
        "name",
    )
    readonly_fields = ("created_at", "updated_at", "full_path", "region", "province")


@admin.register(StaffTeam)
class StaffTeamAdmin(admin.ModelAdmin):
    """Admin configuration for staff teams."""

    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description", "mission")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(StaffTeamMembership)
class StaffTeamMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for staff team memberships."""

    list_display = (
        "user",
        "team",
        "role",
        "is_active",
        "joined_at",
    )
    list_filter = ("role", "is_active", "team")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "team__name",
    )
    autocomplete_fields = ("team", "user", "assigned_by")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StaffTask)
class StaffTaskAdmin(admin.ModelAdmin):
    """Admin configuration for staff tasks."""

    list_display = (
        "title",
        "teams_list",
        "assignee_list",
        "status",
        "priority",
        "due_date",
        "progress",
    )
    list_filter = ("status", "priority", "teams", "assignees")
    search_fields = ("title", "description", "impact")
    autocomplete_fields = ("teams", "assignees", "created_by", "linked_event")
    readonly_fields = ("created_at", "updated_at", "completed_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "teams",
                    "assignees",
                    "created_by",
                    "linked_event",
                    "impact",
                )
            },
        ),
        (
            "Schedule",
            {"fields": ("start_date", "due_date", "status", "priority", "progress")},
        ),
        ("Details", {"fields": ("description",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at", "completed_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Assignees")
    def assignee_list(self, obj):
        return obj.assignee_display_name

    def teams_list(self, obj):
        """Display teams for the task."""
        teams = list(obj.teams.all())
        if not teams:
            return "No teams"
        return ", ".join(team.name for team in teams)

    teams_list.short_description = "Teams"

    fieldsets = (
        (None, {"fields": ("municipality", "code", "name", "is_urban", "is_active")}),
        (
            "Administrative Path",
            {"fields": ("full_path", "region", "province"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def province(self, obj):
        """Display province name in list view."""
        return obj.province.name

    province.short_description = "Province"

    def region(self, obj):
        """Display region name in list view."""
        return obj.region.name

    region.short_description = "Region"
