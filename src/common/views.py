from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.utils import timezone
from .models import User, Region
from .forms import UserRegistrationForm, CustomLoginForm

# 5 Standard PPS (Policy, Program, Service) Areas for Recommendations
RECOMMENDATIONS_AREAS = {
    'economic-development': {
        'name': 'Economic Development',
        'categories': ['economic_development'],
        'icon': 'fas fa-chart-line',
        'color': 'green'
    },
    'social-development': {
        'name': 'Social Development', 
        'categories': ['social_development'],
        'icon': 'fas fa-users',
        'color': 'purple'
    },
    'cultural-development': {
        'name': 'Cultural Development',
        'categories': ['cultural_development'],
        'icon': 'fas fa-mosque',
        'color': 'orange'
    },
    'rehabilitation-development': {
        'name': 'Rehabilitation & Development',
        'categories': ['infrastructure', 'environment'],
        'icon': 'fas fa-hammer',
        'color': 'blue'
    },
    'protection-rights': {
        'name': 'Protection of Rights',
        'categories': ['human_rights'],
        'icon': 'fas fa-balance-scale',
        'color': 'red'
    }
}


class CustomLoginView(LoginView):
    """Custom login view with OBC branding and approval check."""
    template_name = 'common/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Check if user is approved before allowing login."""
        user = form.get_user()
        if not user.is_approved and not user.is_superuser:
            messages.error(
                self.request,
                'Your account is pending approval. Please contact the administrator.'
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    next_page = reverse_lazy('common:login')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    """User registration view with approval workflow."""
    model = User
    form_class = UserRegistrationForm
    template_name = 'common/register.html'
    success_url = reverse_lazy('common:login')
    
    def form_valid(self, form):
        """Set user as pending approval after registration."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Registration successful! Your account is pending approval. '
            'You will be notified once your account is approved.'
        )
        return response


@login_required
def dashboard(request):
    """Main dashboard view after login."""
    from communities.models import OBCCommunity, Stakeholder
    from mana.models import Assessment, Need
    from coordination.models import Event, Partnership
    from policy_tracking.models import PolicyRecommendation
    from django.db.models import Count
    
    # Get dashboard statistics
    stats = {
        'communities': {
            'total': OBCCommunity.objects.count(),
            'active': OBCCommunity.objects.filter(is_active=True).count(),
            'by_region': OBCCommunity.objects.values('barangay__municipality__province__region__name').annotate(count=Count('id'))[:5],
            'recent': OBCCommunity.objects.order_by('-created_at')[:5]
        },
        'mana': {
            'total_assessments': Assessment.objects.count(),
            'completed': Assessment.objects.filter(status='completed').count(),
            'in_progress': Assessment.objects.filter(status__in=['data_collection', 'analysis']).count(),
            'high_priority': Need.objects.filter(impact_severity=5).count(),
        },
        'coordination': {
            'total_events': Event.objects.count(),
            'active_partnerships': Partnership.objects.filter(status='active').count(),
            'upcoming_events': Event.objects.filter(start_date__gte=timezone.now().date(), status='planned').count(),
            'pending_actions': 0,  # Will be calculated if ActionItem model exists
            # Partnership breakdown by organization type
            'bmoas': Partnership.objects.filter(
                status='active',
                lead_organization__organization_type='bmoa'
            ).count(),
            'ngas': Partnership.objects.filter(
                status='active',
                lead_organization__organization_type='nga'
            ).count(),
            'lgus': Partnership.objects.filter(
                status='active',
                lead_organization__organization_type='lgu'
            ).count(),
        },
        'policy_tracking': {
            'total_policies': PolicyRecommendation.objects.count(),
            'implemented': PolicyRecommendation.objects.filter(status='implemented').count(),
            'under_review': PolicyRecommendation.objects.filter(status='under_review').count(),
            'high_priority': PolicyRecommendation.objects.filter(priority__in=['high', 'urgent', 'critical']).count(),
            # Recommendations breakdown by category
            'total_recommendations': PolicyRecommendation.objects.count(),
            'policies': PolicyRecommendation.objects.filter(
                category__in=['governance', 'legal_framework', 'administrative']
            ).count(),
            'programs': PolicyRecommendation.objects.filter(
                category__in=['education', 'economic_development', 'social_development', 'cultural_development']
            ).count(),
            'services': PolicyRecommendation.objects.filter(
                category__in=['healthcare', 'infrastructure', 'environment', 'human_rights']
            ).count(),
        }
    }
    
    context = {
        'user': request.user,
        'user_type_display': request.user.get_user_type_display(),
        'is_approved': request.user.is_approved,
        'stats': stats,
    }
    return render(request, 'common/dashboard.html', context)


@login_required
def profile(request):
    """User profile view."""
    context = {
        'user': request.user,
    }
    return render(request, 'common/profile.html', context)


@login_required
def communities_home(request):
    """OBC Communities module home page."""
    from communities.models import OBCCommunity, MunicipalityCoverage, Stakeholder, CommunityInfrastructure
    from django.db.models import Count, Sum, Q, Avg

    # Get community statistics
    communities = OBCCommunity.objects.select_related(
        'barangay__municipality__province__region'
    ).annotate(
        stakeholder_count=Count('stakeholders')
    )

    # Get municipal coverage statistics
    municipal_coverages = MunicipalityCoverage.objects.select_related(
        'municipality__province__region'
    )

    # Calculate total OBC population (avoid double-counting since municipal data is auto-synced from barangay data)
    total_obc_population = communities.aggregate(total=Sum('estimated_obc_population'))['total'] or 0

    # Count of barangay and municipal OBCs
    total_barangay_obcs = communities.count()
    total_municipal_obcs = municipal_coverages.count()

    # Additional demographic statistics
    vulnerable_sectors = communities.aggregate(
        total_women=Sum('women_count'),
        total_pwd=Sum('pwd_count'),
        total_elderly=Sum('elderly_count'),
        total_idps=Sum('idps_count'),
        total_farmers=Sum('farmers_count'),
        total_fisherfolk=Sum('fisherfolk_count'),
        total_teachers_asatidz=Sum('teachers_asatidz_count'),
        total_religious_leaders_ulama=Sum('religious_leaders_ulama_count'),
        total_csos=Sum('csos_count'),
        total_associations=Sum('associations_count')
    )

    # Infrastructure statistics
    infrastructure_stats = CommunityInfrastructure.objects.filter(
        availability_status__in=['limited', 'poor', 'none']
    ).values('infrastructure_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Unemployment rate breakdown
    unemployment_rates = communities.values('unemployment_rate').annotate(
        count=Count('id')
    ).order_by('-count')

    # Ethnolinguistic group distribution
    ethnolinguistic_groups = communities.exclude(
        primary_ethnolinguistic_group__isnull=True
    ).exclude(
        primary_ethnolinguistic_group=''
    ).values('primary_ethnolinguistic_group').annotate(
        count=Count('id')
    ).order_by('-count')

    stats = {
        'communities': {
            'total': communities.count(),
            'active': communities.filter(is_active=True).count(),
            'total_population': communities.aggregate(total=Sum('estimated_obc_population'))['total'] or 0,
            'total_households': communities.aggregate(total=Sum('households'))['total'] or 0,
            'by_region': communities.values(
                'barangay__municipality__province__region__name'
            ).annotate(count=Count('id')).order_by('-count'),
            'recent': communities.order_by('-created_at')[:10],
            'unemployment_rates': unemployment_rates,
            'with_madrasah': communities.filter(has_madrasah=True).count(),
            'with_mosque': communities.filter(has_mosque=True).count(),
            # New statistics for the requested stat cards
            'total_obc_population_database': total_obc_population,
            'total_barangay_obcs_database': total_barangay_obcs,
            'total_municipal_obcs_database': total_municipal_obcs,
        },
        'vulnerable_sectors': vulnerable_sectors,
        'infrastructure_needs': infrastructure_stats,
        'ethnolinguistic_groups': ethnolinguistic_groups,
        'poverty_levels': communities.values('estimated_poverty_incidence').annotate(
            count=Count('id')
        ).exclude(estimated_poverty_incidence='').order_by('estimated_poverty_incidence'),
    }
    
    context = {
        'stats': stats,
        'communities': communities[:20],  # Show first 20 communities
    }
    return render(request, 'common/communities_home.html', context)


@login_required
def mana_home(request):
    """MANA module home page."""
    from mana.models import Assessment, Need, BaselineStudy
    from django.db.models import Count, Q
    
    # Get MANA statistics
    assessments = Assessment.objects.select_related('community', 'category')
    needs = Need.objects.select_related('category', 'assessment')
    baseline_studies = BaselineStudy.objects.select_related('community')
    
    # Calculate assessment metrics
    total_assessments = assessments.count()
    completed_assessments = assessments.filter(status='completed').count()
    in_progress_assessments = assessments.filter(status__in=['data_collection', 'analysis']).count()
    planned_assessments = assessments.filter(status__in=['planning', 'preparation']).count()
    
    # Calculate assessments by area/category (based on category name containing keywords)
    education_assessments = assessments.filter(
        Q(category__name__icontains='education') | Q(category__category_type__icontains='education')
    ).count()
    economic_assessments = assessments.filter(
        Q(category__name__icontains='economic') | Q(category__category_type__icontains='economic')
    ).count()
    social_assessments = assessments.filter(
        Q(category__name__icontains='social') | Q(category__category_type__icontains='social')
    ).count()
    cultural_assessments = assessments.filter(
        Q(category__name__icontains='cultural') | Q(category__category_type__icontains='cultural')
    ).count()
    infrastructure_assessments = assessments.filter(
        Q(category__name__icontains='infrastructure') | Q(category__category_type__icontains='infrastructure')
    ).count()
    
    stats = {
        'mana': {
            'total_assessments': total_assessments,
            'completed': completed_assessments,
            'in_progress': in_progress_assessments,
            'planned': planned_assessments,
            'by_area': {
                'education': education_assessments,
                'economic': economic_assessments,
                'social': social_assessments,
                'cultural': cultural_assessments,
                'infrastructure': infrastructure_assessments,
            }
        },
        'assessments': {
            'total': total_assessments,
            'completed': completed_assessments,
            'ongoing': in_progress_assessments,
            'by_status': assessments.values('status').annotate(count=Count('id')),
            'recent': assessments.order_by('-created_at')[:10]
        },
        'needs': {
            'total': needs.count(),
            'critical': needs.filter(urgency_level='immediate').count(),
            'by_category': needs.values('category__name').annotate(count=Count('id'))[:10],
            'recent': needs.order_by('-created_at')[:10]
        },
        'baseline_studies': {
            'total': baseline_studies.count(),
            'completed': baseline_studies.filter(status='completed').count(),
            'ongoing': baseline_studies.filter(status__in=['data_collection', 'analysis']).count(),
        }
    }
    
    context = {
        'stats': stats,
    }
    return render(request, 'common/mana_home.html', context)


@login_required
def coordination_home(request):
    """Coordination module home page - Coordination with BMOAs, NGAs, and LGUs."""
    from coordination.models import Event, Partnership, Organization, StakeholderEngagement, PartnershipSignatory, EventParticipant
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get coordination statistics for BMOAs, NGAs, and LGUs
    now = timezone.now()
    
    # 1. Mapped Partners (Organizations that have been registered and researched)
    # Organizations that are active and have description/mandate information (indicating research)
    mapped_partners = Organization.objects.filter(
        is_active=True,
        organization_type__in=['bmoa', 'nga', 'lgu']
    ).exclude(description='')
    
    mapped_partners_stats = {
        'total': mapped_partners.count(),
        'bmoa': mapped_partners.filter(organization_type='bmoa').count(),
        'nga': mapped_partners.filter(organization_type='nga').count(), 
        'lgu': mapped_partners.filter(organization_type='lgu').count(),
    }
    
    # 2. Active Partnerships
    active_partnerships = Partnership.objects.filter(status='active')
    
    # Count partnerships by organization type involved through signatories
    bmoa_partnerships = active_partnerships.filter(
        signatories__organization__organization_type='bmoa'
    ).distinct().count()
    nga_partnerships = active_partnerships.filter(
        signatories__organization__organization_type='nga'
    ).distinct().count()
    lgu_partnerships = active_partnerships.filter(
        signatories__organization__organization_type='lgu'
    ).distinct().count()
    
    active_partnerships_stats = {
        'total': active_partnerships.count(),
        'bmoa': bmoa_partnerships,
        'nga': nga_partnerships,
        'lgu': lgu_partnerships,
    }
    
    # 3. Coordination Activities Done (Completed events and engagements)
    completed_events = Event.objects.filter(status='completed')
    completed_engagements = StakeholderEngagement.objects.filter(status='completed')
    
    total_completed_activities = completed_events.count() + completed_engagements.count()
    
    # Count by organization type for events through participants
    bmoa_events = completed_events.filter(
        participants__organization__organization_type='bmoa'
    ).distinct().count()
    nga_events = completed_events.filter(
        participants__organization__organization_type='nga'
    ).distinct().count()
    lgu_events = completed_events.filter(
        participants__organization__organization_type='lgu'
    ).distinct().count()
    
    coordination_activities_done_stats = {
        'total': total_completed_activities,
        'bmoa': bmoa_events,
        'nga': nga_events, 
        'lgu': lgu_events,
    }
    
    # 4. Planned Coordination Activities (Upcoming events and planned engagements)
    planned_events = Event.objects.filter(
        status__in=['planned', 'scheduled'],
        start_date__gte=now.date()
    )
    
    planned_engagements = StakeholderEngagement.objects.filter(
        status__in=['planned', 'scheduled'],
        planned_date__gte=now
    )
    
    total_planned_activities = planned_events.count() + planned_engagements.count()
    
    # Count by organization type for planned events through participants
    bmoa_planned = planned_events.filter(
        participants__organization__organization_type='bmoa'
    ).distinct().count()
    nga_planned = planned_events.filter(
        participants__organization__organization_type='nga'
    ).distinct().count()
    lgu_planned = planned_events.filter(
        participants__organization__organization_type='lgu'
    ).distinct().count()
    
    planned_coordination_activities_stats = {
        'total': total_planned_activities,
        'bmoa': bmoa_planned,
        'nga': nga_planned,
        'lgu': lgu_planned,
    }
    
    # Recent activities for display
    recent_events = Event.objects.filter(
        start_date__gte=now.date() - timedelta(days=30)
    ).order_by('-start_date')[:5]
    
    # Event categories breakdown (for Event Categories section)
    event_by_type = {
        'meeting': Event.objects.filter(event_type='meeting').count(),
        'workshop': Event.objects.filter(event_type='workshop').count(),
        'conference': Event.objects.filter(event_type='conference').count(),
        'consultation': Event.objects.filter(event_type='consultation').count(),
    }
    
    # Active partnerships list for display
    active_partnerships_list = Partnership.objects.filter(
        status='active'
    ).order_by('-created_at')[:5]
    
    stats = {
        'mapped_partners': mapped_partners_stats,
        'active_partnerships': active_partnerships_stats,
        'coordination_activities_done': coordination_activities_done_stats,
        'planned_coordination_activities': planned_coordination_activities_stats,
        'recent_events': recent_events,
        'coordination': {
            'active_partnerships': active_partnerships_list,
            'by_type': event_by_type,
        }
    }
    
    context = {
        'stats': stats,
    }
    return render(request, 'common/coordination_home.html', context)


@login_required
def recommendations_home(request):
    """Recommendations Tracking module home page."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count, Q
    
    # Get recommendations tracking statistics
    recommendations = PolicyRecommendation.objects.select_related('proposed_by', 'lead_author')
    evidence = PolicyEvidence.objects.select_related('policy')
    
    # Define recommendation types
    policy_categories = ['governance', 'legal_framework', 'administrative']
    program_categories = ['education', 'economic_development', 'social_development', 'cultural_development']
    service_categories = ['healthcare', 'infrastructure', 'environment', 'human_rights']
    
    # Define status mappings
    submitted_statuses = ['submitted', 'under_consideration', 'approved', 'in_implementation', 'implemented']
    proposed_statuses = ['draft', 'under_review', 'needs_revision']
    
    # Calculate main metrics
    total_recommendations = recommendations.count()
    total_implemented = recommendations.filter(status='implemented').count()
    total_submitted = recommendations.filter(status__in=submitted_statuses).count()
    total_proposed = recommendations.filter(status__in=proposed_statuses).count()
    
    # Calculate breakdown by type
    policies_total = recommendations.filter(category__in=policy_categories).count()
    programs_total = recommendations.filter(category__in=program_categories).count()
    services_total = recommendations.filter(category__in=service_categories).count()
    
    # Implemented breakdown
    implemented_policies = recommendations.filter(status='implemented', category__in=policy_categories).count()
    implemented_programs = recommendations.filter(status='implemented', category__in=program_categories).count()
    implemented_services = recommendations.filter(status='implemented', category__in=service_categories).count()
    
    # Submitted breakdown
    submitted_policies = recommendations.filter(status__in=submitted_statuses, category__in=policy_categories).count()
    submitted_programs = recommendations.filter(status__in=submitted_statuses, category__in=program_categories).count()
    submitted_services = recommendations.filter(status__in=submitted_statuses, category__in=service_categories).count()
    
    # Proposed breakdown
    proposed_policies = recommendations.filter(status__in=proposed_statuses, category__in=policy_categories).count()
    proposed_programs = recommendations.filter(status__in=proposed_statuses, category__in=program_categories).count()
    proposed_services = recommendations.filter(status__in=proposed_statuses, category__in=service_categories).count()
    
    # Area breakdowns using the 5 standard areas
    economic_development = recommendations.filter(category='economic_development').count()
    social_development = recommendations.filter(category='social_development').count()
    cultural_development = recommendations.filter(category='cultural_development').count()
    rehabilitation_development = recommendations.filter(category__in=['infrastructure', 'environment']).count()
    protection_rights = recommendations.filter(category='human_rights').count()
    
    stats = {
        'recommendations': {
            'total': total_recommendations,
            'implemented': total_implemented,
            'submitted': total_submitted,
            'proposed': total_proposed,
            'policies': policies_total,
            'programs': programs_total,
            'services': services_total,
            'implemented_policies': implemented_policies,
            'implemented_programs': implemented_programs,
            'implemented_services': implemented_services,
            'submitted_policies': submitted_policies,
            'submitted_programs': submitted_programs,
            'submitted_services': submitted_services,
            'proposed_policies': proposed_policies,
            'proposed_programs': proposed_programs,
            'proposed_services': proposed_services,
        },
        'areas': {
            'economic_development': economic_development,
            'social_development': social_development,
            'cultural_development': cultural_development,
            'rehabilitation_development': rehabilitation_development,
            'protection_rights': protection_rights,
        },
        'recommendations_tracking': {
            'recent_recommendations': recommendations.order_by('-created_at')[:5],
            'recent_evidence': evidence.order_by('-date_added')[:5],
        },
        'areas_data': RECOMMENDATIONS_AREAS,
    }
    
    context = {
        'stats': stats,
    }
    return render(request, 'common/recommendations_home.html', context)


@login_required
def communities_add(request):
    """Add new community page."""
    from communities.models import OBCCommunity
    from common.models import Barangay
    from .forms import OBCCommunityForm
    
    if request.method == 'POST':
        form = OBCCommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            # Set any additional fields if needed
            community.save()
            messages.success(request, f'Community "{community.barangay.name}" has been successfully added.')
            return redirect('common:communities_manage')
    else:
        form = OBCCommunityForm()
    
    # Get recent communities for reference
    recent_communities = OBCCommunity.objects.order_by('-created_at')[:5]
    barangays = Barangay.objects.select_related(
        'municipality__province__region'
    ).order_by('municipality__province__region__name', 'municipality__name', 'name')
    
    context = {
        'form': form,
        'recent_communities': recent_communities,
        'barangays': barangays,
    }
    return render(request, 'common/communities_add.html', context)


def _render_manage_obc(request, scope='barangay'):
    """Shared renderer for managing OBC records at different administrative levels."""
    from communities.models import OBCCommunity
    from django.db.models import Count, Sum
    from django.db.models import Q

    # Base queryset for communities with related data
    communities = OBCCommunity.objects.select_related(
        'barangay__municipality__province__region'
    ).annotate(
        stakeholder_count=Count('stakeholders')
    ).order_by('barangay__name')

    # Filters
    region_filter = request.GET.get('region')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    if region_filter:
        communities = communities.filter(
            barangay__municipality__province__region__id=region_filter
        )

    if status_filter:
        if status_filter == 'active':
            communities = communities.filter(is_active=True)
        elif status_filter == 'inactive':
            communities = communities.filter(is_active=False)

    if search_query:
        communities = communities.filter(
            Q(barangay__name__icontains=search_query) |
            Q(barangay__municipality__name__icontains=search_query) |
            Q(barangay__municipality__province__name__icontains=search_query) |
            Q(barangay__municipality__province__region__name__icontains=search_query)
        )

    total_communities = communities.count()
    total_obc_population = communities.aggregate(
        total=Sum('estimated_obc_population')
    )['total'] or 0
    municipality_ids = set(
        communities.values_list('barangay__municipality_id', flat=True)
    )
    total_municipalities = len(municipality_ids)

    # Municipal-level synchronization breakdown based on assessment activity
    manual_municipality_ids = set(
        communities.filter(needs_assessment_date__isnull=False).values_list(
            'barangay__municipality_id', flat=True
        )
    )
    manual_municipalities = len(manual_municipality_ids)
    auto_synced_municipalities = max(total_municipalities - manual_municipalities, 0)

    if scope == 'municipal':
        page_title = 'Manage Municipal OBCs'
        page_description = (
            'Monitor municipal-level OBC records and synchronization status.'
        )
        stat_cards = [
            {
                'title': 'Total Municipal OBCs in the Database',
                'value': total_municipalities,
                'icon': 'fas fa-city',
                'gradient': 'from-blue-500 via-blue-600 to-blue-700',
                'text_color': 'text-blue-100',
            },
            {
                'title': 'Total OBC Population from the Municipalities',
                'value': total_obc_population,
                'icon': 'fas fa-users',
                'gradient': 'from-emerald-500 via-emerald-600 to-emerald-700',
                'text_color': 'text-emerald-100',
            },
            {
                'title': 'Auto-Synced Municipalities',
                'value': auto_synced_municipalities,
                'icon': 'fas fa-sync-alt',
                'gradient': 'from-purple-500 via-purple-600 to-purple-700',
                'text_color': 'text-purple-100',
            },
            {
                'title': 'Manually Updated Municipalities',
                'value': manual_municipalities,
                'icon': 'fas fa-edit',
                'gradient': 'from-orange-500 via-orange-600 to-orange-700',
                'text_color': 'text-orange-100',
            },
        ]
    else:
        page_title = 'Manage Barangay OBCs'
        page_description = (
            'View, edit, and manage all registered barangay-level OBC communities.'
        )
        stat_cards = [
            {
                'title': 'Total Barangay OBCs in the Database',
                'value': total_communities,
                'icon': 'fas fa-users',
                'gradient': 'from-blue-500 via-blue-600 to-blue-700',
                'text_color': 'text-blue-100',
            },
            {
                'title': 'Total OBC Population from Barangays',
                'value': total_obc_population,
                'icon': 'fas fa-user-friends',
                'gradient': 'from-emerald-500 via-emerald-600 to-emerald-700',
                'text_color': 'text-emerald-100',
            },
            {
                'title': 'Total Municipalities OBCs in the Database',
                'value': total_municipalities,
                'icon': 'fas fa-city',
                'gradient': 'from-purple-500 via-purple-600 to-purple-700',
                'text_color': 'text-purple-100',
            },
        ]

    lg_columns = 4 if len(stat_cards) >= 4 else 3
    stat_cards_grid_class = (
        f"mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-{lg_columns} gap-6"
    )

    regions = Region.objects.all().order_by('name')

    context = {
        'communities': communities,
        'regions': regions,
        'current_region': region_filter,
        'current_status': status_filter,
        'search_query': search_query,
        'total_communities': total_communities,
        'total_population': total_obc_population,
        'total_municipalities': total_municipalities,
        'stat_cards': stat_cards,
        'stat_cards_grid_class': stat_cards_grid_class,
        'page_title': page_title,
        'page_description': page_description,
        'view_scope': scope,
    }
    return render(request, 'common/communities_manage.html', context)


@login_required
def communities_manage(request):
    """Manage communities page (barangay scope by default)."""
    return _render_manage_obc(request, scope='barangay')


@login_required
def communities_manage_barangay_obc(request):
    """Explicit barangay-level management view."""
    return _render_manage_obc(request, scope='barangay')


@login_required
def communities_manage_municipal_obc(request):
    """Municipal-level OBC management view."""
    return _render_manage_obc(request, scope='municipal')


@login_required
def communities_stakeholders(request):
    """Manage stakeholders page."""
    from communities.models import Stakeholder, OBCCommunity
    from django.db.models import Count
    
    # Get all stakeholders with related data
    stakeholders = Stakeholder.objects.select_related(
        'community', 'community__barangay__municipality__province__region'
    ).prefetch_related('engagements')
    
    # Filter functionality
    community_filter = request.GET.get('community')
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    
    if community_filter:
        stakeholders = stakeholders.filter(community__id=community_filter)
    
    if type_filter:
        stakeholders = stakeholders.filter(stakeholder_type=type_filter)
    
    if status_filter:
        if status_filter == 'active':
            stakeholders = stakeholders.filter(is_active=True)
        elif status_filter == 'verified':
            stakeholders = stakeholders.filter(is_verified=True)
    
    # Get filter options
    communities = OBCCommunity.objects.order_by('barangay__name')
    stakeholder_types = Stakeholder.STAKEHOLDER_TYPES
    
    # Statistics
    stats = {
        'total_stakeholders': stakeholders.count(),
        'active_stakeholders': stakeholders.filter(is_active=True).count(),
        'verified_stakeholders': stakeholders.filter(is_verified=True).count(),
        'by_type': stakeholders.values('stakeholder_type').annotate(count=Count('id')),
    }
    
    context = {
        'stakeholders': stakeholders.order_by('full_name'),
        'communities': communities,
        'stakeholder_types': stakeholder_types,
        'current_community': community_filter,
        'current_type': type_filter,
        'current_status': status_filter,
        'stats': stats,
    }
    return render(request, 'common/communities_stakeholders.html', context)


@login_required
def mana_new_assessment(request):
    """New MANA assessment page."""
    from mana.models import Assessment, NeedsCategory
    from communities.models import OBCCommunity
    
    # Get recent assessments for reference
    recent_assessments = Assessment.objects.order_by('-created_at')[:5]
    communities = OBCCommunity.objects.filter(is_active=True).order_by('barangay__name')
    categories = NeedsCategory.objects.all().order_by('name')
    
    context = {
        'recent_assessments': recent_assessments,
        'communities': communities,
        'categories': categories,
    }
    return render(request, 'common/mana_new_assessment.html', context)


@login_required
def mana_manage_assessments(request):
    """Manage MANA assessments page."""
    from mana.models import Assessment, Need
    from django.db.models import Count
    
    # Get all assessments with related data
    assessments = Assessment.objects.select_related(
        'community', 'category', 'lead_assessor'
    ).annotate(
        needs_count=Count('identified_needs')
    ).order_by('-created_at')
    
    # Filter functionality
    status_filter = request.GET.get('status')
    community_filter = request.GET.get('community')
    
    if status_filter:
        assessments = assessments.filter(status=status_filter)
    
    if community_filter:
        assessments = assessments.filter(community__id=community_filter)
    
    # Get filter options
    from communities.models import OBCCommunity
    communities = OBCCommunity.objects.order_by('barangay__name')
    status_choices = Assessment.STATUS_CHOICES if hasattr(Assessment, 'STATUS_CHOICES') else []
    
    # Statistics
    stats = {
        'total_assessments': assessments.count(),
        'completed': assessments.filter(status='completed').count(),
        'in_progress': assessments.filter(status__in=['data_collection', 'analysis']).count(),
        'pending': assessments.filter(status='pending').count(),
    }
    
    context = {
        'assessments': assessments,
        'communities': communities,
        'status_choices': status_choices,
        'current_status': status_filter,
        'current_community': community_filter,
        'stats': stats,
    }
    return render(request, 'common/mana_manage_assessments.html', context)


@login_required
def mana_geographic_data(request):
    """Delegate to domain-specific MANA geographic data view."""
    from .mana import mana_geographic_data as module_mana_geographic_data

    return module_mana_geographic_data(request)


@login_required
def coordination_organizations(request):
    """Manage coordination organizations page."""
    from coordination.models import Organization, OrganizationContact
    from django.db.models import Count
    
    # Get all organizations with related data
    organizations = Organization.objects.annotate(
        contacts_count=Count('contacts'),
        partnerships_count=Count('led_partnerships')
    ).order_by('name')
    
    # Filter functionality
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    
    if type_filter:
        organizations = organizations.filter(organization_type=type_filter)
    
    if status_filter == 'active':
        organizations = organizations.filter(is_active=True)
    elif status_filter == 'inactive':
        organizations = organizations.filter(is_active=False)
    
    # Get filter options
    org_types = Organization.ORGANIZATION_TYPE_CHOICES if hasattr(Organization, 'ORGANIZATION_TYPE_CHOICES') else []
    
    # Statistics
    stats = {
        'total_organizations': organizations.count(),
        'active_organizations': organizations.filter(is_active=True).count(),
        'total_contacts': OrganizationContact.objects.count(),
        'by_type': organizations.values('organization_type').annotate(count=Count('id')),
    }
    
    context = {
        'organizations': organizations,
        'org_types': org_types,
        'current_type': type_filter,
        'current_status': status_filter,
        'stats': stats,
    }
    return render(request, 'common/coordination_organizations.html', context)


@login_required
def coordination_partnerships(request):
    """Manage coordination partnerships page."""
    from coordination.models import Partnership, Organization
    from django.db.models import Count
    
    # Get all partnerships with related data
    partnerships = Partnership.objects.select_related(
        'lead_organization'
    ).annotate(
        signatories_count=Count('signatories')
    ).order_by('-created_at')
    
    # Filter functionality
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    
    if status_filter:
        partnerships = partnerships.filter(status=status_filter)
    
    if type_filter:
        partnerships = partnerships.filter(partnership_type=type_filter)
    
    # Get filter options
    status_choices = Partnership.STATUS_CHOICES if hasattr(Partnership, 'STATUS_CHOICES') else []
    type_choices = Partnership.PARTNERSHIP_TYPE_CHOICES if hasattr(Partnership, 'PARTNERSHIP_TYPE_CHOICES') else []
    
    # Statistics
    stats = {
        'total_partnerships': partnerships.count(),
        'active_partnerships': partnerships.filter(status='active').count(),
        'pending_partnerships': partnerships.filter(status='pending').count(),
        'by_type': partnerships.values('partnership_type').annotate(count=Count('id')),
    }
    
    context = {
        'partnerships': partnerships,
        'status_choices': status_choices,
        'type_choices': type_choices,
        'current_status': status_filter,
        'current_type': type_filter,
        'stats': stats,
    }
    return render(request, 'common/coordination_partnerships.html', context)


@login_required
def coordination_events(request):
    """Manage coordination events page."""
    from coordination.models import Event, EventParticipant
    from django.db.models import Count
    from django.utils import timezone
    
    # Get all events with related data
    events = Event.objects.select_related(
        'community', 'organizer'
    ).annotate(
        participants_count=Count('participants')
    ).order_by('-start_date')
    
    # Filter functionality
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    
    if status_filter:
        events = events.filter(status=status_filter)
    
    if type_filter:
        events = events.filter(event_type=type_filter)
    
    # Get filter options
    status_choices = Event.STATUS_CHOICES if hasattr(Event, 'STATUS_CHOICES') else []
    type_choices = Event.EVENT_TYPE_CHOICES if hasattr(Event, 'EVENT_TYPE_CHOICES') else []
    
    # Separate upcoming and past events
    now = timezone.now().date()
    upcoming_events = events.filter(start_date__gte=now)
    past_events = events.filter(start_date__lt=now)
    
    # Statistics
    stats = {
        'total_events': events.count(),
        'upcoming_events': upcoming_events.count(),
        'past_events': past_events.count(),
        'total_participants': EventParticipant.objects.count(),
    }
    
    context = {
        'events': events,
        'upcoming_events': upcoming_events[:10],
        'past_events': past_events[:10],
        'status_choices': status_choices,
        'type_choices': type_choices,
        'current_status': status_filter,
        'current_type': type_filter,
        'stats': stats,
    }
    return render(request, 'common/coordination_events.html', context)


@login_required
def coordination_view_all(request):
    """Coordination overview and reports page."""
    from coordination.models import Event, Partnership, Organization
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Get comprehensive coordination data
    events = Event.objects.select_related('community', 'organizer')
    partnerships = Partnership.objects.select_related('lead_organization')
    organizations = Organization.objects.filter(is_active=True)
    
    # Time-based statistics
    now = timezone.now()
    last_30_days = now.date() - timedelta(days=30)
    
    # Comprehensive statistics
    stats = {
        'organizations': {
            'total': organizations.count(),
            'by_type': organizations.values('organization_type').annotate(count=Count('id'))[:5],
        },
        'partnerships': {
            'total': partnerships.count(),
            'active': partnerships.filter(status='active').count(),
            'recent': partnerships.filter(created_at__gte=last_30_days).count(),
            'by_status': partnerships.values('status').annotate(count=Count('id')),
        },
        'events': {
            'total': events.count(),
            'upcoming': events.filter(start_date__gte=now.date()).count(),
            'recent': events.filter(start_date__gte=last_30_days).count(),
            'by_type': events.values('event_type').annotate(count=Count('id'))[:5],
        }
    }
    
    # Recent activity
    recent_events = events.order_by('-created_at')[:5]
    recent_partnerships = partnerships.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_events': recent_events,
        'recent_partnerships': recent_partnerships,
        'organizations': organizations[:10],
    }
    return render(request, 'common/coordination_view_all.html', context)


