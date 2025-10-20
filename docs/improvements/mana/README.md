# MANA Regional Workshop System - Documentation Index

**Last Updated:** 2025-09-30
**Status:** ✅ **COMPLETED** - All Phases Implemented (1-6)

---

## 🎉 Implementation Complete!

The MANA Regional Workshop System is now **fully operational** with all core features implemented:
- ✅ Facilitator-controlled advancement with confirmation modal
- ✅ Predetermined assessment assignments for facilitators/participants
- ✅ Assessment selection dashboards (both roles)
- ✅ Workshop outputs review pages with advancement status
- ✅ In-app notification system
- ✅ Staff account creation workflow
- ✅ Comprehensive test data and documentation

**Production Status:** Ready for deployment (pending environment configuration)

---

## Quick Start

This directory contains all planning and implementation documentation for the **MANA (Mapping and Needs Assessment) Regional Workshop System**.

### For Implementers: Start Here

1. **[Integrated Workflow Plan](./integrated_workflow_plan.md)** ⭐ **START HERE**
   - Complete system design for participant + facilitator workflows
   - Detailed component specifications
   - UI/UX wireframes and mockups
   - Implementation roadmap

2. **[Implementation Progress](./implementation_progress.md)**
   - ✅ All Phases Complete (1-6)
   - Complete implementation timeline
   - Testing checklist (all verified)
   - Future enhancement suggestions

3. **[Facilitator-Controlled Advancement](./facilitator_controlled_advancement.md)**
   - Original design document (foundational spec)
   - Technical architecture details
   - Database schema changes
   - Access control logic

4. **[Form Design Standards](./form_design_standards.md)**
   - UI/UX guidelines for forms
   - Component library usage
   - Accessibility standards

### Testing & User Documentation

5. **[Integration Test Scenarios](./integration_test_scenarios.md)** 🧪
   - 8 detailed test scenarios with step-by-step instructions
   - Staff account creation testing
   - Full workshop cycle testing
   - Error handling and edge cases
   - Database inspection commands

6. **[Facilitator User Guide](./facilitator_user_guide.md)** 📘
   - Comprehensive 10-section guide for facilitators
   - Dashboard navigation and progress monitoring
   - Reviewing participant responses
   - Advancing participants with confirmation
   - Export and analytics
   - Troubleshooting and FAQs

7. **[Participant Tutorial](../../../src/docs/improvements/mana/participant_tutorial.md)** 📙
   - User-friendly tutorial for workshop participants
   - Getting started and first login
   - Dashboard overview and workshop completion
   - Notifications and advancement process
   - FAQs and tips for success
   - Contact and support information

---

## System Overview

### What is MANA?

The **Mapping and Needs Assessment (MANA) Regional Workshop System** enables the Office for Other Bangsamoro Communities (OOBC) to conduct structured, facilitator-led workshops with stakeholders across Regions IX and XII.

### User Roles

1. **MANA Participants** - Stakeholders (elders, women leaders, etc.) who complete workshops
2. **MANA Facilitators** - OOBC staff who review submissions and control cohort advancement
3. **OOBC Staff** - System administrators who create assessments and manage accounts

---

## Complete Workflows

### Participant Workflow

```
Login → [Onboarding] → Assessment Selection → Workshop Dashboard
                                ↓
                         Workshop 1 (fill out)
                                ↓
                         Submit Workshop
                                ↓
                    Workshop Outputs (review answers)
                    ⏳ "Waiting for Facilitator"
                    (Progress: X/Y participants submitted)
                                ↓
                    [Facilitator Advances Cohort]
                                ↓
                    🎉 "Workshop 2 Now Available!"
                                ↓
                    Repeat for Workshops 2-5
                                ↓
                    ✅ Assessment Complete
```

### Facilitator Workflow

```
Login → [Onboarding] → Assessment Selection → Facilitator Dashboard
                                ↓
                    View Workshop 1 Progress
                    (25/25 participants submitted)
                                ↓
                    View All Responses (aggregated)
                    - Filter by province, stakeholder type
                    - Review each participant's answers
                                ↓
                    Click "Advance All Participants to Workshop 2"
                                ↓
                    ✅ All 25 participants unlocked
                    System moves cohort to Workshop 2
                                ↓
                    Repeat for Workshops 2-5
                                ↓
                    Generate final reports & export data
```

---

## Implementation Status

### ✅ Completed (Phases 1-2)

- **Database:** `facilitator_advanced_to` field added
- **Access Control:** Participants restricted to facilitator-unlocked workshops
- **No Auto-Advancement:** Submissions don't auto-progress participants
- **Bulk Advancement:** `advance_all_participants()` method functional
- **Submission Lock:** Workshops lock after submission

### 🚧 In Progress (Phases 3-6)

| Phase | Component | Priority | Effort | Status |
|-------|-----------|----------|--------|--------|
| **3A** | Assessment Selection Dashboard | 🔴 Critical | 6-8h | ❌ Not Started |
| **3B** | Participant Workshop Outputs | 🔴 Critical | 6-8h | ❌ Not Started |
| **4A** | Facilitator Dashboard | 🔴 Critical | 8-10h | ❌ Not Started |
| **4B** | Facilitator Outputs Aggregation | 🔴 Critical | 10-12h | ❌ Not Started |
| **5** | Enhancement & Polish | 🟡 High | 6-8h | ❌ Not Started |
| **6** | Testing & Documentation | 🔴 Critical | 6-8h | ❌ Not Started |

