"""UI URLs for the Monitoring & Evaluation module."""

from django.urls import path

from . import views

app_name = "monitoring"

urlpatterns = [
    path("", views.monitoring_dashboard, name="home"),
    path("moa-ppas/", views.moa_ppas_dashboard, name="moa_ppas"),
    path("moa-ppas/import/", views.import_moa_data, name="import_moa_data"),
    path("moa-ppas/export/", views.export_moa_data, name="export_moa_data"),
    path("moa-ppas/report/", views.generate_moa_report, name="generate_moa_report"),
    path("moa-ppas/bulk-update/", views.bulk_update_moa_status, name="bulk_update_moa_status"),
    path("moa-ppas/schedule-review/", views.schedule_moa_review, name="schedule_moa_review"),
    path("oobc-initiatives/", views.oobc_initiatives_dashboard, name="oobc_initiatives"),
    path("oobc-initiatives/impact/", views.oobc_impact_report, name="oobc_impact_report"),
    path("oobc-initiatives/performance/", views.oobc_unit_performance, name="oobc_unit_performance"),
    path("oobc-initiatives/export/", views.export_oobc_data, name="export_oobc_data"),
    path("oobc-initiatives/budget/", views.oobc_budget_review, name="oobc_budget_review"),
    path("oobc-initiatives/feedback/", views.oobc_community_feedback, name="oobc_community_feedback"),
    path("obc-requests/", views.obc_requests_dashboard, name="obc_requests"),
    path("obc-requests/priority/", views.obc_priority_queue, name="obc_priority_queue"),
    path("obc-requests/community/", views.obc_community_dashboard, name="obc_community_dashboard"),
    path("obc-requests/report/", views.generate_obc_report, name="generate_obc_report"),
    path("obc-requests/bulk-update/", views.bulk_update_obc_status, name="bulk_update_obc_status"),
    path("obc-requests/export/", views.export_obc_data, name="export_obc_data"),
    path("entry/<uuid:pk>/", views.monitoring_entry_detail, name="detail"),
    path("create/moa/", views.create_moa_entry, name="create_moa"),
    path("create/moa/obc/", views.ajax_create_obc, name="ajax_create_obc"),
    path("create/oobc/", views.create_oobc_entry, name="create_oobc"),
    path("create/request/", views.create_request_entry, name="create_request"),
]
