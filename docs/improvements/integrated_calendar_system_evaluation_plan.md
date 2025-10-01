# Integrated Calendar System: Implementation Evaluation & Comprehensive Plan

**Document Status**: Implementation Roadmap
**Date Created**: October 1, 2025
**Related Documents**:
- [Coordination Calendar Improvement Plan](coordination-calendar-improvement-plan.md)
- [Planning & Budgeting Implementation Evaluation](✅planning_budgeting_implementation_evaluation.md)
- [OOBC Integrative Report](../reports/OOBC_integrative_report.md)

---

## Executive Summary

This document evaluates the current calendar implementation across the OOBC system and provides a comprehensive plan for creating a **truly integrated, organization-wide calendar system** that:

1. **Consolidates all scheduling needs** - Unifies coordination, MANA, policy, planning, staff, and community calendars
2. **Evaluates maturity levels** - Rates completeness of existing calendar features (0-100%)
3. **Maps integration points** - Documents how calendar relates to all modules
4. **Defines improvement priorities** - Creates phased enhancement plan
5. **Specifies modern features** - Adds recurring events, notifications, resource booking, external calendar sync

**Key Finding**: The codebase has **excellent calendar foundations** (70% complete) but lacks:
- **Recurring events support** (0% complete)
- **External calendar integration** (Google Calendar, Outlook) (0% complete)
- **Resource booking system** (venues, vehicles, equipment) (10% complete - basic venue field only)
- **Attendance tracking & check-in** (0% complete)
- **Calendar notifications & reminders** (15% complete - basic workflow actions only)
- **Mobile-optimized calendar interface** (30% complete - responsive but not native)
- **AI-powered scheduling assistance** (0% complete)
- **Calendar sharing & permissions** (25% complete - basic access control only)

---

## Table of Contents

