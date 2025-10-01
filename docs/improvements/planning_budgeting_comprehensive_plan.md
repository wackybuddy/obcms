# Comprehensive Planning & Budgeting Module Improvement Plan for OOBC

**Document Status**: Draft for Review
**Date Created**: October 1, 2025
**Author**: System Analysis & Planning
**Related Documents**:
- [OBC Guidelines Assistance](../guidelines/OBC_guidelines_assistance.md)
- [OOBC Integrative Report](../reports/OOBC_integrative_report.md)
- [Current Planning & Budgeting Module Improvements](planning_budgeting_module_improvements.md)

---

## Executive Summary

This document outlines a comprehensive improvement plan for the OOBC Planning & Budgeting Module at http://localhost:8000/oobc-management/planning-budgeting/. The plan integrates:

1. **International best practices** in government planning and budgeting (GFOA, IMF, performance-based budgeting)
2. **Philippine government standards** (DBM requirements, BARMM budget cycle)
3. **OOBC-specific mandates** from the Bangsamoro Organic Law and Guidelines for Assistance to OBCs
4. **Participatory budgeting principles** to ensure community involvement
5. **Evidence-based policy linkage** connecting the 10 policy recommendations to budget allocations

The improvements transform the module from a basic monitoring dashboard into a comprehensive **Planning, Programming, and Budgeting System (PPBS)** that supports the "whole of government" approach mandated by the BOL.

---

## Table of Contents

