from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    CommunityEvent,
    CommunityInfrastructure,
    CommunityLivelihood,
    GeographicDataLayer,
    MapVisualization,
    MunicipalityCoverage,
    OBCCommunity,
    ProvinceCoverage,
    SpatialDataPoint,
    Stakeholder,
    StakeholderEngagement,
)


class CommunityLivelihoodInline(admin.TabularInline):
    """Inline admin for community livelihoods."""

    model = CommunityLivelihood
    extra = 1
    fields = (
        "livelihood_type",
        "specific_activity",
        "households_involved",
        "percentage_of_community",
        "is_primary_livelihood",
        "income_level",
    )


class CommunityInfrastructureInline(admin.TabularInline):
    """Inline admin for community infrastructure."""

    model = CommunityInfrastructure
    extra = 1
    fields = (
        "infrastructure_type",
        "availability_status",
        "coverage_percentage",
        "condition",
        "priority_for_improvement",
    )


class StakeholderInline(admin.TabularInline):
    """Inline admin for community stakeholders."""

    model = Stakeholder
    extra = 1
    fields = (
        "full_name",
        "nickname",
        "stakeholder_type",
        "position",
        "contact_number",
        "influence_level",
        "is_active",
    )
    readonly_fields = ("created_at",)


@admin.register(OBCCommunity)
class OBCCommunityAdmin(admin.ModelAdmin):
    """Admin interface for OBC Community model."""

    list_display = (
        "barangay",
        "municipality",
        "province",
        "region",
        "estimated_obc_population",
        "households",
        "unemployment_rate",
        "is_active",
    )
    list_filter = (
        "unemployment_rate",
        "settlement_type",
        "is_active",
        "barangay__municipality__province__region",
        "barangay__municipality__province",
        "barangay__municipality",
        "mosques_count",
        "madrasah_count",
        "asatidz_count",
    )
    search_fields = (
        "barangay__name",
        "barangay__municipality__name",
        "barangay__municipality__province__name",
        "community_leader",
        "community_names",
        "obc_id",
    )
    ordering = (
        "barangay__municipality__province__region__code",
        "barangay__municipality__province__name",
        "barangay__municipality__name",
        "barangay__name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "full_location",
        "total_age_demographics",
        "average_household_size",
        "percentage_obc_in_barangay",
        "coordinates",
    )

    inlines = [
        CommunityLivelihoodInline,
        CommunityInfrastructureInline,
        StakeholderInline,
    ]

    fieldsets = (
        (
            "Identification & Location",
            {
                "fields": (
                    ("obc_id", "source_document_reference"),
                    ("community_names",),
                    ("barangay", "purok_sitio"),
                    ("specific_location", "settlement_type"),
                    ("latitude", "longitude", "coordinates"),
                    ("proximity_to_barmm", "is_active"),
                )
            },
        ),
        (
            "Demographics",
            {
                "fields": (
                    (
                        "estimated_obc_population",
                        "total_barangay_population",
                        "percentage_obc_in_barangay",
                    ),
                    ("households", "families", "average_household_size"),
                    (
                        "children_0_9",
                        "adolescents_10_14",
                        "youth_15_30",
                        "adults_31_59",
                        "seniors_60_plus",
                    ),
                    ("total_age_demographics",),
                    ("primary_ethnolinguistic_group", "other_ethnolinguistic_groups"),
                    ("languages_spoken",),
                )
            },
        ),
        (
            "Vulnerable Sectors",
            {
                "fields": (
                    ("women_count", "solo_parents_count", "pwd_count"),
                    ("farmers_count", "fisherfolk_count", "unemployed_count"),
                    (
                        "indigenous_peoples_count",
                        "idps_count",
                        "migrants_transients_count",
                    ),
                    (
                        "csos_count",
                        "associations_count",
                        "number_of_peoples_organizations",
                    ),
                    (
                        "number_of_cooperatives",
                        "number_of_social_enterprises",
                        "number_of_micro_enterprises",
                    ),
                    ("other_vulnerable_sectors",),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Socio-Economic Profile",
            {
                "fields": (
                    ("primary_livelihoods", "secondary_livelihoods"),
                    ("estimated_poverty_incidence",),
                    ("land_tenure_issues",),
                    ("financial_access_level", "number_of_unbanked_obc"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Access to Basic Services",
            {
                "fields": (
                    ("access_formal_education", "access_als", "access_madrasah"),
                    ("access_healthcare", "access_clean_water", "access_sanitation"),
                    (
                        "access_electricity",
                        "access_roads_transport",
                        "access_communication",
                    ),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Cultural & Historical Context",
            {
                "fields": (
                    ("brief_historical_background",),
                    ("established_year", "origin_story", "migration_history"),
                    ("cultural_practices_traditions", "religious_affiliation"),
                    ("traditional_leaders_role", "cultural_preservation_efforts"),
                    (
                        "mosques_count",
                        "madrasah_count",
                        "asatidz_count",
                        "religious_leaders_count",
                    ),
                    ("other_cultural_facilities",),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Governance & Leadership",
            {
                "fields": (
                    (
                        "formal_political_representation",
                        "informal_leadership_structures",
                    ),
                    ("community_organizations", "relationship_with_lgu"),
                    ("participation_local_governance", "access_government_info"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Challenges & Barriers",
            {
                "fields": (
                    (
                        "governance_policy_challenges",
                        "access_public_services_challenges",
                    ),
                    ("land_ownership_security_issues", "economic_disparities"),
                    ("social_instability_conflict", "cultural_miscommunication"),
                    ("gender_inequality_issues", "substance_abuse_issues"),
                    ("investment_scam_issues", "environmental_degradation"),
                    ("other_challenges", "challenges_impact"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Community Aspirations & Priorities",
            {
                "fields": (
                    ("key_aspirations",),
                    ("infrastructure_priorities", "livelihood_program_priorities"),
                    ("education_priorities", "healthcare_priorities"),
                    ("cultural_preservation_priorities", "peace_security_priorities"),
                    ("specific_project_proposals",),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Unemployment & Assessment",
            {
                "fields": (
                    ("unemployment_rate",),
                    ("needs_assessment_date", "key_findings_last_assessment"),
                    ("assessment_data_sources", "identified_gaps"),
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    ("key_community_leaders", "relevant_lgu_officials"),
                    ("community_leader", "leader_contact"),
                )
            },
        ),
        (
            "Administrative",
            {"fields": ("notes", "full_location"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def municipality(self, obj):
        """Display municipality name."""
        return obj.municipality.name

    municipality.short_description = "Municipality"
    municipality.admin_order_field = "barangay__municipality__name"

    def province(self, obj):
        """Display province name."""
        return obj.province.name

    province.short_description = "Province"
    province.admin_order_field = "barangay__municipality__province__name"

    def region(self, obj):
        """Display region name."""
        return obj.region.name

    region.short_description = "Region"
    region.admin_order_field = "barangay__municipality__province__region__name"

    def colored_unemployment_rate(self, obj):
        """Display unemployment rate with color coding."""
        colors = {
            "very_low": "#16a34a",
            "low": "#22c55e",
            "moderate": "#f97316",
            "high": "#f97316",
            "very_high": "#ef4444",
            "extremely_high": "#b91c1c",
            "unknown": "#6b7280",
        }
        color = colors.get(obj.unemployment_rate, "#374151")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_unemployment_rate_display(),
        )

    colored_unemployment_rate.short_description = "Unemployment Rate"
    actions = [
        "mark_unemployment_low",
        "mark_unemployment_moderate",
        "mark_unemployment_high",
    ]

    def mark_unemployment_low(self, request, queryset):
        updated = queryset.update(unemployment_rate="low")
        self.message_user(
            request, f"{updated} communities marked with low unemployment."
        )

    mark_unemployment_low.short_description = "Mark unemployment rate as Low"

    def mark_unemployment_moderate(self, request, queryset):
        updated = queryset.update(unemployment_rate="moderate")
        self.message_user(
            request, f"{updated} communities marked with moderate unemployment."
        )

    mark_unemployment_moderate.short_description = "Mark unemployment rate as Moderate"

    def mark_unemployment_high(self, request, queryset):
        updated = queryset.update(unemployment_rate="high")
        self.message_user(
            request, f"{updated} communities marked with high unemployment."
        )

    mark_unemployment_high.short_description = "Mark unemployment rate as High"


@admin.register(CommunityLivelihood)
class CommunityLivelihoodAdmin(admin.ModelAdmin):
    """Admin interface for Community Livelihood model."""

    list_display = (
        "specific_activity",
        "community",
        "livelihood_type",
        "households_involved",
        "percentage_of_community",
        "is_primary_livelihood",
        "income_level",
        "seasonal",
    )
    list_filter = (
        "livelihood_type",
        "is_primary_livelihood",
        "seasonal",
        "income_level",
        "community__unemployment_rate",
        "community__barangay__municipality__province__region",
    )
    search_fields = ("specific_activity", "description", "community__barangay__name")
    ordering = (
        "community__barangay__name",
        "-is_primary_livelihood",
        "livelihood_type",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("community", "livelihood_type", "specific_activity")},
        ),
        (
            "Participation Details",
            {
                "fields": (
                    ("households_involved", "percentage_of_community"),
                    ("is_primary_livelihood", "seasonal"),
                    "income_level",
                )
            },
        ),
        (
            "Description & Analysis",
            {"fields": ("description", "challenges", "opportunities")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(CommunityInfrastructure)
class CommunityInfrastructureAdmin(admin.ModelAdmin):
    """Admin interface for Community Infrastructure model."""

    list_display = (
        "infrastructure_type",
        "community",
        "availability_status",
        "coverage_percentage",
        "condition",
        "priority_for_improvement",
    )
    list_filter = (
        "infrastructure_type",
        "availability_status",
        "condition",
        "priority_for_improvement",
        "community__unemployment_rate",
        "community__barangay__municipality__province__region",
    )
    search_fields = ("description", "notes", "community__barangay__name")
    ordering = ("community__barangay__name", "infrastructure_type")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("community", "infrastructure_type", "availability_status")},
        ),
        (
            "Assessment Details",
            {
                "fields": (
                    ("coverage_percentage", "condition"),
                    "priority_for_improvement",
                    "last_assessed",
                )
            },
        ),
        ("Description & Notes", {"fields": ("description", "notes")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def colored_priority(self, obj):
        """Display priority with color coding."""
        colors = {
            "critical": "darkred",
            "high": "red",
            "medium": "orange",
            "low": "green",
        }
        color = colors.get(obj.priority_for_improvement, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_for_improvement_display(),
        )

    colored_priority.short_description = "Priority"

    actions = ["mark_as_critical", "mark_as_high_priority", "mark_as_low_priority"]

    def mark_as_critical(self, request, queryset):
        """Mark selected infrastructure as critical priority."""
        updated = queryset.update(priority_for_improvement="critical")
        self.message_user(
            request, f"{updated} infrastructure items marked as critical."
        )

    mark_as_critical.short_description = "Mark as Critical Priority"

    def mark_as_high_priority(self, request, queryset):
        """Mark selected infrastructure as high priority."""
        updated = queryset.update(priority_for_improvement="high")
        self.message_user(
            request, f"{updated} infrastructure items marked as high priority."
        )

    mark_as_high_priority.short_description = "Mark as High Priority"

    def mark_as_low_priority(self, request, queryset):
        """Mark selected infrastructure as low priority."""
        updated = queryset.update(priority_for_improvement="low")
        self.message_user(
            request, f"{updated} infrastructure items marked as low priority."
        )

    mark_as_low_priority.short_description = "Mark as Low Priority"


class StakeholderEngagementInline(admin.TabularInline):
    """Inline admin for stakeholder engagements."""

    model = StakeholderEngagement
    extra = 0
    fields = ("date", "engagement_type", "title", "outcome", "follow_up_needed")
    readonly_fields = ("created_at",)
    ordering = ("-date",)


@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    """Admin interface for Stakeholder model."""

    list_display = (
        "display_name_with_type",
        "community",
        "stakeholder_type",
        "position",
        "influence_level",
        "engagement_level",
        "contact_info_short",
        "is_active",
        "is_verified",
    )
    list_filter = (
        "stakeholder_type",
        "influence_level",
        "engagement_level",
        "is_active",
        "is_verified",
        "community__barangay__municipality__province__region",
        "community__unemployment_rate",
    )
    search_fields = (
        "full_name",
        "nickname",
        "position",
        "organization",
        "community__barangay__name",
        "contact_number",
        "email",
    )
    ordering = ("community__barangay__name", "stakeholder_type", "full_name")
    readonly_fields = ("created_at", "updated_at", "years_of_service", "contact_info")

    inlines = [StakeholderEngagementInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    ("full_name", "nickname"),
                    ("stakeholder_type", "community"),
                    ("position", "organization"),
                    "responsibilities",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    ("contact_number", "alternate_contact"),
                    "email",
                    "address",
                    "contact_info",
                )
            },
        ),
        (
            "Influence & Engagement",
            {"fields": (("influence_level", "engagement_level"), "areas_of_influence")},
        ),
        (
            "Background",
            {
                "fields": (
                    ("age", "educational_background"),
                    ("cultural_background", "languages_spoken"),
                    ("since_year", "years_in_community", "years_of_service"),
                    "previous_roles",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "special_skills",
                    "networks",
                    "achievements",
                    "challenges_faced",
                    "support_needed",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Administrative",
            {"fields": (("is_active", "is_verified"), "verification_date", "notes")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def display_name_with_type(self, obj):
        """Display name with stakeholder type."""
        return f"{obj.display_name} ({obj.get_stakeholder_type_display()})"

    display_name_with_type.short_description = "Name & Type"
    display_name_with_type.admin_order_field = "full_name"

    def contact_info_short(self, obj):
        """Display short contact information."""
        info = []
        if obj.contact_number:
            info.append(obj.contact_number)
        if obj.email:
            info.append(obj.email.split("@")[0] + "...")
        return " | ".join(info) if info else "No contact"

    contact_info_short.short_description = "Contact"

    def colored_influence(self, obj):
        """Display influence level with color coding."""
        colors = {
            "very_high": "darkred",
            "high": "red",
            "medium": "orange",
            "low": "blue",
            "emerging": "green",
        }
        color = colors.get(obj.influence_level, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_influence_level_display(),
        )

    colored_influence.short_description = "Influence"

    def colored_engagement(self, obj):
        """Display engagement level with color coding."""
        colors = {
            "very_active": "green",
            "active": "blue",
            "moderate": "orange",
            "limited": "red",
            "inactive": "darkred",
        }
        color = colors.get(obj.engagement_level, "black")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_engagement_level_display(),
        )

    colored_engagement.short_description = "Engagement"

    actions = [
        "mark_as_verified",
        "mark_as_unverified",
        "mark_as_active",
        "mark_as_inactive",
    ]

    def mark_as_verified(self, request, queryset):
        """Mark selected stakeholders as verified."""
        from datetime import date

        updated = queryset.update(is_verified=True, verification_date=date.today())
        self.message_user(request, f"{updated} stakeholders marked as verified.")

    mark_as_verified.short_description = "Mark as Verified"

    def mark_as_unverified(self, request, queryset):
        """Mark selected stakeholders as unverified."""
        updated = queryset.update(is_verified=False, verification_date=None)
        self.message_user(request, f"{updated} stakeholders marked as unverified.")

    mark_as_unverified.short_description = "Mark as Unverified"

    def mark_as_active(self, request, queryset):
        """Mark selected stakeholders as active."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} stakeholders marked as active.")

    mark_as_active.short_description = "Mark as Active"

    def mark_as_inactive(self, request, queryset):
        """Mark selected stakeholders as inactive."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} stakeholders marked as inactive.")

    mark_as_inactive.short_description = "Mark as Inactive"


@admin.register(StakeholderEngagement)
class StakeholderEngagementAdmin(admin.ModelAdmin):
    """Admin interface for Stakeholder Engagement model."""

    list_display = (
        "title",
        "stakeholder",
        "community",
        "engagement_type",
        "date",
        "outcome",
        "follow_up_needed",
        "participants_count",
    )
    list_filter = (
        "engagement_type",
        "outcome",
        "follow_up_needed",
        "date",
        "stakeholder__stakeholder_type",
        "stakeholder__community__barangay__municipality__province__region",
    )
    search_fields = (
        "title",
        "description",
        "stakeholder__full_name",
        "stakeholder__nickname",
        "stakeholder__community__barangay__name",
        "key_points",
        "documented_by",
    )
    ordering = ("-date", "stakeholder__full_name")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "stakeholder",
                    ("engagement_type", "title"),
                    "description",
                    ("date", "duration_hours"),
                    ("location", "participants_count"),
                )
            },
        ),
        (
            "Outcomes & Feedback",
            {
                "fields": (
                    "outcome",
                    "key_points",
                    "action_items",
                    "challenges_encountered",
                    "stakeholder_feedback",
                )
            },
        ),
        (
            "Follow-up",
            {"fields": (("follow_up_needed", "follow_up_date"), "documented_by")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def community(self, obj):
        """Display community name."""
        return obj.stakeholder.community.barangay.name

    community.short_description = "Community"
    community.admin_order_field = "stakeholder__community__barangay__name"

    def colored_outcome(self, obj):
        """Display outcome with color coding."""
        colors = {
            "very_positive": "green",
            "positive": "blue",
            "neutral": "orange",
            "challenging": "red",
            "negative": "darkred",
        }
        color = colors.get(obj.outcome, "black")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_outcome_display()
        )

    colored_outcome.short_description = "Outcome"

    actions = ["mark_follow_up_needed", "mark_follow_up_completed"]

    def mark_follow_up_needed(self, request, queryset):
        """Mark selected engagements as needing follow-up."""
        updated = queryset.update(follow_up_needed=True)
        self.message_user(
            request, f"{updated} engagements marked as needing follow-up."
        )

    mark_follow_up_needed.short_description = "Mark as Needing Follow-up"

    def mark_follow_up_completed(self, request, queryset):
        """Mark selected engagements as follow-up completed."""
        updated = queryset.update(follow_up_needed=False)
        self.message_user(
            request, f"{updated} engagements marked as follow-up completed."
        )

    mark_follow_up_completed.short_description = "Mark Follow-up Completed"


@admin.register(MunicipalityCoverage)
class MunicipalityCoverageAdmin(admin.ModelAdmin):
    """Admin interface for municipality Bangsamoro coverage records."""

    list_display = (
        "municipality",
        "province",
        "region",
        "total_obc_communities",
        "estimated_obc_population",
        "auto_sync",
        "created_by",
        "updated_at",
    )
    list_filter = (
        "municipality__province__region",
        "municipality__province",
        "municipality__municipality_type",
        "auto_sync",
    )
    search_fields = (
        "municipality__name",
        "municipality__province__name",
        "municipality__province__region__name",
        "key_barangays",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "coordinates",
        "total_age_demographics",
        "average_household_size",
        "percentage_obc_in_barangay",
    )
    autocomplete_fields = ("municipality", "created_by", "updated_by")
    fieldsets = (
        (
            "Identification & Location",
            {
                "fields": (
                    ("obc_id", "source_document_reference"),
                    ("community_names",),
                    ("municipality", "purok_sitio"),
                    ("specific_location", "settlement_type"),
                    ("latitude", "longitude"),
                    ("proximity_to_barmm", "total_obc_communities"),
                    ("auto_sync", "is_active"),
                )
            },
        ),
        (
            "Demographics",
            {
                "fields": (
                    ("estimated_obc_population", "total_barangay_population"),
                    ("households", "families", "average_household_size"),
                    (
                        "children_0_9",
                        "adolescents_10_14",
                        "youth_15_30",
                        "adults_31_59",
                        "seniors_60_plus",
                    ),
                    ("primary_ethnolinguistic_group", "other_ethnolinguistic_groups"),
                    ("languages_spoken",),
                )
            },
        ),
        (
            "Vulnerable Sectors",
            {
                "fields": (
                    ("women_count", "solo_parents_count", "pwd_count"),
                    ("farmers_count", "fisherfolk_count", "unemployed_count"),
                    (
                        "indigenous_peoples_count",
                        "idps_count",
                        "migrants_transients_count",
                    ),
                    (
                        "csos_count",
                        "associations_count",
                        "number_of_peoples_organizations",
                    ),
                    (
                        "number_of_cooperatives",
                        "number_of_social_enterprises",
                        "number_of_micro_enterprises",
                    ),
                    ("other_vulnerable_sectors",),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Socio-Economic Profile",
            {
                "fields": (
                    ("primary_livelihoods", "secondary_livelihoods"),
                    ("estimated_poverty_incidence",),
                    ("land_tenure_issues",),
                    ("financial_access_level", "number_of_unbanked_obc"),
                    ("existing_support_programs",),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Access to Basic Services",
            {
                "fields": (
                    ("access_formal_education", "access_als", "access_madrasah"),
                    ("access_healthcare", "access_clean_water", "access_sanitation"),
                    (
                        "access_electricity",
                        "access_roads_transport",
                        "access_communication",
                    ),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Cultural & Historical Context",
            {
                "fields": (
                    ("brief_historical_background",),
                    ("established_year", "origin_story", "migration_history"),
                    ("cultural_practices_traditions", "religious_affiliation"),
                    ("traditional_leaders_role", "cultural_preservation_efforts"),
                    (
                        "mosques_count",
                        "madrasah_count",
                        "asatidz_count",
                        "religious_leaders_count",
                    ),
                    ("other_cultural_facilities",),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Governance & Leadership",
            {
                "fields": (
                    (
                        "formal_political_representation",
                        "informal_leadership_structures",
                    ),
                    ("community_organizations", "relationship_with_lgu"),
                    ("participation_local_governance", "access_government_info"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Challenges & Barriers",
            {
                "fields": (
                    (
                        "governance_policy_challenges",
                        "access_public_services_challenges",
                    ),
                    ("land_ownership_security_issues", "economic_disparities"),
                    ("social_instability_conflict", "cultural_miscommunication"),
                    ("gender_inequality_issues", "substance_abuse_issues"),
                    ("investment_scam_issues", "environmental_degradation"),
                    ("other_challenges", "challenges_impact"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Community Aspirations & Priorities",
            {
                "fields": (
                    ("key_aspirations",),
                    ("infrastructure_priorities", "livelihood_program_priorities"),
                    ("education_priorities", "healthcare_priorities"),
                    ("cultural_preservation_priorities", "peace_security_priorities"),
                    ("specific_project_proposals",),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Unemployment & Assessment",
            {
                "fields": (
                    ("unemployment_rate",),
                    ("needs_assessment_date", "key_findings_last_assessment"),
                    ("assessment_data_sources", "identified_gaps"),
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    ("key_community_leaders", "relevant_lgu_officials"),
                    ("community_leader", "leader_contact"),
                )
            },
        ),
        ("Administrative", {"fields": ("notes",), "classes": ("collapse",)}),
    )


# ============================================================================
# GEOGRAPHIC DATA ADMIN (Moved from mana app for better organization)
# ============================================================================


@admin.register(GeographicDataLayer)
class GeographicDataLayerAdmin(admin.ModelAdmin):
    """Admin interface for Geographic Data Layers."""

    list_display = [
        "name",
        "layer_type",
        "data_source",
        "administrative_level_display",
        "community_link",
        "visibility_status",
        "feature_count",
        "created_by",
        "created_at",
    ]
    list_filter = [
        "layer_type",
        "data_source",
        "is_public",
        "is_visible",
        "created_at",
        "data_collection_date",
    ]
    search_fields = [
        "name",
        "description",
        "community__barangay__name",
        "region__name",
        "province__name",
        "municipality__name",
        "barangay__name",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    autocomplete_fields = [
        "community",
        "assessment",
        "region",
        "province",
        "municipality",
        "barangay",
        "created_by",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "administrative_level",
        "full_administrative_path",
    ]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "description", "layer_type", "data_source")},
        ),
        (
            "Administrative Location",
            {
                "fields": (
                    ("region", "province"),
                    ("municipality", "barangay"),
                    ("administrative_level", "full_administrative_path"),
                ),
                "description": "Link this layer to specific administrative levels. Fill in the most specific level that applies.",
            },
        ),
        (
            "Related Objects",
            {"fields": ("community", "assessment"), "classes": ("collapse",)},
        ),
        (
            "Geographic Data",
            {
                "fields": (
                    "geojson_data",
                    ("bounding_box", "center_point"),
                    ("coordinate_system", "accuracy_meters"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    ("is_visible", "is_public"),
                    ("opacity", "zoom_level_min", "zoom_level_max"),
                    "style_properties",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    ("data_collection_date", "feature_count", "file_size_bytes"),
                    ("attribution", "license_info"),
                    "access_groups",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "System Information",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def administrative_level_display(self, obj):
        """Display the administrative level with path."""
        level = obj.administrative_level
        if level == "none":
            return format_html(
                '<span style="color: orange;">No administrative assignment</span>'
            )

        colors = {
            "region": "#007bff",
            "province": "#28a745",
            "municipality": "#ffc107",
            "barangay": "#dc3545",
            "community": "#6f42c1",
        }
        color = colors.get(level, "#6c757d")

        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            level.title(),
        )

    administrative_level_display.short_description = "Admin Level"

    def community_link(self, obj):
        """Link to community if available."""
        if obj.community:
            url = reverse(
                "admin:communities_obccommunity_change", args=[obj.community.pk]
            )
            return format_html('<a href="{}">{}</a>', url, obj.community.display_name)
        return "-"

    community_link.short_description = "Community"

    def visibility_status(self, obj):
        """Display visibility and public status."""
        if obj.is_visible and obj.is_public:
            return format_html('<span style="color: green;">✓ Public & Visible</span>')
        elif obj.is_visible:
            return format_html('<span style="color: blue;">✓ Visible</span>')
        elif obj.is_public:
            return format_html('<span style="color: orange;">Public Only</span>')
        else:
            return format_html('<span style="color: red;">✗ Hidden</span>')

    visibility_status.short_description = "Visibility"


@admin.register(MapVisualization)
class MapVisualizationAdmin(admin.ModelAdmin):
    """Admin interface for Map Visualizations."""

    list_display = [
        "title",
        "visualization_type",
        "community_link",
        "assessment_link",
        "visibility_status",
        "layers_count",
        "basemap_provider",
        "created_at",
    ]
    list_filter = [
        "visualization_type",
        "basemap_provider",
        "is_public",
        "is_interactive",
        "created_at",
    ]
    search_fields = [
        "title",
        "description",
        "community__barangay__name",
        "assessment__title",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    autocomplete_fields = ["community", "assessment", "created_by"]
    filter_horizontal = ["layers"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "description", "visualization_type")},
        ),
        (
            "Related Objects",
            {"fields": ("community", "assessment", "layers")},
        ),
        (
            "Map Configuration",
            {
                "fields": (
                    ("basemap_provider", "initial_zoom"),
                    "initial_center",
                    "bounding_box",
                ),
            },
        ),
        (
            "Visualization Settings",
            {
                "fields": (
                    "color_scheme",
                    "legend_configuration",
                    "popup_template",
                    "filters_configuration",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Interactivity",
            {
                "fields": (
                    ("is_interactive", "is_public"),
                    ("enable_clustering", "enable_search", "enable_drawing"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "System Information",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def community_link(self, obj):
        """Link to community if available."""
        if obj.community:
            url = reverse(
                "admin:communities_obccommunity_change", args=[obj.community.pk]
            )
            return format_html('<a href="{}">{}</a>', url, obj.community.display_name)
        return "-"

    community_link.short_description = "Community"

    def assessment_link(self, obj):
        """Link to assessment if available."""
        if obj.assessment:
            url = reverse("admin:mana_assessment_change", args=[obj.assessment.pk])
            return format_html('<a href="{}">{}</a>', url, obj.assessment.title)
        return "-"

    assessment_link.short_description = "Assessment"

    def visibility_status(self, obj):
        """Display visibility and interactivity status."""
        status_parts = []
        if obj.is_public:
            status_parts.append('<span style="color: green;">Public</span>')
        else:
            status_parts.append('<span style="color: orange;">Private</span>')

        if obj.is_interactive:
            status_parts.append('<span style="color: blue;">Interactive</span>')
        else:
            status_parts.append('<span style="color: gray;">Static</span>')

        return format_html(" | ".join(status_parts))

    visibility_status.short_description = "Status"

    def layers_count(self, obj):
        """Count of associated layers."""
        count = obj.layers.count()
        if count > 0:
            return format_html('<span style="color: green;">{} layers</span>', count)
        return format_html('<span style="color: orange;">No layers</span>')

    layers_count.short_description = "Layers"


@admin.register(SpatialDataPoint)
class SpatialDataPointAdmin(admin.ModelAdmin):
    """Admin interface for Spatial Data Points."""

    list_display = [
        "name",
        "data_layer_link",
        "point_type",
        "coordinates_display",
        "status",
        "is_verified",
        "created_at",
    ]
    list_filter = [
        "point_type",
        "status",
        "is_verified",
        "collection_method",
        "data_layer__layer_type",
        "data_layer__data_source",
        "created_at",
    ]
    search_fields = [
        "name",
        "description",
        "data_layer__name",
        "community__barangay__name",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    autocomplete_fields = [
        "data_layer",
        "community",
        "assessment",
        "collected_by",
        "verified_by",
    ]
    readonly_fields = ["created_at", "updated_at", "coordinates_display"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "data_layer", "point_type", "description", "status")},
        ),
        (
            "Location",
            {"fields": ("community", "assessment")},
        ),
        (
            "Geographic Data",
            {
                "fields": (
                    ("latitude", "longitude"),
                    "coordinates_display",
                    ("elevation", "accuracy_meters"),
                ),
            },
        ),
        (
            "Collection Data",
            {
                "fields": (
                    ("collected_date", "collected_by"),
                    "collection_method",
                    ("photo_url", "media_files"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    ("is_verified", "verified_by"),
                    "verification_date",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Attributes",
            {"fields": ("attributes",), "classes": ("collapse",)},
        ),
        (
            "System Information",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def data_layer_link(self, obj):
        """Link to geographic data layer."""
        if obj.data_layer:
            url = reverse(
                "admin:communities_geographicdatalayer_change", args=[obj.data_layer.pk]
            )
            return format_html('<a href="{}">{}</a>', url, obj.data_layer.name)
        return "-"

    data_layer_link.short_description = "Data Layer"

    def coordinates_display(self, obj):
        """Display coordinates in a readable format."""
        if obj.latitude is not None and obj.longitude is not None:
            return f"[{obj.longitude:.6f}, {obj.latitude:.6f}]"
        return "No coordinates"

    coordinates_display.short_description = "Coordinates"


@admin.register(ProvinceCoverage)
class ProvinceCoverageAdmin(admin.ModelAdmin):
    """Admin interface for provincial Bangsamoro coverage records."""

    list_display = (
        "province",
        "region",
        "total_municipalities",
        "total_obc_communities",
        "estimated_obc_population",
        "auto_sync",
        "created_by",
        "updated_at",
    )
    list_filter = (
        "province__region",
        "auto_sync",
    )
    search_fields = (
        "province__name",
        "province__region__name",
        "key_municipalities",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("province", "created_by", "updated_by")

    fieldsets = (
        (
            "Identification & Location",
            {
                "fields": (
                    ("province", "obc_id", "source_document_reference"),
                    ("community_names",),
                    ("latitude", "longitude"),
                    ("proximity_to_barmm", "auto_sync", "is_active"),
                )
            },
        ),
        (
            "Aggregated Totals",
            {
                "fields": (
                    ("total_municipalities", "total_obc_communities"),
                    ("estimated_obc_population", "total_barangay_population"),
                    ("households", "families"),
                    ("women_count", "solo_parents_count", "pwd_count"),
                    ("farmers_count", "fisherfolk_count", "unemployed_count"),
                    (
                        "indigenous_peoples_count",
                        "idps_count",
                        "migrants_transients_count",
                    ),
                    (
                        "csos_count",
                        "associations_count",
                        "number_of_peoples_organizations",
                    ),
                    (
                        "number_of_cooperatives",
                        "number_of_social_enterprises",
                        "number_of_micro_enterprises",
                    ),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Key Insights",
            {
                "fields": (
                    ("key_municipalities",),
                    ("existing_support_programs",),
                    ("notes",),
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    ("created_by", "updated_by"),
                    ("created_at", "updated_at"),
                )
            },
        ),
    )


@admin.register(CommunityEvent)
class CommunityEventAdmin(admin.ModelAdmin):
    """Admin interface for Community Events."""

    list_display = (
        "title",
        "community",
        "event_type",
        "start_date",
        "end_date",
        "is_public",
        "is_recurring",
        "created_by",
    )
    list_filter = ("event_type", "is_public", "is_recurring", "start_date")
    search_fields = ("title", "description", "community__name", "location", "organizer")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_date"

    fieldsets = (
        ("Community", {"fields": ("community",)}),
        ("Event Details", {"fields": ("title", "description", "event_type")}),
        (
            "Schedule",
            {"fields": ("start_date", "end_date", "all_day", "start_time", "end_time")},
        ),
        ("Location & Organizer", {"fields": ("location", "organizer")}),
        ("Visibility", {"fields": ("is_public",)}),
        (
            "Recurrence",
            {
                "fields": (
                    "is_recurring",
                    "recurrence_pattern",
                    "recurrence_parent",
                    "is_recurrence_exception",
                ),
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
