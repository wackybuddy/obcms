"""
API Documentation for OBC Management System

This module provides comprehensive API documentation and statistics.
"""

from django.conf import settings
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_overview(request):
    """
    Provides an overview of all available API endpoints in the OBC Management System.
    """

    base_url = request.build_absolute_uri("/api/")

    api_endpoints = {
        "authentication": {
            "description": "Authentication and token management",
            "endpoints": {
                "token_obtain": f"{base_url}auth/token/",
                "token_refresh": f"{base_url}auth/token/refresh/",
                "browsable_auth": f"{base_url}api-auth/",
            },
        },
        "administrative": {
            "description": "Administrative hierarchy management (Regions, Provinces, etc.)",
            "endpoints": {
                "users": f"{base_url}administrative/users/",
                "regions": f"{base_url}administrative/regions/",
                "provinces": f"{base_url}administrative/provinces/",
                "municipalities": f"{base_url}administrative/municipalities/",
                "barangays": f"{base_url}administrative/barangays/",
            },
        },
        "communities": {
            "description": "OBC community profiles and stakeholder management",
            "endpoints": {
                "communities": f"{base_url}communities/communities/",
                "stakeholders": f"{base_url}communities/stakeholders/",
                "stakeholder_engagements": f"{base_url}communities/stakeholder-engagements/",
                "livelihoods": f"{base_url}communities/livelihoods/",
                "infrastructure": f"{base_url}communities/infrastructure/",
            },
        },
        "mana": {
            "description": "Mapping and Needs Assessment (MANA) functionality",
            "endpoints": {
                "assessment_categories": f"{base_url}mana/assessment-categories/",
                "assessments": f"{base_url}mana/assessments/",
                "needs_categories": f"{base_url}mana/needs-categories/",
                "needs": f"{base_url}mana/needs/",
                "surveys": f"{base_url}mana/surveys/",
                "mapping_activities": f"{base_url}mana/mapping-activities/",
                "baseline_studies": f"{base_url}mana/baseline-studies/",
                "geographic_data_layers": f"{base_url}mana/geographic-data-layers/",
                "map_visualizations": f"{base_url}mana/map-visualizations/",
            },
        },
        "coordination": {
            "description": "Multi-stakeholder coordination and partnership management",
            "endpoints": {
                "organizations": f"{base_url}coordination/organizations/",
                "stakeholder_engagements": f"{base_url}coordination/stakeholder-engagements/",
                "communications": f"{base_url}coordination/communications/",
                "events": f"{base_url}coordination/events/",
                "action_items": f"{base_url}coordination/action-items/",
                "partnerships": f"{base_url}coordination/partnerships/",
                "partnership_milestones": f"{base_url}coordination/partnership-milestones/",
            },
        },
        "policy_tracking": {
            "description": "Policy recommendation tracking and evidence management",
            "endpoints": {
                "recommendations": f"{base_url}policy-tracking/recommendations/",
                "evidence": f"{base_url}policy-tracking/evidence/",
                "impacts": f"{base_url}policy-tracking/impacts/",
                "documents": f"{base_url}policy-tracking/documents/",
            },
        },
    }

    response_data = {
        "system": {
            "name": "Other Bangsamoro Communities (OBC) Management System",
            "description": "Comprehensive system for managing OBC communities outside BARMM",
            "version": "1.0.0",
            "base_url": base_url,
        },
        "authentication": {
            "type": "JWT (JSON Web Token)",
            "access_token_lifetime": "1 hour",
            "refresh_token_lifetime": "7 days",
            "header_format": "Authorization: Bearer <token>",
        },
        "features": {
            "filtering": "Use ?field=value for filtering",
            "searching": "Use ?search=term for text search",
            "ordering": "Use ?ordering=field or ?ordering=-field",
            "pagination": "20 items per page by default",
        },
        "endpoints": api_endpoints,
    }

    return Response(response_data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def api_statistics(request):
    """
    Provides system-wide statistics for the OBC Management System.
    """
    from common.models import User
    from communities.models import OBCCommunity, Stakeholder
    from coordination.models import Event, Partnership
    from mana.models import Assessment, Need
    from recommendations.policy_tracking.models import PolicyRecommendation

    stats = {
        "system_overview": {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "total_communities": OBCCommunity.objects.count(),
            "active_communities": OBCCommunity.objects.filter(is_active=True).count(),
        },
        "communities": {
            "total_communities": OBCCommunity.objects.count(),
            "total_stakeholders": Stakeholder.objects.count(),
            "active_stakeholders": Stakeholder.objects.filter(is_active=True).count(),
            "verified_stakeholders": Stakeholder.objects.filter(
                is_verified=True
            ).count(),
        },
        "assessments": {
            "total_assessments": Assessment.objects.count(),
            "completed_assessments": Assessment.objects.filter(
                status="completed"
            ).count(),
            "ongoing_assessments": Assessment.objects.filter(
                status__in=["data_collection", "analysis"]
            ).count(),
            "total_needs": Need.objects.count(),
        },
        "coordination": {
            "total_events": Event.objects.count(),
            "upcoming_events": Event.objects.filter(status="planned").count(),
            "total_partnerships": Partnership.objects.count(),
            "active_partnerships": Partnership.objects.filter(status="active").count(),
        },
        "policy_tracking": {
            "total_recommendations": PolicyRecommendation.objects.count(),
            "implemented_policies": PolicyRecommendation.objects.filter(
                status="implemented"
            ).count(),
            "pending_review": PolicyRecommendation.objects.filter(
                status="under_review"
            ).count(),
        },
    }

    return Response(stats)
