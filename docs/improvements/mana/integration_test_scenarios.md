# MANA Regional Workshop Integration Test Scenarios

## Overview

This document provides step-by-step integration test scenarios for the MANA Regional Workshop system. These scenarios cover the complete user journey for both facilitators and participants.

## Test Data Setup

Before running these scenarios, set up test data:

```bash
cd src
./manage.py setup_mana_test_data --reset
```

This creates:
- **Admin**: `admin` / `admin123`
- **Facilitators**: `test_facilitator1`, `test_facilitator2` / `password123`
- **Participants**: `test_participant1-5` / `password123`
- **2 Regional Workshop Assessments** (Cotabato, Sultan Kudarat)
- **5 Workshop Activities** per assessment
- **5 Enrolled Participants** across assessments

---

## Scenario 1: Staff Creates and Assigns Accounts

**Actor**: Admin/Staff
**Duration**: 5 minutes
**Prerequisites**: None

### Steps:

1. **Login as Admin**
   - Navigate to `http://localhost:8000/admin/`
   - Username: `admin`
   - Password: `admin123`

2. **Access Account Creation**
   - Navigate to MANA → Regional MANA
   - Click "Create MANA Facilitator / Participant Account"

3. **Create Facilitator Account**
   - **Account Type**: Select "MANA Facilitator"
   - **User Details**:
     - Username: `facilitator_new`
     - Email: `facilitator.new@oobc.gov.ph`
     - First Name: `Juan`
     - Last Name: `Dela Cruz`
     - Password: `secure123`
     - Confirm Password: `secure123`
   - **Assigned Assessments**:
     - Hold Ctrl/Cmd and select both assessments
   - Click "Create Account"

4. **Create Participant Account**
   - **Account Type**: Select "MANA Participant"
   - **User Details**:
     - Username: `participant_new`
     - Email: `participant.new@oobc.gov.ph`
     - First Name: `Maria`
     - Last Name: `Santos`
     - Password: `secure123`
     - Confirm Password: `secure123`
   - **Participant Details**:
     - Assessment: Select "[TEST] Regional Workshop - Cotabato 2025"
     - Stakeholder Type: "Community Elder"
     - Province: "Cotabato"
   - Click "Create Account"

### Expected Results:
✅ Success message: "Facilitator account created and assigned to 2 assessment(s)!"
✅ Success message: "Participant account created and enrolled in assessment!"
✅ New accounts can log in immediately

---

## Scenario 2: Facilitator Assessment Management

**Actor**: Facilitator
**Duration**: 10 minutes
**Prerequisites**: Scenario 1 complete OR test data loaded

### Steps:

1. **Login as Facilitator**
   - Navigate to `http://localhost:8000/`
   - Username: `test_facilitator1`
   - Password: `password123`

2. **View Assigned Assessments**
   - Navigate to MANA → Facilitator Dashboard
   - Expected: See list of assigned assessments only

3. **Open Assessment Dashboard**
   - Click "Open Dashboard" on first assessment
   - Expected: See workshop tabs (Workshop 1-5)
   - Expected: Progress bar showing 0/5 participants submitted

4. **View Workshop Responses**
   - Default view: Workshop 1
   - Expected: Empty responses table (no submissions yet)
   - Test filters:
     - Province: Select a province
     - Stakeholder: Select a type
     - Click "Apply Filters"

5. **Export Data**
   - Click "Export XLSX"
   - Expected: File downloads with workshop structure
   - Click "Export CSV"
   - Expected: CSV file downloads

### Expected Results:
✅ Only assigned assessments visible
✅ Dashboard shows real-time progress
✅ Filters work correctly
✅ Export buttons generate files

---

## Scenario 3: Participant Workshop Completion

**Actor**: Participant
**Duration**: 15 minutes
**Prerequisites**: Test data loaded

### Steps:

1. **Login as Participant**
   - Navigate to `http://localhost:8000/`
   - Username: `test_participant1`
   - Password: `password123`

2. **View Enrolled Assessments**
   - Navigate to MANA → My Assessments
   - Expected: See enrolled assessment with progress 0%

