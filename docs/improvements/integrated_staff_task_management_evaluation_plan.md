# Integrated Staff Task Management: Evaluation & Implementation Plan

**Document Status**: Implementation Roadmap
**Date Created**: October 1, 2025
**Related Documents**:
- [Planning & Budgeting Implementation Evaluation](planning_budgeting_implementation_evaluation.md)
- [Integrated Calendar System Evaluation Plan](integrated_calendar_system_evaluation_plan.md)
- [Staff Task Board Research](../reports/staff_task_board_research.md)

---

## Executive Summary

This document evaluates the current codebase against the need for **integrated staff task management across all OBCMS modules**. The goal is to create a unified task management system that:

1. **Builds on existing foundations** - Leverage the well-designed `StaffTask` model in `common` app
2. **Integrates with domain workflows** - Link tasks to MANA assessments, coordination events, policies, PPAs, etc.
3. **Maintains single source of truth** - One task system across all modules
4. **Supports diverse workflows** - From simple todos to complex multi-phase processes
5. **Enables unified visibility** - Single dashboard showing all staff tasks regardless of domain

**Key Finding**: The codebase has **excellent task management foundations** (70% complete) but lacks:
- **Domain-specific task integration** (15% complete - only monitoring has MonitoringEntryTaskAssignment)
- **Unified task dashboard across modules** (30% complete - StaffTask board exists but limited)
- **Automated task generation** (0% complete - no workflow-driven task creation)
- **Task templates per workflow** (0% complete - manual task creation only)

---

## Table of Contents

