from django.contrib import admin
from django.utils.html import format_html

from .models import (CommunityInfrastructure, CommunityLivelihood,
                     MunicipalityCoverage, OBCCommunity, Stakeholder,
                     StakeholderEngagement)


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
        "development_status",
        "is_active",
    )
    list_filter = (
        "development_status",
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
                    ("children_0_9", "adolescents_10_14", "youth_15_30", "adults_31_59", "seniors_60_plus"),
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
                    ("indigenous_peoples_count", "idps_count", "migrants_transients_count"),
                    ("csos_count", "associations_count", "number_of_cooperatives"),
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
                    ("number_of_employed_obc", "number_of_unbanked_obc"),
                    (
                        "number_of_social_enterprises",
                        "number_of_micro_enterprises",
                    ),
                    ("financial_literacy_access",),
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
                    ("mosques_count", "madrasah_count", "asatidz_count", "religious_leaders_count"),
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
            "Development Status & Assessment",
            {
                "fields": (
                    ("development_status",),
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

    def colored_status(self, obj):
        """Display development status with color coding."""
        colors = {
            "developing": "orange",
            "established": "green",
            "vulnerable": "red",
            "thriving": "blue",
            "at_risk": "darkred",
        }
        color = colors.get(obj.development_status, "black")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_development_status_display(),
        )

    colored_status.short_description = "Status"

    actions = ["mark_as_established", "mark_as_vulnerable", "mark_as_thriving"]

    def mark_as_established(self, request, queryset):
        """Mark selected communities as established."""
        updated = queryset.update(development_status="established")
        self.message_user(request, f"{updated} communities marked as established.")

    mark_as_established.short_description = "Mark as Established"

    def mark_as_vulnerable(self, request, queryset):
        """Mark selected communities as vulnerable."""
        updated = queryset.update(development_status="vulnerable")
        self.message_user(request, f"{updated} communities marked as vulnerable.")

    mark_as_vulnerable.short_description = "Mark as Vulnerable"

    def mark_as_thriving(self, request, queryset):
        """Mark selected communities as thriving."""
        updated = queryset.update(development_status="thriving")
        self.message_user(request, f"{updated} communities marked as thriving.")

    mark_as_thriving.short_description = "Mark as Thriving"


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
        "community__development_status",
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
        "community__development_status",
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
        "community__development_status",
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
                    ("children_0_9", "adolescents_10_14", "youth_15_30", "adults_31_59", "seniors_60_plus"),
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
                    ("indigenous_peoples_count", "idps_count", "migrants_transients_count"),
                    ("csos_count", "associations_count", "number_of_cooperatives"),
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
                    ("number_of_employed_obc", "number_of_unbanked_obc"),
                    (
                        "number_of_social_enterprises",
                        "number_of_micro_enterprises",
                    ),
                    ("financial_literacy_access",),
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
                    ("mosques_count", "madrasah_count", "asatidz_count", "religious_leaders_count"),
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
            "Development Status & Assessment",
            {
                "fields": (
                    ("development_status",),
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
