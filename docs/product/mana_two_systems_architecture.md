# MANA Two-System Architecture

**Last Updated:** September 30, 2025

---

## Overview

OBCMS currently operates **two distinct MANA (Mapping and Needs Assessment) systems** serving different user groups with different workflows:

1. **Legacy MANA System** - For OOBC staff and authorized users
2. **Sequential Workshop System** - For external workshop participants

Both systems coexist but are **completely isolated** to prevent unauthorized access and ensure appropriate user experiences.

---

## System 1: Legacy MANA (Staff Only)

### URL Pattern
```
/mana/regional/
/mana/provincial/
/mana/provincial/{province_id}/
/mana/desk-review/
/mana/survey/
/mana/kii/
/mana/manage-assessments/
```

### Purpose
- Internal OOBC staff workflows
- Provincial and regional MANA coordination
- Assessment management (create, edit, view all assessments)
- Desk reviews, surveys, key informant interviews
- Aggregate data analysis across provinces/regions

### User Access
- **Allowed:** OOBC staff (`is_staff=True`) OR users with `can_facilitate_workshop` permission
- **Denied:** Workshop participants (even those with `can_access_regional_mana` permission)

### Key Features
- Multi-assessment dashboard
- Province-level and region-level aggregation
- Direct data entry by staff
- Comprehensive assessment lifecycle management
- Integration with broader OBCMS modules (communities, coordination, policies)

### Implementation Details
- **Views:** `common.views.mana.mana_regional_overview`, etc.
- **URL Config:** `common/urls.py` (lines 38-54)
- **Access Control:**
  - `@login_required` decorator
  - Additional staff check in view logic (line 781-789 of `common/views/mana.py`)
  - Explicitly **excluded** from `ManaParticipantAccessMiddleware.ALLOWED_PREFIXES`

### Templates
- `src/templates/mana/mana_regional_overview.html`
- `src/templates/mana/mana_provincial_*`
- Styled with OOBC staff interface patterns

---

## System 2: Sequential Workshop System (Participants)

### URL Pattern
```
/mana/workshops/assessments/{assessment_id}/participant/onboarding/
/mana/workshops/assessments/{assessment_id}/participant/dashboard/
/mana/workshops/assessments/{assessment_id}/participant/workshops/{workshop_type}/
/mana/workshops/assessments/{assessment_id}/facilitator/dashboard/
/mana/workshops/assessments/{assessment_id}/facilitator/participants/
/mana/workshops/assessments/{assessment_id}/facilitator/exports/{workshop_type}/{format}/
```

### Purpose
- External stakeholder engagement (community elders, women leaders, youth, etc.)
- Structured, sequential data collection across 5 workshops
- Facilitator-managed workflow with AI synthesis
- Participant isolation and consent-based participation

### User Access
- **Participants:** Users with `WorkshopParticipantAccount` linked to an assessment
  - Can ONLY access their assigned assessment's workshops
  - Sequential progression enforced (cannot skip workshops)
  - Must complete onboarding (consent + profile) first
- **Facilitators:** Users with `can_facilitate_workshop` permission
  - Can access all participant data for their assessments
  - Can manage participants, advance workshops, generate syntheses

### Key Features
- **5 Sequential Workshops:**
  1. Understanding the Community Context
  2. Community Aspirations and Priorities
  3. Community Collaboration and Empowerment
  4. Community Feedback on Existing Initiatives
  5. OBCs Needs, Challenges, Factors, and Outcomes

- **Structured Data Capture:**
  - Dynamic forms generated from JSON schema
  - 25 questions total across 5 workshops
  - Support for text, long_text, select, repeater, structured fields
  - Autosave every 1.2 seconds (HTMX)

- **Sequential Access Control:**
  - Participants can only access unlocked workshops
  - Completing a workshop auto-unlocks the next one
  - Completed workshops remain accessible for review (read-only)
  - Facilitators can manually unlock/reset if needed

- **AI Synthesis:**
  - Multi-provider support (Anthropic Claude, OpenAI GPT)
  - Filtering by province and stakeholder type
  - Regeneration and approval workflow
  - Token usage tracking

- **Export Capabilities:**
  - CSV, XLSX, PDF formats
  - Respect participant filters
  - Include all metadata and structured responses

### Implementation Details
- **Views:**
  - `mana.participant_views` (onboarding, dashboard, workshop detail)
  - `mana.facilitator_views` (dashboard, participant management, synthesis, exports)
- **URL Config:** `mana/urls.py` (app namespace: `mana`)
- **Models:**
  - `WorkshopParticipantAccount` - Participant identity
  - `WorkshopActivity` - Workshop definition
  - `WorkshopResponse` - Normalized per-question responses
  - `WorkshopSynthesis` - AI-generated consolidations
  - `WorkshopAccessLog` - Audit trail
  - `WorkshopQuestionDefinition` - Versioned question schemas
