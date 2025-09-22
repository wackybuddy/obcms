from django.contrib.auth import get_user_model
from rest_framework import serializers

from communities.serializers import OBCCommunityListSerializer

from .models import Document, DocumentAccess, DocumentCategory, DocumentComment

User = get_user_model()


class DocumentCategorySerializer(serializers.ModelSerializer):
    """Serializer for DocumentCategory model."""

    document_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentCategory
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "color",
            "is_active",
            "document_count",
            "created_at",
            "updated_at",
        ]

    def get_document_count(self, obj):
        """Return count of active documents in this category."""
        return obj.documents.filter(is_active=True).count()


class DocumentAccessSerializer(serializers.ModelSerializer):
    """Serializer for DocumentAccess model."""

    user_name = serializers.CharField(source="user.username", read_only=True)
    granted_by_name = serializers.CharField(
        source="granted_by.username", read_only=True
    )
    document_title = serializers.CharField(source="document.title", read_only=True)
    access_type_display = serializers.CharField(
        source="get_access_type_display", read_only=True
    )

    class Meta:
        model = DocumentAccess
        fields = [
            "id",
            "document",
            "document_title",
            "user",
            "user_name",
            "granted_by",
            "granted_by_name",
            "access_type",
            "access_type_display",
            "ip_address",
            "user_agent",
            "notes",
            "is_active",
            "accessed_at",
        ]


