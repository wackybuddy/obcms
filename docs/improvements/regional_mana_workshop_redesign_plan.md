# Regional MANA Workshop Redesign Plan

## Executive Summary

This document outlines a comprehensive redesign of the Regional MANA (Mapping and Needs Assessment) Workshops to enable participant-driven collaborative assessment with controlled access, sequential workflow, and AI-assisted consolidation capabilities.

**Key Objectives:**
1. Enable stakeholder participation through dedicated OBCMS accounts
2. Implement progressive workshop access control
3. Build robust output management with filtering and AI synthesis

**Estimated Timeline:** 6-8 weeks
**Priority:** High
**Complexity:** High

---

## 1. Current State Analysis

### Existing Models
- **WorkshopActivity**: Tracks 6 workshop types with status, facilitators, and JSONField outputs
- **WorkshopParticipant**: Records participant demographics and attendance
- **WorkshopOutput**: Captures deliverables like maps, plans, and documentation
- **Assessment**: Parent model for regional/provincial assessments

### Current Limitations
1. ❌ No participant authentication/authorization system
2. ❌ No workshop access control mechanism
3. ❌ No structured input forms for participants
4. ❌ No filtering/consolidation for outputs by province/region
5. ❌ No AI integration for synthesis generation
6. ❌ Workshop outputs stored as unstructured JSON

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MANA Workshop System                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌──────▼──────┐      ┌──────▼──────┐
   │  User   │         │  Workshop   │      │   Output    │
   │  Mgmt   │         │   Access    │      │   Mgmt      │
   └────┬────┘         └──────┬──────┘      └──────┬──────┘
        │                     │                     │
   ┌────▼─────────┐    ┌─────▼──────┐       ┌──────▼─────────┐
   │ Participant  │    │ Sequential │       │ AI Synthesis   │
   │ Registration │    │ Unlocking  │       │ & Filtering    │
   └──────────────┘    └────────────┘       └────────────────┘
```

---

## 3. User Management & Access Control

### 3.1 Participant User Types

Create new user groups with specific permissions:

```python
# New User Groups
MANA_PARTICIPANT_GROUPS = [
    'mana_regional_participant',  # Can access regional MANA workshops
    'mana_provincial_viewer',     # Can view provincial OBC data
    'mana_facilitator',           # OOBC staff facilitating workshops
    'mana_admin',                 # Full admin access to MANA system
]
```

### 3.2 Stakeholder Categories

Participants represent different stakeholder groups:

| Stakeholder Type | Description | Access Level |
|------------------|-------------|--------------|
| **LGU Representatives** | Provincial, Municipal, Barangay officials | Regional MANA + Provincial OBC |
| **NGA Representatives** | DSWD, DepEd, DOH, DA, DTI, etc. | Regional MANA + Provincial OBC |
| **OBC Community Leaders** | Community representatives | Regional MANA + Provincial OBC |
| **CSO/NGO Partners** | Civil society organizations | Regional MANA + Provincial OBC |
| **OOBC Staff** | OOBC facilitators and coordinators | Full access |

### 3.3 Database Schema Changes

#### New Model: `WorkshopParticipantAccount`

```python
class WorkshopParticipantAccount(models.Model):
    """Extended participant model linking to User accounts."""

    STAKEHOLDER_TYPES = [
        ('lgu_provincial', 'LGU - Provincial Government'),
        ('lgu_municipal', 'LGU - Municipal Government'),
        ('lgu_barangay', 'LGU - Barangay Government'),
        ('nga', 'National Government Agency'),
        ('obc_community', 'OBC Community Leader'),
        ('cso_ngo', 'CSO/NGO Partner'),
        ('oobc_staff', 'OOBC Staff'),
    ]

    # Link to Django User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mana_participant_profile'
    )

    # Assessment participation
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='registered_participants'
    )

    # Stakeholder information
    stakeholder_type = models.CharField(max_length=20, choices=STAKEHOLDER_TYPES)
    organization = models.CharField(max_length=200)
    position = models.CharField(max_length=150)

    # Geographic scope
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True, blank=True)

    # Workshop access
    current_workshop = models.CharField(
        max_length=15,
        choices=WorkshopActivity.WORKSHOP_TYPES,
        default='workshop_1'
    )

    completed_workshops = models.JSONField(
        default=list,
        help_text="List of completed workshop IDs"
    )

    # Metadata
    registered_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'assessment']
        permissions = [
            ('can_access_regional_mana', 'Can access Regional MANA workshops'),
            ('can_view_provincial_obc', 'Can view Provincial OBC Database'),
            ('can_facilitate_workshop', 'Can facilitate MANA workshops'),
        ]
