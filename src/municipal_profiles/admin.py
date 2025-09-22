from django.contrib import admin

from .models import MunicipalOBCProfile, MunicipalOBCProfileHistory, OBCCommunityHistory


@admin.register(MunicipalOBCProfile)
class MunicipalOBCProfileAdmin(admin.ModelAdmin):
    list_display = (
        "municipality",
        "last_aggregated_at",
        "last_reported_update",
        "aggregation_version",
        "is_locked",
    )
    search_fields = ("municipality__name", "municipality__province__name")
    list_filter = ("is_locked", "municipality__province__region__code")
    readonly_fields = ("created_at", "updated_at", "last_aggregated_at", "last_reported_update")


@admin.register(MunicipalOBCProfileHistory)
class MunicipalOBCProfileHistoryAdmin(admin.ModelAdmin):
    list_display = ("profile", "change_type", "changed_by", "created_at")
    list_filter = ("change_type", "created_at")
    search_fields = ("profile__municipality__name", "note")
    readonly_fields = ("payload", "diff", "created_at", "updated_at")


@admin.register(OBCCommunityHistory)
class OBCCommunityHistoryAdmin(admin.ModelAdmin):
    list_display = ("community", "source", "changed_by", "created_at")
    list_filter = ("source", "created_at")
    search_fields = ("community__barangay__name", "note")
    readonly_fields = ("created_at", "updated_at")