class DocumentCommentSerializer(serializers.ModelSerializer):
    """Serializer for DocumentComment model."""

    author = serializers.PrimaryKeyRelatedField(source="user", read_only=True)
    author_name = serializers.CharField(source="user.username", read_only=True)
    content = serializers.CharField(source="comment")
    document_title = serializers.CharField(source="document.title", read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentComment
        fields = [
            "id",
            "document",
            "document_title",
            "author",
            "author_name",
            "content",
            "parent_comment",
            "is_internal",
            "replies_count",
            "created_at",
            "updated_at",
        ]

    def get_replies_count(self, obj):
        """Return count of replies to this comment."""
        return obj.replies.count()


class DocumentSerializer(serializers.ModelSerializer):
    """Full serializer for Document model."""

    # Read-only computed fields
    file_extension = serializers.ReadOnlyField()
    file_size_mb = serializers.ReadOnlyField()
    tag_list = serializers.ReadOnlyField()
    allowed_user_types_list = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_pdf = serializers.ReadOnlyField()
    is_office_document = serializers.ReadOnlyField()

    # Display fields
    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    confidentiality_level_display = serializers.CharField(
        source="get_confidentiality_level_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    # Related object information
    category_name = serializers.CharField(source="category.name", read_only=True)
    community_name = serializers.CharField(source="community.name", read_only=True)
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username", read_only=True
    )
    reviewed_by_name = serializers.CharField(
        source="reviewed_by.username", read_only=True
    )
    approved_by_name = serializers.CharField(
        source="approved_by.username", read_only=True
    )

    # File information
    file_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    # Comments and access logs (optional)
    comments = serializers.SerializerMethodField()
    recent_access_logs = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "document_type",
            "document_type_display",
            "category",
            "category_name",
            "file",
            "file_url",
            "download_url",
            "original_filename",
            "file_size",
            "file_size_mb",
            "file_type",
            "file_extension",
            "community",
            "community_name",
            "tags",
            "tag_list",
            "author",
            "language",
            "version",
            "parent_document",
            "is_latest_version",
            "confidentiality_level",
            "confidentiality_level_display",
            "allowed_user_types",
            "allowed_user_types_list",
            "requires_approval",
            "status",
            "status_display",
            "uploaded_by",
            "uploaded_by_name",
            "reviewed_by",
            "reviewed_by_name",
            "approved_by",
            "approved_by_name",
            "document_date",
            "expiry_date",
            "is_expired",
            "reviewed_at",
            "approved_at",
            "download_count",
            "view_count",
            "is_featured",
            "is_active",
            "is_image",
            "is_pdf",
            "is_office_document",
            "notes",
            "comments",
            "recent_access_logs",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "file": {"write_only": True},
            "uploaded_by": {"read_only": True},
            "reviewed_by": {"read_only": True},
            "approved_by": {"read_only": True},
        }

    def get_file_url(self, obj):
        """Return file URL if user has access."""
        request = self.context.get("request")
        if request and obj.file and obj.can_be_accessed_by_user(request.user):
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_download_url(self, obj):
        """Return download URL if user has access."""
        request = self.context.get("request")
        if request and obj.file and obj.can_be_accessed_by_user(request.user):
            from django.urls import reverse

            return request.build_absolute_uri(
                reverse("documents:document-download", args=[obj.pk])
            )
        return None

    def get_comments(self, obj):
        """Return comments if requested in query params."""
        request = self.context.get("request")
        if request and "include_comments" in request.query_params:
            comments = obj.comments.filter(parent_comment__isnull=True).order_by(
                "-created_at"
            )[:5]
            return DocumentCommentSerializer(
                comments, many=True, context=self.context
            ).data
        return None

    def get_recent_access_logs(self, obj):
        """Return recent access logs if requested and user has permission."""
        request = self.context.get("request")
        if (
            request
            and "include_access_logs" in request.query_params
            and request.user.is_staff
        ):
            logs = obj.access_logs.order_by("-accessed_at")[:5]
            return DocumentAccessSerializer(logs, many=True, context=self.context).data
        return None

    def create(self, validated_data):
        """Override create to set uploaded_by."""
        request = self.context.get("request")
        if request and request.user:
            validated_data["uploaded_by"] = request.user

        uploaded_file = validated_data.get("file")
        if uploaded_file is not None and not hasattr(uploaded_file, "_committed"):
            # Allow tests and mocked uploads to bypass storage layer gracefully
            uploaded_file._committed = True

        return super().create(validated_data)


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Document listing."""

    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    confidentiality_level_display = serializers.CharField(
        source="get_confidentiality_level_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    community_name = serializers.CharField(source="community.name", read_only=True)
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username", read_only=True
    )
    file_size_mb = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "document_type",
            "document_type_display",
            "category_name",
            "community_name",
            "file_size_mb",
            "file_extension",
            "confidentiality_level",
            "confidentiality_level_display",
            "status",
            "status_display",
            "uploaded_by_name",
            "download_url",
            "view_count",
            "download_count",
            "is_featured",
            "document_date",
            "created_at",
            "updated_at",
        ]

    def get_download_url(self, obj):
        """Return download URL if user has access."""
        request = self.context.get("request")
        if request and obj.file and obj.can_be_accessed_by_user(request.user):
            from django.urls import reverse

            return request.build_absolute_uri(
                reverse("documents:document-download", args=[obj.pk])
            )
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload operations."""

    class Meta:
        model = Document
        fields = [
            "title",
            "description",
            "document_type",
            "category",
            "file",
            "community",
            "tags",
            "author",
            "language",
            "confidentiality_level",
            "allowed_user_types",
            "requires_approval",
            "document_date",
            "expiry_date",
            "notes",
        ]

    def create(self, validated_data):
        """Override create to set uploaded_by."""
        request = self.context.get("request")
        if request and request.user:
            validated_data["uploaded_by"] = request.user
        return super().create(validated_data)


class DocumentStatsSerializer(serializers.Serializer):
    """Serializer for document statistics."""

    total_documents = serializers.IntegerField()
    active_documents = serializers.IntegerField()
    featured_documents = serializers.IntegerField()
    by_type = serializers.DictField()
    by_status = serializers.DictField()
    by_confidentiality = serializers.DictField()
    by_category = serializers.DictField()
    by_community = serializers.DictField()
    total_file_size_mb = serializers.FloatField()
    average_file_size_mb = serializers.FloatField()
    most_viewed_documents = serializers.ListField()
    most_downloaded_documents = serializers.ListField()
    recent_uploads = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for document version information."""

    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username", read_only=True
    )
    file_size_mb = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "version",
            "document_type",
            "document_type_display",
            "file_size_mb",
            "uploaded_by_name",
            "is_latest_version",
            "created_at",
            "updated_at",
        ]
