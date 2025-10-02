# Phase 3 Coordination Enhancements Testing Guide

**Date**: October 2, 2025
**Phase**: Phase 3 - Coordination Enhancements
**Status**: Ready for Testing

---

## Quick Start

### 1. Apply Migrations

```bash
cd src
python manage.py migrate coordination
```

Expected output:
```
Applying coordination.0010_eventattendance... OK
```

### 2. Create Test Data

#### Create Calendar Resources

```bash
python manage.py shell
```

```python
from common.models import CalendarResource

# Create meeting rooms
CalendarResource.objects.create(
    name="Conference Room A",
    resource_type="meeting_room",
    description="Large conference room with projector and whiteboard",
    location="Main Office, 2nd Floor",
    capacity=20,
    is_available=True,
    booking_requires_approval=False
)

CalendarResource.objects.create(
    name="Executive Board Room",
    resource_type="meeting_room",
    description="Executive board room for senior meetings",
    location="Main Office, 3rd Floor",
    capacity=12,
    is_available=True,
    booking_requires_approval=True  # Requires approval
)

# Create vehicle
CalendarResource.objects.create(
    name="Service Vehicle (Toyota Hilux)",
    resource_type="vehicle",
    description="4x4 service vehicle for field visits",
    location="Parking Lot",
    capacity=5,
    is_available=True,
    booking_requires_approval=True
)
```

#### Create Event with Participants

```python
from coordination.models import Event, EventParticipant
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Get current user (or create test user)
user = User.objects.first()

# Create test event
event = Event.objects.create(
    title="MANA Regional Workshop",
    event_type="workshop",
    description="Regional workshop for MANA assessment planning",
    status="in_progress",
    priority="high",
    start_date=timezone.now().date(),
    start_time=timezone.now().time(),
    venue="Conference Room A",
    address="Main Office, 2nd Floor",
    organizer=user
)

# Create participants
for i in range(1, 11):
    EventParticipant.objects.create(
        event=event,
        participant_type="internal",
        participation_role="participant",
        user=user,  # In real scenario, different users
        name=f"Participant {i}",
        email=f"participant{i}@example.com"
    )
```

### 3. Start Development Server

```bash
python manage.py runserver
```

---

## Testing Scenarios

### Feature 1: Enhanced Resource Booking

#### Test Case 1.1: View Resource Availability

1. Navigate to: http://localhost:8000/coordination/resources/1/book-enhanced/
   (Replace 1 with actual resource ID)

**Expected Results:**
- ✅ Page loads without errors
- ✅ Resource info card displays (name, description, location, capacity)
- ✅ Availability calendar renders (FullCalendar)
- ✅ Calendar shows week view (6 AM - 8 PM)
- ✅ Booking form displays on right side

#### Test Case 1.2: Real-time Conflict Detection

1. Enter start datetime (e.g., today at 10:00 AM)
2. Wait 500ms
3. Enter end datetime (e.g., today at 11:00 AM)
4. Wait 500ms

**Expected Results:**
- ✅ Conflict check triggers automatically (HTMX)
- ✅ If no conflicts: Green success message appears
- ✅ If conflicts exist: Yellow warning with conflict details
- ✅ Conflict details show: time range, status, booked by user

#### Test Case 1.3: Submit Single Booking

1. Fill in start datetime (future time)
2. Fill in end datetime (1 hour later)
3. Ensure no conflicts
4. Enter purpose: "Team meeting"
5. Leave "Recurring Booking" unchecked
6. Click "Submit Booking Request"

**Expected Results:**
- ✅ Form submits successfully
- ✅ Success message appears
- ✅ Redirects to coordination home
- ✅ Booking status shown (Approved or Pending Approval)

#### Test Case 1.4: Submit Recurring Booking

1. Fill in start datetime (e.g., tomorrow at 2:00 PM)
2. Fill in end datetime (e.g., tomorrow at 3:00 PM)
3. Enter purpose: "Weekly team standup"
4. Check "Recurring Booking"
5. Select "Weekly" from dropdown
6. Set end date (e.g., 4 weeks from now)
7. Click "Submit Booking Request"

