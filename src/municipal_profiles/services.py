from __future__ import annotations

from typing import Dict, Iterable, Optional

from django.db import transaction
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.utils import timezone

from common.models import Municipality
from communities.models import OBCCommunity

from .models import (
    AggregationResult,
    MunicipalOBCProfile,
    OBCCommunityHistory,
)

# Numeric fields that should be summed when computing aggregates.
AGGREGATABLE_FIELDS = {
    "estimated_obc_population",
    "total_barangay_population",
    "households",
    "families",
    "children_0_12",
    "youth_13_30",
    "adults_31_59",
    "seniors_60_plus",
    "women_count",
    "solo_parents_count",
    "elderly_count",
    "pwd_count",
    "farmers_count",
    "fisherfolk_count",
    "indigenous_peoples_count",
    "idps_count",
    "religious_leaders_ulama_count",
    "csos_count",
    "associations_count",
    "teachers_asatidz_count",
    "number_of_employed_obc",
    "number_of_cooperatives",
    "number_of_social_enterprises",
    "number_of_micro_enterprises",
    "number_of_unbanked_obc",
}


def ensure_profile(municipality: Municipality) -> MunicipalOBCProfile:
    """Return the municipal profile instance, creating it when needed."""

    profile, _ = MunicipalOBCProfile.objects.get_or_create(municipality=municipality)
    return profile


def _serialise_community(instance: OBCCommunity) -> Dict[str, object]:
    """Return a JSON-friendly representation of the community."""

    field_names = [
        field.name
        for field in instance._meta.fields
        if field.concrete and field.editable and field.name not in {"created_at", "updated_at"}
    ]
    payload = model_to_dict(instance, fields=field_names)
    payload["id"] = instance.pk
    payload["barangay"] = instance.barangay_id
    payload["municipality"] = instance.barangay.municipality_id
    payload["province"] = instance.barangay.municipality.province_id
    payload["region"] = instance.barangay.municipality.province.region_id
    payload["updated_at"] = instance.updated_at.isoformat() if instance.updated_at else None
    payload["created_at"] = instance.created_at.isoformat() if instance.created_at else None
    return payload


def record_community_history(
    *,
    instance: OBCCommunity,
    source: str,
    changed_by=None,
    note: str = "",
) -> OBCCommunityHistory:
    """Persist a barangay level history snapshot."""

    return OBCCommunityHistory.objects.create(
        community=instance,
        snapshot=_serialise_community(instance),
        source=source,
        changed_by=changed_by,
        note=note,
    )


def compute_aggregate_for_municipality(
    municipality: Municipality,
) -> AggregationResult:
    """Aggregate barangay metrics for a municipality."""

    queryset = OBCCommunity.objects.filter(barangay__municipality=municipality)
    aggregated: Dict[str, int] = {}
    for field in AGGREGATABLE_FIELDS:
        aggregated[field] = queryset.aggregate(total=Sum(field))['total'] or 0

    aggregated["community_count"] = queryset.count()
    aggregated["barangay_count"] = queryset.values_list("barangay_id", flat=True).distinct().count()
    aggregated["last_source_update"] = timezone.now().isoformat()

    return AggregationResult(
        municipality=municipality,
        aggregated_metrics=aggregated,
        barangay_count=aggregated["barangay_count"],
        communities_considered=queryset.values_list("id", flat=True),
    )


def aggregate_and_store(
    *,
    municipality: Municipality,
    changed_by=None,
    note: str = "",
) -> MunicipalOBCProfile:
    """Compute aggregation and persist it on the municipal profile."""

    result = compute_aggregate_for_municipality(municipality)
    profile = ensure_profile(municipality)
    with transaction.atomic():
        profile.apply_aggregation(
            aggregated_payload=result.aggregated_metrics,
            changed_by=changed_by,
            note=note or "Automatic barangay roll-up",
            history_payload=result.as_payload(),
        )
    return profile