3. **Access Assessment Dashboard**
   - Click "Continue Assessment"
   - Expected: See 5 workshop cards
   - Expected: Workshop 1 is unlocked (green), others locked (gray)

4. **Complete Workshop 1**
   - Click "Start Workshop 1"
   - Fill out all form fields with test data:
     - Text fields: "Test response for question X"
     - Number fields: "100"
     - Long text: "This is a detailed test response with multiple sentences."
   - Observe autosave indicator (should show "Saved X seconds ago")
   - Click "Submit Workshop"

5. **Review Submission**
   - Expected: Redirect to Workshop Outputs page
   - Expected: Yellow banner "⏳ Waiting for Facilitator"
   - Expected: Progress bar showing "1/5 submitted"
   - Expected: All Q&A pairs displayed
   - Click "Download PDF" to test print functionality

6. **Return to Dashboard**
   - Click "Back to Dashboard"
   - Expected: Workshop 1 shows checkmark ✓
   - Expected: Workshop 2-5 still locked

### Expected Results:
✅ Autosave works every few seconds
✅ Submission successful
✅ Outputs page shows all responses
✅ Cannot access locked workshops
✅ Dashboard reflects completion

---

## Scenario 4: Facilitator Advances Participants

**Actor**: Facilitator
**Duration**: 10 minutes
**Prerequisites**: Scenario 3 complete (at least 1 participant submitted Workshop 1)

### Steps:

1. **Login as Facilitator**
   - Navigate to facilitator dashboard
   - Select assessment with submissions

2. **Monitor Progress**
   - View Workshop 1 tab
   - Expected: Progress bar shows X/5 submitted
   - Expected: Responses table shows submitted answers
   - Filter by participant to review individual submissions

3. **Advance All Participants**
   - Expected: Blue button "Advance All Participants to Workshop 2"
   - Click button
   - Expected: Confirmation modal appears
   - Modal shows:
     - Total participant count
     - Current progress (X/5 submitted)
     - Warning that non-submitters also advance

4. **Confirm Advancement**
   - Click "Confirm Advancement"
   - Expected: Modal closes
   - Expected: Toast notification "Advanced 5 participants to Workshop 2"
   - Expected: Button now shows "Advance All Participants to Workshop 3"

5. **Verify Notifications Created**
   - (Optional) Check database or wait for participant login
   - Expected: 5 WorkshopNotification records created

### Expected Results:
✅ Progress visualization accurate
✅ Confirmation modal prevents accidental clicks
✅ All participants advanced simultaneously
✅ Notifications created for all participants

---

## Scenario 5: Participant Receives Advancement Notification

**Actor**: Participant
**Duration**: 5 minutes
**Prerequisites**: Scenario 4 complete

### Steps:

1. **Login as Participant**
   - Username: `test_participant1`
   - Password: `password123`

2. **View Dashboard**
   - Expected: Blue notification banner at top
   - Banner text: "🎉 New Workshop Available: Workshop 2"
   - Message: "The facilitator has unlocked Workshop 2. You can now proceed..."

3. **Interact with Notification**
   - Click "Start Workshop" button in notification
   - Expected: Navigate directly to Workshop 2
   - OR: Click dismiss (X) button
   - Expected: Notification fades out and disappears

4. **Verify Workshop Access**
   - Return to dashboard
   - Expected: Workshop 2 now has green "Unlocked" badge
   - Expected: Can access Workshop 2 form
   - Expected: Workshop 3-5 still locked

### Expected Results:
✅ Notification appears immediately on login
✅ Direct link to new workshop works
✅ Dismiss functionality works
✅ Workshop 2 is now accessible

---

## Scenario 6: Complete Full Workshop Cycle

**Actor**: Both Facilitator & Participant
**Duration**: 30 minutes
**Prerequisites**: Scenario 5 complete

### Steps:

1. **Participant Completes Workshop 2-5**
   - For each workshop (2, 3, 4, 5):
     - Login as participant
     - Navigate to workshop
     - Fill out all fields
     - Submit
     - Review outputs page
     - Wait for facilitator advancement

