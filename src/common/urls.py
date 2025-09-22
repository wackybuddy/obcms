from django.urls import path

from communities import data_utils
from coordination import views as coordination_views

from . import views

app_name = "common"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("communities/", views.communities_home, name="communities_home"),
    path("communities/add/", views.communities_add, name="communities_add"),
    path(
        "communities/add/municipality/",
        views.communities_add_municipality,
        name="communities_add_municipality",
    ),
    path(
        "communities/managebarangayobc/",
        views.communities_manage,
        name="communities_manage",
    ),
    path(
        "communities/managebarangayobc/<int:community_id>/edit/",
        views.communities_edit,
        name="communities_edit",
    ),
    path(
        "communities/managebarangayobc/<int:community_id>/delete/",
        views.communities_delete,
        name="communities_delete",
    ),
    path(
        "communities/managemunicipalobc/",
        views.communities_manage_municipal,
        name="communities_manage_municipal",
    ),
    path(
        "communities/managemunicipalobc/<int:coverage_id>/edit/",
        views.communities_edit_municipal,
        name="communities_edit_municipal",
    ),
    path(
        "communities/managemunicipalobc/<int:coverage_id>/delete/",
        views.communities_delete_municipal,
        name="communities_delete_municipal",
    ),
    path(
        "communities/stakeholders/",
        views.communities_stakeholders,
        name="communities_stakeholders",
    ),
    path("mana/", views.mana_home, name="mana_home"),
    path("mana/new-assessment/", views.mana_new_assessment, name="mana_new_assessment"),
    path(
        "mana/manage-assessments/",
        views.mana_manage_assessments,
        name="mana_manage_assessments",
    ),
    path(
        "mana/geographic-data/", views.mana_geographic_data, name="mana_geographic_data"
    ),
    path("coordination/", views.coordination_home, name="coordination_home"),
    path(
        "coordination/organizations/",
        views.coordination_organizations,
        name="coordination_organizations",
    ),
    path(
        "coordination/organizations/add/",
        coordination_views.organization_create,
        name="coordination_organization_add",
    ),
    path(
        "coordination/partnerships/add/",
        coordination_views.partnership_create,
        name="coordination_partnership_add",
    ),
    path(
        "coordination/partnerships/",
        views.coordination_partnerships,
        name="coordination_partnerships",
    ),
    path("coordination/events/", views.coordination_events, name="coordination_events"),
    path(
        "coordination/view-all/",
        views.coordination_view_all,
        name="coordination_view_all",
    ),
    path("recommendations/", views.recommendations_home, name="recommendations_home"),
    path("recommendations/new/", views.recommendations_new, name="recommendations_new"),
    path(
        "recommendations/manage/",
        views.recommendations_manage,
        name="recommendations_manage",
    ),
    path(
        "recommendations/area/<str:area_slug>/",
        views.recommendations_by_area,
        name="recommendations_by_area",
    ),
    # Data Import/Export/Report URLs
    path(
        "communities/import/",
        data_utils.import_communities_csv,
        name="import_communities",
    ),
    path(
        "communities/export/", data_utils.export_communities, name="export_communities"
    ),
    path(
        "communities/report/",
        data_utils.generate_obc_report,
        name="generate_obc_report",
    ),
    path("data-guidelines/", data_utils.data_guidelines, name="data_guidelines"),
    path("", views.dashboard, name="home"),  # Default to dashboard
]