```

### 3.4 Registration Workflow

1. **Facilitator Creates Participant Accounts**
   - OOBC staff create user accounts during assessment planning
   - Bulk registration via CSV import
   - Auto-generate secure passwords for participants
   - Email credentials to participants

2. **Participant Onboarding**
   - Participants may change their passwords. Passwords can be seen/viewed/accessed by Admin (superuser)
   - Profile completion form (organization, position, contact)
   - Accept data privacy consent
   - View workshop schedule and guidelines

3. **Access Provisioning**
   - Automatically assign to `mana_regional_participant` group
   - Grant permissions: `can_access_regional_mana` + `can_view_provincial_obc`
   - Set `current_workshop = 'workshop_1'`

---

## 4. Sequential Workshop Access Control

### 4.1 Progressive Unlocking Mechanism

Participants can only access workshops they're currently authorized for:

```python
class WorkshopAccessManager:
    """Manages workshop access progression."""

    @staticmethod
    def can_access_workshop(participant, workshop_type):
        """Check if participant can access a specific workshop."""
        workshop_sequence = [
            'workshop_1', 'workshop_2', 'workshop_3',
            'workshop_4', 'workshop_5', 'workshop_6'
        ]

        current_index = workshop_sequence.index(participant.current_workshop)
        requested_index = workshop_sequence.index(workshop_type)

        # Can only access current workshop
        return requested_index == current_index

    @staticmethod
    def advance_workshop(participant):
        """Move participant to next workshop."""
        workshop_sequence = [
            'workshop_1', 'workshop_2', 'workshop_3',
            'workshop_4', 'workshop_5', 'workshop_6'
        ]

        current_index = workshop_sequence.index(participant.current_workshop)

        # Add current workshop to completed list
        if participant.current_workshop not in participant.completed_workshops:
            participant.completed_workshops.append(participant.current_workshop)

        # Advance to next workshop
        if current_index < len(workshop_sequence) - 1:
            participant.current_workshop = workshop_sequence[current_index + 1]
            participant.save()
            return True

        return False  # Already at last workshop
```

### 4.2 Workshop Advancement Triggers

Advancement can be triggered by:

1. **Facilitator-Controlled** (Recommended)
   - Facilitator reviews workshop outputs
   - Clicks "Advance All Participants" button
   - All participants move to next workshop simultaneously

2. **Time-Based** (Optional)
   - Workshop unlocks at scheduled date/time
   - Participants automatically advanced

3. **Completion-Based** (Recommended; For OOBC Staff)
   - Participant must complete required forms
   - System validates completeness
   - Auto-advance when conditions met

### 4.3 View/Template Guards

```python
# views.py
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied

@permission_required('mana.can_access_regional_mana')
def workshop_detail_view(request, assessment_id, workshop_type):
    """Display workshop form for participants."""

    participant = request.user.mana_participant_profile

    # Check workshop access
    if not WorkshopAccessManager.can_access_workshop(participant, workshop_type):
        raise PermissionDenied("You don't have access to this workshop yet.")

    # Render workshop form
    ...
