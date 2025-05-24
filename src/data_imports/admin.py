from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import DataImport, ImportLog, FieldMapping, ImportTemplate


@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'import_type', 'status', 'progress_display', 
        'records_summary', 'imported_by', 'created_at'
    ]
    list_filter = ['import_type', 'status', 'created_at', 'imported_by']
    search_fields = ['title', 'description', 'imported_by__username']
    readonly_fields = [
        'progress_percentage', 'success_rate', 'duration', 'file_size',
        'records_total', 'records_processed', 'records_imported', 
        'records_updated', 'records_failed', 'records_skipped',
        'started_at', 'completed_at', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Import Configuration', {
            'fields': ('title', 'import_type', 'description', 'imported_by')
        }),
        ('File Information', {
            'fields': ('file', 'file_size')
        }),
        ('Settings', {
            'fields': ('mapping', 'import_options'),
            'classes': ('collapse',)
        }),
        ('Progress', {
            'fields': (
                'status', 'progress_percentage', 'success_rate', 'duration',
                'started_at', 'completed_at'
            )
        }),
        ('Statistics', {
            'fields': (
                'records_total', 'records_processed', 'records_imported',
                'records_updated', 'records_failed', 'records_skipped'
            )
        }),
        ('Logs', {
            'fields': ('processing_log', 'error_log'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def progress_display(self, obj):
        """Display progress bar."""
        percentage = obj.progress_percentage
        if obj.status == 'completed':
            color = 'green'
        elif obj.status == 'failed':
            color = 'red'
        elif obj.status == 'processing':
            color = 'blue'
        else:
            color = 'gray'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; '
            'text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            percentage, color, percentage
        )
    progress_display.short_description = 'Progress'
    
    def records_summary(self, obj):
        """Display records summary."""
        if obj.records_total:
            return format_html(
                '{} / {} <span style="color: green;">({} imported)</span> '
                '<span style="color: red;">({} failed)</span>',
                obj.records_processed, obj.records_total, 
                obj.records_imported, obj.records_failed
            )
        return 'Not started'
    records_summary.short_description = 'Records'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('imported_by')


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['import_session', 'level', 'message_preview', 'row_number', 'created_at']
    list_filter = ['level', 'import_session__import_type', 'created_at']
    search_fields = ['message', 'import_session__title']
    readonly_fields = ['import_session', 'level', 'message', 'row_number', 'record_data', 'created_at']
    
    def message_preview(self, obj):
        """Show truncated message."""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FieldMapping)
class FieldMappingAdmin(admin.ModelAdmin):
    list_display = ['name', 'import_type', 'is_default', 'created_by', 'created_at']
    list_filter = ['import_type', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'import_type', 'description', 'is_default')
        }),
        ('Mapping Configuration', {
            'fields': ('mapping',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ImportTemplate)
class ImportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'import_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['import_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'import_type', 'description', 'is_active')
        }),
        ('Template File', {
            'fields': ('template_file',)
        }),
        ('Field Configuration', {
            'fields': ('required_fields', 'optional_fields', 'field_descriptions'),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('validation_rules',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)