"""
Analytics & Forecasting Utilities for Budget Planning.

Part of Phase 7: Analytics & Forecasting.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone


def calculate_budget_trends(years=5):
    """
    Calculate budget allocation trends over specified years.

    Returns:
        dict: Trend data including totals, growth rates, sector breakdowns
    """
    from monitoring.models import MonitoringEntry

    current_year = timezone.now().year
    start_year = current_year - years

    trends = {
        'years': [],
        'total_budget': [],
        'ppas_count': [],
        'avg_budget_per_ppa': [],
        'sectors': {},
    }

    for year in range(start_year, current_year + 1):
        year_data = MonitoringEntry.objects.filter(
            start_date__year=year
        ).aggregate(
            total=Sum('budget_allocation'),
            count=Count('id'),
            avg=Avg('budget_allocation')
        )

        trends['years'].append(year)
        trends['total_budget'].append(float(year_data['total'] or 0))
        trends['ppas_count'].append(year_data['count'] or 0)
        trends['avg_budget_per_ppa'].append(float(year_data['avg'] or 0))

    # Calculate year-over-year growth
    trends['growth_rates'] = []
    for i in range(1, len(trends['total_budget'])):
        prev = trends['total_budget'][i - 1]
        curr = trends['total_budget'][i]
        if prev > 0:
            growth = ((curr - prev) / prev) * 100
            trends['growth_rates'].append(round(growth, 2))
        else:
            trends['growth_rates'].append(0)

    return trends


def forecast_budget_needs(horizon_years=3):
    """
    Forecast future budget needs based on historical trends.

    Uses simple linear regression on historical data.

    Args:
        horizon_years: Number of years to forecast ahead

    Returns:
        dict: Forecast data with projected budgets
    """
    from monitoring.models import MonitoringEntry
    import statistics

    current_year = timezone.now().year

    # Get historical data (last 5 years)
    historical_years = 5
    start_year = current_year - historical_years

    historical_budgets = []
    for year in range(start_year, current_year + 1):
        total = MonitoringEntry.objects.filter(
            start_date__year=year
        ).aggregate(Sum('budget_allocation'))['budget_allocation__sum'] or 0

        historical_budgets.append(float(total))

    # Simple linear regression
    if len(historical_budgets) >= 3:
        # Calculate average growth rate
        growth_rates = []
        for i in range(1, len(historical_budgets)):
            if historical_budgets[i - 1] > 0:
                rate = ((historical_budgets[i] - historical_budgets[i - 1]) / historical_budgets[i - 1]) * 100
                growth_rates.append(rate)

        avg_growth_rate = statistics.mean(growth_rates) if growth_rates else 5.0
    else:
        avg_growth_rate = 5.0  # Default 5% growth

    # Forecast future years
    forecast = {
        'forecast_years': [],
        'projected_budget': [],
        'confidence_level': 'medium',
        'avg_growth_rate': round(avg_growth_rate, 2),
    }

    last_budget = historical_budgets[-1] if historical_budgets else 1000000

    for year_offset in range(1, horizon_years + 1):
        forecast_year = current_year + year_offset
        projected = last_budget * ((1 + avg_growth_rate / 100) ** year_offset)

        forecast['forecast_years'].append(forecast_year)
        forecast['projected_budget'].append(round(projected, 2))

    # Determine confidence based on data availability
    if len(historical_budgets) >= 5:
        forecast['confidence_level'] = 'high'
    elif len(historical_budgets) >= 3:
        forecast['confidence_level'] = 'medium'
    else:
        forecast['confidence_level'] = 'low'

    return forecast


def analyze_sector_performance():
    """
    Analyze budget allocation and outcomes by sector.

    Returns:
        list: Sector performance metrics
    """
    from monitoring.models import MonitoringEntry

    sectors = MonitoringEntry.objects.values('sector').annotate(
        total_budget=Sum('budget_allocation'),
        ppas_count=Count('id'),
        avg_budget=Avg('budget_allocation'),
        completed=Count('id', filter=Q(status='completed')),
        ongoing=Count('id', filter=Q(status='ongoing')),
        planned=Count('id', filter=Q(status='planned')),
    ).order_by('-total_budget')

    sector_performance = []
    total_budget_all = sum(s['total_budget'] or 0 for s in sectors)

    for sector in sectors:
        if sector['sector']:
            completion_rate = 0
            if sector['ppas_count'] > 0:
                completion_rate = (sector['completed'] / sector['ppas_count']) * 100

            budget_share = 0
            if total_budget_all > 0:
                budget_share = (sector['total_budget'] / total_budget_all) * 100

            sector_performance.append({
                'sector': sector['sector'],
                'total_budget': float(sector['total_budget'] or 0),
                'budget_share': round(budget_share, 2),
                'ppas_count': sector['ppas_count'],
                'avg_budget': float(sector['avg_budget'] or 0),
                'completed': sector['completed'],
                'ongoing': sector['ongoing'],
                'planned': sector['planned'],
                'completion_rate': round(completion_rate, 2),
            })

    return sector_performance


def calculate_impact_metrics():
    """
    Calculate overall impact metrics across all PPAs.

    Returns:
        dict: Aggregated impact metrics
    """
    from monitoring.models import MonitoringEntry
    from mana.models import Need

    total_ppas = MonitoringEntry.objects.count()
    active_ppas = MonitoringEntry.objects.filter(status='ongoing').count()

    total_beneficiaries = MonitoringEntry.objects.aggregate(
        Sum('target_beneficiaries')
    )['target_beneficiaries__sum'] or 0

    total_budget = MonitoringEntry.objects.aggregate(
        Sum('budget_allocation')
    )['budget_allocation__sum'] or 0

    # Needs addressed
    total_needs = Need.objects.count()
    addressed_needs = Need.objects.filter(
        addressing_ppas__isnull=False
    ).distinct().count()

    # Geographic coverage
    covered_municipalities = MonitoringEntry.objects.values(
        'municipality_coverage'
    ).distinct().count()

    covered_provinces = MonitoringEntry.objects.values(
        'province_coverage'
    ).distinct().count()

    # Cost efficiency
    cost_per_beneficiary = 0
    if total_beneficiaries > 0:
        cost_per_beneficiary = total_budget / total_beneficiaries

    # Needs coverage rate
    needs_coverage_rate = 0
    if total_needs > 0:
        needs_coverage_rate = (addressed_needs / total_needs) * 100

    return {
        'total_ppas': total_ppas,
        'active_ppas': active_ppas,
        'total_beneficiaries': int(total_beneficiaries),
        'total_budget': float(total_budget),
        'cost_per_beneficiary': float(cost_per_beneficiary),
        'total_needs': total_needs,
        'addressed_needs': addressed_needs,
        'needs_coverage_rate': round(needs_coverage_rate, 2),
        'covered_municipalities': covered_municipalities,
        'covered_provinces': covered_provinces,
    }


def predict_needs_priority(need_id):
    """
    Predict priority score for a community need based on various factors.

    Args:
        need_id: UUID of the need

    Returns:
        dict: Priority prediction with score and factors
    """
    from mana.models import Need

    try:
        need = Need.objects.get(id=need_id)
    except Need.DoesNotExist:
        return {'error': 'Need not found'}

    # Scoring factors
    score = 0
    factors = []

    # Factor 1: Community votes (0-30 points)
    votes = need.community_votes or 0
    vote_score = min(votes * 2, 30)
    score += vote_score
    factors.append(f"Community support: {votes} votes (+{vote_score})")

    # Factor 2: Urgency level (0-25 points)
    urgency_scores = {
        'critical': 25,
        'high': 20,
        'medium': 15,
        'low': 10,
    }
    urgency_score = urgency_scores.get(need.urgency_level, 10)
    score += urgency_score
    factors.append(f"Urgency: {need.urgency_level} (+{urgency_score})")

    # Factor 3: Geographic reach (0-20 points)
    if need.coverage_level == 'regional':
        reach_score = 20
    elif need.coverage_level == 'provincial':
        reach_score = 15
    elif need.coverage_level == 'municipal':
        reach_score = 10
    else:
        reach_score = 5
    score += reach_score
    factors.append(f"Coverage: {need.coverage_level} (+{reach_score})")

    # Factor 4: Beneficiaries (0-15 points)
    beneficiaries = need.estimated_beneficiaries or 0
    if beneficiaries > 10000:
        ben_score = 15
    elif beneficiaries > 5000:
        ben_score = 12
    elif beneficiaries > 1000:
        ben_score = 9
    elif beneficiaries > 100:
        ben_score = 6
    else:
        ben_score = 3
    score += ben_score
    factors.append(f"Beneficiaries: {beneficiaries:,} (+{ben_score})")

    # Factor 5: Existing solutions (0-10 points)
    addressing_ppas = need.addressing_ppas.count()
    if addressing_ppas == 0:
        solution_score = 10
        factors.append("No existing solutions (+10)")
    elif addressing_ppas == 1:
        solution_score = 5
        factors.append("Partially addressed (+5)")
    else:
        solution_score = 0
        factors.append("Multiple solutions (0)")
    score += solution_score

    # Normalize to 0-100 scale
    max_score = 100
    normalized_score = min(score, max_score)

    # Priority category
    if normalized_score >= 80:
        priority = 'Critical Priority'
    elif normalized_score >= 60:
        priority = 'High Priority'
    elif normalized_score >= 40:
        priority = 'Medium Priority'
    else:
        priority = 'Low Priority'

    return {
        'need_id': str(need_id),
        'need_title': need.need_title,
        'priority_score': normalized_score,
        'priority_category': priority,
        'factors': factors,
    }


def generate_budget_recommendations(total_budget):
    """
    Generate budget allocation recommendations across sectors.

    Args:
        total_budget: Total budget available

    Returns:
        dict: Recommended allocations by sector
    """
    from mana.models import Need
    from decimal import Decimal

    total_budget = Decimal(str(total_budget))

    # Get needs by sector with priority scoring
    needs_by_sector = {}

    for need in Need.objects.filter(status__in=['validated', 'prioritized']):
        sector = need.sector or 'other'
        if sector not in needs_by_sector:
            needs_by_sector[sector] = {
                'needs_count': 0,
                'total_votes': 0,
                'total_beneficiaries': 0,
                'avg_urgency': 0,
            }

        needs_by_sector[sector]['needs_count'] += 1
        needs_by_sector[sector]['total_votes'] += need.community_votes or 0
        needs_by_sector[sector]['total_beneficiaries'] += need.estimated_beneficiaries or 0

    # Calculate allocation weights
    total_weight = sum(
        s['needs_count'] * 2 + s['total_votes'] + (s['total_beneficiaries'] / 1000)
        for s in needs_by_sector.values()
    )

    recommendations = []
    for sector, data in needs_by_sector.items():
        weight = (
            data['needs_count'] * 2 +
            data['total_votes'] +
            (data['total_beneficiaries'] / 1000)
        )

        allocation_percentage = (weight / total_weight * 100) if total_weight > 0 else 0
        recommended_amount = total_budget * Decimal(str(allocation_percentage / 100))

        recommendations.append({
            'sector': sector,
            'recommended_amount': float(recommended_amount),
            'percentage': round(allocation_percentage, 2),
            'needs_count': data['needs_count'],
            'total_votes': data['total_votes'],
            'total_beneficiaries': data['total_beneficiaries'],
            'rationale': f"{data['needs_count']} needs, {data['total_votes']} votes, {data['total_beneficiaries']:,} beneficiaries"
        })

    recommendations.sort(key=lambda x: x['recommended_amount'], reverse=True)

    return {
        'total_budget': float(total_budget),
        'recommendations': recommendations,
    }
