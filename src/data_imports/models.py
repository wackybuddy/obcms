import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class DataImport(models.Model):
    """
    Model for tracking data import operations.
    """

    IMPORT_TYPES = [
        ("communities", "OBC Communities"),
        ("stakeholders", "Community Stakeholders"),
        ("assessments", "Assessments"),
        ("needs", "Community Needs"),
        ("organizations", "Organizations"),
        ("administrative", "Administrative Hierarchy"),
        ("baseline_data", "Baseline Study Data"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("partial", "Partially Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Import Configuration
    import_type = models.CharField(
        max_length=20, choices=IMPORT_TYPES, help_text="Type of data being imported"
    )

    title = models.CharField(
        max_length=255, help_text="Descriptive title for this import"
    )

    description = models.TextField(
        blank=True, help_text="Detailed description of the import"
    )

    # File Information
    file = models.FileField(
        upload_to="imports/%Y/%m/",
        validators=[FileExtensionValidator(allowed_extensions=["csv", "xlsx", "xls"])],
        help_text="CSV or Excel file to import",
    )

    file_size = models.PositiveIntegerField(
        null=True, blank=True, help_text="File size in bytes"
    )

    # Import Configuration
    mapping = models.JSONField(
        default=dict,
        blank=True,
        help_text="Field mapping configuration from file columns to model fields",
    )

    import_options = models.JSONField(
        default=dict, blank=True, help_text="Additional import options and settings"
    )

    # Progress Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current status of the import",
    )

    records_total = models.PositiveIntegerField(
        null=True, blank=True, help_text="Total number of records in the file"
    )

    records_processed = models.PositiveIntegerField(
        default=0, help_text="Number of records processed"
    )

    records_imported = models.PositiveIntegerField(
        default=0, help_text="Number of records successfully imported"
    )

    records_updated = models.PositiveIntegerField(
        default=0, help_text="Number of existing records updated"
    )

    records_failed = models.PositiveIntegerField(
        default=0, help_text="Number of records that failed to import"
    )

    records_skipped = models.PositiveIntegerField(
        default=0, help_text="Number of records skipped"
    )

    # Logging and Error Tracking
    error_log = models.TextField(blank=True, help_text="Detailed error log")

    processing_log = models.TextField(
        blank=True, help_text="Processing log with detailed information"
    )

    # Metadata
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="data_imports",
        help_text="User who initiated this import",
    )

    started_at = models.DateTimeField(
        null=True, blank=True, help_text="When processing started"
    )

    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="When processing completed"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "data_imports_import"
        ordering = ["-created_at"]
        verbose_name = "Data Import"
        verbose_name_plural = "Data Imports"

    def __str__(self):
        return f"{self.title} ({self.get_import_type_display()})"

    @property
    def progress_percentage(self):
        """Calculate import progress percentage."""
        if not self.records_total or self.records_total == 0:
            return 0
        return round((self.records_processed / self.records_total) * 100, 1)

    @property
    def success_rate(self):
        """Calculate success rate percentage."""
        if not self.records_processed or self.records_processed == 0:
            return 0
        successful = self.records_imported + self.records_updated
        return round((successful / self.records_processed) * 100, 1)

    @property
    def duration(self):
        """Calculate import duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class ImportLog(models.Model):
    """
    Model for detailed import logging.
    """

    LOG_LEVELS = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("debug", "Debug"),
    ]

    import_session = models.ForeignKey(
        DataImport,
        on_delete=models.CASCADE,
        related_name="logs",
        help_text="Associated import session",
    )

    level = models.CharField(
        max_length=10, choices=LOG_LEVELS, default="info", help_text="Log level"
    )

    message = models.TextField(help_text="Log message")

    row_number = models.PositiveIntegerField(
        null=True, blank=True, help_text="Row number in source file (if applicable)"
    )

    record_data = models.JSONField(
        default=dict, blank=True, help_text="Raw record data that caused the log entry"
    )

    exception_type = models.CharField(
        max_length=255, blank=True, help_text="Exception type (for error logs)"
    )

    exception_details = models.TextField(
        blank=True, help_text="Detailed exception information"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "data_imports_log"
        ordering = ["created_at"]
        verbose_name = "Import Log"
        verbose_name_plural = "Import Logs"

    def __str__(self):
        row_info = f" (Row {self.row_number})" if self.row_number else ""
        return f"{self.get_level_display()}: {self.message[:100]}{row_info}"


class FieldMapping(models.Model):
    """
    Model for storing reusable field mappings.
    """

    name = models.CharField(
        max_length=255, unique=True, help_text="Name for this field mapping"
    )

    import_type = models.CharField(
        max_length=20,
        choices=DataImport.IMPORT_TYPES,
        help_text="Type of data this mapping is for",
    )

    description = models.TextField(blank=True, help_text="Description of this mapping")

    mapping = models.JSONField(help_text="Field mapping configuration")

    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default mapping for this import type",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who created this mapping",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "data_imports_field_mapping"
        ordering = ["import_type", "name"]
        verbose_name = "Field Mapping"
        verbose_name_plural = "Field Mappings"

    def __str__(self):
        default_indicator = " (Default)" if self.is_default else ""
        return f"{self.name} - {self.get_import_type_display()}{default_indicator}"


class ImportTemplate(models.Model):
    """
    Model for import templates with sample data.
    """

    name = models.CharField(max_length=255, help_text="Template name")

    import_type = models.CharField(
        max_length=20,
        choices=DataImport.IMPORT_TYPES,
        help_text="Type of data this template is for",
    )

    description = models.TextField(
        blank=True, help_text="Template description and instructions"
    )

    template_file = models.FileField(
        upload_to="templates/",
        validators=[FileExtensionValidator(allowed_extensions=["csv", "xlsx"])],
        help_text="Template file with sample data and headers",
    )

    required_fields = models.JSONField(
        default=list, help_text="List of required field names"
    )

    optional_fields = models.JSONField(
        default=list, help_text="List of optional field names"
    )

    field_descriptions = models.JSONField(
        default=dict, help_text="Descriptions for each field"
    )

    validation_rules = models.JSONField(
        default=dict, help_text="Validation rules for fields"
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this template is active"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who created this template",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "data_imports_template"
        ordering = ["import_type", "name"]
        verbose_name = "Import Template"
        verbose_name_plural = "Import Templates"

    def __str__(self):
        return f"{self.name} - {self.get_import_type_display()}"
