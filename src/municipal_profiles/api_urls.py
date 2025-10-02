from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import MunicipalOBCProfileViewSet

router = DefaultRouter()
router.register(
    r"profiles", MunicipalOBCProfileViewSet, basename="municipal-obc-profile"
)

app_name = "municipal_profiles_api"

urlpatterns = [
    path("", include(router.urls)),
]