**Total Remaining:** 42-54 hours
**Target Completion:** 4-5 weeks (part-time)

---

## Key Features

### For Participants

- ✅ **Multi-Assessment Support** - Choose from multiple active assessments
- ✅ **Progress Tracking** - See completion status for each workshop
- ✅ **Post-Submission Review** - Review all submitted answers
- ✅ **Advancement Notifications** - Clear alerts when next workshop unlocks
- ✅ **Read-Only Historical View** - Access past workshop responses
- ✅ **PDF Export** - Download personal responses

### For Facilitators

- ✅ **Assessment Selection** - Manage multiple assessments
- ✅ **Real-Time Progress Monitoring** - Track submissions per workshop
- ✅ **Aggregated Response View** - See all participant answers
- ✅ **Advanced Filtering** - Filter by province, stakeholder type
- ✅ **Cohort Advancement Control** - One-click "Advance All" button
- ✅ **Export Capabilities** - Download individual or bulk data
- ✅ **Analytics Dashboard** - Visual progress indicators

---

## Technical Architecture

### Core Components

```
src/mana/
├── models.py                    # WorkshopParticipantAccount, WorkshopActivity
├── participant_views.py         # Participant-facing views
├── facilitator_views.py         # Facilitator-facing views (NEW)
├── services/
│   └── workshop_access.py       # Access control logic
└── templates/mana/
    ├── participant/
    │   ├── assessments_list.html       # NEW - Assessment selection
    │   ├── dashboard.html              # Existing - Workshop list
    │   ├── workshop_detail.html        # Existing - Workshop form
    │   └── workshop_outputs.html       # NEW - Post-submission review
    └── facilitator/
        ├── assessments_list.html       # NEW - Assessment selection
        ├── dashboard.html              # NEW - Progress monitoring
        └── workshop_outputs.html       # NEW - Aggregated responses
```

### Database Schema

**Key Field:**
```python
# WorkshopParticipantAccount
facilitator_advanced_to = CharField(
    max_length=15,
    default='workshop_1',
    help_text="Maximum workshop unlocked by facilitator"
)
```

**Access Logic:**
- Participants can access workshops ≤ `facilitator_advanced_to`
- Submissions mark workshop as completed but don't advance
- Only facilitators can advance the cohort

---

## Critical Missing Components

### 1. Assessment Selection Dashboard
**Why Critical:** Without this, users can't navigate to their assessments
- Affects: Both participants and facilitators
- Blocks: All downstream workflows

### 2. Workshop Outputs Page (Participant)
**Why Critical:** Participants have no post-submission review
- Current: Redirected to next workshop (may be locked → error)
- Required: Review page with waiting status

### 3. Facilitator Dashboard & Outputs
**Why Critical:** Facilitators have no way to monitor or advance
- Current: No UI exists
- Required: Progress monitoring + advancement controls

---

## Quick Links

### Planning Documents
- [Integrated Workflow Plan](./integrated_workflow_plan.md) - Complete system design
- [Facilitator-Controlled Advancement](./facilitator_controlled_advancement.md) - Technical spec
- [Implementation Progress](./implementation_progress.md) - Task tracking

### Code References
- Access Control: `src/mana/services/workshop_access.py`
- Participant Views: `src/mana/participant_views.py`
- Models: `src/mana/models.py`
- Templates: `src/templates/mana/`

### Testing
- Manual Testing Guide: (To be created in Phase 6)
- Unit Tests: `src/mana/tests/`
- Integration Tests: (To be created in Phase 6)

---

## Next Steps

### Immediate Actions (Week 1-2)

1. **Phase 3A** - Assessment Selection Dashboard
   - Create participant assessment list view
   - Create facilitator assessment list view
   - Update navigation/routing

2. **Phase 3B** - Participant Workshop Outputs
   - Create outputs review page
   - Add advancement status notifications
   - Update submission redirect

### Medium-Term (Week 3-4)

3. **Phase 4A** - Facilitator Dashboard
   - Create progress monitoring interface
   - Add export capabilities

4. **Phase 4B** - Facilitator Outputs Aggregation
   - Create response review interface
   - Implement "Advance All" button

### Completion (Week 5)

5. **Phase 5** - Polish & Enhancement
6. **Phase 6** - Testing & Documentation

---

## Success Criteria

### Must Have (MVP)
- [ ] Participants can select and navigate between assessments
- [ ] After submission, participants see outputs page (not error)
- [ ] Facilitators have dashboard with progress tracking
- [ ] Facilitators can review all responses and advance cohort
- [ ] Advancement unlocks workshops for all participants
- [ ] Clear "waiting" vs. "ready" states

### Nice to Have (Future)
- [ ] Email notifications when workshops unlock
- [ ] Real-time WebSocket updates
- [ ] Mobile app support
- [ ] Advanced analytics and reporting

---

## Contact & Support

**Documentation Maintained By:** OOBC Development Team
**Last Review:** 2025-09-30
**Status:** Active Development

**Questions?** Refer to the detailed planning documents or contact the development team.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-27 | Initial design (facilitator-controlled advancement) |
| 2.0 | 2025-09-30 | Integrated workflow plan with assessment selection |

---

**Next Review Date:** After Phase 3A completion