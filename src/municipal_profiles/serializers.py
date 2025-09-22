from __future__ import annotations

from typing import Any, Dict, Optional

from rest_framework import serializers

from .models import MunicipalOBCProfile, MunicipalOBCProfileHistory


class MunicipalOBCProfileHistorySerializer(serializers.ModelSerializer):
    """Serializer exposing audit entries."""

    changed_by_display = serializers.SerializerMethodField()

    class Meta:
        model = MunicipalOBCProfileHistory
        fields = [
            "id",
            "change_type",
            "payload",
            "diff",
            "changed_by",
            "changed_by_display",
            "note",
            "created_at",
        ]
        read_only_fields = fields

    def get_changed_by_display(self, obj: MunicipalOBCProfileHistory) -> Optional[str]:
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return None


class MunicipalOBCProfileSerializer(serializers.ModelSerializer):
    """Serializer driving the municipal OBC form."""

    municipality_name = serializers.CharField(source="municipality.name", read_only=True)
    province_name = serializers.CharField(source="municipality.province.name", read_only=True)
    region_name = serializers.CharField(source="municipality.province.region.name", read_only=True)
    history = MunicipalOBCProfileHistorySerializer(source="history_entries", many=True, read_only=True)
    history_note = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = MunicipalOBCProfile
        fields = [
            "id",
            "municipality",
            "municipality_name",
            "province_name",
            "region_name",
            "aggregated_metrics",
            "reported_metrics",
            "reported_notes",
            "history",
            "history_note",
            "last_aggregated_at",
            "last_reported_update",
            "aggregation_version",
            "is_locked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "municipality_name",
            "province_name",
            "region_name",
            "aggregated_metrics",
            "history",
            "last_aggregated_at",
            "last_reported_update",
            "aggregation_version",
            "created_at",
            "updated_at",
        )

    def update(self, instance: MunicipalOBCProfile, validated_data: Dict[str, Any]) -> MunicipalOBCProfile:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None and not getattr(user, "is_authenticated", False):
            user = None

        history_note = validated_data.pop("history_note", "")
        reported_metrics = validated_data.pop("reported_metrics", None)
        reported_notes = validated_data.pop("reported_notes", None)
        is_locked = validated_data.pop("is_locked", None)
        validated_data.pop("municipality", None)

        update_fields = []
        if reported_notes is not None:
            instance.reported_notes = reported_notes
            update_fields.append("reported_notes")
        if is_locked is not None:
            instance.is_locked = is_locked
            update_fields.append("is_locked")
        if update_fields:
            update_fields.append("updated_at")
            instance.save(update_fields=update_fields)

        if reported_metrics is not None:
            instance.apply_reported_update(
                reported_payload=reported_metrics,
                changed_by=user,
                note=history_note,
                update_notes=reported_notes is not None,
            )

        return instance