1. [Context and Mandate](#context-and-mandate)
2. [Current State Analysis](#current-state-analysis)
3. [Research Findings](#research-findings)
4. [Strategic Improvement Areas](#strategic-improvement-areas)
5. [Detailed Feature Specifications](#detailed-feature-specifications)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Success Metrics](#success-metrics)
8. [Appendices](#appendices)

---

## Context and Mandate

### Legal and Policy Framework

**Bangsamoro Organic Law (BOL) Section 12, Article VI** mandates that:
- The Bangsamoro Government shall provide assistance to OBCs in coordination with LGUs and appropriate NGAs
- Assistance shall enhance economic, social, and cultural development of OBCs

**Guidelines for Assistance to OBCs** specify that:
- MAOs shall employ a "whole of government" approach
- OOBC shall coordinate to promote this approach
- MAOs shall prepare **menu of programs, projects, and services** that OBCs can access
- OCM shall conduct **quarterly coordination and consultation meetings**
- Planning shall be based on **participatory needs assessments**
- Budget allocations shall be based on these needs assessments

### OOBC's Coordinating Role

The OOBC is a **recommendatory and coordinating body**, not a direct implementer. The planning and budgeting module must therefore support:

1. **Policy recommendation** to the Chief Minister
2. **Coordination** among MAOs, LGUs, and NGAs
3. **Consolidation** of interventions to avoid duplication
4. **Monitoring and evaluation** of assistance programs
5. **Community participation** in planning processes

---

## Current State Analysis

### Existing Strengths

The current module (analyzed at `src/common/views/management.py:2683` and template `src/templates/common/oobc_planning_budgeting.html`) already provides:

✅ **Comprehensive data model** (`MonitoringEntry`) with:
- Plan year, fiscal year tracking
- Sector classification (6 sectors)
- Appropriation class (PS/MOOE/CO)
- Funding source tracking (GAA, Block Grant, LGU, Donor, etc.)
- Compliance flags (GAD, CCET, IP, Peace, SDG)
- Budget ceiling and allocation fields
- Geographic coverage (Region → Barangay)

✅ **Funding flow tracking** (`MonitoringEntryFunding`) for:
- Allocations, obligations, disbursements, adjustments
- Multiple funding tranches per PPA

✅ **Workflow stage management** (`MonitoringEntryWorkflowStage`) covering:
- Budget Call → Formulation → Technical Hearing → Legislation → Execution → Accountability

✅ **Dashboard analytics** showing:
- Financial totals (budget, OBC allocation, ceiling, allocations, obligations, disbursements)
- Category, status, sector, appropriation, and funding breakdowns
- Compliance snapshot
- Top allocations and upcoming milestones
- Workflow summary
- Funding timeline

### Critical Gaps

Despite strong foundations, the module lacks:

❌ **Participatory planning mechanisms** - No structured way for OBCs to submit priorities or vote on budget allocations
❌ **Needs-to-budget linkage** - Weak connection between MANA assessments and budget proposals
❌ **MAO coordination workflows** - No systematic tracking of quarterly coordination meetings or MAO focal persons
❌ **Menu of services** - No catalog of programs/projects that OBCs can access
❌ **Multi-year strategic planning** - Focus is on annual budgets, not medium-term plans
❌ **Performance-based budgeting** - No systematic linking of outcomes to funding decisions
❌ **Scenario planning** - Limited tools for comparing different allocation strategies
❌ **Community feedback loops** - No mechanism for OBCs to provide input on implemented programs
❌ **Policy recommendation tracking** - The 10 policy recommendations are not systematically linked to budget items

---

## Research Findings

### International Best Practices

#### 1. Government Finance Officers Association (GFOA) Recommendations

**Key principles for state and local government budgeting:**

- **Strategic planning integration**: Budget must align with long-term vision and strategic priorities
- **Multi-year perspective**: Consider consequences over 3-5 year horizon, not just annual balance
- **Community engagement**: Active stakeholder involvement in priority-setting
- **Performance measurement**: Link funding to measurable outcomes
- **Transparent communication**: Make budget accessible to public

**Application to OOBC**: The module should support multi-year planning aligned with Bangsamoro Development Plan and enable community input into priorities.

#### 2. Performance-Based Budgeting (PBB)

**Core concept**: Link funding to results, making systematic use of performance information.

**Key characteristics:**
- Result-oriented framework
- Measurable performance goals and outcomes
- Resource allocation based on effectiveness and efficiency
- Integration of sectoral plans with budget cycle

**International examples:**
- **Australia**: Outcome Budget Framework ties agency budgets to specific outcomes
- **New Zealand**: Comprehensive PBB system across all agencies
- **United States**: Government Performance and Results Act (GPRA) requires strategic plans and performance reporting

**Application to OOBC**: Each PPA should define expected outcomes (e.g., "50 scholars graduated," "10 Madaris strengthened") and track achievement against funding.

#### 3. Participatory Budgeting (PB)

**Definition**: Citizen engagement process where community members directly decide how to allocate public budget.

**Origins**: Started in Porto Alegre, Brazil (1989), now used in 7,000+ cities worldwide.

**Benefits:**
- Better use of public funding
- Increased transparency and reduced corruption
- Access for historically excluded citizens
- Improved government accountability

**Approaches:**
- **Top-down**: Required by federal government (e.g., Peru)
- **Bottom-up**: Initiated by local governments (e.g., Porto Alegre)

**Application to OOBC**: Given OOBC's mandate for community consultation, a bottom-up PB approach would allow OBC representatives to submit priorities and participate in allocation decisions during quarterly meetings.

### Philippine Government Context

#### DBM Budget Preparation Guidelines

The Philippine government budget cycle follows:

1. **Budget Call** (January-March): DBM issues budget call with ceilings
2. **Budget Preparation** (April-July): Agencies prepare budget proposals
3. **Budget Hearings** (August): Technical hearings on proposals
4. **Budget Legislation** (September-December): Congressional approval
5. **Budget Execution** (January-December): Implementation and monitoring
6. **Accountability** (Year-round): Audits and performance reviews

**BARMM-specific**: The Bangsamoro Government has its own budget process but must coordinate with national DBM for certain funding sources (GAA).

#### Outcome Budgeting Best Practices

Philippine DBM emphasizes:
- Linking scheme-level outcomes to Sustainable Development Goals (SDGs)
- Adopting data management practices
- Tracking progress on outcome indicators
- Using performance information in decision-making

---

## Strategic Improvement Areas

Based on research, OOBC mandates, and current gaps, the module should be enhanced in **eight strategic areas**:

### Area 1: Participatory Planning & Community Engagement

**Objective**: Enable OBCs to actively participate in planning and budget priority-setting.

**Key features:**
- **Community needs submission portal** where OBC leaders submit priorities with supporting data
- **Priority voting system** for OBC representatives during quarterly meetings
- **Consultation tracking** to document community input from regional meetings
- **Feedback mechanism** for OBCs to comment on budget proposals and implemented programs

**Alignment**: Directly supports BOL mandate and Guidelines requirement for "participatory needs assessments" and "active community involvement."

### Area 2: Needs-to-Budget Integration

**Objective**: Systematically link MANA findings and community needs to budget proposals.

**Key features:**
- **Needs assessment linkage** showing which MANA findings inform each PPA
- **Priority matrix** ranking proposals by urgency, impact, feasibility, equity
- **Gap analysis dashboard** highlighting high-priority needs lacking budget allocations
- **Evidence repository** storing consultation reports, MANA data, and supporting documents

**Alignment**: Implements Guidelines requirement that "allocations shall be based on needs assessments."

### Area 3: MAO Coordination & "Whole of Government" Approach

**Objective**: Facilitate systematic coordination among OOBC, MAOs, LGUs, and NGAs.

**Key features:**
- **MAO focal person registry** tracking permanent and alternate focal persons per MAO
- **Quarterly meeting scheduler** for OCM coordination meetings
- **Coordination event tracker** logging meetings, decisions, and action items
- **MOA/agreement management** storing memoranda and partnership documents
- **Duplication prevention** flagging overlapping interventions across MAOs

**Alignment**: Implements Guidelines requirement for "quarterly coordination and consultation meetings" and "whole of government approach."

### Area 4: Menu of Services & Program Catalog

**Objective**: Consolidate and publish all programs/projects/services available to OBCs.

**Key features:**
- **Service catalog** listing all MAO programs accessible to OBCs
- **Eligibility criteria** defining who can access each program
- **Application workflows** showing how OBCs can apply
- **Service coverage map** showing which regions/provinces are served
- **Performance history** displaying past beneficiaries and outcomes

**Alignment**: Implements Guidelines requirement that "MAOs shall prepare their respective menu of programs, projects, and services."

### Area 5: Multi-Year Strategic Planning

**Objective**: Enable planning beyond annual budgets, aligned with medium-term development plans.

**Key features:**
- **3-5 year planning horizon** for major infrastructure and capacity-building programs
- **Rolling plan process** with annual reviews and updates
- **Strategic goal alignment** linking PPAs to Bangsamoro Development Plan and Chief Minister's Priority Agenda
- **Multi-year obligation tracking** for programs spanning multiple fiscal years

**Alignment**: Follows GFOA best practice for "long-range perspective."

### Area 6: Performance-Based Budgeting

**Objective**: Link funding to measurable outcomes and use performance data in decision-making.

**Key features:**
- **Outcome indicators** for each PPA (quantitative and qualitative)
- **Results-based M&E framework** tracking outputs, outcomes, and impacts
- **Performance scorecards** comparing planned vs. actual results
- **Lessons learned repository** capturing what worked and what didn't
- **Budget-performance dashboard** showing cost-effectiveness of interventions

**Alignment**: Aligns with DBM outcome budgeting practices and international PBB standards.

### Area 7: Policy Recommendation Tracking

**Objective**: Systematically link the 10 policy recommendations to budget allocations and implementation.

**Key features:**
- **Policy recommendation registry** for the 10 recommendations from the Integrative Report
- **Budget tagging** showing which PPAs implement each recommendation
- **Implementation tracker** monitoring progress on each recommendation
- **Resource gap analysis** identifying which recommendations lack adequate funding
- **Impact assessment** evaluating whether recommendations achieve intended outcomes

**Alignment**: Supports OOBC's mandate to "recommend policies and systematic programs."

### Area 8: Scenario Planning & Resource Optimization

**Objective**: Enable planners to model different allocation strategies and optimize resource use.

**Key features:**
- **Budget scenario builder** comparing different allocation options
- **Ceiling management** tracking limits per funding source
- **Variance analysis** monitoring deviations from plan
- **Forecasting tools** predicting slippages and bottlenecks
- **Equity analysis** ensuring balanced distribution across regions and sectors

**Alignment**: Supports evidence-based decision-making and efficient resource use.

---

## Detailed Feature Specifications

### Feature Set 1: Community Needs Submission Portal

**User stories:**
- As an OBC leader, I want to submit priority needs so they are considered in budget planning
- As an OOBC coordinator, I want to review submitted needs and link them to MANA data
- As an MAO planner, I want to see which needs fall under my agency's mandate

**Technical requirements:**

**Data model extensions:**
```python
class CommunityNeedSubmission(models.Model):
    """Community-submitted priority needs for budget consideration."""

    PRIORITY_URGENT = 'urgent'
    PRIORITY_HIGH = 'high'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_LOW = 'low'

    submitted_by_community = ForeignKey('communities.OBCCommunity')
    submitted_by_user = ForeignKey(User)  # OBC leader/representative
    title = CharField(max_length=255)
    description = TextField()
    category = CharField(choices=[
        ('education', 'Education'),
        ('health', 'Health'),
        ('livelihood', 'Livelihood'),
        ('infrastructure', 'Infrastructure'),
        ('cultural', 'Cultural Development'),
        # ... other categories
    ])
    priority_level = CharField(choices=PRIORITY_CHOICES)
    estimated_beneficiaries = PositiveIntegerField()
    estimated_cost = DecimalField()
    supporting_evidence = TextField()  # References to MANA, consultations
    related_mana_assessment = ForeignKey('mana.Assessment', null=True)

    # Workflow
    status = CharField(choices=[
        ('submitted', 'Submitted'),
        ('under_review', 'Under OOBC Review'),
        ('forwarded_to_mao', 'Forwarded to MAO'),
        ('included_in_budget', 'Included in Budget Proposal'),
        ('approved', 'Approved for Funding'),
        ('deferred', 'Deferred'),
    ])
    reviewed_by = ForeignKey(User, null=True, related_name='reviewed_needs')
    review_notes = TextField(blank=True)
    forwarded_to_mao = ForeignKey('coordination.Organization', null=True)
    linked_ppa = ForeignKey('monitoring.MonitoringEntry', null=True)

    # Community engagement
    community_votes = PositiveIntegerField(default=0)  # For participatory budgeting
    public_comments = ManyToManyField('CommunityNeedComment')

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class CommunityNeedComment(models.Model):
    """Public comments on submitted needs."""

    need = ForeignKey(CommunityNeedSubmission, related_name='comments')
    commenter = ForeignKey(User)
    comment = TextField()
    created_at = DateTimeField(auto_now_add=True)
```

**UI/UX:**
- Simple form accessible to OBC leaders with minimal training
- Mobile-friendly (many rural areas primarily use phones)
- File upload for supporting documents (photos, MANA excerpts, petitions)
- Real-time status tracking

**Workflow:**
1. OBC leader submits need
2. OOBC staff reviews and validates
3. OOBC forwards to appropriate MAO(s)
4. MAO assesses feasibility and cost
5. Need is included in budget proposal or deferred with explanation
6. OBC leader receives notification of decision

### Feature Set 2: Quarterly Coordination Meeting Management

**User stories:**
- As OCM staff, I want to schedule quarterly meetings and track attendance
- As MAO focal person, I want to receive reminders and submit reports before meetings
- As OOBC coordinator, I want to consolidate MAO reports and identify duplication

**Technical requirements:**

**Data model extensions:**
```python
class MAOFocalPerson(models.Model):
    """Focal persons designated by MAOs for OBC coordination."""

    mao = ForeignKey('coordination.Organization')
    user = ForeignKey(User)
    role = CharField(choices=[
        ('primary', 'Primary Focal Person'),
        ('alternate', 'Alternate Focal Person'),
    ])
    is_active = BooleanField(default=True)
    designation = CharField(max_length=255)  # Official position
    contact_email = EmailField()
    contact_phone = CharField(max_length=50)
    appointed_date = DateField()

class QuarterlyCoordinationMeeting(models.Model):
    """OCM quarterly coordination meetings with MAOs."""

    meeting_date = DateField()
    quarter = CharField(max_length=2, choices=[
        ('Q1', 'Quarter 1'),
        ('Q2', 'Quarter 2'),
        ('Q3', 'Quarter 3'),
        ('Q4', 'Quarter 4'),
    ])
    fiscal_year = PositiveIntegerField()
    venue = CharField(max_length=255)
    agenda = TextField()

    # Attendance
    attendees = ManyToManyField(User, through='MeetingAttendance')

    # Outputs
    minutes = TextField(blank=True)
    decisions_made = TextField(blank=True)
    action_items = ManyToManyField('MeetingActionItem')
    attachments = ManyToManyField('coordination.EventDocument')

    # Status
    status = CharField(choices=[
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])

class MeetingActionItem(models.Model):
    """Action items from quarterly coordination meetings."""

    meeting = ForeignKey(QuarterlyCoordinationMeeting, related_name='action_items')
    description = TextField()
    responsible_mao = ForeignKey('coordination.Organization', null=True)
    responsible_person = ForeignKey(User, null=True)
    due_date = DateField()
    status = CharField(choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ])
    completion_notes = TextField(blank=True)

class MAOInterventionReport(models.Model):
    """MAO reports on interventions to OBCs, submitted quarterly."""

    meeting = ForeignKey(QuarterlyCoordinationMeeting)
    mao = ForeignKey('coordination.Organization')
    submitted_by = ForeignKey(User)

    # Intervention summary
    ppas_implemented = ManyToManyField('monitoring.MonitoringEntry')
    total_budget_allocated = DecimalField()
    total_obc_beneficiaries = PositiveIntegerField()
    regions_covered = ManyToManyField('common.Region')

    # Narrative
    accomplishments = TextField()
    challenges = TextField()
    plans_next_quarter = TextField()
    coordination_needs = TextField()  # Support needed from OOBC or other MAOs

    submitted_at = DateTimeField(auto_now_add=True)
```

**Dashboard features:**
- **Meeting calendar** showing past and upcoming quarterly meetings
- **Attendance tracker** with participation rates by MAO
- **Action item dashboard** monitoring completion of assignments
- **MAO report consolidation** aggregating interventions across agencies
- **Duplication alerts** flagging similar PPAs across different MAOs

### Feature Set 3: Menu of Services Catalog

**User stories:**
- As an OBC leader, I want to browse available programs to see what support I can access
- As an MAO planner, I want to update my agency's service catalog
- As an OOBC coordinator, I want to generate a consolidated service menu for distribution

**Technical requirements:**

**Data model extensions:**
```python
class ServiceOffering(models.Model):
    """Catalog of programs/projects/services available to OBCs."""

    # Basic info
    offering_mao = ForeignKey('coordination.Organization')
    title = CharField(max_length=255)
    description = TextField()
    category = CharField(max_length=50)  # Education, Health, Livelihood, etc.

    # Service type
    service_type = CharField(choices=[
        ('financial_assistance', 'Financial Assistance'),
        ('scholarship', 'Scholarship'),
        ('livelihood_program', 'Livelihood Program'),
        ('infrastructure_support', 'Infrastructure Support'),
        ('capacity_building', 'Capacity Building/Training'),
        ('health_service', 'Health Service'),
        ('cultural_support', 'Cultural Development Support'),
        ('other', 'Other'),
    ])

    # Eligibility and access
    eligibility_criteria = TextField()
    target_beneficiaries = TextField()  # Who can apply
    application_process = TextField()  # How to apply
    required_documents = TextField()
    processing_time = CharField(max_length=100)  # e.g., "30 days"

    # Coverage
    geographic_coverage = ManyToManyField('common.Region')
    is_nationwide = BooleanField(default=False)

    # Capacity
    annual_budget = DecimalField(null=True, blank=True)
    slots_available = PositiveIntegerField(null=True, blank=True)
    application_period = CharField(max_length=255, blank=True)  # e.g., "Year-round"

    # Performance history
    total_beneficiaries_to_date = PositiveIntegerField(default=0)
    obc_beneficiaries_to_date = PositiveIntegerField(default=0)

    # Status
    is_active = BooleanField(default=True)
    last_updated = DateTimeField(auto_now=True)

    # Links
    website_url = URLField(blank=True)
    contact_person = CharField(max_length=255, blank=True)
    contact_email = EmailField(blank=True)
    contact_phone = CharField(max_length=50, blank=True)
```

**UI/UX:**
- **Filterable catalog** (by category, MAO, region, service type)
- **Search functionality** for OBC leaders to find relevant programs
- **Service detail pages** with clear eligibility and application instructions
- **Application tracker** showing OBC's submitted applications and their status
- **Public-facing version** that can be published on OOBC website

### Feature Set 4: Policy Recommendation Tracker

**User stories:**
- As an OOBC planner, I want to track implementation of the 10 policy recommendations
- As OCM leadership, I want to see which recommendations are adequately funded
- As a policy analyst, I want to assess whether recommendations are achieving intended impacts

**Technical requirements:**

**Data model extensions:**
```python
class PolicyRecommendation(models.Model):
    """The 10 policy recommendations from Integrative Report."""

    # Identification
    number = PositiveIntegerField()  # 1-10
    title = CharField(max_length=500)
    full_text = TextField()
    category = CharField(max_length=100)

    # Strategic alignment
    related_sectors = ManyToManyField('monitoring.MonitoringEntry',
                                      limit_choices_to={'sector__isnull': False})
    target_regions = ManyToManyField('common.Region')

    # Implementation tracking
    status = CharField(choices=[
        ('proposed', 'Proposed'),
        ('endorsed', 'Endorsed by OCM'),
        ('approved', 'Approved by Parliament'),
        ('in_implementation', 'In Implementation'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
    ])

    # Resource tracking
    total_budget_allocated = DecimalField(default=0)
    total_budget_required = DecimalField(null=True, blank=True)
    funding_gap = DecimalField(null=True, blank=True)

    # Linked interventions
    implementing_ppas = ManyToManyField('monitoring.MonitoringEntry',
                                       related_name='policy_recommendations')
    implementing_maos = ManyToManyField('coordination.Organization')

    # Impact tracking
    expected_beneficiaries = PositiveIntegerField(null=True, blank=True)
    actual_beneficiaries = PositiveIntegerField(default=0)
    outcome_indicators = JSONField(default=list)  # List of indicator definitions

    # Key considerations (from the report)
    key_considerations = JSONField(default=list)  # Structured list

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class PolicyImplementationMilestone(models.Model):
    """Milestones for policy recommendation implementation."""

    policy = ForeignKey(PolicyRecommendation, related_name='milestones')
    title = CharField(max_length=255)
    description = TextField()
    target_date = DateField()
    actual_completion_date = DateField(null=True, blank=True)
    status = CharField(choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
    ])
    responsible_party = CharField(max_length=255)
    notes = TextField(blank=True)
```

**Dashboard features:**
- **Policy overview** showing all 10 recommendations with status indicators
- **Budget allocation matrix** showing which PPAs fund each recommendation
- **Gap analysis** highlighting underfunded recommendations
- **Impact scorecard** tracking beneficiaries and outcomes per recommendation
- **Timeline view** showing implementation milestones

**Pre-populated data:**
The system should come pre-loaded with the 10 recommendations:
1. Scholarships and Financial Assistance for Higher Education Learners
2. Support to OBC Madaris
3. Support to OBC Halal Enterprise Development
4. Expansion of Social Services (TABANG, AMBAG, KAPYANAN) to OBCs
5. Cultural Development Program for OBCs
6. Women and Youth Development Program
7. Tourism Development Program for OBCs
8. Infrastructure Development for OBCs
9. Increased Participation of OBCs in Governance and Development Planning
10. Institutional Partnerships and Coordination Mechanisms for OBC Development

### Feature Set 5: Multi-Year Strategic Planning

**User stories:**
- As a strategic planner, I want to create 3-5 year plans aligned with BDP
- As an MAO coordinator, I want to see how this year's budget fits into longer-term goals
- As OCM leadership, I want to assess whether we're on track with multi-year commitments

**Technical requirements:**

**Data model extensions:**
```python
class StrategicPlan(models.Model):
    """Multi-year strategic plans for OBC development."""

    title = CharField(max_length=255)
    description = TextField()

    # Time horizon
    start_year = PositiveIntegerField()
    end_year = PositiveIntegerField()

    # Alignment
    aligned_with_bdp = BooleanField(default=True)  # Bangsamoro Development Plan
    aligned_with_cm_priorities = BooleanField(default=True)  # Chief Minister priorities

    # Strategic goals
    strategic_goals = JSONField(default=list)  # List of goal objects

    # Resource envelope
    total_resource_envelope = DecimalField(null=True, blank=True)

    # Linked annual plans
    annual_plans = ManyToManyField('AnnualInvestmentPlan')

    status = CharField(choices=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ])

    created_by = ForeignKey(User, related_name='created_strategic_plans')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class AnnualInvestmentPlan(models.Model):
    """Annual Investment Plan (AIP) for a given fiscal year."""

    fiscal_year = PositiveIntegerField()
    strategic_plan = ForeignKey(StrategicPlan, null=True, related_name='annual_plans')

    # Budget totals
    total_budget = DecimalField()
    total_obc_budget = DecimalField()

    # Sector allocations
    sector_allocations = JSONField(default=dict)  # {sector: amount}

    # Funding sources
    funding_source_breakdown = JSONField(default=dict)  # {source: amount}

    # PPAs
    included_ppas = ManyToManyField('monitoring.MonitoringEntry')

    # Approval workflow
    status = CharField(choices=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('enacted', 'Enacted'),
    ])

    submitted_to_ocm = DateField(null=True, blank=True)
    approved_by_parliament = DateField(null=True, blank=True)

    document = FileField(upload_to='annual_plans/', null=True, blank=True)
```

**Dashboard features:**
- **Strategic plan tracker** showing progress across multi-year horizon
- **Annual plan comparison** comparing year-over-year allocations
- **Rolling plan manager** enabling annual updates to strategic plan
- **Resource envelope dashboard** tracking available ceilings vs. planned expenditures

### Feature Set 6: Performance-Based Budgeting Framework

**User stories:**
- As a program manager, I want to define outcome indicators for my PPA
- As an M&E officer, I want to track actual vs. planned outcomes
- As OCM leadership, I want to see which PPAs deliver best value for money

**Technical requirements:**

**Extensions to existing `MonitoringEntry` model:**
```python
# Add to MonitoringEntry
class MonitoringEntry(models.Model):
    # ... existing fields ...

    # Performance framework
    outcome_framework = JSONField(default=dict, help_text="""
        {
            "outputs": [
                {"indicator": "Number of scholars", "target": 100, "actual": 85},
                ...
            ],
            "outcomes": [
                {"indicator": "Graduation rate", "target": 90, "actual": 88},
                ...
            ],
            "impacts": [
                {"indicator": "Employment rate", "target": 75, "actual": null},
                ...
            ]
        }
    """)

    cost_per_beneficiary = DecimalField(null=True, blank=True)
    cost_effectiveness_rating = CharField(max_length=20, choices=[
        ('very_high', 'Very High'),
        ('high', 'High'),
        ('moderate', 'Moderate'),
        ('low', 'Low'),
    ], blank=True)

    # Lessons learned
    lessons_learned = TextField(blank=True)
    best_practices = TextField(blank=True)
    recommendations_for_future = TextField(blank=True)

class OutcomeIndicator(models.Model):
    """Standardized outcome indicators for common intervention types."""

    category = CharField(max_length=100)  # Education, Health, Livelihood, etc.
    indicator_name = CharField(max_length=255)
    definition = TextField()
    measurement_method = TextField()
    data_source = CharField(max_length=255)
    frequency = CharField(max_length=100)  # Annual, Quarterly, etc.

    # SDG linkage
    related_sdg = CharField(max_length=50, blank=True)

    is_active = BooleanField(default=True)
```

**Dashboard features:**
- **Outcome scorecard** showing planned vs. actual for all PPAs
- **Cost-effectiveness ranking** comparing similar interventions
- **Lessons learned repository** searchable by category, MAO, region
- **Performance trends** showing improvement over time

### Feature Set 7: Scenario Planning & Resource Optimization

**User stories:**
- As a budget planner, I want to compare different allocation scenarios
- As OCM leadership, I want to see what happens if we increase education vs. infrastructure
- As an equity analyst, I want to ensure balanced distribution across regions

**Technical requirements:**

**Data model:**
```python
class BudgetScenario(models.Model):
    """Different budget allocation scenarios for comparison."""

    fiscal_year = PositiveIntegerField()
    scenario_name = CharField(max_length=255)
    description = TextField()

    # Total envelope
    total_budget = DecimalField()

    # Allocation strategy
    allocation_strategy = CharField(choices=[
        ('needs_based', 'Needs-Based (MANA priority)'),
        ('equity_based', 'Equity-Based (Equal distribution)'),
        ('performance_based', 'Performance-Based (Past results)'),
        ('policy_based', 'Policy-Based (10 recommendations)'),
        ('custom', 'Custom'),
    ])

    # Sector allocations
    sector_allocations = JSONField(default=dict)

    # Regional allocations
    regional_allocations = JSONField(default=dict)

    # Appropriation class mix
    ps_allocation = DecimalField(default=0)
    mooe_allocation = DecimalField(default=0)
    co_allocation = DecimalField(default=0)

    # Projected outcomes
    projected_beneficiaries = PositiveIntegerField(null=True)
    projected_outcomes = JSONField(default=dict)

    # Equity metrics
    gini_coefficient = DecimalField(null=True, blank=True)  # Measure of distribution inequality
    regional_balance_score = DecimalField(null=True, blank=True)

    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
    is_approved = BooleanField(default=False)

class CeilingManagement(models.Model):
    """Budget ceilings per funding source and sector."""

    fiscal_year = PositiveIntegerField()
    funding_source = CharField(max_length=50)
    sector = CharField(max_length=50, blank=True)  # Optional: ceiling per sector

    ceiling_amount = DecimalField()
    allocated_amount = DecimalField(default=0)
    remaining_ceiling = DecimalField()

    # Alerts
    threshold_warning = DecimalField(default=0.90)  # Warn at 90% utilization
    is_exceeded = BooleanField(default=False)

    notes = TextField(blank=True)
    updated_at = DateTimeField(auto_now=True)
```

**Dashboard features:**
- **Scenario comparison matrix** showing side-by-side scenarios
- **Interactive allocation builder** allowing drag-and-drop budget adjustments
- **Ceiling monitor** with real-time alerts when approaching limits
- **Equity analyzer** showing distribution across regions, sectors, populations
- **Variance tracker** monitoring actual vs. planned expenditures

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-3)

**Goals:**
- Strengthen needs-to-budget linkage
- Implement policy recommendation tracker
- Set up MAO coordination infrastructure

**Deliverables:**
1. ✅ Extend data models for community needs, policy recommendations, MAO focal persons
2. ✅ Create policy recommendation dashboard pre-loaded with 10 recommendations
3. ✅ Build community needs submission portal (basic version)
4. ✅ Implement quarterly meeting tracker
5. ✅ Create MAO focal person registry
6. ✅ Update planning-budgeting dashboard to show policy linkages

**Success criteria:**
- All 10 policy recommendations tracked in system
- At least 3 MAOs have registered focal persons
- Community needs submission portal tested with 5 OBC communities

### Phase 2: Participation & Coordination (Months 4-6)

**Goals:**
- Enable participatory budgeting mechanisms
- Launch service catalog
- Implement performance framework

**Deliverables:**
1. ✅ Community priority voting system
2. ✅ Service offering catalog (menu of services)
3. ✅ MAO intervention reporting workflow
4. ✅ Outcome indicator framework
5. ✅ Performance scorecard dashboard
6. ✅ Duplication detection alerts

**Success criteria:**
- At least 50 service offerings cataloged from 10+ MAOs
- First participatory budgeting exercise completed with OBC representatives
- Quarterly coordination meeting workflow tested

### Phase 3: Strategic Planning & Optimization (Months 7-9)

**Goals:**
- Enable multi-year planning
- Implement scenario planning tools
- Advanced analytics and reporting

**Deliverables:**
1. ✅ Strategic plan module (3-5 year)
2. ✅ Annual Investment Plan (AIP) generator
3. ✅ Budget scenario builder
4. ✅ Ceiling management system
5. ✅ Equity analyzer
6. ✅ Cost-effectiveness ranking

**Success criteria:**
- First 3-year strategic plan created and approved
- At least 3 budget scenarios compared for upcoming fiscal year
- Ceiling management operational for all funding sources

### Phase 4: Integration & Refinement (Months 10-12)

**Goals:**
- Integrate with external systems
- Refine based on user feedback
- Full documentation and training

**Deliverables:**
1. ✅ Integration with BTMS (if applicable)
2. ✅ API for LGU/NGA coordination
3. ✅ Mobile-responsive improvements
4. ✅ Public-facing service catalog
5. ✅ Comprehensive user manuals
6. ✅ Training program for OOBC, MAOs, OBC leaders

**Success criteria:**
- System used successfully for full budget cycle
- 80%+ user satisfaction rating
- All features documented and tested

---

## Success Metrics

### Quantitative Metrics

**Planning efficiency:**
- Time to compile AIP reduced by 50%
- 100% of PPAs tagged with complete metadata
- Budget-to-disbursement cycle time reduced by 30%

**Coordination effectiveness:**
- 100% of quarterly meetings tracked in system
- 90%+ attendance rate from MAO focal persons
- 80%+ of action items completed on time

**Community participation:**
- At least 100 community needs submitted per year
- 75%+ of submitted needs reviewed within 30 days
- 50%+ of high-priority needs included in budget proposals

**Policy implementation:**
- Budget allocated to at least 8 of 10 policy recommendations
- 70%+ of policy-linked PPAs show measurable progress
- Funding gap reduced by 25% year-over-year

**Performance:**
- 80%+ of PPAs have defined outcome indicators
- 70%+ achievement rate on outcome targets
- Cost-effectiveness improved by 15% for similar interventions

### Qualitative Metrics

**Transparency:**
- Positive feedback from OBC leaders on visibility into budget process
- Reduced complaints about duplication or gaps
- Increased trust in OOBC coordination role

**Collaboration:**
- MAOs report improved coordination
- Fewer conflicting interventions
- More joint programs across agencies

**Evidence-based decision-making:**
- Budget proposals explicitly reference MANA findings
- Performance data routinely discussed in quarterly meetings
- Lessons learned inform future planning

---

## Appendices

### Appendix A: Alignment with OOBC Guidelines

| Guideline Requirement | Module Feature |
|----------------------|----------------|
| "Whole of government approach" | MAO coordination workflows, duplication detection |
| "Participatory needs assessments" | Community needs portal, priority voting |
| "Menu of programs/projects/services" | Service catalog |
| "Quarterly coordination meetings" | Meeting scheduler, MAO reports, action items |
| "Allocations based on needs assessments" | Needs-to-budget linkage, gap analysis |
| "Monitoring and evaluation system" | Performance framework, outcome scorecards |
| "Mandatory regular reports" | MAO intervention reports, automated consolidation |

### Appendix B: Alignment with 10 Policy Recommendations

All 10 recommendations will be systematically tracked:

1. **Scholarships** → Tracked as education-sector PPAs with beneficiary counts
2. **Madaris Support** → Linked to religious education indicators
3. **Halal Enterprise** → Livelihood PPAs tagged to economic indicators
4. **TABANG/AMBAG/KAPYANAN** → Social services expansion tracked by coverage
5. **Cultural Development** → Cultural PPAs with preservation indicators
6. **Women/Youth** → Demographics tracked, gender/age disaggregation
7. **Tourism** → Infrastructure + livelihood combined indicators
8. **Infrastructure** → Physical progress tracking, beneficiary access
9. **Governance Participation** → Measured by community engagement metrics
10. **Coordination Mechanisms** → MOAs/agreements, meeting frequency

### Appendix C: Technology Stack Recommendations

**Backend:**
- Django 4.2+ (already in use)
- PostgreSQL (recommended upgrade from SQLite for production)
- Celery + Redis for background tasks (scheduled reports, alerts)
- Django REST Framework for APIs

**Frontend:**
- HTMX (already in use) for dynamic interactions
- Alpine.js for lightweight interactivity
- Chart.js or D3.js for data visualizations
- Tailwind CSS (already in use) for responsive design

**Integrations:**
- Excel/CSV export (already supported via pandas)
- PDF generation for official reports (ReportLab or WeasyPrint)
- Email notifications (Django email backend)
- SMS notifications for rural OBC leaders (optional: Twilio)

**Security:**
- Role-based access control (RBAC) - already implemented
- Audit logging for all budget changes
- Data encryption at rest and in transit
- Regular backups and disaster recovery

### Appendix D: Training & Change Management

**Target audiences:**
1. **OOBC Staff** - Full system training, 3 days
2. **MAO Focal Persons** - Service catalog, reporting workflows, 1 day
3. **OBC Leaders** - Community portal, needs submission, 0.5 day
4. **OCM Leadership** - Dashboard overview, strategic planning, 0.5 day

**Training approach:**
- Hands-on workshops with test data
- Video tutorials for self-paced learning
- Quick reference guides (1-page cheat sheets)
- Ongoing help desk support

**Change management:**
- Pilot with 3-5 MAOs before full rollout
- Regular feedback sessions
- Iterative improvements based on user input
- Champions program (power users in each MAO)

---

## Conclusion

This comprehensive improvement plan transforms the OOBC Planning & Budgeting Module from a monitoring dashboard into a full-featured **Planning, Programming, and Budgeting System (PPBS)** that:

✅ Empowers OBCs to participate in budget decisions (participatory budgeting)
✅ Links community needs to budget allocations (evidence-based)
✅ Facilitates "whole of government" coordination (quarterly meetings, focal persons)
✅ Tracks the 10 policy recommendations systematically
✅ Supports multi-year strategic planning
✅ Uses performance data to improve decision-making
✅ Optimizes resource allocation across regions and sectors

By implementing these improvements, OOBC will fulfill its mandate as specified in the BOL and Guidelines, ensuring that assistance to Other Bangsamoro Communities is well-planned, well-coordinated, transparent, and effective.

---

**Next Steps:**

1. **Review & Validation**: Present this plan to OOBC leadership and key MAO partners for feedback
2. **Prioritization**: Confirm phasing and identify any features to accelerate or defer
3. **Resource Allocation**: Secure budget and personnel for development
4. **Kick-off**: Initiate Phase 1 with data model extensions and policy tracker

**Document Control:**
- Version: 1.0 Draft
- Last Updated: October 1, 2025
- Next Review: After stakeholder feedback session
