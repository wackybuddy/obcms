# Regional MANA Workshop Redesign Plan

## Overview
The Regional MANA (Mapping and Needs Assessment) workshops currently run on manual coordination and lightly structured JSON notes captured through `WorkshopActivity` records. Participants submit insights via facilitators, limiting traceability, delaying synthesis across provinces IX and XII, and preventing instant UI updates promised in `docs/improvements/instant_ui_improvements_plan.md`. This plan outlines a sequential, participant-authenticated workflow inside OBCMS that links assessments, structured inputs, and AI-assisted consolidation while honouring Barangay OBC interface standards.

## Objectives
- Deliver authenticated participant access with province-aware permissions for every regional assessment.
- Enforce sequential workshop unlocks, optimistic UI updates, and audit logs for each critical action.
- Capture workshop data in normalized tables that support filtering, exports, and AI summarization.
- Provide facilitators with HTMX-ready dashboards for synthesis triggers, status checks, and report pulls.

## Scope
- **In scope:** Participant account onboarding, access management, structured forms for five workshops, HTMX-driven progression, aggregation dashboards, AI synthesis pipeline, exports, documentation.
- **Out of scope:** Mobile offline apps, GIS visualisation, multi-language delivery, real-time co-editing, and integration with external government systems.

## Current Limitations
- **Unverified identities:** `WorkshopParticipant` objects store demographics but are not linked to Django users or permissions.
- **No sequential gating:** All workshops sit behind the same templates, so facilitators must police progression manually.
- **Unstructured capture:** Outputs live as ad-hoc JSON blobs, blocking province/stakeholder filtering and analytics.
- **Manual synthesis:** Facilitators aggregate findings offline; there is no AI workflow or audit trail.
- **Fragile exports:** Existing exports are ad-hoc and do not reflect the question catalogue.

## Proposed Enhancements
### 1. Participant Identity & Access Control
- Introduce `WorkshopParticipantAccount` (one-to-one with `User`, scoped to `Assessment`) holding stakeholder type, geography, and completion state.
- Seed user groups (`mana_regional_participant`, `mana_facilitator`, `mana_admin`) plus model-level permissions (`can_access_regional_mana`, `can_view_provincial_obc`).
- Build facilitator-driven onboarding: CSV import, temporary credentials, consent capture, and profile completion UI with `_apply_form_field_styles` helpers.
- Record every view/submit event through `WorkshopAccessLog` and expose activity summaries to admins.

### 2. Sequenced Workshop Experience
- Implement `WorkshopAccessManager` service to enforce allowed workshop types and bulk progression; log triggers to Celery for notifications.
- Refresh navigation tabs via HTMX (`hx-get` + `hx-swap="outerHTML swap:300ms"`) so locked states update instantly, showing badges for completion.
- Provide facilitator controls (`Advance All`, `Reset Participant`) with optimistic UI updates and toast feedback via HX triggers.
- Store schedule metadata per workshop to support optional time-based auto-unlocks and email nudges.

### 3. Structured Data Capture & Validation
- Replace JSON outputs with `WorkshopResponse` rows keyed by question ID, participant, and workshop; include draft/final states.
- Maintain question catalogues per workshop (e.g., `WORKSHOP_1_QUESTIONS`) describing field types, repeater definitions, and validation rules.
- Generate forms dynamically using a `WorkshopResponseForm` builder that binds Tailwind-ready partials (`components/form_field_*.html`) and supports autosave drafts.
- Add management commands to seed question definitions from `workshop_questions_schema.json` and version them for future revisions.

### 4. Output Review, AI Synthesis, and Reporting
- Ship `WorkshopOutputAggregationView` with province/stakeholder filters, participant counts, and `components/data_table_card.html` for consistent layout.
- Enable exports (XLSX via `openpyxl`, CSV, PDF via `reportlab`) respecting filters and question groupings.
- Create `WorkshopSynthesis` model plus `AIWorkshopSynthesizer` service that queues Celery tasks, stores prompt/response metadata, and supports review, regeneration, and approval notes.
- Emit HX triggers (`task-updated`, `show-toast`, `refresh-counters`) so facilitator dashboards refresh without full reloads; log synthesis invocations for audit.

## Stakeholders & Ownership
- Product: OOBC Planning & Coordination lead (owner of assessment workflows).
- Engineering: Mana module feature team lead (backend) + shared frontend engineer for HTMX/templating.
- Data & AI: AI assistant integration owner for LLM configuration and usage monitoring.
- QA: Central QA analyst responsible for pytest coverage and UAT sign-off.
- Change Management: Regional coordinators delivering participant onboarding and training.

## Implementation Approach
1. **Discovery & Alignment** – Confirm assessment calendar, stakeholder roster, and data privacy requirements; review current `mana` models and templates.
2. **Identity & Access Build** – Add new models/migrations, seed groups/permissions, implement registration flows, and wire consent logging.
3. **Sequential Workflow Delivery** – Implement `WorkshopAccessManager`, facilitator controls, and HTMX navigation/UI updates; add Celery hooks for notifications.
4. **Structured Forms & Storage** – Define question schemas, build dynamic forms with autosave, migrate existing JSON data where feasible, and add validation tests.
5. **Output Dashboards & Exports** – Develop aggregation views, filtering, and export endpoints; secure with permissions and audit logging.
6. **AI Synthesis Enablement** – Integrate LLM providers, build synthesis queue/UX, enforce rate limits, and provide manual override tools.
7. **Testing & Rollout** – Write pytest suites, run accessibility/performance checks, conduct pilot with one regional cohort, document processes, and prepare training collateral.

## Dependencies & Risks
- Reliable participant rosters and contact details are needed for account provisioning; delays block onboarding.
- LLM providers (OpenAI/Anthropic) require stable credentials and budget monitoring; outages need fallbacks.
- Celery + Redis infrastructure must be available for autosave and AI queues; otherwise synthesis falls back to synchronous mode.
- Migrating existing JSON outputs may require manual cleaning; missing mappings could cause data gaps.
- Strict consent and privacy handling is mandatory; misconfiguration risks compliance breaches.

## Success Metrics
- ≥90% of invited participants complete onboarding before Workshop 1 starts.
- ≥85% of participants submit responses for each workshop on schedule.
- Facilitator review time per workshop reduced by ≥40% thanks to aggregation and AI synthesis.
- Export generation succeeds in under 10 seconds for 100 responses; synthesis completes within 30 seconds average.
- Audit logs capture 100% of view/submit/synthesis actions for sampled assessments.

## Open Questions & Next Actions
- Confirm whether barangay-level participants need restricted data views beyond province scope (Product, due 15 Oct).
- Validate retention policy for WorkshopResponses and Syntheses to satisfy data privacy regulations (Legal, due 22 Oct).
- Decide on default LLM provider/model mix and budget caps per assessment cycle (AI owner, due 25 Oct).
- Determine migration strategy for legacy JSON outputs and whether historical workshops need backfill (Engineering, due 29 Oct).

## References
- `src/mana/models.py`
- `src/mana/views.py`
- `docs/improvements/instant_ui_improvements_plan.md`
- `docs/reports/obc-system-requirements.md`
- `docs/improvements/improvement_plan_template.md`