```

### 4.4 UI/UX for Locked Workshops

```html
<!-- Workshop Navigation -->
{% for workshop in workshop_list %}
<div class="workshop-tab
    {% if workshop.type == current_workshop %}active{% endif %}
    {% if not workshop.accessible %}locked{% endif %}">

    {% if workshop.accessible %}
        <a href="{% url 'mana:workshop_detail' workshop.type %}">
            {{ workshop.get_type_display }}
        </a>
    {% else %}
        <span class="text-gray-400 cursor-not-allowed">
            <i class="fas fa-lock"></i>
            {{ workshop.get_type_display }}
        </span>
    {% endif %}

    {% if workshop.type in completed_workshops %}
        <span class="badge badge-success">Completed</span>
    {% endif %}
</div>
{% endfor %}
```

---

## 5. Workshop Input Forms & Structured Outputs

### 5.1 Replace Unstructured JSON with Structured Models

#### New Model: `WorkshopResponse`

```python
class WorkshopResponse(models.Model):
    """Individual participant responses to workshop questions."""

    workshop_activity = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name='participant_responses'
    )

    participant = models.ForeignKey(
        WorkshopParticipantAccount,
        on_delete=models.CASCADE,
        related_name='workshop_responses'
    )

    # Question identification
    question_id = models.CharField(
        max_length=50,
        help_text="Unique identifier for the question (e.g., 'w1_q1_demographics')"
    )

    question_text = models.TextField(help_text="The actual question text")

    # Response data
    response_text = models.TextField(blank=True)
    response_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured response data for complex questions"
    )

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True)

    class Meta:
        unique_together = ['workshop_activity', 'participant', 'question_id']
        ordering = ['workshop_activity', 'question_id', 'submitted_at']
```

### 5.2 Workshop Question Schema

Define structured questions for each workshop:

```python
# Workshop 1: Understanding the Community Context
WORKSHOP_1_QUESTIONS = [
    {
        'id': 'w1_q1_demographics',
        'category': 'demographics',
        'question': 'What is the current demographic profile of OBCs in your province?',
        'input_type': 'textarea',
        'required': True,
    },
    {
        'id': 'w1_q2_population_distribution',
        'category': 'demographics',
        'question': 'How are OBC populations distributed across municipalities?',
        'input_type': 'multi_select',
        'options': [],  # Dynamically populated with municipalities
        'required': True,
    },
    {
        'id': 'w1_q3_cultural_practices',
        'category': 'cultural_context',
        'question': 'What are the predominant cultural practices and traditions?',
        'input_type': 'textarea',
        'required': True,
    },
    {
        'id': 'w1_q4_religious_institutions',
        'category': 'cultural_context',
        'question': 'List key religious institutions (mosques, madaris) and their status.',
        'input_type': 'repeater',  # Dynamic add/remove rows
        'fields': [
            {'name': 'institution_name', 'type': 'text'},
            {'name': 'municipality', 'type': 'select'},
            {'name': 'status', 'type': 'select', 'options': ['Active', 'Needs Support', 'Non-functional']},
        ],
        'required': True,
    },
    # ... more questions
]

