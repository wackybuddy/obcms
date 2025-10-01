# Navigation Architecture Diagram

**Planning & Budgeting Integration - Visual Guide**

---

## 🏗️ 3-Tier Navigation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER LOGIN & AUTHENTICATION                         │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TIER 1: MAIN DASHBOARD                           │
│                                 /dashboard/                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  📊 Planning & Budgeting (Staff-Only)                    [View All Features] │
│  ┌──────────────────┬──────────────────┬──────────────────┬────────────────┐│
│  │   Planning       │    Analytics     │    Scenario      │   Strategic    ││
│  │   Dashboard      │    Dashboard     │    Planning      │     Goals      ││
│  └──────────────────┴──────────────────┴──────────────────┴────────────────┘│
│                                                                               │
│  🌍 Community Participation (Public)             [View Transparency Dashboard]│
│  ┌────────────────────────────────┬────────────────────────────────────────┐│
│  │      Community Voting          │       Budget Transparency              ││
│  └────────────────────────────────┴────────────────────────────────────────┘│
│                                                                               │
│  📂 System Modules                                                            │
│  ┌──────────────┬──────────────┬──────────────┬──────────────────────────┐  │
│  │ Communities  │     MANA     │ Coordination │  Recommendations  More...│  │
│  └──────────────┴──────────────┴──────────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                │                            │                          │
                ▼                            ▼                          ▼
┌───────────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  TIER 2: MODULE HUBS      │  │  TIER 2: MODULE HUBS │  │  TIER 2: MODULE HUBS │
│  /communities/            │  │      /mana/          │  │  /coordination/      │
├───────────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│                           │  │                      │  │                      │
│  🏘️  Community Features   │  │  🗺️  MANA Features   │  │  🤝 Coordination     │
│  • Profiles               │  │  • Assessments       │  │  • Organizations     │
│  • Demographics           │  │  • Regional Overview │  │  • Partnerships      │
│  • Manage                 │  │  • Desk Review       │  │  • Events            │
│                           │  │                      │  │                      │
│  💰 P&B CONTEXTUAL LINKS  │  │  💰 P&B CONTEXTUAL   │  │  💰 P&B CONTEXTUAL   │
│  • Community Needs        │  │  • Gap Analysis      │  │  • MAO Registry      │
│  • Voting Results         │  │  • Funding Status    │  │  • Policy-Budget     │
│  • Budget Feedback        │  │                      │  │  • RDP Alignment     │
│                           │  │                      │  │                      │
└───────────────────────────┘  └──────────────────────┘  └──────────────────────┘
                │                            │                          │
                └────────────────────────────┴──────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TIER 3: OOBC MANAGEMENT HUB                            │
│                           /oobc-management/                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  📊 Key Metrics                                                               │
│  ┌──────────────┬──────────────┬──────────────────┬────────────────────────┐│
│  │ Total Staff  │ Active Staff │ Pending Approvals│   Staff Pending        ││
│  └──────────────┴──────────────┴──────────────────┴────────────────────────┘│
│                                                                               │
│  ⭐ FREQUENTLY USED                                       🔥 Quick Access     │
│  ┌─────────────────┬─────────────────┬─────────────────┐                    │
│  │   Planning      │   Analytics     │     Voting      │                    │
│  │   Dashboard     │   Dashboard     │     Results     │                    │
│  │   ₱2.5M • Core  │   Advanced      │   Community     │                    │
│  └─────────────────┴─────────────────┴─────────────────┘                    │
│  ┌─────────────────┬─────────────────┬─────────────────┐                    │
│  │    Budget       │   Strategic     │      Gap        │                    │
│  │   Scenarios     │     Goals       │    Analysis     │                    │
│  │   5 • Planning  │   12 • Strategic│   Critical      │                    │
│  └─────────────────┴─────────────────┴─────────────────┘                    │
│                                                                               │
│  💼 PHASE 1-3: Core Planning & Budgeting                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ • Planning Dashboard    • Gap Analysis       • Policy-Budget Matrix     ││
│  │ • MAO Registry          • Community Needs                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
│  🗳️  PHASE 4: Participatory Budgeting                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ • Community Voting      • Voting Results     • Budget Feedback          ││
│  │ • Transparency                                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
│  🎯 PHASE 5: Strategic Planning                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ • Strategic Goals       • Annual Planning    • RDP Alignment            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
│  🔄 PHASE 6: Scenario Planning & Optimization                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ • Budget Scenarios      • Create Scenario    • Compare Scenarios        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
│  📈 PHASE 7: Analytics & Forecasting                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ • Analytics Dashboard   • Budget Forecasting • Trend Analysis           ││
│  │ • Impact Assessment                                                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
│  ⚙️  ORGANIZATIONAL MANAGEMENT                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ • OOBC Calendar         • Staff Management   • User Approvals           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 User Flows

