from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Barangay, Municipality, Province, Region, User
from .serializers import (BarangayListSerializer, BarangaySerializer,
                          MunicipalityListSerializer, MunicipalitySerializer,
                          ProvinceListSerializer, ProvinceSerializer,
                          RegionListSerializer, RegionSerializer,
                          UserCreateSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Provides CRUD operations for users with proper permissions.
    """

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["user_type", "is_active", "is_approved"]
    search_fields = ["username", "first_name", "last_name", "email", "organization"]
    ordering_fields = ["username", "date_joined", "last_login"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == "create":
            # Allow user registration
            return [permissions.AllowAny()]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Only admin users can modify other users
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Region model.
    Provides list and detail views for regions.
    """

    queryset = Region.objects.filter(is_active=True)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["code", "name", "description"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["code"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return RegionListSerializer
        return RegionSerializer

    @action(detail=True, methods=["get"])
    def provinces(self, request, pk=None):
        """Get all provinces in this region."""
        region = self.get_object()
        provinces = region.provinces.filter(is_active=True)
        serializer = ProvinceListSerializer(provinces, many=True)
        return Response(serializer.data)


class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Province model.
    Provides list and detail views for provinces.
    """

    queryset = Province.objects.filter(is_active=True).select_related("region")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["region", "is_active"]
    search_fields = ["code", "name", "capital", "region__name"]
    ordering_fields = ["name", "region__code", "created_at"]
    ordering = ["region__code", "name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ProvinceListSerializer
        return ProvinceSerializer

    @action(detail=True, methods=["get"])
    def municipalities(self, request, pk=None):
        """Get all municipalities in this province."""
        province = self.get_object()
        municipalities = province.municipalities.filter(is_active=True)
        serializer = MunicipalityListSerializer(municipalities, many=True)
        return Response(serializer.data)


class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Municipality model.
    Provides list and detail views for municipalities.
    """

    queryset = Municipality.objects.filter(is_active=True).select_related(
        "province__region"
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["province", "municipality_type", "is_active"]
    search_fields = ["code", "name", "province__name", "province__region__name"]
    ordering_fields = ["name", "municipality_type", "created_at"]
    ordering = ["province__region__code", "province__name", "name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return MunicipalityListSerializer
        return MunicipalitySerializer

    @action(detail=True, methods=["get"])
    def barangays(self, request, pk=None):
        """Get all barangays in this municipality."""
        municipality = self.get_object()
        barangays = municipality.barangays.filter(is_active=True)
        serializer = BarangayListSerializer(barangays, many=True)
        return Response(serializer.data)


class BarangayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Barangay model.
    Provides list and detail views for barangays.
    """

    queryset = Barangay.objects.filter(is_active=True).select_related(
        "municipality__province__region"
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["municipality", "is_urban", "is_active"]
    search_fields = [
        "code",
        "name",
        "municipality__name",
        "municipality__province__name",
        "municipality__province__region__name",
    ]
    ordering_fields = ["name", "is_urban", "created_at"]
    ordering = [
        "municipality__province__region__code",
        "municipality__province__name",
        "municipality__name",
        "name",
    ]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return BarangayListSerializer
        return BarangaySerializer