# Workshop 2: Community Aspirations and Priorities
WORKSHOP_2_QUESTIONS = [
    {
        'id': 'w2_q1_key_aspirations',
        'category': 'aspirations',
        'question': 'What are the top 5 community aspirations identified?',
        'input_type': 'repeater',
        'max_items': 5,
        'fields': [
            {'name': 'aspiration', 'type': 'text'},
            {'name': 'priority_level', 'type': 'select', 'options': ['Critical', 'High', 'Medium', 'Low']},
            {'name': 'affected_population', 'type': 'number'},
        ],
        'required': True,
    },
    # ... more questions
]
```

### 5.3 Dynamic Form Generation

```python
# forms.py
class WorkshopResponseForm(forms.Form):
    """Dynamically generate form based on workshop questions."""

    def __init__(self, workshop_type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load questions for this workshop
        questions = self.get_questions_for_workshop(workshop_type)

        # Generate form fields
        for question in questions:
            field_class = self.get_field_class(question['input_type'])
            self.fields[question['id']] = field_class(
                label=question['question'],
                required=question['required'],
                **self.get_field_kwargs(question)
            )

    def get_field_class(self, input_type):
        """Map input type to Django form field."""
        mapping = {
            'text': forms.CharField,
            'textarea': forms.CharField,
            'number': forms.IntegerField,
            'select': forms.ChoiceField,
            'multi_select': forms.MultipleChoiceField,
            'date': forms.DateField,
            'repeater': forms.JSONField,  # Special handling
        }
        return mapping.get(input_type, forms.CharField)
```

---

## 6. Output Management & Filtering

### 6.1 Output Aggregation View

Facilitators need a consolidated view of all participant responses:

```python
class WorkshopOutputAggregationView(TemplateView):
    """View for facilitators to see all workshop outputs."""

    template_name = 'mana/workshop_output_aggregation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        assessment_id = self.kwargs['assessment_id']
        workshop_type = self.request.GET.get('workshop', 'workshop_1')

        # Filtering options
        filter_province = self.request.GET.get('province')
        filter_stakeholder = self.request.GET.get('stakeholder')

        # Get workshop and responses
        workshop = WorkshopActivity.objects.get(
            assessment_id=assessment_id,
            workshop_type=workshop_type
        )

        responses = WorkshopResponse.objects.filter(
            workshop_activity=workshop,
            is_draft=False
        )

        # Apply filters
        if filter_province:
            responses = responses.filter(
                participant__province_id=filter_province
            )

        if filter_stakeholder:
            responses = responses.filter(
                participant__stakeholder_type=filter_stakeholder
            )

        # Group responses by question
        grouped_responses = self.group_responses_by_question(responses)

        context.update({
            'workshop': workshop,
            'grouped_responses': grouped_responses,
            'provinces': Province.objects.filter(region_id__in=[9, 12]),  # IX, XII
            'stakeholder_types': WorkshopParticipantAccount.STAKEHOLDER_TYPES,
            'filter_province': filter_province,
            'filter_stakeholder': filter_stakeholder,
        })

        return context

    def group_responses_by_question(self, responses):
        """Group responses by question for easy comparison."""
        grouped = {}
        for response in responses:
            if response.question_id not in grouped:
                grouped[response.question_id] = {
                    'question_text': response.question_text,
                    'responses': []
                }
            grouped[response.question_id]['responses'].append({
                'participant': response.participant,
                'text': response.response_text,
                'data': response.response_data,
                'submitted_at': response.submitted_at,
            })
        return grouped
```

### 6.2 Export Capabilities

```python
class WorkshopOutputExportView(View):
    """Export workshop outputs in various formats."""

    def get(self, request, assessment_id, workshop_type):
        format_type = request.GET.get('format', 'xlsx')

        responses = self.get_filtered_responses(request, assessment_id, workshop_type)

        if format_type == 'xlsx':
            return self.export_excel(responses)
        elif format_type == 'csv':
            return self.export_csv(responses)
        elif format_type == 'pdf':
            return self.export_pdf(responses)

    def export_excel(self, responses):
        """Export to Excel with multiple sheets per question."""
        import openpyxl
        wb = openpyxl.Workbook()

        grouped = self.group_by_question(responses)

        for question_id, data in grouped.items():
            ws = wb.create_sheet(title=question_id[:31])  # Excel sheet name limit

            # Headers
            ws.append(['Participant', 'Organization', 'Province', 'Response', 'Submitted At'])

            # Data rows
            for resp in data['responses']:
                ws.append([
                    resp['participant'].user.get_full_name(),
                    resp['participant'].organization,
                    resp['participant'].province.name if resp['participant'].province else '',
                    resp['text'],
                    resp['submitted_at'].strftime('%Y-%m-%d %H:%M'),
                ])

        # Save to response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=workshop_outputs_{workshop_type}.xlsx'
        wb.save(response)

        return response
```

---

## 7. AI-Assisted Synthesis & Consolidation

### 7.1 AI Integration Architecture

```python
class AIWorkshopSynthesizer:
    """Use AI to consolidate and synthesize workshop outputs."""

    def __init__(self, llm_provider='openai'):
        """Initialize with LLM provider (OpenAI, Anthropic Claude, local model)."""
        self.llm_provider = llm_provider
        self.client = self.initialize_client()

    def synthesize_responses(self, question_id, responses, context):
        """Generate synthesis for a specific question's responses."""

        # Prepare prompt
        prompt = self.build_synthesis_prompt(question_id, responses, context)

        # Call LLM
        synthesis = self.client.generate(prompt)

        # Store synthesis
        WorkshopSynthesis.objects.create(
            question_id=question_id,
            synthesis_text=synthesis['text'],
            key_themes=synthesis.get('themes', []),
            consensus_points=synthesis.get('consensus', []),
            divergent_views=synthesis.get('divergent', []),
            generated_at=timezone.now(),
        )

        return synthesis

    def build_synthesis_prompt(self, question_id, responses, context):
        """Build prompt for LLM with context."""

        responses_text = "\n\n".join([
            f"[{r['participant'].organization}] {r['text']}"
            for r in responses
        ])

        prompt = f"""
You are analyzing responses from a Regional MANA (Mapping and Needs Assessment) workshop
for Other Bangsamoro Communities (OBCs) in {context['region']}.

**Question:** {context['question_text']}

**Stakeholder Responses:**
{responses_text}

**Task:**
1. Identify common themes and patterns across all responses
2. Summarize consensus points (what most stakeholders agree on)
3. Note divergent views or unique perspectives
4. Extract actionable insights and recommendations
5. Categorize findings by province if geographic patterns emerge

Provide a structured synthesis in JSON format:
{{
    "summary": "2-3 paragraph synthesis",
    "key_themes": ["theme1", "theme2", ...],
    "consensus_points": ["point1", "point2", ...],
    "divergent_views": ["view1", "view2", ...],
    "provincial_insights": {{"province_name": "insight", ...}},
    "recommendations": ["rec1", "rec2", ...]
}}
"""
        return prompt
```

### 7.2 Synthesis Storage Model

```python
class WorkshopSynthesis(models.Model):
    """AI-generated synthesis of workshop responses."""

    workshop_activity = models.ForeignKey(
        WorkshopActivity,
        on_delete=models.CASCADE,
        related_name='syntheses'
    )

    question_id = models.CharField(max_length=50)
    question_text = models.TextField()

    # Synthesis content
    synthesis_text = models.TextField(help_text="Main synthesis summary")

    key_themes = models.JSONField(
        default=list,
        help_text="List of identified key themes"
    )

    consensus_points = models.JSONField(
        default=list,
        help_text="Points of agreement across stakeholders"
    )

    divergent_views = models.JSONField(
        default=list,
        help_text="Divergent perspectives or disagreements"
    )

    provincial_insights = models.JSONField(
        default=dict,
        help_text="Geographic-specific insights by province"
    )

    recommendations = models.JSONField(
        default=list,
        help_text="Actionable recommendations"
    )

    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Facilitator who triggered synthesis"
    )

    llm_model = models.CharField(
        max_length=50,
        help_text="LLM model used (e.g., 'gpt-4', 'claude-3')"
    )

    reviewed = models.BooleanField(default=False)
    reviewer_notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Workshop Syntheses"
        unique_together = ['workshop_activity', 'question_id']