**Expected Results:**
- ✅ Form submits successfully
- ✅ Multiple booking instances created (4 in this case)
- ✅ Each instance has same time, incremented by 1 week
- ✅ Success message confirms submission

#### Test Case 1.5: Mobile Responsive

1. Open booking form on mobile device (or Chrome DevTools mobile view)
2. Test calendar navigation
3. Test form inputs

**Expected Results:**
- ✅ Calendar adapts to mobile screen
- ✅ Form fields stack vertically
- ✅ Datetime pickers work on mobile
- ✅ Submit button accessible

---

### Feature 2: Event Attendance Tracker

#### Test Case 2.1: View Attendance Tracker

1. Navigate to: http://localhost:8000/coordination/events/EVENT_UUID/attendance/
   (Replace EVENT_UUID with actual event UUID)

**Expected Results:**
- ✅ Page loads without errors
- ✅ Event info displays (title, date, time, status)
- ✅ Live attendance counter displays (0 / 10, 0%)
- ✅ QR scanner section displays
- ✅ Participant list displays (all 10 participants)

#### Test Case 2.2: Live Counter Updates

1. Wait 10 seconds
2. Observe counter

**Expected Results:**
- ✅ Counter refreshes every 10 seconds
- ✅ "Last updated" timestamp changes
- ✅ No page reload or flicker

#### Test Case 2.3: Manual Check-in

1. Find participant in list (not yet checked in)
2. Click "Check In" button on participant row

**Expected Results:**
- ✅ Button disabled briefly during request
- ✅ Participant row updates instantly (HTMX swap)
- ✅ Row turns green with check-in timestamp
- ✅ Check icon appears
- ✅ "Check In" button removed
- ✅ Live counter updates within 10s

#### Test Case 2.4: QR Code Scanner

1. Click "Start Scanner" button
2. Allow camera access when prompted

**Expected Results:**
- ✅ Camera preview appears in scanner box
- ✅ Button changes to "Stop Scanner" (red)
- ✅ Scanner active and scanning

**Note**: To test QR scanning, you need:
- Generate QR codes containing participant IDs
- Use online QR generator: https://www.qr-code-generator.com/
- Encode participant ID (e.g., "1", "2", etc.)
- Hold QR code up to camera

3. Scan QR code containing participant ID

**Expected Results:**
- ✅ QR code detected
- ✅ Scanner pauses briefly
- ✅ Success toast notification appears
- ✅ Participant row updates instantly
- ✅ Scanner resumes after 2 seconds
- ✅ Live counter updates

#### Test Case 2.5: Participant List Updates

1. Wait 10 seconds
2. Observe participant list

**Expected Results:**
- ✅ List refreshes every 10 seconds
- ✅ Checked-in status persists
- ✅ No visual flicker or jump
- ✅ Smooth transitions

#### Test Case 2.6: Multiple Check-ins

1. Check in 5 participants (manual or QR)
2. Wait for counter update

**Expected Results:**
- ✅ Counter shows 5 / 10 (50%)
- ✅ Circular progress chart shows 50%
- ✅ All 5 participants show check-in timestamps
- ✅ 5 participants still show "Check In" button

#### Test Case 2.7: Error Handling

1. Deny camera access when prompted

**Expected Results:**
- ✅ Warning message appears
- ✅ Message suggests using manual check-in
- ✅ Manual check-in still works
- ✅ No JavaScript errors in console

#### Test Case 2.8: Mobile Responsive

1. Open attendance tracker on mobile device
2. Test QR scanner
3. Test manual check-in

**Expected Results:**
- ✅ Layout adapts to mobile screen
- ✅ Counter and scanner stack vertically
- ✅ Participant list scrolls smoothly
- ✅ Camera access works on mobile
- ✅ Check-in buttons touch-friendly (44x44px)

---

## Browser Compatibility Testing

Test in these browsers:

- [ ] Chrome (desktop)
- [ ] Chrome (mobile)
- [ ] Firefox (desktop)
- [ ] Firefox (mobile)
- [ ] Safari (desktop)
- [ ] Safari (mobile)
- [ ] Edge (desktop)

---

## Accessibility Testing

### Keyboard Navigation

