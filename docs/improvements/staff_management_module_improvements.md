# OOBC Staff Management Module – Simplified Improvement Plan

## Overview
- **Goal**: Refresh `http://localhost:8000/oobc-management/staff/` into a lightweight yet practical workspace tailored to OOBC’s coordinating role.
- **Reference Materials**: Mandate and operational context drawn from `docs/obcMS-summary.md`, `docs/OBC_briefer.md`, and `docs/OOBC_integrative_report.md`.
- **Design Principle**: Mirror familiar patterns from the Barangay OBC list (`http://localhost:8000/communities/manage/`) to minimise training overhead while supporting core staff administration needs.

## Core Submodules

### 1. Staff Profiles (CRUD)
**Purpose**: Maintain an accessible directory with the essentials needed for deployment and competency-based management.
- **Features**
  - List view with filters/search (name, role, status, team) similar to Barangay OBC list tables.
  - Detail view summarising demographics, contact info, position, employment status, and notes.
  - Create/Edit/Delete flows with validation and audit trails.
  - Competency capture split into:
    - *Core*: e.g., Moral Governance, Integrity, Service Orientation.
    - *Leadership*: e.g., Strategic Thinking, Stakeholder Engagement, Team Leadership.
    - *Functional*: e.g., Community Mapping, Policy Analysis, Monitoring & Evaluation.
  - File attachments for basic documents (ID, deployment clearance) if available.
- **Data Considerations**
  - Extend `User` profile to store competency ratings (1–5 scale or achieved/not achieved), employment status, and deployment notes.
  - Align competency taxonomy with CSC/BARMM frameworks; store as reference data for reuse.

### 2. Task Management
**Purpose**: Provide an intuitive board/list for planning and tracking work, inspired by Notion/ClickUp/Monday but scoped to essentials.
- **Features**
  - Kanban-style board with status columns (To Do, In Progress, Blocked, Done).
  - Quick-create modal with title, description, assignee, due date, tags/labels.
  - Inline updates for status, progress, and comments.
  - Task list view with bulk actions (assign, change status) and filters (team, priority, due window).
  - Optional recurring tasks and attachments for reference documents.
- **Data Considerations**
  - Reuse `StaffTask` model; add lightweight fields for tags and simple recurrence.
  - Ensure tasks link to staff profiles and teams for downstream analytics.

### 3. Team Management
**Purpose**: Group staff by function and surface team-level workload snapshots.
- **Features**
  - Team directory (MANA, Planning & Budgeting, Coordination, M&E, etc.) with counts of members and active tasks.
  - CRUD for teams, including mission, focus areas, and lead.
  - Team detail page summarising members, aggregated tasks, and recent updates.
  - Ability to assign/remove members from teams directly within the module.
- **Data Considerations**
  - Build on `StaffTeam` and `StaffTeamMembership`; ensure membership history tracked for audit.
  - Support staff belonging to multiple teams when cross-functional deployment is required.

### 4. Performance Management
**Purpose**: Offer clear dashboards for individual and team performance targets, standards, and results.
- **Features**
  - Personal dashboard: tasks completed vs. assigned, competency status, achievement against predefined targets.
  - Team dashboard: aggregated metrics (completion rate, overdue percentage, workload distribution).
  - Performance target entry: annual/quarterly targets and standards per staff/team.
  - Simple rating capture (self, supervisor) with remarks.
- **Data Considerations**
  - Introduce `PerformanceTarget` and `PerformanceRecord` entities tied to users/teams, periods, and metrics.
  - Define minimal KPI set (e.g., tasks completed on time %, coordination outputs delivered, policy briefs drafted).
  - Support export (CSV/PDF) for submission to leadership.

### 5. Training & Development
**Purpose**: Track learning plans and address competency gaps surfaced by performance dashboards.
- **Features**
  - Individual Development Plan (IDP) form linked to each staff profile with goals, actions, timelines, and responsible mentors.
  - Training catalogue: internal/external courses, seminars, certifications.
  - Assignment of trainings to staff with status (Planned, Ongoing, Completed) and evidence uploads.
  - Gap analysis widget pulling from competencies and performance shortfalls.
- **Data Considerations**
  - Add `TrainingProgram` and `TrainingEnrollment` models; ensure relation to competencies addressed.
  - Provide reminders or simple calendar export for upcoming trainings.

## Implementation Pacing (Suggested)
1. **Foundation Sprint**: Extend models, serializers, and forms for enriched staff profiles and CRUD interfaces.
2. **Task & Team Experience**: Refresh task UI to Kanban/list views and integrate team aggregation panels.
3. **Performance Dashboards**: Define KPI schema, implement metric calculations, and build charts for individuals/teams.
4. **Learning Tracker**: Launch training catalogue and IDP forms, integrating gap analysis from performance data.
5. **Polish & Adoption**: Add exports, permissions polish, user help text, and run user acceptance sessions with OOBC leads.

## Immediate Next Steps
- Confirm competency taxonomy and performance KPIs with OOBC leadership.
- Draft user stories for each submodule, starting with staff profile CRUD pages.
- Prepare wireframes mirroring the Barangay list layout to guide UI work.
