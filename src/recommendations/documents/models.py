import os
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from communities.models import OBCCommunity

User = get_user_model()


def validate_file_size(value):
    """Validate that file size is not larger than 50MB."""
    file_size = value.size
    if file_size > 50 * 1024 * 1024:  # 50 MB
        raise ValidationError("File size cannot exceed 50 MB.")


def validate_file_mime_type(value):
    """
    Validate file MIME type to ensure it matches allowed types.

    This provides defense-in-depth against malicious files disguised
    with safe extensions. Checks actual file content, not just extension.

    Note: Requires libmagic to be installed on the system.
    Gracefully degrades if libmagic is not available.
    """
    # Try to import magic - gracefully handle if not available
    try:
        import magic
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.warning(
            "python-magic not available. Install libmagic for enhanced file validation. "
            "Ubuntu/Debian: apt-get install libmagic1  |  "
            "macOS: brew install libmagic  |  "
            "Production: Add to Dockerfile"
        )
        return  # Skip MIME validation if magic not available

    # Define allowed MIME types matching our FileExtensionValidator
    ALLOWED_MIME_TYPES = {
        # Documents
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/rtf',
        'application/vnd.oasis.opendocument.text',
        # Spreadsheets
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.oasis.opendocument.spreadsheet',
        # Presentations
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.oasis.opendocument.presentation',
        # Images
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/bmp',
        'image/svg+xml',
        # Videos
        'video/mp4',
        'video/x-msvideo',
        'video/quicktime',
        'video/x-ms-wmv',
        'video/x-flv',
        # Audio
        'audio/mpeg',
        'audio/wav',
        'audio/ogg',
        # Archives (Note: These can contain malware - scan recommended)
        'application/zip',
        'application/x-rar-compressed',
        'application/x-7z-compressed',
        'application/x-rar',
    }

    try:
        # Read first 2KB of file for MIME detection
        file_start = value.read(2048)
        value.seek(0)  # Reset file pointer to beginning

        # Detect MIME type from file content
        mime_type = magic.from_buffer(file_start, mime=True)

        if mime_type not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"File type '{mime_type}' is not allowed. "
                f"The file content does not match any accepted file type."
            )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        # If MIME detection fails, log but don't block
        # (FileExtensionValidator will still provide basic protection)
        logger = logging.getLogger(__name__)
        logger.warning(f"MIME type validation failed: {e}")


def document_upload_path(instance, filename):
    """Generate upload path for documents."""
    # Create directory structure: documents/year/month/community_id/filename
    now = timezone.now()
    community_part = (
        f"community_{instance.community.id}" if instance.community else "general"
    )
    filename_base, file_extension = os.path.splitext(filename)
    safe_filename = slugify(filename_base) + file_extension

    return f"documents/{now.year}/{now.month:02d}/{community_part}/{safe_filename}"


