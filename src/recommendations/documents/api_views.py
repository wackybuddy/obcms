import mimetypes
import os
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import Document, DocumentAccess, DocumentCategory, DocumentComment
from .serializers import (DocumentAccessSerializer, DocumentCategorySerializer,
                          DocumentCommentSerializer, DocumentListSerializer,
                          DocumentSerializer, DocumentUploadSerializer)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Comprehensive document management viewset with security and access control.
    """

    queryset = Document.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "confidentiality_level", "status", "tags"]
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["created_at", "updated_at", "title", "file_size"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentListSerializer
        elif self.action == "upload":
            return DocumentUploadSerializer
        return DocumentSerializer

    def get_queryset(self):
        """Filter documents based on user access permissions."""
        user = self.request.user

        # Superusers can see all documents
        if user.is_superuser:
            return Document.objects.all()

        # Filter based on user access permissions
        accessible_docs = Q()

        # Public documents
        accessible_docs |= Q(confidentiality_level="public")

        # Documents user has explicit access to
        user_access = DocumentAccess.objects.filter(user=user, is_active=True)
        accessible_docs |= Q(id__in=user_access.values("document_id"))

        # Documents uploaded by user
        accessible_docs |= Q(uploaded_by=user)

        # Internal documents for staff
        if user.is_staff:
            accessible_docs |= Q(confidentiality_level="internal")

        return Document.objects.filter(accessible_docs).distinct()

    def perform_create(self, serializer):
        """Set the uploader and create access log."""
        document = serializer.save(uploaded_by=self.request.user)

        # Log the upload
        DocumentAccess.objects.create(
            document=document,
            user=self.request.user,
            access_type="upload",
            granted_by=self.request.user,
            is_active=True,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get("HTTP_USER_AGENT", "")[:500],
        )

    def get_client_ip(self):
        """Get client IP address."""
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """
        Download document file with access logging and security checks.
        """
        document = get_object_or_404(Document, pk=pk)

        # Check if user has access to this document
        if not self.has_document_access(request.user, document):
            return Response(
                {"error": "You do not have permission to access this document."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Log the download
        DocumentAccess.objects.create(
            document=document,
            user=request.user,
            access_type="download",
            granted_by=document.uploaded_by,
            ip_address=self.get_client_ip(),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        # Increment download count
        document.download_count += 1
        document.save(update_fields=["download_count"])

        # Serve the file
        try:
            if document.file and os.path.exists(document.file.path):
                response = HttpResponse(
                    document.file.read(),
                    content_type=mimetypes.guess_type(document.file.name)[0]
                    or "application/octet-stream",
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{document.original_filename or document.file.name}"'
                )
                response["Content-Length"] = document.file.size
                return response
            else:
                return Response(
                    {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"error": f"Error downloading file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def has_document_access(self, user, document):
        """Check if user has access to the document."""
        # Superusers have access to everything
        if user.is_superuser:
            return True

        # Document uploader has access
        if document.uploaded_by == user:
            return True

        # Public documents
        if document.confidentiality_level == "public":
            return True

        # Internal documents for staff
        if document.confidentiality_level == "internal" and user.is_staff:
            return True

        # Check explicit access
        return DocumentAccess.objects.filter(
            document=document, user=user, is_active=True
        ).exists()

    @action(detail=True, methods=["post"])
    def grant_access(self, request, pk=None):
        """Grant access to a document for specific users."""
        document = get_object_or_404(Document, pk=pk)

        # Only document owner or superuser can grant access
        if not (request.user == document.uploaded_by or request.user.is_superuser):
            return Response(
                {
                    "error": "You do not have permission to grant access to this document."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user_ids = request.data.get("user_ids", [])
        access_type = request.data.get("access_type", "view")

        granted_access = []
        for user_id in user_ids:
            try:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                user = User.objects.get(id=user_id)

                access, created = DocumentAccess.objects.get_or_create(
                    document=document,
                    user=user,
                    defaults={
                        "access_type": access_type,
                        "granted_by": request.user,
                        "is_active": True,
                        "ip_address": self.get_client_ip(),
                        "user_agent": request.META.get("HTTP_USER_AGENT", "")[:500],
                    },
                )

                if not created:
                    access.is_active = True
                    access.access_type = access_type
                    access.granted_by = request.user
                    access.ip_address = self.get_client_ip()
                    access.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
                    access.save()

                granted_access.append(
                    {
                        "user_id": user.id,
                        "username": user.username,
                        "access_type": access.access_type,
                        "created": created,
                    }
                )
            except Exception as e:
                return Response(
                    {"error": f"Error granting access to user {user_id}: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response({"granted_access": granted_access})

    @action(detail=True, methods=["post"])
    def revoke_access(self, request, pk=None):
        """Revoke access to a document for specific users."""
        document = get_object_or_404(Document, pk=pk)

        # Only document owner or superuser can revoke access
        if not (request.user == document.uploaded_by or request.user.is_superuser):
            return Response(
                {
                    "error": "You do not have permission to revoke access to this document."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user_ids = request.data.get("user_ids", [])

        revoked_count = DocumentAccess.objects.filter(
            document=document, user_id__in=user_ids
        ).update(is_active=False)

        return Response({"revoked_access_count": revoked_count})

    @action(detail=True, methods=["get"])
    def access_log(self, request, pk=None):
        """Get access log for a document."""
        document = get_object_or_404(Document, pk=pk)

        # Only document owner or superuser can view access log
        if not (request.user == document.uploaded_by or request.user.is_superuser):
            return Response(
                {
                    "error": "You do not have permission to view access log for this document."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        access_logs = DocumentAccess.objects.filter(document=document).order_by(
            "-accessed_at"
        )
        serializer = DocumentAccessSerializer(access_logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get document statistics."""
        queryset = self.get_queryset()

        download_counts = queryset.values_list("download_count", flat=True)
        file_sizes = queryset.values_list("file_size", flat=True)

        stats = {
            "total_documents": queryset.count(),
            "by_category": queryset.values("category__name").annotate(
                count=Count("id")
            ),
            "by_confidentiality": queryset.values("confidentiality_level").annotate(
                count=Count("id")
            ),
            "by_status": queryset.values("status").annotate(count=Count("id")),
            "total_downloads": sum(count or 0 for count in download_counts),
            "total_file_size": sum(size or 0 for size in file_sizes),
        }

        return Response(stats)

    @action(detail=False, methods=["get"])
    def recent_uploads(self, request):
        """Get recently uploaded documents."""
        days = int(request.query_params.get("days", 7))
        since_date = datetime.now() - timedelta(days=days)

        recent_docs = (
            self.get_queryset()
            .filter(created_at__gte=since_date)
            .order_by("-created_at")[:20]
        )

        serializer = DocumentListSerializer(recent_docs, many=True)
        return Response(serializer.data)


