from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'policies_api'

router = DefaultRouter()
# Add policy viewsets here when implemented

urlpatterns = [
    path('', include(router.urls)),
]