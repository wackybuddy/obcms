# OOBC Calendar System - User Guide

**Version:** 1.0
**Last Updated:** October 1, 2025
**Audience:** OOBC Staff, MANA Facilitators, Administrators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Viewing the Calendar](#viewing-the-calendar)
4. [Managing Events](#managing-events)
5. [Recurring Events](#recurring-events)
6. [Resource Booking](#resource-booking)
7. [Staff Leave Management](#staff-leave-management)
8. [Calendar Sharing](#calendar-sharing)
9. [Event Attendance](#event-attendance)
10. [Notification Preferences](#notification-preferences)
11. [Mobile Access](#mobile-access)
12. [Troubleshooting](#troubleshooting)
13. [FAQ](#faq)

---

## Introduction

The OOBC Calendar System is an integrated scheduling and coordination platform designed to help the Office for Other Bangsamoro Communities manage:

- **Coordination Events** - Meetings, workshops, and activities with stakeholders
- **Resource Bookings** - Meeting rooms, vehicles, and equipment
- **Staff Leave** - Vacation, sick leave, and time-off tracking
- **MANA Assessments** - Field work and assessment schedules
- **Shared Calendars** - Public access for stakeholders and partners

### Key Features

✅ **Unified Calendar View** - See all events, bookings, and leave in one place
✅ **Drag-and-Drop Scheduling** - Quickly reschedule events by dragging
✅ **Recurring Events** - Set up daily, weekly, or monthly recurring activities
✅ **QR Code Check-In** - Track event attendance with mobile QR scanning
✅ **Email Notifications** - Automatic reminders and updates
✅ **Calendar Sharing** - Share public calendars with stakeholders
✅ **Mobile Responsive** - Access from any device

---

## Getting Started

### Accessing the Calendar

1. **Log in** to the OOBC Management System at `https://your-oobc-domain.gov.ph`
2. From the **Dashboard**, click **"OOBC Management"** in the navigation menu
3. Select **"Calendar"** to view the integrated calendar

**Quick Links:**
- Main Calendar: `/oobc-management/calendar/`
- Coordination Calendar: `/coordination/calendar/`
- Resource Booking: `/oobc-management/calendar/resources/`
- Staff Leave: `/oobc-management/staff/leave/`

### User Roles

Different roles have different permissions:

| Role | Permissions |
|------|------------|
| **Staff Member** | View calendar, create events, request resources/leave |
| **MANA Facilitator** | + Schedule assessments, manage field activities |
| **Administrator** | + Approve bookings/leave, manage resources, share calendars |
| **Superuser** | Full access to all calendar features |

---

## Viewing the Calendar

### Calendar Views

The calendar supports multiple view modes:

- **Month View** - See the entire month at a glance (default)
- **Week View** - Detailed weekly schedule with time slots
- **List View** - Chronological list of upcoming events

**Switch Views:**
- Click the view buttons in the top-right corner of the calendar
- Use keyboard shortcuts: `M` (Month), `W` (Week), `L` (List)

### Calendar Color Coding

Events are color-coded by type:

- 🟦 **Blue** - Coordination events and meetings
- 🟩 **Green** - Resource bookings (rooms, vehicles)
- 🟧 **Orange** - Staff leave and time-off
- 🟪 **Purple** - MANA assessments and field work
- 🟥 **Red** - Holidays (Jumu'ah Fridays are marked in red)

### Recurring Event Indicators

Events that repeat have a small 🔁 icon next to the title.

### Filtering Calendar Items

Use the filter controls to show/hide specific types:

1. Click **"Filter"** in the calendar toolbar
2. Toggle checkboxes:
   - ☑️ Events
   - ☑️ Resource Bookings
   - ☑️ Staff Leave
   - ☑️ MANA Activities
3. Click **"Apply"** to update the view

---

## Managing Events

### Creating a New Event

1. Navigate to **Coordination > Calendar**
2. Click **"+ New Event"** button
3. Fill in the event details:
   - **Title** - Short descriptive name
   - **Description** - Additional details
   - **Start Date** - Event date
   - **Start Time** - Event time (leave blank for all-day event)
   - **Duration** - How long the event will last
   - **Status** - Planned, Scheduled, Completed, Cancelled
   - **Community** - Associated OBC (optional)
   - **Participants** - Invitees and attendees
4. Click **"Save Event"**

**Tip:** You can also create events by clicking directly on a date in the calendar!

### Editing an Event

**Method 1: Quick Reschedule (Drag-and-Drop)**
1. Click and drag an event to a new date/time
2. The system will update automatically
3. A confirmation message will appear

**Method 2: Full Edit**
1. Click the event on the calendar
2. Click **"Edit Event"** in the popup
3. Update the details
4. Click **"Save Changes"**

**Permission Note:** You can only edit events you created or if you're an administrator.

### Deleting an Event

1. Click the event on the calendar
2. Click **"Delete Event"**
3. Confirm the deletion
4. The event will be permanently removed

⚠️ **Warning:** Deleting an event also removes all participant records and attendance data.

### Event Details Popup

Clicking any event shows a popup with:
- Event title and description
- Date, time, and duration
- Status and community
- Participant list
- Quick action buttons (Edit, Delete, QR Code, Attendance)

---

## Recurring Events

### Creating Recurring Events

Recurring events repeat on a schedule (daily, weekly, monthly, yearly).

1. Click **"+ New Event"** > **"Create Recurring Event"**
2. Fill in base event details
3. Configure recurrence pattern:

**Daily Recurrence:**
- Every X days
- Example: "Every 2 days" (Mon, Wed, Fri)

**Weekly Recurrence:**
- Select days of the week
- Example: "Every Monday and Wednesday"
- Interval: "Every 2 weeks" for bi-weekly

**Monthly Recurrence:**
- Day of month: "15th of every month"
- OR Day of week: "Second Tuesday of every month"

**Yearly Recurrence:**
- Specific date: "October 1st every year"

4. Set end condition:
   - **End Date** - Stop recurring after specific date
   - **Number of Occurrences** - Stop after X events
   - **Never** - Continue indefinitely

5. Click **"Create Recurring Series"**

### Editing Recurring Events

When you edit a recurring event, you'll be asked:

**Option 1: Edit This Event Only**
- Changes only the selected occurrence
- Other occurrences remain unchanged
- Creates an "exception" to the pattern

**Option 2: Edit All Future Events**
- Updates this event and all future occurrences
- Past occurrences remain unchanged

**Option 3: Edit Entire Series**
- Updates all occurrences (past and future)
- Changes the recurrence pattern itself

### Deleting Recurring Events

Similar to editing, you can:
- **Delete This Event Only** - Remove single occurrence
- **Delete All Future Events** - Cancel from this point forward
- **Delete Entire Series** - Remove all occurrences

### Viewing Recurring Patterns

1. Click a recurring event
2. Look for the 🔁 icon
3. Click **"View Series Details"** to see:
   - Recurrence pattern
   - Total occurrences
   - Next 10 occurrences
   - Exception dates

---

## Resource Booking

### Viewing Available Resources

1. Navigate to **OOBC Management > Calendar > Resources**
2. Browse the resource directory:
   - 🏢 **Meeting Rooms** - Conference rooms, training halls
   - 🚗 **Vehicles** - Service vehicles for field work
   - 💻 **Equipment** - Projectors, laptops, cameras
   - 🏨 **Facilities** - Guest houses, event venues

### Requesting a Resource Booking

1. Click **"Book Resource"** or select a resource
2. Fill in booking details:
   - **Resource** - Select from dropdown
   - **Start Date/Time** - When you need it
   - **End Date/Time** - When you'll return it
   - **Purpose** - Brief description of use
   - **Notes** - Any special requirements
3. Click **"Submit Booking Request"**

**Booking Status:**
- 🟡 **Pending** - Waiting for admin approval
- 🟢 **Approved** - Confirmed, resource reserved
- 🔴 **Rejected** - Request denied (see admin notes)
- ⚫ **Cancelled** - You or admin cancelled

### Checking Resource Availability

Before booking, check the resource calendar:

1. Click on a resource
2. View **"Resource Calendar"**
3. See all existing bookings
4. Find an available time slot

**Conflict Detection:**
The system automatically prevents double-booking. If your requested time conflicts with an approved booking, you'll see an error message.

### Managing Your Bookings

**View Your Bookings:**
1. Go to **OOBC Management > Calendar > Bookings**
2. See list of all your bookings:
   - Pending requests
   - Upcoming bookings
   - Past bookings

**Cancel a Booking:**
1. Find the booking in your list
2. Click **"Cancel Booking"**
3. Confirm cancellation
4. Admin will be notified

### Admin: Approving Bookings

If you're an administrator:

1. Go to **OOBC Management > Calendar > Bookings**
2. Filter by **"Pending"** status
3. Review each request:
   - Check for conflicts
   - Verify purpose and requester
4. Click **"Approve"** or **"Reject"**
5. Add admin notes (required for rejection)
6. Requester will receive email notification

---

## Staff Leave Management

### Requesting Leave

1. Navigate to **OOBC Management > Staff > Leave**
2. Click **"Request Leave"**
3. Fill in leave details:
   - **Leave Type:**
     - Vacation Leave (VL)
     - Sick Leave (SL)
     - Emergency Leave
     - Bereavement Leave
     - Maternity/Paternity Leave
   - **Start Date** - First day of leave
   - **End Date** - Last day of leave
   - **Reason** - Brief explanation
   - **Attachments** - Medical certificate (if applicable)
4. Click **"Submit Leave Request"**

**Leave Balance:**
Your current leave balance is displayed at the top of the form:
- Vacation Leave: XX days remaining
- Sick Leave: XX days remaining

### Checking Leave Status

**Your Leave Dashboard:**
1. Go to **OOBC Management > Staff > Leave**
2. View all your leave requests:
   - 🟡 Pending Approval
   - 🟢 Approved
   - 🔴 Rejected
   - ⚫ Cancelled

**On Calendar:**
Approved leave appears on the calendar in **orange** with your name.

### Cancelling Leave Request

For pending or approved leave:

1. Find the leave request
2. Click **"Cancel Request"**
3. Confirm cancellation
4. Your leave balance will be restored

⚠️ **Note:** Cancelling approved leave requires admin notification.

### Admin: Approving Leave

Administrators can manage all staff leave:

1. Go to **OOBC Management > Staff > Leave**
2. Filter by **"Pending"** status
3. Review request details:
   - Staff member and leave type
   - Dates and duration
   - Reason
   - Current leave balance
4. Check calendar for conflicts
5. Click **"Approve"** or **"Reject"**
6. Add admin notes
7. Staff member receives email notification

**Leave Balance Tracking:**
- System automatically deducts from balance on approval
- Balance is restored on rejection/cancellation
- View all staff balances in **Staff Management**

---

## Calendar Sharing

### Creating a Public Calendar Link

Administrators can create shareable calendar links for stakeholders:

1. Navigate to **OOBC Management > Calendar > Share**
2. Click **"Create Share Link"**
3. Configure sharing options:
   - **Description** - Purpose of this link (e.g., "Q4 2025 Public Events")
   - **Expiration Date** - When link stops working (default: 30 days)
   - **Filter Modules** - What to include:
     - ☑️ Coordination Events
     - ☑️ Resource Bookings
     - ☑️ Staff Leave (usually unchecked for public)
     - ☑️ MANA Activities
4. Click **"Generate Link"**

**Security Note:** Sensitive information (internal notes, private details) is automatically removed from shared calendars.

### Managing Share Links

**View All Share Links:**
1. Go to **OOBC Management > Calendar > Share > Manage**
2. See list of all active links:
   - Description and created date
   - Expiration status
   - View count (how many times accessed)
   - Active/Inactive toggle

**Share Link Actions:**
- **Copy Link** - Click 📋 to copy URL to clipboard
- **Toggle Active** - Temporarily disable without deleting
- **Extend Expiration** - Add more days
- **Delete** - Permanently remove link

### Accessing Shared Calendars

No login required for public calendars:

1. Open the shared link URL
2. View read-only calendar
3. Filter by event type
4. Export to iCal (Add to Google Calendar, Outlook)

**Public Calendar Features:**
- Month, Week, List views
- Color-coded events
- Event details (title, date, time, location)
- Export to personal calendar

---

## Event Attendance

### QR Code Check-In

For event organizers to track attendance:

**1. Generate QR Code:**
1. Open your event on the calendar
2. Click **"QR Code"**
3. Download or display QR code image
4. Print or project at event venue

**2. Participant Scan:**
1. Participants scan QR code with phone camera
2. Opens check-in page
3. Confirms attendance
4. System records timestamp

**3. Manual Check-In:**
If QR scanning isn't available:

1. Click event > **"Check In Participants"**
2. Search for participant name
3. Click **"Check In"** button
4. Repeat for all attendees

### Viewing Attendance Reports

**Event Attendance Report:**
1. Click event on calendar
2. Select **"Attendance Report"**
3. View statistics:
   - Total invited vs attended
   - Check-in times
   - By organization breakdown
   - On-time vs late arrivals

**Export Attendance:**
- Download as CSV for records
- Print summary report
- Email to stakeholders

### Attendance Analytics

For administrators:

1. Go to **OOBC Management > Analytics > Attendance**
2. View system-wide metrics:
   - Average attendance rate
   - Most attended events
   - Organization participation trends
   - Time analysis (peak check-in times)

---

## Notification Preferences

### Configuring Your Notifications

Customize how and when you receive calendar notifications:

1. Navigate to **OOBC Management > Calendar > Preferences**
2. Configure settings:

**Reminder Times:**
- Add custom reminder intervals (15, 30, 60, 120, 1440 minutes before event)
- Receive multiple reminders for important events

**Notification Channels:**
- ☑️ Email Notifications
- ☑️ Push Notifications (if enabled)
- ☑️ SMS Alerts (if available)

**Quiet Hours:**
- Start Time: 10:00 PM (default)
- End Time: 7:00 AM (default)
- No notifications during this period

**Email Digests:**
- ☑️ Daily Digest (7:00 AM) - Summary of today + upcoming
- ☑️ Weekly Digest (Monday 8:00 AM) - Week ahead preview
- ☑️ Monthly Digest (1st of month) - Month overview

**Timezone:**
- Default: Asia/Manila
- Adjust if working remotely

3. Click **"Save Preferences"**

### Email Notification Types

You'll receive emails for:

- **Event Invitations** - When added as participant
- **Event Reminders** - Based on your reminder times
- **Event Changes** - When event is rescheduled
- **Booking Status** - Approval/rejection of your resource requests
- **Leave Status** - Approval/rejection of leave requests
- **Daily/Weekly Digests** - Schedule summaries

**Unsubscribe:**
- Click "Unsubscribe" link in any email
- Or disable specific types in preferences

---

## Mobile Access

### Mobile-Responsive Interface

The calendar works on all devices:

**Smartphone:**
- Touch-friendly interface
- Swipe to navigate months
- Tap events for details
- Quick actions menu

**Tablet:**
- Split-view month/detail
- Optimized for larger screens
- Landscape mode support

### QR Scanning with Mobile

**Using Built-in Camera:**
1. Open phone camera app
2. Point at event QR code
3. Tap notification to open check-in
4. Confirm attendance

**Alternative: Any QR Scanner App**
- Download free QR scanner
- Scan event QR code
- Opens browser to check-in page

### Mobile Tips

✅ **Add to Home Screen** - Save calendar as app icon
✅ **Enable Notifications** - Allow browser notifications
✅ **Use Landscape Mode** - Better week view on tablets
✅ **Offline Access** - Coming soon (PWA feature)

---

## Troubleshooting

### Common Issues

**Problem: Calendar not loading**
- ✅ Check internet connection
- ✅ Refresh page (Ctrl+R or Cmd+R)
- ✅ Clear browser cache
- ✅ Try different browser (Chrome, Firefox, Safari)

**Problem: Can't see my events**
- ✅ Check filter settings - ensure event types are enabled
- ✅ Verify date range - switch to Month view
- ✅ Confirm event was saved - check event list

**Problem: Drag-and-drop not working**
- ✅ Ensure you have edit permissions
- ✅ Try using Edit button instead
- ✅ Check if event is locked (past events can't be moved)

**Problem: Not receiving email notifications**
- ✅ Check spam/junk folder
- ✅ Verify email in profile settings
- ✅ Check notification preferences are enabled
- ✅ Contact admin if emails still don't arrive

**Problem: QR code not scanning**
- ✅ Ensure good lighting on QR code
- ✅ Try manual check-in instead
- ✅ Use different QR scanner app
- ✅ Download and print clearer QR code

**Problem: Booking request rejected**
- ✅ Read admin notes for reason
- ✅ Check for resource conflicts
- ✅ Contact admin for clarification
- ✅ Submit new request with adjustments

### Getting Help

**Within System:**
- Click **Help** icon (?) in calendar toolbar
- View tooltips by hovering over buttons
- Check field hints in forms

**Contact Support:**
- Email: support@oobc.gov.ph
- Phone: [Office Number]
- Submit ticket: **Dashboard > Help > Submit Issue**

**Training Resources:**
- Video tutorials: [Link to training videos]
- Quick reference guide: [PDF download]
- FAQs: See below

---

## FAQ

**Q: Can I create private events?**
A: Yes. When creating an event, only invited participants can see details. Events don't appear in shared public calendars unless explicitly included.

**Q: How far in advance can I book resources?**
A: Resources can be booked up to 6 months in advance. For longer-term reservations, contact an administrator.

**Q: What happens if I'm late cancelling a booking?**
A: Cancellations should be made at least 24 hours before start time. Late cancellations may affect future booking priority.

**Q: Can I see other staff members' calendars?**
A: Administrators can view all calendars. Regular staff can only see events they're invited to or public events.

**Q: How do recurring events handle holidays?**
A: By default, recurring events skip Philippine national holidays. You can override this when creating the series.

**Q: Can I export calendar to Outlook/Google Calendar?**
A: Yes! Click **Export** > **iCal Feed** and subscribe in your calendar app. Updates sync automatically.

**Q: What if I have overlapping events?**
A: The system allows overlapping events (you might have multiple responsibilities). You'll see a warning but can proceed.

**Q: How long are QR codes valid?**
A: QR codes for check-in are valid from 1 hour before event start until event end time.

**Q: Can I request leave for half-days?**
A: Yes. Enter same date for start and end, and specify "Half-Day" in notes. Your leave balance will be deducted by 0.5 days.

**Q: What's the difference between 'Planned' and 'Scheduled' status?**
A: **Planned** = tentative, dates not final. **Scheduled** = confirmed, participants invited. Use Planned for early coordination.

**Q: Can I edit events created by others?**
A: Only if you're an administrator or the event organizer added you as co-organizer. Otherwise, you can only view.

**Q: How do I report a bug or suggest a feature?**
A: Go to **Dashboard > Help > Report Issue** or email support@oobc.gov.ph with "Calendar Feature Request" in subject.

---

## Quick Reference Card

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `N` | New event |
| `M` | Month view |
| `W` | Week view |
| `L` | List view |
| `T` | Today (jump to current date) |
| `←` `→` | Previous/Next month |
| `/` | Search events |
| `?` | Show help |

### Status Indicators

| Color | Meaning |
|-------|---------|
| 🟢 Green | Approved/Confirmed |
| 🟡 Yellow | Pending/Awaiting Action |
| 🔴 Red | Rejected/Cancelled/Overdue |
| 🔵 Blue | In Progress/Active |
| ⚫ Grey | Draft/Inactive |

### Best Practices

✅ **DO:**
- Create events as soon as dates are confirmed
- Set multiple reminders for critical events
- Check resource availability before booking
- Submit leave requests 2+ weeks in advance
- Use clear, descriptive event titles
- Add participants early for better coordination

❌ **DON'T:**
- Create duplicate events
- Book resources "just in case" (blocks others)
- Wait until last minute for leave requests
- Use all-caps in titles
- Delete events with attendance records
- Share calendar links publicly without admin approval

---

## Glossary

**All-Day Event** - Event without specific time, shows at top of calendar day
**Booking Conflict** - Overlap of approved resource bookings
**Check-In** - Recording participant arrival at event
**iCal** - Calendar format for importing/exporting to other apps
**Occurrence** - Single instance of a recurring event
**QR Code** - Scannable code for quick event check-in
**Recurrence Pattern** - Rule defining how event repeats
**Shared Link** - Public URL for read-only calendar access
**Time Slot** - Specific date/time block on calendar
**View Count** - Number of times shared calendar was accessed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 1, 2025 | Initial release |

---

**For additional support, contact OOBC IT Support:**
📧 support@oobc.gov.ph
📞 [Office Phone Number]
🌐 [Internal Help Portal]

---

*This guide is maintained by the OOBC IT Department. Last reviewed: October 1, 2025.*
