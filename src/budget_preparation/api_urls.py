"""
Budget Preparation API URLs

Provides REST API endpoints for budget proposals, program budgets, and line items.
Implements Parliament Bill No. 325 budget workflows.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from budget_preparation.api_views import (
    BudgetProposalViewSet,
    ProgramBudgetViewSet,
    BudgetLineItemViewSet,
)

app_name = 'budget'

router = DefaultRouter()

# Register budget viewsets
router.register(r'proposals', BudgetProposalViewSet, basename='proposal')
router.register(r'programs', ProgramBudgetViewSet, basename='program')
router.register(r'line-items', BudgetLineItemViewSet, basename='line-item')

urlpatterns = [
    # Router URLs (for viewsets)
    path('', include(router.urls)),
]
