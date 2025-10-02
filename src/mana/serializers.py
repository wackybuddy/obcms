from rest_framework import serializers

from communities.models import GeographicDataLayer, MapVisualization, SpatialDataPoint
from communities.serializers import OBCCommunityListSerializer

from .models import (
    Assessment,
    AssessmentCategory,
    AssessmentTeamMember,
    BaselineDataCollection,
    BaselineIndicator,
    BaselineStudy,
    BaselineStudyTeamMember,
    MappingActivity,
    Need,
    NeedsCategory,
    NeedsPrioritization,
    NeedsPrioritizationItem,
    Survey,
    SurveyQuestion,
    SurveyResponse,
)


class AssessmentCategorySerializer(serializers.ModelSerializer):
    """Serializer for AssessmentCategory model."""

    class Meta:
        model = AssessmentCategory
        fields = "__all__"


class AssessmentTeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for AssessmentTeamMember model."""

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = AssessmentTeamMember
        fields = "__all__"


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment model."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    community_name = serializers.CharField(source="community.name", read_only=True)
    lead_assessor_name = serializers.CharField(
        source="lead_assessor.get_full_name", read_only=True
    )
    team_members = AssessmentTeamMemberSerializer(many=True, read_only=True)
    duration_days = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Assessment
        fields = "__all__"


class AssessmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Assessment list view."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    community_name = serializers.CharField(source="community.name", read_only=True)
    lead_assessor_name = serializers.CharField(
        source="lead_assessor.get_full_name", read_only=True
    )
    duration_days = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "title",
            "category_name",
            "community_name",
            "status",
            "priority",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "lead_assessor_name",
            "duration_days",
            "progress_percentage",
            "created_at",
        ]


class SurveyQuestionSerializer(serializers.ModelSerializer):
    """Serializer for SurveyQuestion model."""

    class Meta:
        model = SurveyQuestion
        fields = "__all__"


class SurveyResponseSerializer(serializers.ModelSerializer):
    """Serializer for SurveyResponse model."""

    question_text = serializers.CharField(
        source="question.question_text", read_only=True
    )
    respondent_name = serializers.CharField(
        source="respondent.get_full_name", read_only=True
    )

    class Meta:
        model = SurveyResponse
        fields = "__all__"


class SurveySerializer(serializers.ModelSerializer):
    """Serializer for Survey model."""

    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    questions = SurveyQuestionSerializer(many=True, read_only=True)
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = "__all__"

    def get_response_count(self, obj):
        return obj.responses.count()


class NeedsCategorySerializer(serializers.ModelSerializer):
    """Serializer for NeedsCategory model."""

    class Meta:
        model = NeedsCategory
        fields = "__all__"


class NeedSerializer(serializers.ModelSerializer):
    """Serializer for Need model."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    community_name = serializers.CharField(
        source="assessment.community.name", read_only=True
    )

    class Meta:
        model = Need
        fields = "__all__"


class NeedListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Need list view."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    community_name = serializers.CharField(
        source="assessment.community.name", read_only=True
    )

    class Meta:
        model = Need
        fields = [
            "id",
            "title",
            "category_name",
            "priority_level",
            "urgency_level",
            "assessment_title",
            "community_name",
            "estimated_beneficiaries",
            "resource_requirements",
            "implementation_timeframe",
            "status",
        ]


class NeedsPrioritizationItemSerializer(serializers.ModelSerializer):
    """Serializer for NeedsPrioritizationItem model."""

    need_title = serializers.CharField(source="need.title", read_only=True)

    class Meta:
        model = NeedsPrioritizationItem
        fields = "__all__"


class NeedsPrioritizationSerializer(serializers.ModelSerializer):
    """Serializer for NeedsPrioritization model."""

    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    facilitator_name = serializers.CharField(
        source="facilitator.get_full_name", read_only=True
    )
    prioritized_needs = NeedsPrioritizationItemSerializer(many=True, read_only=True)

    class Meta:
        model = NeedsPrioritization
        fields = "__all__"


class GeographicDataLayerSerializer(serializers.ModelSerializer):
    """Serializer for GeographicDataLayer model."""

    class Meta:
        model = GeographicDataLayer
        fields = "__all__"


class SpatialDataPointSerializer(serializers.ModelSerializer):
    """Serializer for SpatialDataPoint model."""

    layer_name = serializers.CharField(source="layer.name", read_only=True)

    class Meta:
        model = SpatialDataPoint
        fields = "__all__"


class MapVisualizationSerializer(serializers.ModelSerializer):
    """Serializer for MapVisualization model."""

    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    data_layers = GeographicDataLayerSerializer(many=True, read_only=True)

    class Meta:
        model = MapVisualization
        fields = "__all__"


class MappingActivitySerializer(serializers.ModelSerializer):
    """Serializer for MappingActivity model."""

    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    facilitator_name = serializers.CharField(
        source="facilitator.get_full_name", read_only=True
    )

    class Meta:
        model = MappingActivity
        fields = "__all__"


class BaselineIndicatorSerializer(serializers.ModelSerializer):
    """Serializer for BaselineIndicator model."""

    class Meta:
        model = BaselineIndicator
        fields = "__all__"


class BaselineDataCollectionSerializer(serializers.ModelSerializer):
    """Serializer for BaselineDataCollection model."""

    indicator_name = serializers.CharField(source="indicator.name", read_only=True)
    collected_by_name = serializers.CharField(
        source="collected_by.get_full_name", read_only=True
    )

    class Meta:
        model = BaselineDataCollection
        fields = "__all__"


class BaselineStudyTeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for BaselineStudyTeamMember model."""

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = BaselineStudyTeamMember
        fields = "__all__"


class BaselineStudySerializer(serializers.ModelSerializer):
    """Serializer for BaselineStudy model."""

    community_name = serializers.CharField(source="community.name", read_only=True)
    lead_researcher_name = serializers.CharField(
        source="lead_researcher.get_full_name", read_only=True
    )
    team_members = BaselineStudyTeamMemberSerializer(many=True, read_only=True)
    indicators = BaselineIndicatorSerializer(many=True, read_only=True)
    data_collections = BaselineDataCollectionSerializer(many=True, read_only=True)

    class Meta:
        model = BaselineStudy
        fields = "__all__"


class BaselineStudyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for BaselineStudy list view."""

    community_name = serializers.CharField(source="community.name", read_only=True)
    lead_researcher_name = serializers.CharField(
        source="lead_researcher.get_full_name", read_only=True
    )
    indicator_count = serializers.SerializerMethodField()

    class Meta:
        model = BaselineStudy
        fields = [
            "id",
            "title",
            "community_name",
            "study_type",
            "status",
            "priority_level",
            "planned_start_date",
            "planned_end_date",
            "lead_researcher_name",
            "indicator_count",
            "created_at",
        ]

    def get_indicator_count(self, obj):
        return obj.indicators.count()
