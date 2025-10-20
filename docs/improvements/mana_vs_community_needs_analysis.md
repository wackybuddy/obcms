# MANA vs. Community Needs: Analysis & Recommended Approach

**Document Status**: Critical Design Decision
**Date Created**: October 1, 2025
**Issue**: Potential conflict between MANA `Need` model and proposed `CommunityNeedSubmission` model

---

## The Problem

The [Planning & Budgeting Implementation Evaluation](planning_budgeting_implementation_evaluation.md) proposed creating a `CommunityNeedSubmission` model for participatory budgeting. However, **MANA already has a comprehensive `Need` model** (`mana/models.py:866-1016`).

**Creating a separate model could result in**:
- ❌ Data duplication
- ❌ Confusion about which model to use when
- ❌ Inconsistent need tracking
- ❌ Integration complexity

---

## Existing MANA `Need` Model Analysis

### What MANA `Need` Already Has ✅

**Excellent Coverage**:
```python
class Need(models.Model):
    # Core Fields
    title = CharField(max_length=200)
    description = TextField()
    category = ForeignKey(NeedsCategory)
    assessment = ForeignKey(Assessment)  # Links to formal MANA assessment
    community = ForeignKey(OBCCommunity)

    # Impact Metrics
    affected_population = IntegerField()
    affected_households = IntegerField(null=True)
    geographic_scope = TextField()

    # Prioritization (ALREADY BUILT IN!)
    urgency_level = CharField(choices=URGENCY_LEVELS)  # immediate, short_term, medium_term, long_term
    impact_severity = IntegerField(1-5 scale)
    feasibility = CharField(choices=FEASIBILITY_LEVELS)  # very_low → very_high
    estimated_cost = DecimalField()
    priority_score = DecimalField()  # Calculated priority
    priority_rank = IntegerField()  # Ranking within community

    # Validation Workflow (ALREADY BUILT IN!)
    status = CharField(choices=[
        'identified',
        'validated',
        'prioritized',
        'planned',          # ← Ready for budget inclusion
        'in_progress',      # ← Implementation started
        'completed',
        'deferred',
        'rejected'
    ])
    is_validated = BooleanField()
    validated_by = ForeignKey(User)
    validation_date = DateTimeField()

    # Evidence
    evidence_sources = TextField()
    validation_method = CharField()

    # Metadata
    identified_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
```

### What MANA `Need` is Missing ❌

**For Participatory Budgeting Workflow**:
- ❌ No "submitted by community leader" field (currently requires staff to create via Assessment)
- ❌ No community voting/ranking mechanism
- ❌ No "forwarded to MAO" tracking
- ❌ No link to `MonitoringEntry` (which PPA addresses this need)
- ❌ No workflow for community-initiated needs (outside formal Assessment process)

---

## The Two Types of Needs

After analysis, there are **two distinct pathways** for needs to enter the system:

### Pathway 1: MANA Assessment-Driven (FORMAL)
**Process**:
1. OOBC conducts formal MANA Assessment
2. Assessors identify needs during workshops/surveys
3. Needs validated by OOBC staff
4. Needs prioritized using scoring system
5. Needs inform budget proposals

**Use Case**: Regional/provincial MANA workshops, systematic baseline studies

**Current Model**: ✅ `mana.Need` (perfect fit)

---

### Pathway 2: Community-Initiated Requests (INFORMAL/AD-HOC)
**Process**:
1. OBC leader/community member identifies urgent need
2. Submits request via online portal (outside formal Assessment cycle)
3. OOBC reviews and may link to existing Assessment data
4. OOBC forwards to appropriate MAO
5. If funded, becomes a `MonitoringEntry`

**Use Case**: Ongoing community engagement, urgent needs arising between MANA cycles

**Current Model**: ❌ No model exists (but should we create one?)

---

## Three Possible Solutions

### Option 1: Extend MANA `Need` Model (RECOMMENDED ✅)

**Approach**: Add fields to existing `mana.Need` to support both pathways