class DocumentCategoryViewSet(viewsets.ModelViewSet):
    """Document category management."""

    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        """Get all documents in this category."""
        category = get_object_or_404(DocumentCategory, pk=pk)
        documents = Document.objects.filter(category=category)

        # Apply same access control as DocumentViewSet
        user = request.user
        if not user.is_superuser:
            accessible_docs = Q()
            accessible_docs |= Q(confidentiality_level="public")
            accessible_docs |= Q(uploaded_by=user)

            if user.is_staff:
                accessible_docs |= Q(confidentiality_level="internal")

            user_access = DocumentAccess.objects.filter(user=user, is_active=True)
            accessible_docs |= Q(id__in=user_access.values("document_id"))

            documents = documents.filter(accessible_docs).distinct()

        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)


class DocumentCommentViewSet(viewsets.ModelViewSet):
    """Document comment management."""

    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["document"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filter comments based on document access."""
        user = self.request.user

        # Get documents user has access to
        if user.is_superuser:
            accessible_docs = Document.objects.all()
        else:
            accessible_docs = Q()
            accessible_docs |= Q(confidentiality_level="public")
            accessible_docs |= Q(uploaded_by=user)

            if user.is_staff:
                accessible_docs |= Q(confidentiality_level="internal")

            user_access = DocumentAccess.objects.filter(user=user, is_active=True)
            accessible_docs |= Q(id__in=user_access.values("document_id"))

            accessible_docs = Document.objects.filter(accessible_docs).distinct()

        return DocumentComment.objects.filter(document__in=accessible_docs)

    def perform_create(self, serializer):
        """Set the comment author."""
        serializer.save(user=self.request.user)
