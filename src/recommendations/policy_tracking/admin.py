from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (PolicyDocument, PolicyEvidence, PolicyImpact,
                     PolicyRecommendation)


class PolicyEvidenceInline(admin.TabularInline):
    """Inline admin for policy evidence."""

    model = PolicyEvidence
    extra = 1
    fields = ("title", "evidence_type", "reliability_level", "verified")
    readonly_fields = ("date_added",)


class PolicyImpactInline(admin.TabularInline):
    """Inline admin for policy impacts."""

    model = PolicyImpact
    extra = 1
    fields = (
        "impact_type",
        "title",
        "measurement_type",
        "baseline_value",
        "target_value",
        "current_value",
    )


class PolicyDocumentInline(admin.TabularInline):
    """Inline admin for policy documents."""

    model = PolicyDocument
    extra = 1
    fields = ("document_type", "title", "version", "is_confidential", "is_public")
    readonly_fields = ("upload_date", "file_size")


@admin.register(PolicyRecommendation)
class PolicyRecommendationAdmin(admin.ModelAdmin):
    """Admin interface for Policy Recommendations."""

    list_display = (
        "reference_number",
        "title",
        "category",
        "status",
        "priority",
        "proposed_by",
        "submission_date",
        "is_overdue_indicator",
    )
    list_filter = (
        "status",
        "priority",
        "category",
        "scope",
        "submission_date",
        "approval_date",
        "implementation_start_date",
    )
    search_fields = (
        "title",
        "reference_number",
        "description",
        "rationale",
        "proposed_by__username",
        "proposed_by__first_name",
        "proposed_by__last_name",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "reference_number",
                    "category",
                    "priority",
                    "scope",
                    "status",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "description",
                    "rationale",
                    "problem_statement",
                    "policy_objectives",
                    "proposed_solution",
                    "expected_outcomes",
                )
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    "submission_date",
                    "review_deadline",
                    "approval_date",
                    "implementation_start_date",
                    "implementation_deadline",
                )
            },
        ),
        (
            "Management",
            {
                "fields": (
                    "proposed_by",
                    "lead_author",
                    "contributing_authors",
                    "assigned_reviewer",
                )
            },
        ),
        (
            "Implementation",
            {
                "fields": (
                    "implementation_strategy",
                    "success_metrics",
                    "responsible_agencies",
                    "monitoring_framework",
                    "reporting_requirements",
                )
            },
        ),
        (
            "Impact Assessment",
            {
                "fields": (
                    "potential_risks",
                    "mitigation_strategies",
                    "stakeholder_impact",
                )
            },
        ),
        (
            "Resources",
            {
                "fields": (
                    "estimated_cost",
                    "funding_source",
                    "budget_implications",
                    "human_resources_required",
                    "technical_requirements",
                )
            },
        ),
        (
            "Legal & Regulatory",
            {
                "fields": (
                    "legal_implications",
                    "regulatory_changes_needed",
                    "compliance_requirements",
                )
            },
        ),
        (
            "Review & Feedback",
            {"fields": ("review_comments", "feedback_summary", "revision_history")},
        ),
        (
            "Outcomes & Evaluation",
            {
                "fields": (
                    "actual_outcomes",
                    "lessons_learned",
                    "recommendations_for_improvement",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("notes", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at", "reference_number")

    filter_horizontal = (
        "target_communities",
        "related_assessments",
        "related_needs",
        "contributing_authors",
    )

    inlines = [PolicyEvidenceInline, PolicyImpactInline, PolicyDocumentInline]

    actions = ["mark_under_review", "mark_approved", "mark_in_implementation"]

    def is_overdue_indicator(self, obj):
        """Display overdue status with color coding."""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>'
            )
        return "✅ On Track"

    is_overdue_indicator.short_description = "Status"

    def mark_under_review(self, request, queryset):
        """Mark selected policies as under review."""
        count = queryset.update(status="under_review")
        self.message_user(request, f"{count} policies marked as under review.")

    mark_under_review.short_description = "Mark as Under Review"

    def mark_approved(self, request, queryset):
        """Mark selected policies as approved."""
        count = queryset.update(status="approved")
        self.message_user(request, f"{count} policies marked as approved.")

    mark_approved.short_description = "Mark as Approved"

    def mark_in_implementation(self, request, queryset):
        """Mark selected policies as in implementation."""
        count = queryset.update(status="in_implementation")
        self.message_user(request, f"{count} policies marked as in implementation.")

    mark_in_implementation.short_description = "Mark as In Implementation"


@admin.register(PolicyEvidence)
class PolicyEvidenceAdmin(admin.ModelAdmin):
    """Admin interface for Policy Evidence."""

    list_display = (
        "title",
        "policy",
        "evidence_type",
        "reliability_level",
        "verified",
        "date_added",
    )
    list_filter = (
        "evidence_type",
        "reliability_level",
        "verified",
        "date_added",
        "date_collected",
    )
    search_fields = ("title", "description", "policy__title", "source")
    ordering = ("-date_added",)
    date_hierarchy = "date_added"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("policy", "title", "evidence_type", "description", "source")},
        ),
        (
            "Quality & Reliability",
            {"fields": ("reliability_level", "quality_notes", "methodology")},
        ),
        (
            "Content",
            {"fields": ("key_findings", "relevance_explanation", "statistical_data")},
        ),
        ("Documentation", {"fields": ("document", "url", "reference_citation")}),
        (
            "Verification",
            {
                "fields": (
                    "verified",
                    "verified_by",
                    "verification_date",
                    "verification_notes",
                )
            },
        ),
        ("Timeline", {"fields": ("date_collected", "date_added")}),
        ("Metadata", {"fields": ("added_by", "notes"), "classes": ("collapse",)}),
    )

    readonly_fields = ("date_added",)