**Changes to `Need` Model**:
```python
# Add to mana.Need
class Need(models.Model):
    # ... existing fields ...

    # PATHWAY TRACKING
    submission_type = models.CharField(
        max_length=20,
        choices=[
            ('assessment_driven', 'Identified During Assessment'),
            ('community_submitted', 'Community-Submitted'),
        ],
        default='assessment_driven',
        help_text="How this need entered the system"
    )

    # COMMUNITY SUBMISSION FIELDS (for pathway 2)
    submitted_by_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='community_submitted_needs',
        help_text="Community leader/member who submitted (if community-initiated)"
    )

    submission_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when community submitted this need"
    )

    # PARTICIPATORY BUDGETING
    community_votes = models.PositiveIntegerField(
        default=0,
        help_text="Number of community votes received (participatory budgeting)"
    )

    # COORDINATION WORKFLOW
    forwarded_to_mao = models.ForeignKey(
        'coordination.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forwarded_needs',
        help_text="MAO this need was forwarded to"
    )

    forwarded_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when forwarded to MAO"
    )

    forwarded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forwarded_needs',
        help_text="OOBC staff who forwarded to MAO"
    )

    # BUDGET LINKAGE
    linked_ppa = models.ForeignKey(
        'monitoring.MonitoringEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addressing_needs',
        help_text="PPA that addresses this need"
    )

    budget_inclusion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when included in budget/PPA"
    )
```

**Also Add to `MonitoringEntry`**:
```python
# Add to monitoring.MonitoringEntry
needs_addressed = models.ManyToManyField(
    'mana.Need',
    blank=True,
    related_name='implementing_ppas',
    help_text="Community needs this PPA addresses"
)
```

**Pros**:
- ✅ Single source of truth for all needs
- ✅ Reuses MANA's excellent prioritization framework
- ✅ No data duplication
- ✅ Easy to link Assessment-driven needs to Community-submitted needs
- ✅ Consistent reporting (all needs in one model)
- ✅ Simple integration with existing workflows

**Cons**:
- ⚠️ `assessment` field becomes optional (null=True) for community-submitted needs
- ⚠️ Model becomes more complex (but manageable)

---

### Option 2: Create Separate `CommunityNeedSubmission` Model (NOT RECOMMENDED ❌)

**Approach**: Keep MANA `Need` for assessments, create new model for community requests

**Pros**:
- ✅ Clear separation of concerns
- ✅ MANA model stays focused

**Cons**:
- ❌ Data duplication (what if community submits need that was already identified in MANA?)
- ❌ Two different prioritization systems
- ❌ Confusing: which model to link to `MonitoringEntry`?
- ❌ Harder to generate unified reports
- ❌ Need to sync data between two models

**Verdict**: Not recommended due to complexity and duplication

---

### Option 3: Create Lightweight `NeedSubmissionRequest` Model (HYBRID)

**Approach**: Create minimal model for initial submission, then convert to MANA `Need`

**Process**:
1. Community submits via `NeedSubmissionRequest` (simple form)
2. OOBC reviews
3. If validated, system creates/links to MANA `Need`
4. Original submission archived for audit trail

**Changes**:
```python
# New lightweight model
class NeedSubmissionRequest(models.Model):
    """Initial community need submission before conversion to formal Need."""

    submitted_by_community = ForeignKey('communities.OBCCommunity')
    submitted_by_user = ForeignKey(User)
    title = CharField(max_length=255)
    description = TextField()
    category = CharField(max_length=50)  # Simple category, not FK
    estimated_beneficiaries = PositiveIntegerField()
    estimated_cost = DecimalField(null=True)
    supporting_evidence = TextField(blank=True)

    status = CharField(choices=[
        ('pending_review', 'Pending OOBC Review'),
        ('approved', 'Approved - Converted to Need'),
        ('rejected', 'Rejected'),
        ('merged', 'Merged with Existing Need'),
    ])

    # After approval
    converted_to_need = ForeignKey('mana.Need', null=True, on_delete=models.SET_NULL)

    submitted_at = DateTimeField(auto_now_add=True)
    reviewed_by = ForeignKey(User, null=True, related_name='reviewed_submissions')
    reviewed_at = DateTimeField(null=True)
```

