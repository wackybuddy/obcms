from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AssessmentCategoryViewSet, AssessmentViewSet, NeedViewSet,
    BaselineStudyViewSet, SurveyViewSet, MappingActivityViewSet,
    NeedsCategoryViewSet, NeedsPrioritizationViewSet,
    GeographicDataLayerViewSet, MapVisualizationViewSet,
    AssessmentTeamMemberViewSet, SurveyQuestionViewSet,
    SurveyResponseViewSet, SpatialDataPointViewSet,
    BaselineIndicatorViewSet, BaselineDataCollectionViewSet
)

app_name = 'mana_api'

router = DefaultRouter()
router.register(r'assessment-categories', AssessmentCategoryViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'assessment-team-members', AssessmentTeamMemberViewSet)
router.register(r'needs-categories', NeedsCategoryViewSet)
router.register(r'needs', NeedViewSet)
router.register(r'needs-prioritizations', NeedsPrioritizationViewSet)
router.register(r'surveys', SurveyViewSet)
router.register(r'survey-questions', SurveyQuestionViewSet)
router.register(r'survey-responses', SurveyResponseViewSet)
router.register(r'mapping-activities', MappingActivityViewSet)
router.register(r'geographic-data-layers', GeographicDataLayerViewSet)
router.register(r'map-visualizations', MapVisualizationViewSet)
router.register(r'spatial-data-points', SpatialDataPointViewSet)
router.register(r'baseline-studies', BaselineStudyViewSet)
router.register(r'baseline-indicators', BaselineIndicatorViewSet)
router.register(r'baseline-data-collections', BaselineDataCollectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]