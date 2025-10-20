"""
API Views for Budget Preparation

Provides REST API endpoints for budget proposals, program budgets, and line items.
Implements Parliament Bill No. 325 budget workflows.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

from .models import BudgetProposal, ProgramBudget, BudgetLineItem
from .serializers import (
    BudgetProposalSerializer,
    ProgramBudgetSerializer,
    BudgetLineItemSerializer,
)


class BudgetProposalViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for BudgetProposal model.

    Provides endpoints for:
    - Listing budget proposals (GET /proposals/)
    - Creating budget proposals (POST /proposals/)
    - Retrieving individual proposals (GET /proposals/{id}/)
    - Updating proposals (PUT /proposals/{id}/)
    - Deleting proposals (DELETE /proposals/{id}/)
    """

    queryset = BudgetProposal.objects.all()
    serializer_class = BudgetProposalSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        """Filter budgets by organization (multi-tenant)."""
        queryset = BudgetProposal.objects.all()
        # If organization scoping is implemented, add it here
        return queryset


class ProgramBudgetViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for ProgramBudget model.

    Provides endpoints for program budgets linked to proposals.
    """

    queryset = ProgramBudget.objects.all()
    serializer_class = ProgramBudgetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]


class BudgetLineItemViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for BudgetLineItem model.

    Provides endpoints for detailed line items within programs.
    """

    queryset = BudgetLineItem.objects.all()
    serializer_class = BudgetLineItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
