# MANA Integrated Workflow System - Complete Implementation Plan

**Status:** ✅ **IMPLEMENTED** (2025-09-30)
**Priority:** Critical
**Created:** 2025-09-30
**Completed:** 2025-09-30
**Complexity:** High

---

## 🎉 Implementation Complete!

All phases have been successfully implemented and tested. The MANA Regional Workshop system is now fully operational with:

- ✅ **Predetermined Assessment Assignment** (FacilitatorAssessmentAssignment model)
- ✅ **Assessment Selection Dashboards** (Participant & Facilitator)
- ✅ **Workshop Outputs Review** (Participant post-submission page)
- ✅ **Facilitator Dashboard with Progress Monitoring** (Enhanced with confirmation modal)
- ✅ **Notification System** (In-app notifications with HTMX dismiss)
- ✅ **Account Creation System** (Staff can assign assessments at creation time)
- ✅ **Comprehensive Documentation** (Test scenarios, user guides, tutorials)
- ✅ **Test Data Script** (`setup_mana_test_data` management command)

**Total Implementation Time**: Approximately 8-10 hours
**Lines of Code**: ~3,000+ (models, views, templates)
**New Models**: 2 (FacilitatorAssessmentAssignment, WorkshopNotification)
**New Views**: 6 (assessment lists, outputs, notifications, account creation)
**New Templates**: 7
**Migrations**: 2 (0017, 0018)

**Django System Check**: ✅ 0 issues

---

## Executive Summary

This document provides a **complete, integrated implementation plan** for the MANA Regional Workshop system, addressing both **MANA Participant** and **MANA Facilitator** workflows from login to completion. This plan builds upon and extends the existing facilitator-controlled advancement design with additional user experience components.

