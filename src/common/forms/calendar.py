"""Forms for calendar resource and booking management."""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from common.models import (
    CalendarResource,
    CalendarResourceBooking,
    CalendarNotification,
    UserCalendarPreferences,
    StaffLeave,
)

User = get_user_model()

INPUT_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
)
TEXTAREA_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
)
CHECKBOX_CLASS = (
    "h-4 w-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
)

DATE_WIDGET = forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS})
TIME_WIDGET = forms.TimeInput(attrs={"type": "time", "class": INPUT_CLASS})
DATETIME_WIDGET = forms.DateTimeInput(
    attrs={"type": "datetime-local", "class": INPUT_CLASS}
)


def _apply_field_styles(fields):
    """Apply consistent styling to form fields."""
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
            widget.attrs.setdefault("class", CHECKBOX_CLASS)
        elif isinstance(widget, forms.SelectMultiple):
            widget.attrs.setdefault("class", INPUT_CLASS)
        elif isinstance(widget, forms.Textarea):
            widget.attrs.setdefault("class", TEXTAREA_CLASS)
            widget.attrs.setdefault("rows", "4")
        elif isinstance(
            widget, (forms.Select, forms.TextInput, forms.NumberInput, forms.EmailInput)
        ):
            widget.attrs.setdefault("class", INPUT_CLASS)


