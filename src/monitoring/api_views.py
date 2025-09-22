"""REST API viewsets for Monitoring & Evaluation data."""

from django.db.models import Prefetch
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import MonitoringEntry, MonitoringUpdate
from .serializers import MonitoringEntrySerializer, MonitoringUpdateSerializer


class MonitoringEntryViewSet(viewsets.ModelViewSet):
    """CRUD operations for monitoring entries."""

    serializer_class = MonitoringEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    queryset = MonitoringEntry.objects.all()
    filterset_fields = {
        "category": ["exact"],
        "status": ["exact"],
        "request_status": ["exact"],
        "priority": ["exact"],
        "lead_organization": ["exact"],
        "submitted_by_community": ["exact"],
        "submitted_to_organization": ["exact"],
    }
    search_fields = ["title", "summary", "oobc_unit", "support_required"]
    ordering_fields = [
        "created_at",
        "updated_at",
        "title",
        "priority",
        "progress",
        "target_end_date",
    ]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return (
            MonitoringEntry.objects.all()
            .select_related(
                "lead_organization",
                "submitted_by_community",
                "submitted_to_organization",
                "related_assessment",
                "related_event",
                "related_policy",
                "created_by",
                "updated_by",
            )
            .prefetch_related(
                "supporting_organizations",
                "communities",
                Prefetch(
                    "updates",
                    queryset=MonitoringUpdate.objects.select_related("created_by"),
                ),
            )
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class MonitoringUpdateViewSet(viewsets.ModelViewSet):
    """CRUD operations for monitoring updates."""

    serializer_class = MonitoringUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    queryset = MonitoringUpdate.objects.all()
    filterset_fields = {
        "entry": ["exact"],
        "update_type": ["exact"],
        "status": ["exact"],
        "request_status": ["exact"],
    }
    search_fields = ["notes", "next_steps"]
    ordering_fields = ["created_at", "follow_up_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return MonitoringUpdate.objects.select_related("entry", "created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)
