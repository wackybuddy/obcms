# Hero Section Specifications for All Modules

**Date**: October 2, 2025
**Status**: Design Specifications
**Purpose**: Define hero section designs for each OBCMS module dashboard
**Related**: [Consistent Dashboard Implementation Plan](CONSISTENT_DASHBOARD_IMPLEMENTATION_PLAN.md)

---

## 🎯 **HERO SECTION PATTERN**

Based on the OOBC Calendar Management implementation, every module hero section includes:

1. **Gradient Background** - Module-specific color scheme
2. **Context Badge** - Category or mission statement
3. **Headline** - Module name or value proposition
4. **Description** - Purpose and key capabilities (2-3 sentences)
5. **Inline Stats** - 3 key metrics in glassmorphism cards
6. **Action Buttons** - 4-6 primary actions (vertical stack on right)

---

## 📐 **MODULE HERO SECTIONS**

### **1. Main Dashboard Hero** (`common/dashboard.html`)

**Gradient**: `from-blue-600 via-indigo-600 to-purple-700`

```html
<section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 shadow-2xl">
    <!-- Background decoration -->
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>
    <div class="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -mr-48 -mt-48"></div>

    <div class="relative px-10 py-10">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

            <!-- Left: Branding -->
            <div class="flex-1 space-y-6">
                <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                    <i class="fas fa-tachometer-alt mr-2"></i>
                    COMMAND CENTER
                </div>

                <h2 class="text-4xl font-bold text-white">
                    Your OBCMS Dashboard
                </h2>

                <p class="text-white/90 text-lg max-w-2xl">
                    Welcome, {{ user.get_full_name }}. Monitor all OBC initiatives, track assessments, coordinate partnerships, and manage office operations from your central command center.
                </p>

                <!-- Inline Stats -->
                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Active Modules</p>
                        <p class="text-2xl font-bold text-white">6</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Pending Tasks</p>
                        <p class="text-2xl font-bold text-white">{{ stats.pending_tasks|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Recent Updates</p>
                        <p class="text-2xl font-bold text-white">{{ stats.recent_count|default:0 }}</p>
                    </div>
                </div>
            </div>

            <!-- Right: Actions -->
            <div class="flex-shrink-0">
                <div class="flex flex-col gap-3 min-w-[220px]">
                    <a href="{% url 'common:communities_add' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-blue-600 font-semibold shadow-lg hover:shadow-xl transition-all">
                        <i class="fas fa-mosque"></i>
                        <span>Add OBC</span>
                    </a>
                    <a href="{% url 'common:mana_new_assessment' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-map-marked-alt"></i>
                        <span>New Assessment</span>
                    </a>
                    <a href="{% url 'common:coordination_event_add' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-calendar-plus"></i>
                        <span>Schedule Event</span>
                    </a>
                    <a href="{% url 'common:oobc_calendar' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all">
                        <i class="fas fa-calendar-week"></i>
                        <span>View Calendar</span>
                    </a>
                </div>
            </div>

        </div>
    </div>
</section>
```

---

### **2. Communities Home Hero** (`communities/communities_home.html`)

**Gradient**: `from-blue-500 via-cyan-500 to-teal-600`

```html
<section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-600 shadow-2xl">
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>

    <div class="relative px-10 py-10">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

            <div class="flex-1 space-y-6">
                <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                    <i class="fas fa-mosque mr-2"></i>
                    COMMUNITY DATA HUB
                </div>

                <h2 class="text-4xl font-bold text-white">
                    Other Bangsamoro Communities
                </h2>

                <p class="text-white/90 text-lg max-w-2xl">
                    Comprehensive database of Bangsamoro communities outside BARMM. Manage barangay, municipal, and provincial OBC profiles with demographic data and geographic information.
                </p>

                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Total Communities</p>
                        <p class="text-2xl font-bold text-white">{{ stats.total_obcs|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Provinces</p>
                        <p class="text-2xl font-bold text-white">{{ stats.provinces|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Population</p>
                        <p class="text-2xl font-bold text-white">{{ stats.total_population|intcomma }}</p>
                    </div>
                </div>
            </div>

            <div class="flex-shrink-0">
                <div class="flex flex-col gap-3 min-w-[220px]">
                    <a href="{% url 'common:communities_add' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-cyan-600 font-semibold shadow-lg hover:shadow-xl transition-all">
                        <i class="fas fa-plus-circle"></i>
                        <span>Add Barangay OBC</span>
                    </a>
                    <a href="{% url 'common:communities_add_municipality' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-city"></i>
                        <span>Add Municipal</span>
                    </a>
                    <a href="{% url 'common:mana_regional_overview' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-map"></i>
                        <span>View on Map</span>
                    </a>
                    <a href="#" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all">
                        <i class="fas fa-file-export"></i>
                        <span>Export Data</span>
                    </a>
                </div>
            </div>

        </div>
    </div>
</section>
```

