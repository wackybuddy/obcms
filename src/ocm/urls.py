from django.urls import path

from . import views

app_name = "ocm"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("budget/", views.ConsolidatedBudgetView.as_view(), name="consolidated_budget"),
    path("planning/", views.PlanningOverviewView.as_view(), name="planning_overview"),
    path("coordination/", views.CoordinationMatrixView.as_view(), name="coordination_matrix"),
    path("performance/", views.PerformanceOverviewView.as_view(), name="performance_overview"),
    path("reports/", views.ReportsView.as_view(), name="reports_list"),
]