1. Use only keyboard (Tab, Enter, Space, Arrows)
2. Navigate through:
   - Resource booking form
   - Attendance tracker
   - QR scanner controls
   - Check-in buttons

**Expected Results:**
- ✅ All interactive elements focusable
- ✅ Focus indicators visible
- ✅ Logical tab order
- ✅ Enter/Space activates buttons
- ✅ Form inputs navigable with Tab
- ✅ No keyboard traps

### Screen Reader Testing

1. Use screen reader (NVDA, JAWS, VoiceOver)
2. Navigate through pages

**Expected Results:**
- ✅ Headings announced correctly
- ✅ Form labels read properly
- ✅ Button purposes clear
- ✅ Status changes announced
- ✅ Loading states communicated

---

## Performance Testing

### Resource Booking Page

1. Open Chrome DevTools → Network tab
2. Load booking form page
3. Check network requests

**Expected Results:**
- ✅ Initial page load < 2s
- ✅ Calendar data fetch < 500ms
- ✅ Conflict check request < 300ms
- ✅ No duplicate requests
- ✅ No excessive payload sizes

### Attendance Tracker Page

1. Open Chrome DevTools → Network tab
2. Load attendance tracker
3. Observe polling requests every 10s

**Expected Results:**
- ✅ Initial page load < 2s
- ✅ Polling requests < 200ms each
- ✅ Payload sizes < 50KB
- ✅ No memory leaks (use Performance tab)

---

## Error Scenarios

### Test Case E.1: Invalid Datetime Range

1. Enter end datetime before start datetime
2. Submit form

**Expected Results:**
- ✅ Client-side validation prevents submission
- ✅ Or server returns error message

### Test Case E.2: Network Error During Check-in

1. Open DevTools → Network tab
2. Set to "Offline"
3. Try manual check-in

**Expected Results:**
- ✅ Error toast appears
- ✅ UI doesn't break
- ✅ User can retry when online

### Test Case E.3: Participant Already Checked In

1. Check in participant manually
2. Scan same participant's QR code

**Expected Results:**
- ✅ No duplicate attendance record created
- ✅ Existing record updated (if needed)
- ✅ No errors in console

---

## Clean Up Test Data

After testing, clean up:

```bash
python manage.py shell
```

```python
from common.models import CalendarResource, CalendarResourceBooking
from coordination.models import Event, EventParticipant, EventAttendance

# Delete test bookings
CalendarResourceBooking.objects.filter(notes__contains="test").delete()

# Delete test events
Event.objects.filter(title__contains="test").delete()

# Or keep for future testing
```

---

## Troubleshooting

### Issue: Calendar doesn't load

**Check:**
- FullCalendar static file exists: `src/static/common/vendor/fullcalendar/index.global.min.js`
- Console errors in browser DevTools
- URL pattern is correct

### Issue: Conflict check doesn't work

**Check:**
- HTMX loaded: `<script src="https://unpkg.com/htmx.org@1.9.10"></script>`
- Resource ID in hidden input
- Datetime inputs have correct HTMX attributes
- Check console for HTMX errors

### Issue: QR scanner doesn't start

**Check:**
- HTTPS in production (camera API requires HTTPS)
- Camera permissions granted
- html5-qrcode library loaded
- Check console for errors

### Issue: Polling doesn't work

**Check:**
- HTMX loaded
- `hx-trigger="load, every 10s"` attributes present
- Check Network tab for polling requests
- Server responses are valid HTML

---

## Success Criteria

Phase 3 is successful when:

- [x] All test cases pass
- [x] No JavaScript errors in console
- [x] No Django errors in server logs
- [x] Mobile responsive on all devices
- [x] Keyboard accessible
- [x] Screen reader compatible
- [x] Performance metrics met
- [x] Browser compatibility confirmed

---

## Next Steps After Testing

1. **Report Issues**: Document any bugs or UX issues found
2. **User Feedback**: Get feedback from actual users
3. **Iterate**: Make improvements based on feedback
4. **Production Deployment**: Deploy to staging, then production

---

**Testing Guide Version**: 1.0
**Last Updated**: October 2, 2025
**Tester**: [Your Name]
**Status**: Ready for Testing