- **Services:**
  - `WorkshopAccessManager` - Sequential progression logic
  - `AIWorkshopSynthesizer` - AI synthesis pipeline
- **Access Control:**
  - `@participant_required` decorator (verifies `WorkshopParticipantAccount`)
  - `@facilitator_required` decorator (verifies permissions)
  - `ManaParticipantAccessMiddleware` - Restricts participants to workshop system only
  - `ManaWorkshopContextMiddleware` - Attaches assessment/participant context

### Templates
- `src/templates/mana/participant/` (onboarding, dashboard, workshop_detail)
- `src/templates/mana/facilitator/` (dashboard, participants)
- HTMX-powered for instant UI updates

---

## Access Control Matrix

| User Type | /mana/regional/ | /mana/workshops/ | Permissions |
|-----------|----------------|------------------|-------------|
| **OOBC Staff** | ✅ Full Access | ✅ Facilitator Dashboard | `is_staff=True` |
| **Facilitator** | ✅ Full Access | ✅ Facilitator Dashboard | `can_facilitate_workshop` |
| **Workshop Participant** | ❌ Denied | ✅ Participant Dashboard (own assessment only) | `can_access_regional_mana` + `WorkshopParticipantAccount` |
| **Regular User** | ❌ Denied | ❌ Denied | None |

---

## Middleware Enforcement

### `ManaParticipantAccessMiddleware`
**Location:** `src/mana/middleware.py:59-115`

**Purpose:** Restricts non-staff participants to workshop system only

**Logic:**
1. If user is staff or has `can_facilitate_workshop` → **Allow all**
2. If user has `can_access_regional_mana` but NO `WorkshopParticipantAccount` → **Redirect to dashboard**
3. If user has `WorkshopParticipantAccount`:
   - **Allowed paths:** `/mana/workshops/`, `/dashboard/`, `/profile/`, `/logout/`
   - **Denied paths:** `/mana/regional/`, `/mana/provincial/`, ALL other modules
   - If not onboarded → **Force redirect to onboarding**
   - Otherwise → **Restrict to participant dashboard and assigned workshops**

**Key Change (Sept 30, 2025):**
- **Removed** `/mana/regional/` and `/mana/provincial/` from `ALLOWED_PREFIXES`
- Participants can NO LONGER access legacy MANA system

### Staff Check in `mana_regional_overview`
**Location:** `src/common/views/mana.py:781-789`

**Purpose:** Double protection for legacy MANA system

**Logic:**
```python
if not request.user.is_staff and not request.user.has_perm("mana.can_facilitate_workshop"):
    messages.error(request, "Access denied...")
    return redirect("common:dashboard")
```

---

## Participant Workflow (Sequential System)

```
1. Participant invited & account created
   └─> User created with temporary password
   └─> WorkshopParticipantAccount linked to Assessment

2. First login
   └─> Forced to /mana/workshops/assessments/{id}/participant/onboarding/
   └─> Must give consent
   └─> Must complete profile (stakeholder type, province, org)

3. After onboarding
   └─> Redirected to /mana/workshops/assessments/{id}/participant/dashboard/
   └─> Sees 5 workshops:
       - Workshop 1: UNLOCKED (green)
       - Workshops 2-5: LOCKED (gray)

4. Completes Workshop 1
   └─> Submits responses
   └─> System auto-unlocks Workshop 2
   └─> Workshop 1 becomes read-only (can review, cannot edit)

5. Repeats for Workshops 2-5
   └─> Sequential progression enforced
   └─> Cannot skip workshops
   └─> All completed workshops accessible for review

6. After completing all 5 workshops
   └─> current_workshop = "" (empty)
   └─> completed_workshops = ["workshop_1", ..., "workshop_5"]
   └─> All workshops remain accessible (read-only)
```

---

## Facilitator Workflow (Sequential System)

```
1. Import participants
   └─> Bulk CSV import OR single-participant registration
   └─> System creates User + WorkshopParticipantAccount
   └─> Temporary passwords generated

2. Send invitations
   └─> Email/SMS with login credentials
   └─> Onboarding deadline reminder

3. Monitor progress
   └─> Facilitator dashboard shows submission rates
   └─> Filter by province, stakeholder type
   └─> Target: ≥85% submission per workshop

4. Advance participants
   └─> "Advance All" button unlocks next workshop for everyone
   └─> OR automatic based on schedule (auto-unlock)

5. Generate AI synthesis
   └─> Select workshop, filters (province/stakeholder), provider (Anthropic/OpenAI)
   └─> Review synthesized insights
   └─> Regenerate if needed
   └─> Approve for inclusion in reports

6. Export data
   └─> CSV/XLSX/PDF with filters
   └─> Target: ≤10s for 100 responses
```

