from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    OBCCommunityViewSet, CommunityLivelihoodViewSet, CommunityInfrastructureViewSet,
    StakeholderViewSet, StakeholderEngagementViewSet
)

router = DefaultRouter()
router.register(r'communities', OBCCommunityViewSet)
router.register(r'livelihoods', CommunityLivelihoodViewSet)
router.register(r'infrastructure', CommunityInfrastructureViewSet)
router.register(r'stakeholders', StakeholderViewSet)
router.register(r'engagements', StakeholderEngagementViewSet)

app_name = 'communities_api'

urlpatterns = [
    path('', include(router.urls)),
]