# Regional MANA Workshop Redesign - Implementation Summary

## Overview
Implemented core backend infrastructure for the Regional MANA (Mapping and Needs Assessment) workshop redesign as outlined in `regional_mana_workshop_redesign_plan.md`.

**Date:** 2025-09-30
**Status:** Phase 2 In Progress (Participant UX & Facilitator Operations)

## What Was Implemented

### 1. Database Models (mana/models.py)

#### WorkshopParticipantAccount
Authenticated participant accounts for regional MANA workshops with:
- One-to-one relationship with Django User
- Stakeholder type classification (15 types: elders, women leaders, youth, farmers, etc.)
- Geographic scope (province, municipality, barangay)
- Workshop completion tracking (`completed_workshops`, `current_workshop`)
- Onboarding state (consent, profile completion)
- Custom permissions: `can_access_regional_mana`, `can_view_provincial_obc`

**Key Features:**
- Tracks which workshops participant has completed
- Sequential unlock mechanism via `completed_workshops` JSONField
- Province-aware for data filtering

#### WorkshopResponse
Structured responses to workshop questions:
- Links participant to workshop and specific question ID
- Stores response data as JSON (flexible schema)
- Status tracking: draft → submitted → validated
- Timestamp tracking for submissions

**Key Features:**
- Unique constraint on (participant, workshop, question_id)
- Supports autosave with draft status
- Database indexes for efficient filtering

#### WorkshopAccessLog
Audit trail for all workshop actions:
- Action types: view, submit, update, unlock, complete
- Metadata field for IP address, user agent, etc.
- Timestamp-based ordering

**Key Features:**
- Immutable audit log
- Indexed for fast queries by participant/workshop
- Supports compliance requirements

#### WorkshopSynthesis
AI-generated synthesis of workshop outputs:
- Configuration: prompt template, filters (province, stakeholder)
- Results: synthesis text, key themes (JSON)
- AI provider metadata: provider, model, tokens, processing time
- Review workflow: queued → processing → completed → reviewed → approved

**Key Features:**
- Supports multiple AI providers (OpenAI, Anthropic, etc.)
- Review and approval workflow
- Error tracking and regeneration support

### 2. Service Layer (mana/services/)

#### WorkshopAccessManager (services/workshop_access.py)
Manages sequential workshop unlocks:
- `get_allowed_workshops(participant)` - Returns accessible workshops
- `is_workshop_accessible(participant, workshop_type)` - Check access
- `unlock_workshop(participant, workshop_type, by_user)` - Manual unlock
- `mark_workshop_complete(participant, workshop_type)` - Complete workshop
- `advance_all_participants(workshop_type, by_user)` - Bulk unlock
- `reset_participant_progress(participant, by_user)` - Reset progress
- `get_progress_summary(participant)` - Progress statistics
- `get_assessment_progress_summary()` - Assessment-wide statistics

**Workshop Sequence:**
```
workshop_1 → workshop_2 → workshop_3 → workshop_4 → workshop_5 → workshop_6
```

**Rules:**
- Workshop 1 always accessible
- Each workshop unlocks after previous is completed
- Facilitators can manually unlock or bulk advance

#### AIWorkshopSynthesizer (services/workshop_synthesis.py)
Generates AI-powered workshop syntheses:
- `synthesize(created_by, provider, custom_prompt)` - Generate synthesis
- `regenerate_synthesis(synthesis, created_by)` - Regenerate existing
- `approve_synthesis(synthesis, reviewed_by, notes)` - Approve synthesis
- `synthesize_workshop_async(workshop_id, filters, user_id)` - Celery task

**Features:**
- Default prompt template for MANA context
- Filter by province and stakeholder type
- Response formatting for AI consumption
- Token usage and cost tracking
- Error handling and retry support

**Note:** AI provider integration now supports OpenAI and Anthropic with graceful fallbacks when credentials are absent.

### 3. Workshop Question Schemas (mana/data/workshop_questions_schema.json)

Structured question definitions for all 6 workshops:

**Question Types:**
- `long_text` - Free-form text responses
- `repeater` - Multiple items with sub-fields
- `structured` - Fixed set of labeled fields
- `select` - Dropdown options

**Workshops:**
1. **Workshop 1:** Understanding Community Context (4 questions)
   - Historical background, strengths/resources, stakeholders, demographics
2. **Workshop 2:** Community Aspirations and Priorities (6 questions)
   - Vision, needs by sector (education, economic, social, cultural, infrastructure)
3. **Workshop 3:** Community Collaboration and Empowerment (4 questions)
   - Organizations, collaboration patterns, capacity gaps, strategies
4. **Workshop 4:** Community Feedback on Existing Initiatives (4 questions)
   - Government programs, best practices, implementation challenges, lessons
