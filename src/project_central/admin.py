"""
Project Central Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ProjectWorkflow, BudgetApprovalStage, BudgetCeiling, BudgetScenario, Alert


@admin.register(ProjectWorkflow)
class ProjectWorkflowAdmin(admin.ModelAdmin):
    list_display = ['id', 'primary_need', 'current_stage', 'priority_level', 'project_lead', 'is_on_track', 'overall_progress', 'initiated_date']
    list_filter = ['current_stage', 'priority_level', 'is_on_track', 'is_blocked', 'budget_approved']
    search_fields = ['primary_need__title', 'notes', 'blocker_description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'stage_history']


@admin.register(BudgetApprovalStage)
class BudgetApprovalStageAdmin(admin.ModelAdmin):
    list_display = ['ppa', 'stage', 'status', 'approver', 'approved_at', 'created_at']
    list_filter = ['stage', 'status', 'approved_at']
    search_fields = ['ppa__title', 'comments']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['ppa', 'approver']


@admin.register(BudgetCeiling)
class BudgetCeilingAdmin(admin.ModelAdmin):
    list_display = ['name', 'fiscal_year', 'sector', 'funding_source', 'ceiling_amount', 'allocated_amount', 'is_active', 'enforcement_level']
    list_filter = ['fiscal_year', 'sector', 'funding_source', 'is_active', 'enforcement_level']
    search_fields = ['name', 'notes']
    readonly_fields = ['id', 'allocated_amount', 'created_at', 'updated_at']


@admin.register(BudgetScenario)
class BudgetScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'fiscal_year', 'status', 'is_baseline', 'total_budget_envelope', 'created_by', 'created_at']
    list_filter = ['fiscal_year', 'status', 'is_baseline']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'approved_date']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'alert_type', 'severity', 'title', 'is_active', 'is_acknowledged', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_active', 'is_acknowledged', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'acknowledged_at']

    actions = ['mark_acknowledged', 'deactivate_alerts']

    def mark_acknowledged(self, request, queryset):
        for alert in queryset:
            if not alert.is_acknowledged:
                alert.acknowledge(request.user)
        self.message_user(request, f"{queryset.count()} alerts marked as acknowledged.")
    mark_acknowledged.short_description = "Mark selected alerts as acknowledged"

    def deactivate_alerts(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} alerts deactivated.")
    deactivate_alerts.short_description = "Deactivate selected alerts"
