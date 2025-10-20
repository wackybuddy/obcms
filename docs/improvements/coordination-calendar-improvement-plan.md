# OOBC Calendar Management Improvement Plan

## Overview
The existing calendar view lives in the coordination stack (`src/templates/coordination/calendar.html`, `src/coordination/views.py:488`) and primarily serves coordination events and stakeholder engagements. OOBC leadership, however, requires a shared scheduling and follow-up workspace covering consultation, coordination, MANA field work, policy tracking, and internal administration. This plan outlines the work to relocate and expand the calendar under the OOBC Management module (`/oobc-management/` via `src/common/urls.py`) and to equip it for organization-wide use while honoring mandates in `docs/obcMS-summary.md`, `docs/OBC_briefer.md`, and `docs/OOBC_integrative_report.md`.

## Current Implementation Status
- Phase 1 delivered: centralized view at `src/templates/common/oobc_calendar.html` served by `src/common/views/management.py:oobc_calendar`, aggregated payload builder in `src/common/services/calendar.py`, module filters, upcoming highlights, and conflict hints. Navigation now points `/oobc-management/calendar/` to the new workspace.
- Phase 2 extends the shared payload with workflow-driven lifecycle actions (approvals, escalations, follow-ups) stitched across coordination events, partnerships, milestones, planning stages, policies, staff tasks, and MANA baselines, enabling compliance tracking per OOBC function.
- Analytics card now renders module heatmaps, status tallies, workflow summaries, and a compliance snapshot that spotlights overdue actions and pending approvals per module; JSON/ICS feeds expose the same telemetry for downstream tooling.
- Outstanding work: cross-module task hand-offs, advanced briefing packs (PDF/email), and deeper automation for document packages remain in scope for subsequent phases.

## Objectives
- Stand up a central calendar experience under OOBC Management that aggregates schedules across coordination, MANA, policy, planning, and staff operations.
- Align workflows with Philippine government practices (approvals, statutory deadlines, audit trails) applicable to all OOBC functions.
- Surface cross-module context (communities, agencies, assessments, policy items) directly in calendar records and exports.
- Provide interoperable outputs (REST, ICS, printable briefs) for BARMM ministries, NGAs, LGUs, and partner organizations.
- Enable leadership analytics that highlight risks, bottlenecks, and follow-through rates across the OOBC portfolio.

## Current Limitations
- **Module silo:** Calendar assets sit inside the coordination app, preventing other OOBC teams from contributing or consuming schedules without duplicating logic.
- **Restricted metadata:** Events and engagements expose coordination-specific fields; there is no taxonomy for planning cycles, staff tasks, assessments, or policy checkpoints.
- **Workflow gaps:** Approval, logistics, and post-activity follow-up steps differ per OOBC function yet are not modeled, limiting compliance with BARMM/NGA norms (e.g., RA 11032 service levels, DBM budget timelines).
- **Integration weakness:** Calendar entries lack links to coordination requests, MANA assessments, policy recommendations, staff tasks, or monitoring entries, breaking the consultation → coordination → policy chain.
- **Limited reporting:** No organization-wide dashboards, conflict detection, or export tooling suitable for executive briefings and partner coordination.

## Proposed Enhancements
### 1. Unified Data & Metadata Layer
- Introduce shared dictionaries covering BARMM ministries, NGAs/LGUs, OBC regions, sector focus areas, funding sources, program identifiers, and OOBC internal teams.
- Extend event models (or add a consolidated calendar model) with module tags, lifecycle state, statutory deadlines, RA 11032 turnaround targets, DBM/BARMM budget milestones, gender/culture flags, and follow-up commitment tracking.
- Implement validation and archival routines to enforce completeness, prevent stale statuses, and maintain audit-ready records.

### 2. OOBC Management Calendar Experience
- Create a dedicated template (e.g., `src/templates/common/oobc_calendar.html`) and view (`src/common/views/management.py`) presented from `/oobc-management/calendar/` with FullCalendar components, view toggles, quick filters, and saved presets.
- Store color palettes and labeling in configuration tables so each module (coordination, MANA, policy, planning, staff) can be represented consistently without code edits.
- Provide conflict detection for shared facilitators, venues, or resources and highlight overlaps with critical deadlines or field deployments.
- Support document bundles (agenda, travel orders, minutes, evaluation forms) with version history and access logging.

