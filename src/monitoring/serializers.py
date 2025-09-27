"""API serializers for Monitoring & Evaluation resources."""

from rest_framework import serializers

from .models import (
    MonitoringEntry,
    MonitoringEntryFunding,
    MonitoringEntryWorkflowStage,
    MonitoringUpdate,
)


class MonitoringEntryFundingSerializer(serializers.ModelSerializer):
    """Serialize detailed funding flow entries."""

    tranche_type_display = serializers.CharField(
        source="get_tranche_type_display", read_only=True
    )
    funding_source_display = serializers.CharField(
        source="get_funding_source_display", read_only=True
    )

    class Meta:
        model = MonitoringEntryFunding
        fields = [
            "id",
            "tranche_type",
            "tranche_type_display",
            "amount",
            "funding_source",
            "funding_source_display",
            "funding_source_other",
            "scheduled_date",
            "remarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "tranche_type_display",
            "funding_source_display",
        ]


class MonitoringEntryWorkflowStageSerializer(serializers.ModelSerializer):
    """Serialize workflow stages and status updates."""

    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    owner_team_name = serializers.CharField(
        source="owner_team.name", read_only=True
    )
    owner_organization_name = serializers.CharField(
        source="owner_organization.name", read_only=True
    )

    class Meta:
        model = MonitoringEntryWorkflowStage
        fields = [
            "id",
            "stage",
            "stage_display",
            "status",
            "status_display",
            "owner_team",
            "owner_team_name",
            "owner_organization",
            "owner_organization_name",
            "due_date",
            "completed_at",
            "notes",
            "updated_at",
        ]
        read_only_fields = [
            "stage_display",
            "status_display",
            "owner_team_name",
            "owner_organization_name",
            "updated_at",
        ]


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
    funding_flows = MonitoringEntryFundingSerializer(many=True, read_only=True)
    workflow_stages = MonitoringEntryWorkflowStageSerializer(many=True, read_only=True)
    sector_display = serializers.CharField(source="get_sector_display", read_only=True)
    appropriation_class_display = serializers.CharField(
        source="get_appropriation_class_display",
        read_only=True,
    )
    funding_source_display = serializers.CharField(
        source="get_funding_source_display", read_only=True
    )

    class Meta:
        model = MonitoringEntry
        fields = [
            "id",
            "title",
            "category",
            "category_display",
            "summary",
            "plan_year",
            "fiscal_year",
            "sector",
            "sector_display",
            "appropriation_class",
            "appropriation_class_display",
            "funding_source",
            "funding_source_display",
            "funding_source_other",
            "program_code",
            "plan_reference",
            "goal_alignment",
            "moral_governance_pillar",
            "compliance_gad",
            "compliance_ccet",
            "benefits_indigenous_peoples",
            "supports_peace_agenda",
            "supports_sdg",
            "budget_ceiling",
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
            "budget_obc_allocation",
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
            "funding_flows",
            "workflow_stages",
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
            "sector_display",
            "appropriation_class_display",
            "funding_source_display",
        ]
