# MANA Facilitator-Controlled Workshop Advancement

**Status:** Design Document
**Priority:** High
**Created:** 2025-01-27
**Complexity:** Medium-High

---

## Executive Summary

This document outlines a redesign of the Regional MANA Workshop progression system to implement **facilitator-controlled advancement**. Participants will submit workshop responses and wait for a facilitator to review outputs before the entire cohort advances to the next workshop simultaneously.

**Key Changes:**
1. Remove automatic workshop advancement after participant submission
2. Introduce MANA Facilitator role with full assessment access
3. Add post-submission review page showing all participant answers
4. Implement "Advance All Participants" functionality for facilitators
5. Create facilitator dashboard for progress monitoring

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Proposed Solution](#proposed-solution)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Workshop Flow](#workshop-flow)
5. [Technical Architecture](#technical-architecture)
6. [Implementation Plan](#implementation-plan)
7. [UI/UX Specifications](#uiux-specifications)

---

## Problem Statement

### Current Issues

The current Regional MANA Workshop system has these limitations:

1. **Auto-Advancement**: When a participant submits a workshop, they're **immediately** advanced to the next workshop
   - No facilitator review before progression
   - Participants move at different paces
   - No cohort synchronization

2. **No Facilitator Role**: System lacks a dedicated facilitator account type with oversight capabilities
   - No way to review all participant responses
   - No bulk advancement controls
   - No progress monitoring dashboard

3. **No Post-Submission Review**: After submission, participants are redirected to next workshop
   - Cannot review what they just submitted
   - No confirmation of submission success
   - No "waiting for facilitator" state

### Requirements

From the Regional MANA Workshop design:

> **Facilitator-Controlled Advancement (Recommended)**
> - Facilitator reviews workshop outputs
> - Clicks "Advance All Participants" button
> - All participants move to next workshop simultaneously

This ensures:
- Quality control through facilitator review
- Cohort remains synchronized
- Facilitators can provide feedback before advancement
- Workshop sessions progress as a group

---

## Proposed Solution

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Workshop Lifecycle                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌──────▼──────┐      ┌──────▼──────┐
   │  Participant │    │  Facilitator │     │   System    │
   │   Actions    │    │   Actions    │     │   State     │
   └────┬────┘         └──────┬──────┘      └──────┬──────┘
        │                     │                     │
        │                     │                     │
   1. Access           1. Monitor             • Not Started
      Workshop            Progress             • In Progress
        │                     │                • Submitted
        │                     │                • Reviewed
   2. Fill Out         2. Review              • Advanced
      Questions           Responses
        │                     │
        │                     │
   3. Submit           3. Click
      Workshop            "Advance All"
        │                     │
        ▼                     ▼
   4. View Review      4. All Participants
      Page                Move to Next
      (WAIT)
```

### Core Changes

1. **Remove Auto-Advancement**
   - `mark_workshop_complete()` only marks workshop as submitted
   - Does NOT update `participant.current_workshop`
   - Participant stays on submitted workshop until facilitator advances

2. **Add Facilitator Role**
   - New permission: `mana.can_facilitate_workshop`
   - Can view all workshops
   - Can see all participant responses
   - Can advance all participants

3. **Post-Submission Review Page**
   - After submission, redirect to review page
   - Shows all participant's answers for that workshop
   - Clear message: "Submitted - Waiting for facilitator to advance cohort"
   - Cannot edit, can only review

4. **Facilitator Dashboard**
   - Progress tracking for all participants
   - Workshop-by-workshop response viewing
   - "Advance All Participants" button per workshop
   - Export/reporting capabilities

---

## User Roles & Permissions

### 1. MANA Participant (Existing)

**Permissions:**
- `mana.can_access_regional_mana`
- `mana.can_view_provincial_obc`

**Capabilities:**
- Access assigned assessment only
- View/edit current workshop (if not submitted)
- Submit workshop responses
- View submitted workshops (read-only)
- **Cannot** access next workshop until facilitator advances

**Access Rules:**
```python
# Can access workshops where:
workshop_type in participant.completed_workshops  # Submitted, read-only
OR workshop_type == participant.current_workshop   # Active workshop

# Cannot access:
workshop_type not in completed AND != current  # Future workshops
```

### 2. MANA Facilitator (NEW)

**Permissions:**
- `mana.can_facilitate_workshop`
- `mana.can_access_regional_mana`
- `mana.can_view_provincial_obc`

**Capabilities:**
- Access all workshops in the assessment
- View all participant responses for all workshops
- Advance all participants to next workshop
- Reset individual participant progress (if needed)
- Export workshop responses
- View assessment-wide analytics

**Access Rules:**
```python
# Can access:
- ALL workshops in their assigned assessment(s)
- ALL participant responses
- Facilitator dashboard
- Advancement controls
```

### 3. OOBC Staff (Existing)

**Permissions:**
- `is_staff=True` or `is_superuser=True`
- All MANA permissions

**Capabilities:**
- Full system access
- Create assessments
- Create facilitator and participant accounts
- Override any restrictions

### Permission Matrix

| Action | Participant | Facilitator | Staff |
|--------|------------|-------------|-------|
| View own current workshop | ✅ | ✅ | ✅ |
| Submit own responses | ✅ | ✅ | ✅ |
| View own submitted workshops | ✅ | ✅ | ✅ |
| View others' responses | ❌ | ✅ | ✅ |
| Advance to next workshop | ❌ | ✅ (all) | ✅ (all) |
| Reset participant progress | ❌ | ✅ | ✅ |
| Create assessment | ❌ | ❌ | ✅ |
| Create accounts | ❌ | ❌ | ✅ |

---

## Workshop Flow

### Participant Flow

#### State 1: Workshop In Progress

```
┌──────────────────────────────────────────────┐
│         Workshop 1: Community Context         │
│                                               │
│  Progress: 5/10 questions answered           │
│  Status: In Progress                          │
│                                               │
│  [Question 1] ✓ Answered                     │
│  [Question 2] ✓ Answered                     │
│  [Question 3] → Currently editing...         │
│                                               │
│  [Save Draft]  [Submit Workshop]             │
└──────────────────────────────────────────────┘
```

#### State 2: Workshop Submitted (NEW)

After clicking "Submit Workshop":

```
┌──────────────────────────────────────────────┐
│    ✓ Workshop 1 Submitted Successfully        │
│                                               │
│  Your responses have been locked and          │
│  submitted to the facilitator for review.     │
│                                               │
│  Review Your Answers:                         │
│  ┌─────────────────────────────────────┐    │
│  │ Q1: What is the population of...    │    │
│  │ A: Approximately 5,000 residents... │    │
│  │                                      │    │
│  │ Q2: Key economic activities...      │    │
│  │ A: Agriculture, fishing...          │    │
│  │                                      │    │
│  │ [Full Review →]                     │    │
│  └─────────────────────────────────────┘    │
│                                               │
│  ⏳ Waiting for Facilitator                  │
│  The facilitator will review all participant  │
│  responses and advance the cohort to the      │
│  next workshop together.                      │
│                                               │
│  [Back to Dashboard]                          │
└──────────────────────────────────────────────┘
```

**Key Elements:**
- ✅ Success confirmation
- 📄 Summary of all answers
- ⏳ Clear "waiting" state
- 📝 Explanation of next steps
- 🔒 Cannot edit or proceed

#### State 3: Facilitator Advances Cohort

After facilitator clicks "Advance All Participants":

```
┌──────────────────────────────────────────────┐
│    🎉 Workshop 2 Now Available!               │
│                                               │
│  The facilitator has reviewed submissions     │
│  and advanced the cohort to the next          │
│  workshop.                                    │
│                                               │
│  Workshop 2: Community Aspirations            │
│                                               │
│  [Start Workshop 2 →]                        │
│                                               │
│  Previous Workshops:                          │
│  • Workshop 1: Community Context ✓           │
│    [Review Answers]                           │
└──────────────────────────────────────────────┘
```

### Facilitator Flow

#### Facilitator Dashboard

```
┌───────────────────────────────────────────────────────────┐
│  MANA Facilitator Dashboard                               │
│  Assessment: Region IX OBC Needs Assessment               │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  📊 Overall Progress                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Total Participants: 25                          │   │
│  │ Active Workshop: Workshop 1                     │   │
│  │ Fully Completed: 0                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  📝 Workshop Progress                                     │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Workshop 1: Community Context                   │   │
│  │ ━━━━━━━━━━━━━━━━━━━━ 100% (25/25)            │   │
│  │                                                 │   │
│  │ 📈 25 Submitted  ⏱ 0 In Progress              │   │
│  │                                                 │   │
│  │ [View All Responses]  [Advance All to W2 →]   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Workshop 2: Community Aspirations               │   │
│  │ ━━━━━━━━━━━━━━━━━━━━ 0% (0/25)               │   │
│  │                                                 │   │
│  │ 🔒 Not Yet Unlocked                            │   │
│  │ Prerequisites: All participants complete W1     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  [Export All Data]  [Generate Report]                   │
└───────────────────────────────────────────────────────────┘
```

#### Workshop Response Review

```
┌───────────────────────────────────────────────────────────┐
│  Workshop 1: All Participant Responses                    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Filters: [All Provinces ▼] [All Stakeholder Types ▼]   │
│  Search: [                                          🔍]   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Juan Dela Cruz • Zamboanga del Norte • Elder   │   │
│  │ Submitted: Jan 27, 2025 2:30 PM                │   │
│  │                                                 │   │
│  │ Q1: What is the estimated population...        │   │
│  │ A: Approximately 5,000 residents distributed   │   │
│  │    across 12 barangays...                      │   │
│  │                                                 │   │
│  │ [View Full Response]  [Export]                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  │ Maria Santos • Zamboanga del Sur • Women Leader│   │
│  │ ...                                             │   │
│                                                           │
│  Showing 25 of 25 participants                           │
│                                                           │
│  All participants have submitted.                        │
│  [✓ Advance All Participants to Workshop 2]             │
└───────────────────────────────────────────────────────────┘
```

---

## Technical Architecture

### Database Schema Changes

#### 1. Add Facilitator Tracking

**WorkshopParticipantAccount Model** (existing):
```python
class WorkshopParticipantAccount(models.Model):
    # ... existing fields ...

    # Keep existing:
    current_workshop = models.CharField(...)  # Current accessible workshop
    completed_workshops = models.JSONField(...)  # Submitted workshops

    # Add NEW field:
    facilitator_advanced_to = models.CharField(
        max_length=15,
        blank=True,
        default="workshop_1",
        help_text="Workshop that facilitator has unlocked for this participant"
    )
```

**Logic:**
- `current_workshop` = What participant can currently work on
- `completed_workshops` = What participant has submitted
- `facilitator_advanced_to` = What facilitator has unlocked (limits max accessible)

#### 2. Add Facilitator Permission

**Migration:**
```python
Permission.objects.get_or_create(
    codename='can_facilitate_workshop',
    content_type=ContentType.objects.get_for_model(WorkshopParticipantAccount),
    defaults={'name': 'Can facilitate and manage MANA workshops'},
)
```

#### 3. Workshop State Tracking

**WorkshopActivity Model** (existing - no changes needed):
```python
class WorkshopActivity(models.Model):
    # Current fields already support tracking:
    status  # planning, active, completed

    # We can use existing fields to track:
    # - Number of submissions (via WorkshopResponse.filter(status="submitted"))
    # - Advancement status (check if all participants.current_workshop > this workshop)
```

### Access Control Logic

#### Current vs. Proposed

**CURRENT (Auto-Advancement):**
```python
# participant_views.py - mark_workshop_complete()
def mark_workshop_complete(participant, workshop_type):
    # Add to completed
    completed.append(workshop_type)

    # PROBLEM: Auto-advances immediately
    current_index = SEQUENCE.index(workshop_type)
    participant.current_workshop = SEQUENCE[current_index + 1]  # ❌ Auto-advance
    participant.save()
```

**PROPOSED (Facilitator-Controlled):**
```python
# services/workshop_access.py
def mark_workshop_complete(participant, workshop_type):
    """Participant submits - does NOT auto-advance."""
    # Add to completed
    completed.append(workshop_type)
    participant.completed_workshops = completed

    # DO NOT UPDATE current_workshop - wait for facilitator
    participant.save(update_fields=["completed_workshops"])
    # Participant stays on same current_workshop until facilitator advances


def get_allowed_workshops(participant):
    """
    Determines which workshops participant can access.

    NEW Logic:
    - Can access workshops up to facilitator_advanced_to
    - Can view all completed workshops (read-only)
    - Can edit current_workshop (if not yet submitted)
    """
    max_allowed = participant.facilitator_advanced_to or "workshop_1"
    max_index = SEQUENCE.index(max_allowed)

    # Can access workshops up to max_allowed
    allowed = SEQUENCE[:max_index + 1]

    return allowed


def is_workshop_accessible(participant, workshop_type):
    """Check if workshop is accessible (within facilitator-unlocked range)."""
    allowed = get_allowed_workshops(participant)
    return workshop_type in allowed


def advance_all_participants(assessment, to_workshop_type, by_user):
    """
    Facilitator action: Unlock next workshop for entire cohort.

    This is the ONLY way participants progress to next workshop.
    """
    participants = WorkshopParticipantAccount.objects.filter(
        assessment=assessment
    )

    for participant in participants:
        # Update facilitator_advanced_to (max accessible)
        participant.facilitator_advanced_to = to_workshop_type

        # If participant completed previous workshop, move them forward
        prev_index = SEQUENCE.index(to_workshop_type) - 1
        if prev_index >= 0:
            prev_workshop = SEQUENCE[prev_index]
            if prev_workshop in participant.completed_workshops:
                participant.current_workshop = to_workshop_type

        participant.save()

        # Log advancement
        WorkshopAccessLog.objects.create(
            participant=participant,
            workshop=workshop_activity,
            action_type="advance",
            metadata={
                "advanced_by": by_user.get_full_name(),
                "to_workshop": to_workshop_type,
            }
        )

    return participants.count()
```

#### Workshop Access States

| State | Description | Participant Can |
|-------|-------------|-----------------|
| **Not Accessible** | Future workshop, not yet unlocked by facilitator | ❌ Cannot view at all |
| **Accessible - Not Started** | Unlocked by facilitator, participant hasn't started | ✅ Can view, can fill out |
| **Accessible - In Progress** | Participant is actively working on it | ✅ Can view, can edit |
| **Submitted - Waiting** | Participant submitted, waiting for facilitator | ✅ Can view (read-only), ❌ Cannot edit, ❌ Cannot proceed |
| **Completed - Advanced** | Facilitator advanced cohort, participant moved to next | ✅ Can view (read-only), ❌ Cannot edit |

---

## Implementation Plan

### Phase 1: Database & Model Changes

**Priority:** High
**Effort:** Low (2-3 hours)

1. **Add Migration**
   - Add `facilitator_advanced_to` field to `WorkshopParticipantAccount`
   - Add `can_facilitate_workshop` permission
   - Default all existing participants to `facilitator_advanced_to='workshop_1'`

2. **Update Models**
   ```python
   # models.py - WorkshopParticipantAccount
   facilitator_advanced_to = models.CharField(
       max_length=15,
       choices=WorkshopActivity.WORKSHOP_TYPES,
       default='workshop_1',
       help_text="Maximum workshop unlocked by facilitator"
   )

   class Meta:
       permissions = [
           # ... existing ...
           ("can_facilitate_workshop", "Can facilitate and manage MANA workshops"),
       ]
   ```

### Phase 2: Access Control Logic

**Priority:** High
**Effort:** Medium (4-6 hours)

1. **Modify `workshop_access.py`**
   - Update `get_allowed_workshops()` to respect `facilitator_advanced_to`
   - Update `mark_workshop_complete()` to NOT auto-advance `current_workshop`
   - Enhance `advance_all_participants()` to update `facilitator_advanced_to` and `current_workshop`

2. **Update Participant Views**
   - Modify `participant_workshop_detail()` to redirect to review page after submission
   - Keep submission lock logic (implemented earlier)

3. **Add Decorators**
   ```python
   # decorators.py
   def facilitator_required(view_func):
       """Decorator to restrict views to MANA facilitators only."""
       @wraps(view_func)
       def wrapper(request, *args, **kwargs):
           if not request.user.has_perm('mana.can_facilitate_workshop'):
               raise PermissionDenied("Facilitator access required")
           return view_func(request, *args, **kwargs)
       return wrapper
   ```

### Phase 3: Post-Submission Review Page

**Priority:** High
**Effort:** Medium (4-6 hours)

1. **Create View**
   ```python
   # participant_views.py
   @login_required
   @participant_required
   def participant_workshop_review(request, assessment_id, workshop_type):
       """
       Show submitted workshop responses in read-only format.
       Displayed after participant submits workshop.
       """
       assessment = request.mana_assessment
       participant = request.mana_participant_account

       workshop = get_object_or_404(
           WorkshopActivity,
           assessment=assessment,
           workshop_type=workshop_type
       )

       # Must be submitted
       responses = WorkshopResponse.objects.filter(
           participant=participant,
           workshop=workshop,
           status="submitted"
       ).order_by("question_id")

       if not responses.exists():
           return redirect("mana:participant_workshop_detail", ...)

       # Check if facilitator has advanced cohort
       next_workshop_unlocked = False
       if participant.current_workshop != workshop_type:
           next_workshop_unlocked = True

       questions = get_questions_for_workshop(workshop_type)

       # Pair questions with responses
       qa_pairs = []
       for question in questions:
           response = responses.filter(question_id=question["id"]).first()
           qa_pairs.append({
               "question": question,
               "response": response,
           })

       context = {
           "assessment": assessment,
           "participant": participant,
           "workshop": workshop,
           "qa_pairs": qa_pairs,
           "next_workshop_unlocked": next_workshop_unlocked,
       }
       return render(request, "mana/participant/workshop_review.html", context)
   ```

2. **Create Template**
   - `templates/mana/participant/workshop_review.html`
   - Show all Q&A pairs
   - "Waiting for facilitator" banner if not advanced
   - "Next workshop available" if advanced

3. **Update Redirect After Submission**
   ```python
   # In participant_workshop_detail POST handler:
   if saved_status == "submitted":
       return redirect(
           "mana:participant_workshop_review",
           assessment_id=str(assessment.id),
           workshop_type=workshop_type
       )
   ```

### Phase 4: Facilitator Dashboard

**Priority:** High
**Effort:** High (8-12 hours)

1. **Create Facilitator Views**
   ```python
   # facilitator_views.py (NEW FILE)

   @login_required
   @facilitator_required
   def facilitator_dashboard(request, assessment_id):
       """Main facilitator dashboard showing progress."""
       pass

   @login_required
   @facilitator_required
   def facilitator_workshop_responses(request, assessment_id, workshop_type):
       """View all participant responses for a workshop."""
       pass

   @login_required
   @facilitator_required
   @require_POST
   def facilitator_advance_participants(request, assessment_id, workshop_type):
       """Advance all participants to next workshop."""
       pass

   @login_required
   @facilitator_required
   def facilitator_participant_detail(request, assessment_id, participant_id):
       """View individual participant progress and responses."""
       pass
   ```

2. **Create Templates**
   - `templates/mana/facilitator/dashboard.html`
   - `templates/mana/facilitator/workshop_responses.html`
   - `templates/mana/facilitator/participant_detail.html`

3. **Add URLs**
   ```python
   # urls.py
   urlpatterns += [
       path(
           'facilitator/<uuid:assessment_id>/',
           facilitator_views.facilitator_dashboard,
           name='facilitator_dashboard'
       ),
       path(
           'facilitator/<uuid:assessment_id>/workshop/<str:workshop_type>/',
           facilitator_views.facilitator_workshop_responses,
           name='facilitator_workshop_responses'
       ),
       path(
           'facilitator/<uuid:assessment_id>/workshop/<str:workshop_type>/advance/',
           facilitator_views.facilitator_advance_participants,
           name='facilitator_advance_participants'
       ),
   ]
   ```

### Phase 5: Account Creation Workflow

**Priority:** Medium
**Effort:** Medium (4-6 hours)

1. **Create Management Command**
   ```python
   # management/commands/create_mana_facilitator.py
   from django.core.management.base import BaseCommand
   from django.contrib.auth.models import User, Permission

   class Command(BaseCommand):
       help = 'Create a MANA Facilitator account'

       def add_arguments(self, parser):
           parser.add_argument('username', type=str)
           parser.add_argument('email', type=str)
           parser.add_argument('--password', type=str, default=None)

       def handle(self, *args, **options):
           # Create user
           user = User.objects.create_user(
               username=options['username'],
               email=options['email'],
               password=options.get('password') or 'changeme123'
           )

           # Grant facilitator permission
           perm = Permission.objects.get(codename='can_facilitate_workshop')
           user.user_permissions.add(perm)

           self.stdout.write(
               self.style.SUCCESS(
                   f'Facilitator account created: {user.username}'
               )
           )
   ```

2. **Add Admin Interface**
   ```python
   # admin.py
   class FacilitatorAdmin(UserAdmin):
       """Custom admin for managing facilitator accounts."""
       list_filter = UserAdmin.list_filter + ('user_permissions',)

       def get_queryset(self, request):
           qs = super().get_queryset(request)
           return qs.filter(
               user_permissions__codename='can_facilitate_workshop'
           )
   ```

3. **Update Documentation**
   - Add facilitator account creation guide
   - Document facilitator workflow
   - Add troubleshooting section

### Phase 6: Testing & Validation

**Priority:** High
**Effort:** Medium (4-6 hours)

1. **Unit Tests**
   - Test `get_allowed_workshops()` with facilitator advancement
   - Test `advance_all_participants()`
   - Test submission without auto-advancement

2. **Integration Tests**
   - Full participant flow: start → submit → wait → advance → continue
   - Facilitator actions: review → advance → monitor

3. **User Acceptance Testing**
   - Create test assessment with 3-5 test participants
   - Create facilitator account
   - Run through full workshop cycle

---

## UI/UX Specifications

### Participant Post-Submission Review Page

**URL:** `/mana/participant/<assessment_id>/workshop/<workshop_type>/review/`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  ✓ Workshop Submitted Successfully                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ ✅ Submission Confirmed                            │    │
│  │                                                    │    │
│  │ Your responses for "Workshop 1: Community         │    │
│  │ Context" have been successfully submitted and     │    │
│  │ locked.                                           │    │
│  │                                                    │    │
│  │ Submitted: January 27, 2025 at 2:30 PM           │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ ⏳ Waiting for Facilitator                        │    │
│  │                                                    │    │
│  │ The facilitator will review all participant       │    │
│  │ submissions before advancing the cohort to the    │    │
│  │ next workshop. You'll be notified when Workshop  │    │
│  │ 2 becomes available.                              │    │
│  │                                                    │    │
│  │ Progress: 5 of 25 participants have submitted     │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  📄 Review Your Submitted Answers                          │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Q1: What is the estimated population of OBCs?     │    │
│  │                                                    │    │
│  │ A: Approximately 5,000 residents distributed      │    │
│  │    across 12 barangays in our municipality.       │    │
│  │    The largest concentration is in...             │    │
│  │                                                    │    │
│  │    [See full answer ▼]                           │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ Q2: What are the key economic activities?         │    │
│  │                                                    │    │
│  │ A: Primary activities include agriculture...      │    │
│  │    [See full answer ▼]                           │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  [Show all 10 questions ▼]                                 │
│                                                             │
│  [« Back to Dashboard]  [Download My Answers PDF]          │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**
- ✅ Clear success confirmation with timestamp
- ⏳ "Waiting" state with progress indicator (X of Y submitted)
- 📄 Expandable/collapsible Q&A pairs
- 🔒 Visual indicators that content is locked
- 📥 Option to download PDF of responses
- 🔔 Refresh page to check if next workshop unlocked

**When Facilitator Advances:**
```
┌─────────────────────────────────────────────────────────────┐
│  🎉 Workshop 2 Now Available!                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │ ✅ Facilitator has advanced the cohort            │    │
│  │                                                    │    │
│  │ All participants have been moved to Workshop 2.   │    │
│  │ You can now begin the next assessment session.    │    │
│  │                                                    │    │
│  │ [Start Workshop 2: Community Aspirations →]      │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  Your Workshop 1 answers remain available for review:      │
│  [Review Workshop 1 Answers]                                │
└─────────────────────────────────────────────────────────────┘
```

### Facilitator Dashboard

**URL:** `/mana/facilitator/<assessment_id>/`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  MANA Facilitator Dashboard                                 │
│  Assessment: Region IX OBC Needs Assessment                 │
│  Facilitator: Maria Santos                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Assessment Overview                                     │
│  ┌─────────────────────────────────────────────────┐      │
│  │ Total Participants: 25                          │      │
│  │ Active Workshop: Workshop 1                     │      │
│  │ Assessment Progress: 20% Complete               │      │
│  │ Started: Jan 20, 2025                           │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  📝 Workshop Progress                                       │
│                                                             │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 📗 Workshop 1: Understanding Community Context  │      │
│  │                                                 │      │
│  │ Progress: ━━━━━━━━━━━━━━━━ 100% (25/25)        │      │
│  │                                                 │      │
│  │ ✅ 25 Submitted  ⏱ 0 In Progress  ⏸ 0 Not Started │   │
│  │                                                 │      │
│  │ Latest Submission: 5 minutes ago                │      │
│  │                                                 │      │
│  │ [📊 View All Responses]                        │      │
│  │ [✓ Advance All to Workshop 2 →]               │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 📘 Workshop 2: Community Aspirations            │      │
│  │                                                 │      │
│  │ Progress: ━━━━━━━━━━━━━━━━ 0% (0/25)          │      │
│  │                                                 │      │
│  │ 🔒 Locked - Waiting for Workshop 1 advancement │      │
│  │                                                 │      │
│  │ Prerequisites:                                  │      │
│  │ ✓ All participants complete Workshop 1         │      │
│  │ ✓ Facilitator reviews submissions              │      │
│  │ ⏳ Facilitator advances cohort                 │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 📙 Workshop 3: Community Collaboration          │      │
│  │ 🔒 Locked                                       │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  📥 Export & Reports                                        │
│  [Export All Data CSV]  [Generate PDF Report]              │
│  [Export Workshop 1 Responses]                              │
│                                                             │
│  👥 Participant Management                                  │
│  [View All Participants]  [Reset Progress]  [Add New]      │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**
- 📊 Real-time progress tracking
- 🚦 Color-coded workshop states (completed, active, locked)
- ✓ One-click "Advance All" button
- 📥 Export capabilities per workshop
- 👥 Participant management links

### Facilitator Workshop Responses View

**URL:** `/mana/facilitator/<assessment_id>/workshop/<workshop_type>/`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Workshop 1: All Participant Responses                      │
│  « Back to Dashboard                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Submission Status: 25/25 Completed (100%)               │
│  ✅ All participants have submitted                         │
│                                                             │
│  🎯 Ready to Advance                                        │
│  [✓ Advance All Participants to Workshop 2 →]             │
│                                                             │
│  ─────────────────────────────────────────────────────     │
│                                                             │
│  🔍 Filters & Search                                        │
│  ┌─────────────────────────────────────────────────┐      │
│  │ Province: [All ▼]  Stakeholder: [All ▼]        │      │
│  │ Search: [                                  🔍] │      │
│  │                                                 │      │
│  │ [Clear Filters]  [Export Filtered Results]     │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  📄 Participant Responses (25)                              │
│                                                             │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 👤 Juan Dela Cruz                               │      │
│  │ 📍 Zamboanga del Norte • Community Elder        │      │
│  │ 📅 Submitted: Jan 27, 2025 2:30 PM             │      │
│  │                                                 │      │
│  │ Q1: What is the estimated population...        │      │
│  │ A: Approximately 5,000 residents...            │      │
│  │                                                 │      │
│  │ Q2: Key economic activities...                 │      │
│  │ A: Agriculture (60%), fishing (25%)...         │      │
│  │                                                 │      │
│  │ [▼ Show all 10 responses]                      │      │
│  │                                                 │      │
│  │ [View Full Submission]  [Export PDF]           │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────┐      │
│  │ 👤 Maria Santos                                 │      │
│  │ 📍 Zamboanga del Sur • Women Leader            │      │
│  │ 📅 Submitted: Jan 27, 2025 3:15 PM             │      │
│  │ ...                                             │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  [Load More]  [Export All as ZIP]                          │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**
- 📊 Submission progress at top
- 🎯 Prominent "Advance All" button when ready
- 🔍 Filter by province, stakeholder type
- 📄 Expandable responses (preview + full view)
- 📥 Export individual or bulk

---

## Workflow Summary

### Complete Assessment Workflow

```
┌────────────────────────────────────────────────────────────┐
│  PHASE 1: Setup (OOBC Staff)                               │
├────────────────────────────────────────────────────────────┤
│  1. Create Regional MANA Assessment                        │
│     • Assessment details (title, description, region)      │
│     • Schedule (start date, estimated duration)            │
│                                                            │
│  2. Create Workshop Activities                             │
│     • Workshop 1-5 (titles, descriptions)                  │
│     • Configure questions for each workshop                │
│                                                            │
│  3. Create Facilitator Account                             │
│     • Create User with username/password                   │
│     • Assign can_facilitate_workshop permission            │
│                                                            │
│  4. Create Participant Accounts                            │
│     • Import participant list (CSV or manual)              │
│     • Create WorkshopParticipantAccount for each           │
│     • Send login credentials                               │
└────────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────┐
│  PHASE 2: Onboarding (Participants)                        │
├────────────────────────────────────────────────────────────┤
│  1. First Login                                            │
│     • Participant logs in with provided credentials        │
│     • Redirected to onboarding page                        │
│                                                            │
│  2. Consent & Profile                                      │
│     • Read and agree to data privacy consent               │
│     • Complete demographic profile                         │
│     • Set password (if needed)                             │
│                                                            │
│  3. Dashboard Access                                       │
│     • Onboarding complete → redirect to dashboard          │
│     • Workshop 1 is accessible                             │
└────────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────┐
│  PHASE 3: Workshop Cycle (Participants + Facilitator)      │
├────────────────────────────────────────────────────────────┤
│  PARTICIPANT ACTIONS:                                      │
│                                                            │
│  1. Access Workshop 1                                      │
│     • View workshop description and questions              │
│     • Begin filling out responses                          │
│                                                            │
│  2. Work on Responses                                      │
│     • Auto-save as participant types                       │
│     • Save drafts anytime                                  │
│     • Return and continue later                            │
│                                                            │
│  3. Submit Workshop                                        │
│     • Click "Submit Workshop" button                       │
│     • Confirm submission (cannot undo)                     │
│     • Redirected to Review Page                            │
│                                                            │
│  4. Review Submitted Answers                               │
│     • View all submitted responses (read-only)             │
│     • See "Waiting for facilitator" banner                 │
│     • Check progress: "X of Y participants submitted"      │
│     • WAIT - cannot proceed to Workshop 2                  │
│  ─────────────────────────────────────────────────────── │
│  FACILITATOR ACTIONS:                                      │
│                                                            │
│  5. Monitor Submissions                                    │
│     • Facilitator dashboard shows: 25/25 submitted         │
│     • Review participant responses                         │
│     • Filter by province, stakeholder type                 │
│     • Export responses for analysis                        │
│                                                            │
│  6. Advance Cohort                                         │
│     • Click "Advance All Participants to Workshop 2"       │
│     • Confirm action                                       │
│     • System unlocks Workshop 2 for ALL participants       │
│  ─────────────────────────────────────────────────────── │
│  PARTICIPANT CONTINUES:                                    │
│                                                            │
│  7. Access Workshop 2                                      │
│     • Participant refreshes/returns to dashboard           │
│     • Sees "Workshop 2 Now Available!" notification        │
│     • Can access Workshop 2                                │
│     • Can still review Workshop 1 (read-only)              │
│                                                            │
│  8. Repeat for Workshops 2-5                               │
│     • Same cycle: fill → submit → review → wait → advance │
│     • Facilitator reviews and advances after each          │
└────────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────┐
│  PHASE 4: Completion & Analysis                            │
├────────────────────────────────────────────────────────────┤
│  1. All Workshops Completed                                │
│     • Participants see "Assessment Complete" status        │
│     • Can review all 5 workshops                           │
│                                                            │
│  2. Facilitator Analysis                                   │
│     • Access all workshop responses                        │
│     • Generate consolidated reports                        │
│     • Export data for stakeholder analysis                 │
│     • Create synthesis documents                           │
│                                                            │
│  3. Next Steps                                             │
│     • Share findings with OOBC leadership                  │
│     • Plan interventions based on assessment               │
│     • Archive assessment data                              │
└────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

### Functional Requirements

- [ ] Participant cannot advance to next workshop without facilitator action
- [ ] Post-submission review page shows all participant answers
- [ ] Facilitator can view all participant responses
- [ ] "Advance All Participants" button works for entire cohort
- [ ] Workshop submission locks responses (cannot edit)
- [ ] Facilitator dashboard shows real-time progress
- [ ] All participants advance simultaneously when facilitator acts

### User Experience

- [ ] Clear "waiting" state for participants after submission
- [ ] Facilitator can easily identify who has/hasn't submitted
- [ ] One-click advancement for facilitator
- [ ] Participants notified when next workshop unlocks
- [ ] No auto-advancement surprises for participants

### Technical Requirements

- [ ] No regression in existing functionality
- [ ] Access control properly enforced
- [ ] Database migration successful
- [ ] All tests passing
- [ ] Performance acceptable (< 2s page load)

---

## Migration Strategy

### For Existing Assessments

If there are already active assessments with participants:

1. **Run Migration**
   - Add `facilitator_advanced_to` field
   - Default to `workshop_5` for all existing participants (full access)

2. **Communication**
   - Notify active participants of system changes
   - Explain new workflow with facilitator control

3. **Phased Rollout**
   - Phase 1: New assessments use new system
   - Phase 2: Migrate active assessments (if possible)
   - Phase 3: Full switchover

### Backward Compatibility

- Existing participants keep their progress
- Can complete workshops already started
- New workshops follow new advancement rules

---

## Open Questions & Decisions Needed

1. **Facilitator Assignment**
   - Can one facilitator manage multiple assessments?
   - Should facilitators be linked to specific assessments?
   - **Decision:** Yes, facilitators can manage multiple. Link via UI filters.

2. **Notification System**
   - How do participants know when next workshop is available?
   - Email notifications? In-app only?
   - **Decision:** Start with in-app banner, add email later.

3. **Partial Advancement**
   - Can facilitator advance some participants but not others?
   - **Decision:** No, all or nothing. Keeps cohort synchronized.

4. **Review Period**
   - Should there be a minimum review period before advancement?
   - **Decision:** No, facilitator decides when ready.

5. **Re-opening Submissions**
   - Can facilitator unlock submitted workshop for editing?
   - **Decision:** Yes, via "Reset Progress" for individual participant.

---

## Timeline

**Total Estimated Effort:** 30-40 hours

| Phase | Tasks | Effort | Timeline |
|-------|-------|--------|----------|
| 1 | Database & model changes | 2-3 hours | Week 1 |
| 2 | Access control logic | 4-6 hours | Week 1 |
| 3 | Post-submission review | 4-6 hours | Week 1-2 |
| 4 | Facilitator dashboard | 8-12 hours | Week 2-3 |
| 5 | Account creation | 4-6 hours | Week 3 |
| 6 | Testing & validation | 4-6 hours | Week 3-4 |
| - | Documentation | 4-6 hours | Week 4 |

**Target Completion:** 3-4 weeks

---

## Appendix

### Example Facilitator Credentials

For testing purposes:

```
Username: mana_facilitator_r9
Password: changeme123
Email: facilitator.r9@oobc.gov.ph
Permissions: can_facilitate_workshop, can_access_regional_mana
```

### Example Assessment Setup

```python
# Create assessment
assessment = Assessment.objects.create(
    title="Region IX OBC Needs Assessment",
    assessment_level="regional",
    province=Province.objects.get(name="Zamboanga del Norte"),
    # ... other fields
)

# Create workshops
for i in range(1, 6):
    WorkshopActivity.objects.create(
        assessment=assessment,
        workshop_type=f"workshop_{i}",
        title=f"Workshop {i}",
        status="active"
    )

# Create facilitator
facilitator_user = User.objects.create_user(
    username="facilitator_r9",
    password="changeme123"
)
facilitator_user.user_permissions.add(
    Permission.objects.get(codename='can_facilitate_workshop')
)

# Create participants
for name in ["Juan", "Maria", "Pedro"]:
    user = User.objects.create_user(username=name.lower())
    WorkshopParticipantAccount.objects.create(
        user=user,
        assessment=assessment,
        province=assessment.province,
        stakeholder_type="elder",
        current_workshop="workshop_1",
        facilitator_advanced_to="workshop_1"
    )
```

---

**Document Version:** 1.0
**Last Updated:** 2025-01-27
**Author:** AI Assistant
**Status:** Ready for Implementation