**Pros**:
- ✅ Simple intake form for communities (fewer required fields)
- ✅ MANA `Need` stays focused on validated needs
- ✅ Clear approval workflow
- ✅ Audit trail of all submissions (even rejected ones)

**Cons**:
- ⚠️ Additional model to maintain
- ⚠️ Conversion logic needed
- ⚠️ Risk of submissions staying in limbo if not converted

---

## Recommended Approach: **Option 1 (Extend MANA `Need`)**

### Rationale

1. **Single Source of Truth**: All needs (formal or informal) tracked in one place
2. **Reuse Existing Infrastructure**: MANA's prioritization system is excellent
3. **Simplified Integration**: MonitoringEntry.needs_addressed links to one model
4. **Flexible Workflow**: Status field already supports full lifecycle
5. **Reporting Efficiency**: Unified reports showing all needs

### Implementation Plan

#### Phase 1: Extend `Need` Model

**File**: `src/mana/models.py`

```python
# Add to Need model (around line 1011)

# PATHWAY TRACKING
submission_type = models.CharField(
    max_length=20,
    choices=[
        ('assessment_driven', 'Identified During Assessment'),
        ('community_submitted', 'Community-Submitted'),
    ],
    default='assessment_driven',
)

# COMMUNITY SUBMISSION
submitted_by_user = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='community_submitted_needs',
)

submission_date = models.DateField(null=True, blank=True)

# PARTICIPATORY BUDGETING
community_votes = models.PositiveIntegerField(default=0)

# COORDINATION
forwarded_to_mao = models.ForeignKey(
    'coordination.Organization',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='forwarded_needs',
)

forwarded_date = models.DateField(null=True, blank=True)
forwarded_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='forwarded_needs',
)

# BUDGET LINKAGE
linked_ppa = models.ForeignKey(
    'monitoring.MonitoringEntry',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='addressing_needs',
)

budget_inclusion_date = models.DateField(null=True, blank=True)
```

**Also change**:
```python
# Change Need.assessment to allow NULL for community-submitted needs
assessment = models.ForeignKey(
    Assessment,
    on_delete=models.CASCADE,
    related_name="identified_needs",
    null=True,  # ← ADD THIS
    blank=True,  # ← ADD THIS
    help_text="Assessment that identified this need (if assessment-driven)",
)
```

#### Phase 2: Add Reverse Relationship to `MonitoringEntry`

**File**: `src/monitoring/models.py`

```python
# Add to MonitoringEntry model

needs_addressed = models.ManyToManyField(
    'mana.Need',
    blank=True,
    related_name='implementing_ppas',
    help_text="Community needs this PPA addresses"
)
```

#### Phase 3: Create Community Submission Views

**New Views** (`src/mana/views.py` or new `src/mana/views/community_needs.py`):

1. `community_need_submit` - Simple form for OBC leaders
2. `community_need_list` - Community dashboard showing their submitted needs
3. `oobc_need_review_queue` - OOBC staff review pending community needs
4. `oobc_need_forward_to_mao` - Forward need to MAO
5. `need_gap_analysis` - Dashboard showing unfunded needs

**Forms** (`src/mana/forms.py`):

```python
class CommunityNeedSubmissionForm(forms.ModelForm):
    """Simplified form for community leaders to submit needs."""

    class Meta:
        model = Need
        fields = [
            'title',
            'description',
            'category',
            'affected_population',
            'affected_households',
            'geographic_scope',
            'urgency_level',
            'estimated_cost',
            'evidence_sources',
        ]

    def __init__(self, *args, **kwargs):
        self.community = kwargs.pop('community', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        need = super().save(commit=False)
        need.submission_type = 'community_submitted'
        need.submitted_by_user = self.user
        need.community = self.community
        need.submission_date = timezone.now().date()
        need.status = 'identified'  # Starts as identified, pending validation
        need.identified_by = self.user
        if commit:
            need.save()
        return need
```