### 3. Cross-Module Workflow Integration
- Link calendar items to their source modules: coordination requests, stakeholder engagements, MANA assessments, policy recommendations, planning/budgeting PPAs, staff tasks, and monitoring entries.
- Allow module-specific lifecycle actions (e.g., pre-departure checklists for MANA, policy endorsement checkpoints) while retaining a unified status vocabulary for executive oversight.
- Auto-create follow-up tasks and alerts when commitments are logged; emit structured signals to the AI assistant for proactive reminders and summary briefs.

### 4. Interoperability & Transparency
- Publish authenticated REST endpoints and ICS feeds with filter parameters, respecting community data sovereignty and access controls per user roles.
- Generate printable/email-ready briefing packs summarizing objectives, stakeholders, agenda, commitments, compliance milestones, and documents for each event.
- Maintain audit logs for edits, approvals, and external shares, aligning with OOBC moral-governance expectations.

### 5. Analytics & Oversight
- Build dashboards (within OOBC Management) that roll up activity by module, ministry, LGU tier, region, sector, and compliance status (pending endorsements, lapsed commitments, overdue reports).
- Track RA 11032 compliance, DBM budget-call milestones, field deployment coverage, and closure rates on commitments sourced from consultations and coordination meetings.
- Highlight coverage gaps where critical communities or programs lack scheduled interventions; feed insights to policy and planning teams.

## Implementation Approach
1. **Discovery & Alignment**
   - Convene workshops with coordination, MANA, policy, planning/budgeting, and staff management teams to define taxonomies, lifecycles, and analytics needs.
   - Audit existing `Event` and `StakeholderEngagement` data and inventory other modules’ scheduling artefacts to scope migrations.
2. **Design**
   - Update data dictionary and ERD to accommodate shared calendar metadata; draft API contracts and UX wireframes for the OOBC Management calendar and dashboards.
   - Define role-based access, approval hierarchies, retention policies, and integration touchpoints per module.
3. **Development**
   - Implement migrations or new models, extend serializers/forms, and refactor `calendar_overview` logic into a common service reusable across modules.
   - Build the new OOBC Management calendar view/template and relocate existing coordination calendar routes to the shared subsystem.
   - Deliver REST/ICS endpoints, conflict-detection services, document handling, and analytics queries with caching/aggregation as needed.
4. **Testing & Quality**
   - Author pytest suites covering model validations, workflow transitions, conflict detection, API responses, and permissions.
   - Perform accessibility, usability, and performance checks on the new calendar UI and dashboards across desktop/mobile.
5. **Rollout & Change Management**
   - Pilot the centralized calendar with internal OOBC users and selected partner agencies; iterate based on feedback.
   - Publish SOPs, training materials, and quick-reference guides; schedule refresher sessions for module teams.
   - Establish a governance cadence (e.g., quarterly reviews) to adjust taxonomies, workflows, and analytics as mandates evolve.

## Dependencies & Risks
- Requires coordinated data cleanup and taxonomy mapping across multiple OOBC units; staffing and time commitments must be secured.
- Formal data-sharing agreements with external agencies are needed before enabling APIs or feeds to protect community data sovereignty.
- Model refactors could impact existing coordination forms and tests; careful sequencing and regression coverage are necessary.
- Increased storage and compute demands are likely for document bundles, analytics, and higher user concurrency.

## Success Metrics
- 100% of calendar entries tagged with module, partner, community, status, and compliance metadata.
- Measurable reduction in scheduling conflicts or missed statutory deadlines compared to the baseline quarter.
- Documented follow-up tasks for all commitments, with closure rates reported in OOBC Management dashboards.
- Positive user feedback from coordination, MANA, policy, planning, and staff teams on usability, reporting, and interoperability.

## References
- `docs/obcMS-summary.md`
- `docs/OBC_briefer.md`
- `docs/OOBC_integrative_report.md`
- `src/common/urls.py`
- `src/common/views/management.py`
- `src/coordination/views.py`
- `src/templates/coordination/calendar.html`