---

### **3. MANA Home Hero** (`mana/mana_home.html`)

**Gradient**: `from-emerald-500 via-teal-500 to-cyan-600`

```html
<section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-600 shadow-2xl">
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>

    <div class="relative px-10 py-10">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

            <div class="flex-1 space-y-6">
                <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                    <i class="fas fa-map-marked-alt mr-2"></i>
                    ASSESSMENT OPERATIONS CENTER
                </div>

                <h2 class="text-4xl font-bold text-white">
                    Mapping & Needs Assessment
                </h2>

                <p class="text-white/90 text-lg max-w-2xl">
                    Comprehensive geospatial mapping and community needs assessment system. Combine desk review, surveys, and key informant interviews to inform evidence-based planning.
                </p>

                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Active Assessments</p>
                        <p class="text-2xl font-bold text-white">{{ stats.active_assessments|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Fieldwork Planned</p>
                        <p class="text-2xl font-bold text-white">{{ stats.planned_activities|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Coverage Areas</p>
                        <p class="text-2xl font-bold text-white">{{ stats.coverage_areas|default:0 }}</p>
                    </div>
                </div>
            </div>

            <div class="flex-shrink-0">
                <div class="flex flex-col gap-3 min-w-[220px]">
                    <a href="{% url 'common:mana_new_assessment' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-emerald-600 font-semibold shadow-lg hover:shadow-xl transition-all">
                        <i class="fas fa-plus-circle"></i>
                        <span>New Assessment</span>
                    </a>
                    <a href="{% url 'common:mana_activity_planner' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-calendar-day"></i>
                        <span>Plan Activity</span>
                    </a>
                    <a href="{% url 'common:mana_regional_overview' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-map"></i>
                        <span>Regional Map</span>
                    </a>
                    <a href="{% url 'common:mana_playbook' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all">
                        <i class="fas fa-book"></i>
                        <span>View Playbook</span>
                    </a>
                </div>
            </div>

        </div>
    </div>
</section>
```

---

### **4. Coordination Home Hero** (`coordination/coordination_home.html`)

**Gradient**: `from-orange-500 via-amber-500 to-yellow-600`

```html
<section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-600 shadow-2xl">
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>

    <div class="relative px-10 py-10">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

            <div class="flex-1 space-y-6">
                <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                    <i class="fas fa-handshake mr-2"></i>
                    PARTNERSHIP COORDINATION HUB
                </div>

                <h2 class="text-4xl font-bold text-white">
                    Multi-Stakeholder Coordination
                </h2>

                <p class="text-white/90 text-lg max-w-2xl">
                    Build strategic partnerships, manage MOAs and agreements, coordinate inter-agency activities, and track collaboration outcomes across BMOA, NGA, and LGU partners.
                </p>

                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Active Partners</p>
                        <p class="text-2xl font-bold text-white">{{ stats.active_partners|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">MOAs/MOUs</p>
                        <p class="text-2xl font-bold text-white">{{ stats.partnerships|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Upcoming Events</p>
                        <p class="text-2xl font-bold text-white">{{ stats.upcoming_events|default:0 }}</p>
                    </div>
                </div>
            </div>

            <div class="flex-shrink-0">
                <div class="flex flex-col gap-3 min-w-[220px]">
                    <a href="{% url 'common:coordination_organization_add' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-orange-600 font-semibold shadow-lg hover:shadow-xl transition-all">
                        <i class="fas fa-building"></i>
                        <span>Add Partner</span>
                    </a>
                    <a href="{% url 'common:coordination_partnership_add' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-file-contract"></i>
                        <span>New MOA/MOU</span>
                    </a>
                    <a href="{% url 'common:coordination_event_add' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-calendar-plus"></i>
                        <span>Schedule Event</span>
                    </a>
                    <a href="{% url 'common:coordination_calendar' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all">
                        <i class="fas fa-calendar-alt"></i>
                        <span>View Calendar</span>
                    </a>
                </div>
            </div>

        </div>
    </div>
</section>
```

