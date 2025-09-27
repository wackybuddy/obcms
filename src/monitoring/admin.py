"""Admin registrations for Monitoring & Evaluation models."""

from django.contrib import admin

from .models import (
    MonitoringEntry,
    MonitoringEntryFunding,
    MonitoringEntryWorkflowStage,
    MonitoringUpdate,
)


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


class MonitoringEntryFundingInline(admin.TabularInline):
    """Inline funding flow management for quick adjustments."""

    model = MonitoringEntryFunding
    extra = 0
    fields = (
        "tranche_type",
        "amount",
        "funding_source",
        "funding_source_other",
        "scheduled_date",
        "remarks",
    )


class MonitoringEntryWorkflowStageInline(admin.TabularInline):
    """Inline workflow stage tracking for planning milestones."""

    model = MonitoringEntryWorkflowStage
    extra = 0
    fields = (
        "stage",
        "status",
        "owner_team",
        "owner_organization",
        "due_date",
        "completed_at",
        "notes",
    )


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
        "plan_year",
        "funding_source",
        "appropriation_class",
        "lead_organization",
        "submitted_by_community",
        "updated_at",
    )
    list_filter = (
        "category",
        "status",
        "request_status",
        "priority",
        "plan_year",
        "fiscal_year",
        "sector",
        "appropriation_class",
        "funding_source",
        "compliance_gad",
        "compliance_ccet",
        "supports_peace_agenda",
        "lead_organization",
        "submitted_to_organization",
        "communities",
    )
    search_fields = (
        "title",
        "summary",
        "oobc_unit",
        "program_code",
        "plan_reference",
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
    inlines = [
        MonitoringEntryFundingInline,
        MonitoringEntryWorkflowStageInline,
        MonitoringUpdateInline,
    ]
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


@admin.register(MonitoringEntryFunding)
class MonitoringEntryFundingAdmin(admin.ModelAdmin):
    """Admin configuration for detailed funding flows."""

    list_display = (
        "entry",
        "tranche_type",
        "amount",
        "funding_source",
        "scheduled_date",
        "updated_at",
    )
    list_filter = (
        "tranche_type",
        "funding_source",
        "scheduled_date",
    )
    search_fields = (
        "entry__title",
        "remarks",
    )
    autocomplete_fields = ("entry",)
    date_hierarchy = "scheduled_date"


@admin.register(MonitoringEntryWorkflowStage)
class MonitoringEntryWorkflowStageAdmin(admin.ModelAdmin):
    """Admin configuration for workflow stage tracking."""

    list_display = (
        "entry",
        "stage",
        "status",
        "owner_team",
        "owner_organization",
        "due_date",
        "completed_at",
        "updated_at",
    )
    list_filter = (
        "stage",
        "status",
        "owner_team",
        "owner_organization",
    )
    search_fields = (
        "entry__title",
        "notes",
    )
    autocomplete_fields = (
        "entry",
        "owner_team",
        "owner_organization",
    )
    date_hierarchy = "due_date"