```

### 7.3 Synthesis UI Component

```html
<!-- Template: workshop_synthesis_panel.html -->
<div class="synthesis-panel border rounded-lg p-6 bg-gradient-to-br from-blue-50 to-indigo-50">
    <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold text-gray-900">
            <i class="fas fa-robot text-indigo-600"></i>
            AI Synthesis
        </h3>

        {% if not synthesis %}
        <button
            hx-post="{% url 'mana:generate_synthesis' question_id=question.id %}"
            hx-target="#synthesis-{{ question.id }}"
            class="btn btn-primary">
            <i class="fas fa-magic"></i> Generate Synthesis
        </button>
        {% endif %}
    </div>

    {% if synthesis %}
    <div id="synthesis-{{ question.id }}">
        <!-- Summary -->
        <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-2">Summary</h4>
            <p class="text-gray-600">{{ synthesis.synthesis_text }}</p>
        </div>

        <!-- Key Themes -->
        <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-2">Key Themes</h4>
            <div class="flex flex-wrap gap-2">
                {% for theme in synthesis.key_themes %}
                <span class="badge badge-primary">{{ theme }}</span>
                {% endfor %}
            </div>
        </div>

        <!-- Consensus Points -->
        <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-2">Consensus Points</h4>
            <ul class="list-disc list-inside text-gray-600">
                {% for point in synthesis.consensus_points %}
                <li>{{ point }}</li>
                {% endfor %}
            </ul>
        </div>

        <!-- Divergent Views -->
        {% if synthesis.divergent_views %}
        <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-2">Divergent Perspectives</h4>
            <ul class="list-disc list-inside text-gray-600 text-sm">
                {% for view in synthesis.divergent_views %}
                <li>{{ view }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        <!-- Provincial Insights -->
        {% if synthesis.provincial_insights %}
        <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-2">Provincial Insights</h4>
            {% for province, insight in synthesis.provincial_insights.items %}
            <div class="bg-white p-3 rounded mb-2">
                <strong class="text-indigo-700">{{ province }}:</strong>
                <span class="text-gray-600">{{ insight }}</span>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Recommendations -->
        <div class="mb-4">
            <h4 class="font-semibold text-gray-700 mb-2">Recommendations</h4>
            <ol class="list-decimal list-inside text-gray-600">
                {% for rec in synthesis.recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ol>
        </div>

        <!-- Review Controls -->
        <div class="flex gap-2 mt-4 pt-4 border-t">
            <button class="btn btn-sm btn-success">
                <i class="fas fa-check"></i> Approve Synthesis
            </button>
            <button class="btn btn-sm btn-warning">
                <i class="fas fa-edit"></i> Request Revision
            </button>
            <button class="btn btn-sm btn-secondary">
                <i class="fas fa-redo"></i> Regenerate
            </button>
        </div>
    </div>
    {% endif %}
</div>
```

---

## 8. Provincial & Regional Filtering

### 8.1 Filter UI Component

```html
<!-- Advanced Filtering Panel -->
<div class="filters-panel bg-white rounded-lg shadow-sm p-4 mb-6">
    <form method="get" class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Province Filter -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Province</label>
            <select name="province" class="form-select w-full">
                <option value="">All Provinces</option>
                {% for province in provinces %}
                <option value="{{ province.id }}" {% if filter_province == province.id|stringformat:"s" %}selected{% endif %}>
                    {{ province.name }}
                </option>
                {% endfor %}
            </select>
        </div>

        <!-- Stakeholder Type Filter -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Stakeholder Type</label>
            <select name="stakeholder" class="form-select w-full">
                <option value="">All Stakeholders</option>
                {% for type_key, type_label in stakeholder_types %}
                <option value="{{ type_key }}" {% if filter_stakeholder == type_key %}selected{% endif %}>
                    {{ type_label }}
                </option>
                {% endfor %}
            </select>
        </div>

        <!-- Workshop Filter -->
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Workshop</label>
            <select name="workshop" class="form-select w-full">
                {% for ws in workshops %}
                <option value="{{ ws.workshop_type }}" {% if filter_workshop == ws.workshop_type %}selected{% endif %}>
                    {{ ws.get_workshop_type_display }}
                </option>
                {% endfor %}
            </select>
        </div>

        <!-- Actions -->
        <div class="flex items-end gap-2">
            <button type="submit" class="btn btn-primary flex-1">
                <i class="fas fa-filter"></i> Apply Filters
            </button>
            <a href="?export=xlsx&{{ request.GET.urlencode }}" class="btn btn-secondary">
                <i class="fas fa-download"></i>
            </a>
        </div>
    </form>
</div>
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation 
- [ ] Create `WorkshopParticipantAccount` model
- [ ] Implement participant registration system
- [ ] Set up user groups and permissions
- [ ] Build participant onboarding flow

### Phase 2: Access Control
- [ ] Implement `WorkshopAccessManager`
- [ ] Add workshop progression logic
- [ ] Build facilitator controls for advancement
- [ ] Create UI for locked/unlocked workshops

### Phase 3: Structured Inputs 
- [ ] Create `WorkshopResponse` model
- [ ] Define question schemas for all 6 workshops
- [ ] Build dynamic form generation
- [ ] Implement draft saving and submission

### Phase 4: Output Management 
- [ ] Build output aggregation view
- [ ] Implement filtering by province/stakeholder
- [ ] Add export functionality (Excel, CSV, PDF)
- [ ] Create comparison views

### Phase 5: AI Integration 
- [ ] Set up LLM API integration
- [ ] Create `WorkshopSynthesis` model
- [ ] Build synthesis generation pipeline
- [ ] Implement review/approval workflow

### Phase 6: Testing & Refinement 
- [ ] User acceptance testing with sample participants
- [ ] Performance testing with realistic data volumes
- [ ] Security audit of access controls
- [ ] Documentation and training materials

---

## 10. Technical Specifications

### 10.1 Dependencies

```python
# requirements/base.txt additions
openai>=1.0.0              # OpenAI API for GPT models
anthropic>=0.25.0          # Anthropic Claude API
openpyxl>=3.1.0           # Excel export
reportlab>=4.0.0          # PDF generation
celery>=5.3.0             # Background tasks for AI synthesis
redis>=5.0.0              # Celery broker
```

### 10.2 Environment Variables

```bash
# .env additions
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AI_SYNTHESIS_MODEL=gpt-4  # or claude-3-opus-20240229
AI_SYNTHESIS_ENABLED=True
```

### 10.3 Database Migrations

```bash
# Generate migrations
python manage.py makemigrations mana

# Expected migrations:
# - 0013_workshopparticipantaccount.py
# - 0014_workshopresponse.py
# - 0015_workshopsynthesis.py
# - 0016_add_workshop_permissions.py
```

---

## 11. Security Considerations

### 11.1 Data Privacy
- [ ] Ensure participant responses are only visible to facilitators and admins
- [ ] Implement data anonymization options for reporting
- [ ] Add consent checkboxes for data usage

### 11.2 Access Logs
```python
class WorkshopAccessLog(models.Model):
    """Audit log for workshop access."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workshop = models.ForeignKey(WorkshopActivity, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # 'viewed', 'submitted', 'edited'
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
```

### 11.3 Rate Limiting
- Generously limit AI synthesis requests to prevent abuse
- Throttle export downloads
- Monitor for suspicious access patterns

---

## 12. UI/UX Mockups

### 12.1 Participant Dashboard
```
┌─────────────────────────────────────────────────────────┐
│  Regional MANA Workshop - Region XII Assessment         │
│                                                          │
│  Welcome, Juan Dela Cruz (LGU - Provincial Government)  │
│  Province: South Cotabato                               │
└─────────────────────────────────────────────────────────┘

Current Workshop: Workshop 2 - Community Aspirations

┌─────────────────────────────────────────────────────────┐
│  Workshop Progress                                       │
│                                                          │
│  ✅ Workshop 1: Understanding Community Context          │
│      Completed: Jan 15, 2025 | View Submission          │
│                                                          │
│  ▶️  Workshop 2: Community Aspirations (IN PROGRESS)     │
│      Due: Jan 22, 2025 | Continue Working               │
│                                                          │
│  🔒 Workshop 3: Collaboration & Empowerment              │
│      Unlocks after Workshop 2 completion                 │
│                                                          │
│  🔒 Workshop 4-6: (Locked)                               │
└─────────────────────────────────────────────────────────┘

[Continue to Workshop 2] [View Schedule] [Resources]
```

### 12.2 Facilitator Dashboard
```
┌─────────────────────────────────────────────────────────┐
│  Workshop Output Management                              │
│  Assessment: Demo Regional MANA - Region XII            │
└─────────────────────────────────────────────────────────┘

Filters: [Province: All ▼] [Stakeholder: All ▼] [Workshop: 2 ▼]

Workshop 2 Responses: 45 participants, 42 submitted (93%)

┌─────────────────────────────────────────────────────────┐
│ Question 1: Top 5 Community Aspirations                 │
│                                                          │
│ [AI Synthesis] ━━━━━━━━━━━━━━━━━━━━━━━ Generated ✓     │
│                                                          │
│ Key Themes: Infrastructure, Livelihood, Education       │
│ Consensus: All provinces prioritize road improvements   │
│                                                          │
│ [View Details] [Regenerate] [Export]                    │
│                                                          │
│ Individual Responses (12):                              │
│ • [South Cotabato - LGU] "Road improvement..."          │
│ • [Sultan Kudarat - OBC] "Access to healthcare..."      │
│ • [Sarangani - NGA] "Livelihood programs..."            │
│ [Show all 12 responses]                                 │
└─────────────────────────────────────────────────────────┘

[Advance All to Workshop 3] [Export All Data] [Generate Report]
```

---

## 13. Training & Documentation

### 13.1 User Guides
- **Participant Guide**: How to navigate workshops, submit responses, track progress
- **Facilitator Guide**: Managing participants, reviewing outputs, generating synthesis
- **Admin Guide**: System configuration, user management, troubleshooting

### 13.2 Training Sessions
1. **Facilitator Training** (4 hours)
   - System overview and navigation
   - Participant management
   - Output review and synthesis generation
   - Report generation

2. **Participant Orientation** (1 hour)
   - Login and password setup
   - Workshop navigation
   - Submitting responses
   - Understanding the MANA process

---

## 14. Success Metrics

### 14.1 Adoption Metrics
- Participant registration completion rate: Target >90%
- Workshop completion rate: Target >85%
- Response submission rate: Target >80%

### 14.2 System Performance
- Page load time: <2 seconds
- AI synthesis generation: <30 seconds
- Export generation: <10 seconds for 100 responses

### 14.3 Data Quality
- Average response length: >100 words for text questions
- Synthesis accuracy: >85% (measured by facilitator review)
- Data completeness: >90% of required fields filled

---

## 15. Future Enhancements

### 15.1 Phase 2 Features (Post-MVP)
- Real-time collaboration (multiple participants editing simultaneously)
- Mobile app for field data collection
- Integration with GIS for geographic visualization
- Automated report generation with charts/graphs
- Multi-language support (English, Filipino, Maguindanaon, Tausug)

### 15.2 Advanced AI Features
- Sentiment analysis of responses
- Trend detection across multiple assessments
- Predictive modeling for needs prioritization
- Automated translation between languages

---

## 16. Appendices

### Appendix A: Workshop Question Schemas
See separate file: `workshop_questions_schema.json`

### Appendix B: Permission Matrix
| User Group | Regional MANA | Provincial OBC | Facilitate | Admin |
|------------|---------------|----------------|------------|-------|
| Participant | Read/Write (current workshop) | Read | No | No |
| Facilitator | Read All | Read All | Yes | No |
| Admin | Full | Full | Yes | Yes |

### Appendix C: API Endpoints
```
/api/mana/workshops/<assessment_id>/                # List workshops
/api/mana/workshops/<workshop_id>/responses/        # Submit responses
/api/mana/workshops/<workshop_id>/synthesis/        # Get/generate synthesis
/api/mana/participants/<assessment_id>/advance/     # Advance workshop
```

---

## Document Control

**Version:** 1.0
**Last Updated:** 2025-09-30
**Author:** Claude (AI Assistant)
**Review Status:** Draft
**Next Review:** Upon Phase 1 completion

---

**End of Regional MANA Workshop Redesign Plan**