# URL Navigation Map - OBCMS

**Complete URL structure for the OBC Management System**

Last Updated: October 1, 2025

---

## Main Application Sections

### 1. Dashboard
**Base URL:** `/dashboard/`

Main landing page with system overview statistics:
- OBC Communities count (Barangay + Municipal)
- MANA Assessments
- Active Partnerships (BMOAs, NGAs, LGUs)
- Policy Recommendations

---

### 2. Communities Management
**Base URL:** `/communities/`

Manage Bangsamoro OBC communities across regions.

**Key Pages:**
- `/communities/` - Communities list and overview
- `/communities/barangay/` - Barangay-level OBCs
- `/communities/municipal/` - Municipal-level OBCs
- `/communities/<id>/` - Community detail pages

---

### 3. MANA (Mapping and Needs Assessment)
**Base URL:** `/mana/`

Community needs assessment and MANA workshop management.

**Key Pages:**
- `/mana/` - MANA overview
- `/mana/facilitator/` - Facilitator dashboard
- `/mana/participant/` - Participant dashboard
- `/mana/workshops/` - Workshop management
- `/mana/needs/` - Community needs tracking

---

### 4. Coordination
**Base URL:** `/coordination/`

Multi-stakeholder coordination and partnership management.

**Key Pages:**
- `/coordination/` - Coordination overview
- `/coordination/partnerships/` - Partnership registry
- `/coordination/maos/` - MAO (Mandated Agency Organizations) management
- `/coordination/meetings/` - Coordination meetings

---

### 5. Policy Recommendations
**Base URL:** `/recommendations/`

Policy tracking and evidence-based recommendations.

**Key Pages:**
- `/recommendations/` - Recommendations overview
- `/recommendations/policies/` - Policy recommendations
- `/recommendations/programs/` - Program recommendations
- `/recommendations/services/` - Service recommendations

---

### 6. Monitoring (PPAs)
**Base URL:** `/monitoring/`

Program, Project, and Activity (PPA) monitoring and tracking.

**Key Pages:**
- `/monitoring/` - Monitoring overview
- `/monitoring/dashboard/` - PPA dashboard
- `/monitoring/ppas/` - PPA list
- `/monitoring/ppa/<id>/` - PPA details

---

## 7. OOBC Management (Planning & Budgeting Hub)
**Base URL:** `/oobc-management/`

**Central hub for all Planning & Budgeting features (Phases 1-8)**

### Phase 1-3: Core Planning & Budgeting

| Feature | URL | Description |
|---------|-----|-------------|
| **Planning Dashboard** | `/oobc-management/planning-budgeting/` | Budget allocation tracking and planning cycles |
| **Gap Analysis** | `/oobc-management/gap-analysis/` | Identify funding gaps and unmet needs |
| **Policy-Budget Matrix** | `/oobc-management/policy-budget-matrix/` | Link policies to budget allocations |
| **MAO Registry** | `/oobc-management/mao-focal-persons/` | Focal persons and contact information |
| **Community Needs Summary** | `/oobc-management/community-needs/` | Aggregated community needs summary |

### Phase 4: Participatory Budgeting

| Feature | URL | Description |
|---------|-----|-------------|
| **Community Voting** | `/community/voting/` | Vote on community priority needs |
| **Voting Results** | `/community/voting/results/` | View community voting analytics |
| **Budget Feedback** | `/oobc-management/budget-feedback/` | Service satisfaction and feedback |
| **Transparency Dashboard** | `/transparency/` | Public budget accountability |

### Phase 5: Strategic Planning

| Feature | URL | Description |
|---------|-----|-------------|
| **Strategic Goals Dashboard** | `/oobc-management/strategic-goals/` | 3-5 year goals and progress tracking |
| **Annual Planning Dashboard** | `/oobc-management/annual-planning/` | Fiscal year planning cycles |
| **RDP Alignment** | `/oobc-management/rdp-alignment/` | Regional Development Plan alignment |

### Phase 6: Scenario Planning & Optimization

