from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    AssessmentCategoryViewSet,
    AssessmentTeamMemberViewSet,
    AssessmentViewSet,
    BaselineDataCollectionViewSet,
    BaselineIndicatorViewSet,
    BaselineStudyViewSet,
    GeographicDataLayerViewSet,
    MappingActivityViewSet,
    MapVisualizationViewSet,
    NeedsCategoryViewSet,
    NeedsPrioritizationViewSet,
    NeedViewSet,
    SpatialDataPointViewSet,
    SurveyQuestionViewSet,
    SurveyResponseViewSet,
    SurveyViewSet,
)

app_name = "mana_api"

router = DefaultRouter()
router.register(r"assessment-categories", AssessmentCategoryViewSet)
router.register(r"assessments", AssessmentViewSet)
router.register(r"assessment-team-members", AssessmentTeamMemberViewSet)
router.register(r"needs-categories", NeedsCategoryViewSet)
router.register(r"needs", NeedViewSet)
router.register(r"needs-prioritizations", NeedsPrioritizationViewSet)
router.register(r"surveys", SurveyViewSet)
router.register(r"survey-questions", SurveyQuestionViewSet)
router.register(r"survey-responses", SurveyResponseViewSet)
router.register(r"mapping-activities", MappingActivityViewSet)
router.register(r"geographic-data-layers", GeographicDataLayerViewSet)
router.register(r"map-visualizations", MapVisualizationViewSet)
router.register(r"spatial-data-points", SpatialDataPointViewSet)
router.register(r"baseline-studies", BaselineStudyViewSet)
router.register(r"baseline-indicators", BaselineIndicatorViewSet)
router.register(r"baseline-data-collections", BaselineDataCollectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
