"""API views for calendar drag-and-drop and interactive features."""

import json
import logging
from datetime import datetime, time, timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from coordination.models import Event, StakeholderEngagement

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def calendar_event_update(request):
    """
    Update event date/time via drag-and-drop or resize.

    Expected POST data:
    {
        "id": "event-uuid",
        "type": "event",  # or "engagement"
        "start": "2025-10-15T09:00:00",
        "end": "2025-10-15T11:00:00",
        "allDay": false
    }
    """
    try:
        data = json.loads(request.body)
        event_id = data.get("id")
        event_type = data.get("type", "event")
        start_str = data.get("start")
        end_str = data.get("end")
        all_day = data.get("allDay", False)

        if not event_id or not start_str:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"},
                status=400
            )

        # Parse datetime strings
        try:
            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            if timezone.is_aware(start_dt):
                start_dt = timezone.localtime(start_dt)

            end_dt = None
            if end_str:
                end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                if timezone.is_aware(end_dt):
                    end_dt = timezone.localtime(end_dt)
        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing datetime: {e}")
            return JsonResponse(
                {"success": False, "error": "Invalid datetime format"},
                status=400
            )

        # Update event based on type
        if event_type == "event":
            try:
                event = Event.objects.get(pk=event_id)

                # Check permissions
                if not (request.user.is_staff or
                        request.user.is_superuser or
                        event.created_by == request.user or
                        request.user.has_perm("coordination.change_event")):
                    return JsonResponse(
                        {"success": False, "error": "Permission denied"},
                        status=403
                    )

                # Update event fields
                event.start_date = start_dt.date()

                if all_day:
                    event.start_time = None
                    event.end_time = None
                    if end_dt:
                        # FullCalendar adds 1 day to end for all-day events
                        event.end_date = (end_dt - timedelta(days=1)).date()
                    else:
                        event.end_date = start_dt.date()
                else:
                    event.start_time = start_dt.time()

                    if end_dt:
                        if end_dt.date() == start_dt.date():
                            event.end_time = end_dt.time()
                            event.end_date = None
                        else:
                            event.end_date = end_dt.date()
                            event.end_time = end_dt.time()

                        # Calculate duration
                        duration = end_dt - start_dt
                        event.duration_hours = duration.total_seconds() / 3600

                event.save(update_fields=[
                    'start_date', 'start_time', 'end_date', 'end_time', 'duration_hours'
                ])

                logger.info(
                    f"Event {event_id} rescheduled by {request.user.username}: "
                    f"{start_dt} to {end_dt}"
                )

                return JsonResponse({
                    "success": True,
                    "message": f"Event '{event.title}' rescheduled successfully"
                })

            except Event.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Event not found"},
                    status=404
                )

        elif event_type == "engagement" or event_type == "activity":
            try:
                engagement = StakeholderEngagement.objects.get(pk=event_id)

                # Check permissions
                if not (request.user.is_staff or
                        request.user.is_superuser or
                        engagement.created_by == request.user or
                        request.user.has_perm("coordination.change_stakeholderengagement")):
                    return JsonResponse(
                        {"success": False, "error": "Permission denied"},
                        status=403
                    )

                # Update engagement
                engagement.planned_date = start_dt

                if end_dt:
                    duration = end_dt - start_dt
                    engagement.expected_duration_hours = duration.total_seconds() / 3600

                engagement.save(update_fields=[
                    'planned_date', 'expected_duration_hours'
                ])

                logger.info(
                    f"Engagement {event_id} rescheduled by {request.user.username}: "
                    f"{start_dt} to {end_dt}"
                )

                return JsonResponse({
                    "success": True,
                    "message": f"Activity '{engagement.title}' rescheduled successfully"
                })

            except StakeholderEngagement.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Engagement not found"},
                    status=404
                )

        else:
            return JsonResponse(
                {"success": False, "error": "Invalid event type"},
                status=400
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        logger.error(f"Error updating calendar event: {e}", exc_info=True)
        return JsonResponse(
            {"success": False, "error": "Server error"},
            status=500
        )