class DocumentCategory(models.Model):
    """Model for categorizing documents."""

    name = models.CharField(
        max_length=100, unique=True, help_text="Name of the document category"
    )

    description = models.TextField(
        blank=True, help_text="Description of what documents belong in this category"
    )

    icon = models.CharField(
        max_length=50, blank=True, help_text="CSS icon class for this category"
    )

    color = models.CharField(
        max_length=7,
        blank=True,
        default="#007bff",
        help_text="Hex color code for this category",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this category is active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents_category"
        ordering = ["name"]
        verbose_name = "Document Category"
        verbose_name_plural = "Document Categories"

    def __str__(self):
        return self.name


class Document(models.Model):
    """Main document model for storing files and metadata."""

    DOCUMENT_TYPES = [
        ("report", "Assessment Report"),
        ("correspondence", "Correspondence"),
        ("profile", "Community Profile"),
        ("policy", "Policy Document"),
        ("moa", "Memorandum of Agreement"),
        ("minutes", "Meeting Minutes"),
        ("presentation", "Presentation"),
        ("photo", "Photograph"),
        ("form", "Form/Template"),
        ("certificate", "Certificate"),
        ("legal", "Legal Document"),
        ("financial", "Financial Document"),
        ("research", "Research Document"),
        ("other", "Other"),
    ]

    CONFIDENTIALITY_LEVELS = [
        ("public", "Public"),
        ("internal", "Internal Use"),
        ("restricted", "Restricted"),
        ("confidential", "Confidential"),
        ("secret", "Secret"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("published", "Published"),
        ("archived", "Archived"),
        ("deleted", "Deleted"),
    ]

    # Basic Information
    title = models.CharField(max_length=255, help_text="Title of the document")

    description = models.TextField(
        blank=True, help_text="Detailed description of the document"
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default="other",
        blank=True,
        help_text="Type of document",
    )

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
        help_text="Category this document belongs to",
    )

    # File Information
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[
            validate_file_size,
            validate_file_mime_type,  # MIME type validation for security
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                    "ppt",
                    "pptx",
                    "txt",
                    "rtf",
                    "odt",
                    "ods",
                    "odp",
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "bmp",
                    "svg",
                    "mp4",
                    "avi",
                    "mov",
                    "wmv",
                    "flv",
                    "mp3",
                    "wav",
                    "ogg",
                    "zip",
                    "rar",
                    "7z",
                ]
            ),
        ],
        help_text="Upload the document file",
    )

    original_filename = models.CharField(
        max_length=255, blank=True, help_text="Original filename provided during upload"
    )

    file_size = models.PositiveIntegerField(
        null=True, blank=True, help_text="File size in bytes"
    )

    file_type = models.CharField(
        max_length=100, blank=True, help_text="MIME type of the file"
    )

    # Relationships
    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
        help_text="Community this document relates to",
    )

    # Metadata
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags for categorization and search",
    )

    author = models.CharField(
        max_length=255,
        blank=True,
        help_text="Author of the document (if different from uploader)",
    )

    language = models.CharField(
        max_length=10, blank=True, default="en", help_text="Language of the document"
    )

    # Version Control
    version = models.CharField(
        max_length=20, default="1.0", help_text="Version number of the document"
    )

    parent_document = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="versions",
        help_text="Parent document if this is a version",
    )

    is_latest_version = models.BooleanField(
        default=True, help_text="Whether this is the latest version"
    )

    # Access Control
    confidentiality_level = models.CharField(
        max_length=20,
        choices=CONFIDENTIALITY_LEVELS,
        default="internal",
        help_text="Confidentiality level of the document",
    )

    allowed_user_types = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated list of user types allowed to access this document",
    )

    requires_approval = models.BooleanField(
        default=False, help_text="Whether accessing this document requires approval"
    )

    # Status and Workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of the document",
    )

    # Audit Trail
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents",
        help_text="User who uploaded this document",
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_documents",
        help_text="User who reviewed this document",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_documents",
        help_text="User who approved this document",
    )

    # Important Dates
    document_date = models.DateField(
        null=True, blank=True, help_text="Date when the document was created/issued"
    )

    expiry_date = models.DateField(
        null=True, blank=True, help_text="Date when this document expires"
    )

    reviewed_at = models.DateTimeField(
        null=True, blank=True, help_text="When this document was last reviewed"
    )

    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="When this document was approved"
    )

    # System Fields
    download_count = models.PositiveIntegerField(
        default=0, help_text="Number of times this document has been downloaded"
    )

    view_count = models.PositiveIntegerField(
        default=0, help_text="Number of times this document has been viewed"
    )

    is_featured = models.BooleanField(
        default=False, help_text="Whether this document is featured"
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this document is active"
    )

    notes = models.TextField(blank=True, help_text="Internal notes about this document")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents_document"
        ordering = ["-created_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        indexes = [
            models.Index(fields=["document_type", "status"]),
            models.Index(fields=["community", "document_type"]),
            models.Index(fields=["confidentiality_level"]),
            models.Index(fields=["is_latest_version", "parent_document"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save to handle file metadata and versioning."""
        if self.file:
            self.file_size = self.file.size
            # Basic file type detection
            if hasattr(self.file, "content_type"):
                self.file_type = self.file.content_type
            if not self.original_filename:
                self.original_filename = os.path.basename(
                    getattr(self.file, "name", "")
                )

        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        """Get the file extension."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ""

    @property
    def file_size_mb(self):
        """Get file size in MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    @property
    def tag_list(self):
        """Get tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
        return []

    @property
    def allowed_user_types_list(self):
        """Get allowed user types as a list."""
        if self.allowed_user_types:
            return [
                user_type.strip()
                for user_type in self.allowed_user_types.split(",")
                if user_type.strip()
            ]
        return []

    @property
    def is_expired(self):
        """Check if document has expired."""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

    @property
    def is_image(self):
        """Check if document is an image file."""
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"]
        return self.file_extension in image_extensions

    @property
    def is_pdf(self):
        """Check if document is a PDF file."""
        return self.file_extension == ".pdf"

    @property
    def is_office_document(self):
        """Check if document is an office document."""
        office_extensions = [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]
        return self.file_extension in office_extensions

    def can_be_accessed_by_user(self, user):
        """Check if user can access this document."""
        if not user.is_authenticated:
            return False

        # Superusers can access everything
        if user.is_superuser:
            return True

        # Check if document is active
        if not self.is_active:
            return False

        # Check user type restrictions
        if self.allowed_user_types:
            if user.user_type not in self.allowed_user_types_list:
                return False

        # Check confidentiality level
        if self.confidentiality_level == "secret" and not user.is_superuser:
            return False

        if self.confidentiality_level == "confidential":
            allowed_types = ["admin", "oobc_staff"]
            if user.user_type not in allowed_types:
                return False

        if self.confidentiality_level == "restricted":
            allowed_types = ["admin", "oobc_staff", "cm_office"]
            if user.user_type not in allowed_types:
                return False

        return True

    def increment_view_count(self):
        """Increment the view count."""
        self.view_count += 1
        self.save(update_fields=["view_count"])

    def increment_download_count(self):
        """Increment the download count."""
        self.download_count += 1
        self.save(update_fields=["download_count"])


class DocumentAccess(models.Model):
    """Model for tracking document access and permissions."""

    ACCESS_TYPES = [
        ("view", "View"),
        ("download", "Download"),
        ("edit", "Edit"),
        ("delete", "Delete"),
        ("share", "Share"),
        ("upload", "Upload"),
    ]

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="access_logs"
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="document_accesses"
    )

    access_type = models.CharField(
        max_length=20, choices=ACCESS_TYPES, help_text="Type of access performed"
    )

    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_document_accesses",
        help_text="User who granted this access, when applicable",
    )

    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of the user"
    )

    user_agent = models.TextField(blank=True, help_text="User agent string")

    notes = models.TextField(blank=True, help_text="Additional notes about the access")

    is_active = models.BooleanField(
        default=True, help_text="Whether this access grant is currently active"
    )

    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "documents_access"
        ordering = ["-accessed_at"]
        verbose_name = "Document Access"
        verbose_name_plural = "Document Accesses"
        indexes = [
            models.Index(fields=["document", "access_type"]),
            models.Index(fields=["user", "accessed_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} {self.access_type} {self.document.title}"


class DocumentComment(models.Model):
    """Model for comments on documents."""

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="comments"
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="document_comments"
    )

    comment = models.TextField(help_text="Comment text")

    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    is_internal = models.BooleanField(
        default=False, help_text="Whether this is an internal comment"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents_comment"
        ordering = ["created_at"]
        verbose_name = "Document Comment"
        verbose_name_plural = "Document Comments"

    def __str__(self):
        return f"Comment by {self.author.username} on {self.document.title}"

    @property
    def author(self):
        return self.user

    @author.setter
    def author(self, value):
        self.user = value

    @property
    def content(self):
        return self.comment

    @content.setter
    def content(self, value):
        self.comment = value