class CalendarResourceForm(forms.ModelForm):
    """Form for creating and editing calendar resources."""

    class Meta:
        model = CalendarResource
        fields = [
            "name",
            "resource_type",
            "description",
            "location",
            "capacity",
            "is_available",
            "booking_requires_approval",
            "cost_per_use",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "name": "Unique identifier for this resource (e.g., 'Toyota Hilux - Plate ABC 1234')",
            "resource_type": "Category of resource for filtering and organization",
            "location": "Physical location or storage area",
            "capacity": "Maximum number of people (for rooms/vehicles) or units available",
            "linked_user": "For facilitator resources, link to the staff member's user account",
            "requires_approval": "If checked, bookings must be approved by an administrator",
            "allow_booking_advance_days": "Maximum days in advance that bookings can be made (0 = no limit)",
            "max_booking_duration_hours": "Maximum duration for a single booking (0 = no limit)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)

        linked_user_field = self.fields.get("linked_user")
        if linked_user_field:
            linked_user_field.queryset = User.objects.filter(is_staff=True).order_by(
                "first_name", "last_name"
            )
            linked_user_field.required = False

        # Set numeric field constraints
        for field_name in [
            "capacity",
            "allow_booking_advance_days",
            "max_booking_duration_hours",
        ]:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.setdefault("min", "0")

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get("resource_type")
        linked_user = cleaned_data.get("linked_user")

        # Validate that facilitator resources have a linked user
        if resource_type == CalendarResource.RESOURCE_FACILITATOR and not linked_user:
            self.add_error(
                "linked_user", "Facilitator resources must be linked to a user account."
            )

        return cleaned_data


class CalendarResourceBookingForm(forms.ModelForm):
    """Form for requesting resource bookings."""

    class Meta:
        model = CalendarResourceBooking
        fields = [
            "resource",
            "start_datetime",
            "end_datetime",
            "notes",
        ]
        widgets = {
            "start_datetime": DATETIME_WIDGET,
            "end_datetime": DATETIME_WIDGET,
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "resource": "Select the resource you want to book",
            "start_datetime": "When do you need the resource?",
            "end_datetime": "When will you return/release the resource?",
            "purpose": "Briefly describe why you need this resource",
            "notes": "Any additional information (e.g., destination, special requirements)",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.event = kwargs.pop("event", None)  # Optional linked event
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)

        # Filter resources to only available ones
        self.fields["resource"].queryset = CalendarResource.objects.filter(
            is_available=True
        ).order_by("resource_type", "name")

    def clean(self):
        cleaned_data = super().clean()
        resource = cleaned_data.get("resource")
        start_datetime = cleaned_data.get("start_datetime")
        end_datetime = cleaned_data.get("end_datetime")

        if not all([resource, start_datetime, end_datetime]):
            return cleaned_data

        # Validate start before end
        if start_datetime >= end_datetime:
            self.add_error("end_datetime", "End time must be after start time.")

        # Validate booking is in the future
        if start_datetime < timezone.now():
            self.add_error("start_datetime", "Cannot book resources in the past.")

        # Validate advance booking limit
        allow_advance_days = getattr(resource, "allow_booking_advance_days", 0) or 0
        if allow_advance_days > 0:
            max_advance = timezone.now() + timezone.timedelta(days=allow_advance_days)
            if start_datetime > max_advance:
                self.add_error(
                    "start_datetime",
                    f"Cannot book more than {allow_advance_days} days in advance.",
                )

        # Validate max booking duration
        max_duration = getattr(resource, "max_booking_duration_hours", 0) or 0
        if max_duration > 0:
            duration = (end_datetime - start_datetime).total_seconds() / 3600
            if duration > max_duration:
                self.add_error(
                    "end_datetime",
                    f"Booking duration cannot exceed {max_duration} hours.",
                )

        # Check for overlapping bookings
        overlapping = CalendarResourceBooking.objects.filter(
            resource=resource,
            start_datetime__lt=end_datetime,
            end_datetime__gt=start_datetime,
            status__in=[
                CalendarResourceBooking.STATUS_PENDING,
                CalendarResourceBooking.STATUS_APPROVED,
            ],
        )

        # Exclude current booking if editing
        if self.instance.pk:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            conflict = overlapping.first()
            self.add_error(
                "start_datetime",
                f"Resource is already booked from {conflict.start_datetime.strftime('%Y-%m-%d %H:%M')} "
                f"to {conflict.end_datetime.strftime('%Y-%m-%d %H:%M')}.",
            )

        return cleaned_data


class StaffLeaveForm(forms.ModelForm):
    """Form for staff to request leave."""

    class Meta:
        model = StaffLeave
        fields = [
            "leave_type",
            "start_date",
            "end_date",
            "reason",
        ]
        widgets = {
            "start_date": DATE_WIDGET,
            "end_date": DATE_WIDGET,
            "reason": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "leave_type": "Select the type of leave you're requesting",
            "start_date": "First day of leave",
            "end_date": "Last day of leave (inclusive)",
            "reason": "Brief explanation for the leave request",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)

        backup_staff_field = self.fields.get("backup_staff")
        if backup_staff_field:
            queryset = User.objects.filter(is_staff=True).order_by(
                "first_name", "last_name"
            )
            if self.user:
                queryset = queryset.exclude(pk=self.user.pk)
            backup_staff_field.queryset = queryset
            backup_staff_field.required = False

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            # Validate end after start
            if end_date < start_date:
                self.add_error("end_date", "End date must be on or after start date.")

            # Validate not too far in past
            if start_date < timezone.now().date() - timezone.timedelta(days=7):
                self.add_error(
                    "start_date", "Cannot request leave more than 7 days in the past."
                )

            # Check for overlapping leave (if user is set)
            if self.user:
                overlapping = StaffLeave.objects.filter(
                    staff=self.user,
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                    status__in=[StaffLeave.STATUS_PENDING, StaffLeave.STATUS_APPROVED],
                )

                # Exclude current leave if editing
                if self.instance.pk:
                    overlapping = overlapping.exclude(pk=self.instance.pk)

                if overlapping.exists():
                    conflict = overlapping.first()
                    self.add_error(
                        "start_date",
                        f"You already have leave scheduled from {conflict.start_date} to {conflict.end_date}.",
                    )

        return cleaned_data


class UserCalendarPreferencesForm(forms.ModelForm):
    """Form for user calendar notification preferences."""

    class Meta:
        model = UserCalendarPreferences
        fields = [
            "default_reminder_times",
            "email_enabled",
            "sms_enabled",
            "push_enabled",
            "daily_digest",
            "weekly_digest",
            "quiet_hours_start",
            "quiet_hours_end",
            "timezone",
        ]
        widgets = {
            "quiet_hours_start": TIME_WIDGET,
            "quiet_hours_end": TIME_WIDGET,
            "default_reminder_times": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "default_reminder_times": "Default Reminder Times",
            "email_enabled": "Email Notifications",
            "sms_enabled": "SMS Notifications",
            "push_enabled": "Push Notifications",
            "daily_digest": "Daily Digest Email",
            "weekly_digest": "Weekly Digest Email",
            "quiet_hours_start": "Quiet Hours Start",
            "quiet_hours_end": "Quiet Hours End",
            "timezone": "Time Zone",
        }
        help_texts = {
            "default_reminder_times": "Minutes before event (JSON array, e.g., [15, 60, 1440] for 15min, 1hr, 1 day)",
            "email_enabled": "Receive event notifications via email",
            "sms_enabled": "Receive event notifications via SMS (if available)",
            "push_enabled": "Receive push notifications in browser",
            "daily_digest": "Get a daily summary of upcoming events",
            "weekly_digest": "Get a weekly summary of upcoming events",
            "quiet_hours_start": "Don't send notifications after this time",
            "quiet_hours_end": "Resume notifications after this time",
            "timezone": "Your local timezone for displaying event times",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)

    def clean_default_reminder_times(self):
        """Validate reminder times JSON."""
        data = self.cleaned_data.get("default_reminder_times")

        if isinstance(data, str):
            import json

            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError(
                    "Invalid JSON format. Use array like [15, 60, 1440]"
                )

        if not isinstance(data, list):
            raise forms.ValidationError("Reminder times must be a list of numbers")

        if data and not all(isinstance(x, int) and x > 0 for x in data):
            raise forms.ValidationError(
                "All reminder times must be positive integers (minutes)"
            )

        return data

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("quiet_hours_start")
        end = cleaned_data.get("quiet_hours_end")

        # Both or neither must be set
        if (start and not end) or (end and not start):
            raise forms.ValidationError(
                "Both quiet hours start and end must be set, or neither"
            )

        if start and end and start == end:
            self.add_error(
                "quiet_hours_end",
                "Quiet hours end time must differ from start time.",
            )

        return cleaned_data