| Feature | URL | Description |
|---------|-----|-------------|
| **Budget Scenarios** | `/oobc-management/scenarios/` | Manage what-if budget scenarios |
| **Create Scenario** | `/oobc-management/scenarios/create/` | Build new budget scenario |
| **Scenario Detail** | `/oobc-management/scenarios/<uuid>/` | View scenario allocations |
| **Compare Scenarios** | `/oobc-management/scenarios/compare/` | Side-by-side scenario comparison |
| **Run Optimization** | `/oobc-management/scenarios/<uuid>/optimize/` | Execute optimization algorithm |

### Phase 7: Analytics & Forecasting

| Feature | URL | Description |
|---------|-----|-------------|
| **Analytics Dashboard** | `/oobc-management/analytics/` | Comprehensive insights and metrics |
| **Budget Forecasting** | `/oobc-management/forecasting/` | 3-year budget projections |
| **Trend Analysis** | `/oobc-management/trends/` | Multi-year trend analysis |
| **Impact Assessment** | `/oobc-management/impact/` | Outcomes & effectiveness metrics |

### Organizational Management

| Feature | URL | Description |
|---------|-----|-------------|
| **OOBC Calendar** | `/oobc-management/calendar/` | Organization-wide schedule |
| **Staff Management** | `/oobc-management/staff/` | Team workflows and tasks |
| **User Approvals** | `/oobc-management/approvals/` | Review pending accounts |

---

## Quick Access: Most Important URLs

### For OOBC Staff (Planning & Budgeting):
1. `/oobc-management/` - **Start here** for all P&B features
2. `/oobc-management/planning-budgeting/` - Main planning dashboard
3. `/oobc-management/analytics/` - Analytics & insights
4. `/oobc-management/scenarios/` - Budget scenario planning
5. `/oobc-management/strategic-goals/` - Strategic goals tracking

### For Community Members:
1. `/dashboard/` - Main overview
2. `/community/voting/` - Vote on community needs
3. `/transparency/` - View budget transparency
4. `/mana/` - Participate in MANA assessments

### For MAO Coordination:
1. `/coordination/` - Partnership management
2. `/oobc-management/mao-focal-persons/` - MAO registry
3. `/oobc-management/policy-budget-matrix/` - Policy linkages
4. `/monitoring/` - Track PPAs

---

## API Endpoints

### REST API Base URL: `/api/`

**Authentication:** All API endpoints require JWT authentication
- **Login:** `POST /api/token/`
- **Refresh Token:** `POST /api/token/refresh/`

### Planning & Budgeting APIs (Phase 8)

| Resource | Endpoint | Methods |
|----------|----------|---------|
| **Strategic Goals** | `/api/monitoring/strategic-goals/` | GET, POST, PUT, DELETE |
| **Planning Cycles** | `/api/monitoring/planning-cycles/` | GET, POST, PUT, DELETE |
| **Budget Scenarios** | `/api/monitoring/scenarios/` | GET, POST, PUT, DELETE |
| **Scenario Allocations** | `/api/monitoring/allocations/` | GET, POST, PUT, DELETE |

**Special Actions:**
- **Optimize Scenario:** `POST /api/monitoring/scenarios/<id>/optimize/`
- **Compare Scenarios:** `GET /api/monitoring/scenarios/<id>/compare/?scenario2=<id>`
- **Current Planning Cycle:** `GET /api/monitoring/planning-cycles/current/`
- **Active Strategic Goals:** `GET /api/monitoring/strategic-goals/active/`

### Other APIs

| Resource | Endpoint |
|----------|----------|
| Communities | `/api/communities/` |
| MANA Needs | `/api/mana/needs/` |
| Partnerships | `/api/coordination/partnerships/` |
| Policies | `/api/policy-tracking/recommendations/` |
| PPAs | `/api/monitoring/entries/` |

---

## Navigation Flow

### Typical User Journey (OOBC Staff)

```
1. Login → /dashboard/
2. Access P&B Features → /oobc-management/
3. View Planning Dashboard → /oobc-management/planning-budgeting/
4. Analyze Gaps → /oobc-management/gap-analysis/
5. Create Budget Scenario → /oobc-management/scenarios/create/
6. Run Optimization → /oobc-management/scenarios/<id>/optimize/
7. Compare Scenarios → /oobc-management/scenarios/compare/
8. View Analytics → /oobc-management/analytics/
9. Check Strategic Goals → /oobc-management/strategic-goals/
10. Assess Impact → /oobc-management/impact/
```

