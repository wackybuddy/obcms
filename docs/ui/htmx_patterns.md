# HTMX Patterns Documentation

This document provides common HTMX patterns used across the OBCMS project with code examples and best practices.

## Table of Contents

1. [Inline Editing](#inline-editing)
2. [Modal Dialogs](#modal-dialogs)
3. [Infinite Scroll](#infinite-scroll)
4. [Live Counters (Polling)](#live-counters-polling)
5. [Dependent Dropdowns](#dependent-dropdowns)
6. [Real-time Form Validation](#real-time-form-validation)
7. [Out-of-Band Swaps](#out-of-band-swaps)
8. [Delete Confirmation](#delete-confirmation)
9. [Optimistic Updates](#optimistic-updates)
10. [File Upload Progress](#file-upload-progress)

---

## 1. Inline Editing

### Pattern: Click-to-Edit Text

**Use Case**: Allow users to edit content without navigating to a separate form page.

**Frontend Template**:
```html
<div id="task-title-{{ task.id }}"
     class="editable-field"
     hx-get="{% url 'task_edit_field' task.id 'title' %}"
     hx-trigger="click"
     hx-swap="outerHTML"
     tabindex="0"
     role="button">
    <span>{{ task.title }}</span>
    <i class="fas fa-pen text-gray-400 ml-2"></i>
</div>
```

**Edit Form Fragment** (`task_edit_field.html`):
```html
<form id="task-title-{{ task.id }}"
      hx-post="{% url 'task_update_field' task.id 'title' %}"
      hx-swap="outerHTML">
    {% csrf_token %}
    <input type="text"
           name="title"
           value="{{ task.title }}"
           class="border border-emerald-500 rounded px-2 py-1"
           autofocus>
    <button type="submit" class="btn-sm btn-success">Save</button>
    <button type="button"
            hx-get="{% url 'task_field_display' task.id 'title' %}"
            hx-swap="outerHTML"
            class="btn-sm btn-secondary">Cancel</button>
</form>
```

**Django View**:
```python
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

def task_edit_field(request, task_id, field_name):
    """Return edit form for a specific field"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/fragments/task_edit_field.html', {
        'task': task,
        'field_name': field_name
    })

def task_update_field(request, task_id, field_name):
    """Update field and return display version"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        setattr(task, field_name, request.POST.get(field_name))
        task.save()

    return render(request, 'tasks/fragments/task_field_display.html', {
        'task': task,
        'field_name': field_name
    })
```

**Key Points**:
- Use `hx-trigger="click"` for click-to-edit behavior
- Include autofocus on input for better UX
- Provide cancel button that reverts to display view
- Use `outerHTML` swap to replace entire container

---

## 2. Modal Dialogs

### Pattern: HTMX-Loaded Modal

**Use Case**: Load modal content dynamically without page reload.

**Modal Container in Base Template**:
```html
<!-- Place in base template -->
<div id="modal-container"></div>

<!-- Include Alpine.js for modal interactions -->
<script src="//unpkg.com/alpinejs" defer></script>
```

**Trigger Button**:
```html
<button type="button"
        hx-get="{% url 'task_detail_modal' task.id %}"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        class="btn btn-primary">
    View Task Details
</button>
```

**Modal Fragment** (`task_detail_modal.html`):
```html
{% include "components/modal.html" with
    modal_id="task-detail-modal"
    title=task.title
    content_template="tasks/fragments/task_detail_content.html"
    size="lg"
%}
```

**Django View**:
```python
def task_detail_modal(request, task_id):
    """Return modal with task details"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/fragments/task_detail_modal.html', {
        'task': task
    })
```

**Key Points**:
- Use reusable `modal.html` component
- Target `#modal-container` for all modals
- Alpine.js handles open/close animations
- Press Escape or click backdrop to close

---

## 3. Infinite Scroll

### Pattern: Load More on Scroll

**Use Case**: Paginate large lists without traditional pagination controls.

**Frontend Template**:
```html
<div id="task-list" class="space-y-2">
    {% for task in tasks %}
    <div class="task-item">{{ task.title }}</div>
    {% endfor %}
</div>

{% if has_next_page %}
<div hx-get="{% url 'tasks_list' %}?page={{ next_page }}"
     hx-trigger="revealed"
     hx-swap="afterend"
     hx-target="#task-list"
     class="text-center py-4">
    <i class="fas fa-spinner fa-spin"></i> Loading more...
</div>
{% endif %}
```

**Django View**:
```python
from django.core.paginator import Paginator

def tasks_list(request):
    page = request.GET.get('page', 1)
    tasks = Task.objects.all().order_by('-created_at')

    paginator = Paginator(tasks, per_page=20)
    page_obj = paginator.get_page(page)

    context = {
        'tasks': page_obj.object_list,
        'has_next_page': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None
    }

    if request.headers.get('HX-Request'):
        return render(request, 'tasks/fragments/task_list_items.html', context)

    return render(request, 'tasks/task_list.html', context)
```

**Key Points**:
- Use `hx-trigger="revealed"` to detect when element enters viewport
- Use `hx-swap="afterend"` to append new items
- Show loading spinner for feedback
- Check `HX-Request` header to return fragment vs full page

---

## 4. Live Counters (Polling)

### Pattern: Auto-Refresh Metrics

**Use Case**: Display real-time statistics that update automatically.

**Frontend Template**:
```html
<div class="stats-panel grid grid-cols-3 gap-4">
    <div class="stat-card"
         hx-get="{% url 'metrics_pending_tasks' %}"
         hx-trigger="load, every 30s"
         hx-swap="innerHTML"
         aria-live="polite">
        <div class="stat-value">{{ pending_count }}</div>
        <div class="stat-label">Pending Tasks</div>
    </div>

    <div class="stat-card"
         hx-get="{% url 'metrics_in_progress_tasks' %}"
         hx-trigger="load, every 30s"
         hx-swap="innerHTML"
         aria-live="polite">
        <div class="stat-value">{{ in_progress_count }}</div>
        <div class="stat-label">In Progress</div>
    </div>

    <div class="stat-card"
         hx-get="{% url 'metrics_completed_tasks' %}"
         hx-trigger="load, every 30s"
         hx-swap="innerHTML"
         aria-live="polite">
        <div class="stat-value">{{ completed_count }}</div>
        <div class="stat-label">Completed</div>
    </div>
</div>
```

**Django View**:
```python
def metrics_pending_tasks(request):
    """Return pending task count"""
    count = Task.objects.filter(status='pending').count()
    return HttpResponse(f'''
        <div class="stat-value">{count}</div>
        <div class="stat-label">Pending Tasks</div>
    ''')
```

**Key Points**:
- Use `hx-trigger="every 30s"` for polling
- Include `load` trigger for immediate initial load
- Add `aria-live="polite"` for screen reader announcements
- Keep response lightweight (just the updated data)

---

## 5. Dependent Dropdowns

### Pattern: Cascade Filtering

**Use Case**: Update dropdown options based on parent selection (Region → Province → Municipality).

**Frontend Template**:
```html
<form>
    <!-- Region Dropdown -->
    <select id="region-select"
            name="region"
            hx-get="{% url 'get_provinces' %}"
            hx-trigger="change"
            hx-target="#province-select"
            hx-include="#region-select"
            class="form-select">
        <option value="">Select Region...</option>
        {% for region in regions %}
        <option value="{{ region.id }}">{{ region.name }}</option>
        {% endfor %}
    </select>

    <!-- Province Dropdown -->
    <select id="province-select"
            name="province"
            hx-get="{% url 'get_municipalities' %}"
            hx-trigger="change"
            hx-target="#municipality-select"
            hx-include="#region-select, #province-select"
            class="form-select"
            disabled>
        <option value="">Select Province...</option>
    </select>

    <!-- Municipality Dropdown -->
    <select id="municipality-select"
            name="municipality"
            class="form-select"
            disabled>
        <option value="">Select Municipality...</option>
    </select>
</form>
```

**Django Views**:
```python
def get_provinces(request):
    """Return provinces for selected region"""
    region_id = request.GET.get('region')

    if not region_id:
        return HttpResponse('<option value="">Select Province...</option>')

    provinces = Province.objects.filter(region_id=region_id).order_by('name')

    html = '<option value="">Select Province...</option>'
    for province in provinces:
        html += f'<option value="{province.id}">{province.name}</option>'

    return HttpResponse(html)

def get_municipalities(request):
    """Return municipalities for selected province"""
    province_id = request.GET.get('province')

    if not province_id:
        return HttpResponse('<option value="">Select Municipality...</option>')

    municipalities = Municipality.objects.filter(province_id=province_id).order_by('name')

    html = '<option value="">Select Municipality...</option>'
    for municipality in municipalities:
        html += f'<option value="{municipality.id}">{municipality.name}</option>'

    return HttpResponse(html)
```

**Key Points**:
- Use `hx-include` to send parent selection values
- Target the dependent dropdown with `hx-target`
- Enable/disable dropdowns based on parent selection
- Return just the `<option>` tags, not full `<select>`

---

## 6. Real-time Form Validation

### Pattern: Validate on Blur

**Use Case**: Provide immediate feedback on form field validity.

**Frontend Template**:
```html
<form>
    <div class="form-field">
        <label for="email">Email Address</label>
        <input type="email"
               id="email"
               name="email"
               hx-post="{% url 'validate_email' %}"
               hx-trigger="blur changed"
               hx-target="#email-error"
               hx-swap="innerHTML"
               class="form-input">
        <div id="email-error" class="error-message"></div>
    </div>

    <div class="form-field">
        <label for="username">Username</label>
        <input type="text"
               id="username"
               name="username"
               hx-post="{% url 'validate_username' %}"
               hx-trigger="blur changed delay:500ms"
               hx-target="#username-error"
               hx-swap="innerHTML"
               class="form-input">
        <div id="username-error" class="error-message"></div>
    </div>
</form>
```

**Django View**:
```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def validate_email_view(request):
    """Validate email format"""
    email = request.POST.get('email', '')

    try:
        validate_email(email)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return HttpResponse(
                '<span class="text-red-600 text-sm">Email already in use</span>'
            )

        return HttpResponse(
            '<span class="text-green-600 text-sm"><i class="fas fa-check"></i> Valid</span>'
        )
    except ValidationError:
        return HttpResponse(
            '<span class="text-red-600 text-sm">Invalid email format</span>'
        )
```

**Key Points**:
- Use `hx-trigger="blur changed"` to validate on field exit
- Add `delay:500ms` for debouncing on text inputs
- Target error container for validation messages
- Return only validation message HTML
- Use color coding for visual feedback

---

## 7. Out-of-Band Swaps

### Pattern: Update Multiple UI Regions

**Use Case**: Update multiple parts of the page from a single request (e.g., update task and refresh counters).

**Frontend Template**:
```html
<!-- Task Card -->
<div id="task-{{ task.id }}" data-task-id="{{ task.id }}">
    <h4>{{ task.title }}</h4>
    <button hx-post="{% url 'task_complete' task.id %}"
            hx-target="#task-{{ task.id }}"
            hx-swap="outerHTML">
        Mark Complete
    </button>
</div>

<!-- Counters (will be updated out-of-band) -->
<div id="pending-counter">{{ pending_count }}</div>
<div id="completed-counter">{{ completed_count }}</div>
```

**Django View**:
```python
from django.http import HttpResponse

def task_complete(request, task_id):
    """Mark task complete and update counters"""
    task = get_object_or_404(Task, id=task_id)
    task.status = 'completed'
    task.save()

    # Render updated task card
    task_html = render_to_string('tasks/fragments/task_card.html', {'task': task})

    # Render updated counters (out-of-band)
    pending_count = Task.objects.filter(status='pending').count()
    completed_count = Task.objects.filter(status='completed').count()

    counters_html = f'''
        <div id="pending-counter" hx-swap-oob="true">{pending_count}</div>
        <div id="completed-counter" hx-swap-oob="true">{completed_count}</div>
    '''

    return HttpResponse(task_html + counters_html)
```

**Key Points**:
- Add `hx-swap-oob="true"` on elements to update
- Match `id` attributes on both frontend and response
- Combine main response with OOB updates in single HttpResponse
- Use for updating counters, notifications, breadcrumbs

---

## 8. Delete Confirmation

### Pattern: Two-Step Delete with Preview

**Use Case**: Show confirmation dialog before deleting, with option to review details.

**Frontend Template**:
```html
<button type="button"
        class="btn-delete"
        data-delete-url="{% url 'task_delete' task.id %}"
        data-delete-preview="{% url 'task_detail' task.id %}?review_delete=1"
        data-delete-message="Delete task: {{ task.title }}?">
    <i class="fas fa-trash"></i> Delete
</button>
```

**JavaScript Handler**:
```javascript
// In components/data_table_card.html
document.addEventListener('click', function(event) {
    const trigger = event.target.closest('[data-delete-preview]');
    if (!trigger) return;

    event.preventDefault();
    const previewUrl = trigger.getAttribute('data-delete-preview');
    const message = trigger.getAttribute('data-delete-message') || 'Are you sure?';

    if (window.confirm(message)) {
        window.location.href = previewUrl;
    }
});
```

**Detail Page with Delete Confirmation** (`task_detail.html`):
```html
{% if request.GET.review_delete %}
<div class="alert alert-warning">
    <p>You are about to delete this task. This action cannot be undone.</p>
    <form hx-delete="{% url 'task_delete' task.id %}"
          hx-target="body"
          hx-swap="outerHTML">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Confirm Delete</button>
        <a href="{% url 'tasks_list' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endif %}
```

**Django View**:
```python
def task_delete(request, task_id):
    """Delete task and redirect"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'DELETE':
        task.delete()

        if request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={
                    'HX-Redirect': reverse('tasks_list')
                }
            )

        return redirect('tasks_list')

    return HttpResponseNotAllowed(['DELETE'])
```

**Key Points**:
- Use two-step confirmation for safety
- Show detail page with `review_delete=1` flag
- Use `hx-delete` for RESTful delete
- Return `HX-Redirect` header for post-delete navigation

---

## 9. Optimistic Updates

### Pattern: Update UI Before Server Confirmation

**Use Case**: Provide instant feedback for user actions (like/favorite/toggle).

**Frontend Template**:
```html
<button id="favorite-{{ task.id }}"
        hx-post="{% url 'task_toggle_favorite' task.id %}"
        hx-swap="none"
        hx-trigger="click"
        class="{% if task.is_favorited %}text-yellow-500{% else %}text-gray-400{% endif %}"
        onclick="toggleFavoriteOptimistic(this)">
    <i class="fas fa-star"></i>
</button>
```

**JavaScript Handler**:
```javascript
function toggleFavoriteOptimistic(button) {
    // Optimistic update
    const icon = button.querySelector('i');
    const isFavorited = button.classList.contains('text-yellow-500');

    if (isFavorited) {
        button.classList.remove('text-yellow-500');
        button.classList.add('text-gray-400');
    } else {
        button.classList.remove('text-gray-400');
        button.classList.add('text-yellow-500');
    }
}

// Revert on error
document.body.addEventListener('htmx:responseError', function(event) {
    // Revert optimistic update
    const button = event.detail.elt;
    toggleFavoriteOptimistic(button); // Toggle back

    if (window.showToast) {
        window.showToast('Failed to update favorite', 'error');
    }
});
```

**Django View**:
```python
def task_toggle_favorite(request, task_id):
    """Toggle favorite status"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.is_favorited = not task.is_favorited
        task.save()

        return HttpResponse(status=204)

    return HttpResponseNotAllowed(['POST'])
```

**Key Points**:
- Update UI immediately with JavaScript
- Use `hx-swap="none"` when no HTML response needed
- Listen for `htmx:responseError` to revert on failure
- Return 204 No Content for successful toggle

---

## 10. File Upload Progress

### Pattern: Progress Bar for File Uploads

**Use Case**: Show upload progress for large files.

**Frontend Template**:
```html
<form hx-post="{% url 'document_upload' %}"
      hx-encoding="multipart/form-data"
      hx-target="#upload-result">
    {% csrf_token %}

    <input type="file"
           name="document"
           id="document-upload"
           class="form-input">

    <button type="submit" class="btn btn-primary">Upload</button>

    <!-- Progress Bar -->
    <div id="upload-progress" class="hidden mt-4">
        <div class="progress-bar">
            <div id="progress-bar-fill" class="progress-bar-fill" style="width: 0%"></div>
        </div>
        <p id="progress-text" class="text-sm text-gray-600 mt-2">Uploading...</p>
    </div>
</form>

<div id="upload-result"></div>

<script>
document.body.addEventListener('htmx:xhr:progress', function(event) {
    const progressBar = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-bar-fill');
    const progressText = document.getElementById('progress-text');

    progressBar.classList.remove('hidden');

    const percent = Math.round((event.detail.loaded / event.detail.total) * 100);
    progressFill.style.width = percent + '%';
    progressText.textContent = `Uploading... ${percent}%`;
});

document.body.addEventListener('htmx:afterRequest', function() {
    document.getElementById('upload-progress').classList.add('hidden');
});
</script>
```

**Django View**:
```python
def document_upload(request):
    """Handle document upload"""
    if request.method == 'POST' and request.FILES.get('document'):
        document = request.FILES['document']

        # Save document
        doc = Document.objects.create(
            file=document,
            uploaded_by=request.user
        )

        return HttpResponse(f'''
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                Document uploaded successfully: {document.name}
            </div>
        ''')

    return HttpResponse('<div class="alert alert-danger">Upload failed</div>')
```

**Key Points**:
- Use `hx-encoding="multipart/form-data"` for file uploads
- Listen for `htmx:xhr:progress` event
- Update progress bar width based on `loaded` / `total`
- Hide progress bar after upload completes

---

## Best Practices Summary

1. **Always use CSRF tokens** for POST/PUT/DELETE requests
2. **Return minimal HTML** in HTMX responses (fragments, not full pages)
3. **Check `HX-Request` header** in views to determine response type
4. **Use consistent targeting** with `data-*` attributes for reliability
5. **Implement loading states** with `htmx:beforeRequest` and `htmx:afterSwap`
6. **Handle errors gracefully** with `htmx:responseError` listeners
7. **Provide accessibility** with ARIA labels and live regions
8. **Test keyboard navigation** for all HTMX interactions
9. **Use optimistic updates** for instant feedback
10. **Keep JavaScript minimal** - prefer HTMX attributes over custom JS

---

## Related Documentation

- [Component Library Guide](component_library_guide.md)
- [Accessibility Patterns](accessibility_patterns.md)
- [Mobile Responsiveness](mobile_patterns.md)
