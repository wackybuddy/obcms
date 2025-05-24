from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.utils import timezone
from .models import User
from .forms import UserRegistrationForm, CustomLoginForm


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
        },
        'policy_tracking': {
            'total_policies': PolicyRecommendation.objects.count(),
            'implemented': PolicyRecommendation.objects.filter(status='implemented').count(),
            'under_review': PolicyRecommendation.objects.filter(status='under_review').count(),
            'high_priority': PolicyRecommendation.objects.filter(priority__in=['high', 'urgent', 'critical']).count(),
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
    from communities.models import OBCCommunity, Stakeholder, CommunityInfrastructure
    from django.db.models import Count, Sum, Q, Avg
    
    # Get community statistics
    communities = OBCCommunity.objects.select_related(
        'barangay__municipality__province__region'
    ).annotate(
        stakeholder_count=Count('stakeholders')
    )
    
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
    
    # Development status breakdown
    development_status = communities.values('development_status').annotate(
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
            'development_status': development_status,
            'with_madrasah': communities.filter(has_madrasah=True).count(),
            'with_mosque': communities.filter(has_mosque=True).count(),
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
    from django.db.models import Count
    
    # Get MANA statistics
    assessments = Assessment.objects.select_related('community', 'category')
    needs = Need.objects.select_related('category', 'assessment')
    baseline_studies = BaselineStudy.objects.select_related('community')
    
    stats = {
        'assessments': {
            'total': assessments.count(),
            'completed': assessments.filter(status='completed').count(),
            'ongoing': assessments.filter(status__in=['data_collection', 'analysis']).count(),
            'by_status': assessments.values('status').annotate(count=Count('id')),
            'recent': assessments.order_by('-created_at')[:10]
        },
        'needs': {
            'total': needs.count(),
            'high_priority': needs.filter(impact_severity=5).count(),
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
    """Coordination module home page."""
    from coordination.models import Event, Partnership, Organization
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Get coordination statistics
    events = Event.objects.select_related('community', 'organizer')
    partnerships = Partnership.objects.select_related('lead_organization')
    organizations = Organization.objects.filter(is_active=True)
    
    # Recent and upcoming events
    now = timezone.now()
    recent_events = events.filter(start_date__gte=now.date() - timedelta(days=30))
    upcoming_events = events.filter(start_date__gte=now.date(), status='planned')
    
    stats = {
        'events': {
            'total': events.count(),
            'recent': recent_events.count(),
            'upcoming': upcoming_events.count(),
            'by_type': events.values('event_type').annotate(count=Count('id'))[:10],
            'upcoming_list': upcoming_events.order_by('start_date')[:10]
        },
        'partnerships': {
            'total': partnerships.count(),
            'active': partnerships.filter(status='active').count(),
            'by_type': partnerships.values('partnership_type').annotate(count=Count('id')),
            'by_status': partnerships.values('status').annotate(count=Count('id'))
        },
        'organizations': {
            'total': organizations.count(),
            'by_type': organizations.values('organization_type').annotate(count=Count('id'))
        }
    }
    
    context = {
        'stats': stats,
    }
    return render(request, 'common/coordination_home.html', context)


@login_required
def policy_tracking_home(request):
    """Policy Tracking module home page."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count
    
    # Get policy tracking statistics
    recommendations = PolicyRecommendation.objects.select_related('submitted_by', 'reviewed_by')
    evidence = PolicyEvidence.objects.select_related('recommendation')
    
    stats = {
        'recommendations': {
            'total': recommendations.count(),
            'implemented': recommendations.filter(status='implemented').count(),
            'under_review': recommendations.filter(status='under_review').count(),
            'approved': recommendations.filter(status='approved').count(),
            'by_category': recommendations.values('category').annotate(count=Count('id'))[:10],
            'by_status': recommendations.values('status').annotate(count=Count('id')),
            'recent': recommendations.order_by('-created_at')[:10]
        },
        'evidence': {
            'total': evidence.count(),
            'verified': evidence.filter(verified=True).count(),
            'by_type': evidence.values('evidence_type').annotate(count=Count('id'))[:10]
        }
    }
    
    context = {
        'stats': stats,
    }
    return render(request, 'common/policy_tracking_home.html', context)


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


@login_required
def communities_manage(request):
    """Manage communities page."""
    from communities.models import OBCCommunity
    from django.db.models import Count, Sum
    from django.db.models import Q # Import Q for complex lookups
    
    # Get all communities with related data
    communities = OBCCommunity.objects.select_related(
        'barangay__municipality__province__region'
    ).annotate(
        stakeholder_count=Count('stakeholders')
    ).order_by('barangay__name')
    
    # Filter functionality
    region_filter = request.GET.get('region')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search') # Get the search query
    
    if region_filter:
        communities = communities.filter(
            barangay__municipality__province__region__id=region_filter
        )
    
    if status_filter:
        if status_filter == 'active':
            communities = communities.filter(is_active=True)
        elif status_filter == 'inactive':
            communities = communities.filter(is_active=False)
            
    if search_query: # Apply search filter
        communities = communities.filter(
            Q(barangay__name__icontains=search_query) |
            Q(barangay__municipality__name__icontains=search_query) |
            Q(barangay__municipality__province__name__icontains=search_query) |
            Q(barangay__municipality__province__region__name__icontains=search_query)
        )
    
    # Get filter options
    from common.models import Region
    regions = Region.objects.all().order_by('name')
    
    context = {
        'communities': communities,
        'regions': regions,
        'current_region': region_filter,
        'current_status': status_filter,
        'search_query': search_query, # Add search_query to context
        'total_communities': communities.count(),
        'total_population': communities.aggregate(total=Sum('total_barangay_population'))['total'] or 0,
    }
    return render(request, 'common/communities_manage.html', context)


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
    """MANA geographic data and mapping page."""
    from mana.models import GeographicDataLayer, MapVisualization
    from communities.models import OBCCommunity
    from django.db.models import Count
    
    # Get geographic data layers and visualizations
    data_layers = GeographicDataLayer.objects.all().order_by('name')
    visualizations = MapVisualization.objects.select_related(
        'community'
    ).order_by('-created_at')[:10]
    
    # Get communities with geographic data
    communities = OBCCommunity.objects.annotate(
        visualizations_count=Count('map_visualizations')
    ).filter(visualizations_count__gt=0)
    
    # Statistics
    stats = {
        'total_layers': data_layers.count(),
        'total_visualizations': visualizations.count(),
        'communities_mapped': communities.count(),
        'active_layers': data_layers.filter(is_active=True).count() if hasattr(GeographicDataLayer, 'is_active') else data_layers.count(),
    }
    
    context = {
        'data_layers': data_layers,
        'visualizations': visualizations,
        'communities': communities,
        'stats': stats,
    }
    return render(request, 'common/mana_geographic_data.html', context)


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
def policy_tracking_new_policy(request):
    """Create new policy recommendation page."""
    from policy_tracking.models import PolicyRecommendation
    
    # Get recent policies for reference
    recent_policies = PolicyRecommendation.objects.order_by('-created_at')[:5]
    
    context = {
        'recent_policies': recent_policies,
    }
    return render(request, 'common/policy_tracking_new_policy.html', context)


@login_required
def policy_tracking_manage_policies(request):
    """Manage policy recommendations page."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count
    
    # Get all policies with related data
    policies = PolicyRecommendation.objects.select_related(
        'proposed_by', 'lead_author', 'assigned_reviewer'
    ).annotate(
        evidence_count=Count('evidence')
    ).order_by('-created_at')
    
    # Filter functionality
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    
    if status_filter:
        policies = policies.filter(status=status_filter)
    
    if category_filter:
        policies = policies.filter(category=category_filter)
    
    # Get filter options
    status_choices = PolicyRecommendation.STATUS_CHOICES if hasattr(PolicyRecommendation, 'STATUS_CHOICES') else []
    category_choices = PolicyRecommendation.CATEGORY_CHOICES if hasattr(PolicyRecommendation, 'CATEGORY_CHOICES') else []
    
    # Statistics
    stats = {
        'total_policies': policies.count(),
        'implemented': policies.filter(status='implemented').count(),
        'under_review': policies.filter(status='under_review').count(),
        'approved': policies.filter(status='approved').count(),
    }
    
    context = {
        'policies': policies,
        'status_choices': status_choices,
        'category_choices': category_choices,
        'current_status': status_filter,
        'current_category': category_filter,
        'stats': stats,
    }
    return render(request, 'common/policy_tracking_manage_policies.html', context)