1. [Existing Feature Evaluation](#existing-feature-evaluation)
2. [Module-by-Module Analysis](#module-by-module-analysis)
3. [Gap Analysis](#gap-analysis)
4. [Integration Architecture](#integration-architecture)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Technical Specifications](#technical-specifications)

---

## Existing Feature Evaluation

### Current Task Management Infrastructure

**Maturity**: 🟡 **70% Complete** - Strong foundation, needs domain integration

#### Existing Features

✅ **Core StaffTask Model** (`common/models.py:622-783`):
- Comprehensive status workflow (not_started → in_progress → at_risk → completed)
- Priority levels (low, medium, high, critical)
- Progress tracking (0-100%)
- Team assignments (many-to-many to StaffTeam)
- Assignee management (many-to-many to User)
- Due dates and completion tracking
- Kanban board positioning
- Event linkage (`linked_event` FK to coordination.Event)

✅ **MonitoringEntryTaskAssignment** (`monitoring/models.py`):
- Role-based assignments (lead, contributor, reviewer, approver, monitor)
- Status tracking (pending → in_progress → completed → blocked → cancelled)
- Estimated vs actual hours
- Notes and completion tracking
- Direct link to MonitoringEntry (PPAs)

✅ **Task Management UI** (`src/templates/common/`):
- Kanban board view (`staff_task_board.html`)
- Table view with sorting/filtering
- Task creation form (`staff_task_create.html`)
- Modal-based task editing (`partials/staff_task_modal.html`)
- HTMX-powered instant UI updates

✅ **Team Infrastructure** (`common/models.py`):
- `StaffTeam` model with focus areas
- `StaffTeamMembership` with roles (lead, coordinator, member)
- Active membership tracking

#### Missing Features

❌ **Domain-Specific Task Linking**:
- No FK from StaffTask to Assessment, Survey, Policy, Service, etc.
- Cannot track "Review MANA report for Region XII" with direct assessment link
- Cannot filter tasks by "All assessment-related tasks"

❌ **Automated Task Generation**:
- No workflow-triggered task creation
- When Assessment created, no auto-generation of "Planning", "Data Collection", "Analysis" tasks
- When Policy drafted, no auto-creation of review/approval tasks

❌ **Task Templates**:
- No pre-defined task sets per workflow
- No "MANA Assessment" template creating standard sub-tasks
- Manual task creation for repetitive workflows

❌ **Unified Task Dashboard**:
- StaffTask board doesn't show MonitoringEntryTaskAssignment tasks
- No cross-module task aggregation
- No "My Tasks Across All Domains" view

❌ **Task Dependencies**:
- No task-to-task dependency tracking
- Cannot model "Task B cannot start until Task A completes"
- No critical path analysis

❌ **Workflow Integration**:
- Tasks don't update when related entities change status
- Assessment status change doesn't update task statuses
- No bidirectional sync

---

## Module-by-Module Analysis

### 1. common App (✅ Foundation Exists)

**Maturity**: 🟢 **85% Complete**

#### Existing Features
- ✅ StaffTask model with comprehensive fields
- ✅ Kanban board and table views
- ✅ Team and assignee management
- ✅ HTMX instant UI updates

#### Integration Needs
- ⚠️ Link to TrainingEnrollment (staff development tasks)
- ⚠️ Link to StaffDevelopmentPlan (development action items)
- ⚠️ Link to PerformanceTarget (target-related tasks)

#### Recommended Actions
```python
# Extend StaffTask with:
related_training = ForeignKey('TrainingEnrollment', null=True, blank=True)
related_dev_plan = ForeignKey('StaffDevelopmentPlan', null=True, blank=True)
related_performance_target = ForeignKey('PerformanceTarget', null=True, blank=True)
```

---

### 2. communities App

**Maturity**: 🟡 **25% Complete** - Models exist, no task integration

#### Existing Workflow Patterns
- **OBCCommunity**: Soft delete workflow (active ↔ deleted)
- **MunicipalityCoverage**: Submission workflow (draft → submitted → approved → returned)
- **StakeholderEngagement**: Engagement lifecycle

#### Task Management Needs
**HIGH PRIORITY** - Community data maintenance is ongoing:

1. **Community Profile Tasks**
   - "Update demographic data for [OBCCommunity]"
   - "Verify population counts for [Barangay]"
   - "Update infrastructure data for [Community]"

2. **Stakeholder Management**
   - "Verify contact information for [Stakeholder]"
   - "Schedule engagement with [Community Leader]"
   - "Follow up on [StakeholderEngagement]"

3. **Coverage Data Tasks**
   - "Sync municipal coverage for [Municipality]"
   - "Review provincial aggregation for [Province]"
   - "Reconcile reported vs aggregated data"

#### Integration Approach
```python
# Add to StaffTask:
related_community = ForeignKey('communities.OBCCommunity', null=True, blank=True)
related_stakeholder = ForeignKey('communities.Stakeholder', null=True, blank=True)
related_engagement = ForeignKey('communities.StakeholderEngagement', null=True, blank=True)
related_municipality_coverage = ForeignKey('communities.MunicipalityCoverage', null=True, blank=True)
```

**Task Templates**:
- "Community Profile Update" → 5 standard sub-tasks
- "Stakeholder Verification" → 3 standard sub-tasks
- "Municipal Coverage Review" → 4 standard sub-tasks

---

### 3. mana App (🔴 HIGHEST PRIORITY)

**Maturity**: 🔴 **15% Complete** - Complex workflows, no task integration

#### Existing Workflow Patterns (30+ models)

**Assessment Lifecycle** (7 phases):
```
draft → planning → data_collection → analysis →
report_writing → review → completed → archived
```

**Survey Workflow**:
```
draft → active → paused → closed → archived
```

**Workshop Workflow**:
```
planned → registration_open → ongoing → completed → cancelled
```

**Baseline Study**:
```
planning → data_collection → analysis →
report_writing → review → final_report → completed
```

**Need Lifecycle**:
```
identified → validated → prioritized →
planned → in_progress → completed
```

#### Task Management Needs
**CRITICAL** - MANA has the most complex, multi-phase workflows:

**Assessment Phase Tasks**:
1. **Planning Phase**
   - "Assemble assessment team for [Assessment]"
   - "Develop assessment methodology"
   - "Prepare data collection tools"
   - "Schedule field visits"
   - "Coordinate with LGUs"

2. **Data Collection Phase**
   - "Conduct surveys in [Municipality]"
   - "Perform KII with [Stakeholder]"
   - "Facilitate FGD in [Community]"
   - "Complete mapping for [Area]"
   - "Collect baseline data for [Indicator]"

3. **Analysis Phase**
   - "Analyze survey data for [Region]"
   - "Identify needs from assessment data"
   - "Prioritize needs based on scoring"
   - "Validate findings with stakeholders"

4. **Report Writing Phase**
   - "Draft executive summary"
   - "Write methodology section"
   - "Compile findings and analysis"
   - "Create visualizations and maps"
   - "Review draft report"

5. **Review Phase**
   - "Internal review of [Report]"
   - "Incorporate stakeholder feedback"
   - "Final approval by assessment lead"

**Workshop Tasks**:
- "Prepare workshop materials for [Workshop]"
- "Facilitate [WorkshopSession]"
- "Document workshop outputs"
- "Follow up on workshop action items"

**Survey Tasks**:
- "Design survey questions"
- "Test survey in pilot site"
- "Administer [Survey] in [Municipality]"
- "Clean and validate survey data"
- "Analyze survey results"

**Needs Management Tasks**:
- "Validate identified needs"
- "Facilitate needs prioritization workshop"
- "Score and rank needs"
- "Link needs to budget proposals"

#### Integration Approach

**Option A: Comprehensive Integration** (Recommended)
```python
# Add to StaffTask:
related_assessment = ForeignKey('mana.Assessment', null=True, blank=True)
related_survey = ForeignKey('mana.Survey', null=True, blank=True)
related_workshop = ForeignKey('mana.WorkshopActivity', null=True, blank=True)
related_baseline = ForeignKey('mana.BaselineStudy', null=True, blank=True)
related_need = ForeignKey('mana.Need', null=True, blank=True)
related_mapping = ForeignKey('mana.MappingActivity', null=True, blank=True)

# Assessment-specific fields
assessment_phase = CharField(
    max_length=30,
    choices=ASSESSMENT_PHASE_CHOICES,
    blank=True,
    help_text="Which assessment phase this task supports"
)
deliverable_type = CharField(
    max_length=50,
    choices=DELIVERABLE_TYPE_CHOICES,
    blank=True,
    help_text="Expected deliverable (survey_data, analysis_report, etc.)"
)
geographic_scope = JSONField(
    default=dict,
    blank=True,
    help_text="Geographic coverage: {region, province, municipality, barangay}"
)
```

**Option B: Dedicated AssessmentTask Model**
```python
class AssessmentTask(models.Model):
    """MANA-specific task extending StaffTask functionality."""
    staff_task = OneToOneField('common.StaffTask', on_delete=CASCADE, primary_key=True)
    assessment = ForeignKey('Assessment', on_delete=CASCADE, related_name='tasks')
    phase = CharField(max_length=30, choices=ASSESSMENT_PHASE_CHOICES)
    deliverable_type = CharField(max_length=50, choices=DELIVERABLE_TYPE_CHOICES)
    geographic_scope = JSONField(default=dict)
    quality_checklist = JSONField(default=list, blank=True)

    # Relationships to specific MANA entities
    survey = ForeignKey('Survey', null=True, blank=True)
    workshop = ForeignKey('WorkshopActivity', null=True, blank=True)
    baseline = ForeignKey('BaselineStudy', null=True, blank=True)
    need = ForeignKey('Need', null=True, blank=True)
```

**Recommendation**: **Option A** for unified task management with domain-specific fields.

**Task Templates for MANA**:

**Template 1: "MANA Assessment (Full Cycle)"**
Creates 25+ standard tasks across all phases:
- 5 planning tasks
- 8 data collection tasks
- 4 analysis tasks
- 5 report writing tasks
- 3 review tasks

**Template 2: "Baseline Study"**
Creates 12 standard tasks:
- 3 planning tasks
- 5 data collection tasks
- 2 analysis tasks
- 2 reporting tasks

**Template 3: "Community Workshop"**
Creates 6 standard tasks:
- 2 preparation tasks
- 2 facilitation tasks
- 2 follow-up tasks

**Automated Task Generation**:
```python
@receiver(post_save, sender=Assessment)
def create_assessment_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when assessment created."""
    if created and instance.methodology in ['participatory', 'mixed']:
        # Create standard task set
        create_task_from_template(
            assessment=instance,
            template='mana_assessment_full_cycle'
        )
```

---

### 4. coordination App

**Maturity**: 🟡 **35% Complete** - Has Event linkage, needs expansion

#### Existing Features
- ✅ StaffTask already has `linked_event` FK to coordination.Event

#### Workflow Patterns

**Event Lifecycle**:
```
draft → published → registration_open →
ongoing → completed → cancelled
```

**Partnership Lifecycle**:
```
draft → under_negotiation → signed →
active → completed → terminated
```

**Partnership Milestone**:
```
pending → in_progress → completed → delayed → cancelled
```

**Communication Status**:
```
draft → scheduled → sent → delivered → failed
```

#### Task Management Needs

**Event Tasks** (partially covered via `linked_event`):
- "Plan [Event] for [Date]"
- "Arrange venue and logistics"
- "Coordinate participants"
- "Prepare materials and agenda"
- "Facilitate [Event]"
- "Document outputs and action items"
- "Follow up on action items"

**Partnership Tasks**:
- "Negotiate MOA with [Organization]"
- "Draft partnership agreement"
- "Review partnership terms"
- "Complete [PartnershipMilestone]"
- "Monitor partnership deliverables"
- "Prepare partnership report"

**Communication Tasks**:
- "Draft communication for [Stakeholders]"
- "Review and approve communication"
- "Schedule communication delivery"
- "Track communication responses"

**MAO Coordination Tasks**:
- "Follow up with [MAOFocalPerson]"
- "Prepare quarterly coordination meeting"
- "Review quarterly report from [Organization]"
- "Coordinate joint activity with [Organization]"

#### Integration Approach
```python
# Extend StaffTask (Event linkage already exists):
# linked_event = ForeignKey('coordination.Event')  # ✅ Already exists!

# Add additional coordination relationships:
related_organization = ForeignKey('coordination.Organization', null=True, blank=True)
related_partnership = ForeignKey('coordination.Partnership', null=True, blank=True)
related_partnership_milestone = ForeignKey('coordination.PartnershipMilestone', null=True, blank=True)
related_communication = ForeignKey('coordination.Communication', null=True, blank=True)
related_mao_focal_person = ForeignKey('coordination.MAOFocalPerson', null=True, blank=True)
```

**Task Templates**:
- "Event Planning" → 8 standard sub-tasks
- "Partnership Negotiation" → 6 standard sub-tasks
- "Quarterly Coordination Meeting" → 10 standard sub-tasks

**Automated Task Generation**:
```python
@receiver(post_save, sender=Event)
def create_event_tasks(sender, instance, created, **kwargs):
    """Auto-create event planning tasks."""
    if created and instance.event_type in ['meeting', 'workshop', 'conference']:
        create_task_from_template(
            event=instance,
            template='event_planning_standard'
        )
```

---

### 5. monitoring App

**Maturity**: 🟡 **50% Complete** - Has MonitoringEntryTaskAssignment, needs unification

#### Existing Features
- ✅ `MonitoringEntryTaskAssignment` with role-based assignments
- ✅ Status tracking (pending → in_progress → completed → blocked → cancelled)
- ✅ Hours tracking (estimated vs actual)

#### Workflow Patterns

**PPA Status**:
```
planning → ongoing → completed → on_hold → cancelled
```

**Request Status**:
```
submitted → under_review → clarification → endorsed →
approved → in_progress → completed → deferred → declined
```

**Budget Workflow Stages**:
```
budget_call → formulation → technical_hearing →
legislation → execution → accountability
```

#### Task Management Needs

**Budget Formulation Tasks**:
- "Formulate budget for [PPA] FY[Year]"
- "Prepare budget justification"
- "Review budget alignment with policies"
- "Submit budget proposal"

**Technical Hearing Tasks**:
- "Prepare presentation materials"
- "Respond to technical questions"
- "Revise budget based on feedback"

**Allocation & Disbursement Tasks**:
- "Process allocation for [PPA]"
- "Track obligation milestones"
- "Monitor disbursement flows"
- "Reconcile budget vs actual"

**Outcome Monitoring Tasks**:
- "Collect data for [OutcomeIndicator]"
- "Analyze outcome achievement"
- "Report on PPA progress"
- "Update monitoring entry"

**Strategic Planning Tasks**:
- "Develop budget scenario for [AnnualPlanningCycle]"
- "Review strategic goal progress"
- "Align PPA with strategic goals"

#### Integration Approach

**Option A: Unify with StaffTask** (Recommended)
```python
# Migrate MonitoringEntryTaskAssignment functionality into StaffTask:
# Add to StaffTask:
related_ppa = ForeignKey('monitoring.MonitoringEntry', null=True, blank=True)
related_funding_flow = ForeignKey('monitoring.MonitoringEntryFunding', null=True, blank=True)
related_workflow_stage = ForeignKey('monitoring.MonitoringEntryWorkflowStage', null=True, blank=True)
related_outcome_indicator = ForeignKey('monitoring.OutcomeIndicator', null=True, blank=True)
related_strategic_goal = ForeignKey('monitoring.StrategicGoal', null=True, blank=True)

# Add MonitoringEntryTaskAssignment fields:
task_role = CharField(
    max_length=20,
    choices=[
        ('lead', 'Lead'),
        ('contributor', 'Contributor'),
        ('reviewer', 'Reviewer'),
        ('approver', 'Approver'),
        ('monitor', 'Monitor'),
    ],
    blank=True
)
estimated_hours = DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
actual_hours = DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
```

**Option B: Keep Separate, Add Integration**
Keep MonitoringEntryTaskAssignment but link it to StaffTask:
```python
class MonitoringEntryTaskAssignment(models.Model):
    # ... existing fields ...
    staff_task = ForeignKey('common.StaffTask', null=True, blank=True)
```

**Recommendation**: **Option A** - Unify into StaffTask for single task dashboard.

**Migration Strategy**:
1. Add new fields to StaffTask
2. Create data migration: MonitoringEntryTaskAssignment → StaffTask
3. Update monitoring views to use StaffTask
4. Deprecate MonitoringEntryTaskAssignment (or keep as historical)

---

### 6. policy_tracking App

**Maturity**: 🟡 **20% Complete** - Rich workflow, no task integration

#### Workflow Patterns

**Policy Status** (11 states):
```
draft → under_review → needs_revision → submitted →
under_consideration → approved → in_implementation →
implemented

[Alternative paths: rejected, withdrawn, on_hold, expired]
```

**Milestone Status**:
```
not_started → in_progress → completed → delayed → cancelled
```

#### Task Management Needs

**Policy Drafting Tasks**:
- "Draft policy recommendation on [Topic]"
- "Collect evidence for [Policy]"
- "Research best practices for [Policy Area]"
- "Analyze stakeholder positions"

**Review & Revision Tasks**:
- "Review [Policy] by [Deadline]"
- "Incorporate feedback from [Reviewer]"
- "Revise [Policy] based on comments"
- "Validate evidence sources"

**Stakeholder Consultation Tasks**:
- "Consult [Stakeholder Group] on [Policy]"
- "Facilitate policy workshop"
- "Document consultation feedback"
- "Analyze consultation results"

**Submission & Approval Tasks**:
- "Prepare policy brief for submission"
- "Submit [Policy] to CM Office"
- "Respond to policy questions"
- "Track approval status"

**Implementation Tasks**:
- "Complete [PolicyImplementationMilestone]"
- "Monitor policy implementation"
- "Assess policy impact"
- "Report on policy outcomes"

#### Integration Approach
```python
# Add to StaffTask:
related_policy = ForeignKey('policy_tracking.PolicyRecommendation', null=True, blank=True)
related_policy_milestone = ForeignKey('policy_tracking.PolicyImplementationMilestone', null=True, blank=True)
related_policy_evidence = ForeignKey('policy_tracking.PolicyEvidence', null=True, blank=True)
related_policy_impact = ForeignKey('policy_tracking.PolicyImpact', null=True, blank=True)

# Policy-specific fields:
policy_phase = CharField(
    max_length=30,
    choices=[
        ('drafting', 'Drafting'),
        ('evidence_collection', 'Evidence Collection'),
        ('review', 'Review & Revision'),
        ('consultation', 'Stakeholder Consultation'),
        ('submission', 'Submission & Approval'),
        ('implementation', 'Implementation'),
        ('monitoring', 'Monitoring & Evaluation'),
    ],
    blank=True
)
```

**Task Templates**:
- "Policy Recommendation Development" → 15 standard tasks
- "Policy Review Cycle" → 5 standard tasks
- "Policy Implementation" → 8 standard tasks

**Automated Task Generation**:
```python
@receiver(post_save, sender=PolicyRecommendation)
def create_policy_tasks(sender, instance, created, **kwargs):
    """Auto-create policy lifecycle tasks."""
    if created:
        create_task_from_template(
            policy=instance,
            template='policy_development_full_cycle'
        )

@receiver(post_save, sender=PolicyImplementationMilestone)
def create_milestone_tasks(sender, instance, created, **kwargs):
    """Auto-create milestone delivery tasks."""
    if created:
        StaffTask.objects.create(
            title=f"Complete: {instance.title}",
            description=instance.description,
            related_policy=instance.policy,
            related_policy_milestone=instance,
            due_date=instance.target_date,
            priority='high' if instance.is_critical else 'medium',
            status='not_started',
        )
```

---

### 7. services App

**Maturity**: 🟡 **10% Complete** - New app, minimal integration

#### Workflow Patterns

**Service Offering Status**:
```
draft → active → paused → closed → archived
```

**Application Status** (10 states):
```
draft → submitted → under_review → additional_info_required →
approved → rejected → waitlisted → in_progress →
completed → cancelled
```

#### Task Management Needs

**Service Setup Tasks**:
- "Set up service offering: [ServiceOffering]"
- "Define eligibility criteria"
- "Create application template"
- "Set budget allocation for [Service]"

**Application Processing Tasks**:
- "Review application from [Applicant]"
- "Verify eligibility for [Service]"
- "Request additional information from [Applicant]"
- "Approve/reject application"

**Service Delivery Tasks**:
- "Deliver [Service] to [Beneficiary]"
- "Monitor service delivery quality"
- "Follow up with beneficiary"
- "Document service outcomes"

**Reporting Tasks**:
- "Compile service statistics for [Period]"
- "Report on [Service] performance"
- "Analyze application trends"

#### Integration Approach
```python
# Add to StaffTask:
related_service = ForeignKey('services.ServiceOffering', null=True, blank=True)
related_application = ForeignKey('services.ServiceApplication', null=True, blank=True)

# Service-specific fields:
service_phase = CharField(
    max_length=30,
    choices=[
        ('setup', 'Service Setup'),
        ('application_review', 'Application Review'),
        ('delivery', 'Service Delivery'),
        ('followup', 'Follow-up'),
        ('reporting', 'Reporting'),
    ],
    blank=True
)
```

**Task Templates**:
- "Service Offering Setup" → 6 standard tasks
- "Application Review Process" → 4 standard tasks
- "Service Delivery" → 5 standard tasks

---

### 8. municipal_profiles App

**Maturity**: 🟡 **15% Complete** - Aggregation workflows, no tasks

#### Workflow Patterns

**Profile Submission**:
```
draft → submitted → approved → returned
```

#### Task Management Needs

**Aggregation Tasks**:
- "Aggregate OBC data for [Municipality]"
- "Verify municipal profile completeness"
- "Reconcile aggregated vs reported data"

**Review Tasks**:
- "Review municipal profile for [Municipality]"
- "Approve/return municipal submission"
- "Audit data quality for [Province]"

**History Tasks**:
- "Review profile change history"
- "Investigate discrepancy in [Field]"

#### Integration Approach
```python
# Add to StaffTask:
related_municipal_profile = ForeignKey('municipal_profiles.MunicipalOBCProfile', null=True, blank=True)
```

---

### 9. data_imports App

**Maturity**: 🟡 **5% Complete** - Import workflows, no tasks

#### Workflow Patterns

**Import Status**:
```
pending → processing → completed → failed → partial → cancelled
```

#### Task Management Needs

**Import Tasks**:
- "Set up import for [DataType]"
- "Configure field mappings"
- "Validate imported data"
- "Resolve import errors"
- "Review import results"

#### Integration Approach
```python
# Add to StaffTask:
related_import = ForeignKey('data_imports.DataImport', null=True, blank=True)
```

---

### 10. ai_assistant App

**Maturity**: 🟡 **5% Complete** - Emerging functionality

#### Task Management Needs

**AI Review Tasks**:
- "Review AI-generated insight"
- "Validate AI-generated document"
- "Refine AI content for publication"

#### Integration Approach
```python
# Add to StaffTask:
related_ai_conversation = ForeignKey('ai_assistant.AIConversation', null=True, blank=True)
related_ai_document = ForeignKey('ai_assistant.AIGeneratedDocument', null=True, blank=True)
```

---

## Gap Analysis

### Critical Gaps Requiring Immediate Attention

#### Gap 1: No MANA Assessment Task Integration
**Impact**: CRITICAL - MANA is core OOBC function with complex multi-phase workflows
**Effort**: HIGH - 30+ models, multiple workflow types
**Priority**: 🔴 **Critical**

**Current State**:
- Assessments have 7-phase lifecycle
- No automated task generation when assessment created
- No task templates for standard assessment activities
- Team members manually create tasks (or forget)

**Desired State**:
- Creating Assessment → auto-generates 25+ standard tasks
- Task templates for each methodology type
- Tasks linked to specific assessment phases
- Geographic scope filtering (region, province, municipality)

**Solution**: Implement MANA task integration in Milestone 1 & 2

---

#### Gap 2: Fragmented Task Systems (StaffTask vs MonitoringEntryTaskAssignment)
**Impact**: HIGH - Staff must use different interfaces for different task types
**Effort**: MEDIUM - Data migration + view updates
**Priority**: 🔴 **Critical**

**Current State**:
- `StaffTask` for general tasks
- `MonitoringEntryTaskAssignment` for PPA tasks
- No unified "My Tasks" dashboard
- Different status models, different UIs

**Desired State**:
- Single task model across all domains
- Unified task dashboard showing all tasks
- Consistent UI/UX for all task types

**Solution**: Migrate MonitoringEntryTaskAssignment into StaffTask (Milestone 1)

---

#### Gap 3: No Automated Task Generation
**Impact**: MEDIUM - Manual overhead, inconsistent workflows
**Effort**: MEDIUM - Template system + signals
**Priority**: 🟠 **High**

**Current State**:
- All tasks created manually
- No workflow-triggered task creation
- No standard task sets per process

**Desired State**:
- Assessment created → auto-creates phase-specific tasks
- Policy drafted → auto-creates review/approval tasks
- Event scheduled → auto-creates planning/logistics tasks

**Solution**: Build task template system (Milestone 3)

---

#### Gap 4: Limited Task Filtering and Discovery
**Impact**: MEDIUM - Hard to find domain-specific tasks
**Effort**: LOW - Add filters to existing views
**Priority**: 🟡 **Medium**

**Current State**:
- Can filter by team, assignee, status
- Cannot filter by "All assessment tasks" or "All policy tasks"
- No domain-based grouping

**Desired State**:
- Filter tasks by domain (MANA, Coordination, Policy, etc.)
- Filter by related entity (Assessment, Event, Policy)
- Group tasks by workflow phase

**Solution**: Enhanced filtering UI (Milestone 2)

---

#### Gap 5: No Task Dependencies
**Impact**: MEDIUM - Cannot model sequential workflows
**Effort**: HIGH - Complex dependency tracking
**Priority**: 🟡 **Medium**

**Current State**:
- All tasks independent
- No "Task B depends on Task A" modeling
- Manual coordination of task sequences

**Desired State**:
- Define task dependencies
- Auto-update dependent task status
- Critical path visualization

**Solution**: Task dependency system (Milestone 4 - Optional)

---

## Integration Architecture

### Recommended Approach: Extended StaffTask with Domain FKs

#### Core Principle
**Single Task Model**, **Multiple Domain Relationships**, **Unified Interface**

#### Database Schema

```python
# common/models.py - Extended StaffTask
class StaffTask(models.Model):
    """Unified task model for all OBCMS domains."""

    # ========== EXISTING CORE FIELDS ==========
    title = CharField(max_length=255)
    description = TextField(blank=True)
    impact = CharField(max_length=255, blank=True)
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = CharField(max_length=12, choices=PRIORITY_CHOICES, default='medium')
    progress = PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    board_position = PositiveIntegerField(default=0)
    start_date = DateField(null=True, blank=True)
    due_date = DateField(null=True, blank=True)
    completed_at = DateTimeField(null=True, blank=True)

    # Teams & Assignments
    teams = ManyToManyField('StaffTeam', related_name='tasks', blank=True)
    assignees = ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_staff_tasks', blank=True)
    created_by = ForeignKey(settings.AUTH_USER_MODEL, related_name='created_staff_tasks', on_delete=SET_NULL, null=True, blank=True)

    # ========== DOMAIN-SPECIFIC RELATIONSHIPS ==========

    # Common App (Staff Management)
    related_training = ForeignKey('TrainingEnrollment', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_dev_plan = ForeignKey('StaffDevelopmentPlan', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_performance_target = ForeignKey('PerformanceTarget', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # Communities App
    related_community = ForeignKey('communities.OBCCommunity', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_stakeholder = ForeignKey('communities.Stakeholder', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_engagement = ForeignKey('communities.StakeholderEngagement', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_municipality_coverage = ForeignKey('communities.MunicipalityCoverage', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # MANA App
    related_assessment = ForeignKey('mana.Assessment', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_survey = ForeignKey('mana.Survey', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_workshop = ForeignKey('mana.WorkshopActivity', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_baseline = ForeignKey('mana.BaselineStudy', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_need = ForeignKey('mana.Need', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_mapping = ForeignKey('mana.MappingActivity', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # Coordination App
    linked_event = ForeignKey('coordination.Event', null=True, blank=True, on_delete=SET_NULL, related_name='staff_tasks')  # Already exists
    related_organization = ForeignKey('coordination.Organization', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_partnership = ForeignKey('coordination.Partnership', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_partnership_milestone = ForeignKey('coordination.PartnershipMilestone', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_communication = ForeignKey('coordination.Communication', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_mao_focal_person = ForeignKey('coordination.MAOFocalPerson', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # Monitoring App (from MonitoringEntryTaskAssignment)
    related_ppa = ForeignKey('monitoring.MonitoringEntry', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_funding_flow = ForeignKey('monitoring.MonitoringEntryFunding', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_workflow_stage = ForeignKey('monitoring.MonitoringEntryWorkflowStage', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_outcome_indicator = ForeignKey('monitoring.OutcomeIndicator', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_strategic_goal = ForeignKey('monitoring.StrategicGoal', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # Policy Tracking App
    related_policy = ForeignKey('policy_tracking.PolicyRecommendation', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_policy_milestone = ForeignKey('policy_tracking.PolicyImplementationMilestone', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_policy_evidence = ForeignKey('policy_tracking.PolicyEvidence', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # Services App
    related_service = ForeignKey('services.ServiceOffering', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_application = ForeignKey('services.ServiceApplication', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # Municipal Profiles App
    related_municipal_profile = ForeignKey('municipal_profiles.MunicipalOBCProfile', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # Data Imports App
    related_import = ForeignKey('data_imports.DataImport', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # AI Assistant App
    related_ai_conversation = ForeignKey('ai_assistant.AIConversation', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')
    related_ai_document = ForeignKey('ai_assistant.AIGeneratedDocument', null=True, blank=True, on_delete=SET_NULL, related_name='tasks')

    # ========== DOMAIN-SPECIFIC CATEGORIZATION ==========

    domain = CharField(
        max_length=30,
        choices=[
            ('general', 'General Staff Task'),
            ('communities', 'Community Management'),
            ('mana', 'MANA Assessment'),
            ('coordination', 'Coordination & Partnerships'),
            ('monitoring', 'Monitoring & Evaluation'),
            ('policy', 'Policy Development'),
            ('services', 'Service Delivery'),
            ('municipal', 'Municipal Profiles'),
            ('data', 'Data Management'),
            ('ai', 'AI Operations'),
        ],
        default='general',
        blank=True,
    )

    task_category = CharField(max_length=50, blank=True, help_text="Specific task type within domain")

    # ========== WORKFLOW-SPECIFIC FIELDS ==========

    # MANA-specific
    assessment_phase = CharField(
        max_length=30,
        choices=[
            ('planning', 'Planning'),
            ('data_collection', 'Data Collection'),
            ('analysis', 'Analysis'),
            ('report_writing', 'Report Writing'),
            ('review', 'Review'),
        ],
        blank=True,
    )
    deliverable_type = CharField(max_length=50, blank=True, help_text="Expected deliverable")
    geographic_scope = JSONField(default=dict, blank=True, help_text="Geographic coverage")

    # Policy-specific
    policy_phase = CharField(
        max_length=30,
        choices=[
            ('drafting', 'Drafting'),
            ('evidence_collection', 'Evidence Collection'),
            ('review', 'Review & Revision'),
            ('consultation', 'Stakeholder Consultation'),
            ('submission', 'Submission & Approval'),
            ('implementation', 'Implementation'),
            ('monitoring', 'Monitoring & Evaluation'),
        ],
        blank=True,
    )

    # Service-specific
    service_phase = CharField(
        max_length=30,
        choices=[
            ('setup', 'Service Setup'),
            ('application_review', 'Application Review'),
            ('delivery', 'Service Delivery'),
            ('followup', 'Follow-up'),
            ('reporting', 'Reporting'),
        ],
        blank=True,
    )

    # Monitoring-specific (from MonitoringEntryTaskAssignment)
    task_role = CharField(
        max_length=20,
        choices=[
            ('lead', 'Lead'),
            ('contributor', 'Contributor'),
            ('reviewer', 'Reviewer'),
            ('approver', 'Approver'),
            ('monitor', 'Monitor'),
        ],
        blank=True,
    )
    estimated_hours = DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # ========== TASK DEPENDENCIES (OPTIONAL - MILESTONE 4) ==========
    depends_on = ManyToManyField('self', symmetrical=False, related_name='dependent_tasks', blank=True)

    # ========== TEMPLATE SUPPORT ==========
    created_from_template = ForeignKey('TaskTemplate', null=True, blank=True, on_delete=SET_NULL, related_name='created_tasks')

    class Meta:
        ordering = ['board_position', 'due_date', '-priority', 'title']
        indexes = [
            models.Index(fields=['domain', 'status']),
            models.Index(fields=['related_assessment', 'assessment_phase']),
            models.Index(fields=['related_ppa', 'task_role']),
            models.Index(fields=['related_policy', 'policy_phase']),
            models.Index(fields=['linked_event']),
            models.Index(fields=['due_date', 'status']),
        ]

    @property
    def primary_domain_object(self):
        """Return the primary domain object this task is linked to."""
        for field in [
            'related_assessment', 'related_survey', 'related_workshop', 'related_baseline',
            'related_need', 'related_ppa', 'related_policy', 'linked_event',
            'related_service', 'related_community', 'related_organization',
        ]:
            obj = getattr(self, field, None)
            if obj:
                return obj
        return None

    @property
    def domain_display(self):
        """Return human-friendly domain name."""
        return dict(self._meta.get_field('domain').choices).get(self.domain, 'General')
```

---

### Task Template System

```python
# common/models.py

class TaskTemplate(models.Model):
    """Reusable task templates for workflows."""

    name = CharField(max_length=255, unique=True)
    domain = CharField(max_length=30, choices=StaffTask.domain.field.choices)
    description = TextField(blank=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['domain', 'name']

    def __str__(self):
        return f"{self.get_domain_display()}: {self.name}"


class TaskTemplateItem(models.Model):
    """Individual task item within a template."""

    template = ForeignKey(TaskTemplate, on_delete=CASCADE, related_name='items')
    title = CharField(max_length=255)
    description = TextField(blank=True)
    task_category = CharField(max_length=50, blank=True)
    priority = CharField(max_length=12, choices=StaffTask.priority.field.choices, default='medium')
    estimated_hours = DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sequence = PositiveIntegerField(default=0)
    days_from_start = PositiveIntegerField(default=0, help_text="Due date offset from parent entity start date")

    # Phase-specific fields (populated based on template domain)
    assessment_phase = CharField(max_length=30, blank=True)
    policy_phase = CharField(max_length=30, blank=True)
    service_phase = CharField(max_length=30, blank=True)
    task_role = CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['template', 'sequence']

    def __str__(self):
        return f"{self.template.name} - {self.sequence}: {self.title}"
```

---

### Automated Task Generation

```python
# common/services/task_automation.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import StaffTask, TaskTemplate
from datetime import timedelta


def create_tasks_from_template(template_name, **kwargs):
    """
    Create task set from template.

    Args:
        template_name: Name of TaskTemplate
        **kwargs: Domain-specific FK values (e.g., related_assessment=assessment_obj)

    Returns:
        List of created StaffTask objects
    """
    try:
        template = TaskTemplate.objects.get(name=template_name, is_active=True)
    except TaskTemplate.DoesNotExist:
        return []

    created_tasks = []
    base_date = kwargs.get('start_date') or timezone.now().date()

    for item in template.items.all():
        task = StaffTask.objects.create(
            title=item.title.format(**kwargs),  # Allow template variable substitution
            description=item.description.format(**kwargs),
            priority=item.priority,
            status='not_started',
            domain=template.domain,
            task_category=item.task_category,
            estimated_hours=item.estimated_hours,
            due_date=base_date + timedelta(days=item.days_from_start),
            created_from_template=template,
            # Domain-specific fields
            assessment_phase=item.assessment_phase,
            policy_phase=item.policy_phase,
            service_phase=item.service_phase,
            task_role=item.task_role,
            **kwargs  # Pass through related_* FKs
        )
        created_tasks.append(task)

    return created_tasks


# Signal handlers for automated task generation

@receiver(post_save, sender='mana.Assessment')
def create_assessment_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when MANA Assessment created."""
    if created:
        # Determine template based on methodology
        template_map = {
            'desk_review': 'mana_assessment_desk_review',
            'survey': 'mana_assessment_survey',
            'key_informant_interview': 'mana_assessment_kii',
            'focus_group_discussion': 'mana_assessment_fgd',
            'participatory': 'mana_assessment_participatory',
            'workshop': 'mana_assessment_workshop',
            'mixed': 'mana_assessment_full_cycle',
        }

        template_name = template_map.get(instance.methodology, 'mana_assessment_basic')

        create_tasks_from_template(
            template_name=template_name,
            related_assessment=instance,
            assessment_name=instance.title,
            start_date=instance.start_date,
        )


@receiver(post_save, sender='coordination.Event')
def create_event_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when Event created."""
    if created and instance.event_type in ['meeting', 'workshop', 'conference']:
        template_map = {
            'meeting': 'event_meeting_standard',
            'workshop': 'event_workshop_full',
            'conference': 'event_conference_full',
        }

        template_name = template_map.get(instance.event_type, 'event_basic')

        create_tasks_from_template(
            template_name=template_name,
            linked_event=instance,
            event_name=instance.title,
            start_date=instance.start_date or timezone.now().date(),
        )


@receiver(post_save, sender='policy_tracking.PolicyRecommendation')
def create_policy_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when Policy created."""
    if created:
        create_tasks_from_template(
            template_name='policy_development_full_cycle',
            related_policy=instance,
            policy_title=instance.title,
            start_date=timezone.now().date(),
        )


@receiver(post_save, sender='policy_tracking.PolicyImplementationMilestone')
def create_milestone_tasks(sender, instance, created, **kwargs):
    """Auto-create task when PolicyImplementationMilestone created."""
    if created:
        StaffTask.objects.create(
            title=f"Complete: {instance.title}",
            description=instance.description,
            related_policy=instance.policy,
            related_policy_milestone=instance,
            domain='policy',
            policy_phase='implementation',
            priority='high' if instance.is_critical else 'medium',
            due_date=instance.target_date,
            status='not_started',
        )


@receiver(post_save, sender='monitoring.MonitoringEntry')
def create_ppa_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when PPA created."""
    if created and instance.category in ['moa_ppa', 'oobc_ppa']:
        create_tasks_from_template(
            template_name='ppa_budget_cycle',
            related_ppa=instance,
            ppa_title=instance.title,
            start_date=instance.start_date or timezone.now().date(),
        )


@receiver(post_save, sender='services.ServiceApplication')
def create_application_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when ServiceApplication submitted."""
    if created and instance.status == 'submitted':
        StaffTask.objects.create(
            title=f"Review application: {instance.applicant_name}",
            description=f"Review service application for {instance.service.title}",
            related_service=instance.service,
            related_application=instance,
            domain='services',
            service_phase='application_review',
            priority='medium',
            due_date=timezone.now().date() + timedelta(days=7),
            status='not_started',
        )
```

---

## Implementation Roadmap

### Milestone 1: Foundation & Core Integration (Weeks 1-2)

**Goal**: Extend StaffTask with domain relationships, migrate MonitoringEntryTaskAssignment

#### 1.1 Database Schema Updates

**Model Changes**:
```python
# Add to common.StaffTask:
- All domain-specific FK fields (20+ new ForeignKeys)
- domain CharField
- task_category CharField
- assessment_phase, policy_phase, service_phase (workflow fields)
- task_role, estimated_hours, actual_hours (from MonitoringEntryTaskAssignment)
- geographic_scope JSONField
- deliverable_type CharField
```

**Migration Tasks**:
1. Create migration adding new fields to StaffTask
2. Create data migration: MonitoringEntryTaskAssignment → StaffTask
3. Update indexes for performance
4. Add database constraints

**Testing**:
- Unit tests for new fields
- Migration testing (forward and backward)
- Verify data integrity after migration

---

### Milestone 2: MANA Task Integration (Weeks 3-4)

**Goal**: Full MANA assessment task management with templates

#### 2.1 Task Template System

**New Models**:
```python
- TaskTemplate (template metadata)
- TaskTemplateItem (individual task items)
```

**Template Creation**:
1. `mana_assessment_full_cycle` (25+ tasks across all phases)
2. `mana_assessment_desk_review` (10 tasks)
3. `mana_assessment_survey` (15 tasks)
4. `mana_assessment_participatory` (20 tasks)
5. `mana_baseline_study` (12 tasks)
6. `mana_workshop_facilitation` (6 tasks)

#### 2.2 Automated Task Generation

**Signal Handlers**:
```python
@receiver(post_save, sender=Assessment)
def create_assessment_tasks(...)

@receiver(post_save, sender=BaselineStudy)
def create_baseline_tasks(...)

@receiver(post_save, sender=WorkshopActivity)
def create_workshop_tasks(...)
```

#### 2.3 MANA-Specific Views

**New Views**:
- `assessment_tasks_dashboard` - Tasks grouped by assessment phase
- `assessment_task_create` - Create assessment-specific task
- `mana_team_workload` - Team workload by assessment

**Template Updates**:
- Add "Tasks" tab to Assessment detail view
- Show task progress in Assessment list
- Phase-based task filtering

---

### Milestone 3: Coordination & Policy Integration (Weeks 5-6)

#### 3.1 Coordination Task Templates

**Templates**:
1. `event_meeting_standard` (8 tasks)
2. `event_workshop_full` (12 tasks)
3. `event_conference_full` (15 tasks)
4. `partnership_negotiation` (6 tasks)
5. `quarterly_coordination_meeting` (10 tasks)

**Signal Handlers**:
```python
@receiver(post_save, sender=Event)
def create_event_tasks(...)

@receiver(post_save, sender=Partnership)
def create_partnership_tasks(...)
```

#### 3.2 Policy Task Templates

**Templates**:
1. `policy_development_full_cycle` (15 tasks)
2. `policy_review_cycle` (5 tasks)
3. `policy_implementation` (8 tasks)

**Signal Handlers**:
```python
@receiver(post_save, sender=PolicyRecommendation)
def create_policy_tasks(...)

@receiver(post_save, sender=PolicyImplementationMilestone)
def create_milestone_tasks(...)
```

#### 3.3 Enhanced Task Dashboard

**Features**:
- Domain filtering (MANA, Coordination, Policy, etc.)
- Related entity filtering (by Assessment, Event, Policy)
- Phase-based grouping
- Geographic scope filtering
- Workload analytics by domain

---

### Milestone 4: Services & Communities Integration (Weeks 7-8)

#### 4.1 Service Task Management

**Templates**:
1. `service_offering_setup` (6 tasks)
2. `application_review_process` (4 tasks)
3. `service_delivery` (5 tasks)

**Signal Handlers**:
```python
@receiver(post_save, sender=ServiceApplication)
def create_application_tasks(...)
```

#### 4.2 Community Task Management

**Task Types**:
- Community profile updates
- Stakeholder verification
- Coverage data sync
- Engagement follow-ups

**Views**:
- `community_tasks_dashboard`
- Community detail → Tasks tab

---

### Milestone 5: Monitoring Integration (Weeks 9-10)

#### 5.1 PPA Task Templates

**Templates**:
1. `ppa_budget_cycle` (10 tasks)
2. `ppa_technical_hearing` (5 tasks)
3. `ppa_outcome_monitoring` (7 tasks)

#### 5.2 Deprecate MonitoringEntryTaskAssignment

**Migration Steps**:
1. Verify all MonitoringEntryTaskAssignment migrated
2. Update monitoring views to use StaffTask
3. Add deprecation warnings
4. Remove MonitoringEntryTaskAssignment in future release

---

### Milestone 6: Advanced Features (Weeks 11-12)

#### 6.1 Task Dependencies (Optional)

**Features**:
- `depends_on` M2M relationship
- Dependency validation
- Auto-update dependent task status
- Critical path visualization

#### 6.2 Task Analytics

**Dashboards**:
- Task completion rates by domain
- Average task duration by type
- Team workload distribution
- Overdue task trends
- Domain-specific metrics

#### 6.3 Task Automation Enhancements

**Features**:
- Task recurrence (weekly reports, monthly reviews)
- Conditional task creation (if assessment.methodology == 'survey', create survey tasks)
- Task notifications and reminders
- Task delegation workflows

---

## Technical Specifications

### Database Schema Changes

#### New Fields on StaffTask (25+ new fields)

**Domain Relationships** (18 new ForeignKeys):
```sql
ALTER TABLE common_stafftask ADD COLUMN related_training_id INT NULL;
ALTER TABLE common_stafftask ADD COLUMN related_dev_plan_id INT NULL;
ALTER TABLE common_stafftask ADD COLUMN related_performance_target_id INT NULL;
ALTER TABLE common_stafftask ADD COLUMN related_community_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_stakeholder_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_engagement_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_municipality_coverage_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_assessment_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_survey_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_workshop_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_baseline_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_need_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_mapping_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_organization_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_partnership_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_partnership_milestone_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_communication_id UUID NULL;
ALTER TABLE common_stafftask ADD COLUMN related_mao_focal_person_id UUID NULL;
-- ... (continue for all domain relationships)
```

**Categorization & Workflow Fields**:
```sql
ALTER TABLE common_stafftask ADD COLUMN domain VARCHAR(30) DEFAULT 'general';
ALTER TABLE common_stafftask ADD COLUMN task_category VARCHAR(50);
ALTER TABLE common_stafftask ADD COLUMN assessment_phase VARCHAR(30);
ALTER TABLE common_stafftask ADD COLUMN policy_phase VARCHAR(30);
ALTER TABLE common_stafftask ADD COLUMN service_phase VARCHAR(30);
ALTER TABLE common_stafftask ADD COLUMN task_role VARCHAR(20);
ALTER TABLE common_stafftask ADD COLUMN deliverable_type VARCHAR(50);
ALTER TABLE common_stafftask ADD COLUMN geographic_scope JSON;
ALTER TABLE common_stafftask ADD COLUMN estimated_hours DECIMAL(6,2);
ALTER TABLE common_stafftask ADD COLUMN actual_hours DECIMAL(6,2);
```

**Indexes**:
```sql
CREATE INDEX idx_stafftask_domain_status ON common_stafftask(domain, status);
CREATE INDEX idx_stafftask_assessment_phase ON common_stafftask(related_assessment_id, assessment_phase);
CREATE INDEX idx_stafftask_policy_phase ON common_stafftask(related_policy_id, policy_phase);
CREATE INDEX idx_stafftask_ppa_role ON common_stafftask(related_ppa_id, task_role);
CREATE INDEX idx_stafftask_event ON common_stafftask(linked_event_id);
CREATE INDEX idx_stafftask_due_status ON common_stafftask(due_date, status);
```

#### New Tables (3)

1. **TaskTemplate**
```sql
CREATE TABLE common_tasktemplate (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    domain VARCHAR(30) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

2. **TaskTemplateItem**
```sql
CREATE TABLE common_tasktemplateitem (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_category VARCHAR(50),
    priority VARCHAR(12) DEFAULT 'medium',
    estimated_hours DECIMAL(6,2),
    sequence INT DEFAULT 0,
    days_from_start INT DEFAULT 0,
    assessment_phase VARCHAR(30),
    policy_phase VARCHAR(30),
    service_phase VARCHAR(30),
    task_role VARCHAR(20),
    FOREIGN KEY (template_id) REFERENCES common_tasktemplate(id) ON DELETE CASCADE
);
```

3. **TaskDependency** (Optional - Milestone 6)
```sql
CREATE TABLE common_stafftask_depends_on (
    id INT PRIMARY KEY AUTO_INCREMENT,
    from_stafftask_id INT NOT NULL,
    to_stafftask_id INT NOT NULL,
    FOREIGN KEY (from_stafftask_id) REFERENCES common_stafftask(id) ON DELETE CASCADE,
    FOREIGN KEY (to_stafftask_id) REFERENCES common_stafftask(id) ON DELETE CASCADE,
    UNIQUE (from_stafftask_id, to_stafftask_id)
);
```

---

### View & URL Structure

#### New URL Patterns

**Task Management**:
```python
# common/urls.py additions
path('tasks/', views.staff_task_board, name='staff_task_board'),  # Already exists
path('tasks/create/', views.staff_task_create, name='staff_task_create'),  # Already exists
path('tasks/<int:pk>/', views.staff_task_detail, name='staff_task_detail'),
path('tasks/<int:pk>/edit/', views.staff_task_edit, name='staff_task_edit'),
path('tasks/<int:pk>/delete/', views.staff_task_delete, name='staff_task_delete'),

# Domain-specific task views
path('tasks/domain/<str:domain>/', views.tasks_by_domain, name='tasks_by_domain'),
path('tasks/assessment/<uuid:assessment_id>/', views.assessment_tasks, name='assessment_tasks'),
path('tasks/event/<uuid:event_id>/', views.event_tasks, name='event_tasks'),
path('tasks/policy/<uuid:policy_id>/', views.policy_tasks, name='policy_tasks'),
path('tasks/ppa/<uuid:ppa_id>/', views.ppa_tasks, name='ppa_tasks'),
path('tasks/service/<uuid:service_id>/', views.service_tasks, name='service_tasks'),

# Task analytics
path('tasks/analytics/', views.task_analytics, name='task_analytics'),
path('tasks/analytics/domain/<str:domain>/', views.domain_task_analytics, name='domain_task_analytics'),
```

**Template Management**:
```python
# common/urls.py additions
path('task-templates/', views.task_template_list, name='task_template_list'),
path('task-templates/create/', views.task_template_create, name='task_template_create'),
path('task-templates/<int:pk>/', views.task_template_detail, name='task_template_detail'),
path('task-templates/<int:pk>/edit/', views.task_template_edit, name='task_template_edit'),
```

---

### API Endpoints

**Task API**:
```python
# common/api_urls.py
GET    /api/v1/tasks/                           # List all tasks (with filtering)
POST   /api/v1/tasks/                           # Create task
GET    /api/v1/tasks/{id}/                      # Task detail
PATCH  /api/v1/tasks/{id}/                      # Update task
DELETE /api/v1/tasks/{id}/                      # Delete task

# Domain-specific filtering
GET    /api/v1/tasks/?domain=mana               # MANA tasks
GET    /api/v1/tasks/?assessment={uuid}         # Assessment tasks
GET    /api/v1/tasks/?event={uuid}              # Event tasks
GET    /api/v1/tasks/?policy={uuid}             # Policy tasks
GET    /api/v1/tasks/?ppa={uuid}                # PPA tasks

# Task actions
POST   /api/v1/tasks/{id}/complete/             # Mark complete
POST   /api/v1/tasks/{id}/start/                # Start task
POST   /api/v1/tasks/{id}/assign/               # Assign to user/team

# Template API
GET    /api/v1/task-templates/                  # List templates
POST   /api/v1/task-templates/                  # Create template
GET    /api/v1/task-templates/{id}/             # Template detail
POST   /api/v1/task-templates/{id}/instantiate/ # Create tasks from template

# Analytics API
GET    /api/v1/tasks/analytics/summary/         # Overall stats
GET    /api/v1/tasks/analytics/by-domain/       # Stats by domain
GET    /api/v1/tasks/analytics/by-team/         # Stats by team
GET    /api/v1/tasks/analytics/by-assignee/     # Stats by assignee
```

---

### Performance Considerations

#### Database Optimization

**Query Optimization**:
```python
# Use select_related for FK lookups
tasks = StaffTask.objects.select_related(
    'related_assessment',
    'related_assessment__lead_facilitator',
    'related_policy',
    'related_ppa',
    'linked_event',
    'created_by',
).prefetch_related(
    'assignees',
    'teams',
)

# Domain-specific filtering with indexes
mana_tasks = tasks.filter(domain='mana', status='in_progress').order_by('due_date')
```

**Aggregation Queries**:
```python
from django.db.models import Count, Q, Avg

# Task stats by domain
domain_stats = StaffTask.objects.values('domain').annotate(
    total=Count('id'),
    completed=Count('id', filter=Q(status='completed')),
    in_progress=Count('id', filter=Q(status='in_progress')),
    overdue=Count('id', filter=Q(due_date__lt=timezone.now().date(), status__in=['not_started', 'in_progress'])),
)

# Average hours by domain
hours_by_domain = StaffTask.objects.values('domain').annotate(
    avg_estimated=Avg('estimated_hours'),
    avg_actual=Avg('actual_hours'),
)
```

#### Caching Strategy

```python
from django.core.cache import cache

def get_task_dashboard_data(user):
    """Get cached dashboard data."""
    cache_key = f'task_dashboard_{user.id}'
    data = cache.get(cache_key)

    if not data:
        data = {
            'my_tasks': StaffTask.objects.filter(assignees=user),
            'team_tasks': StaffTask.objects.filter(teams__memberships__user=user),
            'domain_stats': compute_domain_stats(user),
            'upcoming_deadlines': get_upcoming_deadlines(user),
        }
        cache.set(cache_key, data, timeout=300)  # 5 minutes

    return data

# Invalidate cache when tasks updated
@receiver(post_save, sender=StaffTask)
def invalidate_task_cache(sender, instance, **kwargs):
    """Invalidate cached task data when task updated."""
    for assignee in instance.assignees.all():
        cache.delete(f'task_dashboard_{assignee.id}')
```

---

## Success Criteria

### Quantitative Metrics

**Task Management Adoption**:
- ✅ 90%+ of MANA assessments have auto-generated task sets
- ✅ 80%+ of coordination events have linked tasks
- ✅ 70%+ of policies have task tracking from draft to implementation
- ✅ 100% of PPAs migrated from MonitoringEntryTaskAssignment to StaffTask

**Task Completion Rates**:
- ✅ 75%+ task completion rate within due dates
- ✅ 60%+ of tasks completed with actual_hours tracking
- ✅ 50%+ reduction in overdue tasks after template implementation

**System Integration**:
- ✅ Zero duplicate task systems (MonitoringEntryTaskAssignment deprecated)
- ✅ Single unified task dashboard used by 100% of staff
- ✅ 10+ task templates created covering major workflows

### Qualitative Metrics

**User Satisfaction**:
- ✅ Positive feedback from staff on unified task interface
- ✅ Reduced complaints about "too many systems"
- ✅ Increased visibility into team workloads

**Process Efficiency**:
- ✅ Reduced manual task creation overhead (templates automate)
- ✅ Better workflow compliance (standard task sets ensure steps not skipped)
- ✅ Improved coordination (clear task assignments prevent duplication)

---

## Conclusion

### Summary of Findings

The OBCMS has **strong task management foundations** in `StaffTask` but requires **domain-specific integration** to support the full breadth of OOBC operations.

**Strengths**:
- ✅ Well-designed StaffTask model with teams, assignees, progress tracking
- ✅ Kanban board and table views with HTMX instant UI
- ✅ Existing MonitoringEntryTaskAssignment shows demand for PPA task tracking

**Gaps Addressed by This Plan**:
- ✅ Domain-specific task linking (MANA, Coordination, Policy, Services, etc.)
- ✅ Automated task generation via templates
- ✅ Unified task dashboard across all modules
- ✅ Phase-based task organization (assessment phases, policy phases, etc.)
- ✅ Workflow integration (task status tied to domain entity status)

### Implementation Philosophy

This plan emphasizes **extending, not replacing**:

1. **Single Task Model**: Extend StaffTask rather than creating separate task models per domain
2. **Opt-In Automation**: Templates are optional; manual task creation still supported
3. **Gradual Migration**: Start with MANA (highest impact), expand to other domains
4. **Backward Compatibility**: Existing tasks continue to work; new fields are nullable
5. **Performance First**: Indexes, caching, and query optimization from Day 1

### Next Steps

1. **Review & Approval**: Present this plan to OOBC leadership and development team
2. **Prioritization**: Confirm milestone sequencing based on urgency and resources
3. **Sprint Planning**: Break Milestone 1 into 2-week sprints
4. **Kickoff**: Begin with database schema updates and MANA integration
5. **Iterative Delivery**: Deploy features incrementally, gather feedback, iterate

---

## Implementation Checklist: 39 Actionable Tasks

### Milestone 1: Foundation & Core Integration (Tasks 1-7)

**Database Schema**
- [ ] **Task 1**: Create database migration adding domain FK fields to StaffTask (20+ new ForeignKeys for communities, MANA, coordination, monitoring, policy, services, municipal_profiles, data_imports, ai_assistant apps)
- [ ] **Task 2**: Add domain categorization fields to StaffTask model (domain CharField, task_category, assessment_phase, policy_phase, service_phase, task_role, deliverable_type, geographic_scope JSONField, estimated_hours, actual_hours)
- [ ] **Task 3**: Create TaskTemplate model with fields: name, domain, description, is_active, timestamps
- [ ] **Task 4**: Create TaskTemplateItem model with fields: template FK, title, description, task_category, priority, estimated_hours, sequence, days_from_start, phase fields
- [ ] **Task 5**: Add database indexes for performance (domain+status, assessment+phase, policy+phase, ppa+role, event, due_date+status)
- [ ] **Task 6**: Create data migration to migrate MonitoringEntryTaskAssignment records to StaffTask
- [ ] **Task 7**: Add created_from_template FK field to StaffTask and depends_on M2M for task dependencies

### Milestone 2: Task Automation System (Tasks 8-12)

**Automation Service & Signal Handlers**
- [ ] **Task 8**: Implement task automation service (create_tasks_from_template function in common/services/task_automation.py)
- [ ] **Task 9**: Create signal handlers for MANA Assessment automated task generation (@receiver for Assessment, BaselineStudy, WorkshopActivity)
- [ ] **Task 10**: Create signal handlers for Coordination Event automated task generation (@receiver for Event, Partnership)
- [ ] **Task 11**: Create signal handlers for Policy automated task generation (@receiver for PolicyRecommendation, PolicyImplementationMilestone)
- [ ] **Task 12**: Create signal handlers for Services and Monitoring automated task generation (@receiver for ServiceApplication, MonitoringEntry)

### Milestone 3: Task Templates (Tasks 13-17)

**Template Data Creation**
- [ ] **Task 13**: Create MANA task templates: mana_assessment_full_cycle (25+ tasks), mana_assessment_desk_review (10 tasks), mana_assessment_survey (15 tasks), mana_assessment_participatory (20 tasks), mana_baseline_study (12 tasks), mana_workshop_facilitation (6 tasks)
- [ ] **Task 14**: Create Coordination task templates: event_meeting_standard (8 tasks), event_workshop_full (12 tasks), event_conference_full (15 tasks), partnership_negotiation (6 tasks), quarterly_coordination_meeting (10 tasks)
- [ ] **Task 15**: Create Policy task templates: policy_development_full_cycle (15 tasks), policy_review_cycle (5 tasks), policy_implementation (8 tasks)
- [ ] **Task 16**: Create Services task templates: service_offering_setup (6 tasks), application_review_process (4 tasks), service_delivery (5 tasks)
- [ ] **Task 17**: Create Monitoring PPA task templates: ppa_budget_cycle (10 tasks), ppa_technical_hearing (5 tasks), ppa_outcome_monitoring (7 tasks)

### Milestone 4: Views & UI Integration (Tasks 18-24)

**View Layer**
- [ ] **Task 18**: Create domain-specific task views: tasks_by_domain, assessment_tasks, event_tasks, policy_tasks, ppa_tasks, service_tasks
- [ ] **Task 19**: Enhance task dashboard with domain filtering, related entity filtering, phase-based grouping, geographic scope filtering
- [ ] **Task 20**: Add task analytics views: task_analytics, domain_task_analytics with stats by domain, team, assignee
- [ ] **Task 21**: Create task template management views: task_template_list, task_template_create, task_template_detail, task_template_edit
- [ ] **Task 22**: Add Tasks tab to Assessment detail view showing assessment-specific tasks grouped by phase
- [ ] **Task 23**: Add Tasks tab to Event detail view showing event-specific tasks
- [ ] **Task 24**: Add Tasks tab to PolicyRecommendation detail view showing policy-specific tasks grouped by phase
- [ ] **Task 25**: Update monitoring views to use StaffTask instead of MonitoringEntryTaskAssignment

### Milestone 5: API Development (Tasks 26-28)

**API Endpoints**
- [ ] **Task 26**: Create API endpoints for task management: list/create/detail/update/delete with domain filtering, task actions (complete/start/assign)
- [ ] **Task 27**: Create API endpoints for task templates: list/create/detail and instantiate endpoint to create tasks from template
- [ ] **Task 28**: Create API endpoints for task analytics: summary, by-domain, by-team, by-assignee

### Milestone 6: Performance & Code Quality (Tasks 29-35)

**Optimization & Testing**
- [ ] **Task 29**: Implement query optimization with select_related/prefetch_related for task FK lookups
- [ ] **Task 30**: Implement caching strategy for task dashboard data with cache invalidation on task updates
- [ ] **Task 31**: Add @property methods to StaffTask: primary_domain_object, domain_display
- [ ] **Task 32**: Update StaffTask admin interface to support all new domain-specific fields and filtering
- [ ] **Task 33**: Create unit tests for new StaffTask fields, task templates, and automated task generation
- [ ] **Task 34**: Create integration tests for signal handlers and task automation workflows
- [ ] **Task 35**: Test migration forward and backward compatibility, verify data integrity

### Milestone 7: Advanced Features (Optional) (Tasks 36-39)

**Optional Enhancements**
- [ ] **Task 36**: Add task dependency M2M relationship (depends_on) with validation and auto-update logic
- [ ] **Task 37**: Create task recurrence feature for weekly reports and monthly reviews
- [ ] **Task 38**: Add task notifications and reminders system
- [ ] **Task 39**: Create deprecation plan for MonitoringEntryTaskAssignment with warnings and migration guide

### Final Task

**Documentation**
- [ ] **Task 40**: Update documentation with task management integration guide and API reference

---

**Document Version**: 1.0
**Last Updated**: October 1, 2025
**Next Review**: After Milestone 2 completion
**Implementation Started**: October 1, 2025
