"""
Common signals for the OBCMS application.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Municipality, Barangay
from .services.enhanced_geocoding import enhanced_ensure_location_coordinates

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Municipality)
def municipality_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a Municipality is saved.
    This will automatically geocode the municipality if it doesn't have coordinates.
    """
    if not instance.center_coordinates:
        logger.info(f"Municipality {instance.name} has no coordinates. Triggering geocoding.")
        try:
            lat, lng, updated, source = enhanced_ensure_location_coordinates(instance)
            if updated:
                logger.info(f"Successfully geocoded Municipality {instance.name} using {source}. New coordinates: [{lng}, {lat}]")
            elif lat and lng:
                logger.info(f"Municipality {instance.name} already had coordinates from {source}: [{lng}, {lat}]")
            else:
                logger.warning(f"Geocoding failed for Municipality {instance.name} from source {source}.")
        except Exception as e:
            logger.error(f"An error occurred during geocoding for Municipality {instance.name}: {e}", exc_info=True)

@receiver(post_save, sender=Barangay)
def barangay_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a Barangay is saved.
    This will automatically geocode the barangay if it doesn't have coordinates.
    """
    if not instance.center_coordinates:
        logger.info(f"Barangay {instance.name} has no coordinates. Triggering geocoding.")
        try:
            lat, lng, updated, source = enhanced_ensure_location_coordinates(instance)
            if updated:
                logger.info(f"Successfully geocoded Barangay {instance.name} using {source}. New coordinates: [{lng}, {lat}]")
            elif lat and lng:
                logger.info(f"Barangay {instance.name} already had coordinates from {source}: [{lng}, {lat}]")
            else:
                logger.warning(f"Geocoding failed for Barangay {instance.name} from source {source}.")
        except Exception as e:
            logger.error(f"An error occurred during geocoding for Barangay {instance.name}: {e}", exc_info=True)
