"""API serializers for Monitoring & Evaluation resources."""

from rest_framework import serializers

from .models import MonitoringEntry, MonitoringUpdate


class MonitoringUpdateSerializer(serializers.ModelSerializer):
    """Serialize monitoring updates with author metadata."""

    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    update_type_display = serializers.CharField(
        source="get_update_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    request_status_display = serializers.CharField(
        source="get_request_status_display", read_only=True
    )

    class Meta:
        model = MonitoringUpdate
        fields = [
            "id",
            "entry",
            "update_type",
            "update_type_display",
            "status",
            "status_display",
            "request_status",
            "request_status_display",
            "progress",
            "notes",
            "next_steps",
            "follow_up_date",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = [
            "created_by",
            "created_by_name",
            "created_at",
            "status_display",
            "request_status_display",
            "update_type_display",
        ]


class MonitoringEntrySerializer(serializers.ModelSerializer):
    """Serialize monitoring entries with related resource links."""

    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    request_status_display = serializers.CharField(
        source="get_request_status_display", read_only=True
    )
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    lead_organization_name = serializers.CharField(
        source="lead_organization.name", read_only=True
    )
    submitted_by_community_name = serializers.CharField(
        source="submitted_by_community.name", read_only=True
    )
    submitted_to_organization_name = serializers.CharField(
        source="submitted_to_organization.name", read_only=True
    )
    supporting_organizations = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    communities = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    updates = MonitoringUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = MonitoringEntry
        fields = [
            "id",
            "title",
            "category",
            "category_display",
            "summary",
            "status",
            "status_display",
            "request_status",
            "request_status_display",
            "priority",
            "priority_display",
            "progress",
            "lead_organization",
            "lead_organization_name",
            "supporting_organizations",
            "oobc_unit",
            "submitted_by_community",
            "submitted_by_community_name",
            "communities",
            "submitted_to_organization",
            "submitted_to_organization_name",
            "related_assessment",
            "related_event",
            "related_policy",
            "start_date",
            "target_end_date",
            "actual_end_date",
            "next_milestone_date",
            "budget_allocation",
            "budget_currency",
            "outcome_indicators",
            "accomplishments",
            "challenges",
            "support_required",
            "follow_up_actions",
            "last_status_update",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "updates",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "category_display",
            "status_display",
            "request_status_display",
            "priority_display",
            "lead_organization_name",
            "submitted_by_community_name",
            "submitted_to_organization_name",
        ]
