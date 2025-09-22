from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatAPIView, DocumentGenerationAPIView

app_name = "ai_assistant"

# Create router for viewsets
router = DefaultRouter()

urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    # Direct API endpoints
    path("chat/", ChatAPIView.as_view(), name="chat"),
    path(
        "generate-document/",
        DocumentGenerationAPIView.as_view(),
        name="generate_document",
    ),
]
