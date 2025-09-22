"""Admin registrations for Monitoring & Evaluation models."""

from django.contrib import admin

from .models import MonitoringEntry, MonitoringUpdate


class MonitoringUpdateInline(admin.TabularInline):
    """Inline updates to provide quick history in the admin panel."""

    model = MonitoringUpdate
    extra = 0
    fields = (
        "created_at",
        "update_type",
        "status",
        "request_status",
        "progress",
        "follow_up_date",
        "created_by",
    )
    readonly_fields = ("created_at",)


@admin.register(MonitoringEntry)
class MonitoringEntryAdmin(admin.ModelAdmin):
    """Admin configuration for monitoring entries."""

    list_display = (
        "title",
        "category",
        "status",
        "request_status",
        "progress",
        "priority",
        "lead_organization",
        "submitted_by_community",
        "updated_at",
    )
    list_filter = (
        "category",
        "status",
        "request_status",
        "priority",
        "lead_organization",
        "submitted_to_organization",
        "communities",
    )
    search_fields = (
        "title",
        "summary",
        "oobc_unit",
        "support_required",
    )
    autocomplete_fields = (
        "lead_organization",
        "supporting_organizations",
        "submitted_by_community",
        "communities",
        "submitted_to_organization",
        "related_assessment",
        "related_event",
        "related_policy",
    )
    inlines = [MonitoringUpdateInline]
    date_hierarchy = "created_at"


@admin.register(MonitoringUpdate)
class MonitoringUpdateAdmin(admin.ModelAdmin):
    """Admin configuration for monitoring updates."""

    list_display = (
        "entry",
        "update_type",
        "status",
        "request_status",
        "progress",
        "follow_up_date",
        "created_by",
        "created_at",
    )
    list_filter = (
        "update_type",
        "status",
        "request_status",
        "created_at",
    )
    search_fields = ("entry__title", "notes", "next_steps")
    autocomplete_fields = ("entry",)
    date_hierarchy = "created_at"