2. **Facilitator Advances After Each Workshop**
   - For each workshop:
     - Login as facilitator
     - Review submissions
     - Click "Advance All Participants"
     - Confirm advancement

3. **Final State Verification**
   - **Participant Dashboard**:
     - All 5 workshops show checkmarks
     - Progress: 5/5 (100%)
     - Status: "Completed"
   - **Facilitator Dashboard**:
     - Progress bar: 100% green
     - Status: "All participants submitted"
     - No advancement button (last workshop complete)

### Expected Results:
✅ Sequential advancement works correctly
✅ Progress tracking accurate throughout
✅ Final completion state correct
✅ No errors during full cycle

---

## Scenario 7: Error Handling & Edge Cases

**Actor**: Mixed
**Duration**: 15 minutes

### Test Cases:

1. **Non-Assigned Facilitator Access**
   - Login as `test_facilitator2`
   - Try to access assessment not assigned
   - Expected: 403 Forbidden or redirect

2. **Non-Enrolled Participant Access**
   - Login as `test_participant1`
   - Try to access different assessment URL directly
   - Expected: 403 Forbidden or redirect

3. **Submit Empty Workshop**
   - Login as participant
   - Try to submit workshop without filling fields
   - Expected: Form validation errors

4. **Edit Submitted Workshop**
   - Login as participant
   - Try to access submitted workshop
   - Expected: Read-only view or redirect to outputs

5. **Double Advancement**
   - Facilitator advances participants
   - Try to advance again immediately
   - Expected: No duplicate notifications, safe handling

### Expected Results:
✅ Proper access control enforced
✅ Form validation prevents invalid submissions
✅ Submitted workshops locked from editing
✅ Idempotent operations

---

## Scenario 8: AI Synthesis Generation (Bonus)

**Actor**: Facilitator
**Duration**: 10 minutes
**Prerequisites**: Multiple participants submitted Workshop 1

### Steps:

1. **Access Facilitator Dashboard**
   - Navigate to Workshop 1 tab
   - Scroll to "AI Synthesis" section

2. **Generate Synthesis**
   - Select filters (Province, Stakeholder) - optional
   - Select Provider: "openai" or "anthropic"
   - Click "Generate Synthesis"

3. **View Synthesis**
   - Expected: Async task initiated
   - Expected: Synthesis appears in list below
   - Expected: AI-generated summary of responses

4. **Regenerate/Approve**
   - Click "Regenerate" to create new version
   - Click "Approve" to mark as final

### Expected Results:
✅ Synthesis generation works (if AI keys configured)
✅ Filters apply correctly
✅ Multiple versions can be created
✅ Approval workflow functional

---

## Test Completion Checklist

- [ ] All 8 scenarios executed successfully
- [ ] No 500 errors encountered
- [ ] Access control verified
- [ ] Notifications delivered correctly
- [ ] Progress tracking accurate
- [ ] Export functionality works
- [ ] Mobile responsiveness tested (optional)
- [ ] Browser compatibility verified (Chrome, Firefox, Safari)

---

## Common Issues & Troubleshooting

### Issue: Facilitator sees no assessments
**Solution**: Verify FacilitatorAssessmentAssignment exists in database

### Issue: Participant can't access workshop
**Solution**: Check WorkshopParticipantAccount exists and `current_workshop` field

### Issue: Autosave not working
**Solution**: Check HTMX library loaded, check browser console for errors

### Issue: Notifications not appearing
**Solution**: Verify WorkshopNotification records created in database

---

## Database Inspection Commands

```bash
# Check facilitator assignments
./manage.py shell -c "from mana.models import FacilitatorAssessmentAssignment; print(FacilitatorAssessmentAssignment.objects.all())"

# Check participant enrollments
./manage.py shell -c "from mana.models import WorkshopParticipantAccount; print(WorkshopParticipantAccount.objects.all())"

# Check notifications
./manage.py shell -c "from mana.models import WorkshopNotification; print(WorkshopNotification.objects.filter(is_read=False).count())"
```

---

**Last Updated**: 2025-09-30
**Test Data Version**: 1.0
**Django Version**: 4.2+