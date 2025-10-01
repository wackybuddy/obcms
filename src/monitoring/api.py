"""
REST API ViewSets and Serializers for Planning & Budgeting Integration.

Part of Phase 8: API Integration & Documentation.
"""

from rest_framework import viewsets, serializers, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg

from .models import (
    StrategicGoal,
    AnnualPlanningCycle,
    BudgetScenario,
    ScenarioAllocation,
)


# =============================================================================
# Serializers
# =============================================================================

class StrategicGoalSerializer(serializers.ModelSerializer):
    """Serializer for StrategicGoal model."""

    duration_years = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    achievement_rate = serializers.ReadOnlyField()
    linked_ppas_count = serializers.SerializerMethodField()
    linked_policies_count = serializers.SerializerMethodField()

    class Meta:
        model = StrategicGoal
        fields = [
            'id', 'title', 'description', 'sector', 'priority_level',
            'start_year', 'target_year', 'duration_years',
            'baseline_value', 'target_value', 'current_value',
            'indicator_description', 'progress_percentage',
            'aligns_with_rdp', 'rdp_reference', 'national_framework_alignment',
            'linked_ppas_count', 'linked_policies_count',
            'status', 'is_active', 'achievement_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_linked_ppas_count(self, obj):
        return obj.linked_ppas.count()

    def get_linked_policies_count(self, obj):
        return obj.linked_policies.count()


class AnnualPlanningCycleSerializer(serializers.ModelSerializer):
    """Serializer for AnnualPlanningCycle model."""

    budget_utilization_rate = serializers.ReadOnlyField()
    is_current_cycle = serializers.ReadOnlyField()
    unallocated_budget = serializers.ReadOnlyField()
    strategic_goals_count = serializers.SerializerMethodField()
    ppas_count = serializers.SerializerMethodField()
    needs_count = serializers.SerializerMethodField()

    class Meta:
        model = AnnualPlanningCycle
        fields = [
            'id', 'fiscal_year', 'planning_start_date', 'planning_end_date',
            'budget_submission_date', 'execution_start_date', 'execution_end_date',
            'total_budget_envelope', 'allocated_budget', 'budget_utilization_rate',
            'unallocated_budget', 'status', 'is_current_cycle',
            'strategic_goals_count', 'ppas_count', 'needs_count',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_strategic_goals_count(self, obj):
        return obj.strategic_goals.count()

    def get_ppas_count(self, obj):
        return obj.monitoring_entries.count()

    def get_needs_count(self, obj):
        return obj.needs_addressed.count()


class ScenarioAllocationSerializer(serializers.ModelSerializer):
    """Serializer for ScenarioAllocation model."""

    ppa_title = serializers.CharField(source='ppa.title', read_only=True)
    ppa_sector = serializers.CharField(source='ppa.sector', read_only=True)

    class Meta:
        model = ScenarioAllocation
        fields = [
            'id', 'ppa', 'ppa_title', 'ppa_sector',
            'allocated_amount', 'priority_rank', 'status',
            'allocation_rationale', 'cost_per_beneficiary',
            'needs_coverage_score', 'equity_score',
            'strategic_alignment_score', 'overall_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'cost_per_beneficiary', 'needs_coverage_score',
            'equity_score', 'strategic_alignment_score', 'overall_score',
            'created_at', 'updated_at'
        ]


class BudgetScenarioSerializer(serializers.ModelSerializer):
    """Serializer for BudgetScenario model."""

    allocations = ScenarioAllocationSerializer(many=True, read_only=True)
    budget_utilization_rate = serializers.ReadOnlyField()
    unallocated_budget = serializers.ReadOnlyField()
    is_fully_allocated = serializers.ReadOnlyField()
    optimization_weights_sum = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = BudgetScenario
        fields = [
            'id', 'name', 'description', 'scenario_type', 'total_budget',
            'allocated_budget', 'budget_utilization_rate', 'unallocated_budget',
            'is_baseline', 'planning_cycle', 'status',
            'weight_needs_coverage', 'weight_equity', 'weight_strategic_alignment',
            'optimization_weights_sum', 'optimization_score',
            'estimated_beneficiaries', 'estimated_needs_addressed',
            'is_fully_allocated', 'allocations',
            'created_by', 'created_by_username', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'allocated_budget', 'optimization_score',
            'estimated_beneficiaries', 'estimated_needs_addressed',
            'created_at', 'updated_at'
        ]


# Simplified serializer without nested allocations
class BudgetScenarioListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing scenarios."""

    allocations_count = serializers.SerializerMethodField()
    budget_utilization_rate = serializers.ReadOnlyField()

    class Meta:
        model = BudgetScenario
        fields = [
            'id', 'name', 'scenario_type', 'total_budget', 'allocated_budget',
            'budget_utilization_rate', 'is_baseline', 'status',
            'optimization_score', 'estimated_beneficiaries',
            'allocations_count', 'created_at'
        ]

    def get_allocations_count(self, obj):
        return obj.allocations.count()


# =============================================================================
# ViewSets
# =============================================================================

class StrategicGoalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Strategic Goals.

    list: Get all strategic goals
    retrieve: Get a specific strategic goal
    create: Create a new strategic goal
    update: Update a strategic goal
    partial_update: Partially update a strategic goal
    destroy: Delete a strategic goal
    """

    queryset = StrategicGoal.objects.all()
    serializer_class = StrategicGoalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sector', 'priority_level', 'status', 'aligns_with_rdp']
    search_fields = ['title', 'description', 'rdp_reference']
    ordering_fields = ['start_year', 'target_year', 'progress_percentage', 'created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active strategic goals."""
        active_goals = self.queryset.filter(status='active')
        serializer = self.get_serializer(active_goals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_sector(self, request):
        """Get strategic goals grouped by sector."""
        sector_breakdown = {}
        for goal in self.queryset.all():
            sector = goal.get_sector_display()
            if sector not in sector_breakdown:
                sector_breakdown[sector] = []
            sector_breakdown[sector].append(self.get_serializer(goal).data)
        return Response(sector_breakdown)


class AnnualPlanningCycleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Annual Planning Cycles.
    """

    queryset = AnnualPlanningCycle.objects.all()
    serializer_class = AnnualPlanningCycleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'status']
    ordering_fields = ['fiscal_year', 'created_at']
    ordering = ['-fiscal_year']

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current planning cycle."""
        from django.utils import timezone
        current_year = timezone.now().year
        current_cycle = self.queryset.filter(fiscal_year=current_year).first()

        if current_cycle:
            serializer = self.get_serializer(current_cycle)
            return Response(serializer.data)
        return Response({'detail': 'No current planning cycle found.'}, status=404)


class BudgetScenarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Budget Scenarios.

    Supports creating, listing, retrieving, updating scenarios.
    Includes actions for optimization and comparison.
    """

    queryset = BudgetScenario.objects.prefetch_related('allocations')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'scenario_type', 'is_baseline', 'planning_cycle']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'total_budget', 'optimization_score']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use different serializers for list vs detail views."""
        if self.action == 'list':
            return BudgetScenarioListSerializer
        return BudgetScenarioSerializer

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def optimize(self, request, pk=None):
        """
        Run optimization algorithm for this scenario.

        POST /api/scenarios/{id}/optimize/
        """
        scenario = self.get_object()

        try:
            from monitoring.analytics import generate_budget_recommendations
            from decimal import Decimal

            # Get eligible PPAs
            from .models import MonitoringEntry

            eligible_ppas = MonitoringEntry.objects.filter(
                status__in=['approved', 'planned']
            ).prefetch_related('addresses_needs', 'contributing_strategic_goals')

            # Score each PPA
            ppa_scores = []
            for ppa in eligible_ppas:
                needs_count = ppa.addresses_needs.count()
                needs_score = Decimal(str(needs_count * 10))

                coverage_count = ppa.municipality_coverage.count() + ppa.province_coverage.count()
                equity_score = Decimal(str(coverage_count * 5))

                strategic_goals_count = ppa.contributing_strategic_goals.count()
                strategic_score = Decimal(str(strategic_goals_count * 15))

                overall_score = (
                    (needs_score * scenario.weight_needs_coverage) +
                    (equity_score * scenario.weight_equity) +
                    (strategic_score * scenario.weight_strategic_alignment)
                )

                budget_request = ppa.budget_allocation or Decimal('1')
                efficiency = overall_score / budget_request if budget_request > 0 else Decimal('0')

                ppa_scores.append({
                    'ppa': ppa,
                    'overall_score': overall_score,
                    'efficiency': efficiency,
                    'budget_request': budget_request,
                    'needs_score': needs_score,
                    'equity_score': equity_score,
                    'strategic_score': strategic_score,
                })

            # Sort by efficiency
            ppa_scores.sort(key=lambda x: float(x['efficiency']), reverse=True)

            # Greedy allocation
            remaining_budget = scenario.total_budget
            allocated_count = 0

            # Clear existing allocations
            scenario.allocations.all().delete()

            for idx, item in enumerate(ppa_scores, 1):
                if remaining_budget <= 0:
                    break

                ppa = item['ppa']
                budget_request = item['budget_request']
                allocation_amount = min(budget_request, remaining_budget)

                if allocation_amount > 0:
                    ScenarioAllocation.objects.create(
                        scenario=scenario,
                        ppa=ppa,
                        allocated_amount=allocation_amount,
                        priority_rank=idx,
                        status='proposed',
                        allocation_rationale=f"Optimized (rank {idx})",
                        needs_coverage_score=item['needs_score'],
                        equity_score=item['equity_score'],
                        strategic_alignment_score=item['strategic_score'],
                        overall_score=item['overall_score'],
                    )
                    remaining_budget -= allocation_amount
                    allocated_count += 1

            # Update scenario optimization score
            if allocated_count > 0:
                avg_score = sum(item['overall_score'] for item in ppa_scores[:allocated_count]) / allocated_count
                scenario.optimization_score = avg_score
                scenario.save()

            scenario.recalculate_totals()

            serializer = self.get_serializer(scenario)
            return Response({
                'message': f'Optimization complete! Allocated {allocated_count} PPAs.',
                'scenario': serializer.data
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def compare(self, request):
        """
        Compare multiple scenarios.

        POST /api/scenarios/compare/
        Body: {"scenario_ids": ["uuid1", "uuid2", ...]}
        """
        scenario_ids = request.data.get('scenario_ids', [])

        if not scenario_ids:
            return Response(
                {'error': 'scenario_ids required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        scenarios = self.queryset.filter(id__in=scenario_ids)

        comparison = []
        for scenario in scenarios:
            comparison.append({
                'id': str(scenario.id),
                'name': scenario.name,
                'type': scenario.scenario_type,
                'total_budget': float(scenario.total_budget),
                'allocated_budget': float(scenario.allocated_budget),
                'utilization_rate': float(scenario.budget_utilization_rate),
                'optimization_score': float(scenario.optimization_score or 0),
                'estimated_beneficiaries': scenario.estimated_beneficiaries,
                'needs_addressed': scenario.estimated_needs_addressed,
                'allocations_count': scenario.allocations.count(),
            })

        return Response({'scenarios': comparison})


class ScenarioAllocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Scenario Allocations.
    """

    queryset = ScenarioAllocation.objects.select_related('scenario', 'ppa')
    serializer_class = ScenarioAllocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['scenario', 'status', 'ppa__sector']
    ordering_fields = ['priority_rank', 'allocated_amount', 'overall_score']
    ordering = ['priority_rank']

    @action(detail=True, methods=['post'])
    def calculate_metrics(self, request, pk=None):
        """
        Recalculate metrics for this allocation.

        POST /api/allocations/{id}/calculate_metrics/
        """
        allocation = self.get_object()
        allocation.calculate_metrics()

        serializer = self.get_serializer(allocation)
        return Response(serializer.data)