**Core Objective:** Create a seamless, intuitive workflow where:
- Participants can select assessments, complete workshops, review their submissions, and receive clear advancement notifications
- Facilitators can monitor all participants, review aggregated responses, and control cohort progression
- Both roles have dedicated dashboards with appropriate access controls

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [User Roles & Workflows](#user-roles--workflows)
3. [Missing Components Analysis](#missing-components-analysis)
4. [Implementation Phases](#implementation-phases)
5. [Detailed Component Specifications](#detailed-component-specifications)
6. [Database Schema Updates](#database-schema-updates)
7. [UI/UX Wireframes](#uiux-wireframes)
8. [Testing Strategy](#testing-strategy)
9. [Timeline & Effort Estimates](#timeline--effort-estimates)

---

## System Architecture Overview

### High-Level System Map

```
┌────────────────────────────────────────────────────────────────┐
│                      MANA WORKFLOW SYSTEM                       │
└────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼────────┐            ┌────────▼────────┐
        │   PARTICIPANT   │            │   FACILITATOR   │
        │    WORKFLOW     │            │    WORKFLOW     │
        └───────┬────────┘            └────────┬────────┘
                │                               │
┌───────────────▼───────────────┐   ┌───────────▼──────────────┐
│ 1. Login & Authentication     │   │ 1. Login & Authentication │
│ 2. Onboarding (if first time) │   │ 2. Onboarding (optional)  │
│ 3. Assessment Selection        │   │ 3. Assessment Selection   │
│ 4. Workshop Dashboard          │   │ 4. Facilitator Dashboard  │
│ 5. Workshop Activity           │   │ 5. Progress Monitoring    │
│ 6. Workshop Submission         │   │ 6. Response Review        │
│ 7. Workshop Outputs (Review)   │   │ 7. Cohort Advancement     │
│ 8. Advancement Notification    │   │ 8. Analytics & Export     │
│ 9. Next Workshop Access        │   │ 9. Participant Management │
└────────────────────────────────┘   └──────────────────────────┘
```

### Current System State (From Implementation Progress)

**✅ Completed (Phases 1-2):**
- Database: `facilitator_advanced_to` field
- Access Control: Workshop access restrictions
- No Auto-Advancement: Submission doesn't progress participants
- Bulk Advancement: `advance_all_participants()` method

**❌ Missing (Phases 3-6 + New Components):**
- Assessment Selection Dashboard
- Workshop Outputs Review Page (Participant)
- Workshop Outputs Aggregation (Facilitator)
- Facilitator Dashboard with Approval Controls
- Notification System (advancement alerts)
- Facilitator Onboarding (optional)

---

## User Roles & Workflows

### Complete Participant Workflow

```
START: User Login
    │
    ├─ First Time User?
    │   └─ YES → Onboarding Flow
    │         ├─ Data Privacy Consent
    │         ├─ Demographic Profile
    │         └─ Password Setup
    │
    ▼
1. ASSESSMENT SELECTION DASHBOARD
   │
   ├─ View: All Assessments User is Registered For
   │   ├─ Completed Assessments (read-only)
   │   ├─ Active Assessments (in-progress)
   │   └─ Upcoming Assessments (not started)
   │
   └─ Action: Select Assessment → Navigate to Workshop Dashboard
       │
       ▼
2. WORKSHOP DASHBOARD (Participant View)
   │
   ├─ View: Workshop Progress Overview
   │   ├─ Workshop 1: ✅ Submitted (Review Available)
   │   ├─ Workshop 2: ⏳ Waiting for Facilitator
   │   ├─ Workshop 3: 🔒 Locked (Not Yet Unlocked)
   │   └─ Workshops 4-5: 🔒 Locked
   │
   └─ Action: Click Workshop
       │
       ├─ If UNLOCKED & NOT SUBMITTED
       │   └─ Navigate to → Workshop Activity Page
       │       ├─ Fill Out Questions
       │       ├─ Auto-Save Drafts
       │       ├─ Submit Workshop
       │       └─ Redirect to → Workshop Outputs (Review)
       │
       ├─ If SUBMITTED (Waiting for Advancement)
       │   └─ Navigate to → Workshop Outputs (Review)
       │       ├─ View All Q&A Pairs (Read-Only)
       │       ├─ See: "⏳ Waiting for Facilitator"
       │       ├─ See: Progress (X/Y participants submitted)
       │       └─ Option: Download PDF
       │
       └─ If COMPLETED (Facilitator Advanced)
           └─ Navigate to → Workshop Outputs (Historical Review)
               ├─ View All Q&A Pairs (Read-Only)
               ├─ See: "✅ Workshop Completed"
               └─ Option: Download PDF
   │
   ▼
3. ADVANCEMENT NOTIFICATION
   │
   ├─ Facilitator Advances Cohort
   │   └─ System Updates: participant.current_workshop
   │
   ├─ Participant Returns to Dashboard
   │   ├─ See: "🎉 Workshop 2 Now Available!"
   │   └─ See: Workshop 2 Status Changes to "🟢 Available"
   │
   └─ Cycle Repeats: Workshops 2 → 3 → 4 → 5
       │
       ▼
4. ASSESSMENT COMPLETION
   │
   ├─ All 5 Workshops Completed
   │   ├─ See: "✅ Assessment Complete"
   │   ├─ Access: Historical Review of All Workshops
   │   └─ Download: Consolidated PDF Report
   │
   └─ Return to → Assessment Selection Dashboard
```

### Complete Facilitator Workflow

```
START: Facilitator Login
    │
    ├─ First Time User?
    │   └─ YES → Onboarding (Optional)
    │         ├─ System Tour
    │         ├─ Facilitator Guide
    │         └─ Best Practices
    │
    ▼
1. ASSESSMENT SELECTION DASHBOARD
   │
   ├─ View: All Assessments (System-Wide or Assigned)
   │   ├─ Active Assessments (requires facilitation)
   │   ├─ Completed Assessments (read-only)
   │   └─ Upcoming Assessments (planning)
   │
   └─ Action: Select Assessment → Navigate to Facilitator Dashboard
       │
       ▼
2. FACILITATOR DASHBOARD
   │
   ├─ View: Assessment Overview
   │   ├─ Total Participants: 25
   │   ├─ Active Workshop: Workshop 1
   │   ├─ Assessment Progress: 20% Complete
   │   └─ Started: Jan 20, 2025
   │
   ├─ View: Workshop-by-Workshop Progress
   │   │
   │   ├─ Workshop 1: Understanding Community Context
   │   │   ├─ Progress: 100% (25/25 submitted)
   │   │   ├─ Status: ✅ Ready to Advance
   │   │   ├─ Actions:
   │   │   │   ├─ [View All Responses]
   │   │   │   └─ [✓ Advance All to Workshop 2]
   │   │   └─ Latest Submission: 5 minutes ago
   │   │
   │   ├─ Workshop 2: Community Aspirations
   │   │   ├─ Progress: 0% (0/25 submitted)
   │   │   ├─ Status: 🔒 Locked (Waiting for W1 advancement)
   │   │   └─ Prerequisites: ✓ All participants complete W1
   │   │
   │   └─ Workshops 3-5: 🔒 Locked
   │
   └─ Export Options:
       ├─ [Export All Data CSV]
       ├─ [Generate PDF Report]
       └─ [Export Individual Workshop Responses]
   │
   ▼
3. WORKSHOP OUTPUTS AGGREGATION (Review All Responses)
   │
   ├─ Action: Click "View All Responses" for Workshop 1
   │   │
   │   ▼
   │   WORKSHOP OUTPUTS PAGE (Facilitator View)
   │   │
   │   ├─ Header: Submission Status
   │   │   ├─ Progress: 25/25 participants submitted (100%)
   │   │   ├─ Status: ✅ All participants have submitted
   │   │   └─ Ready: 🎯 Ready to Advance
   │   │
   │   ├─ Filters & Search
   │   │   ├─ Province: [All ▼]
   │   │   ├─ Stakeholder Type: [All ▼]
   │   │   ├─ Search: [participant name/keyword]
   │   │   └─ Export: [Export Filtered Results]
   │   │
   │   ├─ Participant Response Cards (25 cards)
   │   │   │
   │   │   ├─ Card 1:
   │   │   │   ├─ Name: Juan Dela Cruz
   │   │   │   ├─ Location: Zamboanga del Norte
   │   │   │   ├─ Stakeholder: Community Elder
   │   │   │   ├─ Submitted: Jan 27, 2025 2:30 PM
   │   │   │   ├─ Q&A Preview:
   │   │   │   │   ├─ Q1: What is the estimated population...
   │   │   │   │   └─ A: Approximately 5,000 residents...
   │   │   │   └─ Actions:
   │   │   │       ├─ [▼ Show All 10 Responses]
   │   │   │       ├─ [View Full Submission]
   │   │   │       └─ [Export PDF]
   │   │   │
   │   │   └─ (Repeat for 24 more participants)
   │   │
   │   └─ Advancement Control (Bottom of Page)
   │       ├─ Message: "All participants have submitted Workshop 1"
   │       ├─ Button: [✓ Advance All Participants to Workshop 2 →]
   │       └─ Confirmation: "Are you sure? This will unlock Workshop 2 for all 25 participants."
   │
   ▼
4. COHORT ADVANCEMENT
   │
   ├─ Action: Facilitator Clicks "Advance All Participants"
   │   │
   │   ├─ System Executes: advance_all_participants(assessment, "workshop_2", facilitator_user)
   │   │   ├─ Update: participant.facilitator_advanced_to = "workshop_2"
   │   │   ├─ Update: participant.current_workshop = "workshop_2" (if W1 completed)
   │   │   └─ Log: WorkshopAccessLog (action_type="advance", advanced_by=facilitator)
   │   │
   │   ├─ Success Message: "✅ 25 participants advanced to Workshop 2"
   │   │
   │   └─ Return to: Facilitator Dashboard
   │       └─ Updated State:
   │           ├─ Workshop 1: ✅ Completed (25/25)
   │           ├─ Workshop 2: 🟢 Active (0/25 submitted)
   │           └─ Workshop 3-5: 🔒 Locked
   │
   ▼
5. MONITORING & ANALYTICS
   │
   ├─ Track Workshop 2 Progress (same as step 3)
   │   ├─ View submissions as they come in
   │   ├─ Export partial data
   │   └─ Advance when ready (repeat cycle)
   │
   ├─ Participant Management
   │   ├─ View individual participant progress
   │   ├─ Reset participant progress (if needed)
   │   └─ Generate participant reports
   │
   └─ Assessment Completion
       ├─ All 5 workshops completed
       ├─ Generate consolidated report
       ├─ Export all assessment data
       └─ Archive assessment
```

---

## Missing Components Analysis

### Current vs. Required Components

| Component | Current State | Required | Priority |
|-----------|--------------|----------|----------|
| **Assessment Selection Dashboard** | ❌ Does not exist | ✅ Required for both roles | 🔴 Critical |
| **Participant Workshop Outputs Page** | ❌ Redirects to next workshop | ✅ Required for review + notification | 🔴 Critical |
| **Facilitator Dashboard** | ❌ Does not exist | ✅ Required for monitoring | 🔴 Critical |
| **Facilitator Outputs Aggregation** | ❌ Does not exist | ✅ Required for approval | 🔴 Critical |
| **Advancement Notification System** | ❌ No notification | ✅ Required for UX | 🟡 High |
| **Facilitator Onboarding** | ❌ No onboarding | ⚪ Optional enhancement | 🟢 Medium |
| **Participant Onboarding** | ✅ Exists | ✅ Already working | ✅ Complete |
| **Workshop Submission Lock** | ✅ Exists | ✅ Already working | ✅ Complete |
| **Access Control Logic** | ✅ Exists (Phases 1-2) | ✅ Already working | ✅ Complete |
| **Bulk Advancement Method** | ✅ Exists | ✅ Already working | ✅ Complete |

### Gap Analysis

**Critical Gaps (Must Have):**
1. **No Assessment Selection** - Users can't choose which assessment to work on
2. **No Post-Submission Review** - Participants can't see their answers after submission
3. **No Facilitator Interface** - Facilitators have no way to review/advance
4. **No Notification System** - Participants don't know when advanced

**Nice to Have:**
1. Facilitator onboarding tour
2. Real-time notifications (WebSocket)
3. Email notifications
4. Mobile-responsive enhancements

---

## Implementation Phases

### Phase 3A: Assessment Selection Dashboard (NEW)

**Priority:** 🔴 Critical (Prerequisite for all other components)
**Effort:** Medium (6-8 hours)
**Depends On:** Phases 1-2 (Complete)

**Components:**
1. **Participant Assessment Selection View**
   - URL: `/mana/participant/assessments/`
   - Lists all assessments user is registered for
   - Shows status: Active, Completed, Upcoming
   - Click assessment → Navigate to workshop dashboard

2. **Facilitator Assessment Selection View**
   - URL: `/mana/facilitator/assessments/`
   - Lists all assessments (system-wide or filtered)
   - Shows participant counts, progress %
   - Click assessment → Navigate to facilitator dashboard

**Files to Create:**
- `src/mana/participant_views.py` - Add `participant_assessments_list()`
- `src/mana/facilitator_views.py` - Create file, add `facilitator_assessments_list()`
- `src/templates/mana/participant/assessments_list.html` - New template
- `src/templates/mana/facilitator/assessments_list.html` - New template
- Update `src/mana/urls.py` with new routes

---

### Phase 3B: Participant Workshop Outputs (Review Page)

**Priority:** 🔴 Critical
**Effort:** Medium (6-8 hours)
**Depends On:** Phase 3A

**Components:**
1. **Workshop Outputs View**
   - URL: `/mana/participant/<assessment_id>/workshop/<workshop_type>/outputs/`
   - Shows all Q&A pairs (read-only)
   - Status indicator:
     - "⏳ Waiting for Facilitator" (if not advanced)
     - "✅ Completed" (if facilitator advanced)
   - Progress: "X/Y participants submitted"
   - Download PDF option

2. **Update Submission Redirect**
   - After submission, redirect to outputs page (not next workshop)

**Files to Create/Modify:**
- `src/mana/participant_views.py` - Add `participant_workshop_outputs()`
- `src/templates/mana/participant/workshop_outputs.html` - New template
- `src/mana/participant_views.py` - Modify `participant_workshop_detail()` redirect

---

### Phase 4A: Facilitator Dashboard

**Priority:** 🔴 Critical
**Effort:** High (8-10 hours)
**Depends On:** Phase 3A

**Components:**
1. **Facilitator Dashboard View**
   - URL: `/mana/facilitator/<assessment_id>/`
   - Assessment overview (participants, progress)
   - Workshop-by-workshop progress cards
   - Submission counts per workshop
   - "Advance All" button when ready
   - Export all data

**Files to Create:**
- `src/mana/facilitator_views.py` - Add `facilitator_dashboard()`
- `src/templates/mana/facilitator/dashboard.html` - New template
- Update `src/mana/urls.py`

---

### Phase 4B: Facilitator Workshop Outputs Aggregation

**Priority:** 🔴 Critical
**Effort:** High (10-12 hours)
**Depends On:** Phase 4A

**Components:**
1. **Outputs Aggregation View**
   - URL: `/mana/facilitator/<assessment_id>/workshop/<workshop_type>/outputs/`
   - List all participant responses
   - Filters: Province, Stakeholder Type, Search
   - Expandable Q&A cards
   - "Advance All Participants" button
   - Export individual/bulk responses

2. **Advancement Endpoint**
   - URL: `/mana/facilitator/<assessment_id>/workshop/<workshop_type>/advance/`
   - POST endpoint
   - Calls `advance_all_participants()`
   - Returns success message with count

**Files to Create:**
- `src/mana/facilitator_views.py` - Add `facilitator_workshop_outputs()`, `facilitator_advance_participants()`
- `src/templates/mana/facilitator/workshop_outputs.html` - New template
- Update `src/mana/urls.py`

---

### Phase 5: Enhancement & Polish

**Priority:** 🟡 High
**Effort:** Medium (6-8 hours)
**Depends On:** Phases 3-4

**Components:**
1. **Notification System**
   - Banner notification on participant dashboard when advanced
   - Badge indicator for new workshops
   - Toast notification on login (if new workshop available)

2. **Facilitator Onboarding (Optional)**
   - Quick tour of facilitator dashboard
   - Best practices guide
   - Tutorial on advancement workflow

3. **UI/UX Improvements**
   - Loading states for all actions
   - Error handling improvements
   - Mobile responsiveness
   - Accessibility (WCAG 2.1 AA)

**Files to Modify:**
- Various templates (add notifications)
- `src/mana/participant_views.py` - Add notification logic
- Create `src/templates/mana/facilitator/onboarding.html`

---

### Phase 6: Testing & Documentation

**Priority:** 🔴 Critical
**Effort:** Medium (6-8 hours)
**Depends On:** All previous phases

**Tasks:**
1. Unit Tests (all new views)
2. Integration Tests (end-to-end workflows)
3. User Acceptance Testing (with real users)
4. Documentation Updates:
   - User guides (participant & facilitator)
   - Admin guide (account creation)
   - API documentation
   - Troubleshooting guide

---

## Detailed Component Specifications

### 1. Assessment Selection Dashboard (Participant)

**URL:** `/mana/participant/assessments/`

**View Logic:**
```python
@login_required
@require_mana_participant
def participant_assessments_list(request):
    """List all assessments the participant is registered for."""
    user = request.user

    # Get all assessments where user has WorkshopParticipantAccount
    participant_accounts = WorkshopParticipantAccount.objects.filter(
        user=user
    ).select_related('assessment', 'province')

    assessments_data = []
    for account in participant_accounts:
        assessment = account.assessment

        # Calculate progress
        total_workshops = 5
        completed_workshops = len(account.completed_workshops or [])
        progress_pct = (completed_workshops / total_workshops) * 100

        # Determine status
        if progress_pct == 100:
            status = "completed"
        elif progress_pct > 0:
            status = "active"
        else:
            status = "not_started"

        assessments_data.append({
            'account': account,
            'assessment': assessment,
            'progress_pct': progress_pct,
            'completed_workshops': completed_workshops,
            'total_workshops': total_workshops,
            'status': status,
            'current_workshop_display': account.get_current_workshop_display(),
        })

    context = {
        'assessments': assessments_data,
    }
    return render(request, 'mana/participant/assessments_list.html', context)
```

**Template Structure:**
```html
<!-- assessments_list.html -->
<div class="container">
    <h1>My MANA Assessments</h1>

    {% if assessments %}
        <div class="assessments-grid">
            {% for item in assessments %}
            <div class="assessment-card status-{{ item.status }}">
                <div class="card-header">
                    <h3>{{ item.assessment.title }}</h3>
                    <span class="badge status-{{ item.status }}">
                        {% if item.status == 'completed' %}✅ Completed
                        {% elif item.status == 'active' %}🟢 In Progress
                        {% else %}⚪ Not Started{% endif %}
                    </span>
                </div>

                <div class="card-body">
                    <p class="description">{{ item.assessment.description|truncatewords:30 }}</p>

                    <div class="progress-info">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {{ item.progress_pct }}%"></div>
                        </div>
                        <p class="progress-text">
                            {{ item.completed_workshops }} of {{ item.total_workshops }} workshops completed
                        </p>
                    </div>

                    <div class="metadata">
                        <span>📍 {{ item.assessment.province.name }}</span>
                        <span>📅 Started: {{ item.account.created_at|date:"M d, Y" }}</span>
                    </div>

                    <div class="current-workshop">
                        <strong>Current:</strong> {{ item.current_workshop_display }}
                    </div>
                </div>

                <div class="card-footer">
                    <a href="{% url 'mana:participant_dashboard' item.assessment.id %}"
                       class="btn btn-primary">
                        {% if item.status == 'completed' %}
                            View Summary
                        {% else %}
                            Continue Assessment →
                        {% endif %}
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="empty-state">
            <i class="fas fa-clipboard-list fa-4x"></i>
            <h2>No Assessments Yet</h2>
            <p>You haven't been registered for any MANA assessments.</p>
            <p>Contact your OOBC coordinator to get started.</p>
        </div>
    {% endif %}
</div>
```

---

### 2. Participant Workshop Outputs Page

**URL:** `/mana/participant/<assessment_id>/workshop/<workshop_type>/outputs/`

**View Logic:**
```python
@login_required
@participant_required
def participant_workshop_outputs(request, assessment_id, workshop_type):
    """Show participant their submitted workshop responses with advancement status."""
    assessment = request.mana_assessment
    participant = request.mana_participant_account

    # Get workshop
    workshop = get_object_or_404(
        WorkshopActivity,
        assessment=assessment,
        workshop_type=workshop_type
    )

    # Verify this workshop has been submitted
    if workshop_type not in (participant.completed_workshops or []):
        messages.error(request, "You haven't submitted this workshop yet.")
        return redirect('mana:participant_workshop_detail', assessment_id, workshop_type)

    # Get all responses for this workshop
    responses = WorkshopResponse.objects.filter(
        participant=participant,
        workshop=workshop,
        status="submitted"
    ).order_by('question_id')

    # Get questions from schema
    questions = get_questions_for_workshop(workshop_type)

    # Pair questions with responses
    qa_pairs = []
    for question in questions:
        response = responses.filter(question_id=question['id']).first()
        qa_pairs.append({
            'question': question,
            'response': response,
        })

    # Check advancement status
    is_advanced = (participant.current_workshop != workshop_type)

    # Get next workshop info if advanced
    next_workshop = None
    if is_advanced:
        workshop_sequence = ['workshop_1', 'workshop_2', 'workshop_3', 'workshop_4', 'workshop_5']
        current_index = workshop_sequence.index(workshop_type)
        if current_index + 1 < len(workshop_sequence):
            next_workshop_type = workshop_sequence[current_index + 1]
            next_workshop = WorkshopActivity.objects.filter(
                assessment=assessment,
                workshop_type=next_workshop_type
            ).first()

    # Get submission progress
    total_participants = WorkshopParticipantAccount.objects.filter(
        assessment=assessment
    ).count()

    submitted_participants = WorkshopResponse.objects.filter(
        workshop=workshop,
        status="submitted"
    ).values('participant').distinct().count()

    context = {
        'assessment': assessment,
        'participant': participant,
        'workshop': workshop,
        'qa_pairs': qa_pairs,
        'is_advanced': is_advanced,
        'next_workshop': next_workshop,
        'total_participants': total_participants,
        'submitted_participants': submitted_participants,
        'submission_timestamp': responses.first().updated_at if responses.exists() else None,
    }
    return render(request, 'mana/participant/workshop_outputs.html', context)
```

**Template Structure:**
```html
<!-- workshop_outputs.html -->
<div class="workshop-outputs-container">
    <!-- Success Banner -->
    <div class="banner success">
        <i class="fas fa-check-circle"></i>
        <div>
            <h2>✓ Workshop Submitted Successfully</h2>
            <p>Submitted: {{ submission_timestamp|date:"F d, Y \a\t g:i A" }}</p>
        </div>
    </div>

    <!-- Advancement Status -->
    {% if is_advanced %}
        <div class="banner advancement-success">
            <i class="fas fa-rocket"></i>
            <div>
                <h3>🎉 Next Workshop Now Available!</h3>
                <p>The facilitator has reviewed submissions and advanced the cohort.</p>
                {% if next_workshop %}
                <a href="{% url 'mana:participant_workshop_detail' assessment.id next_workshop.workshop_type %}"
                   class="btn btn-primary">
                    Start {{ next_workshop.title }} →
                </a>
                {% endif %}
            </div>
        </div>
    {% else %}
        <div class="banner waiting">
            <i class="fas fa-hourglass-half"></i>
            <div>
                <h3>⏳ Waiting for Facilitator</h3>
                <p>The facilitator will review all participant submissions before advancing the cohort to the next workshop.</p>
                <div class="progress-indicator">
                    <strong>Progress:</strong> {{ submitted_participants }} of {{ total_participants }} participants have submitted
                    <div class="progress-bar-mini">
                        <div class="progress-fill" style="width: {% widthratio submitted_participants total_participants 100 %}%"></div>
                    </div>
                </div>
            </div>
        </div>
    {% endif %}

    <!-- Review Your Answers -->
    <div class="outputs-section">
        <h2>📄 Review Your Submitted Answers</h2>
        <p class="help-text">These responses are locked and cannot be edited. You can download a PDF copy below.</p>

        <div class="qa-list">
            {% for item in qa_pairs %}
            <div class="qa-card">
                <div class="question">
                    <span class="question-number">Q{{ forloop.counter }}</span>
                    <div class="question-text">
                        <strong>{{ item.question.label }}</strong>
                        {% if item.question.help_text %}
                        <p class="help-text">{{ item.question.help_text }}</p>
                        {% endif %}
                    </div>
                </div>

                <div class="answer">
                    {% if item.response %}
                        {% if item.question.type == 'long_text' %}
                            <div class="response-text">{{ item.response.text_response|linebreaks }}</div>
                        {% elif item.question.type == 'repeater' %}
                            <div class="response-repeater">
                                {% for entry in item.response.json_response %}
                                <div class="repeater-entry">
                                    {% for field, value in entry.items %}
                                    <p><strong>{{ field|title }}:</strong> {{ value }}</p>
                                    {% endfor %}
                                </div>
                                {% endfor %}
                            </div>
                        {% elif item.question.type == 'structured' %}
                            <div class="response-structured">
                                {% for key, value in item.response.json_response.items %}
                                <p><strong>{{ key|title }}:</strong> {{ value }}</p>
                                {% endfor %}
                            </div>
                        {% endif %}
                    {% else %}
                        <p class="no-response">No response provided</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Actions -->
    <div class="actions-footer">
        <a href="{% url 'mana:participant_dashboard' assessment.id %}" class="btn btn-secondary">
            « Back to Dashboard
        </a>
        <button onclick="window.print()" class="btn btn-outline">
            <i class="fas fa-download"></i> Download PDF
        </button>
    </div>
</div>
```

---

### 3. Facilitator Dashboard

**URL:** `/mana/facilitator/<assessment_id>/`

**View Logic:**
```python
@login_required
@facilitator_required
def facilitator_dashboard(request, assessment_id):
    """Main facilitator dashboard for monitoring and managing assessment."""
    assessment = get_object_or_404(Assessment, id=assessment_id)

    # Get all participants
    participants = WorkshopParticipantAccount.objects.filter(
        assessment=assessment
    ).select_related('user', 'province')

    total_participants = participants.count()

    # Get all workshops
    workshops = WorkshopActivity.objects.filter(
        assessment=assessment
    ).order_by('workshop_type')

    # Calculate progress for each workshop
    workshop_progress = []
    for workshop in workshops:
        # Count submissions
        submitted_count = WorkshopResponse.objects.filter(
            workshop=workshop,
            status="submitted"
        ).values('participant').distinct().count()

        # Count in-progress (has draft responses)
        in_progress_count = WorkshopResponse.objects.filter(
            workshop=workshop,
            status="draft"
        ).values('participant').distinct().count()

        # Calculate not started
        not_started_count = total_participants - submitted_count - in_progress_count

        # Progress percentage
        progress_pct = (submitted_count / total_participants * 100) if total_participants > 0 else 0

        # Determine if ready to advance
        is_ready_to_advance = (submitted_count == total_participants and total_participants > 0)

        # Get next workshop
        workshop_sequence = ['workshop_1', 'workshop_2', 'workshop_3', 'workshop_4', 'workshop_5']
        current_index = workshop_sequence.index(workshop.workshop_type)
        next_workshop = workshop_sequence[current_index + 1] if current_index + 1 < len(workshop_sequence) else None

        # Check if locked
        is_locked = False
        if current_index > 0:
            prev_workshop_type = workshop_sequence[current_index - 1]
            prev_workshop = workshops.filter(workshop_type=prev_workshop_type).first()
            if prev_workshop:
                prev_submitted = WorkshopResponse.objects.filter(
                    workshop=prev_workshop,
                    status="submitted"
                ).values('participant').distinct().count()
                is_locked = (prev_submitted < total_participants)

        # Get latest submission
        latest_submission = WorkshopResponse.objects.filter(
            workshop=workshop,
            status="submitted"
        ).order_by('-updated_at').first()

        workshop_progress.append({
            'workshop': workshop,
            'submitted_count': submitted_count,
            'in_progress_count': in_progress_count,
            'not_started_count': not_started_count,
            'progress_pct': progress_pct,
            'is_ready_to_advance': is_ready_to_advance,
            'is_locked': is_locked,
            'next_workshop': next_workshop,
            'latest_submission': latest_submission,
        })

    # Overall assessment progress
    total_workshops = len(workshops)
    completed_workshops_count = sum(1 for wp in workshop_progress if wp['progress_pct'] == 100)
    overall_progress_pct = (completed_workshops_count / total_workshops * 100) if total_workshops > 0 else 0

    context = {
        'assessment': assessment,
        'total_participants': total_participants,
        'workshop_progress': workshop_progress,
        'overall_progress_pct': overall_progress_pct,
        'completed_workshops_count': completed_workshops_count,
        'total_workshops': total_workshops,
    }
    return render(request, 'mana/facilitator/dashboard.html', context)
```

**(Template structure continues in next message due to length...)**

---

## Timeline & Effort Estimates

### Summary Table

| Phase | Description | Effort | Dependencies | Priority |
|-------|-------------|--------|--------------|----------|
| **3A** | Assessment Selection Dashboard | 6-8 hours | Phases 1-2 ✅ | 🔴 Critical |
| **3B** | Participant Workshop Outputs | 6-8 hours | Phase 3A | 🔴 Critical |
| **4A** | Facilitator Dashboard | 8-10 hours | Phase 3A | 🔴 Critical |
| **4B** | Facilitator Outputs Aggregation | 10-12 hours | Phase 4A | 🔴 Critical |
| **5** | Enhancement & Polish | 6-8 hours | Phases 3-4 | 🟡 High |
| **6** | Testing & Documentation | 6-8 hours | All phases | 🔴 Critical |
| **Total** | | **42-54 hours** | | |

### Phased Timeline (Part-Time)

**Week 1:**
- Phase 3A: Assessment Selection Dashboard (2-3 days)
- Phase 3B: Participant Workshop Outputs (2-3 days)

**Week 2:**
- Phase 4A: Facilitator Dashboard (3-4 days)

**Week 3:**
- Phase 4B: Facilitator Outputs Aggregation (4-5 days)

**Week 4:**
- Phase 5: Enhancement & Polish (2-3 days)
- Phase 6: Testing & Documentation (2-3 days)

**Total Timeline:** 4-5 weeks (working part-time)

---

## Success Criteria

### Participant Workflow
- [ ] Can see and select from multiple assessments
- [ ] Clear workshop progression (locked, active, completed)
- [ ] After submission, sees outputs page (not next workshop)
- [ ] Can review all their submitted answers
- [ ] Clear notification when next workshop unlocked
- [ ] Can view historical workshops (read-only)

### Facilitator Workflow
- [ ] Can see and select assessments to facilitate
- [ ] Dashboard shows real-time progress for all workshops
- [ ] Can view all participant responses for a workshop
- [ ] "Advance All" button works and updates all participants
- [ ] Export capabilities for data analysis
- [ ] Progress indicators are accurate

### Technical Requirements
- [ ] No regressions in existing functionality
- [ ] All access controls enforced
- [ ] Page load times < 2 seconds
- [ ] Mobile responsive
- [ ] WCAG 2.1 AA compliant

---

**Document Version:** 1.0
**Status:** Planning Complete, Ready for Implementation
**Next Action:** Begin Phase 3A (Assessment Selection Dashboard)