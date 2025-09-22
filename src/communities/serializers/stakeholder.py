"""Stakeholder-related serializers."""

from rest_framework import serializers

from ..models import Stakeholder, StakeholderEngagement


class StakeholderSerializer(serializers.ModelSerializer):
    """Detailed serializer for stakeholder profiles."""

    community_name = serializers.CharField(
        source="community.display_name", read_only=True
    )
    stakeholder_type_display = serializers.CharField(
        source="get_stakeholder_type_display", read_only=True
    )
    influence_level_display = serializers.CharField(
        source="get_influence_level_display", read_only=True
    )
    engagement_level_display = serializers.CharField(
        source="get_engagement_level_display", read_only=True
    )
    years_of_service = serializers.IntegerField(read_only=True)
    recent_engagements = serializers.SerializerMethodField()

    class Meta:
        model = Stakeholder
        fields = [
            "id",
            "display_name",
            "full_name",
            "nickname",
            "stakeholder_type",
            "stakeholder_type_display",
            "community",
            "community_name",
            "position",
            "organization",
            "responsibilities",
            "influence_level",
            "influence_level_display",
            "engagement_level",
            "engagement_level_display",
            "areas_of_influence",
            "contact_number",
            "alternate_contact",
            "email",
            "address",
            "contact_info",
            "years_of_service",
            "age",
            "educational_background",
            "cultural_background",
            "languages_spoken",
            "since_year",
            "years_in_community",
            "previous_roles",
            "special_skills",
            "networks",
            "achievements",
            "challenges_faced",
            "support_needed",
            "is_active",
            "is_verified",
            "verification_date",
            "notes",
            "recent_engagements",
            "created_at",
            "updated_at",
        ]

    def get_recent_engagements(self, obj):
        engagements = obj.engagements.all().order_by("-date")[:5]
        return [
            {
                "id": engagement.id,
                "title": engagement.title,
                "date": engagement.date,
                "outcome": engagement.get_outcome_display(),
            }
            for engagement in engagements
        ]


class StakeholderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing stakeholders."""

    display_name = serializers.ReadOnlyField()
    community_name = serializers.CharField(
        source="community.display_name", read_only=True
    )
    stakeholder_type_display = serializers.CharField(
        source="get_stakeholder_type_display", read_only=True
    )
    influence_level_display = serializers.CharField(
        source="get_influence_level_display", read_only=True
    )
    engagement_level_display = serializers.CharField(
        source="get_engagement_level_display", read_only=True
    )

    class Meta:
        model = Stakeholder
        fields = [
            "id",
            "display_name",
            "full_name",
            "nickname",
            "stakeholder_type",
            "stakeholder_type_display",
            "community_name",
            "position",
            "influence_level",
            "influence_level_display",
            "engagement_level",
            "engagement_level_display",
            "contact_number",
            "email",
            "is_active",
            "is_verified",
            "since_year",
        ]


class StakeholderEngagementSerializer(serializers.ModelSerializer):
    """Serializer for stakeholder engagements."""

    stakeholder_name = serializers.CharField(
        source="stakeholder.display_name", read_only=True
    )
    community_name = serializers.CharField(
        source="stakeholder.community.display_name", read_only=True
    )
    engagement_type_display = serializers.CharField(
        source="get_engagement_type_display", read_only=True
    )
    outcome_display = serializers.CharField(
        source="get_outcome_display", read_only=True
    )

    class Meta:
        model = StakeholderEngagement
        fields = [
            "id",
            "stakeholder",
            "stakeholder_name",
            "community_name",
            "engagement_type",
            "engagement_type_display",
            "title",
            "description",
            "date",
            "duration_hours",
            "location",
            "participants_count",
            "outcome",
            "outcome_display",
            "key_points",
            "action_items",
            "challenges_encountered",
            "stakeholder_feedback",
            "follow_up_needed",
            "follow_up_date",
            "documented_by",
            "created_at",
            "updated_at",
        ]


class StakeholderStatsSerializer(serializers.Serializer):
    """Serializer for stakeholder statistics."""

    total_stakeholders = serializers.IntegerField()
    active_stakeholders = serializers.IntegerField()
    verified_stakeholders = serializers.IntegerField()
    by_type = serializers.DictField()
    by_influence_level = serializers.DictField()
    by_engagement_level = serializers.DictField()
    by_community = serializers.DictField()
    recent_engagements = serializers.IntegerField()


__all__ = [
    "StakeholderSerializer",
    "StakeholderListSerializer",
    "StakeholderEngagementSerializer",
    "StakeholderStatsSerializer",
]
