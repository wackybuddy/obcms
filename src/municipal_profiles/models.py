from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from django.conf import settings
from django.db import models
from django.utils import timezone

from common.models import Municipality


class TimeStampedModel(models.Model):
    """Abstract base model providing created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MunicipalOBCProfile(TimeStampedModel):
    """Stores municipal level OBC information."""

    municipality = models.OneToOneField(
        Municipality,
        on_delete=models.CASCADE,
        related_name="obc_profile",
        help_text="Municipality or city covered by this profile.",
    )
    aggregated_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Roll-up metrics derived from all barangay OBC records.",
    )
    reported_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Municipal level metrics manually encoded by LGU partners.",
    )
    reported_notes = models.TextField(
        blank=True,
        help_text="Narrative notes accompanying the latest municipal submission.",
    )
    last_aggregated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the most recent automatic aggregation run.",
    )
    last_reported_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the most recent manual municipal update.",
    )
    aggregation_version = models.PositiveIntegerField(
        default=0,
        help_text="Version counter for the aggregation pipeline.",
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Lock manual edits while undergoing validation or review.",
    )

    class Meta:
        verbose_name = "Municipal OBC Profile"
        verbose_name_plural = "Municipal OBC Profiles"
        ordering = ["municipality__province__region__code", "municipality__name"]

    def __str__(self) -> str:
        return f"OBC Profile for {self.municipality.name}"

    # --- History helpers -------------------------------------------------
    def log_history(
        self,
        *,
        change_type: str,
        payload: Dict[str, Any],
        changed_by: Optional[models.Model] = None,
        note: str = "",
    ) -> "MunicipalOBCProfileHistory":
        """Persist a history entry for auditing purposes."""

        return MunicipalOBCProfileHistory.objects.create(
            profile=self,
            change_type=change_type,
            payload=payload or {},
            changed_by=changed_by,
            note=note,
        )

    def apply_aggregation(
        self,
        *,
        aggregated_payload: Dict[str, Any],
        changed_by: Optional[models.Model] = None,
        note: str = "",
        history_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist aggregation results and capture an audit record."""

        now = timezone.now()
        self.aggregated_metrics = aggregated_payload or {}
        self.last_aggregated_at = now
        self.aggregation_version = self.aggregation_version + 1
        self.save(update_fields=[
            "aggregated_metrics",
            "last_aggregated_at",
            "aggregation_version",
            "updated_at",
        ])
        self.log_history(
            change_type=MunicipalOBCProfileHistory.CHANGE_AGGREGATED,
            payload=history_payload or self.aggregated_metrics,
            changed_by=changed_by,
            note=note,
        )

    def apply_reported_update(
        self,
        *,
        reported_payload: Dict[str, Any],
        changed_by: Optional[models.Model] = None,
        note: str = "",
        update_notes: bool = False,
    ) -> None:
        """Persist manual form updates with accompanying history."""

        now = timezone.now()
        self.reported_metrics = reported_payload or {}
        self.last_reported_update = now
        update_fields = [
            "reported_metrics",
            "last_reported_update",
            "updated_at",
        ]
        if update_notes:
            update_fields.append("reported_notes")
        self.save(update_fields=update_fields)
        self.log_history(
            change_type=MunicipalOBCProfileHistory.CHANGE_REPORTED,
            payload=self.reported_metrics,
            changed_by=changed_by,
            note=note,
        )


class MunicipalOBCProfileHistory(TimeStampedModel):
    """Immutable audit log capturing all profile mutations."""

    CHANGE_REPORTED = "reported"
    CHANGE_AGGREGATED = "aggregated"
    CHANGE_IMPORT = "import"

    CHANGE_TYPE_CHOICES = [
        (CHANGE_REPORTED, "Manual municipal update"),
        (CHANGE_AGGREGATED, "Barangay aggregation"),
        (CHANGE_IMPORT, "Data import"),
    ]

    profile = models.ForeignKey(
        MunicipalOBCProfile,
        on_delete=models.CASCADE,
        related_name="history_entries",
    )
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="municipal_profile_changes",
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Municipal OBC Profile History"
        verbose_name_plural = "Municipal OBC Profile History"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial repr
        return f"{self.profile} – {self.change_type} @ {self.created_at:%Y-%m-%d %H:%M}"


class OBCCommunityHistory(TimeStampedModel):
    """Historical snapshots for barangay level OBC records."""

    SOURCE_MANUAL = "manual"
    SOURCE_IMPORT = "import"
    SOURCE_AGGREGATION = "aggregation"

    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual update"),
        (SOURCE_IMPORT, "Data import"),
        (SOURCE_AGGREGATION, "System aggregation"),
    ]

    community = models.ForeignKey(
        "communities.OBCCommunity",
        on_delete=models.CASCADE,
        related_name="history_entries",
    )
    snapshot = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="obc_community_changes",
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "OBC Community History"
        verbose_name_plural = "OBC Community History"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial repr
        return f"{self.community} snapshot @ {self.created_at:%Y-%m-%d %H:%M}"


@dataclass
class AggregationResult:
    municipality: Municipality
    aggregated_metrics: Dict[str, Any]
    barangay_count: int
    communities_considered: Iterable[int]

    def as_payload(self) -> Dict[str, Any]:
        return {
            "municipality": self.municipality.pk,
            "barangay_count": self.barangay_count,
            "communities": list(self.communities_considered),
            "aggregated_metrics": self.aggregated_metrics,
        }
