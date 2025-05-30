from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from django.utils.safestring import mark_safe
from .models import (
    AssessmentCategory, Assessment, AssessmentTeamMember,
    Survey, SurveyQuestion, SurveyResponse, MappingActivity,
    NeedsCategory, Need, NeedsPrioritization, NeedsPrioritizationItem,
    GeographicDataLayer, MapVisualization, SpatialDataPoint,
    BaselineStudy, BaselineStudyTeamMember, BaselineDataCollection, BaselineIndicator,
    WorkshopActivity, WorkshopSession, WorkshopParticipant, WorkshopOutput, MANAReport
)


@admin.register(AssessmentCategory)
class AssessmentCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Assessment Categories."""
    
    list_display = [
        'name', 'category_type', 'colored_icon', 'is_active', 
        'assessments_count', 'created_at'
    ]
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category_type', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def colored_icon(self, obj):
        """Display colored icon for the category."""
        if obj.color and obj.icon:
            return format_html(
                '<span style="color: {}"><i class="{}"></i> {}</span>',
                obj.color, obj.icon, obj.icon
            )
        elif obj.color:
            return format_html(
                '<span style="color: {}">●</span>',
                obj.color
            )
        return '-'
    colored_icon.short_description = 'Icon'
    
    def assessments_count(self, obj):
        """Count of assessments in this category."""
        count = obj.assessment_set.count()
        if count > 0:
            url = reverse('admin:mana_assessment_changelist')
            return format_html(
                '<a href="{}?category__id__exact={}">{} assessments</a>',
                url, obj.id, count
            )
        return '0 assessments'
    assessments_count.short_description = 'Assessments'


class AssessmentTeamMemberInline(admin.TabularInline):
    """Inline for assessment team members."""
    model = AssessmentTeamMember
    extra = 1
    fields = ['user', 'role', 'assigned_date', 'is_active', 'notes']
    autocomplete_fields = ['user']


class SurveyInline(admin.TabularInline):
    """Inline for surveys within assessments."""
    model = Survey
    extra = 0
    fields = ['title', 'survey_type', 'status', 'target_respondents', 'actual_respondents']
    readonly_fields = ['actual_respondents']
    show_change_link = True


class MappingActivityInline(admin.TabularInline):
    """Inline for mapping activities within assessments."""
    model = MappingActivity
    extra = 0
    fields = ['title', 'mapping_type', 'status', 'start_date', 'end_date']
    show_change_link = True


class WorkshopActivityInline(admin.TabularInline):
    """Inline for workshop activities within assessments."""
    model = WorkshopActivity
    extra = 0
    fields = ['title', 'workshop_type', 'workshop_day', 'status', 'scheduled_date', 'duration_hours']
    show_change_link = True
    ordering = ['workshop_day', 'start_time']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin interface for Assessments."""
    
    list_display = [
        'title', 'community_link', 'category', 'status_badge', 'priority_badge',
        'progress_bar', 'lead_assessor', 'planned_dates', 'is_overdue_indicator'
    ]
    list_filter = [
        'status', 'priority', 'category', 'planned_start_date', 
        'actual_start_date', 'created_at'
    ]
    search_fields = ['title', 'description', 'community__barangay__name', 'objectives']
    date_hierarchy = 'planned_start_date'
    ordering = ['-created_at']
    autocomplete_fields = ['community', 'lead_assessor', 'created_by']
    readonly_fields = [
        'id', 'duration_days', 'is_overdue', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description', 'objectives')
        }),
        ('Location and Community', {
            'fields': ('community', 'location_details')
        }),
        ('Management', {
            'fields': ('status', 'priority', 'progress_percentage', 'lead_assessor')
        }),
        ('Timeline', {
            'fields': (
                ('planned_start_date', 'planned_end_date'),
                ('actual_start_date', 'actual_end_date'),
                'duration_days', 'is_overdue'
            )
        }),
        ('Budget', {
            'fields': ('estimated_budget', 'actual_budget'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('key_findings', 'recommendations', 'impact_level'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AssessmentTeamMemberInline, SurveyInline, MappingActivityInline, WorkshopActivityInline]
    
    actions = ['mark_as_data_collection', 'mark_as_completed', 'export_to_csv']
    
    def community_link(self, obj):
        """Link to community admin page."""
        url = reverse('admin:communities_obccommunity_change', args=[obj.community.pk])
        return format_html('<a href="{}">{}</a>', url, obj.community.barangay.name)
    community_link.short_description = 'Community'
    community_link.admin_order_field = 'community__barangay__name'
    
    def status_badge(self, obj):
        """Status with color coding."""
        colors = {
            'planning': 'gray',
            'preparation': 'orange',
            'data_collection': 'blue',
            'analysis': 'purple',
            'reporting': 'yellow',
            'completed': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        """Priority with color coding."""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def progress_bar(self, obj):
        """Visual progress bar."""
        percentage = obj.progress_percentage
        color = '#28a745' if percentage >= 75 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 15px; border-radius: 3px; '
            'text-align: center; color: white; font-size: 10px; line-height: 15px;">{} %</div>'
            '</div>',
            percentage, color, percentage
        )
    progress_bar.short_description = 'Progress'
    
    def planned_dates(self, obj):
        """Display planned date range."""
        if obj.planned_start_date and obj.planned_end_date:
            return f"{obj.planned_start_date} to {obj.planned_end_date}"
        return '-'
    planned_dates.short_description = 'Planned Dates'
    
    def is_overdue_indicator(self, obj):
        """Overdue indicator."""
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠ Overdue</span>')
        return format_html('<span style="color: green;">✓ On track</span>')
    is_overdue_indicator.short_description = 'Status'
    
    def mark_as_data_collection(self, request, queryset):
        """Bulk action to mark assessments as data collection."""
        updated = queryset.update(status='data_collection')
        self.message_user(request, f'{updated} assessments marked as data collection.')
    mark_as_data_collection.short_description = "Mark as Data Collection"
    
    def mark_as_completed(self, request, queryset):
        """Bulk action to mark assessments as completed."""
        updated = queryset.update(status='completed', progress_percentage=100)
        self.message_user(request, f'{updated} assessments marked as completed.')
    mark_as_completed.short_description = "Mark as Completed"


class SurveyQuestionInline(admin.TabularInline):
    """Inline for survey questions."""
    model = SurveyQuestion
    extra = 1
    fields = ['order', 'question_text', 'question_type', 'is_required', 'choices']
    ordering = ['order']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """Admin interface for Surveys."""
    
    list_display = [
        'title', 'assessment_link', 'survey_type', 'status_badge',
        'completion_progress', 'questions_count', 'duration_info'
    ]
    list_filter = ['survey_type', 'status', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'assessment__title']
    date_hierarchy = 'start_date'
    autocomplete_fields = ['assessment', 'created_by']
    readonly_fields = ['actual_respondents', 'completion_rate', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'assessment', 'survey_type', 'description', 'status')
        }),
        ('Target and Progress', {
            'fields': (
                ('target_respondents', 'actual_respondents'),
                'completion_rate'
            )
        }),
        ('Timeline', {
            'fields': (('start_date', 'end_date'), 'estimated_duration_minutes')
        }),
        ('Configuration', {
            'fields': ('questions_count',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SurveyQuestionInline]
    
    def assessment_link(self, obj):
        """Link to assessment admin page."""
        url = reverse('admin:mana_assessment_change', args=[obj.assessment.pk])
        return format_html('<a href="{}">{}</a>', url, obj.assessment.title)
    assessment_link.short_description = 'Assessment'
    
    def status_badge(self, obj):
        """Status with color coding."""
        colors = {
            'draft': 'gray',
            'active': 'blue',
            'paused': 'orange',
            'completed': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def completion_progress(self, obj):
        """Visual completion progress."""
        rate = obj.completion_rate
        color = '#28a745' if rate >= 100 else '#ffc107' if rate >= 75 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 15px; border-radius: 3px; '
            'text-align: center; color: white; font-size: 10px; line-height: 15px;">{:.0f}%</div>'
            '</div>',
            min(rate, 100), color, rate
        )
    completion_progress.short_description = 'Completion'
    
    def duration_info(self, obj):
        """Duration information."""
        return f"{obj.estimated_duration_minutes} min"
    duration_info.short_description = 'Duration'


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    """Admin interface for Survey Questions."""
    
    list_display = ['question_text_short', 'survey_link', 'question_type', 'order', 'is_required']
    list_filter = ['question_type', 'is_required', 'survey__survey_type']
    search_fields = ['question_text', 'survey__title']
    ordering = ['survey', 'order']
    autocomplete_fields = ['survey']
    
    def question_text_short(self, obj):
        """Shortened question text."""
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'
    
    def survey_link(self, obj):
        """Link to survey admin page."""
        url = reverse('admin:mana_survey_change', args=[obj.survey.pk])
        return format_html('<a href="{}">{}</a>', url, obj.survey.title)
    survey_link.short_description = 'Survey'


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    """Admin interface for Survey Responses."""
    
    list_display = [
        'survey_link', 'respondent_name', 'collected_by', 'collection_date',
        'validation_status', 'collection_location'
    ]
    list_filter = [
        'is_validated', 'collection_date', 'survey__survey_type', 'collected_by'
    ]
    search_fields = ['respondent_name', 'survey__title', 'collection_location']
    date_hierarchy = 'collection_date'
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['survey', 'collected_by', 'validated_by']
    
    fieldsets = (
        ('Survey Information', {
            'fields': ('survey', 'collected_by', 'collection_date', 'collection_location')
        }),
        ('Respondent Information', {
            'fields': ('respondent_name', 'respondent_contact', 'demographic_info')
        }),
        ('Responses', {
            'fields': ('responses',)
        }),
        ('Validation', {
            'fields': (
                'is_validated', 'validated_by', 'validation_date', 'validation_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def survey_link(self, obj):
        """Link to survey admin page."""
        url = reverse('admin:mana_survey_change', args=[obj.survey.pk])
        return format_html('<a href="{}">{}</a>', url, obj.survey.title)
    survey_link.short_description = 'Survey'
    
    def validation_status(self, obj):
        """Validation status indicator."""
        if obj.is_validated:
            return format_html('<span style="color: green;">✓ Validated</span>')
        return format_html('<span style="color: orange;">⚠ Pending</span>')
    validation_status.short_description = 'Validation'


@admin.register(MappingActivity)
class MappingActivityAdmin(admin.ModelAdmin):
    """Admin interface for Mapping Activities."""
    
    list_display = [
        'title', 'assessment_link', 'mapping_type', 'status_badge',
        'date_range', 'team_size', 'has_coordinates'
    ]
    list_filter = ['mapping_type', 'status', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'assessment__title', 'coverage_area']
    date_hierarchy = 'start_date'
    autocomplete_fields = ['assessment', 'created_by']
    filter_horizontal = ['mapping_team']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'assessment', 'mapping_type', 'description', 'status')
        }),
        ('Geographic Coverage', {
            'fields': ('coverage_area', 'coordinates')
        }),
        ('Timeline', {
            'fields': (('start_date', 'end_date'),)
        }),
        ('Team and Methodology', {
            'fields': ('mapping_team', 'methodology', 'tools_used')
        }),
        ('Results', {
            'fields': ('findings', 'map_outputs'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def assessment_link(self, obj):
        """Link to assessment admin page."""
        url = reverse('admin:mana_assessment_change', args=[obj.assessment.pk])
        return format_html('<a href="{}">{}</a>', url, obj.assessment.title)
    assessment_link.short_description = 'Assessment'
    
    def status_badge(self, obj):
        """Status with color coding."""
        colors = {
            'planning': 'gray',
            'in_progress': 'blue',
            'review': 'orange',
            'completed': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def date_range(self, obj):
        """Date range display."""
        return f"{obj.start_date} to {obj.end_date}"
    date_range.short_description = 'Date Range'
    
    def team_size(self, obj):
        """Team size indicator."""
        count = obj.mapping_team.count()
        return f"{count} members"
    team_size.short_description = 'Team Size'
    
    def has_coordinates(self, obj):
        """Coordinates indicator."""
        if obj.coordinates:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_coordinates.short_description = 'Coordinates'


# Register team member model separately if needed
@admin.register(AssessmentTeamMember)
class AssessmentTeamMemberAdmin(admin.ModelAdmin):
    """Admin interface for Assessment Team Members."""
    
    list_display = ['user', 'assessment_link', 'role', 'assigned_date', 'is_active']
    list_filter = ['role', 'assigned_date', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'assessment__title']
    autocomplete_fields = ['assessment', 'user']
    
    def assessment_link(self, obj):
        """Link to assessment admin page."""
        url = reverse('admin:mana_assessment_change', args=[obj.assessment.pk])
        return format_html('<a href="{}">{}</a>', url, obj.assessment.title)
    assessment_link.short_description = 'Assessment'


@admin.register(NeedsCategory)
class NeedsCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Needs Categories."""
    
    list_display = [
        'name', 'sector', 'colored_icon', 'weight_factor', 'is_active', 'needs_count'
    ]
    list_filter = ['sector', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['sector', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    def colored_icon(self, obj):
        """Display colored icon for the category."""
        if obj.color and obj.icon:
            return format_html(
                '<span style="color: {}"><i class="{}"></i> {}</span>',
                obj.color, obj.icon, obj.icon
            )
        elif obj.color:
            return format_html(
                '<span style="color: {}">●</span>',
                obj.color
            )
        return '-'
    colored_icon.short_description = 'Icon'
    
    def needs_count(self, obj):
        """Count of needs in this category."""
        count = obj.needs.count()
        if count > 0:
            url = reverse('admin:mana_need_changelist')
            return format_html(
                '<a href="{}?category__id__exact={}">{} needs</a>',
                url, obj.id, count
            )
        return '0 needs'
    needs_count.short_description = 'Needs'


@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    """Admin interface for Community Needs."""
    
    list_display = [
        'title', 'community_link', 'category', 'urgency_badge', 'impact_badge',
        'priority_score', 'status_badge', 'validation_status', 'affected_population'
    ]
    list_filter = [
        'urgency_level', 'impact_severity', 'feasibility', 'status', 
        'category', 'is_validated', 'created_at'
    ]
    search_fields = ['title', 'description', 'community__barangay__name', 'evidence_sources']
    date_hierarchy = 'created_at'
    ordering = ['-priority_score', '-impact_severity', 'title']
    autocomplete_fields = ['community', 'assessment', 'category', 'identified_by', 'validated_by']
    readonly_fields = ['priority_score', 'created_at', 'updated_at']
    
    def community_link(self, obj):
        """Link to community admin page."""
        url = reverse('admin:communities_obccommunity_change', args=[obj.community.pk])
        return format_html('<a href="{}">{}</a>', url, obj.community.barangay.name)
    community_link.short_description = 'Community'
    
    def urgency_badge(self, obj):
        """Urgency level with color coding."""
        colors = {
            'immediate': '#dc3545',
            'short_term': '#fd7e14',
            'medium_term': '#ffc107',
            'long_term': '#28a745',
        }
        color = colors.get(obj.urgency_level, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_urgency_level_display()
        )
    urgency_badge.short_description = 'Urgency'
    
    def impact_badge(self, obj):
        """Impact severity with color coding."""
        colors = ['#28a745', '#6f9936', '#ffc107', '#fd7e14', '#dc3545']
        color = colors[obj.impact_severity - 1] if 1 <= obj.impact_severity <= 5 else '#6c757d'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">Impact {}</span>',
            color, obj.impact_severity
        )
    impact_badge.short_description = 'Impact'
    
    def status_badge(self, obj):
        """Status with color coding."""
        colors = {
            'identified': 'gray',
            'validated': 'blue',
            'prioritized': 'purple',
            'planned': 'orange',
            'in_progress': 'yellow',
            'completed': 'green',
            'deferred': 'brown',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def validation_status(self, obj):
        """Validation status indicator."""
        if obj.is_validated:
            return format_html('<span style="color: green;">✓ Validated</span>')
        return format_html('<span style="color: orange;">⚠ Pending</span>')
    validation_status.short_description = 'Validation'


# Workshop-related Admin Classes

class WorkshopSessionInline(admin.TabularInline):
    """Inline for workshop sessions."""
    model = WorkshopSession
    extra = 1
    fields = ['session_title', 'session_type', 'session_order', 'start_time', 'end_time', 'facilitator']
    autocomplete_fields = ['facilitator']
    ordering = ['session_order']


class WorkshopParticipantInline(admin.TabularInline):
    """Inline for workshop participants."""
    model = WorkshopParticipant
    extra = 3
    fields = ['name', 'participant_type', 'gender', 'age_group', 'organization', 'attendance_status']
    ordering = ['participant_type', 'name']


class WorkshopOutputInline(admin.TabularInline):
    """Inline for workshop outputs."""
    model = WorkshopOutput
    extra = 1
    fields = ['output_type', 'title', 'description', 'created_by']
    autocomplete_fields = ['created_by']
    readonly_fields = ['created_at']


@admin.register(WorkshopActivity)
class WorkshopActivityAdmin(admin.ModelAdmin):
    """Admin interface for Workshop Activities."""
    
    list_display = [
        'title', 'assessment_link', 'workshop_type', 'workshop_day', 'status_badge',
        'scheduled_date', 'duration_hours', 'participants_progress', 'outputs_count'
    ]
    list_filter = [
        'workshop_type', 'workshop_day', 'status', 'scheduled_date', 'created_at'
    ]
    search_fields = ['title', 'description', 'assessment__title', 'methodology']
    date_hierarchy = 'scheduled_date'
    ordering = ['workshop_day', 'start_time']
    autocomplete_fields = ['assessment', 'created_by']
    filter_horizontal = ['facilitators']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'assessment', 'workshop_type', 'workshop_day', 'description')
        }),
        ('Schedule', {
            'fields': (
                ('scheduled_date', 'status'),
                ('start_time', 'end_time', 'duration_hours')
            )
        }),
        ('Participants', {
            'fields': (('target_participants', 'actual_participants'),)
        }),
        ('Workshop Details', {
            'fields': ('methodology', 'materials_needed', 'expected_outputs')
        }),
        ('Team', {
            'fields': ('facilitators',)
        }),
        ('Results', {
            'fields': ('key_findings', 'recommendations', 'challenges_encountered'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [WorkshopSessionInline, WorkshopParticipantInline, WorkshopOutputInline]
    
    def assessment_link(self, obj):
        """Link to assessment admin page."""
        url = reverse('admin:mana_assessment_change', args=[obj.assessment.pk])
        return format_html('<a href="{}">{}</a>', url, obj.assessment.title)
    assessment_link.short_description = 'Assessment'
    
    def status_badge(self, obj):
        """Status with color coding."""
        colors = {
            'planned': 'gray',
            'in_progress': 'blue',
            'completed': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def participants_progress(self, obj):
        """Participants progress indicator."""
        actual = obj.actual_participants
        target = obj.target_participants
        percentage = (actual / target * 100) if target > 0 else 0
        color = '#28a745' if percentage >= 90 else '#ffc107' if percentage >= 70 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/{} ({:.0f}%)</span>',
            color, actual, target, percentage
        )
    participants_progress.short_description = 'Participants'
    
    def outputs_count(self, obj):
        """Count of workshop outputs."""
        count = obj.outputs.count()
        if count > 0:
            return format_html('<span style="color: green;">{} outputs</span>', count)
        return format_html('<span style="color: orange;">No outputs</span>')
    outputs_count.short_description = 'Outputs'


@admin.register(WorkshopSession)
class WorkshopSessionAdmin(admin.ModelAdmin):
    """Admin interface for Workshop Sessions."""
    
    list_display = [
        'session_title', 'workshop_link', 'session_type', 'session_order',
        'time_range', 'facilitator', 'has_outputs'
    ]
    list_filter = ['session_type', 'workshop__workshop_type', 'workshop__workshop_day']
    search_fields = ['session_title', 'objectives', 'workshop__title']
    ordering = ['workshop', 'session_order']
    autocomplete_fields = ['workshop', 'facilitator']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('session_title', 'workshop', 'session_type', 'session_order')
        }),
        ('Schedule', {
            'fields': (('start_time', 'end_time'),)
        }),
        ('Content', {
            'fields': ('objectives', 'methodology')
        }),
        ('Team', {
            'fields': ('facilitator',)
        }),
        ('Results', {
            'fields': ('outputs', 'notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def workshop_link(self, obj):
        """Link to workshop admin page."""
        url = reverse('admin:mana_workshopactivity_change', args=[obj.workshop.pk])
        return format_html('<a href="{}">{}</a>', url, obj.workshop.title)
    workshop_link.short_description = 'Workshop'
    
    def time_range(self, obj):
        """Time range display."""
        return f"{obj.start_time} - {obj.end_time}"
    time_range.short_description = 'Time'
    
    def has_outputs(self, obj):
        """Outputs indicator."""
        if obj.outputs:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: orange;">✗ No</span>')
    has_outputs.short_description = 'Outputs'


@admin.register(WorkshopParticipant)
class WorkshopParticipantAdmin(admin.ModelAdmin):
    """Admin interface for Workshop Participants."""
    
    list_display = [
        'name', 'workshop_link', 'participant_type', 'gender', 'age_group',
        'organization', 'attendance_badge'
    ]
    list_filter = [
        'participant_type', 'gender', 'age_group', 'attendance_status',
        'workshop__workshop_type', 'workshop__workshop_day'
    ]
    search_fields = ['name', 'organization', 'contact_info', 'workshop__title']
    ordering = ['workshop', 'participant_type', 'name']
    autocomplete_fields = ['workshop']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'workshop', 'participant_type')
        }),
        ('Demographics', {
            'fields': (('gender', 'age_group'), 'organization')
        }),
        ('Contact', {
            'fields': ('contact_info',)
        }),
        ('Participation', {
            'fields': ('attendance_status', 'participation_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def workshop_link(self, obj):
        """Link to workshop admin page."""
        url = reverse('admin:mana_workshopactivity_change', args=[obj.workshop.pk])
        return format_html('<a href="{}">{}</a>', url, obj.workshop.title)
    workshop_link.short_description = 'Workshop'
    
    def attendance_badge(self, obj):
        """Attendance status with color coding."""
        colors = {
            'attended': 'green',
            'partial': 'orange',
            'absent': 'red',
        }
        color = colors.get(obj.attendance_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_attendance_status_display()
        )
    attendance_badge.short_description = 'Attendance'


@admin.register(WorkshopOutput)
class WorkshopOutputAdmin(admin.ModelAdmin):
    """Admin interface for Workshop Outputs."""
    
    list_display = [
        'title', 'workshop_link', 'output_type', 'created_by', 'created_at', 'has_file'
    ]
    list_filter = [
        'output_type', 'workshop__workshop_type', 'workshop__workshop_day', 'created_at'
    ]
    search_fields = ['title', 'description', 'content', 'workshop__title']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    autocomplete_fields = ['workshop', 'created_by', 'created_by_session']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'workshop', 'output_type', 'description')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('File', {
            'fields': ('file_path',)
        }),
        ('Session Link', {
            'fields': ('created_by_session',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def workshop_link(self, obj):
        """Link to workshop admin page."""
        url = reverse('admin:mana_workshopactivity_change', args=[obj.workshop.pk])
        return format_html('<a href="{}">{}</a>', url, obj.workshop.title)
    workshop_link.short_description = 'Workshop'
    
    def has_file(self, obj):
        """File attachment indicator."""
        if obj.file_path:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: orange;">✗ No</span>')
    has_file.short_description = 'File'


@admin.register(MANAReport)
class MANAReportAdmin(admin.ModelAdmin):
    """Admin interface for MANA Reports."""
    
    list_display = [
        'title', 'assessment_link', 'report_status_badge', 'created_by',
        'validation_date', 'submission_date', 'created_at'
    ]
    list_filter = [
        'report_status', 'validation_date', 'submission_date', 'created_at'
    ]
    search_fields = [
        'title', 'executive_summary', 'assessment__title', 'assessment__community__barangay__name'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    autocomplete_fields = ['assessment', 'created_by', 'submitted_by']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'assessment', 'report_status')
        }),
        ('Executive Summary', {
            'fields': ('executive_summary',)
        }),
        ('Context and Background', {
            'fields': ('context_background', 'methodology'),
            'classes': ('collapse',)
        }),
        ('Findings by Sector', {
            'fields': (
                'social_development_findings',
                'economic_development_findings', 
                'cultural_development_findings',
                'rights_protection_findings'
            ),
            'classes': ('collapse',)
        }),
        ('Priority Issues and Recommendations', {
            'fields': ('priority_issues', 'policy_recommendations'),
            'classes': ('collapse',)
        }),
        ('Program Development', {
            'fields': (
                'program_development_opportunities',
                'strategic_approaches',
                'stakeholder_roles',
                'resource_requirements',
                'monitoring_evaluation'
            ),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': (
                ('validation_date', 'validation_participants'),
                'validation_feedback'
            ),
            'classes': ('collapse',)
        }),
        ('Submission', {
            'fields': (('submission_date', 'submitted_by'),),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_review', 'mark_as_final', 'mark_as_submitted']
    
    def assessment_link(self, obj):
        """Link to assessment admin page."""
        url = reverse('admin:mana_assessment_change', args=[obj.assessment.pk])
        return format_html('<a href="{}">{}</a>', url, obj.assessment.title)
    assessment_link.short_description = 'Assessment'
    
    def report_status_badge(self, obj):
        """Status with color coding."""
        colors = {
            'draft': 'gray',
            'review': 'orange',
            'validation': 'blue',
            'final': 'green',
            'submitted': 'purple',
        }
        color = colors.get(obj.report_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_report_status_display()
        )
    report_status_badge.short_description = 'Status'
    
    def mark_as_review(self, request, queryset):
        """Bulk action to mark reports as under review."""
        updated = queryset.update(report_status='review')
        self.message_user(request, f'{updated} reports marked as under review.')
    mark_as_review.short_description = "Mark as Under Review"
    
    def mark_as_final(self, request, queryset):
        """Bulk action to mark reports as final."""
        updated = queryset.update(report_status='final')
        self.message_user(request, f'{updated} reports marked as final.')
    mark_as_final.short_description = "Mark as Final"
    
    def mark_as_submitted(self, request, queryset):
        """Bulk action to mark reports as submitted."""
        updated = queryset.update(report_status='submitted')
        self.message_user(request, f'{updated} reports marked as submitted.')
    mark_as_submitted.short_description = "Mark as Submitted"
