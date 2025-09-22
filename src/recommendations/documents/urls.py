from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views

# Create router for API endpoints
router = DefaultRouter()
router.register(r"documents", api_views.DocumentViewSet, basename="document")
router.register(r"categories", api_views.DocumentCategoryViewSet, basename="category")
router.register(r"comments", api_views.DocumentCommentViewSet, basename="comment")

app_name = "documents"

urlpatterns = [
    path("api/", include(router.urls)),
]
