"""
Serializers for Budget Preparation API

Defines serialization/deserialization for budget models.
"""

from rest_framework import serializers
from .models import BudgetProposal, ProgramBudget, BudgetLineItem


class BudgetLineItemSerializer(serializers.ModelSerializer):
    """Serializer for BudgetLineItem model."""

    class Meta:
        model = BudgetLineItem
        fields = [
            'id',
            'program_budget',
            'description',
            'amount',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgramBudgetSerializer(serializers.ModelSerializer):
    """Serializer for ProgramBudget model."""

    line_items = BudgetLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProgramBudget
        fields = [
            'id',
            'budget_proposal',
            'monitoring_entry',
            'requested_amount',
            'approved_amount',
            'priority_rank',
            'status',
            'line_items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BudgetProposalSerializer(serializers.ModelSerializer):
    """Serializer for BudgetProposal model."""

    programs = ProgramBudgetSerializer(
        source='program_budgets',
        many=True,
        read_only=True
    )

    class Meta:
        model = BudgetProposal
        fields = [
            'id',
            'organization',
            'fiscal_year',
            'title',
            'description',
            'total_requested_budget',
            'total_approved_budget',
            'status',
            'programs',
            'submitted_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_fiscal_year(self, value):
        """Validate fiscal year is reasonable."""
        if value < 2020 or value > 2100:
            raise serializers.ValidationError(
                "Fiscal year must be between 2020 and 2100."
            )
        return value

    def validate_total_requested_budget(self, value):
        """Validate budget amount is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Budget amount must be greater than zero."
            )
        return value
