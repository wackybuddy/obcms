"""
Calendar Preferences Views
Manage user calendar notification and display preferences.
"""

from datetime import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from common.forms.calendar import UserCalendarPreferencesForm
from common.models import UserCalendarPreferences


@login_required
def calendar_preferences(request):
    """
    View and edit user calendar preferences.
    Creates preferences object if it doesn't exist.
    """
    # Get or create preferences for user
    preferences, created = UserCalendarPreferences.objects.get_or_create(
        user=request.user,
        defaults={
            "default_reminder_times": [15, 60],  # 15 min and 1 hour before
            "email_enabled": True,
            "push_enabled": True,
            "weekly_digest": True,
            "timezone": "Asia/Manila",
        },
    )

    if request.method == "POST":
        form = UserCalendarPreferencesForm(request.POST, instance=preferences)

        if form.is_valid():
            with transaction.atomic():
                preferences = form.save(commit=False)
                preferences.user = request.user
                preferences.save()

                messages.success(request, "Calendar preferences updated successfully.")

            return redirect("common:calendar_preferences")
    else:
        form = UserCalendarPreferencesForm(instance=preferences)

    # Prepare reminder times for display
    reminder_display = []
    if preferences.default_reminder_times:
        for minutes in preferences.default_reminder_times:
            if minutes < 60:
                reminder_display.append(f"{minutes} minutes")
            elif minutes < 1440:
                hours = minutes // 60
                reminder_display.append(f"{hours} hour{'s' if hours > 1 else ''}")
            else:
                days = minutes // 1440
                reminder_display.append(f"{days} day{'s' if days > 1 else ''}")

    context = {
        "form": form,
        "preferences": preferences,
        "reminder_display": reminder_display,
        "page_title": "Calendar Preferences",
        "page_heading": "Calendar Notification Preferences",
        "submit_label": "Save Preferences",
        "return_url": request.GET.get("return", "/oobc-management/calendar/"),
    }

    return render(request, "common/calendar/preferences.html", context)
