"""UI URLs for the Monitoring & Evaluation module."""

from django.urls import path

from . import views

app_name = "monitoring"

urlpatterns = [
    path("", views.monitoring_dashboard, name="home"),
    path("entry/<uuid:pk>/", views.monitoring_entry_detail, name="detail"),
    path("create/moa/", views.create_moa_entry, name="create_moa"),
    path("create/oobc/", views.create_oobc_entry, name="create_oobc"),
    path("create/request/", views.create_request_entry, name="create_request"),
]