---

## Migration Strategy

### Do NOT migrate participants to staff system
- Legacy MANA (`/mana/regional/`) remains staff-only
- Workshop participants stay in sequential system (`/mana/workshops/`)
- Two systems serve different purposes and should remain separate

### Future Consolidation (Optional)
If OOBC decides to consolidate systems:
1. Migrate legacy workshop data to new `WorkshopActivity`/`WorkshopResponse` models
2. Create `WorkshopParticipantAccount` for historical participants
3. Deprecate legacy `/mana/regional/` views
4. Train staff to use facilitator dashboard (`/mana/workshops/assessments/{id}/facilitator/`)

**Recommendation:** Keep systems separate. They serve different user needs.

---

## Testing Access Control

### Test 1: Participant Cannot Access Legacy System
```python
# Create participant
user = User.objects.create_user(username="participant@test.com", password="test")
participant = WorkshopParticipantAccount.objects.create(
    user=user,
    assessment=assessment,
    stakeholder_type="elder",
    consent_given=True,
    profile_completed=True,
)

# Login as participant
client.login(username="participant@test.com", password="test")

# Try to access legacy MANA
response = client.get("/mana/regional/")

# Expected: Redirect to dashboard with error message
assert response.status_code == 302
assert response.url == "/dashboard/"
```

### Test 2: Staff Can Access Both Systems
```python
# Create staff user
staff = User.objects.create_user(username="staff@test.com", password="test", is_staff=True)

# Login as staff
client.login(username="staff@test.com", password="test")

# Access legacy MANA
response = client.get("/mana/regional/")
assert response.status_code == 200  # Success

# Access facilitator dashboard
response = client.get(f"/mana/workshops/assessments/{assessment.id}/facilitator/dashboard/")
assert response.status_code == 200  # Success
```

### Test 3: Participant Restricted to Own Assessment
```python
# Create two assessments
assessment1 = Assessment.objects.create(...)
assessment2 = Assessment.objects.create(...)

# Participant linked to assessment1
participant = WorkshopParticipantAccount.objects.create(user=user, assessment=assessment1, ...)

# Login as participant
client.login(username="participant@test.com", password="test")

# Can access assessment1
response = client.get(f"/mana/workshops/assessments/{assessment1.id}/participant/dashboard/")
assert response.status_code == 200

# Cannot access assessment2
response = client.get(f"/mana/workshops/assessments/{assessment2.id}/participant/dashboard/")
assert response.status_code == 403  # Forbidden
```

---

## URLs Summary

| URL | System | Users | Purpose |
|-----|--------|-------|---------|
| `/mana/regional/` | Legacy | OOBC Staff, Facilitators | Regional MANA overview |
| `/mana/provincial/` | Legacy | OOBC Staff, Facilitators | Provincial MANA management |
| `/mana/manage-assessments/` | Legacy | OOBC Staff | Assessment CRUD |
| `/mana/workshops/assessments/{id}/participant/` | Sequential | Participants | Participant dashboard & workshops |
| `/mana/workshops/assessments/{id}/facilitator/` | Sequential | Facilitators, Staff | Facilitator controls & synthesis |

---

## Key Takeaways

1. **Two Systems, Two User Groups:**
   - Legacy MANA = Staff/Facilitators = Unrestricted access
   - Sequential Workshops = Participants = Tightly controlled, sequential access

2. **Participants CANNOT Access:**
   - `/mana/regional/` (legacy MANA)
   - `/mana/provincial/` (legacy MANA)
   - Other participants' data
   - Workshops they haven't unlocked yet

3. **Participants CAN Access:**
   - Their own participant dashboard
   - Unlocked workshops (current + all completed)
   - Profile and logout pages

4. **Staff/Facilitators CAN Access:**
   - Everything participants can access
   - Legacy MANA system
   - All participant data (via facilitator dashboard)
   - AI synthesis and export tools

5. **Middleware Enforces Isolation:**
   - `ManaParticipantAccessMiddleware` restricts participants
   - `ManaWorkshopContextMiddleware` attaches assessment context
   - View-level decorators double-check permissions

---

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| Sept 30, 2025 | Removed `/mana/regional/` from participant allowed paths | Ensure participants cannot access legacy staff system |
| Sept 30, 2025 | Added staff check to `mana_regional_overview` view | Double protection for staff-only area |
| Sept 30, 2025 | Created this documentation | Clarify two-system architecture |

---

*For questions or clarifications, contact the OBCMS development team or OOBC MANA coordinator.*