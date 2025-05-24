from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserViewSet, RegionViewSet, ProvinceViewSet, MunicipalityViewSet, BarangayViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'provinces', ProvinceViewSet)
router.register(r'municipalities', MunicipalityViewSet)
router.register(r'barangays', BarangayViewSet)

app_name = 'common_api'

urlpatterns = [
    path('', include(router.urls)),
]