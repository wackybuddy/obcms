"""Admin configuration for budget execution models."""

from decimal import Decimal

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Allotment, Disbursement, DisbursementLineItem, Obligation


def _currency(amount: Decimal) -> str:
    return f"P{amount:,.2f}"


class ObligationInline(admin.TabularInline):
    model = Obligation
    extra = 0
    fields = ['work_item', 'payee', 'amount', 'status', 'obligated_at']
    readonly_fields = ['work_item', 'amount']
    can_delete = False


@admin.register(Allotment)
class AllotmentAdmin(admin.ModelAdmin):
    list_display = [
        'program_budget',
        'quarter_display',
        'amount_display',
        'obligated_display',
        'balance_display',
        'utilization_display',
        'status_badge',
        'released_at',
        'released_by_display',
    ]
    list_filter = ['quarter', 'status', 'released_at']
    search_fields = ['program_budget__monitoring_entry__title', 'notes']
    readonly_fields = [
        'created_at',
        'updated_at',
        'obligated_amount_display',
        'remaining_balance_display',
        'utilization_rate_display',
    ]
    fieldsets = (
        (
            "Allotment Information",
            {'fields': ('program_budget', 'quarter', 'amount', 'status')},
        ),
        (
            "Release Details",
            {'fields': ('released_by', 'released_at', 'notes')},
        ),
        (
            "Financial Summary",
            {
                'fields': (
                    'obligated_amount_display',
                    'remaining_balance_display',
                    'utilization_rate_display',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            "Audit Trail",
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )
    inlines = [ObligationInline]

    def quarter_display(self, obj):
        return obj.get_quarter_display()

    quarter_display.short_description = "Quarter"

    def amount_display(self, obj):
        return _currency(obj.amount)

    amount_display.short_description = "Allotment"

    def obligated_display(self, obj):
        return _currency(obj.get_obligated_amount())

    obligated_display.short_description = "Obligated"

    def balance_display(self, obj):
        balance = obj.get_remaining_balance()
        color = 'green' if balance > 0 else 'red'
        return format_html('<span style="color:{};">{}</span>', color, _currency(balance))

    balance_display.short_description = "Balance"

    def utilization_display(self, obj):
        rate = obj.get_utilization_rate()
        color = 'green' if rate < 80 else 'orange' if rate < 100 else 'red'
        return format_html('<span style="color:{};">{:.1f}%</span>', color, rate)

    utilization_display.short_description = "Utilization"

    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'released': 'blue',
            'partially_utilized': 'orange',
            'fully_utilized': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def released_by_display(self, obj):
        if not obj.released_by:
            return "system"
        return obj.released_by.get_full_name() or obj.released_by.get_username()

    released_by_display.short_description = "Released By"

    def obligated_amount_display(self, obj):
        return _currency(obj.get_obligated_amount())

    obligated_amount_display.short_description = "Total Obligated"

    def remaining_balance_display(self, obj):
        return _currency(obj.get_remaining_balance())

    remaining_balance_display.short_description = "Remaining Balance"

    def utilization_rate_display(self, obj):
        return f"{obj.get_utilization_rate():.2f}%"

    utilization_rate_display.short_description = "Utilization Rate"


class DisbursementInline(admin.TabularInline):
    model = Disbursement
    extra = 0
    fields = ['amount', 'payment_method', 'status', 'disbursed_at', 'reference_number']
    readonly_fields = ['amount']
    can_delete = False


@admin.register(Obligation)
class ObligationAdmin(admin.ModelAdmin):
    list_display = [
        'work_item_display',
        'allotment_link',
        'amount_display',
        'disbursed_display',
        'balance_display',
        'status_badge',
        'obligated_at',
        'payee',
        'obligated_by_display',
    ]
    list_filter = ['status', 'obligated_at']
    search_fields = ['work_item__title', 'payee', 'notes']
    readonly_fields = [
        'created_at',
        'updated_at',
        'disbursed_amount_display',
        'remaining_balance_display',
    ]
    fieldsets = (
        (
            "Obligation Information",
            {
                'fields': (
                    'allotment',
                    'work_item',
                    'payee',
                    'amount',
                    'status',
                    'obligated_by',
                    'obligated_at',
                    'notes',
                )
            },
        ),
        (
            "Financial Summary",
            {
                'fields': ('disbursed_amount_display', 'remaining_balance_display'),
                'classes': ('collapse',),
            },
        ),
        (
            "Audit Trail",
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )
    inlines = [DisbursementInline]

    def work_item_display(self, obj):
        return getattr(obj.work_item, "title", "Unassigned")

    work_item_display.short_description = "Work Item"

    def allotment_link(self, obj):
        url = reverse('admin:budget_execution_allotment_change', args=[obj.allotment.pk])
        return format_html('<a href="{}">{}</a>', url, obj.allotment)

    allotment_link.short_description = "Allotment"

    def amount_display(self, obj):
        return _currency(obj.amount)

    amount_display.short_description = "Obligation"

    def disbursed_display(self, obj):
        return _currency(obj.get_disbursed_amount())

    disbursed_display.short_description = "Disbursed"

    def balance_display(self, obj):
        balance = obj.get_remaining_balance()
        color = 'green' if balance > 0 else 'red'
        return format_html('<span style="color:{};">{}</span>', color, _currency(balance))

    balance_display.short_description = "Balance"

    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'obligated': 'blue',
            'partially_disbursed': 'orange',
            'fully_disbursed': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def disbursed_amount_display(self, obj):
        return _currency(obj.get_disbursed_amount())

    disbursed_amount_display.short_description = "Total Disbursed"

    def remaining_balance_display(self, obj):
        return _currency(obj.get_remaining_balance())

    remaining_balance_display.short_description = "Remaining Balance"

    def obligated_by_display(self, obj):
        if not obj.obligated_by:
            return "system"
        return obj.obligated_by.get_full_name() or obj.obligated_by.get_username()

    obligated_by_display.short_description = "Recorded By"


@admin.register(Disbursement)
class DisbursementAdmin(admin.ModelAdmin):
    list_display = [
        'obligation_link',
        'amount_display',
        'status_badge',
        'payment_method',
        'disbursed_at',
        'disbursed_by_display',
        'reference_number',
    ]
    list_filter = ['payment_method', 'status', 'disbursed_at']
    search_fields = ['reference_number', 'obligation__work_item__title', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            "Disbursement Information",
            {'fields': ('obligation', 'amount', 'status', 'disbursed_at', 'disbursed_by')},
        ),
        (
            "Payment Details",
            {'fields': ('payment_method', 'reference_number')},
        ),
        (
            "Additional Details",
            {'fields': ('notes',), 'classes': ('collapse',)},
        ),
        (
            "Audit Trail",
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )

    def obligation_link(self, obj):
        url = reverse('admin:budget_execution_obligation_change', args=[obj.obligation.pk])
        return format_html('<a href="{}">{}</a>', url, obj.obligation)

    obligation_link.short_description = "Obligation"

    def amount_display(self, obj):
        return _currency(obj.amount)

    amount_display.short_description = "Amount"

    def status_badge(self, obj):
        colors = {
            'processing': 'orange',
            'paid': 'green',
            'void': 'red',
        }
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def disbursed_by_display(self, obj):
        if not obj.disbursed_by:
            return "system"
        return obj.disbursed_by.get_full_name() or obj.disbursed_by.get_username()

    disbursed_by_display.short_description = "Processed By"


@admin.register(DisbursementLineItem)
class DisbursementLineItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'disbursement_link', 'amount_display', 'cost_center', 'created_at']
    list_filter = ['cost_center', 'created_at']
    search_fields = ['description', 'cost_center', 'disbursement__reference_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (
            "Line Item Information",
            {'fields': ('disbursement', 'description', 'amount', 'cost_center', 'notes')},
        ),
        (
            "Audit Trail",
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )

    def disbursement_link(self, obj):
        url = reverse('admin:budget_execution_disbursement_change', args=[obj.disbursement.pk])
        return format_html('<a href="{}">{}</a>', url, obj.disbursement)

    disbursement_link.short_description = "Disbursement"

    def amount_display(self, obj):
        return _currency(obj.amount)

    amount_display.short_description = "Amount"