5. **Workshop 5:** OBCs Needs, Challenges, Factors, and Outcomes (4 questions)
   - Root causes, differential impacts, relationships, outcomes
6. **Workshop 6:** Ways Forward and Action Planning (4 questions)
   - Solutions, stakeholder roles, action plans, support needs

**Total:** 26 structured questions across 6 workshops

## Phase 2 Enhancements (2025-10-01)

### 1. Facilitator & Participant Experience
- HTMX-driven participant navigation with autosave toasts and sequential unlocks that honour workshop schedules.
- Facilitator dashboard now surfaces question summaries via `components/data_table_card.html`, exports, and real-time toasts for actions.
- Participant management card uses the shared data table component with inline progress reset controls (HTMX swap-in updates).

### 2. Access Control & Scheduling
- `WorkshopQuestionDefinition` model plus `sync_mana_question_schema` command store versioned workshop schemas in the database.
- `ensure_mana_roles` command seeds `mana_regional_participant`, `mana_facilitator`, and `mana_admin` groups with the new `can_facilitate_workshop` permission.
- `WorkshopAccessManager` auto-unlocks workshops based on scheduled dates and logs system-driven unlock events.

### 3. Background Tasks & Notifications
- `mana.tasks` exposes Celery-compatible tasks for auto-unlock and AI synthesis generation; falls back to synchronous execution when Celery is absent.
- Facilitator synthesis requests queue asynchronously when `MANA_ASYNC_ENABLED` is true; otherwise they continue inline.
- Global toast handler in `base.html` listens to `show-toast` HX triggers for consistent user feedback.

### 4. Testing & Tooling
- Added `test_management_commands.py` for command coverage and extended participant workflow tests for autosave/submission paths.
- New `mana/management/commands/ensure_mana_roles.py` and `sync_mana_question_schema.py` scripts documented via command help output.

### 4. Admin Interface (mana/admin.py)

Added comprehensive admin interfaces:

#### WorkshopParticipantAccountAdmin
- List view with progress badges, consent status, profile completion
- Filters by stakeholder type, province, consent, profile completion
- Bulk actions: mark consent given, mark profile complete, reset progress
- Color-coded progress bars showing X/6 workshops completed

#### WorkshopResponseAdmin
- List view with participant, workshop, question ID, status
- Filters by status, workshop type, submission date
- Status badges: draft (gray), submitted (blue), validated (green)

#### WorkshopAccessLogAdmin
- Audit log view with participant, workshop, action, timestamp
- Filters by action type and workshop
- Action badges color-coded by type
- Read-only (immutable audit trail)

#### WorkshopSynthesisAdmin
- List view with status, AI provider, tokens used, approval status
- Bulk actions: mark as reviewed, mark as approved, queue for regeneration
- Status badges: queued → processing → completed → reviewed → approved

### 5. Database Migrations

Generated and applied migration: `mana/migrations/0013_workshopparticipantaccount_workshopsynthesis_and_more.py`

**Changes:**
- Created 4 new models
- Added custom permissions
- Created database indexes for performance
- All migrations applied successfully

## Architecture Decisions

### 1. Sequential Workshop Unlocks
- Implemented via `completed_workshops` JSONField tracking
- Allows flexible progression (not time-based)
- Facilitators can override with manual unlocks
- Supports bulk operations for cohort management

### 2. Structured Question Storage
- JSON schema separate from code (data/workshop_questions_schema.json)
- Responses stored as JSON in `WorkshopResponse`
- Allows dynamic form generation
- Version control for question schemas
- Easy to update questions without migrations

### 3. AI Synthesis Architecture
- Async-ready with Celery task placeholder
- Provider-agnostic (supports multiple AI providers)
- Review workflow before approval
- Token usage tracking for cost management
- Regeneration support for failed syntheses

### 4. Audit Logging
- Immutable log with all workshop actions
- Metadata field for extensibility
- Indexed for performance
- Supports compliance and troubleshooting

### 5. Province-Based Access Control
- Participants scoped to specific provinces
- Enables province-level data filtering
- Supports future multi-tenancy if needed
- Custom permissions for data access

## Integration Points

### Existing Models
- Links to `Assessment` (regional assessments)
- Links to `WorkshopActivity` (6 workshop types)
- Links to `Province`, `Municipality`, `Barangay` (geography)
- Links to Django `User` (authentication)

### Services Integration
- `WorkshopAccessManager` used by views for access control
- `AIWorkshopSynthesizer` called by Celery tasks or views
- Both services log actions via `WorkshopAccessLog`

### Admin Integration
- All new models registered in Django admin
- Follows existing admin patterns (badges, links, bulk actions)
- Integrated with existing `WorkshopActivity` admin

## What's NOT Implemented (Phase 2)

