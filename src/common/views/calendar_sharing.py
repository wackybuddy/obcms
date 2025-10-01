"""
Calendar Sharing Views
Allow users to create and manage shareable calendar links.
"""

import uuid
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse

from common.models import SharedCalendarLink
from common.services.calendar import build_calendar_payload


@login_required
def calendar_share_create(request):
    """
    Create a new shareable calendar link.
    """
    if request.method == "POST":
        # Get form data
        name = request.POST.get("name", "Shared Calendar")
        is_public = request.POST.get("is_public") == "on"
        expires_in_days = int(request.POST.get("expires_in_days", 30))
        allowed_modules = request.POST.getlist("allowed_modules")

        with transaction.atomic():
            # Calculate expiration
            expires_at = timezone.now() + timedelta(days=expires_in_days)

            # Create share link
            share_link = SharedCalendarLink.objects.create(
                created_by=request.user,
                expires_at=expires_at,
                filter_modules=allowed_modules if allowed_modules else [],
            )

            # Build share URL
            share_url = request.build_absolute_uri(
                reverse("common:calendar_share_view", kwargs={"token": str(share_link.token)})
            )

            messages.success(
                request,
                f"Shareable calendar link created successfully! Share URL: {share_url}"
            )

            return redirect("common:calendar_share_manage")

    # Get available modules
    available_modules = [
        ("coordination", "Coordination & Events"),
        ("mana", "MANA Assessments"),
        ("staff", "Staff Tasks & Leave"),
        ("policy", "Policy Recommendations"),
        ("planning", "Planning & Monitoring"),
        ("resources", "Resource Bookings"),
        ("communities", "Community Events"),
    ]

    context = {
        "available_modules": available_modules,
        "page_title": "Share Calendar",
        "page_heading": "Create Shareable Calendar Link",
    }

    return render(request, "common/calendar/share_create.html", context)


@login_required
def calendar_share_manage(request):
    """
    Manage existing calendar shares.
    """
    shares = SharedCalendarLink.objects.filter(
        created_by=request.user
    ).order_by("-created_at")

    # Build share URLs
    for share in shares:
        share.full_url = request.build_absolute_uri(
            reverse("common:calendar_share_view", kwargs={"token": str(share.token)})
        )

    context = {
        "shares": shares,
        "page_title": "Manage Shared Calendars",
        "page_heading": "Your Shared Calendar Links",
    }

    return render(request, "common/calendar/share_manage.html", context)


def calendar_share_view(request, token):
    """
    Public view for shared calendar (no authentication required).
    """
    share_link = get_object_or_404(
        SharedCalendarLink,
        token=token,
    )

    # Check if link is active and not expired
    if not share_link.is_active:
        return render(request, "common/calendar/share_expired.html", {
            "share_link": share_link,
        })

    if share_link.expires_at < timezone.now():
        return render(request, "common/calendar/share_expired.html", {
            "share_link": share_link,
        })

    # Check access count limit
    if share_link.max_views and share_link.view_count >= share_link.max_views:
        return render(request, "common/calendar/share_limit_reached.html", {
            "share_link": share_link,
        })

    # Increment view count
    share_link.view_count += 1
    share_link.save(update_fields=["view_count"])

    # Build calendar payload with module filter
    filter_modules = share_link.filter_modules if share_link.filter_modules else None
    payload = build_calendar_payload(filter_modules=filter_modules)

    # Remove sensitive data from entries
    for entry in payload.get("entries", []):
        if "extendedProps" in entry:
            # Remove workflow actions from public view
            entry["extendedProps"].pop("workflowActions", None)

    context = {
        "share_link": share_link,
        "calendar_data": payload,
        "page_title": "Shared Calendar",
        "is_public_view": True,
    }

    return render(request, "common/calendar/share_view.html", context)


@login_required
def calendar_share_toggle(request, share_id):
    """
    Toggle share link (activate/deactivate).
    Not used since model doesn't have is_active field.
    Simply use delete instead.
    """
    return redirect("common:calendar_share_manage")


@login_required
def calendar_share_delete(request, share_id):
    """
    Delete a share link.
    """
    share_link = get_object_or_404(
        SharedCalendarLink,
        id=share_id,
        created_by=request.user,
    )

    if request.method == "POST":
        share_link.delete()

        messages.success(request, "Share link has been deleted.")
        return redirect("common:calendar_share_manage")

    context = {
        "share_link": share_link,
        "page_title": "Delete Share Link",
    }

    return render(request, "common/calendar/share_delete_confirm.html", context)
