from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    OBCCommunity, CommunityLivelihood, CommunityInfrastructure,
    Stakeholder, StakeholderEngagement
)
from .serializers import (
    OBCCommunitySerializer, OBCCommunityListSerializer,
    CommunityLivelihoodSerializer, CommunityInfrastructureSerializer,
    StakeholderSerializer, StakeholderListSerializer,
    StakeholderEngagementSerializer, CommunityStatsSerializer,
    StakeholderStatsSerializer
)


class OBCCommunityViewSet(viewsets.ModelViewSet):
    """ViewSet for OBC Community model."""
    
    queryset = OBCCommunity.objects.select_related(
        'barangay', 'barangay__municipality', 'barangay__municipality__province',
        'barangay__municipality__province__region'
    ).prefetch_related('livelihoods', 'infrastructure', 'stakeholders').all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return OBCCommunityListSerializer
        return OBCCommunitySerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get community statistics."""
        communities = self.get_queryset()
        
        # Basic counts
        total_communities = communities.count()
        total_population = sum(c.population or 0 for c in communities)
        total_households = sum(c.households or 0 for c in communities)
        
        # By region
        by_region = {}
        for community in communities:
            region_name = community.region.name
            if region_name not in by_region:
                by_region[region_name] = 0
            by_region[region_name] += 1
        
        # By development status
        by_development_status = {}
        for community in communities:
            status = community.get_development_status_display()
            if status not in by_development_status:
                by_development_status[status] = 0
            by_development_status[status] += 1
        
        # By settlement type
        by_settlement_type = {}
        for community in communities:
            settlement = community.get_settlement_type_display()
            if settlement not in by_settlement_type:
                by_settlement_type[settlement] = 0
            by_settlement_type[settlement] += 1
        
        # Religious facilities
        religious_facilities = {
            'communities_with_mosque': communities.filter(has_mosque=True).count(),
            'communities_with_madrasah': communities.filter(has_madrasah=True).count(),
            'total_religious_leaders': sum(c.religious_leaders_count for c in communities)
        }
        
        # Average household size
        household_sizes = [c.average_household_size for c in communities if c.average_household_size]
        average_household_size = sum(household_sizes) / len(household_sizes) if household_sizes else 0
        
        # Language distribution
        language_distribution = {}
        for community in communities:
            if community.primary_language:
                lang = community.primary_language
                if lang not in language_distribution:
                    language_distribution[lang] = 0
                language_distribution[lang] += 1
        
        stats_data = {
            'total_communities': total_communities,
            'total_population': total_population,
            'total_households': total_households,
            'by_region': by_region,
            'by_development_status': by_development_status,
            'by_settlement_type': by_settlement_type,
            'religious_facilities': religious_facilities,
            'average_household_size': round(average_household_size, 1),
            'language_distribution': language_distribution
        }
        
        serializer = CommunityStatsSerializer(stats_data)
        return Response(serializer.data)


class StakeholderViewSet(viewsets.ModelViewSet):
    """ViewSet for Stakeholder model."""
    
    queryset = Stakeholder.objects.select_related(
        'community', 'community__barangay', 'community__barangay__municipality',
        'community__barangay__municipality__province',
        'community__barangay__municipality__province__region'
    ).prefetch_related('engagements').all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return StakeholderListSerializer
        return StakeholderSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by community
        community_id = self.request.query_params.get('community', None)
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        
        # Filter by stakeholder type
        stakeholder_type = self.request.query_params.get('type', None)
        if stakeholder_type:
            queryset = queryset.filter(stakeholder_type=stakeholder_type)
        
        # Filter by influence level
        influence_level = self.request.query_params.get('influence', None)
        if influence_level:
            queryset = queryset.filter(influence_level=influence_level)
        
        # Filter by active status
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by verified status
        is_verified = self.request.query_params.get('verified', None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get stakeholder statistics."""
        stakeholders = self.get_queryset()
        
        # Basic counts
        total_stakeholders = stakeholders.count()
        active_stakeholders = stakeholders.filter(is_active=True).count()
        verified_stakeholders = stakeholders.filter(is_verified=True).count()
        
        # By type
        by_type = {}
        for stakeholder in stakeholders:
            stype = stakeholder.get_stakeholder_type_display()
            if stype not in by_type:
                by_type[stype] = 0
            by_type[stype] += 1
        
        # By influence level
        by_influence_level = {}
        for stakeholder in stakeholders:
            influence = stakeholder.get_influence_level_display()
            if influence not in by_influence_level:
                by_influence_level[influence] = 0
            by_influence_level[influence] += 1
        
        # By engagement level
        by_engagement_level = {}
        for stakeholder in stakeholders:
            engagement = stakeholder.get_engagement_level_display()
            if engagement not in by_engagement_level:
                by_engagement_level[engagement] = 0
            by_engagement_level[engagement] += 1
        
        # By community
        by_community = {}
        for stakeholder in stakeholders:
            community = stakeholder.community.barangay.name
            if community not in by_community:
                by_community[community] = 0
            by_community[community] += 1
        
        # Recent engagements (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_engagements = StakeholderEngagement.objects.filter(
            stakeholder__in=stakeholders,
            date__gte=thirty_days_ago
        ).count()
        
        stats_data = {
            'total_stakeholders': total_stakeholders,
            'active_stakeholders': active_stakeholders,
            'verified_stakeholders': verified_stakeholders,
            'by_type': by_type,
            'by_influence_level': by_influence_level,
            'by_engagement_level': by_engagement_level,
            'by_community': by_community,
            'recent_engagements': recent_engagements
        }
        
        serializer = StakeholderStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a stakeholder."""
        stakeholder = self.get_object()
        stakeholder.is_verified = True
        stakeholder.verification_date = timezone.now().date()
        stakeholder.save()
        
        serializer = self.get_serializer(stakeholder)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unverify(self, request, pk=None):
        """Unverify a stakeholder."""
        stakeholder = self.get_object()
        stakeholder.is_verified = False
        stakeholder.verification_date = None
        stakeholder.save()
        
        serializer = self.get_serializer(stakeholder)
        return Response(serializer.data)


class StakeholderEngagementViewSet(viewsets.ModelViewSet):
    """ViewSet for Stakeholder Engagement model."""
    
    serializer_class = StakeholderEngagementSerializer
    queryset = StakeholderEngagement.objects.select_related(
        'stakeholder', 'stakeholder__community'
    ).all()
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by stakeholder
        stakeholder_id = self.request.query_params.get('stakeholder', None)
        if stakeholder_id:
            queryset = queryset.filter(stakeholder_id=stakeholder_id)
        
        # Filter by community
        community_id = self.request.query_params.get('community', None)
        if community_id:
            queryset = queryset.filter(stakeholder__community_id=community_id)
        
        # Filter by engagement type
        engagement_type = self.request.query_params.get('type', None)
        if engagement_type:
            queryset = queryset.filter(engagement_type=engagement_type)
        
        # Filter by outcome
        outcome = self.request.query_params.get('outcome', None)
        if outcome:
            queryset = queryset.filter(outcome=outcome)
        
        # Filter by follow-up needed
        follow_up = self.request.query_params.get('follow_up', None)
        if follow_up is not None:
            queryset = queryset.filter(follow_up_needed=follow_up.lower() == 'true')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset


class CommunityLivelihoodViewSet(viewsets.ModelViewSet):
    """ViewSet for Community Livelihood model."""
    
    serializer_class = CommunityLivelihoodSerializer
    queryset = CommunityLivelihood.objects.select_related('community').all()
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by community
        community_id = self.request.query_params.get('community', None)
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        
        return queryset


class CommunityInfrastructureViewSet(viewsets.ModelViewSet):
    """ViewSet for Community Infrastructure model."""
    
    serializer_class = CommunityInfrastructureSerializer
    queryset = CommunityInfrastructure.objects.select_related('community').all()
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by community
        community_id = self.request.query_params.get('community', None)
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        
        return queryset
