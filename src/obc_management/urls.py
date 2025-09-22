"""
URL configuration for obc_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

try:
    from rest_framework.routers import DefaultRouter
    from rest_framework_simplejwt.views import (TokenObtainPairView,
                                                TokenRefreshView)
except ModuleNotFoundError:  # pragma: no cover - fallback for offline tests

    class DefaultRouter:  # minimal stub
        def __init__(self):
            self.urls = []

        def register(self, *args, **kwargs):
            return None

    class _TokenViewStub:
        @classmethod
        def as_view(cls, *args, **kwargs):
            raise NotImplementedError("JWT endpoints require rest_framework_simplejwt.")

    TokenObtainPairView = _TokenViewStub
    TokenRefreshView = _TokenViewStub
from common.admin_views import group_changelist_view

# Import admin customizations
from . import admin as admin_customizations

# API docs import removed - documentation now backend-only

# Main API router
api_router = DefaultRouter()

urlpatterns = [
    # Custom admin views (must come before admin.site.urls)
    path("admin/auth/group/", group_changelist_view, name="custom_group_changelist"),
    path("admin/", admin.site.urls),
    # Main application URLs
    path("", include("common.urls")),
    path(
        "monitoring/",
        include(("monitoring.urls", "monitoring"), namespace="monitoring"),
    ),
    # API Authentication
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # API documentation (backend only - accessible via admin or direct API calls)
    # API endpoints
    path("api/v1/", include(api_router.urls)),
    path("api/administrative/", include("common.api_urls")),
    path("api/communities/", include("communities.api_urls")),
    path("api/mana/", include("mana.api_urls")),
    path("api/coordination/", include("coordination.api_urls")),
    path("api/policies/", include("recommendations.policies.api_urls")),
    path("api/policy-tracking/", include("recommendations.policy_tracking.api_urls")),
    path("api/monitoring/", include("monitoring.api_urls")),
    path("documents/", include(("recommendations.documents.urls", "documents"), namespace="documents")),
    # Browsable API authentication
    path("api-auth/", include("rest_framework.urls")),
    path(
        "", lambda request: redirect("common:dashboard")
    ),  # Redirect root to dashboard
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Add debug toolbar URLs only when the app is installed
    if "debug_toolbar" in settings.INSTALLED_APPS:
        try:
            import debug_toolbar

            urlpatterns = [
                path("__debug__/", include(debug_toolbar.urls)),
            ] + urlpatterns
        except ImportError:
            pass
