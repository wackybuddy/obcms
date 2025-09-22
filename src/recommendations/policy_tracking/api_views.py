from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (PolicyDocument, PolicyEvidence, PolicyImpact,
                     PolicyRecommendation)
from .serializers import (PolicyDocumentListSerializer,
                          PolicyDocumentSerializer,
                          PolicyEvidenceListSerializer,
                          PolicyEvidenceSerializer, PolicyImpactListSerializer,
                          PolicyImpactSerializer,
                          PolicyRecommendationListSerializer,
                          PolicyRecommendationSerializer)


class PolicyRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for PolicyRecommendation model."""

    queryset = PolicyRecommendation.objects.all().select_related(
        "related_need", "submitted_by", "reviewed_by"
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "policy_category",
        "status",
        "priority_level",
        "related_need",
        "submitted_by",
        "reviewed_by",
    ]
    search_fields = ["title", "description", "summary", "reference_number"]
    ordering_fields = [
        "title",
        "submission_date",
        "target_implementation_date",
        "priority_level",
        "created_at",
    ]
    ordering = ["-submission_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return PolicyRecommendationListSerializer
        return PolicyRecommendationSerializer

    @action(detail=True, methods=["get"])
    def evidence(self, request, pk=None):
        """Get evidence for this policy recommendation."""
        recommendation = self.get_object()
        evidence = recommendation.evidence.all()
        serializer = PolicyEvidenceSerializer(evidence, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def impacts(self, request, pk=None):
        """Get impacts for this policy recommendation."""
        recommendation = self.get_object()
        impacts = recommendation.impacts.all()
        serializer = PolicyImpactSerializer(impacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        """Get documents for this policy recommendation."""
        recommendation = self.get_object()
        documents = recommendation.documents.all()
        serializer = PolicyDocumentSerializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get policy recommendation statistics."""
        queryset = self.get_queryset()
        stats = {
            "total": queryset.count(),
            "by_status": {},
            "by_category": {},
            "by_priority": {},
            "recent_submissions": queryset.filter(submission_date__isnull=False)
            .order_by("-submission_date")[:10]
            .values("id", "title", "status", "submission_date"),
        }

        # Count by status
        for status, _ in PolicyRecommendation.STATUS_CHOICES:
            count = queryset.filter(status=status).count()
            stats["by_status"][status] = count

        # Count by category
        for category, _ in PolicyRecommendation.POLICY_CATEGORIES:
            count = queryset.filter(policy_category=category).count()
            stats["by_category"][category] = count

        # Count by priority
        for priority, _ in PolicyRecommendation.PRIORITY_LEVELS:
            count = queryset.filter(priority_level=priority).count()
            stats["by_priority"][priority] = count

        return Response(stats)


class PolicyEvidenceViewSet(viewsets.ModelViewSet):
    """ViewSet for PolicyEvidence model."""

    queryset = PolicyEvidence.objects.all().select_related("recommendation")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "recommendation",
        "evidence_type",
        "is_verified",
        "reliability_score",
    ]
    search_fields = ["title", "description", "source", "recommendation__title"]
    ordering_fields = ["title", "reliability_score", "verification_date", "created_at"]
    ordering = ["-reliability_score", "-verification_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return PolicyEvidenceListSerializer
        return PolicyEvidenceSerializer


class PolicyImpactViewSet(viewsets.ModelViewSet):
    """ViewSet for PolicyImpact model."""

    queryset = PolicyImpact.objects.all().select_related("recommendation")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["recommendation", "measurement_date"]
    search_fields = ["indicator_name", "impact_assessment", "recommendation__title"]
    ordering_fields = ["indicator_name", "measurement_date", "created_at"]
    ordering = ["-measurement_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return PolicyImpactListSerializer
        return PolicyImpactSerializer


class PolicyDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for PolicyDocument model."""

    queryset = PolicyDocument.objects.all().select_related("recommendation")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["recommendation", "document_type", "is_public"]
    search_fields = ["title", "description", "recommendation__title"]
    ordering_fields = ["title", "upload_date", "version", "created_at"]
    ordering = ["-upload_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return PolicyDocumentListSerializer
        return PolicyDocumentSerializer

    def get_permissions(self):
        """Set permissions based on action and document visibility."""
        if self.action in ["list", "retrieve"]:
            # Check if user can view non-public documents
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = super().get_queryset()
        user = self.request.user

        # If not staff/admin, only show public documents or own submissions
        if not user.is_staff:
            from django.db import models as django_models

            queryset = queryset.filter(
                django_models.Q(is_public=True)
                | django_models.Q(recommendation__submitted_by=user)
            )

        return queryset