#### Phase 4: Update MANA Admin

**File**: `src/mana/admin.py`

Add filters and list display to easily distinguish:
- Assessment-driven vs. community-submitted needs
- Forwarded vs. not forwarded
- Funded (linked_ppa) vs. unfunded

```python
@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'community',
        'submission_type',  # NEW
        'status',
        'priority_score',
        'forwarded_to_mao',  # NEW
        'linked_ppa',  # NEW
    ]

    list_filter = [
        'submission_type',  # NEW
        'status',
        'urgency_level',
        'category',
        ('forwarded_to_mao', admin.RelatedOnlyFieldListFilter),  # NEW
    ]

    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'description', 'category', 'community']
        }),
        ('Submission Details', {  # NEW SECTION
            'fields': [
                'submission_type',
                'assessment',
                'submitted_by_user',
                'submission_date',
            ]
        }),
        ('Impact & Scope', {
            'fields': [
                'affected_population',
                'affected_households',
                'geographic_scope',
            ]
        }),
        ('Prioritization', {
            'fields': [
                'urgency_level',
                'impact_severity',
                'feasibility',
                'estimated_cost',
                'priority_score',
                'priority_rank',
            ]
        }),
        ('Workflow', {  # NEW SECTION
            'fields': [
                'status',
                'forwarded_to_mao',
                'forwarded_date',
                'forwarded_by',
            ]
        }),
        ('Budget Linkage', {  # NEW SECTION
            'fields': [
                'linked_ppa',
                'budget_inclusion_date',
            ]
        }),
        ('Validation', {
            'fields': [
                'is_validated',
                'validated_by',
                'validation_date',
                'evidence_sources',
                'validation_method',
            ]
        }),
    ]
```

#### Phase 5: Create Integration Workflow

**Workflow for Community-Submitted Needs**:

```
1. OBC Leader logs in
   ↓
2. Submits need via form (CommunityNeedSubmissionForm)
   → Creates Need with submission_type='community_submitted'
   → status='identified'
   ↓
3. OOBC Staff reviews in queue
   → Validates evidence
   → May link to existing Assessment (if related)
   → status='validated'
   ↓
4. OOBC Staff prioritizes
   → Calculates priority_score
   → Sets priority_rank
   → status='prioritized'
   ↓
5. OOBC Staff forwards to MAO
   → Sets forwarded_to_mao
   → Sets forwarded_date
   ↓
6. MAO creates PPA (MonitoringEntry)
   → MonitoringEntry.needs_addressed.add(need)
   → Need.linked_ppa = monitoring_entry
   → Need.status='planned'
   ↓
7. Implementation begins
   → Need.status='in_progress'
   ↓
8. Implementation completed
   → Need.status='completed'
```

---

## Migration Strategy

### Step 1: Database Migration

```python
# migrations/0XXX_add_community_submission_fields.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('mana', '0XXX_previous_migration'),
        ('coordination', '0XXX_organization_migration'),
        ('monitoring', '0XXX_monitoring_entry_migration'),
    ]

    operations = [
        # Make assessment nullable
        migrations.AlterField(
            model_name='need',
            name='assessment',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='identified_needs',
                to='mana.assessment'
            ),
        ),

        # Add new fields
        migrations.AddField(
            model_name='need',
            name='submission_type',
            field=models.CharField(
                choices=[
                    ('assessment_driven', 'Identified During Assessment'),
                    ('community_submitted', 'Community-Submitted')
                ],
                default='assessment_driven',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='need',
            name='submitted_by_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='community_submitted_needs',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='need',
            name='submission_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='need',
            name='community_votes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='need',
            name='forwarded_to_mao',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='forwarded_needs',
                to='coordination.organization'
            ),
        ),
        migrations.AddField(
            model_name='need',
            name='forwarded_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='need',
            name='forwarded_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='forwarded_needs',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='need',
            name='linked_ppa',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='addressing_needs',
                to='monitoring.monitoringentry'
            ),
        ),
        migrations.AddField(
            model_name='need',
            name='budget_inclusion_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
```

