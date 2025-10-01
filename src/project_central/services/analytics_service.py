"""
Analytics Service

Data aggregation and analysis for project management and budget monitoring.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F, Case, When, Value, DecimalField
from decimal import Decimal

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for analytics and data aggregation.

    Provides:
    - Budget allocation analysis by sector, source, region
    - Utilization rate calculations
    - Cost-effectiveness metrics
    - Workflow performance analytics
    - Trend analysis
    """

    @classmethod
    def get_budget_allocation_by_sector(cls, fiscal_year=None, region=None):
        """
        Aggregate budget allocation by sector.

        Args:
            fiscal_year: Fiscal year to filter (optional)
            region: Region to filter (optional)

        Returns:
            dict: Sector allocation data
        """
        from monitoring.models import MonitoringEntry

        queryset = MonitoringEntry.objects.filter(
            approval_status__in=[
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
            ]
        )

        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)

        if region:
            queryset = queryset.filter(
                Q(implementing_community__municipality__province__region=region) |
                Q(lead_organization__region=region)
            )

        # Aggregate by sector
        sector_data = queryset.values('sector').annotate(
            total_budget=Sum('budget_allocation'),
            project_count=Count('id'),
            avg_budget=Avg('budget_allocation'),
            total_disbursed=Sum('total_disbursed'),
        ).order_by('-total_budget')

        # Calculate utilization rates
        result = []
        total_budget = Decimal('0')
        total_disbursed = Decimal('0')

        for item in sector_data:
            total_budget += item['total_budget'] or Decimal('0')
            total_disbursed += item['total_disbursed'] or Decimal('0')

            utilization_pct = 0
            if item['total_budget'] and item['total_budget'] > 0:
                utilization_pct = (item['total_disbursed'] or Decimal('0')) / item['total_budget'] * 100

            result.append({
                'sector': item['sector'],
                'total_budget': float(item['total_budget'] or 0),
                'project_count': item['project_count'],
                'avg_budget': float(item['avg_budget'] or 0),
                'total_disbursed': float(item['total_disbursed'] or 0),
                'utilization_pct': float(utilization_pct),
            })

        # Add totals
        overall_utilization = 0
        if total_budget > 0:
            overall_utilization = (total_disbursed / total_budget) * 100

        return {
            'sectors': result,
            'totals': {
                'total_budget': float(total_budget),
                'total_disbursed': float(total_disbursed),
                'project_count': sum(s['project_count'] for s in result),
                'utilization_pct': float(overall_utilization),
            }
        }

    @classmethod
    def get_budget_allocation_by_source(cls, fiscal_year=None):
        """
        Aggregate budget allocation by funding source.

        Args:
            fiscal_year: Fiscal year to filter (optional)

        Returns:
            dict: Funding source allocation data
        """
        from monitoring.models import MonitoringEntry

        queryset = MonitoringEntry.objects.filter(
            approval_status__in=[
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
            ]
        )

        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)

        # Aggregate by funding source
        source_data = queryset.values('funding_source').annotate(
            total_budget=Sum('budget_allocation'),
            project_count=Count('id'),
            avg_budget=Avg('budget_allocation'),
        ).order_by('-total_budget')

        result = []
        for item in source_data:
            result.append({
                'funding_source': item['funding_source'],
                'total_budget': float(item['total_budget'] or 0),
                'project_count': item['project_count'],
                'avg_budget': float(item['avg_budget'] or 0),
            })

        return {
            'sources': result,
            'total_budget': sum(s['total_budget'] for s in result),
            'project_count': sum(s['project_count'] for s in result),
        }

    @classmethod
    def get_budget_allocation_by_region(cls, fiscal_year=None):
        """
        Aggregate budget allocation by region.

        Args:
            fiscal_year: Fiscal year to filter (optional)

        Returns:
            dict: Regional allocation data
        """
        from monitoring.models import MonitoringEntry

        queryset = MonitoringEntry.objects.filter(
            approval_status__in=[
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
            ]
        ).select_related('implementing_community__municipality__province__region')

        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)

        # Aggregate by region
        region_data = queryset.values(
            'implementing_community__municipality__province__region__name'
        ).annotate(
            total_budget=Sum('budget_allocation'),
            project_count=Count('id'),
            avg_budget=Avg('budget_allocation'),
        ).order_by('-total_budget')

        result = []
        for item in region_data:
            result.append({
                'region': item['implementing_community__municipality__province__region__name'] or 'Unspecified',
                'total_budget': float(item['total_budget'] or 0),
                'project_count': item['project_count'],
                'avg_budget': float(item['avg_budget'] or 0),
            })

        return {
            'regions': result,
            'total_budget': sum(r['total_budget'] for r in result),
            'project_count': sum(r['project_count'] for r in result),
        }

    @classmethod
    def get_utilization_rates(cls, fiscal_year=None):
        """
        Calculate budget utilization rates.

        Args:
            fiscal_year: Fiscal year to filter (optional)

        Returns:
            dict: Utilization metrics
        """
        from monitoring.models import MonitoringEntry
        from project_central.models import BudgetCeiling

        # Overall PPA utilization
        ppa_queryset = MonitoringEntry.objects.filter(status='ongoing')
        if fiscal_year:
            ppa_queryset = ppa_queryset.filter(fiscal_year=fiscal_year)

        ppa_stats = ppa_queryset.aggregate(
            total_allocated=Sum('budget_allocation'),
            total_obligated=Sum('total_obligated'),
            total_disbursed=Sum('total_disbursed'),
            project_count=Count('id'),
        )

        obligation_rate = 0
        disbursement_rate = 0

        if ppa_stats['total_allocated'] and ppa_stats['total_allocated'] > 0:
            obligation_rate = (ppa_stats['total_obligated'] or Decimal('0')) / ppa_stats['total_allocated'] * 100
            disbursement_rate = (ppa_stats['total_disbursed'] or Decimal('0')) / ppa_stats['total_allocated'] * 100

        # Budget ceiling utilization
        ceiling_year = fiscal_year or timezone.now().year
        ceilings = BudgetCeiling.objects.filter(
            fiscal_year=ceiling_year,
            is_active=True,
        )

        ceiling_stats = []
        for ceiling in ceilings:
            ceiling_stats.append({
                'name': ceiling.name,
                'ceiling_amount': float(ceiling.ceiling_amount),
                'allocated_amount': float(ceiling.allocated_amount),
                'utilization_pct': ceiling.get_utilization_percentage(),
                'remaining_amount': float(ceiling.get_remaining_amount()),
            })

        return {
            'ppa_utilization': {
                'total_allocated': float(ppa_stats['total_allocated'] or 0),
                'total_obligated': float(ppa_stats['total_obligated'] or 0),
                'total_disbursed': float(ppa_stats['total_disbursed'] or 0),
                'obligation_rate': float(obligation_rate),
                'disbursement_rate': float(disbursement_rate),
                'project_count': ppa_stats['project_count'],
            },
            'ceiling_utilization': ceiling_stats,
        }

    @classmethod
    def get_cost_effectiveness_metrics(cls, sector=None, fiscal_year=None):
        """
        Calculate cost-effectiveness metrics.

        Args:
            sector: Filter by sector (optional)
            fiscal_year: Filter by fiscal year (optional)

        Returns:
            dict: Cost-effectiveness data
        """
        from monitoring.models import MonitoringEntry

        queryset = MonitoringEntry.objects.filter(
            status__in=['ongoing', 'completed'],
        ).exclude(
            Q(budget_allocation__isnull=True) | Q(budget_allocation=0)
        )

        if sector:
            queryset = queryset.filter(sector=sector)

        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)

        # Calculate cost per beneficiary
        projects_with_beneficiaries = queryset.exclude(
            Q(beneficiary_count__isnull=True) | Q(beneficiary_count=0)
        ).annotate(
            cost_per_beneficiary=F('budget_allocation') / F('beneficiary_count')
        )

        cost_stats = projects_with_beneficiaries.aggregate(
            avg_cost_per_beneficiary=Avg('cost_per_beneficiary'),
            min_cost_per_beneficiary=Sum('cost_per_beneficiary'),  # Will be recalculated below
            max_cost_per_beneficiary=Sum('cost_per_beneficiary'),  # Will be recalculated below
            total_beneficiaries=Sum('beneficiary_count'),
            total_budget=Sum('budget_allocation'),
        )

        # Manual min/max calculation (Django doesn't support Min/Max on annotated fields)
        cost_values = [
            float(p.budget_allocation / p.beneficiary_count)
            for p in projects_with_beneficiaries
            if p.beneficiary_count and p.beneficiary_count > 0
        ]

        min_cost = min(cost_values) if cost_values else 0
        max_cost = max(cost_values) if cost_values else 0

        # Calculate by sector
        sector_metrics = []
        if not sector:
            sector_data = queryset.values('sector').annotate(
                total_budget=Sum('budget_allocation'),
                total_beneficiaries=Sum('beneficiary_count'),
                project_count=Count('id'),
            )

            for item in sector_data:
                avg_cost = 0
                if item['total_beneficiaries'] and item['total_beneficiaries'] > 0:
                    avg_cost = item['total_budget'] / item['total_beneficiaries']

                sector_metrics.append({
                    'sector': item['sector'],
                    'total_budget': float(item['total_budget'] or 0),
                    'total_beneficiaries': item['total_beneficiaries'] or 0,
                    'avg_cost_per_beneficiary': float(avg_cost),
                    'project_count': item['project_count'],
                })

        overall_cost_per_beneficiary = 0
        if cost_stats['total_beneficiaries'] and cost_stats['total_beneficiaries'] > 0:
            overall_cost_per_beneficiary = cost_stats['total_budget'] / cost_stats['total_beneficiaries']

        return {
            'overall': {
                'avg_cost_per_beneficiary': float(cost_stats['avg_cost_per_beneficiary'] or 0),
                'min_cost_per_beneficiary': float(min_cost),
                'max_cost_per_beneficiary': float(max_cost),
                'total_beneficiaries': cost_stats['total_beneficiaries'] or 0,
                'total_budget': float(cost_stats['total_budget'] or 0),
                'overall_cost_per_beneficiary': float(overall_cost_per_beneficiary),
            },
            'by_sector': sector_metrics,
        }

    @classmethod
    def get_workflow_performance_metrics(cls, fiscal_year=None):
        """
        Calculate workflow performance metrics.

        Args:
            fiscal_year: Filter by fiscal year (optional)

        Returns:
            dict: Workflow performance data
        """
        from project_central.models import ProjectWorkflow

        queryset = ProjectWorkflow.objects.all()

        if fiscal_year:
            queryset = queryset.filter(
                Q(initiated_date__year=fiscal_year) |
                Q(ppa__fiscal_year=fiscal_year)
            )

        # Overall metrics
        total_workflows = queryset.count()
        on_track = queryset.filter(is_on_track=True).count()
        blocked = queryset.filter(is_blocked=True).count()

        # By stage
        stage_distribution = dict(
            queryset.values('current_stage').annotate(
                count=Count('id')
            ).values_list('current_stage', 'count')
        )

        # By priority
        priority_distribution = dict(
            queryset.values('priority_level').annotate(
                count=Count('id')
            ).values_list('priority_level', 'count')
        )

        # Calculate average time in each stage
        stage_durations = {}
        for workflow in queryset:
            if workflow.stage_history:
                for entry in workflow.stage_history:
                    stage = entry.get('stage')
                    entered = entry.get('entered_at')
                    exited = entry.get('exited_at')

                    if entered and exited:
                        duration = (
                            timezone.datetime.fromisoformat(exited) -
                            timezone.datetime.fromisoformat(entered)
                        ).days

                        if stage not in stage_durations:
                            stage_durations[stage] = []
                        stage_durations[stage].append(duration)

        avg_stage_durations = {}
        for stage, durations in stage_durations.items():
            avg_stage_durations[stage] = sum(durations) / len(durations) if durations else 0

        # Completion rate
        completed = queryset.filter(current_stage='completion').count()
        completion_rate = (completed / total_workflows * 100) if total_workflows > 0 else 0

        return {
            'total_workflows': total_workflows,
            'on_track': on_track,
            'blocked': blocked,
            'on_track_pct': (on_track / total_workflows * 100) if total_workflows > 0 else 0,
            'blocked_pct': (blocked / total_workflows * 100) if total_workflows > 0 else 0,
            'completion_rate': float(completion_rate),
            'stage_distribution': stage_distribution,
            'priority_distribution': priority_distribution,
            'avg_stage_durations': avg_stage_durations,
        }

    @classmethod
    def get_trend_analysis(cls, metric, start_date, end_date, interval='month'):
        """
        Generate trend analysis for a given metric.

        Args:
            metric: Metric to analyze ('budget', 'projects', 'beneficiaries')
            start_date: Start date for trend
            end_date: End date for trend
            interval: Time interval ('month' or 'quarter')

        Returns:
            list: Trend data points
        """
        from monitoring.models import MonitoringEntry
        from django.db.models.functions import TruncMonth, TruncQuarter

        queryset = MonitoringEntry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
        )

        # Choose truncation function
        trunc_func = TruncMonth if interval == 'month' else TruncQuarter

        if metric == 'budget':
            trend_data = queryset.annotate(
                period=trunc_func('created_at')
            ).values('period').annotate(
                value=Sum('budget_allocation')
            ).order_by('period')

        elif metric == 'projects':
            trend_data = queryset.annotate(
                period=trunc_func('created_at')
            ).values('period').annotate(
                value=Count('id')
            ).order_by('period')

        elif metric == 'beneficiaries':
            trend_data = queryset.annotate(
                period=trunc_func('created_at')
            ).values('period').annotate(
                value=Sum('beneficiary_count')
            ).order_by('period')

        else:
            raise ValueError(f"Unknown metric: {metric}")

        # Convert to list
        result = []
        for item in trend_data:
            result.append({
                'period': item['period'].isoformat() if item['period'] else None,
                'value': float(item['value'] or 0),
            })

        return result

    @classmethod
    def get_dashboard_summary(cls, fiscal_year=None):
        """
        Get comprehensive dashboard summary.

        Args:
            fiscal_year: Fiscal year to filter (optional)

        Returns:
            dict: Dashboard data
        """
        return {
            'budget_by_sector': cls.get_budget_allocation_by_sector(fiscal_year),
            'budget_by_source': cls.get_budget_allocation_by_source(fiscal_year),
            'budget_by_region': cls.get_budget_allocation_by_region(fiscal_year),
            'utilization_rates': cls.get_utilization_rates(fiscal_year),
            'cost_effectiveness': cls.get_cost_effectiveness_metrics(fiscal_year=fiscal_year),
            'workflow_performance': cls.get_workflow_performance_metrics(fiscal_year),
        }