@admin.register(PolicyImpact)
class PolicyImpactAdmin(admin.ModelAdmin):
    """Admin interface for Policy Impacts."""

    list_display = (
        "title",
        "policy",
        "impact_type",
        "measurement_type",
        "target_achievement_display",
        "confidence_level",
    )
    list_filter = (
        "impact_type",
        "measurement_type",
        "confidence_level",
        "data_quality",
    )
    search_fields = ("title", "description", "policy__title")
    ordering = ("policy", "impact_type", "title")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("policy", "impact_type", "title", "description")},
        ),
        (
            "Measurement",
            {
                "fields": (
                    "measurement_type",
                    "measurement_method",
                    "unit_of_measurement",
                )
            },
        ),
        (
            "Baseline & Targets",
            {
                "fields": (
                    "baseline_value",
                    "baseline_date",
                    "target_value",
                    "target_date",
                )
            },
        ),
        (
            "Results",
            {
                "fields": (
                    "current_value",
                    "last_measurement_date",
                    "final_value",
                    "final_assessment_date",
                )
            },
        ),
        (
            "Analysis",
            {
                "fields": (
                    "analysis_notes",
                    "variance_explanation",
                    "contributing_factors",
                )
            },
        ),
        ("Quality", {"fields": ("data_quality", "confidence_level")}),
        ("Metadata", {"fields": ("measured_by", "notes"), "classes": ("collapse",)}),
    )

    def target_achievement_display(self, obj):
        """Display target achievement percentage with color coding."""
        percentage = obj.target_achievement_percentage
        if percentage is not None:
            if percentage >= 100:
                color = "green"
                icon = "🎯"
            elif percentage >= 75:
                color = "orange"
                icon = "📈"
            elif percentage >= 50:
                color = "blue"
                icon = "📊"
            else:
                color = "red"
                icon = "📉"

            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {}%</span>',
                color,
                icon,
                percentage,
            )
        return "—"

    target_achievement_display.short_description = "Achievement"


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    """Admin interface for Policy Documents."""

    list_display = (
        "title",
        "policy",
        "document_type",
        "version",
        "access_level_display",
        "author",
        "upload_date",
    )
    list_filter = (
        "document_type",
        "is_confidential",
        "is_public",
        "upload_date",
        "document_date",
    )
    search_fields = ("title", "description", "policy__title", "author")
    ordering = ("-upload_date",)
    date_hierarchy = "upload_date"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("policy", "document_type", "title", "description", "version")},
        ),
        (
            "File Information",
            {"fields": ("file", "file_size", "document_date", "author")},
        ),
        ("Access Control", {"fields": ("is_confidential", "is_public")}),
        (
            "Metadata",
            {
                "fields": ("uploaded_by", "upload_date", "notes"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("upload_date", "file_size")

    def access_level_display(self, obj):
        """Display access level with color coding."""
        if obj.is_confidential:
            return format_html(
                '<span style="color: red; font-weight: bold;">🔒 CONFIDENTIAL</span>'
            )
        elif obj.is_public:
            return format_html(
                '<span style="color: green; font-weight: bold;">🌐 PUBLIC</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">👥 INTERNAL</span>'
            )

    access_level_display.short_description = "Access Level"
