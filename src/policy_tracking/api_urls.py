from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PolicyRecommendationViewSet, PolicyEvidenceViewSet, 
    PolicyImpactViewSet, PolicyDocumentViewSet
)

app_name = 'policy_tracking_api'

router = DefaultRouter()
router.register(r'recommendations', PolicyRecommendationViewSet)
router.register(r'evidence', PolicyEvidenceViewSet)
router.register(r'impacts', PolicyImpactViewSet)
router.register(r'documents', PolicyDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]