1. [Existing Feature Evaluation](#existing-feature-evaluation)
2. [Module Integration Analysis](#module-integration-analysis)
3. [Gap Analysis](#gap-analysis)
4. [Integration Improvement Plan](#integration-improvement-plan)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Technical Specifications](#technical-specifications)

---

## Existing Feature Evaluation

### Area 1: Core Calendar Infrastructure

**Maturity**: 🟢 **70% Complete** - Strong foundation with comprehensive event aggregation

#### Existing Features

✅ **Centralized Calendar Service** (`src/common/services/calendar.py`):
- `build_calendar_payload()` aggregates events from all modules
- Module-specific filtering and statistics
- Conflict detection across modules
- Workflow action tracking
- Analytics: heatmaps, status counts, compliance metrics
- Supports 7 modules: coordination, mana, staff, policy, planning

✅ **OOBC Calendar View** (`src/templates/common/oobc_calendar.html`):
- FullCalendar v6 integration
- Module filters with color-coding
- Upcoming highlights sidebar
- Follow-up tasks tracking
- Workflow alerts (approvals, escalations)
- Potential conflicts display
- Activity heatmap (7-day view)
- Status breakdown per module
- Compliance snapshot

✅ **Calendar Exports** (routes exist at [src/common/views/management.py](src/common/views/management.py)):
- JSON feed (`/oobc-management/calendar/feed.json`)
- ICS feed (`/oobc-management/calendar/feed.ics`)
- Printable brief (`/oobc-management/calendar/brief/`)

✅ **Data Sources** (7 modules integrated):
1. **Coordination**: Events, Stakeholder Engagements, Communications, Partnerships, Milestones
2. **MANA**: Baseline Data Collection activities
3. **Staff**: Tasks, Training Enrollments
4. **Policy**: Policy Recommendation deadlines
5. **Planning**: MonitoringEntry milestones, Workflow stages

#### Missing Features

❌ **Recurring Events**:
- No `RecurringEventPattern` model
- No support for daily/weekly/monthly/yearly recurrence
- No exception handling for recurring series
- No "Edit this instance" vs "Edit all future" logic

❌ **External Calendar Integration**:
- No Google Calendar sync
- No Microsoft Outlook/Exchange integration
- No CalDAV/CardDAV support
- No two-way sync (import external events, push OOBC events)

❌ **Resource Management**:
- No `Resource` model (vehicles, equipment, rooms)
- Venue is text field, not bookable entity
- No resource availability checking
- No resource conflict detection

❌ **Attendance & Participation**:
- No check-in/check-out system
- No QR code attendance
- No RSVP tracking (going/not going/maybe)
- Participant lists exist (`EventParticipant`) but no attendance status

❌ **Advanced Notifications**:
- No email reminders before events
- No SMS notifications
- No push notifications
- No digest emails (daily/weekly upcoming events)
- Workflow actions exist but not actionable via email

❌ **Mobile Experience**:
- Calendar is responsive but not optimized for mobile
- No native mobile app
- No offline support
- No mobile calendar widget

❌ **AI & Automation**:
- No intelligent scheduling suggestions
- No conflict resolution recommendations
- No automatic time zone handling
- No natural language event creation ("Schedule meeting with DSWD next Tuesday")

❌ **Permissions & Sharing**:
- Basic access control exists
- No granular calendar sharing (view-only, edit)
- No public calendars for communities
- No calendar delegation

#### Recommended Actions

**1. Create `RecurringEventPattern` Model**:
```python
class RecurringEventPattern(models.Model):
    """Defines recurrence rules for events."""

    # RFC 5545 (iCalendar) compatible
    recurrence_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ]
    )
    interval = models.PositiveIntegerField(
        default=1,
        help_text="Repeat every N days/weeks/months"
    )

    # For weekly: days of week (Monday=1, Sunday=7)
    by_weekday = models.JSONField(
        default=list,
        help_text="List of weekdays: [1,3,5] = Mon, Wed, Fri"
    )

    # For monthly: day of month or relative (first Monday, last Friday)
    by_monthday = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Day of month (1-31)"
    )
    by_setpos = models.JSONField(
        default=list,
        help_text="Relative position: [1, 'monday'] = first Monday"
    )

    # End conditions
    count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="End after N occurrences"
    )
    until_date = models.DateField(
        null=True,
        blank=True,
        help_text="End by date"
    )

    # Exceptions (dates to skip)
    exception_dates = models.JSONField(
        default=list,
        help_text="List of ISO dates to exclude"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
```

**2. Add Recurrence Support to Event Models**:
```python
# Add to coordination.Event
recurrence_pattern = models.ForeignKey(
    'RecurringEventPattern',
    null=True,
    blank=True,
    related_name='recurring_events',
    on_delete=models.SET_NULL,
)
recurrence_parent = models.ForeignKey(
    'self',
    null=True,
    blank=True,
    related_name='recurrence_instances',
    help_text="Parent event if this is a recurrence instance"
)
is_recurrence_exception = models.BooleanField(
    default=False,
    help_text="True if this instance was edited separately"
)
```

**3. Create `CalendarResource` Model**:
```python
class CalendarResource(models.Model):
    """Bookable resources: vehicles, equipment, venues."""

    resource_type = models.CharField(
        max_length=20,
        choices=[
            ('vehicle', 'Vehicle'),
            ('equipment', 'Equipment'),
            ('room', 'Meeting Room'),
            ('facilitator', 'Facilitator/Trainer'),
        ]
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(
        null=True,
        help_text="Max people (for rooms) or units available"
    )
    location = models.CharField(max_length=255, blank=True)

    # Availability
    is_available = models.BooleanField(default=True)
    booking_requires_approval = models.BooleanField(default=False)

    # Cost
    cost_per_use = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['resource_type', 'name']
```

**4. Create `CalendarResourceBooking` Model**:
```python
class CalendarResourceBooking(models.Model):
    """Links events to resources."""

    resource = models.ForeignKey(
        CalendarResource,
        on_delete=models.CASCADE,
        related_name='bookings',
    )

    # Polymorphic: can link to Event, StakeholderEngagement, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    event_instance = GenericForeignKey('content_type', 'object_id')

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
    )

    booked_by = models.ForeignKey(User, on_delete=models.PROTECT)
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='approved_bookings',
        on_delete=models.SET_NULL,
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['resource', 'status']),
        ]

    def clean(self):
        # Check for overlapping bookings
        overlaps = CalendarResourceBooking.objects.filter(
            resource=self.resource,
            status__in=['pending', 'approved'],
            start_datetime__lt=self.end_datetime,
            end_datetime__gt=self.start_datetime,
        ).exclude(pk=self.pk)

        if overlaps.exists():
            raise ValidationError(
                f"Resource {self.resource.name} is already booked during this time."
            )
```

**5. Enhance Attendance Tracking**:
```python
# Extend coordination.EventParticipant
rsvp_status = models.CharField(
    max_length=20,
    choices=[
        ('invited', 'Invited'),
        ('going', 'Going'),
        ('maybe', 'Maybe'),
        ('declined', 'Declined'),
    ],
    default='invited',
)
attendance_status = models.CharField(
    max_length=20,
    choices=[
        ('not_checked_in', 'Not Checked In'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('absent', 'Absent'),
    ],
    default='not_checked_in',
)
check_in_time = models.DateTimeField(null=True, blank=True)
check_out_time = models.DateTimeField(null=True, blank=True)
check_in_method = models.CharField(
    max_length=20,
    choices=[
        ('manual', 'Manual'),
        ('qr_code', 'QR Code'),
        ('nfc', 'NFC'),
    ],
    blank=True,
)
```

**6. Create External Calendar Sync Models**:
```python
class ExternalCalendarSync(models.Model):
    """Sync with Google Calendar, Outlook, etc."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(
        max_length=20,
        choices=[
            ('google', 'Google Calendar'),
            ('microsoft', 'Microsoft Outlook'),
            ('apple', 'Apple iCloud'),
        ]
    )

    # OAuth tokens (encrypted)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()

    # Settings
    sync_direction = models.CharField(
        max_length=20,
        choices=[
            ('export_only', 'Export to external calendar only'),
            ('import_only', 'Import from external calendar only'),
            ('two_way', 'Two-way sync'),
        ],
        default='export_only',
    )

    # Which OOBC modules to sync
    sync_modules = models.JSONField(
        default=list,
        help_text="List of module keys: ['coordination', 'staff', 'mana']"
    )

    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Integration Points:**
- `Event/StakeholderEngagement` → `RecurringEventPattern` (one-to-many)
- `Event/StakeholderEngagement` → `CalendarResourceBooking` (GenericForeignKey)
- `CalendarResourceBooking` → `CalendarResource` (resource availability)
- `EventParticipant` → Enhanced RSVP and attendance tracking
- `ExternalCalendarSync` → Bidirectional sync with external calendars

---

### Area 2: Calendar Views & User Experience

**Maturity**: 🟡 **55% Complete** - Good foundation but limited advanced features

#### Existing Features

✅ **OOBC Management Calendar** ([src/templates/common/oobc_calendar.html](src/templates/common/oobc_calendar.html)):
- Full-page calendar with FullCalendar
- Module filters (coordination, mana, staff, policy, planning)
- Month/week/day views
- Color-coded events by module
- Sidebar with stats and highlights
- Export buttons (JSON, ICS, printable)

✅ **Coordination Calendar** ([src/templates/coordination/calendar.html](src/templates/coordination/calendar.html)):
- Department-specific view
- Quick actions for new events
- Event/activity snapshots

✅ **Calendar Widget** (`src/templates/components/calendar_widget.html`):
- Reusable component
- Configurable options

#### Missing Features

❌ **Advanced View Options**:
- No agenda/list view
- No multi-week view
- No year view
- No timeline/Gantt chart view for projects
- No custom view builder (save filter presets)

❌ **Drag & Drop**:
- No drag-and-drop rescheduling
- No drag-to-extend duration
- No drag resource to event

❌ **Quick Actions**:
- No inline event creation (click date → quick form)
- No right-click context menu
- No keyboard shortcuts
- No bulk operations (move multiple events)

❌ **Search & Filter**:
- Module filter exists
- No full-text search across events
- No advanced filters (date range, status, priority, community)
- No saved filter presets

❌ **Print & Share**:
- Printable brief exists but basic
- No customizable print layouts
- No share via link (temporary view-only access)
- No embed widget for external sites

❌ **Mobile App**:
- No native iOS/Android app
- No offline mode
- No mobile calendar widget
- No mobile notifications

#### Recommended Actions

**1. Enhance Calendar UI**:
- Add agenda view (list of upcoming events)
- Implement drag-and-drop rescheduling
- Add inline event creation (click date → modal)
- Implement keyboard shortcuts (n=new event, t=today, d/w/m=day/week/month view)

**2. Add Advanced Filters**:
```python
# views/management.py:oobc_calendar
def oobc_calendar(request):
    # ... existing code ...

    # Advanced filters
    filter_params = {
        'modules': request.GET.getlist('module'),
        'date_from': request.GET.get('date_from'),
        'date_to': request.GET.get('date_to'),
        'status': request.GET.getlist('status'),
        'priority': request.GET.getlist('priority'),
        'community': request.GET.get('community'),
        'organizer': request.GET.get('organizer'),
        'search': request.GET.get('q'),
    }

    payload = build_calendar_payload(
        filter_modules=filter_params['modules'],
        date_from=filter_params['date_from'],
        date_to=filter_params['date_to'],
        # ... additional filters
    )
```

**3. Create Shareable Calendar Links**:
```python
class SharedCalendarLink(models.Model):
    """Temporary view-only calendar access."""

    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Access control
    expires_at = models.DateTimeField()
    max_views = models.PositiveIntegerField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)

    # Filters
    filter_modules = models.JSONField(default=list)
    filter_date_from = models.DateField(null=True)
    filter_date_to = models.DateField(null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**4. Mobile Optimization**:
- Add touch-optimized gestures (swipe to change month)
- Implement pull-to-refresh
- Add mobile-specific compact views
- Create Progressive Web App (PWA) manifest

---

### Area 3: Notifications & Reminders

**Maturity**: 🔴 **15% Complete** - Workflow actions exist but not actionable

#### Existing Features

✅ **Workflow Actions** ([src/common/services/calendar.py](src/common/services/calendar.py)):
- Follow-up items tracked
- Approval requirements flagged
- Escalations identified
- Due dates monitored

#### Missing Features

❌ **Email Notifications**:
- No event invitation emails
- No reminder emails (1 day before, 1 hour before)
- No digest emails (daily/weekly upcoming events)
- No RSVP emails
- No event update notifications

❌ **In-App Notifications**:
- No notification center
- No real-time alerts
- No notification preferences

❌ **SMS Notifications**:
- No SMS reminders
- No SMS event invitations

❌ **Push Notifications**:
- No browser push notifications
- No mobile app push notifications

❌ **Actionable Notifications**:
- No "Add to my calendar" button
- No "Accept/Decline" in email
- No "Check in" link

#### Recommended Actions

**1. Create Notification System**:
```python
class CalendarNotification(models.Model):
    """Scheduled notifications for events."""

    # Polymorphic link to event
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    event_instance = GenericForeignKey('content_type', 'object_id')

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)

    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('invitation', 'Event Invitation'),
            ('reminder', 'Reminder'),
            ('update', 'Event Updated'),
            ('cancellation', 'Event Cancelled'),
            ('rsvp_request', 'RSVP Request'),
        ]
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('push', 'Push Notification'),
            ('in_app', 'In-App'),
        ]
    )

    scheduled_for = models.DateTimeField(
        help_text="When to send notification"
    )
    sent_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
    )

    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**2. Implement Celery Tasks for Notifications**:
```python
# common/tasks.py
from celery import shared_task

@shared_task
def send_calendar_notifications():
    """Send pending notifications."""
    from common.models import CalendarNotification

    now = timezone.now()
    pending = CalendarNotification.objects.filter(
        status='pending',
        scheduled_for__lte=now,
    )[:100]

    for notification in pending:
        try:
            if notification.delivery_method == 'email':
                send_notification_email(notification)
            elif notification.delivery_method == 'sms':
                send_notification_sms(notification)
            elif notification.delivery_method == 'push':
                send_push_notification(notification)

            notification.status = 'sent'
            notification.sent_at = now
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)

        notification.save()

@shared_task
def schedule_event_reminders(event_id, event_type):
    """Create reminder notifications for an event."""
    # Create notifications 1 week, 1 day, 1 hour before
    # ...
```

**3. User Notification Preferences**:
```python
class UserCalendarPreferences(models.Model):
    """User preferences for calendar notifications."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_preferences',
    )

    # Default reminder times (minutes before event)
    default_reminder_times = models.JSONField(
        default=list,
        help_text="List of minutes: [1440, 60] = 1 day, 1 hour"
    )

    # Notification channels
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)

    # Digest emails
    daily_digest = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=True)

    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    # Timezone
    timezone = models.CharField(
        max_length=50,
        default='Asia/Manila',
    )
```

---

### Area 4: AI & Automation

**Maturity**: 🔴 **0% Complete** - No AI features implemented

#### Missing Features

❌ **Intelligent Scheduling**:
- No availability-based suggestions
- No optimal meeting time finder
- No automatic conflict resolution
- No travel time calculation

❌ **Natural Language Processing**:
- No natural language event creation
- No smart parsing of event details

❌ **Predictive Analytics**:
- No attendance prediction
- No resource usage forecasting
- No scheduling pattern analysis

❌ **Automated Workflows**:
- No automatic event creation from templates
- No workflow-triggered events
- No smart rescheduling suggestions

#### Recommended Actions (Future Phase)

**1. Smart Scheduling Assistant**:
```python
# AI service for scheduling recommendations
from openai import OpenAI

def suggest_meeting_times(
    participants: List[User],
    duration_minutes: int,
    preferred_date_range: Tuple[date, date],
    constraints: Dict = None
) -> List[Dict]:
    """Find optimal meeting times for participants."""

    # Get all participants' busy times
    busy_times = []
    for user in participants:
        user_events = get_user_calendar_events(
            user,
            date_from=preferred_date_range[0],
            date_to=preferred_date_range[1],
        )
        busy_times.extend([
            (event['start'], event['end'])
            for event in user_events
        ])

    # Find available slots
    available_slots = find_free_slots(
        busy_times,
        duration_minutes,
        preferred_date_range,
        constraints,
    )

    # Rank by preference (e.g., avoid early morning, prefer Tuesday-Thursday)
    ranked_slots = rank_time_slots(available_slots, constraints)

    return ranked_slots[:5]  # Top 5 suggestions
```

**2. Natural Language Event Creation**:
```python
def parse_natural_language_event(text: str, user: User) -> Dict:
    """Parse event details from natural language.

    Example: "Schedule meeting with DSWD next Tuesday at 2pm in Cotabato"
    """

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """You are an assistant that extracts event details from text.
                Return JSON with: title, date, time, duration, location, participants."""
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        response_format={"type": "json_object"},
    )

    event_data = json.loads(response.choices[0].message.content)

    # Validate and normalize
    event_data['date'] = parse_date(event_data.get('date'))
    event_data['time'] = parse_time(event_data.get('time'))
    # ...

    return event_data
```

---

### Area 5: Module-Specific Calendar Enhancements

**Maturity**: 🟡 **60% Complete** - Good coverage but missing some modules

#### Existing Integration

✅ **Coordination Module** (100% integrated):
- Events
- Stakeholder Engagements
- Communications follow-ups
- Partnerships (milestones)

✅ **MANA Module** (50% integrated):
- Baseline data collection
- Missing: Assessment schedules, Need follow-ups, Report deadlines

✅ **Staff Module** (75% integrated):
- Staff tasks
- Training enrollments
- Missing: Leave calendar, Performance review schedules

✅ **Policy Module** (60% integrated):
- Policy recommendation deadlines
- Missing: Consultation schedules, Review meetings

✅ **Planning Module** (80% integrated):
- MonitoringEntry milestones
- Workflow stages
- Missing: Budget hearing schedules, Reporting deadlines

#### Missing Modules

❌ **Communities Module** (0% integrated):
- No community-level calendars
- No barangay event schedules
- No cultural/religious observances

❌ **Recommendations Module** (minimal integration):
- Only policy deadlines
- Missing: Advocacy events, Follow-up meetings

#### Recommended Actions

**1. Integrate MANA Assessment Schedules**:
```python
# Add to calendar.py:build_calendar_payload()
if include_module("mana"):
    assessments = Assessment.objects.select_related("lead_facilitator")

    for assessment in assessments:
        milestones = [
            ("planning", assessment.planning_completion_date, "Planning Phase Complete"),
            ("data_collection", assessment.data_collection_end_date, "Data Collection End"),
            ("analysis", assessment.analysis_completion_date, "Analysis Complete"),
            ("reporting", assessment.report_due_date, "Report Due"),
        ]

        for category, date_value, label in milestones:
            if not date_value:
                continue

            # Create calendar entry
            # ...
```

**2. Add Community Calendar Support**:
```python
# communities/models.py
class CommunityEvent(models.Model):
    """Community-level events and observances."""

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name='events',
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    event_type = models.CharField(
        max_length=30,
        choices=[
            ('cultural', 'Cultural Celebration'),
            ('religious', 'Religious Observance'),
            ('meeting', 'Community Meeting'),
            ('training', 'Community Training'),
            ('disaster', 'Disaster/Emergency'),
            ('other', 'Other'),
        ]
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    all_day = models.BooleanField(default=True)

    location = models.CharField(max_length=255, blank=True)
    organizer = models.CharField(max_length=255, blank=True)

    is_public = models.BooleanField(
        default=True,
        help_text="Show on public calendar"
    )

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
```

**3. Staff Leave Calendar**:
```python
# common/models.py (or staff app)
class StaffLeave(models.Model):
    """Staff leave/vacation tracking."""

    staff = models.ForeignKey(User, on_delete=models.CASCADE)

    leave_type = models.CharField(
        max_length=20,
        choices=[
            ('vacation', 'Vacation Leave'),
            ('sick', 'Sick Leave'),
            ('emergency', 'Emergency Leave'),
            ('official', 'Official Business'),
        ]
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )

    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='approved_leaves',
        on_delete=models.SET_NULL,
    )

    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
```

---

## Module Integration Analysis

### Current Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Integrated Calendar System                    │
│                (src/common/services/calendar.py)                 │
│                  build_calendar_payload()                        │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Aggregates from:
             │
      ┌──────┴──────┬──────────┬──────────┬──────────┬──────────┐
      │             │          │          │          │          │
      ▼             ▼          ▼          ▼          ▼          ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Coordination│ │   MANA   │  │  Staff   │  │  Policy  │  │ Planning │  │Community │
│  Events    │ │Baseline  │  │  Tasks   │  │PolicyRec │  │Monitoring│  │  Events  │
│Engagements │ │Collection│  │ Training │  │Deadlines │  │Milestones│  │(proposed)│
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Proposed Enhanced Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  Universal Calendar Infrastructure                       │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Recurrence  │  │   Resources  │  │ Notifications│                  │
│  │   Patterns   │  │   & Booking  │  │  & Reminders │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Attendance  │  │   External   │  │  AI Assist   │                  │
│  │  & RSVP      │  │   Calendar   │  │  & Automation│                  │
│  │              │  │   Sync       │  │              │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
          ┌─────────────────────────────────────────────┐
          │     Unified Calendar Service Layer          │
          │   (Enhanced build_calendar_payload)         │
          └─────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌───────────┬───────────┬───────────┬───────────┬───────────┬───────────┐
    │           │           │           │           │           │           │
    ▼           ▼           ▼           ▼           ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Coord.  │ │ MANA   │ │ Staff  │ │ Policy │ │Planning│ │Community│ │Others  │
│Module  │ │ Module │ │ Module │ │ Module │ │ Module │ │ Module │ │        │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

### Integration Points

#### 1. Coordination → Calendar
**Current Flow**:
```
Event → calendar.py:build_calendar_payload()
StakeholderEngagement → calendar entries
Partnership milestones → calendar entries
```

**Enhanced Flow**:
```
Event → RecurringEventPattern (if recurring)
Event → CalendarResourceBooking (resources needed)
EventParticipant → RSVP status + attendance tracking
Event → ExternalCalendarSync (sync to Google/Outlook)
Event → CalendarNotification (reminders sent)
```

#### 2. MANA → Calendar
**Current Flow**:
```
BaselineDataCollection → calendar entries
```

**Enhanced Flow**:
```
Assessment → Planning/Data/Analysis/Reporting milestones
Need → Follow-up reminders (when status='in_progress')
BaselineDataCollection → Resource bookings (vehicles for field trips)
Assessment → Team member availability checks
```

#### 3. Staff → Calendar
**Current Flow**:
```
StaffTask → calendar entries
TrainingEnrollment → calendar entries
```

**Enhanced Flow**:
```
StaffTask → Recurring tasks (weekly status meetings)
StaffLeave → Leave calendar (proposed)
TrainingEnrollment → Resource booking (training rooms)
PerformanceReview → Review schedules (proposed)
```

#### 4. Policy → Calendar
**Current Flow**:
```
PolicyRecommendation → Deadline milestones
```

**Enhanced Flow**:
```
PolicyRecommendation → Review meetings
PolicyRecommendation → Consultation events
PolicyRecommendation → Implementation milestone tracking
```

#### 5. Planning → Calendar
**Current Flow**:
```
MonitoringEntry → Start/milestone/end dates
MonitoringEntryWorkflowStage → Stage deadlines
```

**Enhanced Flow**:
```
MonitoringEntry → Budget hearing schedules
MonitoringEntryWorkflowStage → Approval meetings
MonitoringEntry → Quarterly reporting deadlines
```

#### 6. Community → Calendar (Proposed)
**New Flow**:
```
CommunityEvent → Community-level calendar
OBCCommunity → Cultural/religious observances
CommunityEvent → Public-facing calendar (optional)
```

---

## Gap Analysis

### Critical Gaps Requiring Immediate Attention

#### Gap 1: No Recurring Events Support
**Impact**: High - Forces manual entry of weekly/monthly meetings
**Effort**: Medium - Requires new model and FullCalendar integration
**Priority**: 🔴 **Critical**

**Solution**: Implement `RecurringEventPattern` model (Area 1) in Milestone 1

---

#### Gap 2: No Resource Management System
**Impact**: High - Cannot prevent double-booking of vehicles/rooms
**Effort**: Medium - New models and booking workflow
**Priority**: 🟠 **High**

**Solution**: Implement `CalendarResource` and `CalendarResourceBooking` models (Area 1) in Milestone 2

---

#### Gap 3: Weak Notification System
**Impact**: High - Users miss important events
**Effort**: High - Email/SMS integration, Celery tasks
**Priority**: 🟠 **High**

**Solution**: Implement `CalendarNotification` and Celery tasks (Area 3) in Milestones 2-3

---

#### Gap 4: No Mobile Optimization
**Impact**: Medium - Poor experience for field staff
**Effort**: High - PWA development
**Priority**: 🟡 **Medium**

**Solution**: Create Progressive Web App (Area 2) in Milestone 4

---

#### Gap 5: Missing Module Coverage
**Impact**: Medium - Communities and some MANA features not in calendar
**Effort**: Low-Medium - Extend build_calendar_payload()
**Priority**: 🟡 **Medium**

**Solution**: Add MANA assessment schedules, community events (Area 5) in Milestone 2

---

#### Gap 6: No External Calendar Sync
**Impact**: Medium - Users must maintain two calendars
**Effort**: High - OAuth integration, sync logic
**Priority**: 🟡 **Medium**

**Solution**: Implement `ExternalCalendarSync` (Area 1) in Milestone 5

---

#### Gap 7: Limited Attendance Tracking
**Impact**: Low-Medium - Manual attendance at events
**Effort**: Medium - Enhance EventParticipant, add QR codes
**Priority**: 🟢 **Low**

**Solution**: Enhance attendance tracking (Area 1) in Milestone 3

---

#### Gap 8: No AI Features
**Impact**: Low - Nice-to-have for efficiency
**Effort**: Very High - ML models, NLP integration
**Priority**: 🟢 **Low**

**Solution**: AI scheduling assistant (Area 4) in Milestone 6+

---

## Integration Improvement Plan

### Milestone 1: Recurring Events & Foundation

**Goal**: Enable recurring events and strengthen calendar infrastructure

#### 1.1 Recurring Events Implementation

**Models to Create**:
```python
# common/models.py (or dedicated calendar app)
class RecurringEventPattern(models.Model):
    # (Full model spec from Area 1)
    # ...
```

**Model Extensions**:
```python
# Add to coordination.Event, StakeholderEngagement, etc.
recurrence_pattern = ForeignKey(RecurringEventPattern, ...)
recurrence_parent = ForeignKey('self', ...)
is_recurrence_exception = BooleanField(default=False)
```

**Views to Create**:
- `event_create_recurring` - Form with recurrence options
- `event_edit_instance` - Edit single instance vs. all future
- `recurring_pattern_preview` - Show dates that will be generated

**FullCalendar Integration**:
```javascript
// calendar.js enhancements
function handleRecurringEvents(events) {
    // Expand recurring events for display
    return events.map(event => {
        if (event.extendedProps.recurrence_pattern) {
            return generateRecurrenceInstances(event);
        }
        return event;
    }).flat();
}
```

---

#### 1.2 Enhanced Calendar Analytics

**Dashboard Enhancements**:
- Workload heatmap (events per day, color-coded by intensity)
- Module utilization chart (which modules use calendar most)
- Conflict rate tracking
- Average meeting duration by module

**Views to Create**:
- `calendar_analytics_dashboard` - Executive-level calendar insights
- `calendar_export_report` - Exportable analytics (PDF/Excel)

---

### Milestone 2: Resources, Notifications & Module Integration

#### 2.1 Resource Management System

**Models to Create**:
```python
class CalendarResource(models.Model):
    # (Full model spec from Area 1)
    # ...

class CalendarResourceBooking(models.Model):
    # (Full model spec from Area 1)
    # ...
```

**Views to Create**:
- `resource_list` - Browse available resources
- `resource_create` - Add new resource
- `resource_calendar` - See bookings for a resource
- `booking_request` - Request resource booking
- `booking_approve` - Approve/reject booking requests

**Integration with Events**:
```python
# When creating Event
def event_create(request):
    # ...
    if form.is_valid():
        event = form.save()

        # Create resource bookings
        for resource_id in request.POST.getlist('resources'):
            CalendarResourceBooking.objects.create(
                resource_id=resource_id,
                event_instance=event,
                start_datetime=event.start_datetime,
                end_datetime=event.end_datetime,
                booked_by=request.user,
            )
```

---

#### 2.2 Notification System

**Models to Create**:
```python
class CalendarNotification(models.Model):
    # (Full model spec from Area 3)
    # ...

class UserCalendarPreferences(models.Model):
    # (Full model spec from Area 3)
    # ...
```

**Celery Tasks**:
```python
# common/tasks.py
@shared_task
def send_calendar_notifications():
    # (Implementation from Area 3)
    # ...

@shared_task
def schedule_event_reminders(event_id, event_type):
    # (Implementation from Area 3)
    # ...

@shared_task
def send_daily_digest():
    """Send daily digest of upcoming events to subscribed users."""
    users = User.objects.filter(
        calendar_preferences__daily_digest=True
    )

    for user in users:
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        events = get_user_calendar_events(
            user,
            date_from=today,
            date_to=tomorrow,
        )

        if events:
            send_digest_email(user, events)
```

**Email Templates**:
- `emails/calendar_invitation.html` - Event invitation
- `emails/calendar_reminder.html` - Event reminder
- `emails/calendar_update.html` - Event changed
- `emails/calendar_cancellation.html` - Event cancelled
- `emails/calendar_daily_digest.html` - Daily digest

---

#### 2.3 Module Integration Expansion

**MANA Assessment Schedules**:
```python
# Extend calendar.py:build_calendar_payload()
if include_module("mana"):
    # Existing: BaselineDataCollection
    # NEW: Assessment milestones
    assessments = Assessment.objects.select_related("lead_facilitator")

    for assessment in assessments:
        # Create calendar entries for planning, data collection, analysis, reporting
        # (Implementation from Area 5)
```

**Community Calendar**:
```python
# Create CommunityEvent model (from Area 5)
# Add to calendar aggregation
if include_module("community"):
    community_events = CommunityEvent.objects.filter(
        is_public=True  # Only show public events
    )

    for event in community_events:
        # Add to calendar payload
        # ...
```

---

### Milestone 3: Attendance, Mobile & Advanced UX

#### 3.1 Attendance Tracking Enhancement

**Model Extensions**:
```python
# Extend coordination.EventParticipant
rsvp_status = CharField(...)
attendance_status = CharField(...)
check_in_time = DateTimeField(...)
check_out_time = DateTimeField(...)
check_in_method = CharField(...)  # manual, qr_code, nfc
```

**Views to Create**:
- `event_check_in` - Check in to event
- `event_generate_qr` - Generate QR code for event
- `event_scan_qr` - Scan QR code to check in
- `event_attendance_report` - View attendance statistics

**QR Code Integration**:
```python
import qrcode

def generate_event_qr_code(event_id):
    """Generate QR code for event check-in."""
    check_in_url = reverse('event_check_in', args=[event_id])
    qr = qrcode.make(check_in_url)

    # Save to temporary file or return as base64
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{qr_base64}"
```

---

#### 3.2 Mobile Optimization

**Progressive Web App (PWA)**:
```json
// manifest.json
{
  "name": "OOBC Calendar",
  "short_name": "OOBC Cal",
  "description": "Integrated calendar for OOBC operations",
  "start_url": "/oobc-management/calendar/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#059669",
  "icons": [
    {
      "src": "/static/icons/calendar-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icons/calendar-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**Service Worker**:
```javascript
// service-worker.js
const CACHE_NAME = 'oobc-calendar-v1';
const urlsToCache = [
  '/oobc-management/calendar/',
  '/static/common/vendor/fullcalendar/index.global.min.js',
  '/static/common/js/calendar.js',
  // ... other assets
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

**Mobile-Specific Features**:
- Touch-optimized gestures
- Swipe to change month
- Pull-to-refresh
- Compact mobile views
- Offline event viewing

---

#### 3.3 Advanced Calendar UX

**Drag & Drop Rescheduling**:
```javascript
// calendar.js enhancements
calendar = new FullCalendar.Calendar(calendarEl, {
    // ... existing config ...

    editable: true,
    eventDrop: function(info) {
        // Handle event rescheduling
        updateEventDateTime(
            info.event.id,
            info.event.start,
            info.event.end
        );
    },
    eventResize: function(info) {
        // Handle duration change
        updateEventDuration(
            info.event.id,
            info.event.start,
            info.event.end
        );
    },
});
```

**Quick Event Creation**:
```javascript
// Click date → inline form
calendar = new FullCalendar.Calendar(calendarEl, {
    dateClick: function(info) {
        showQuickEventModal(info.date);
    },
});

function showQuickEventModal(date) {
    // Show modal with pre-filled date
    const modal = document.getElementById('quick-event-modal');
    modal.querySelector('#event-date').value = date;
    modal.classList.remove('hidden');
}
```

**Keyboard Shortcuts**:
```javascript
document.addEventListener('keydown', (e) => {
    // n = new event
    if (e.key === 'n' && !e.ctrlKey && !e.metaKey) {
        openNewEventModal();
    }

    // t = today
    if (e.key === 't') {
        calendar.today();
    }

    // d/w/m = day/week/month view
    if (e.key === 'd') calendar.changeView('timeGridDay');
    if (e.key === 'w') calendar.changeView('timeGridWeek');
    if (e.key === 'm') calendar.changeView('dayGridMonth');
});
```

---

### Milestone 4: External Integration & Sharing

#### 4.1 External Calendar Sync

**Models to Create**:
```python
class ExternalCalendarSync(models.Model):
    # (Full model spec from Area 1)
    # ...
```

**OAuth Integration**:
```python
# views/calendar_sync.py
def google_calendar_authorize(request):
    """Initiate Google Calendar OAuth flow."""
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/calendar']
    )

    flow.redirect_uri = request.build_absolute_uri(
        reverse('google_calendar_callback')
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    request.session['oauth_state'] = state
    return redirect(authorization_url)

def google_calendar_callback(request):
    """Handle OAuth callback."""
    # Exchange code for tokens
    # Save to ExternalCalendarSync
    # ...
```

**Sync Service**:
```python
# services/calendar_sync.py
from googleapiclient.discovery import build

def sync_to_google_calendar(user):
    """Export OOBC events to user's Google Calendar."""
    sync_config = ExternalCalendarSync.objects.get(
        user=user,
        provider='google',
        is_active=True,
    )

    # Refresh token if needed
    if sync_config.token_expires_at < timezone.now():
        refresh_google_token(sync_config)

    # Get Google Calendar service
    credentials = get_google_credentials(sync_config)
    service = build('calendar', 'v3', credentials=credentials)

    # Get OOBC events
    events = get_user_calendar_events(
        user,
        modules=sync_config.sync_modules,
    )

    # Push to Google Calendar
    for event in events:
        google_event = convert_to_google_event(event)

        # Check if already synced
        if event.get('google_event_id'):
            # Update existing
            service.events().update(
                calendarId='primary',
                eventId=event['google_event_id'],
                body=google_event,
            ).execute()
        else:
            # Create new
            created = service.events().insert(
                calendarId='primary',
                body=google_event,
            ).execute()

            # Save Google event ID
            save_google_event_id(event['id'], created['id'])
```

**Celery Tasks**:
```python
@shared_task
def sync_external_calendars():
    """Periodic task to sync calendars."""
    syncs = ExternalCalendarSync.objects.filter(is_active=True)

    for sync in syncs:
        if sync.provider == 'google':
            sync_to_google_calendar(sync.user)
        elif sync.provider == 'microsoft':
            sync_to_outlook_calendar(sync.user)
```

---

#### 4.2 Calendar Sharing

**Models to Create**:
```python
class SharedCalendarLink(models.Model):
    # (Full model spec from Area 2)
    # ...
```

**Views to Create**:
- `calendar_share_create` - Create shareable link
- `calendar_share_view` - View shared calendar (public, no auth)
- `calendar_share_manage` - Manage shared links

**Public Calendar View**:
```python
def calendar_share_view(request, token):
    """Public calendar view via shared link."""
    try:
        link = SharedCalendarLink.objects.get(
            token=token,
            is_active=True,
        )
    except SharedCalendarLink.DoesNotExist:
        return HttpResponse("Invalid or expired link", status=404)

    # Check expiration
    if link.expires_at < timezone.now():
        return HttpResponse("Link has expired", status=410)

    # Check view limit
    if link.max_views and link.view_count >= link.max_views:
        return HttpResponse("View limit reached", status=403)

    # Increment view count
    link.view_count += 1
    link.save()

    # Build calendar payload with filters
    payload = build_calendar_payload(
        filter_modules=link.filter_modules,
        date_from=link.filter_date_from,
        date_to=link.filter_date_to,
    )

    return render(request, 'common/calendar_shared.html', {
        'calendar_events_json': json.dumps(payload['entries']),
        'link': link,
    })
```

---

### Milestone 5: AI & Advanced Automation

#### 5.1 Smart Scheduling Assistant

**Natural Language Event Creation**:
```python
# services/ai_calendar.py
def parse_natural_language_event(text: str, user: User) -> Dict:
    # (Implementation from Area 4)
    # ...
```

**Optimal Meeting Time Finder**:
```python
def suggest_meeting_times(
    participants: List[User],
    duration_minutes: int,
    preferred_date_range: Tuple[date, date],
    constraints: Dict = None
) -> List[Dict]:
    # (Implementation from Area 4)
    # ...
```

**Views to Create**:
- `smart_schedule_meeting` - AI-powered meeting scheduler
- `find_available_times` - Find optimal times for participants
- `parse_event_text` - Parse natural language to event

---

#### 5.2 Predictive Analytics

**Attendance Prediction**:
```python
def predict_attendance(event_id):
    """Predict attendance based on historical data."""
    event = Event.objects.get(pk=event_id)

    # Get similar past events
    similar_events = Event.objects.filter(
        event_type=event.event_type,
        community=event.community,
        status='completed',
    )

    # Calculate average attendance rate
    avg_rate = similar_events.aggregate(
        avg_rate=Avg('actual_participants') / Avg('expected_participants')
    )['avg_rate']

    predicted = int(event.expected_participants * avg_rate)

    return {
        'predicted_attendance': predicted,
        'confidence': calculate_confidence(similar_events.count()),
        'similar_events_count': similar_events.count(),
    }
```

**Resource Usage Forecasting**:
```python
def forecast_resource_demand(resource_id, months_ahead=3):
    """Forecast resource booking demand."""
    resource = CalendarResource.objects.get(pk=resource_id)

    # Get historical bookings
    bookings = resource.bookings.filter(
        status='approved',
        start_datetime__gte=timezone.now() - timedelta(days=365),
    )

    # Time series analysis (simple moving average)
    monthly_counts = bookings.extra(
        select={'month': 'EXTRACT(month FROM start_datetime)'}
    ).values('month').annotate(count=Count('id'))

    # Forecast future months
    # ... (implement forecasting logic)

    return forecast_data
```

---

## Implementation Roadmap

### Phased Delivery Plan

#### Phase 1: Foundation Enhancement (Milestone 1)
**Duration**: 3 weeks
**Deliverables**:
- ✅ `RecurringEventPattern` model
- ✅ Recurrence support in Event models
- ✅ Recurrence UI in FullCalendar
- ✅ Enhanced calendar analytics

**Success Criteria**:
- Users can create weekly/monthly recurring events
- Recurring events display correctly in calendar
- "Edit this instance" vs "Edit all future" works

---

#### Phase 2: Resources & Notifications (Milestone 2)
**Duration**: 4 weeks
**Deliverables**:
- ✅ `CalendarResource` and `CalendarResourceBooking` models
- ✅ Resource booking workflow
- ✅ `CalendarNotification` model
- ✅ Email notification system (Celery tasks)
- ✅ MANA assessment schedules integration
- ✅ Community calendar support

**Success Criteria**:
- Users can book vehicles/rooms for events
- System prevents resource double-booking
- Users receive email reminders 1 day and 1 hour before events
- MANA assessment deadlines appear in calendar
- Community events integrated

---

#### Phase 3: Attendance & Mobile (Milestone 3)
**Duration**: 3 weeks
**Deliverables**:
- ✅ Enhanced `EventParticipant` with RSVP and attendance
- ✅ QR code check-in system
- ✅ Progressive Web App (PWA)
- ✅ Mobile-optimized calendar interface
- ✅ Drag & drop rescheduling
- ✅ Quick event creation

**Success Criteria**:
- Event organizers can generate QR codes
- Participants can check in via QR scan
- Calendar works offline (view cached events)
- Calendar is installable on mobile devices
- Users can reschedule events via drag-and-drop

---

#### Phase 4: External Integration (Milestone 4)
**Duration**: 4 weeks
**Deliverables**:
- ✅ `ExternalCalendarSync` model
- ✅ Google Calendar OAuth integration
- ✅ Microsoft Outlook integration
- ✅ Two-way sync service (Celery tasks)
- ✅ `SharedCalendarLink` model
- ✅ Public calendar sharing

**Success Criteria**:
- Users can sync OOBC calendar to Google Calendar
- Users can import Google events to OOBC calendar
- Users can create shareable calendar links
- Shared calendars work without login

---

#### Phase 5: AI & Automation (Milestone 5)
**Duration**: 5 weeks
**Deliverables**:
- ✅ Natural language event parsing
- ✅ Smart meeting time suggestions
- ✅ Attendance prediction
- ✅ Resource demand forecasting

**Success Criteria**:
- Users can create events via natural language ("Meeting with DSWD next Tuesday 2pm")
- System suggests 3-5 optimal meeting times based on participant availability
- Attendance predictions are within 15% accuracy
- Resource forecasts help with capacity planning

---

## Technical Specifications

### Database Schema Changes

#### New Tables (8)

1. **`RecurringEventPattern`** - Recurrence rules (RFC 5545 compatible)
2. **`CalendarResource`** - Bookable resources (vehicles, rooms, equipment)
3. **`CalendarResourceBooking`** - Resource reservations
4. **`CalendarNotification`** - Scheduled notifications
5. **`UserCalendarPreferences`** - User notification preferences
6. **`ExternalCalendarSync`** - External calendar sync config
7. **`SharedCalendarLink`** - Temporary calendar sharing
8. **`CommunityEvent`** - Community-level events

#### Modified Tables (6)

1. **`coordination.Event`** - Add recurrence fields
2. **`coordination.StakeholderEngagement`** - Add recurrence fields
3. **`coordination.EventParticipant`** - Add RSVP and attendance fields
4. **`mana.Assessment`** - Add schedule milestone dates
5. **`common.StaffTask`** - Add recurrence fields
6. **`monitoring.MonitoringEntry`** - Add reporting schedule fields

#### New Foreign Key Relationships (8)

1. `Event` → `RecurringEventPattern` (recurrence rules)
2. `Event` → `Event` (parent-child for recurrence instances)
3. `CalendarResourceBooking` → `CalendarResource` (which resource)
4. `CalendarResourceBooking` → GenericForeignKey (which event)
5. `CalendarNotification` → GenericForeignKey (which event)
6. `CalendarNotification` → `User` (recipient)
7. `ExternalCalendarSync` → `User` (sync owner)
8. `SharedCalendarLink` → `User` (link creator)

---

### API Endpoints

#### Calendar Feed API
```python
# REST API endpoints
GET  /api/v1/calendar/events/  # List all calendar events (with filters)
POST /api/v1/calendar/events/  # Create event (with recurrence)
GET  /api/v1/calendar/events/{id}/  # Get single event
PUT  /api/v1/calendar/events/{id}/  # Update event
DELETE /api/v1/calendar/events/{id}/  # Delete event

GET  /api/v1/calendar/events/{id}/instances/  # Get recurrence instances
PUT  /api/v1/calendar/events/{id}/instances/{date}/  # Edit single instance

# Resource booking API
GET  /api/v1/calendar/resources/  # List resources
POST /api/v1/calendar/resources/{id}/book/  # Book resource
GET  /api/v1/calendar/resources/{id}/availability/  # Check availability

# External sync API
POST /api/v1/calendar/sync/google/authorize/  # Start OAuth
POST /api/v1/calendar/sync/google/callback/  # OAuth callback
POST /api/v1/calendar/sync/trigger/  # Manual sync trigger

# Sharing API
POST /api/v1/calendar/share/  # Create shared link
GET  /api/v1/calendar/share/{token}/  # View shared calendar
```

---

### Performance Optimizations

#### Database Indexes
```python
class Meta:
    indexes = [
        # Recurring events
        models.Index(fields=['recurrence_parent', 'start_date']),

        # Resource bookings
        models.Index(fields=['resource', 'start_datetime', 'end_datetime']),
        models.Index(fields=['status', 'start_datetime']),

        # Notifications
        models.Index(fields=['scheduled_for', 'status']),
        models.Index(fields=['recipient', 'scheduled_for']),

        # Calendar queries
        models.Index(fields=['start_date', 'end_date']),
        models.Index(fields=['module', 'status', 'start_date']),
    ]
```

#### Caching Strategy
```python
from django.core.cache import cache

def get_calendar_events_cached(user, date_from, date_to, modules):
    """Get calendar events with caching."""
    cache_key = f'calendar_events_{user.id}_{date_from}_{date_to}_{",".join(modules)}'

    cached = cache.get(cache_key)
    if cached:
        return cached

    payload = build_calendar_payload(
        filter_modules=modules,
        date_from=date_from,
        date_to=date_to,
    )

    # Cache for 5 minutes
    cache.set(cache_key, payload, timeout=300)

    return payload

# Invalidate cache when events change
@receiver(post_save, sender=Event)
def invalidate_calendar_cache(sender, instance, **kwargs):
    # Delete all calendar caches (or be more specific)
    cache.delete_pattern('calendar_events_*')
```

#### Query Optimization
```python
def build_calendar_payload_optimized(**kwargs):
    """Optimized calendar payload with select_related and prefetch_related."""

    # Coordination events
    events = Event.objects.select_related(
        'community',
        'organizer',
        'recurrence_pattern',
        'recurrence_parent',
    ).prefetch_related(
        'participants__user',
        'resource_bookings__resource',
        'documents',
    )

    # ... similar optimizations for other modules
```

---

### Security Considerations

#### Calendar Access Control
```python
def user_can_view_event(user, event):
    """Check if user can view event."""
    # Public events
    if event.is_public:
        return True

    # Event organizer
    if event.organizer == user:
        return True

    # Event participant
    if event.participants.filter(user=user).exists():
        return True

    # Staff with calendar permissions
    if user.has_perm('calendar.view_all_events'):
        return True

    return False

def user_can_edit_event(user, event):
    """Check if user can edit event."""
    # Event organizer
    if event.organizer == user:
        return True

    # Staff with calendar permissions
    if user.has_perm('calendar.change_event'):
        return True

    return False
```

#### External Calendar Sync Security
```python
# Encrypt OAuth tokens
from cryptography.fernet import Fernet

def encrypt_token(token):
    """Encrypt OAuth token before storing."""
    key = settings.CALENDAR_SYNC_ENCRYPTION_KEY
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """Decrypt OAuth token."""
    key = settings.CALENDAR_SYNC_ENCRYPTION_KEY
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()
```

---

### Testing Strategy

#### Unit Tests
```python
# tests/test_recurring_events.py
class RecurringEventTestCase(TestCase):
    def test_generate_weekly_recurrence(self):
        """Test generating weekly recurring events."""
        pattern = RecurringEventPattern.objects.create(
            recurrence_type='weekly',
            interval=1,
            by_weekday=[1, 3, 5],  # Mon, Wed, Fri
            count=10,
        )

        event = Event.objects.create(
            title="Team Standup",
            start_date=date(2025, 10, 6),  # Monday
            recurrence_pattern=pattern,
        )

        instances = event.generate_instances()

        self.assertEqual(len(instances), 10)
        self.assertEqual(instances[0].start_date.weekday(), 0)  # Monday
        self.assertEqual(instances[1].start_date.weekday(), 2)  # Wednesday

# tests/test_resource_booking.py
class ResourceBookingTestCase(TestCase):
    def test_prevent_double_booking(self):
        """Test resource cannot be double-booked."""
        resource = CalendarResource.objects.create(
            name="Conference Room A",
            resource_type='room',
        )

        event1 = Event.objects.create(
            title="Team Meeting",
            start_date=date(2025, 10, 7),
            start_time=time(10, 0),
        )

        booking1 = CalendarResourceBooking.objects.create(
            resource=resource,
            event_instance=event1,
            start_datetime=timezone.make_aware(
                datetime.combine(event1.start_date, event1.start_time)
            ),
            end_datetime=timezone.make_aware(
                datetime.combine(event1.start_date, event1.start_time) + timedelta(hours=1)
            ),
            booked_by=self.user,
        )

        # Try to book overlapping time
        event2 = Event.objects.create(
            title="Another Meeting",
            start_date=date(2025, 10, 7),
            start_time=time(10, 30),
        )

        booking2 = CalendarResourceBooking(
            resource=resource,
            event_instance=event2,
            start_datetime=timezone.make_aware(
                datetime.combine(event2.start_date, event2.start_time)
            ),
            end_datetime=timezone.make_aware(
                datetime.combine(event2.start_date, event2.start_time) + timedelta(hours=1)
            ),
            booked_by=self.user,
        )

        with self.assertRaises(ValidationError):
            booking2.full_clean()
```

#### Integration Tests
```python
# tests/test_calendar_sync.py
class CalendarSyncTestCase(TestCase):
    @patch('googleapiclient.discovery.build')
    def test_google_calendar_export(self, mock_build):
        """Test exporting events to Google Calendar."""
        # Mock Google Calendar API
        mock_service = Mock()
        mock_build.return_value = mock_service

        sync = ExternalCalendarSync.objects.create(
            user=self.user,
            provider='google',
            access_token='test_token',
            sync_direction='export_only',
            sync_modules=['coordination'],
        )

        event = Event.objects.create(
            title="Test Event",
            start_date=date(2025, 10, 7),
            organizer=self.user,
        )

        # Run sync
        sync_to_google_calendar(self.user)

        # Verify API was called
        mock_service.events().insert.assert_called_once()
```

---

## Success Metrics

### Quantitative Metrics

**Calendar Usage**:
- ✅ 500+ events/engagements in calendar per quarter
- ✅ 90%+ of events have location and participants specified
- ✅ 50%+ of users access calendar weekly

**Recurring Events**:
- ✅ 100+ recurring event patterns created
- ✅ 30%+ of meetings set as recurring

**Resource Management**:
- ✅ 100% of vehicle/room bookings go through system
- ✅ <5% resource booking conflicts
- ✅ 80%+ resource utilization rate

**Notifications**:
- ✅ 90%+ event reminder open rate
- ✅ 70%+ daily digest subscription rate
- ✅ <2% notification unsubscribe rate

**External Sync**:
- ✅ 30%+ of staff sync with external calendar
- ✅ 95%+ sync success rate

**Attendance**:
- ✅ 80%+ of events use digital check-in
- ✅ Attendance tracking within 5% of manual count

**Mobile**:
- ✅ 40%+ of calendar views from mobile devices
- ✅ 4+ star rating on PWA experience

### Qualitative Metrics

**User Satisfaction**:
- ✅ Positive feedback on calendar usability
- ✅ Reduced scheduling conflicts reported
- ✅ Staff report calendar saves time

**Integration**:
- ✅ Seamless experience across modules
- ✅ No duplicate calendar systems maintained
- ✅ Calendar is "single source of truth" for scheduling

**Efficiency**:
- ✅ 50% reduction in scheduling emails
- ✅ 30% reduction in resource booking conflicts
- ✅ Automated reminders reduce no-shows

---

## Conclusion

### Summary of Findings

The existing calendar implementation provides **strong foundations** (70% complete) with:

**Strengths**:
- ✅ Centralized calendar service aggregating 7 modules
- ✅ FullCalendar integration with filtering and analytics
- ✅ Workflow actions and conflict detection
- ✅ Export capabilities (JSON, ICS, printable)

**Critical Gaps Addressed by This Plan**:
- ✅ Recurring events support (Milestone 1)
- ✅ Resource management system (Milestone 2)
- ✅ Notification & reminder infrastructure (Milestone 2)
- ✅ Enhanced attendance tracking (Milestone 3)
- ✅ Mobile optimization (PWA) (Milestone 3)
- ✅ External calendar sync (Google, Outlook) (Milestone 4)
- ✅ Calendar sharing capabilities (Milestone 4)
- ✅ AI-powered scheduling assistance (Milestone 5)

### Integration Philosophy

This plan emphasizes **truly integrated, organization-wide calendar** through:

1. **Universal Infrastructure**: Shared models (recurrence, resources, notifications) usable by all modules
2. **Consistent UX**: Same calendar interface for all event types
3. **Smart Automation**: AI-powered scheduling, conflict detection, reminders
4. **External Connectivity**: Sync with Google/Outlook, shareable links
5. **Mobile-First**: PWA for field staff and community leaders
6. **Comprehensive Coverage**: All modules integrated (coordination, MANA, staff, policy, planning, community)

### Next Steps

1. **Review & Approval**: Present this plan to OOBC leadership
2. **Prioritization**: Confirm milestone sequencing based on urgency
3. **Sprint Planning**: Break Milestone 1 into 2-week sprints
4. **Kickoff**: Begin Phase 1 with recurring events implementation
5. **Iterative Delivery**: Deploy features incrementally, gather feedback

---

**Document Version**: 1.0
**Last Updated**: October 1, 2025
**Next Review**: After Milestone 1 completion
**Status**: Ready for Implementation

---

## 88 Actionable Implementation Tasks

### Phase 1: Models & Database (Tasks 1-15)

1. ✅ Create RecurringEventPattern model in common/models.py with RFC 5545 compatible fields
2. ✅ Add recurrence fields to coordination.Event model (recurrence_pattern, recurrence_parent, is_recurrence_exception)
3. ✅ Add recurrence fields to coordination.StakeholderEngagement model
4. ✅ Add recurrence fields to common.StaffTask model
5. ✅ Create CalendarResource model for bookable resources (vehicles, equipment, rooms)
6. ✅ Create CalendarResourceBooking model with GenericForeignKey for polymorphic event linking
7. ✅ Create CalendarNotification model for scheduled event reminders and alerts
8. ✅ Create UserCalendarPreferences model for notification settings and preferences
9. ✅ Create ExternalCalendarSync model for Google/Outlook integration
10. ✅ Create SharedCalendarLink model for temporary public calendar access
11. ✅ Create CommunityEvent model in communities app for community-level events
12. ✅ Create StaffLeave model for staff vacation/leave tracking
13. ✅ Enhance EventParticipant model with RSVP status, attendance status, check-in/check-out times
14. ✅ Create database migrations for all new models and field additions
15. ✅ Add database indexes for performance optimization (recurrence, bookings, notifications)

### Phase 2: Views & Controllers (Tasks 16-34)

16. ✅ Create event_create_recurring view for recurring event creation form
17. ✅ Create event_edit_instance view with 'Edit this instance' vs 'Edit all future' logic
18. ✅ Create recurring_pattern_preview view to show generated recurrence dates
19. ✅ Create resource_list view for browsing available resources
20. ✅ Create resource_create view for adding new resources
21. ✅ Create resource_calendar view for viewing resource bookings
22. ✅ Create booking_request view for requesting resource bookings
23. ✅ Create booking_approve view for approving/rejecting booking requests
24. ✅ Create event_check_in view for manual event attendance check-in
25. ✅ Create event_generate_qr view for generating QR codes for events
26. ✅ Create event_scan_qr view for QR code scanning check-in
27. ✅ Create event_attendance_report view for attendance statistics
28. ✅ Create calendar_share_create view for creating shareable calendar links
29. ✅ Create calendar_share_view view for public access to shared calendars
30. ✅ Create calendar_share_manage view for managing shared links
31. ✅ Create google_calendar_authorize view for OAuth flow initiation
32. ✅ Create google_calendar_callback view for OAuth callback handling
33. ✅ Create calendar_analytics_dashboard view for executive-level insights
34. ✅ Create smart_schedule_meeting view for AI-powered meeting scheduler

### Phase 3: Services & Business Logic (Tasks 35-49)

35. ✅ Enhance build_calendar_payload() to include MANA assessment schedules (planning, data collection, analysis, reporting milestones)
36. ✅ Enhance build_calendar_payload() to include community events
37. ✅ Enhance build_calendar_payload() to include staff leave calendar
38. ✅ Enhance build_calendar_payload() to expand recurring events into instances
39. ✅ Create Celery task send_calendar_notifications for processing pending notifications
40. ✅ Create Celery task schedule_event_reminders for creating reminder notifications
41. ✅ Create Celery task send_daily_digest for daily event digests
42. ✅ Create Celery task send_weekly_digest for weekly event digests
43. ✅ Create Celery task sync_external_calendars for periodic calendar sync
44. ✅ Create calendar sync service sync_to_google_calendar() for exporting to Google Calendar
45. ✅ Create calendar sync service sync_from_google_calendar() for importing from Google Calendar
46. ✅ Create calendar sync service sync_to_outlook_calendar() for Outlook integration
47. ✅ Create AI service parse_natural_language_event() using OpenAI for NLP event creation
48. ✅ Create AI service suggest_meeting_times() for optimal scheduling recommendations
49. ✅ Create AI service predict_attendance() for attendance forecasting

### Phase 4: AI & Advanced Features (Tasks 50-56)

50. ✅ Create AI service forecast_resource_demand() for resource usage forecasting
51. ✅ Create email template calendar_invitation.html for event invitations
52. ✅ Create email template calendar_reminder.html for event reminders
53. ✅ Create email template calendar_update.html for event changes
54. ✅ Create email template calendar_cancellation.html for event cancellations
55. ✅ Create email template calendar_daily_digest.html for daily digests
56. ✅ Create email template calendar_weekly_digest.html for weekly digests

### Phase 5: Frontend & UX (Tasks 57-67)

57. ✅ Enhance FullCalendar JavaScript to handle recurring event display and expansion
58. ✅ Add drag-and-drop rescheduling to FullCalendar configuration
59. ✅ Add event resize (duration change) to FullCalendar configuration
60. ✅ Add quick event creation on date click to FullCalendar
61. ✅ Add keyboard shortcuts (n=new, t=today, d/w/m=views) to calendar interface
62. ✅ Add agenda/list view option to calendar interface
63. ✅ Add multi-week view option to calendar interface
64. ✅ Add year view option to calendar interface
65. ✅ Create PWA manifest.json for mobile app installation
66. ✅ Create service-worker.js for offline calendar support
67. ✅ Add mobile-optimized touch gestures (swipe to change month, pull-to-refresh)

### Phase 6: Mobile, API & Infrastructure (Tasks 68-88)

68. ✅ Create mobile-specific compact calendar views
69. ✅ Add advanced filter UI (date range, status, priority, community, organizer, full-text search)
70. ✅ Add saved filter presets functionality
71. ✅ Implement caching strategy for calendar queries (5-minute cache with invalidation)
72. ✅ Add select_related and prefetch_related optimizations to calendar queries
73. ✅ Create REST API endpoints for calendar events (list, create, update, delete, instances)
74. ✅ Create REST API endpoints for resource booking (list, book, availability)
75. ✅ Create REST API endpoints for external sync (authorize, callback, trigger)
76. ✅ Create REST API endpoints for calendar sharing (create, view, manage)
77. ✅ Implement user_can_view_event permission checking
78. ✅ Implement user_can_edit_event permission checking
79. ✅ Add OAuth token encryption for external calendar sync credentials
80. ✅ Create unit tests for recurring event generation
81. ✅ Create unit tests for resource double-booking prevention
82. ✅ Create integration tests for Google Calendar sync
83. ✅ Create integration tests for notification delivery
84. ✅ Create integration tests for attendance tracking
85. ✅ Update URL patterns for all new calendar views
86. ✅ Configure Celery beat schedule for periodic tasks (notifications, digests, sync)
87. ✅ Add calendar-specific environment variables to settings (sync encryption key, OAuth credentials)
88. ✅ Update documentation with calendar feature guides
