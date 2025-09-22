from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (ActionItem, Communication, CommunicationSchedule,
                     CommunicationTemplate, ConsultationFeedback,
                     EngagementFacilitator, EngagementTracking, Event,
                     EventDocument, EventParticipant, Organization,
                     OrganizationContact, Partnership, PartnershipDocument,
                     PartnershipMilestone, PartnershipSignatory,
                     StakeholderEngagement, StakeholderEngagementType)


# Organization Admin
class OrganizationContactInline(admin.TabularInline):
    """Inline admin for organization contacts."""

    model = OrganizationContact
    extra = 1
    fields = (
        "first_name",
        "last_name",
        "position",
        "email",
        "phone",
        "is_primary",
        "is_active",
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organizations."""

    list_display = (
        "name",
        "organization_type",
        "partnership_status",
        "primary_contact_display",
        "address",
        "partnership_count",
    )
    list_filter = ("organization_type", "partnership_status", "created_at")
    search_fields = ("name", "acronym", "description", "address")
    ordering = ("name",)
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "acronym",
                    "organization_type",
                    "partnership_level",
                    "partnership_status",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "address",
                    "mailing_address",
                    "phone",
                    "mobile",
                    "email",
                    "website",
                    "social_media",
                )
            },
        ),
        (
            "Key Personnel",
            {
                "fields": (
                    "head_of_organization",
                    "head_position",
                    "focal_person",
                    "focal_person_position",
                    "focal_person_contact",
                    "focal_person_email",
                )
            },
        ),
        ("Partnership Information", {"fields": ("partnership_start_date",)}),
        (
            "Operational Details",
            {
                "fields": (
                    "areas_of_expertise",
                    "geographic_coverage",
                    "target_beneficiaries",
                    "annual_budget",
                    "staff_count",
                )
            },
        ),
        (
            "Administrative Information",
            {
                "fields": (
                    "registration_number",
                    "tax_identification_number",
                    "accreditation_details",
                )
            },
        ),
        (
            "Engagement History",
            {"fields": ("last_engagement_date", "engagement_frequency")},
        ),
        ("Notes and Status", {"fields": ("notes", "is_active", "is_priority")}),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")
    inlines = [OrganizationContactInline]

    def primary_contact_display(self, obj):
        """Display primary contact information."""
        primary = obj.contacts.filter(is_primary=True, is_active=True).first()
        if primary:
            return f"{primary.contact_person} ({primary.email})"
        return "No primary contact"

    primary_contact_display.short_description = "Primary Contact"

    def partnership_count(self, obj):
        """Display number of partnerships."""
        count = obj.partnerships_as_lead.count() + obj.partnerships_as_partner.count()
        return f"{count} partnerships"

    partnership_count.short_description = "Partnerships"


@admin.register(OrganizationContact)
class OrganizationContactAdmin(admin.ModelAdmin):
    """Admin interface for Organization Contacts."""

    list_display = (
        "full_name",
        "organization",
        "position",
        "email",
        "phone",
        "is_primary",
        "is_active",
    )
    list_filter = ("is_primary", "is_active", "organization__organization_type")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "organization__name",
        "position",
    )
    ordering = ("organization__name", "first_name", "last_name")

    def full_name(self, obj):
        """Display full name."""
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "Contact Person"


# Event Admin
class EventParticipantInline(admin.TabularInline):
    """Inline admin for event participants."""

    model = EventParticipant
    extra = 1
    fields = (
        "name",
        "organization",
        "participation_role",
        "response_status",
        "satisfaction_rating",
    )


class ActionItemInline(admin.TabularInline):
    """Inline admin for action items."""

    model = ActionItem
    extra = 1
    fields = ("description", "assigned_to", "due_date", "priority", "status")


class EventDocumentInline(admin.TabularInline):
    """Inline admin for event documents."""

    model = EventDocument
    extra = 1
    fields = ("document_type", "title", "file", "is_public")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Events."""

    list_display = (
        "title",
        "event_type",
        "start_date",
        "venue",
        "status",
        "participant_count",
        "action_items_count",
    )
    list_filter = ("event_type", "status", "start_date", "is_virtual")
    search_fields = ("title", "description", "venue", "organizer")
    ordering = ("-start_date",)
    date_hierarchy = "start_date"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "event_type", "status", "organizer")},
        ),
        ("Schedule", {"fields": ("start_date", "end_date", "duration_hours")}),
        (
            "Location",
            {
                "fields": (
                    "is_virtual",
                    "venue",
                    "venue_details",
                    "virtual_meeting_link",
                )
            },
        ),
        (
            "Content",
            {"fields": ("description", "objectives", "agenda", "target_participants")},
        ),
        (
            "Logistics",
            {
                "fields": (
                    "maximum_participants",
                    "registration_required",
                    "registration_deadline",
                    "budget",
                    "logistics_notes",
                )
            },
        ),
        ("Outcomes", {"fields": ("outcomes", "follow_up_actions", "lessons_learned")}),
        (
            "Metadata",
            {"fields": ("notes", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at")
    inlines = [EventParticipantInline, ActionItemInline, EventDocumentInline]

    def participant_count(self, obj):
        """Display participant count with status breakdown."""
        total = obj.participants.count()
        confirmed = obj.participants.filter(response_status="confirmed").count()
        return f"{confirmed}/{total} confirmed"

    participant_count.short_description = "Participants"

    def action_items_count(self, obj):
        """Display action items count with status."""
        total = obj.action_items.count()
        pending = obj.action_items.filter(status="pending").count()
        if pending > 0:
            return format_html(
                '<span style="color: orange;">{} pending / {} total</span>',
                pending,
                total,
            )
        return f"{total} total"

    action_items_count.short_description = "Action Items"


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    """Admin interface for Event Participants."""

    list_display = (
        "name",
        "event",
        "organization",
        "participation_role",
        "response_status",
        "satisfaction_rating",
    )
    list_filter = ("response_status", "participation_role", "event__event_type")
    search_fields = ("name", "organization", "event__title")
    ordering = ("event__start_date", "name")


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    """Admin interface for Action Items."""

    list_display = (
        "description_short",
        "event",
        "assigned_to",
        "due_date",
        "priority",
        "status",
        "overdue_indicator",
    )
    list_filter = ("status", "priority", "due_date", "event__event_type")
    search_fields = ("description", "assigned_to", "event__title")
    ordering = ("due_date", "priority")
    date_hierarchy = "due_date"

    def description_short(self, obj):
        """Display shortened description."""
        return (
            obj.description[:50] + "..."
            if len(obj.description) > 50
            else obj.description
        )

    description_short.short_description = "Description"

    def overdue_indicator(self, obj):
        """Display overdue status."""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>'
            )
        return "✅"

    overdue_indicator.short_description = "Status"


# Partnership Admin
class PartnershipSignatoryInline(admin.TabularInline):
    """Inline admin for partnership signatories."""

    model = PartnershipSignatory
    extra = 1
    fields = ("organization", "name", "position", "signature_date")


class PartnershipMilestoneInline(admin.TabularInline):
    """Inline admin for partnership milestones."""

    model = PartnershipMilestone
    extra = 1
    fields = ("title", "due_date", "status", "progress_percentage")


class PartnershipDocumentInline(admin.TabularInline):
    """Inline admin for partnership documents."""

    model = PartnershipDocument
    extra = 1
    fields = ("document_type", "title", "file", "is_confidential")


@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    """Admin interface for Partnerships."""

    list_display = (
        "title",
        "partnership_type",
        "status",
        "lead_organization",
        "start_date",
        "milestone_progress",
    )
    list_filter = ("partnership_type", "status", "start_date")
    search_fields = ("title", "description", "lead_organization__name")
    ordering = ("-start_date",)
    date_hierarchy = "start_date"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "partnership_type",
                    "status",
                    "priority",
                    "progress_percentage",
                )
            },
        ),
        (
            "Partners",
            {
                "fields": (
                    "lead_organization",
                    "organizations",
                    "communities",
                    "focal_person",
                    "backup_focal_person",
                )
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    "concept_date",
                    "negotiation_start_date",
                    "signing_date",
                    "start_date",
                    "end_date",
                    "renewal_date",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "description",
                    "objectives",
                    "scope",
                    "expected_outcomes",
                    "actual_outcomes",
                    "lessons_learned",
                )
            },
        ),
        (
            "Financials",
            {"fields": ("total_budget", "oobc_contribution", "partner_contribution")},
        ),
        (
            "Legal & Documentation",
            {"fields": ("document_number", "legal_reference", "termination_clause")},
        ),
        (
            "Monitoring & Risk",
            {
                "fields": (
                    "key_performance_indicators",
                    "reporting_requirements",
                    "communication_plan",
                    "risks_identified",
                    "mitigation_strategies",
                )
            },
        ),
        ("Renewal", {"fields": ("is_renewable", "renewal_criteria")}),
        (
            "Metadata",
            {
                "fields": ("notes", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("organizations", "communities")
    inlines = [
        PartnershipSignatoryInline,
        PartnershipMilestoneInline,
        PartnershipDocumentInline,
    ]

    def milestone_progress(self, obj):
        """Display milestone completion progress."""
        milestones = obj.milestones.all()
        if not milestones:
            return "No milestones"

        total = milestones.count()
        completed = milestones.filter(status="completed").count()
        percentage = (completed / total) * 100 if total > 0 else 0

        if percentage == 100:
            color = "green"
            icon = "✅"
        elif percentage >= 50:
            color = "orange"
            icon = "🟡"
        else:
            color = "red"
            icon = "🔴"

        return format_html(
            '<span style="color: {};">{} {}/{} ({}%)</span>',
            color,
            icon,
            completed,
            total,
            int(percentage),
        )

    milestone_progress.short_description = "Progress"


# Communication Admin
@admin.register(CommunicationTemplate)
class CommunicationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for Communication Templates."""

    list_display = (
        "name",
        "template_type",
        "subject_template",
        "language",
        "is_active",
    )
    list_filter = ("template_type", "language", "is_active")
    search_fields = ("name", "subject_template", "content")
    ordering = ("template_type", "name")


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    """Admin interface for Communications."""

    list_display = (
        "subject",
        "communication_type",
        "sender",
        "recipient_count",
        "communication_date",
        "status",
    )
    list_filter = ("communication_type", "status", "communication_date")
    search_fields = ("subject", "content", "sender__username")
    ordering = ("-communication_date",)
    date_hierarchy = "communication_date"

    def recipient_count(self, obj):
        """Display recipient count."""
        return len(obj.recipients.split(",")) if obj.recipients else 0

    recipient_count.short_description = "Recipients"


# Stakeholder Engagement Admin
@admin.register(StakeholderEngagementType)
class StakeholderEngagementTypeAdmin(admin.ModelAdmin):
    """Admin interface for Stakeholder Engagement Types."""

    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    ordering = ("category", "name")


@admin.register(StakeholderEngagement)
class StakeholderEngagementAdmin(admin.ModelAdmin):
    """Admin interface for Stakeholder Engagements."""

    list_display = (
        "title",
        "engagement_type",
        "status",
        "community_display",
        "planned_date",
        "participant_count",
    )
    list_filter = ("engagement_type", "status", "planned_date")
    search_fields = ("title", "description", "facilitator")
    ordering = ("-planned_date",)
    date_hierarchy = "planned_date"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "engagement_type", "status", "facilitator")},
        ),
        (
            "Target",
            {
                "fields": (
                    "community",
                    "target_stakeholder_types",
                    "expected_participants",
                )
            },
        ),
        ("Schedule", {"fields": ("planned_date", "duration_hours", "venue")}),
        ("Content", {"fields": ("description", "objectives", "methodology", "agenda")}),
        (
            "Preparation",
            {
                "fields": (
                    "preparation_activities",
                    "materials_needed",
                    "logistics_requirements",
                )
            },
        ),
        (
            "Outcomes",
            {"fields": ("key_outcomes", "recommendations", "follow_up_actions")},
        ),
        (
            "Evaluation",
            {
                "fields": (
                    "satisfaction_rating",
                    "effectiveness_rating",
                    "lessons_learned",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("notes", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def community_display(self, obj):
        """Display community."""
        return obj.community.name if obj.community else "No community"

    community_display.short_description = "Community"

    def participant_count(self, obj):
        """Display actual participant count if available."""
        return obj.actual_participants or obj.expected_participants or "TBD"

    participant_count.short_description = "Participants"


@admin.register(EngagementFacilitator)
class EngagementFacilitatorAdmin(admin.ModelAdmin):
    """Admin interface for Engagement Facilitators."""

    list_display = ("user", "engagement", "role")
    list_filter = ("role", "engagement__engagement_type")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "engagement__title",
    )
    ordering = ("user__last_name", "user__first_name")


@admin.register(ConsultationFeedback)
class ConsultationFeedbackAdmin(admin.ModelAdmin):
    """Admin interface for Consultation Feedback."""

    list_display = ("engagement", "feedback_type", "priority_level", "created_at")
    list_filter = ("feedback_type", "priority_level", "created_at")
    search_fields = ("feedback_content", "engagement__title", "respondent_name")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"


@admin.register(EngagementTracking)
class EngagementTrackingAdmin(admin.ModelAdmin):
    """Admin interface for Engagement Tracking."""

    list_display = (
        "community",
        "period_type",
        "period_start",
        "period_end",
        "calculated_at",
    )
    list_filter = ("period_type", "period_start", "period_end", "calculated_at")
    search_fields = ("community__name", "calculated_by__username")
    ordering = ("-period_start",)


# Additional Admin Registrations
@admin.register(EventDocument)
class EventDocumentAdmin(admin.ModelAdmin):
    """Admin interface for Event Documents."""

    list_display = ("title", "event", "document_type", "is_public", "upload_date")
    list_filter = ("document_type", "is_public", "upload_date")
    search_fields = ("title", "event__title", "description")
    ordering = ("-upload_date",)


@admin.register(PartnershipSignatory)
class PartnershipSignatoryAdmin(admin.ModelAdmin):
    """Admin interface for Partnership Signatories."""

    list_display = ("name", "partnership", "organization", "position", "signature_date")
    list_filter = ("signature_date", "organization")
    search_fields = ("name", "partnership__title", "organization__name")
    ordering = ("-signature_date",)


@admin.register(PartnershipMilestone)
class PartnershipMilestoneAdmin(admin.ModelAdmin):
    """Admin interface for Partnership Milestones."""

    list_display = (
        "title",
        "partnership",
        "due_date",
        "status",
        "progress_percentage",
        "overdue_indicator",
    )
    list_filter = ("status", "due_date")
    search_fields = ("title", "partnership__title", "description")
    ordering = ("due_date",)

    def overdue_indicator(self, obj):
        """Display overdue status for milestones."""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>'
            )
        return "✅"

    overdue_indicator.short_description = "Status"


@admin.register(PartnershipDocument)
class PartnershipDocumentAdmin(admin.ModelAdmin):
    """Admin interface for Partnership Documents."""

    list_display = (
        "title",
        "partnership",
        "document_type",
        "access_level_display",
        "upload_date",
    )
    list_filter = ("document_type", "is_confidential", "upload_date")
    search_fields = ("title", "partnership__title", "description")
    ordering = ("-upload_date",)

    def access_level_display(self, obj):
        """Display access level with color coding."""
        if obj.is_confidential:
            return format_html(
                '<span style="color: red; font-weight: bold;">🔒 CONFIDENTIAL</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">📋 STANDARD</span>'
            )

    access_level_display.short_description = "Access Level"


@admin.register(CommunicationSchedule)
class CommunicationScheduleAdmin(admin.ModelAdmin):
    """Admin interface for Communication Schedules."""

    list_display = (
        "title",
        "schedule_type",
        "recurrence_pattern",
        "next_execution",
        "is_active",
        "last_executed",
    )
    list_filter = ("schedule_type", "recurrence_pattern", "is_active")
    search_fields = ("title", "template__name", "target_audience")
    ordering = ("next_execution",)
