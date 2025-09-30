# Staff Profile Tabs Implementation Plan

## Overview
The current staff profile detail page (`src/templates/common/staff_profile_detail.html`) presents all information as a long, single-column layout. While comprehensive, the experience is difficult to scan and makes it harder for managers to switch between identity, job design, competency, performance, and task information. This plan introduces a tabbed experience that groups related insights, improves navigation, and sets up the page for richer analytics and future integrations.

## Objectives
- Provide a tabbed structure that surfaces the most relevant staff information without scrolling through the entire page.
- Organise backend queries and template partials so each tab renders efficiently and supports empty states.
- Standardise navigation patterns (URL parameters, breadcrumbs, calls to action) for staff-focused workflows.
- Maintain accessibility, responsive behaviour, and existing edit/delete flows throughout the redesign.

## Current Limitations
- **Linear layout**: All sections appear sequentially, leading to long pages and repeated scrolling.
- **Mixed context**: Job description, competencies, performance data, and tasks are intermingled without clear separation.
- **Limited discoverability**: There is no way to deep-link to specific sections or preserve user context after editing.
- **Performance considerations**: The view loads every related dataset up front, even when a user only needs one segment.

## Proposed Enhancements
### 1. Tabbed Information Architecture
- Add a tab navigation component (responsive, accessible) housed under `src/templates/components/` for reuse.
- Split the existing detail page into partials (e.g., `_overview.html`, `_job_description.html`, `_competency.html`, `_performance.html`, `_tasks.html`) that plug into the tab container.
- Default to the Overview tab, with the ability to activate others via query parameter (`?tab=`) or anchor state.

### 2. Target Tab Content
- **Overview**: Identity header, employment badges, key details, team memberships, job summary highlights, qualification snippets, development plan status.
- **Job Descriptions**: Full job purpose, key result areas, major functions, deliverables, supervision lines, and cross-functional partners with edit CTA.
- **Competency Framework**: Core, leadership, and functional competencies, proficiency levels, linked trainings, and competency notes.
- **Performance Dashboard**: Targets, KPIs, recent evaluations, score summaries, and performance history trends.
- **Tasks Assigned**: Active and recently completed tasks for the staff member with quick links to the task board and creation actions.

### 3. View & Data Layer Updates
- Update `common.views.management.staff_profile_detail` to accept a validated `tab` parameter and compute `active_tab` for the template.
- Optimise queryset usage: prefetch only the data required per tab; consider lazy-loading or AJAX for heavier content (e.g., performance analytics).
- Normalise shared context objects (e.g., job description JSON fields) for consistent rendering across partials.

### 4. Frontend Behaviour & Accessibility
- Ensure tabs follow WAI-ARIA practices (`role="tablist"`, `role="tab"`, keyboard navigation).
- Sync tab changes with URL updates so deep links and back-button behaviour work reliably.
- Provide graceful fallbacks for environments without JavaScript; tabs should still be navigable via full-page reloads.

### 5. Supporting Documentation & Training
- Update admin and staff management guides in `docs/` with screenshots and navigation tips.
- Communicate upcoming UI changes to stakeholders before rollout and collect feedback during UAT.

## Implementation Approach
1. **Discovery & Design**
   - Catalogue existing template sections and confirm data ownership for competencies, performance metrics, and tasks.
   - Produce quick wireframes for the tab layout (desktop and mobile) referencing OOBC design tokens.
2. **Backend & Template Refactor**
   - Extract reusable partials, introduce tab navigation component, and adjust the detail view to handle tab context.
   - Add helper methods or services to aggregate performance and competency data efficiently.
3. **Frontend Interactions**
   - Implement tab switching (with history state updates if JavaScript is available) and responsive tweaks for smaller screens.
   - Verify that edit/delete actions, modals, and CTA links retain or reset the tab state appropriately.
4. **Testing & Quality Assurance**
   - Write pytest view tests validating tab parameter handling and template rendering for each tab.
   - Execute manual QA on major browsers and breakpoints; run accessibility checks to confirm focus order and ARIA attributes.
   - Monitor template performance during load testing, ensuring no unnecessary queries execute per tab.
5. **Rollout & Follow-up**
   - Optionally gate the tabbed layout behind a feature flag for staged release.
   - Capture user feedback post-launch and iterate on content or ordering as needed.

## Dependencies & Risks
- Accuracy and availability of performance and competency datasets must be confirmed; gaps require clear empty states.
- Task and performance queries may introduce heavier database load; caching or pagination strategies might be necessary.
- Coordination with other teams (e.g., training/development owners) ensures data definitions stay consistent across modules.
- UI updates may require new translations or copy review if localisation is planned.

## Success Metrics
- Staff detail pages render within acceptable performance thresholds (<1.5s server render for default tab).
- At least 90% of user feedback indicates improved navigation and clarity post-launch.
- Support team reports fewer tickets about locating job descriptions, competencies, or tasks.
- Automated tests cover tab selection routes and pass consistently in CI.

## References
- `docs/improvements/staff_management_module_improvements.md`
- `docs/admin-interface-guide.md`
- `src/common/views/management.py`
- `src/templates/common/staff_profile_detail.html`
