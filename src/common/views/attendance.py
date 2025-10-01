"""
Event Attendance Tracking Views
QR code check-in, manual attendance, and reporting.
"""

import io
import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.urls import reverse

from datetime import datetime

from coordination.models import Event, EventParticipant


@login_required
def event_check_in(request, event_id):
    """
    Manual check-in interface for event attendance.
    """
    event = get_object_or_404(Event, pk=event_id)

    # Get all participants
    participants = EventParticipant.objects.filter(event=event).select_related("user")

    status_styles = {
        "checked_in": ("Checked In", "bg-emerald-100 text-emerald-700", "checked-in"),
        "checked_out": ("Checked Out", "bg-blue-100 text-blue-700", "checked-out"),
        "absent": ("Absent", "bg-red-100 text-red-700", "absent"),
        "not_checked_in": (
            "Not Checked In",
            "bg-amber-100 text-amber-700",
            "not-checked-in",
        ),
    }

    participant_rows = []
    for item in participants:
        person = item.user
        display_name = (
            person.get_full_name()
            if person and person.get_full_name()
            else (person.username if person else item.name or "Guest")
        )

        label, badge_class, filter_value = status_styles.get(
            item.attendance_status,
            ("Pending", "bg-amber-100 text-amber-700", "not-checked-in"),
        )

        participant_rows.append(
            {
                "id": item.id,
                "display_name": display_name,
                "filter_value": filter_value,
                "status_label": label,
                "badge_class": badge_class,
                "check_in_time": item.check_in_time,
                "check_out_time": item.check_out_time,
                "can_check_in": item.attendance_status
                in {"not_checked_in", "checked_out"},
                "can_check_out": item.attendance_status == "checked_in",
            }
        )

    if request.method == "POST":
        participant_id = request.POST.get("participant_id")
        action = request.POST.get("action")  # check_in or check_out

        participant = get_object_or_404(
            EventParticipant, id=participant_id, event=event
        )

        if action == "check_in":
            participant.check_in_time = timezone.now()
            participant.attendance_status = "checked_in"
            participant.attended = True
            participant.check_in_method = "manual"
            participant.save(
                update_fields=[
                    "check_in_time",
                    "attendance_status",
                    "attended",
                    "check_in_method",
                ]
            )
            messages.success(
                request,
                f"{participant.user.get_full_name()} checked in successfully.",
            )

        elif action == "check_out":
            participant.check_out_time = timezone.now()
            participant.attendance_status = "checked_out"
            participant.save(update_fields=["check_out_time", "attendance_status"])
            messages.success(
                request,
                f"{participant.user.get_full_name()} checked out successfully.",
            )

        return redirect("common:event_check_in", event_id=event_id)

    # Attendance summary
    total_participants = participants.count()
    checked_in = participants.filter(attended=True).count()
    not_checked_in = total_participants - checked_in

    context = {
        "event": event,
        "participant_rows": participant_rows,
        "total_participants": total_participants,
        "checked_in": checked_in,
        "not_checked_in": not_checked_in,
        "attendance_rate": round(
            (checked_in / total_participants * 100) if total_participants > 0 else 0, 1
        ),
        "page_title": f"Check-In: {event.title}",
        "page_heading": f"Event Check-In: {event.title}",
    }

    return render(request, "common/attendance/check_in.html", context)


@login_required
def event_generate_qr(request, event_id):
    """
    Generate QR code for event check-in.
    """
    event = get_object_or_404(Event, pk=event_id)

    # Build check-in URL
    check_in_url = request.build_absolute_uri(
        reverse("common:event_scan_qr", kwargs={"event_id": event_id})
    )

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(check_in_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Return as image
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required
def event_scan_qr(request, event_id):
    """
    QR scanner page for mobile check-in.
    """
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        user_id = request.POST.get("user_id")

        # Find participant
        try:
            participant = EventParticipant.objects.get(event=event, user_id=user_id)

            # Check in
            if not participant.check_in_time:
                participant.check_in_time = timezone.now()
                participant.attendance_status = "checked_in"
                participant.attended = True
                participant.check_in_method = "qr_code"
                participant.save(
                    update_fields=[
                        "check_in_time",
                        "attendance_status",
                        "attended",
                        "check_in_method",
                    ]
                )

                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Welcome, {participant.user.get_full_name()}!",
                        "name": participant.user.get_full_name(),
                        "time": participant.check_in_time.strftime("%I:%M %p"),
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": (
                            f"{participant.user.get_full_name()} already checked in at "
                            f"{participant.check_in_time.strftime('%I:%M %p')}"
                        ),
                    }
                )

        except EventParticipant.DoesNotExist:
            return JsonResponse(
                {
                    "success": False,
                    "message": "User not registered for this event.",
                }
            )

    context = {
        "event": event,
        "page_title": f"Scan QR: {event.title}",
        "page_heading": "Scan QR Code to Check In",
    }

    return render(request, "common/attendance/qr_scanner.html", context)


@login_required
def event_attendance_report(request, event_id):
    """
    Attendance report and analytics for an event.
    """
    event = get_object_or_404(Event, pk=event_id)

    participants = EventParticipant.objects.filter(event=event).select_related("user")

    # Statistics
    total = participants.count()
    present = participants.filter(attended=True).count()
    absent = participants.filter(attendance_status="absent").count()
    pending = participants.filter(attendance_status="not_checked_in").count()
    checked_out = participants.filter(attendance_status="checked_out").count()

    # Time analysis
    event_start = None
    if event.start_date and event.start_time:
        event_start = timezone.make_aware(
            datetime.combine(event.start_date, event.start_time),
            timezone.get_current_timezone(),
        )

    if present > 0 and event_start:
        early_arrivals = participants.filter(
            check_in_time__isnull=False, check_in_time__lt=event_start
        ).count()

        late_arrivals = participants.filter(
            check_in_time__isnull=False, check_in_time__gt=event_start
        ).count()

        on_time = present - min(present, early_arrivals + late_arrivals)
    else:
        early_arrivals = late_arrivals = on_time = 0

    # Group by organization (if applicable)
    org_stats = {}
    for p in participants:
        org_user = p.user
        org = getattr(org_user, "organization", "Individual") if org_user else "Guest"
        if org not in org_stats:
            org_stats[org] = {"total": 0, "present": 0}
        org_stats[org]["total"] += 1
        if p.attended:
            org_stats[org]["present"] += 1

    # Calculate attendance rate per org
    for org in org_stats:
        total_org = org_stats[org]["total"]
        org_stats[org]["rate"] = round(
            (org_stats[org]["present"] / total_org * 100) if total_org > 0 else 0, 1
        )

    context = {
        "event": event,
        "participants": participants,
        "stats": {
            "total": total,
            "present": present,
            "absent": absent,
            "excused": 0,
            "pending": pending,
            "checked_out": checked_out,
            "attendance_rate": round((present / total * 100) if total > 0 else 0, 1),
            "early_arrivals": early_arrivals,
            "late_arrivals": late_arrivals,
            "on_time": on_time,
        },
        "org_stats": org_stats,
        "page_title": f"Attendance Report: {event.title}",
        "page_heading": f"Attendance Report: {event.title}",
    }

    # Provide alias expected by integration tests
    context["attendance_stats"] = context["stats"]

    return render(request, "common/attendance/report.html", context)
