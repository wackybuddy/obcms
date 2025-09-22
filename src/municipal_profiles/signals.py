from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from communities.models import OBCCommunity

from .models import OBCCommunityHistory
from .services import aggregate_and_store, record_community_history


@receiver(post_save, sender=OBCCommunity)
def handle_community_saved(sender, instance: OBCCommunity, created: bool, **kwargs):
    """Capture history and refresh aggregates whenever a community changes."""

    changed_by = getattr(instance, "_history_user", None)
    record_community_history(
        instance=instance,
        source=OBCCommunityHistory.SOURCE_MANUAL,
        note="Created" if created else "Updated",
        changed_by=changed_by,
    )
    municipality = instance.barangay.municipality
    aggregate_and_store(
        municipality=municipality,
        note="Triggered by barangay save",
        changed_by=changed_by,
    )


@receiver(post_delete, sender=OBCCommunity)
def handle_community_deleted(sender, instance: OBCCommunity, **kwargs):
    """Recompute aggregates whenever a community is removed."""

    record_community_history(
        instance=instance,
        source=OBCCommunityHistory.SOURCE_MANUAL,
        note="Deleted",
        changed_by=getattr(instance, "_history_user", None),
    )
    municipality = instance.barangay.municipality
    aggregate_and_store(
        municipality=municipality,
        note="Triggered by barangay delete",
        changed_by=getattr(instance, "_history_user", None),
    )