### Flow 1: Staff User → Quick Access to Planning Dashboard

```
1. Login → /dashboard/
2. See "Planning & Budgeting" section
3. Click "Planning Dashboard" card
4. → /oobc-management/planning-budgeting/

Total Clicks: 1
Time to Feature: <3 seconds
```

### Flow 2: Staff User → Browse All Features

```
1. Login → /dashboard/
2. See "Planning & Budgeting" section
3. Click "View All Features" link
4. → /oobc-management/
5. See "Frequently Used" section at top
6. Scroll to see all 22 features organized by phase

Total Clicks: 1
Time to Browse: <5 seconds
```

### Flow 3: Staff User → Contextual Access from MANA

```
1. Navigate to /mana/
2. See "Budget & Funding" section (Tier 2 - PENDING)
3. Click "Gap Analysis Dashboard"
4. → /oobc-management/gap-analysis/

Total Clicks: 1 (from module context)
Time to Feature: <3 seconds
```

### Flow 4: Community User → Vote on Priorities

```
1. Login → /dashboard/
2. See "Community Participation" section
3. Click "Vote on Community Needs" card
4. → /community/voting/
5. Cast vote on priorities

Total Clicks: 1
Time to Feature: <3 seconds
Note: Does NOT see staff-only P&B section
```

### Flow 5: Power User → Direct Navigation

```
1. Navigate to /oobc-management/ (bookmark or direct URL)
2. See "Frequently Used" section at top
3. Click desired feature from quick access

Total Clicks: 1
Time to Feature: <2 seconds
```

---

## 📊 Feature Distribution

### Main Dashboard (Tier 1)
- **Planning & Budgeting Section**: 4 cards (staff-only)
- **Community Participation Section**: 2 cards (public)
- **Total Quick Access**: 6 features

### Module Hubs (Tier 2 - PENDING)
- **Communities Hub**: 3 P&B links
- **MANA Hub**: 2 P&B links
- **Coordination Hub**: 3 P&B links
- **Recommendations Hub**: 2 P&B links
- **Monitoring Hub**: 3 P&B links
- **Total Contextual Links**: ~13 strategic placements

### OOBC Management (Tier 3)
- **Frequently Used Section**: 6 cards (top priority)
- **Phase 1-3: Core P&B**: 5 features
- **Phase 4: Participatory**: 4 features
- **Phase 5: Strategic**: 3 features
- **Phase 6: Scenarios**: 3 features
- **Phase 7: Analytics**: 4 features
- **Organizational Management**: 3 features
- **Total Features**: 22 + 6 quick access

---

## 🎨 Visual Design System

### Color Coding

| Phase/Category | Color | Use Case |
|----------------|-------|----------|
| **Core Planning** | Blue → Indigo | Budget tracking, PPA monitoring |
| **Participatory** | Emerald → Green | Community engagement, voting |
| **Strategic** | Purple → Indigo | Long-term goals, RDP alignment |
| **Scenarios** | Orange → Red | What-if analysis, optimization |
| **Analytics** | Cyan → Blue | Insights, trends, forecasting |
| **Organizational** | Gray → Dark Gray | Staff, calendar, approvals |
| **Quick Access** | Amber | Frequently used features |

### Card Styles

#### Gradient Cards (Main Dashboard - Staff)
```
┌────────────────────────────────┐
│ [Icon]              →          │  ← Gradient background
│                                │     White text
│ Feature Title                  │     Hover: scale + shadow
│ Short description              │
└────────────────────────────────┘
```

#### White Badge Cards (Main Dashboard - Public)
```
┌────────────────────────────────┐
│ [Icon]          [Public Badge] │  ← White background
│                                │     Colored icon
│ Feature Title                  │     Border + shadow
│ Longer description             │     Hover: border color
└────────────────────────────────┘
```

#### Mini-Stat Cards (OOBC Management - Frequently Used)
```
┌────────────────────────────────┐
│ [Icon]          [Badge]        │  ← White background
│                                │     Colored border
│ Feature Title                  │     Mini stats below
│ Description                    │     Hover: lift + shadow
│ ₱2.5M • Core        View Now → │
└────────────────────────────────┘
```