---

### **5. Recommendations Home Hero** (`recommendations/recommendations_home.html`)

**Gradient**: `from-purple-500 via-violet-500 to-indigo-600`

```html
<section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-600 shadow-2xl">
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>

    <div class="relative px-10 py-10">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

            <div class="flex-1 space-y-6">
                <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                    <i class="fas fa-lightbulb mr-2"></i>
                    POLICY DEVELOPMENT CENTER
                </div>

                <h2 class="text-4xl font-bold text-white">
                    Policy Recommendations
                </h2>

                <p class="text-white/90 text-lg max-w-2xl">
                    Evidence-based policy recommendations and programmatic proposals. Track advocacy efforts, link policies to budget allocations, and monitor implementation progress across sectors.
                </p>

                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Total Policies</p>
                        <p class="text-2xl font-bold text-white">{{ stats.total_policies|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Under Review</p>
                        <p class="text-2xl font-bold text-white">{{ stats.under_review|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Implemented</p>
                        <p class="text-2xl font-bold text-white">{{ stats.implemented|default:0 }}</p>
                    </div>
                </div>
            </div>

            <div class="flex-shrink-0">
                <div class="flex flex-col gap-3 min-w-[220px]">
                    <a href="{% url 'common:recommendations_new' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-purple-600 font-semibold shadow-lg hover:shadow-xl transition-all">
                        <i class="fas fa-plus-circle"></i>
                        <span>New Recommendation</span>
                    </a>
                    <a href="{% url 'common:recommendations_manage' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-balance-scale"></i>
                        <span>View All Policies</span>
                    </a>
                    <a href="{% url 'common:policy_budget_matrix' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-link"></i>
                        <span>Budget Linkage</span>
                    </a>
                    <a href="#" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all">
                        <i class="fas fa-file-export"></i>
                        <span>Export Report</span>
                    </a>
                </div>
            </div>

        </div>
    </div>
</section>
```

---

### **6. M&E Dashboard Hero** (`monitoring/monitoring_dashboard.html`)

**Gradient**: `from-rose-500 via-pink-500 to-fuchsia-600`

```html
<section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-rose-500 via-pink-500 to-fuchsia-600 shadow-2xl">
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>

    <div class="relative px-10 py-10">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

            <div class="flex-1 space-y-6">
                <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                    <i class="fas fa-chart-line mr-2"></i>
                    MONITORING & EVALUATION CENTER
                </div>

                <h2 class="text-4xl font-bold text-white">
                    Performance Monitoring
                </h2>

                <p class="text-white/90 text-lg max-w-2xl">
                    Track MOA PPAs, OOBC initiatives, and community requests. Monitor budget execution, measure impact, and generate compliance reports for evidence-based decision making.
                </p>

                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Total Programs</p>
                        <p class="text-2xl font-bold text-white">{{ stats.total_programs|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Budget Utilized</p>
                        <p class="text-2xl font-bold text-white">{{ stats.budget_utilized_percent|default:0 }}%</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Beneficiaries</p>
                        <p class="text-2xl font-bold text-white">{{ stats.beneficiaries|intcomma }}</p>
                    </div>
                </div>
            </div>

            <div class="flex-shrink-0">
                <div class="flex flex-col gap-3 min-w-[220px]">
                    <a href="{% url 'monitoring:create_moa' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-rose-600 font-semibold shadow-lg hover:shadow-xl transition-all">
                        <i class="fas fa-file-alt"></i>
                        <span>Add MOA PPA</span>
                    </a>
                    <a href="{% url 'project_central:me_analytics_dashboard' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-chart-bar"></i>
                        <span>View Analytics</span>
                    </a>
                    <a href="{% url 'monitoring:prioritization_matrix' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-sort-amount-down"></i>
                        <span>Prioritization</span>
                    </a>
                    <a href="{% url 'project_central:report_list' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all">
                        <i class="fas fa-file-chart-line"></i>
                        <span>Generate Report</span>
                    </a>
                </div>
            </div>

        </div>
    </div>
</section>
```

