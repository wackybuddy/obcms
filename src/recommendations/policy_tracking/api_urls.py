from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    PolicyDocumentViewSet,
    PolicyEvidenceViewSet,
    PolicyImpactViewSet,
    PolicyRecommendationViewSet,
)

app_name = "policy_tracking_api"

router = DefaultRouter()
router.register(r"recommendations", PolicyRecommendationViewSet)
router.register(r"evidence", PolicyEvidenceViewSet)
router.register(r"impacts", PolicyImpactViewSet)
router.register(r"documents", PolicyDocumentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
