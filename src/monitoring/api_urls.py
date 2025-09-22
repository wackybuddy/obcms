"""URL configuration for Monitoring & Evaluation API endpoints."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import MonitoringEntryViewSet, MonitoringUpdateViewSet

app_name = "monitoring_api"

router = DefaultRouter()
router.register(r"entries", MonitoringEntryViewSet)
router.register(r"updates", MonitoringUpdateViewSet)

urlpatterns = [path("", include(router.urls))]
