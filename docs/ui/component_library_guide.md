# Component Library Usage Guide

Complete guide to using the reusable component library in OBCMS.

## Table of Contents

1. [Component Overview](#component-overview)
2. [Kanban Board Component](#kanban-board-component)
3. [Calendar Widget Component](#calendar-widget-component)
4. [Modal Dialog Component](#modal-dialog-component)
5. [Task Card Component](#task-card-component)
6. [Data Table Card Component](#data-table-card-component)
7. [Form Field Components](#form-field-components)
8. [Integration Examples](#integration-examples)

---

## Component Overview

All reusable components are located in `src/templates/components/`.

### Component Philosophy

1. **Reusability**: Components work across all modules without modification
2. **Consistency**: Uniform styling and behavior throughout the application
3. **Accessibility**: WCAG 2.1 AA compliant out of the box
4. **HTMX-First**: Built for seamless HTMX integration
5. **Mobile-Responsive**: Works on all screen sizes

### Dependencies

Components require the following libraries (include in base template):

```html
<!-- In base.html <head> -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.css">
<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js"></script>
```

---

## Kanban Board Component

**File**: `src/templates/components/kanban_board.html`

### Basic Usage

```django
{% include "components/kanban_board.html" with
    board_id="assessment-tasks"
    columns=status_columns
    item_template="components/task_card.html"
    move_endpoint="/api/tasks/move/"
    editable=True
%}
```

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `board_id` | string | Unique ID for the board |
| `columns` | list | List of column dictionaries (see structure below) |
| `item_template` | string | Path to template for rendering items |
| `move_endpoint` | string | URL endpoint for moving items |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `editable` | bool | `True` | Enable drag-and-drop |
| `height_class` | string | `'min-h-[600px]'` | Tailwind height class |
| `column_class` | string | `''` | Additional classes for columns |

### Column Structure

Each column in the `columns` list must be a dictionary with:

```python
{
    'id': 'planning',                    # Column identifier
    'title': 'Planning',                 # Display title
    'items': [task1, task2, ...],        # List of items to display
    'add_url': '/tasks/create/?status=planning'  # Optional: URL for "Add Item" button
}
```

### Django View Example

```python
from django.shortcuts import render
from .models import Task

def kanban_view(request):
    """Display kanban board with task columns"""

    # Define columns
    columns = [
        {
            'id': 'planning',
            'title': 'Planning',
            'items': Task.objects.filter(status='planning'),
            'add_url': reverse('task_create') + '?status=planning'
        },
        {
            'id': 'in_progress',
            'title': 'In Progress',
            'items': Task.objects.filter(status='in_progress'),
            'add_url': reverse('task_create') + '?status=in_progress'
        },
        {
            'id': 'review',
            'title': 'Review',
            'items': Task.objects.filter(status='review'),
        },
        {
            'id': 'completed',
            'title': 'Completed',
            'items': Task.objects.filter(status='completed'),
        }
    ]

    return render(request, 'tasks/kanban.html', {
        'status_columns': columns
    })
```

### Move Endpoint API

The kanban board expects a POST endpoint that accepts:

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

@require_POST
def task_move(request):
    """Move task between kanban columns"""
    data = json.loads(request.body)

    item_id = data.get('item_id')
    old_column = data.get('old_column')
    new_column = data.get('new_column')

    try:
        task = Task.objects.get(id=item_id)
        task.status = new_column
        task.save()

        return JsonResponse({
            'success': True,
            'message': f'Task moved to {new_column}'
        })
    except Task.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Task not found'
        }, status=404)
```

### Mobile Responsiveness

- Desktop: Horizontal columns
- Mobile: Vertical stacked columns
- Touch-friendly drag-and-drop on mobile

---

## Calendar Widget Component

**File**: `src/templates/components/calendar_full.html`

### Basic Usage

```django
{% include "components/calendar_full.html" with
    calendar_id="project-calendar"
    events_feed_url="/api/tasks/calendar-feed/"
    initial_view="dayGridMonth"
    editable=True
    height="700px"
%}
```

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `calendar_id` | string | Unique ID for calendar div |
| `events_feed_url` | string | URL endpoint returning events JSON |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `initial_view` | string | `'dayGridMonth'` | `dayGridMonth`, `timeGridWeek`, `listWeek` |
| `editable` | bool | `False` | Allow drag-to-reschedule |
| `selectable` | bool | `False` | Allow date range selection |
| `height` | string | `'auto'` | `'auto'`, `'parent'`, or pixel value |
| `slot_min_time` | string | `'06:00:00'` | Earliest time slot |
| `slot_max_time` | string | `'20:00:00'` | Latest time slot |
| `timezone` | string | `'Asia/Manila'` | Timezone identifier |
| `show_weekends` | bool | `True` | Show weekend days |

### Events Feed Format

The `events_feed_url` must return JSON in FullCalendar format:

```python
# views.py
from django.http import JsonResponse

def calendar_events_feed(request):
    """Return events in FullCalendar JSON format"""
    tasks = Task.objects.filter(due_date__isnull=False)

    events = []
    for task in tasks:
        events.append({
            'id': task.id,
            'title': task.title,
            'start': task.due_date.isoformat(),
            'end': task.due_date.isoformat(),
            'url': reverse('task_detail_modal', args=[task.id]),
            'extendedProps': {
                'type': 'task',
                'priority': task.priority,
                'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else None,
                'description': task.description
            }
        })

    return JsonResponse(events, safe=False)
```

### Event Types and Colors

The calendar automatically color-codes events by type:

- **Task** (green): `extendedProps.type = 'task'`
- **Event** (orange): `extendedProps.type = 'event'`
- **Milestone** (blue): `extendedProps.type = 'milestone'`

### Drag-to-Reschedule

When `editable=True`, users can drag tasks to reschedule. The component automatically sends PATCH requests to `/api/tasks/{id}/update/`:

```python
# views.py
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["PATCH"])
def task_update(request, task_id):
    """Update task due date from calendar drag"""
    task = get_object_or_404(Task, id=task_id)
    data = json.loads(request.body)

    if 'due_date' in data:
        task.due_date = data['due_date']
        task.save()

    return JsonResponse({'success': True})
```

---

## Modal Dialog Component

**File**: `src/templates/components/modal.html`

### Basic Usage

```django
{% include "components/modal.html" with
    modal_id="task-detail-modal"
    title="Task Details"
    content_template="tasks/fragments/task_detail_content.html"
    size="lg"
%}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `modal_id` | string | auto-generated | Unique modal identifier |
| `title` | string | required | Modal title text |
| `size` | string | `'md'` | `'sm'`, `'md'`, `'lg'`, `'xl'`, `'full'` |
| `content_template` | string | - | Path to template for modal body |
| `content` | string | - | HTML content as string |
| `footer_template` | string | - | Path to template for modal footer |
| `footer_html` | string | - | HTML for footer as string |
| `closeable` | bool | `True` | Show close button |
| `backdrop_dismiss` | bool | `True` | Click backdrop to close |
| `show_footer` | bool | auto | Render footer section |

### HTMX Integration

**Trigger Modal from Button**:

```html
<button type="button"
        hx-get="{% url 'task_detail_modal' task.id %}"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        class="btn btn-primary">
    View Details
</button>
```

**Django View**:

```python
def task_detail_modal(request, task_id):
    """Return modal HTML fragment"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/fragments/task_detail_modal.html', {
        'task': task
    })
```

**Modal Template** (`task_detail_modal.html`):

```django
{% include "components/modal.html" with
    modal_id="task-detail-modal"
    title=task.title
    content_template="tasks/fragments/task_detail_content.html"
    footer_html='<button class="btn btn-secondary" onclick="closeModal()">Close</button>'
    size="lg"
%}
```

### Modal Features

- **Alpine.js powered**: Smooth open/close animations
- **Focus trap**: Keyboard focus stays within modal
- **Escape key**: Press Escape to close
- **Body scroll lock**: Prevents scrolling behind modal
- **Accessibility**: Proper ARIA attributes and keyboard navigation

---

## Task Card Component

**File**: `src/templates/components/task_card.html`

### Basic Usage

```django
{% include "components/task_card.html" with task=task %}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task` | object | required | Task object with attributes |
| `show_actions` | bool | `False` | Show action buttons |
| `show_status_badge` | bool | `False` | Show status badge |
| `detail_url` | string | - | URL for task detail modal |

### Task Object Requirements

The task object must have these attributes:

```python
class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20)  # planning, in_progress, review, completed
    priority = models.CharField(max_length=20)  # low, medium, high
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    domain = models.CharField(max_length=50, blank=True)

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != 'completed':
            return self.due_date < timezone.now().date()
        return False

    def get_domain_display(self):
        """Return human-readable domain name"""
        return dict(self.DOMAIN_CHOICES).get(self.domain, self.domain)
```

### Usage in Kanban Board

```django
{% include "components/kanban_board.html" with
    board_id="tasks-kanban"
    columns=columns
    item_template="components/task_card.html"
    move_endpoint="/api/tasks/move/"
%}
```

### Usage in List View

```django
{% for task in tasks %}
<div class="bg-white rounded-lg shadow-sm p-4 mb-2">
    {% include "components/task_card.html" with
        task=task
        show_actions=True
        show_status_badge=True
        detail_url=task.get_absolute_url
    %}
</div>
{% endfor %}
```

---

## Data Table Card Component

**File**: `src/templates/components/data_table_card.html`

### Basic Usage

```django
{% include "components/data_table_card.html" with
    title="Barangay OBCs"
    icon_class="fas fa-map-marker-alt"
    accent_class="bg-gradient-to-r from-emerald-500 to-emerald-600"
    headers=table_headers
    rows=table_rows
%}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | string | required | Card heading text |
| `icon_class` | string | - | FontAwesome icon class |
| `accent_class` | string | emerald gradient | Tailwind classes for header |
| `headers` | list | required | Table header definitions |
| `rows` | list | required | Table row data |
| `empty_message` | string | "No records..." | Empty state text |
| `show_actions` | bool | `True` | Show action column |

### Headers Structure

```python
headers = [
    {'label': 'Name', 'class': 'flex items-center'},
    {'label': 'Population', 'class': 'text-right'},
    {'label': 'Municipality', 'class': ''},
]
```

### Rows Structure

```python
rows = [
    {
        'cells': [
            {'content': 'Barangay Alpha', 'class': 'font-semibold'},
            {'content': '5,432', 'class': 'text-right text-gray-600'},
            {'content': 'Zamboanga City', 'class': 'text-gray-700'},
        ],
        'view_url': '/communities/barangays/1/',
        'edit_url': '/communities/barangays/1/edit/',
        'delete_preview_url': '/communities/barangays/1/?review_delete=1',
        'delete_message': 'Are you sure you want to delete Barangay Alpha?'
    },
    # ... more rows
]
```

### Django View Example

```python
def barangay_list(request):
    """Display list of barangays in data table"""
    barangays = Barangay.objects.select_related('municipality').all()

    headers = [
        {'label': 'Barangay Name', 'class': ''},
        {'label': 'Municipality', 'class': ''},
        {'label': 'Population', 'class': 'text-right'},
    ]

    rows = []
    for barangay in barangays:
        rows.append({
            'cells': [
                {'content': barangay.name, 'class': 'font-semibold'},
                {'content': barangay.municipality.name, 'class': 'text-gray-700'},
                {'content': f'{barangay.population:,}', 'class': 'text-right text-gray-600'},
            ],
            'view_url': reverse('barangay_detail', args=[barangay.id]),
            'edit_url': reverse('barangay_edit', args=[barangay.id]),
            'delete_preview_url': reverse('barangay_detail', args=[barangay.id]) + '?review_delete=1',
            'delete_message': f'Delete {barangay.name}?'
        })

    return render(request, 'communities/barangay_list.html', {
        'table_headers': headers,
        'table_rows': rows
    })
```

---

## Form Field Components

### Text Input Component

**File**: `src/templates/components/form_field_input.html`

```django
{% include "components/form_field_input.html" with
    field=form.title
    label="Task Title"
    placeholder="Enter task title..."
    required=True
%}
```

### Select Dropdown Component

**File**: `src/templates/components/form_field_select.html`

```django
{% include "components/form_field_select.html" with
    field=form.status
    label="Status"
    placeholder="Select status..."
    icon="fas fa-chevron-down"
    required=True
%}
```

---

## Integration Examples

### Example 1: Project Task Management Page

**Template** (`project_tasks.html`):

```django
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">Project Tasks</h1>

    <!-- Tabs for different views -->
    <div class="mb-6" x-data="{ activeTab: 'kanban' }">
        <div class="border-b border-gray-200">
            <button @click="activeTab = 'kanban'"
                    :class="{ 'border-emerald-500 text-emerald-600': activeTab === 'kanban' }"
                    class="px-4 py-2 border-b-2 border-transparent">
                Kanban View
            </button>
            <button @click="activeTab = 'calendar'"
                    :class="{ 'border-emerald-500 text-emerald-600': activeTab === 'calendar' }"
                    class="px-4 py-2 border-b-2 border-transparent">
                Calendar View
            </button>
        </div>

        <!-- Kanban View -->
        <div x-show="activeTab === 'kanban'" class="mt-6">
            {% include "components/kanban_board.html" with
                board_id="project-tasks-kanban"
                columns=status_columns
                item_template="components/task_card.html"
                move_endpoint="/api/tasks/move/"
                editable=True
            %}
        </div>

        <!-- Calendar View -->
        <div x-show="activeTab === 'calendar'" x-cloak class="mt-6">
            {% include "components/calendar_full.html" with
                calendar_id="project-calendar"
                events_feed_url="/api/projects/{{ project.id }}/calendar-feed/"
                initial_view="dayGridMonth"
                editable=True
                height="700px"
            %}
        </div>
    </div>
</div>

<!-- Modal Container -->
<div id="modal-container"></div>
{% endblock %}
```

### Example 2: Assessment List with Filters

**Template** (`assessment_list.html`):

```django
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-6">MANA Assessments</h1>

    <!-- Filters -->
    <form class="bg-white rounded-lg shadow-sm p-4 mb-6"
          hx-get="{% url 'assessment_list' %}"
          hx-target="#assessment-table"
          hx-trigger="change, submit">

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            {% include "components/form_field_select.html" with
                field=filter_form.region
                label="Region"
                placeholder="All Regions"
            %}

            {% include "components/form_field_select.html" with
                field=filter_form.status
                label="Status"
                placeholder="All Statuses"
            %}

            {% include "components/form_field_select.html" with
                field=filter_form.domain
                label="Domain"
                placeholder="All Domains"
            %}
        </div>
    </form>

    <!-- Data Table -->
    <div id="assessment-table">
        {% include "components/data_table_card.html" with
            title="Assessment Records"
            icon_class="fas fa-clipboard-list"
            headers=headers
            rows=rows
        %}
    </div>
</div>
{% endblock %}
```

---

## Best Practices

1. **Consistent Naming**: Use descriptive IDs for components (`project-tasks-kanban`, not `kanban1`)
2. **Reuse Components**: Never duplicate component code; always use `{% include %}`
3. **Pass Required Data**: Ensure all required parameters are provided
4. **Mobile Testing**: Test components on mobile devices and different screen sizes
5. **Accessibility**: Use provided ARIA attributes; don't remove them
6. **HTMX Integration**: Follow HTMX patterns documented in `htmx_patterns.md`
7. **Performance**: Lazy-load calendars and large datasets
8. **Error Handling**: Implement proper error states for HTMX failures

---

## Troubleshooting

### Kanban Board Not Initializing

**Problem**: Drag-and-drop not working

**Solutions**:
- Check that `move_endpoint` is correct
- Verify CSRF token is present in the page
- Check browser console for JavaScript errors
- Ensure items have unique `data-item-id` attributes

### Calendar Not Rendering

**Problem**: Calendar container is empty

**Solutions**:
- Verify FullCalendar library is loaded
- Check that `events_feed_url` returns valid JSON
- Inspect browser console for errors
- Ensure `calendar_id` is unique on the page

### Modal Not Opening

**Problem**: Modal trigger does nothing

**Solutions**:
- Verify `#modal-container` div exists in the template
- Check that Alpine.js is loaded
- Ensure HTMX request is successful (check network tab)
- Verify modal template is correctly structured

---

## Related Documentation

- [HTMX Patterns](htmx_patterns.md)
- [Accessibility Patterns](accessibility_patterns.md)
- [Mobile Responsiveness](mobile_patterns.md)
