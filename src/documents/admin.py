from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import DocumentCategory, Document, DocumentAccess, DocumentComment


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Document Category model."""
    
    list_display = ('name', 'description_short', 'document_count', 'color_display', 
                   'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Display', {
            'fields': ('icon', 'color')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        """Display shortened description."""
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return '-'
    description_short.short_description = 'Description'
    
    def document_count(self, obj):
        """Display number of documents in this category."""
        count = obj.documents.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:documents_document_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} documents</a>', url, count)
        return '0 documents'
    document_count.short_description = 'Documents'
    
    def color_display(self, obj):
        """Display color swatch."""
        if obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 2px 8px; border-radius: 3px; color: white;">{}</span>',
                obj.color, obj.color
            )
        return '-'
    color_display.short_description = 'Color'


class DocumentCommentInline(admin.TabularInline):
    """Inline admin for document comments."""
    model = DocumentComment
    extra = 0
    fields = ('user', 'comment', 'is_internal', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


class DocumentAccessInline(admin.TabularInline):
    """Inline admin for document access logs."""
    model = DocumentAccess
    extra = 0
    fields = ('user', 'access_type', 'ip_address', 'accessed_at')
    readonly_fields = ('accessed_at',)
    ordering = ('-accessed_at',)
    max_num = 10  # Limit to last 10 access logs


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model."""
    
    list_display = ('title', 'document_type', 'category', 'community', 'confidentiality_level', 
                   'status', 'file_info', 'uploaded_by', 'view_count', 'download_count', 
                   'is_latest_version', 'created_at')
    list_filter = ('document_type', 'confidentiality_level', 'status', 'is_latest_version',
                   'category', 'created_at', 'is_featured', 'is_active')
    search_fields = ('title', 'description', 'tags', 'author', 'uploaded_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'file_type', 'file_extension', 'file_size_mb', 
                      'view_count', 'download_count', 'created_at', 'updated_at')
    filter_horizontal = ()
    
    inlines = [DocumentCommentInline, DocumentAccessInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('title', 'document_type'),
                ('category', 'community'),
                'description',
                ('author', 'language')
            )
        }),
        ('File Information', {
            'fields': (
                'file',
                ('file_size', 'file_type', 'file_extension', 'file_size_mb')
            )
        }),
        ('Metadata & Tags', {
            'fields': (
                'tags',
                ('document_date', 'expiry_date')
            )
        }),
        ('Version Control', {
            'fields': (
                ('version', 'parent_document'),
                'is_latest_version'
            ),
            'classes': ('collapse',)
        }),
        ('Access Control', {
            'fields': (
                'confidentiality_level',
                'allowed_user_types',
                'requires_approval'
            )
        }),
        ('Status & Workflow', {
            'fields': (
                'status',
                ('uploaded_by', 'reviewed_by', 'approved_by'),
                ('reviewed_at', 'approved_at')
            )
        }),
        ('Statistics', {
            'fields': (
                ('view_count', 'download_count'),
                ('is_featured', 'is_active')
            )
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_info(self, obj):
        """Display file information with download link."""
        if obj.file:
            file_icon = self.get_file_icon(obj)
            download_url = reverse('admin:document_download', args=[obj.pk])
            return format_html(
                '{} <a href="{}" target="_blank">{}</a><br>'
                '<small>Size: {} MB | Type: {}</small>',
                file_icon,
                download_url,
                obj.file.name.split('/')[-1],  # Just filename
                obj.file_size_mb,
                obj.file_extension.upper()
            )
        return '-'
    file_info.short_description = 'File'
    
    def get_file_icon(self, obj):
        """Get appropriate file icon based on file type."""
        if obj.is_pdf:
            return '📄'
        elif obj.is_image:
            return '🖼️'
        elif obj.is_office_document:
            return '📊'
        else:
            return '📎'
    
    def colored_status(self, obj):
        """Display status with color coding."""
        colors = {
            'draft': 'gray',
            'under_review': 'orange',
            'approved': 'green',
            'published': 'blue',
            'archived': 'brown',
            'deleted': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    colored_status.short_description = 'Status'
    
    def colored_confidentiality(self, obj):
        """Display confidentiality level with color coding."""
        colors = {
            'public': 'green',
            'internal': 'blue',
            'restricted': 'orange',
            'confidential': 'red',
            'secret': 'darkred',
        }
        color = colors.get(obj.confidentiality_level, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_confidentiality_level_display()
        )
    colored_confidentiality.short_description = 'Confidentiality'
    
    actions = ['mark_as_approved', 'mark_as_archived', 'mark_as_featured', 'export_documents']
    
    def mark_as_approved(self, request, queryset):
        """Mark selected documents as approved."""
        from django.utils import timezone
        updated = queryset.update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} documents marked as approved.')
    mark_as_approved.short_description = "Mark as Approved"
    
    def mark_as_archived(self, request, queryset):
        """Mark selected documents as archived."""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} documents marked as archived.')
    mark_as_archived.short_description = "Mark as Archived"
    
    def mark_as_featured(self, request, queryset):
        """Mark selected documents as featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} documents marked as featured.')
    mark_as_featured.short_description = "Mark as Featured"
    
    def export_documents(self, request, queryset):
        """Export document list as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="documents.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Type', 'Category', 'Community', 'Status', 
            'Confidentiality', 'Uploaded By', 'Created At', 'File Size (MB)'
        ])
        
        for doc in queryset:
            writer.writerow([
                doc.title,
                doc.get_document_type_display(),
                doc.category.name if doc.category else '',
                doc.community.name if doc.community else '',
                doc.get_status_display(),
                doc.get_confidentiality_level_display(),
                doc.uploaded_by.username if doc.uploaded_by else '',
                doc.created_at.strftime('%Y-%m-%d %H:%M'),
                doc.file_size_mb
            ])
        
        return response
    export_documents.short_description = "Export selected documents"
    
    def get_urls(self):
        """Add custom URLs for file operations."""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'download/<int:document_id>/',
                self.admin_site.admin_view(self.download_document),
                name='document_download'
            ),
        ]
        return custom_urls + urls
    
    def download_document(self, request, document_id):
        """Handle document download with access logging."""
        document = get_object_or_404(Document, pk=document_id)
        
        # Check if user can access this document
        if not document.can_be_accessed_by_user(request.user):
            return HttpResponse('Access Denied', status=403)
        
        # Log the access
        DocumentAccess.objects.create(
            document=document,
            user=request.user,
            access_type='download',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Increment download count
        document.increment_download_count()
        
        # Serve the file
        response = HttpResponse(
            document.file.read(),
            content_type=document.file_type or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{document.file.name.split("/")[-1]}"'
        return response
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@admin.register(DocumentAccess)
class DocumentAccessAdmin(admin.ModelAdmin):
    """Admin interface for Document Access model."""
    
    list_display = ('document', 'user', 'access_type', 'ip_address', 'accessed_at')
    list_filter = ('access_type', 'accessed_at', 'document__document_type',
                   'document__confidentiality_level')
    search_fields = ('document__title', 'user__username', 'ip_address')
    ordering = ('-accessed_at',)
    readonly_fields = ('accessed_at',)
    
    fieldsets = (
        ('Access Information', {
            'fields': (
                ('document', 'user'),
                ('access_type', 'accessed_at'),
                ('ip_address', 'user_agent')
            )
        }),
        ('Additional Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual addition of access logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of access logs."""
        return False


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    """Admin interface for Document Comment model."""
    
    list_display = ('document', 'user', 'comment_preview', 'is_internal', 
                   'parent_comment', 'created_at')
    list_filter = ('is_internal', 'created_at', 'document__document_type')
    search_fields = ('document__title', 'user__username', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Comment Information', {
            'fields': (
                ('document', 'user'),
                'comment',
                ('parent_comment', 'is_internal')
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def comment_preview(self, obj):
        """Display comment preview."""
        if obj.comment:
            return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
        return '-'
    comment_preview.short_description = 'Comment'