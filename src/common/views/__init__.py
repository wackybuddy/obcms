"""Domain-organised view exports for the common app."""

from .auth import CustomLoginView, CustomLogoutView, UserRegistrationView, profile
from .communities import (
    communities_add,
    communities_add_municipality,
    communities_delete,
    communities_delete_municipal,
    communities_view,
    communities_view_municipal,
    communities_home,
    communities_manage,
    communities_manage_municipal,
    communities_stakeholders,
    communities_edit,
    communities_edit_municipal,
)
from .coordination import (
    coordination_events,
    coordination_home,
    coordination_organizations,
    coordination_partnerships,
    coordination_view_all,
    organization_create,
    partnership_create,
)
from .dashboard import dashboard
from .mana import (
    mana_geographic_data,
    mana_home,
    mana_manage_assessments,
    mana_new_assessment,
)
from .recommendations import (
    recommendations_by_area,
    recommendations_home,
    recommendations_manage,
    recommendations_new,
)

__all__ = [
    "CustomLoginView",
    "CustomLogoutView",
    "UserRegistrationView",
    "profile",
    "dashboard",
    "communities_home",
    "communities_add",
    "communities_add_municipality",
    "communities_view",
    "communities_view_municipal",
    "communities_manage",
    "communities_manage_municipal",
    "communities_edit",
    "communities_edit_municipal",
    "communities_delete",
    "communities_delete_municipal",
    "communities_stakeholders",
    "mana_home",
    "mana_new_assessment",
    "mana_manage_assessments",
    "mana_geographic_data",
    "coordination_home",
    "coordination_organizations",
    "coordination_partnerships",
    "coordination_events",
    "coordination_view_all",
    "organization_create",
    "partnership_create",
    "recommendations_home",
    "recommendations_new",
    "recommendations_manage",
    "recommendations_by_area",
]
