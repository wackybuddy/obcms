# Planning & Budgeting Module Improvements

## Overview
The planning and budgeting dashboard at `common/oobc_planning_budgeting.html` currently aggregates data from `MonitoringEntry` records to display basic totals, status counts, high-value allocations, and upcoming milestones. While useful, the view (`src/common/views/management.py:498`) lacks the depth required to support the Office for Other Bangsamoro Communities (OOBC) in running a government-grade planning and public financial management (PFM) cycle. This document outlines enhancements that align the module with Philippine government planning and budgeting practices while preserving OOBC's evidence-based, community-first mandate.

## Objectives
- Align obcMS planning workflows with national and BARMM budgeting cycles and compliance requirements.
- Close the gap between community needs assessments (MANA) and resource programming decisions.
- Provide richer analytics, traceability, and collaboration features for planners, coordinators, and decision makers.
- Improve transparency and accountability through tagging, performance tracking, and standardized outputs.

## Current Limitations
- **Insufficient metadata**: `MonitoringEntry` lacks granular fields (e.g., appropriation class, funding source, fiscal year) required for Philippine budget forms.
- **Thin workflow support**: No encoded stages for budget formulation, hearings, legislative approval, or execution monitoring.
- **Weak needs linkage**: MANA findings and community priorities are not tightly connected to PPA proposals.
- **Limited analytics**: Dashboard focuses on totals without ceilings, variance tracking, or compliance tagging.
- **Collaboration gaps**: No shared workspace for forms, comments, approvals, or submission packages.

## Proposed Enhancements
### 1. Data Model Enrichment
- Extend `MonitoringEntry` (and related serializers/forms) with plan year, sector, appropriation class (PS/MOOE/CO), funding type (GAA, BARMM block grant, LGU counterpart, donor), DBM/BARMM program codes, and goal alignment tags (PDP, OPIF, Moral Governance).
- Allow multiple funding tranches per PPA (sub-model for allocations, obligations, disbursements) to track execution detail.
- Add compliance flags for Gender and Development (GAD), Climate Change Expenditure Tagging (CCET), Indigenous Peoples, and Peace/SDG commitments.

### 2. Workflow & Approvals
- Model the Philippine budget cycle stages: Budget Call → Formulation → Technical Budget Hearing → Budget Legislation → Program Execution → Accountability.
- Capture stage owners (OOBC planning team, BARMM MOF, DBM, LGUs) and deadlines with automated reminders and escalations.
- Log approval history, remarks, and uploaded documents (budget call memoranda, AIP submissions, MOA drafts).

### 3. Needs-to-Budget Integration
- Link each PPA to source evidence: MANA assessments, consultations, or monitoring findings with severity scores, beneficiary profiles, and geographic coverage.
- Provide prioritization matrices (urgency, impact, feasibility, equity) to transparently rank proposals.
- Surface gaps where high-priority needs lack corresponding budget entries.

### 4. Analytics & Scenario Planning
- Introduce ceiling management per funding source and multi-year obligation schedule.
- Track obligation and disbursement rates, variance vs. targets, and forecast slippages.
- Offer scenario tools to rebalance allocations, simulate funding mixes, and export AIP Form 2/AIP Summary tables.
- Auto-generate accountability scorecards combining financial and physical progress.

### 5. Compliance & Cross-Cutting Views
- Embed CCET and GAD tagging checklists plus summary dashboards to meet national submission standards.
- Align indicators with Results-Based Monitoring & Evaluation (RBME) and OPIF outputs, highlighting KPI contributions.
- Provide reports for SDG tracking, Moral Governance commitments, and BARMM strategic agenda alignment.

### 6. Collaboration & Reporting Tools
- Enable inline commenting, task assignments, and versioned adjustments per PPA.
- Maintain a document vault for budget call circulars, annexes, and submission receipts.
- Support exports (Excel/CSV/PDF) formatted for DBM, BARMM MOF, and LGU partners.
- Integrate audit logs for transparency.

## Implementation Approach
1. **Discovery & Validation**
   - Interview OOBC planning/budget staff, BARMM MOF counterparts, and LGU focal persons to confirm specific forms, timelines, and approval hierarchies.
   - Catalogue current data sources (MANA, Monitoring, Coordination) and identify required joins.
2. **Design**
   - Update data dictionary and ERD; draft API contracts and UI wireframes (dashboard, form wizard, analytics tabs).
   - Define role-based access matrix for each budget stage.
3. **Development**
   - Add migrations for new fields/models; extend forms, serializers, and view logic.
   - Build DRF endpoints for workflow updates and reporting datasets.
   - Implement front-end components for stage tracking, tagging, and analytics.
4. **Testing & Quality**
   - Create fixtures covering multiple budget years and funding sources.
   - Author pytest suites for model validations, workflow transitions, and export formatting.
   - Run accessibility and performance checks on dashboards.
5. **Rollout**
   - Conduct user acceptance sessions; refine based on feedback.
   - Update admin/training manuals in `docs/` and provide quick reference guides.
   - Plan phased deployment starting with data enrichment, followed by workflow automation, then analytics.

## Dependencies & Risks
- Accurate historical data and ceiling figures from MOF/DBM are needed to validate analytics.
- Additional storage and compute may be necessary for expanded datasets and reporting.
- Change management is critical; planners need training on new workflows and tagging requirements.
- Integration with external systems (BTMS, LGU systems) may require APIs or manual import workflows.

## Success Metrics
- 100% of PPAs tagged with complete metadata and compliance flags.
- Time-to-compile annual investment plan reduced vs. baseline.
- Budget ceilings, obligations, and disbursements balanced within ±5% variance.
- Documented audit trail for all approvals and adjustments.
- Positive user feedback from OOBC planners and partner ministries on usability and reporting accuracy.

## References
- `docs/obcMS-summary.md`
- `docs/OBC_briefer.md`
- `docs/OOBC_integrative_report.md`
- DBM National Budget Memoranda (latest cycle)
- Philippine Public Financial Management Reform Roadmap
- BARMM Ministry of Finance budget call guidelines
