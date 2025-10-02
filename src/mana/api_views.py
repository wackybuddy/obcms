from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from communities.models import GeographicDataLayer, MapVisualization, SpatialDataPoint
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
from .serializers import (
    AssessmentCategorySerializer,
    AssessmentListSerializer,
    AssessmentSerializer,
    AssessmentTeamMemberSerializer,
    BaselineDataCollectionSerializer,
    BaselineIndicatorSerializer,
    BaselineStudyListSerializer,
    BaselineStudySerializer,
    BaselineStudyTeamMemberSerializer,
    GeographicDataLayerSerializer,
    MappingActivitySerializer,
    MapVisualizationSerializer,
    NeedListSerializer,
    NeedsCategorySerializer,
    NeedSerializer,
    NeedsPrioritizationItemSerializer,
    NeedsPrioritizationSerializer,
    SpatialDataPointSerializer,
    SurveyQuestionSerializer,
    SurveyResponseSerializer,
    SurveySerializer,
)


class AssessmentCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for AssessmentCategory model."""

    queryset = AssessmentCategory.objects.all()
    serializer_class = AssessmentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category_type", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class AssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Assessment model."""

    queryset = Assessment.objects.all().select_related(
        "category", "community", "lead_assessor"
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "priority", "category", "community"]
    search_fields = ["title", "description", "community__name"]
    ordering_fields = ["title", "planned_start_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return AssessmentListSerializer
        return AssessmentSerializer

    @action(detail=True, methods=["get"])
    def team_members(self, request, pk=None):
        """Get team members for this assessment."""
        assessment = self.get_object()
        members = assessment.team_members.all()
        serializer = AssessmentTeamMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def needs(self, request, pk=None):
        """Get needs identified in this assessment."""
        assessment = self.get_object()
        needs = assessment.identified_needs.all()
        serializer = NeedListSerializer(needs, many=True)
        return Response(serializer.data)


class NeedViewSet(viewsets.ModelViewSet):
    """ViewSet for Need model."""

    queryset = Need.objects.all().select_related("category", "assessment__community")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "category",
        "priority_level",
        "urgency_level",
        "status",
        "assessment",
    ]
    search_fields = ["title", "description", "assessment__community__name"]
    ordering_fields = ["title", "priority_level", "urgency_level", "created_at"]
    ordering = ["-priority_level", "-urgency_level"]

    def get_serializer_class(self):
        if self.action == "list":
            return NeedListSerializer
        return NeedSerializer


class BaselineStudyViewSet(viewsets.ModelViewSet):
    """ViewSet for BaselineStudy model."""

    queryset = BaselineStudy.objects.all().select_related(
        "community", "lead_researcher"
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "study_type", "priority_level", "community"]
    search_fields = ["title", "description", "community__name"]
    ordering_fields = ["title", "planned_start_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return BaselineStudyListSerializer
        return BaselineStudySerializer

    @action(detail=True, methods=["get"])
    def indicators(self, request, pk=None):
        """Get indicators for this baseline study."""
        study = self.get_object()
        indicators = study.indicators.all()
        serializer = BaselineIndicatorSerializer(indicators, many=True)
        return Response(serializer.data)


class SurveyViewSet(viewsets.ModelViewSet):
    """ViewSet for Survey model."""

    queryset = Survey.objects.all().select_related("assessment")
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["survey_type", "status", "assessment"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_at"]
    ordering = ["-created_at"]


class MappingActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for MappingActivity model."""

    queryset = MappingActivity.objects.all().select_related("assessment", "facilitator")
    serializer_class = MappingActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["activity_type", "status", "assessment"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "activity_date", "created_at"]
    ordering = ["-activity_date"]


class NeedsCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for NeedsCategory model."""

    queryset = NeedsCategory.objects.all()
    serializer_class = NeedsCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class NeedsPrioritizationViewSet(viewsets.ModelViewSet):
    """ViewSet for NeedsPrioritization model."""

    queryset = NeedsPrioritization.objects.all().select_related(
        "assessment", "facilitator"
    )
    serializer_class = NeedsPrioritizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["methodology", "assessment"]
    search_fields = ["title", "assessment__title"]
    ordering_fields = ["title", "session_date", "created_at"]
    ordering = ["-session_date"]


class GeographicDataLayerViewSet(viewsets.ModelViewSet):
    """ViewSet for GeographicDataLayer model."""

    queryset = GeographicDataLayer.objects.all()
    serializer_class = GeographicDataLayerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["layer_type", "is_public"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class MapVisualizationViewSet(viewsets.ModelViewSet):
    """ViewSet for MapVisualization model."""

    queryset = MapVisualization.objects.all().select_related("assessment", "created_by")
    serializer_class = MapVisualizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["visualization_type", "is_public", "assessment"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_at"]
    ordering = ["-created_at"]


# Additional ViewSets for related models
class AssessmentTeamMemberViewSet(viewsets.ModelViewSet):
    queryset = AssessmentTeamMember.objects.all().select_related("assessment", "user")
    serializer_class = AssessmentTeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["assessment", "role"]


class SurveyQuestionViewSet(viewsets.ModelViewSet):
    queryset = SurveyQuestion.objects.all().select_related("survey")
    serializer_class = SurveyQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["survey", "question_type", "is_required"]


class SurveyResponseViewSet(viewsets.ModelViewSet):
    queryset = SurveyResponse.objects.all().select_related("question", "respondent")
    serializer_class = SurveyResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["question", "respondent"]


class SpatialDataPointViewSet(viewsets.ModelViewSet):
    queryset = SpatialDataPoint.objects.all().select_related("layer")
    serializer_class = SpatialDataPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["layer", "point_type"]


class BaselineIndicatorViewSet(viewsets.ModelViewSet):
    queryset = BaselineIndicator.objects.all().select_related("study")
    serializer_class = BaselineIndicatorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["study", "indicator_type", "data_type"]


class BaselineDataCollectionViewSet(viewsets.ModelViewSet):
    queryset = BaselineDataCollection.objects.all().select_related(
        "indicator", "collected_by"
    )
    serializer_class = BaselineDataCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["indicator", "collection_method", "collected_by"]
