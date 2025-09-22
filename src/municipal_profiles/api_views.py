from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.models import Municipality

from .models import MunicipalOBCProfile
from .serializers import MunicipalOBCProfileSerializer
from .services import aggregate_and_store, ensure_profile


class MunicipalOBCProfileViewSet(viewsets.ModelViewSet):
    """API surface for municipal OBC profiles."""

    serializer_class = MunicipalOBCProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = MunicipalOBCProfile.objects.select_related(
        "municipality",
        "municipality__province",
        "municipality__province__region",
    ).all()
    http_method_names = ["get", "post", "patch", "put"]

    def create(self, request, *args, **kwargs):
        municipality_id = request.data.get("municipality")
        municipality = get_object_or_404(Municipality, pk=municipality_id)
        profile = ensure_profile(municipality)
        aggregate_and_store(
            municipality=municipality,
            changed_by=request.user if request.user.is_authenticated else None,
            note="Profile initialisation",
        )
        profile.refresh_from_db()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def get_queryset(self):
        qs = super().get_queryset()
        municipality_id = self.request.query_params.get("municipality")
        if municipality_id:
            qs = qs.filter(municipality_id=municipality_id)
        return qs

    @action(detail=True, methods=["post"], url_path="refresh-aggregation")
    def refresh_aggregation(self, request, pk=None):
        profile = self.get_object()
        aggregate_and_store(
            municipality=profile.municipality,
            changed_by=request.user if request.user.is_authenticated else None,
            note="Manual refresh via API",
        )
        profile.refresh_from_db()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
