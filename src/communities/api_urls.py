from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import (
    CommunityInfrastructureViewSet,
    CommunityLivelihoodViewSet,
    MunicipalityCoverageViewSet,
    OBCCommunityViewSet,
    StakeholderEngagementViewSet,
    StakeholderViewSet,
)

router = DefaultRouter()
router.register(r"municipalities", MunicipalityCoverageViewSet)
router.register(r"communities", OBCCommunityViewSet)
router.register(r"livelihoods", CommunityLivelihoodViewSet)
router.register(r"infrastructure", CommunityInfrastructureViewSet)
router.register(r"stakeholders", StakeholderViewSet)
router.register(r"engagements", StakeholderEngagementViewSet)

app_name = "communities_api"

urlpatterns = [
    path("", include(router.urls)),
]
