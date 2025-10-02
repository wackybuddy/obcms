"""Common signals for the OBCMS application."""

import logging
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import (
    Municipality,
    Barangay,
    StaffTask,
    StaffLeave,
    CalendarResourceBooking,
)
from .services.enhanced_geocoding import enhanced_ensure_location_coordinates
from coordination.models import Event
from monitoring.models import MonitoringEntry

logger = logging.getLogger(__name__)


CALENDAR_CACHE_INDEX_KEY = "calendar:payload:index"


def _invalidate_calendar_cache():
    """Remove cached calendar payloads after data mutations."""

    cached_keys = cache.get(CALENDAR_CACHE_INDEX_KEY) or []

    if cached_keys:
        cache.delete_many(cached_keys)

    cache.delete(CALENDAR_CACHE_INDEX_KEY)


@receiver(post_save, sender=Municipality)
def municipality_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a Municipality is saved.
    This will automatically geocode the municipality if it doesn't have coordinates.
    """
    if not instance.center_coordinates:
        logger.info(
            f"Municipality {instance.name} has no coordinates. Triggering geocoding."
        )
        try:
            lat, lng, updated, source = enhanced_ensure_location_coordinates(instance)
            if updated:
                logger.info(
                    f"Successfully geocoded Municipality {instance.name} using {source}. New coordinates: [{lng}, {lat}]"
                )
            elif lat and lng:
                logger.info(
                    f"Municipality {instance.name} already had coordinates from {source}: [{lng}, {lat}]"
                )
            else:
                logger.warning(
                    f"Geocoding failed for Municipality {instance.name} from source {source}."
                )
        except Exception as e:
            logger.error(
                f"An error occurred during geocoding for Municipality {instance.name}: {e}",
                exc_info=True,
            )


@receiver(post_save, sender=Barangay)
def barangay_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a Barangay is saved.
    This will automatically geocode the barangay if it doesn't have coordinates.
    """
    if not instance.center_coordinates:
        logger.info(
            f"Barangay {instance.name} has no coordinates. Triggering geocoding."
        )
        try:
            lat, lng, updated, source = enhanced_ensure_location_coordinates(instance)
            if updated:
                logger.info(
                    f"Successfully geocoded Barangay {instance.name} using {source}. New coordinates: [{lng}, {lat}]"
                )
            elif lat and lng:
                logger.info(
                    f"Barangay {instance.name} already had coordinates from {source}: [{lng}, {lat}]"
                )
            else:
                logger.warning(
                    f"Geocoding failed for Barangay {instance.name} from source {source}."
                )
        except Exception as e:
            logger.error(
                f"An error occurred during geocoding for Barangay {instance.name}: {e}",
                exc_info=True,
            )


@receiver([post_save, post_delete], sender=StaffTask)
@receiver([post_save, post_delete], sender=Event)
@receiver([post_save, post_delete], sender=MonitoringEntry)
@receiver([post_save, post_delete], sender=StaffLeave)
@receiver([post_save, post_delete], sender=CalendarResourceBooking)
def calendar_cache_invalidator(sender, **kwargs):
    """Clear cached calendar payloads when core calendar data changes."""

    _invalidate_calendar_cache()


def _sync_monitoring_entry_progress(task: StaffTask) -> None:
    """Recalculate MonitoringEntry progress when linked tasks change."""

    entry_id = task.related_ppa_id or task.linked_ppa_id
    if not entry_id:
        return

    related_tasks = StaffTask.objects.filter(
        models.Q(related_ppa_id=entry_id) | models.Q(linked_ppa_id=entry_id)
    )

    total = related_tasks.count()
    if total == 0:
        progress_value = 0
    else:
        completed = related_tasks.filter(status=StaffTask.STATUS_COMPLETED).count()
        progress_value = int((completed / total) * 100)

    entry_qs = MonitoringEntry.objects.filter(pk=entry_id)
    current = entry_qs.values_list("progress", flat=True).first()

    if current is None or current != progress_value:
        entry_qs.update(progress=progress_value)


@receiver(post_save, sender=StaffTask)
def staff_task_progress_sync(sender, instance: StaffTask, **kwargs):
    """Update MonitoringEntry progress when a task is saved."""

    _sync_monitoring_entry_progress(instance)


@receiver(post_delete, sender=StaffTask)
def staff_task_progress_sync_delete(sender, instance: StaffTask, **kwargs):
    """Update MonitoringEntry progress when a task is deleted."""

    _sync_monitoring_entry_progress(instance)