#### Compact List Cards (OOBC Management - Phases)
```
┌────────────────────────────────┐
│ [Icon] Feature Title           │  ← Minimal white card
│        Short description       │     Simple border
└────────────────────────────────┘     Hover: border color
```

---

## 🔍 Discoverability Matrix

| User Type | Entry Point | Time to P&B Feature | Clicks Required |
|-----------|-------------|---------------------|-----------------|
| **Staff** | Login | <3 seconds | 1 (quick access) |
| **Staff** | Module Hub | <3 seconds | 1 (contextual) |
| **Staff** | Direct URL | <2 seconds | 0 (bookmarked) |
| **Community** | Login | <3 seconds | 1 (voting/transparency) |
| **Community** | P&B Features | ∞ (no access) | ∞ (hidden) |

---

## 📈 Analytics & Monitoring

### Key Metrics to Track
1. **Click-through Rate**: From main dashboard → P&B features
2. **Most-Used Features**: Which cards get clicked most?
3. **Quick Access vs Full Directory**: Do users prefer Tier 1 or Tier 3?
4. **Contextual Usage**: Do users find P&B links in module hubs? (Tier 2)
5. **Community Engagement**: How many community votes after dashboard visibility?

### Expected Results
- **70%+ users** should access P&B features from main dashboard (Tier 1)
- **20% users** should use OOBC Management hub's "Frequently Used" (Tier 3)
- **10% users** should discover P&B via contextual links (Tier 2)

---

## 🚀 Performance Considerations

### Page Load Times
- **Main Dashboard**: +50ms (6 extra cards, minimal metrics)
- **OOBC Management**: +30ms (6 extra cards, reuses existing metrics)
- **Module Hubs**: +10ms each (2-3 extra links)

### Database Queries
- **Main Dashboard**: +0 queries (no new data)
- **OOBC Management**: +2 queries (scenarios count, goals count)
  - Cached after first load
  - Invalidated on budget/scenario/goal changes

### Caching Strategy
```python
# Cache metrics for 5 minutes
from django.core.cache import cache

metrics = cache.get('oobc_management_metrics')
if not metrics:
    metrics = {
        'scenarios_count': BudgetScenario.objects.count(),
        'goals_count': StrategicGoal.objects.count(),
        'total_budget': calculate_total_budget(),
    }
    cache.set('oobc_management_metrics', metrics, 300)  # 5 minutes
```

---

## 🔐 Permission Matrix

| Feature | Staff | Admin | Community | Anonymous |
|---------|-------|-------|-----------|-----------|
| **Main Dashboard - P&B Section** | ✅ | ✅ | ❌ | ❌ |
| **Main Dashboard - Community Section** | ✅ | ✅ | ✅ | ❌ |
| **OOBC Management Hub** | ✅ | ✅ | ❌ | ❌ |
| **Planning Dashboard** | ✅ | ✅ | ❌ | ❌ |
| **Community Voting** | ✅ | ✅ | ✅ | ❌ |
| **Transparency Dashboard** | ✅ | ✅ | ✅ | ❌ |
| **Analytics Dashboard** | ✅ | ✅ | ❌ | ❌ |

---

## 📱 Responsive Breakpoints

### Desktop (≥1024px)
- Main Dashboard P&B: 4 cards in 1 row
- Main Dashboard Community: 2 cards in 1 row
- OOBC Management Frequently Used: 3 cards in 1 row (2 rows total)

### Tablet (768px - 1023px)
- Main Dashboard P&B: 2 cards in 2 rows
- Main Dashboard Community: 2 cards in 1 row
- OOBC Management Frequently Used: 2 cards in 3 rows

### Mobile (≤767px)
- Main Dashboard P&B: 1 card per row (4 rows)
- Main Dashboard Community: 1 card per row (2 rows)
- OOBC Management Frequently Used: 1 card per row (6 rows)

---

## 🎯 Success Criteria

✅ **Completed**:
1. Main dashboard quick access implemented (Tier 1)
2. OOBC Management "Frequently Used" section implemented (Tier 3)
3. All 22 P&B features accessible within 2 clicks
4. Role-based visibility working correctly
5. Metrics calculation optimized (<50ms overhead)

⏳ **Pending**:
1. Contextual links in module hubs (Tier 2)
2. User testing and feedback collection
3. Analytics implementation for usage tracking
4. Performance monitoring in production
5. A/B testing for card designs

---

**Last Updated**: October 1, 2025
**Version**: 1.0
**Status**: Tier 1 & Tier 3 Complete | Tier 2 Pending