### Typical User Journey (Community Member)

```
1. Login → /dashboard/
2. View Transparency → /transparency/
3. Participate in Voting → /community/voting/
4. Check Voting Results → /community/voting/results/
5. Submit Feedback → /oobc-management/budget-feedback/
```

---

## Admin Interface

**Admin URL:** `/admin/`

Access Django admin for data management:
- User management: `/admin/common/user/`
- Communities: `/admin/communities/`
- MANA Needs: `/admin/mana/need/`
- Strategic Goals: `/admin/monitoring/strategicgoal/`
- Budget Scenarios: `/admin/monitoring/budgetscenario/`
- PPAs: `/admin/monitoring/monitoringentry/`

---

## URL Naming Conventions

### Pattern: `app:view_name`

**Examples:**
- `{% url 'common:dashboard' %}` → `/dashboard/`
- `{% url 'common:planning_budgeting' %}` → `/oobc-management/planning-budgeting/`
- `{% url 'common:scenario_list' %}` → `/oobc-management/scenarios/`
- `{% url 'common:scenario_detail' scenario_id=uuid %}` → `/oobc-management/scenarios/<uuid>/`

### Common URL Names (common app):

```python
# Core
dashboard
oobc_management_home

# Planning & Budgeting (Phases 1-3)
planning_budgeting
gap_analysis_dashboard
policy_budget_matrix
mao_focal_persons_registry
community_needs_summary

# Participatory Budgeting (Phase 4)
community_voting_browse
community_voting_vote
community_voting_results
budget_feedback_dashboard
transparency_dashboard

# Strategic Planning (Phase 5)
strategic_goals_dashboard
annual_planning_dashboard
regional_development_alignment

# Scenario Planning (Phase 6)
scenario_list
scenario_create
scenario_detail
scenario_compare
scenario_optimize

# Analytics & Forecasting (Phase 7)
analytics_dashboard
budget_forecasting
trend_analysis
impact_assessment

# Organizational
oobc_calendar
staff_management
user_approvals
```

---

## Integration Points

### Where to Add New Features

**Planning & Budgeting Related:**
- Add to `/oobc-management/` hub
- Update `src/templates/common/oobc_management_home.html` navigation
- Add URL to `src/common/urls.py`
- Export view from `src/common/views/__init__.py`

**New Module/App:**
- Create new URL entry in main dashboard
- Add to top-level navigation if needed
- Create app-specific URL configuration

---

## Troubleshooting

### Feature Not Accessible?

1. **Check URL exists:** Visit URL directly in browser
2. **Check permissions:** Ensure user has required permissions
3. **Check authentication:** Ensure user is logged in
4. **Check navigation:** Verify link is in OOBC Management home
5. **Check URL configuration:** Verify URL is in `urls.py`
6. **Check view export:** Verify view is in `__init__.py`

### Common Issues:

- **404 Not Found:** URL pattern doesn't exist or typo in URL
- **403 Forbidden:** User lacks required permissions
- **500 Server Error:** View has a bug (check logs)
- **No navigation link:** Template needs updating

---

## Future Enhancements

### Planned URLs (Phase 9+):

- `/oobc-management/risk-assessment/` - Risk matrix and mitigation
- `/oobc-management/performance-contracts/` - Performance agreements
- `/oobc-management/audit-compliance/` - Audit tracking
- `/oobc-management/resource-mobilization/` - Funding source tracking

---

## Related Documentation

- **[PLANNING_BUDGETING_FINAL_REPORT.md](improvements/PLANNING_BUDGETING_FINAL_REPORT.md)** - Complete P&B implementation details
- **[README.md](../README.md)** - Project overview and setup
- **[development/README.md](development/README.md)** - Development guidelines
- **[CLAUDE.md](../CLAUDE.md)** - AI coding instructions

---

**Navigation Status:** ✅ Complete - All Phases 1-8 URLs are accessible via `/oobc-management/`