The following components from the plan still need implementation:

### 1. Views and Forms
- [ ] Participant onboarding views (registration, consent, profile)
- [ ] Workshop response forms with HTMX autosave
- [ ] Facilitator dashboard with progress tracking
- [ ] Workshop navigation with sequential unlocks
- [ ] Form components using `_apply_form_field_styles`

### 2. Exports
- [ ] XLSX export via openpyxl
- [ ] CSV export
- [ ] PDF export via reportlab
- [ ] Export filtering by province/stakeholder

### 3. AI Integration
- [ ] Actual AI provider implementation (OpenAI/Anthropic)
- [ ] Celery task registration and configuration
- [ ] Redis setup for task queue
- [ ] API key management
- [ ] Rate limiting and budget controls

### 4. HTMX UI Components
- [ ] Instant UI updates with hx-swap
- [ ] Navigation tabs with workshop status badges
- [ ] Optimistic UI for form submissions
- [ ] Out-of-band swaps for counters
- [ ] Toast notifications for user feedback

### 5. Testing
- [ ] Model tests
- [ ] Service layer tests
- [ ] View tests
- [ ] Integration tests
- [ ] Access control tests

### 6. Management Commands
- [ ] Seed question schemas from JSON
- [ ] Bulk import participants from CSV
- [ ] Export workshop responses
- [ ] Generate synthesis reports
- [ ] Reset participant progress

### 7. Documentation
- [ ] API documentation
- [ ] User guide for facilitators
- [ ] Participant onboarding guide
- [ ] Workshop question guide
- [ ] AI synthesis usage guide

## Next Steps

### Immediate (Phase 2a)
1. Create participant onboarding flow (views, forms, templates)
2. Build workshop response forms with dynamic question rendering
3. Implement HTMX for instant UI updates
4. Add management command to seed question schemas

### Short-term (Phase 2b)
1. Build facilitator dashboard with aggregation views
2. Implement export functionality (XLSX, CSV)
3. Create workshop navigation with sequential unlocks
4. Add access control middleware and decorators

### Medium-term (Phase 3)
1. Integrate actual AI provider (Anthropic Claude recommended)
2. Set up Celery + Redis for background tasks
3. Implement synthesis queue and auto-retry logic
4. Add rate limiting and usage monitoring

### Testing & Documentation (Phase 4)
1. Write comprehensive test suite
2. Create facilitator training materials
3. Document API endpoints
4. Prepare pilot deployment guide

## Files Changed

### New Files
- `src/mana/services/__init__.py` - Service layer initialization
- `src/mana/services/workshop_access.py` - Workshop access management
- `src/mana/services/workshop_synthesis.py` - AI synthesis service
- `src/mana/data/workshop_questions_schema.json` - Question definitions
- `src/mana/migrations/0013_workshopparticipantaccount_workshopsynthesis_and_more.py` - Migration

### Modified Files
- `src/mana/models.py` - Added 4 new models (400+ lines)
- `src/mana/admin.py` - Added 4 new admin classes (400+ lines)

### Total Lines Added
- Models: ~400 lines
- Services: ~550 lines
- Admin: ~400 lines
- Question Schema: ~300 lines (JSON)
- **Total: ~1,650 lines of new code**

## Technical Notes

### Performance Considerations
- Database indexes on frequently queried fields
- JSON fields for flexible schema evolution
- Pagination required for large participant lists
- Consider caching for question schemas

### Security Considerations
- Custom permissions enforced at model level
- Audit logging for compliance
- Province-based data isolation
- Consent tracking for data privacy

### Scalability Considerations
- Async synthesis via Celery
- JSON response storage scales well
- Indexes support efficient filtering
- Service layer separates business logic

## Testing Checklist

Before deploying to production:
- [ ] Test participant account creation
- [ ] Test workshop sequential unlocks
- [ ] Test response submission and validation
- [ ] Test access log creation
- [ ] Test synthesis generation (once AI integrated)
- [ ] Test bulk operations performance
- [ ] Test province-based filtering
- [ ] Test admin interface bulk actions
- [ ] Load test with 100+ participants
- [ ] Security audit of permissions

## References

- Original Plan: `docs/improvements/regional_mana_workshop_redesign_plan.md`
- System Requirements: `docs/reports/obc-system-requirements.md`
- Instant UI Plan: `docs/improvements/instant_ui_improvements_plan.md`
- MANA Guidelines: (External OOBC document)

## Contributors

- Implementation: Claude Code (AI Assistant)
- Review: (Pending)
- Approval: (Pending)

## Change Log

- **2025-09-30:** Phase 1 complete - Backend infrastructure implemented
  - Models, services, admin interfaces
  - Database migrations applied
  - Question schemas created
  - Ready for Phase 2 (views and forms)