@login_required
def recommendations_new(request):
    """Create new recommendation page."""
    from policy_tracking.models import PolicyRecommendation
    
    # Get recent recommendations for reference
    recent_recommendations = PolicyRecommendation.objects.order_by('-created_at')[:5]
    
    context = {
        'recent_recommendations': recent_recommendations,
        'areas_data': RECOMMENDATIONS_AREAS,
    }
    return render(request, 'common/recommendations_new.html', context)


@login_required
def recommendations_manage(request):
    """Manage recommendations page."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count
    
    # Get all recommendations with related data
    recommendations = PolicyRecommendation.objects.select_related(
        'proposed_by', 'lead_author', 'assigned_reviewer'
    ).annotate(
        evidence_count=Count('evidence')
    ).order_by('-created_at')
    
    # Filter functionality
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    area_filter = request.GET.get('area')
    
    if status_filter:
        recommendations = recommendations.filter(status=status_filter)
    
    if category_filter:
        recommendations = recommendations.filter(category=category_filter)
        
    if area_filter and area_filter in RECOMMENDATIONS_AREAS:
        area_categories = RECOMMENDATIONS_AREAS[area_filter]['categories']
        recommendations = recommendations.filter(category__in=area_categories)
    
    # Get filter options
    status_choices = PolicyRecommendation.STATUS_CHOICES if hasattr(PolicyRecommendation, 'STATUS_CHOICES') else []
    category_choices = PolicyRecommendation.CATEGORY_CHOICES if hasattr(PolicyRecommendation, 'CATEGORY_CHOICES') else []
    
    # Statistics
    stats = {
        'total_recommendations': recommendations.count(),
        'implemented': recommendations.filter(status='implemented').count(),
        'under_review': recommendations.filter(status='under_review').count(),
        'approved': recommendations.filter(status='approved').count(),
    }
    
    context = {
        'recommendations': recommendations,
        'status_choices': status_choices,
        'category_choices': category_choices,
        'current_status': status_filter,
        'current_category': category_filter,
        'current_area': area_filter,
        'stats': stats,
        'areas_data': RECOMMENDATIONS_AREAS,
    }
    return render(request, 'common/recommendations_manage.html', context)


@login_required
def recommendations_by_area(request, area_slug):
    """View recommendations filtered by specific area."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count, Q
    from django.http import Http404
    
    # Validate area slug
    if area_slug not in RECOMMENDATIONS_AREAS:
        raise Http404("Area not found")
    
    area_info = RECOMMENDATIONS_AREAS[area_slug]
    area_categories = area_info['categories']
    
    # Get recommendations for this area
    recommendations = PolicyRecommendation.objects.filter(
        category__in=area_categories
    ).select_related('proposed_by', 'lead_author').annotate(
        evidence_count=Count('evidence')
    )
    
    # Define status mappings
    submitted_statuses = ['submitted', 'under_consideration', 'approved', 'in_implementation', 'implemented']
    proposed_statuses = ['draft', 'under_review', 'needs_revision']
    
    # Calculate area-specific metrics
    total_area_recommendations = recommendations.count()
    implemented_area = recommendations.filter(status='implemented').count()
    submitted_area = recommendations.filter(status__in=submitted_statuses).count()
    proposed_area = recommendations.filter(status__in=proposed_statuses).count()
    
    # Get filter parameter
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'proposed':
            recommendations = recommendations.filter(status__in=proposed_statuses)
        elif status_filter == 'submitted':
            recommendations = recommendations.filter(status__in=submitted_statuses)
        elif status_filter == 'implemented':
            recommendations = recommendations.filter(status='implemented')
    
    # Recent recommendations for this area
    recent_recommendations = recommendations.order_by('-created_at')[:10]
    
    stats = {
        'area_info': area_info,
        'total': total_area_recommendations,
        'implemented': implemented_area,
        'submitted': submitted_area,
        'proposed': proposed_area,
        'current_filter': status_filter,
    }
    
    context = {
        'area_slug': area_slug,
        'area_info': area_info,
        'stats': stats,
        'recommendations': recent_recommendations,
        'current_filter': status_filter,
    }
    return render(request, 'common/recommendations_by_area.html', context)