### Step 2: Data Migration (Optional)

If there are existing needs that should be marked as assessment_driven:

```python
# migrations/0XXX_set_existing_needs_as_assessment_driven.py

from django.db import migrations

def set_submission_type(apps, schema_editor):
    Need = apps.get_model('mana', 'Need')
    Need.objects.all().update(submission_type='assessment_driven')

class Migration(migrations.Migration):

    dependencies = [
        ('mana', '0XXX_add_community_submission_fields'),
    ]

    operations = [
        migrations.RunPython(set_submission_type, reverse_code=migrations.RunPython.noop),
    ]
```

---

## Comparison: Before vs. After

### BEFORE (Assessment-Only)

```
Assessment (MANA Workshop)
    ↓
  Need identified by assessor
    ↓
  Need validated
    ↓
  Need prioritized
    ↓
  ??? (no clear path to budget)
```

### AFTER (Two Pathways, One Model)

```
PATHWAY 1: Assessment-Driven
============================
Assessment (MANA)
    ↓
  Need (submission_type='assessment_driven')
    ↓
  Validated & Prioritized
    ↓
  Forwarded to MAO
    ↓
  MonitoringEntry created
    ↓
  Need.linked_ppa set


PATHWAY 2: Community-Submitted
===============================
OBC Leader submits
    ↓
  Need (submission_type='community_submitted')
    ↓
  OOBC validates (may link to Assessment)
    ↓
  OOBC prioritizes
    ↓
  Forwarded to MAO
    ↓
  MonitoringEntry created
    ↓
  Need.linked_ppa set
```

**Both pathways converge at the same model with the same budget integration!**

---

## Benefits of This Approach

### 1. Unified Reporting
```sql
-- All unfunded high-priority needs (regardless of pathway)
SELECT * FROM mana_need
WHERE priority_score > 4.0
  AND linked_ppa IS NULL
  AND status NOT IN ('deferred', 'rejected', 'completed')
ORDER BY priority_score DESC;

-- MAO performance: needs forwarded vs. needs funded
SELECT
    forwarded_to_mao.name,
    COUNT(*) as total_forwarded,
    COUNT(linked_ppa) as total_funded,
    (COUNT(linked_ppa)::float / COUNT(*) * 100) as funding_rate
FROM mana_need
WHERE forwarded_to_mao IS NOT NULL
GROUP BY forwarded_to_mao.name;
```

### 2. Gap Analysis Dashboard

Can easily show:
- Needs from Assessment vs. Community submissions
- Validated vs. pending validation
- Forwarded vs. not forwarded
- Funded (has linked_ppa) vs. unfunded

### 3. Participatory Budgeting Integration

During quarterly meetings:
```python
# Get high-priority unfunded needs for voting
unfunded_needs = Need.objects.filter(
    status='prioritized',
    linked_ppa__isnull=True,
    priority_score__gte=3.5
).order_by('-priority_score')

# Community representatives vote
# After voting, sort by community_votes
ranked_by_votes = unfunded_needs.order_by('-community_votes')

# Create PPAs for top-voted needs
for need in ranked_by_votes[:10]:  # Top 10
    ppa = MonitoringEntry.objects.create(...)
    ppa.needs_addressed.add(need)
    need.linked_ppa = ppa
    need.status = 'planned'
    need.save()
```

---

## Conclusion

**DO NOT create a separate `CommunityNeedSubmission` model.**

**Instead, extend the existing MANA `Need` model** to support both assessment-driven and community-submitted needs. This provides:

✅ Single source of truth
✅ Reuse of excellent prioritization framework
✅ Unified reporting
✅ Simplified integration with budgeting
✅ Clear audit trail
✅ Flexible workflow supporting both pathways

The MANA `Need` model is well-designed and can easily accommodate community submissions with minimal changes.

---

**Document Version**: 1.0
**Recommendation**: Extend MANA `Need` model (Option 1)
**Next Steps**: Update implementation evaluation document to reflect this approach