---

### **7. OOBC Management Home Hero** (`common/oobc_management_home.html`)

**Gradient**: `from-sky-500 via-blue-500 to-indigo-600`

```html
<section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-sky-500 via-blue-500 to-indigo-600 shadow-2xl">
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>

    <div class="relative px-10 py-10">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

            <div class="flex-1 space-y-6">
                <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                    <i class="fas fa-cogs mr-2"></i>
                    OFFICE OPERATIONS HUB
                </div>

                <h2 class="text-4xl font-bold text-white">
                    OOBC Management
                </h2>

                <p class="text-white/90 text-lg max-w-2xl">
                    Coordinate internal operations, manage staff tasks and performance, plan budgets, track strategic goals, and maintain organization-wide calendar for seamless office administration.
                </p>

                <div class="flex flex-wrap gap-4">
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Active Staff</p>
                        <p class="text-2xl font-bold text-white">{{ metrics.active_staff|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Open Tasks</p>
                        <p class="text-2xl font-bold text-white">{{ metrics.open_tasks|default:0 }}</p>
                    </div>
                    <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                        <p class="text-sm text-white/70 uppercase tracking-wide">Events This Week</p>
                        <p class="text-2xl font-bold text-white">{{ metrics.week_events|default:0 }}</p>
                    </div>
                </div>
            </div>

            <div class="flex-shrink-0">
                <div class="flex flex-col gap-3 min-w-[220px]">
                    <a href="{% url 'common:staff_task_create' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-sky-600 font-semibold shadow-lg hover:shadow-xl transition-all">
                        <i class="fas fa-plus-square"></i>
                        <span>Create Task</span>
                    </a>
                    <a href="{% url 'common:oobc_calendar' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-calendar-alt"></i>
                        <span>View Calendar</span>
                    </a>
                    <a href="{% url 'common:planning_budgeting' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all">
                        <i class="fas fa-calculator"></i>
                        <span>Budget Planning</span>
                    </a>
                    <a href="{% url 'common:staff_performance_dashboard' %}" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all">
                        <i class="fas fa-chart-line"></i>
                        <span>Performance</span>
                    </a>
                </div>
            </div>

        </div>
    </div>
</section>
```

---

## 📊 **SUMMARY TABLE**

| Module | Gradient Colors | Badge Text | Primary Action |
|--------|----------------|------------|----------------|
| **Main Dashboard** | blue-indigo-purple | COMMAND CENTER | Add OBC |
| **Communities** | blue-cyan-teal | COMMUNITY DATA HUB | Add Barangay OBC |
| **MANA** | emerald-teal-cyan | ASSESSMENT OPERATIONS | New Assessment |
| **Coordination** | orange-amber-yellow | PARTNERSHIP HUB | Add Partner |
| **Recommendations** | purple-violet-indigo | POLICY DEVELOPMENT | New Recommendation |
| **M&E** | rose-pink-fuchsia | MONITORING CENTER | Add MOA PPA |
| **OOBC Mgt** | sky-blue-indigo | OFFICE OPERATIONS | Create Task |

---

## ✅ **IMPLEMENTATION CHECKLIST**

For each module dashboard:

- [ ] Gradient background matches module color scheme
- [ ] Context badge with appropriate icon and text
- [ ] Headline is clear and action-oriented
- [ ] Description explains value proposition (2-3 sentences)
- [ ] 3 inline stats with glassmorphism cards
- [ ] 4-6 action buttons (primary + secondary styles)
- [ ] Proper spacing and responsive layout
- [ ] Accessibility: proper contrast ratios, ARIA labels
- [ ] Mobile responsive: stacks vertically on small screens

---

**End of Hero Section Specifications**

**Next Steps**:
1. Implement hero sections in module templates
2. Test responsive behavior on mobile/tablet
3. Verify accessibility compliance
4. Gather user feedback on visual hierarchy

**Prepared By**: Claude Code AI Agent
**Date**: October 2, 2025
**Version**: 1.0
