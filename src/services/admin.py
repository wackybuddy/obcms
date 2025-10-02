from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import ServiceOffering, ServiceApplication


@admin.register(ServiceOffering)
class ServiceOfferingAdmin(admin.ModelAdmin):
    """Admin interface for Service Offerings."""

    list_display = (
        "title",
        "service_type_badge",
        "offering_mao_link",
        "status_badge",
        "application_period",
        "slots_indicator",
        "budget_indicator",
        "accepting_applications",
    )

    list_filter = (
        "service_type",
        "status",
        "eligibility_level",
        "offering_mao",
        "application_start_date",
    )

    search_fields = (
        "title",
        "description",
        "offering_mao__name",
        "offering_mao__acronym",
    )

    autocomplete_fields = (
        "offering_mao",
        "focal_person",
        "linked_ppas",
        "created_by",
    )

    filter_horizontal = ("linked_ppas",)

    date_hierarchy = "application_start_date"

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "service_type",
                    "description",
                    "objectives",
                )
            },
        ),
        (
            "Offering Organization",
            {
                "fields": (
                    "offering_mao",
                    "focal_person",
                )
            },
        ),
        (
            "Eligibility",
            {
                "fields": (
                    "eligibility_level",
                    "eligibility_criteria",
                    "required_documents",
                )
            },
        ),
        (
            "Funding & Capacity",
            {
                "fields": (
                    ("budget_allocated", "budget_utilized"),
                    ("total_slots", "slots_filled"),
                )
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    ("application_start_date", "application_deadline"),
                    ("service_start_date", "service_end_date"),
                )
            },
        ),
        (
            "Status & Process",
            {
                "fields": (
                    "status",
                    "application_process",
                    "contact_information",
                )
            },
        ),
        (
            "Budget Linkage",
            {
                "fields": ("linked_ppas",),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def service_type_badge(self, obj):
        """Service type with color coding."""
        colors = {
            "financial": "#10b981",
            "training": "#3b82f6",
            "livelihood": "#8b5cf6",
            "education": "#f59e0b",
            "health": "#ef4444",
            "infrastructure": "#6b7280",
            "legal": "#14b8a6",
            "social": "#ec4899",
            "technical": "#6366f1",
            "other": "#9ca3af",
        }
        color = colors.get(obj.service_type, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_service_type_display(),
        )

    service_type_badge.short_description = "Type"
    service_type_badge.admin_order_field = "service_type"

    def offering_mao_link(self, obj):
        """Link to MAO organization."""
        url = reverse(
            "admin:coordination_organization_change", args=[obj.offering_mao.pk]
        )
        display = obj.offering_mao.acronym or obj.offering_mao.name[:30]
        return format_html('<a href="{}">{}</a>', url, display)

    offering_mao_link.short_description = "MAO"
    offering_mao_link.admin_order_field = "offering_mao__name"

    def status_badge(self, obj):
        """Status with color coding."""
        colors = {
            "draft": "#9ca3af",
            "active": "#10b981",
            "paused": "#f59e0b",
            "closed": "#ef4444",
            "archived": "#6b7280",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def application_period(self, obj):
        """Display application period."""
        if obj.application_start_date and obj.application_deadline:
            return f"{obj.application_start_date.strftime('%b %d')} - {obj.application_deadline.strftime('%b %d, %Y')}"
        return "No deadline set"

    application_period.short_description = "Application Period"

    def slots_indicator(self, obj):
        """Slots utilization indicator."""
        if not obj.total_slots:
            return "-"
        rate = obj.slots_utilization_rate
        color = "#10b981" if rate < 80 else "#f59e0b" if rate < 100 else "#ef4444"
        return format_html(
            '<div style="width: 100px;">'
            '<div style="background: #e5e7eb; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; padding: 2px 4px; text-align: center; color: white; font-size: 10px; font-weight: 600;">'
            "{}/{}"
            "</div></div></div>",
            min(rate, 100),
            color,
            obj.slots_filled,
            obj.total_slots,
        )

    slots_indicator.short_description = "Slots"

    def budget_indicator(self, obj):
        """Budget utilization indicator."""
        if not obj.budget_allocated:
            return "-"
        rate = obj.budget_utilization_rate
        color = "#10b981" if rate < 80 else "#f59e0b" if rate < 100 else "#ef4444"
        return format_html(
            '<div style="width: 80px; font-size: 11px;">'
            '<div style="background: #e5e7eb; border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 2px;">'
            '<div style="width: {}%; background: {}; height: 100%;"></div>'
            "</div>"
            '<div style="color: #6b7280;">{:.0f}%</div>'
            "</div>",
            min(rate, 100),
            color,
            rate,
        )

    budget_indicator.short_description = "Budget"

    def accepting_applications(self, obj):
        """Show if currently accepting applications."""
        if obj.is_accepting_applications:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">✓ Open</span>'
            )
        return format_html('<span style="color: #6b7280;">✗ Closed</span>')

    accepting_applications.short_description = "Applications"
    accepting_applications.boolean = True


@admin.register(ServiceApplication)
class ServiceApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Service Applications."""

    list_display = (
        "service_link",
        "applicant_display",
        "submission_date_display",
        "status_badge",
        "requested_amount_display",
        "processing_time",
        "satisfaction_display",
    )

    list_filter = (
        "status",
        "service__service_type",
        "service__offering_mao",
        "submission_date",
        "satisfaction_rating",
    )

    search_fields = (
        "service__title",
        "applicant_name",
        "applicant_user__username",
        "applicant_user__first_name",
        "applicant_user__last_name",
        "applicant_community__barangay__name",
        "application_details",
    )

    autocomplete_fields = (
        "service",
        "applicant_community",
        "applicant_user",
        "reviewed_by",
    )

    date_hierarchy = "submission_date"

    ordering = ("-submission_date", "-created_at")

    fieldsets = (
        (
            "Application",
            {
                "fields": (
                    "service",
                    "status",
                )
            },
        ),
        (
            "Applicant Information",
            {
                "fields": (
                    "applicant_user",
                    "applicant_community",
                    "applicant_name",
                    "applicant_contact",
                )
            },
        ),
        (
            "Application Details",
            {
                "fields": (
                    "application_details",
                    ("requested_amount", "beneficiary_count"),
                )
            },
        ),
        (
            "Review & Decision",
            {
                "fields": (
                    ("submission_date", "reviewed_by", "review_date"),
                    "review_notes",
                    "approval_date",
                    "rejection_reason",
                )
            },
        ),
        (
            "Service Delivery",
            {
                "fields": (
                    ("service_start_date", "service_completion_date"),
                    "actual_amount_received",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Feedback",
            {
                "fields": (
                    "satisfaction_rating",
                    "feedback",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def service_link(self, obj):
        """Link to service offering."""
        url = reverse("admin:services_serviceoffering_change", args=[obj.service.pk])
        return format_html('<a href="{}">{}</a>', url, obj.service.title[:50])

    service_link.short_description = "Service"
    service_link.admin_order_field = "service__title"

    def applicant_display(self, obj):
        """Display applicant information."""
        if obj.applicant_community:
            return str(obj.applicant_community)
        elif obj.applicant_name:
            return obj.applicant_name
        return obj.applicant_user.get_full_name() or obj.applicant_user.username

    applicant_display.short_description = "Applicant"

    def submission_date_display(self, obj):
        """Display submission date."""
        if obj.submission_date:
            return obj.submission_date.strftime("%b %d, %Y")
        return "Not submitted"

    submission_date_display.short_description = "Submitted"
    submission_date_display.admin_order_field = "submission_date"

    def status_badge(self, obj):
        """Status with color coding."""
        colors = {
            "draft": "#9ca3af",
            "submitted": "#3b82f6",
            "under_review": "#8b5cf6",
            "additional_info_required": "#f59e0b",
            "approved": "#10b981",
            "rejected": "#ef4444",
            "waitlisted": "#f59e0b",
            "in_progress": "#06b6d4",
            "completed": "#059669",
            "cancelled": "#6b7280",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def requested_amount_display(self, obj):
        """Display requested amount."""
        if obj.requested_amount:
            return f"₱{obj.requested_amount:,.2f}"
        return "-"

    requested_amount_display.short_description = "Amount"

    def processing_time(self, obj):
        """Display processing time."""
        days = obj.processing_time_days
        if days is None:
            return "-"
        if days <= 7:
            color = "#10b981"
        elif days <= 30:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        return format_html(
            '<span style="color: {}; font-weight: 600;">{} days</span>',
            color,
            days,
        )

    processing_time.short_description = "Processing"

    def satisfaction_display(self, obj):
        """Display satisfaction rating."""
        if obj.satisfaction_rating:
            stars = "★" * obj.satisfaction_rating + "☆" * (5 - obj.satisfaction_rating)
            return format_html('<span style="color: #f59e0b;">{}</span>', stars)
        return "-"

    satisfaction_display.short_description = "Rating"
