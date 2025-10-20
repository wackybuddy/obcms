# Accessibility Patterns (WCAG 2.1 AA)

This document provides accessibility patterns and code examples to ensure OBCMS meets WCAG 2.1 AA compliance standards.

## Table of Contents

1. [Semantic HTML Structure](#semantic-html-structure)
2. [Keyboard Navigation](#keyboard-navigation)
3. [Focus Management](#focus-management)
4. [ARIA Labels and Roles](#aria-labels-and-roles)
5. [Color Contrast](#color-contrast)
6. [Screen Reader Support](#screen-reader-support)
7. [Form Accessibility](#form-accessibility)
8. [Dynamic Content Announcements](#dynamic-content-announcements)
9. [Touch Target Sizes](#touch-target-sizes)
10. [Skip Navigation Links](#skip-navigation-links)

---

## 1. Semantic HTML Structure

### Principle
Use semantic HTML elements to convey meaning and structure, helping assistive technologies understand page layout.

### Pattern: Proper Document Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - OBCMS</title>
</head>
<body>
    <!-- Skip to main content link -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <!-- Site header -->
    <header role="banner">
        <nav role="navigation" aria-label="Main navigation">
            <!-- Navigation items -->
        </nav>
    </header>

    <!-- Main content area -->
    <main id="main-content" role="main">
        <h1>Page Heading</h1>

        <section aria-labelledby="section-1-heading">
            <h2 id="section-1-heading">Section Title</h2>
            <!-- Section content -->
        </section>
    </main>

    <!-- Site footer -->
    <footer role="contentinfo">
        <!-- Footer content -->
    </footer>
</body>
</html>
```

### Best Practices
- Use `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>` appropriately
- Use heading hierarchy correctly (H1 → H2 → H3, no skipping levels)
- One `<h1>` per page
- Use `<button>` for actions, `<a>` for navigation
- Use `<table>` for tabular data, not layout

---

## 2. Keyboard Navigation

### Principle
All interactive elements must be accessible via keyboard (Tab, Enter, Space, Arrow keys).

### Pattern: Keyboard-Accessible Cards

```html
<div class="task-card"
     tabindex="0"
     role="button"
     aria-label="View task: {{ task.title }}"
     @keydown.enter="handleTaskClick"
     @keydown.space.prevent="handleTaskClick"
     onclick="handleTaskClick()">
    <h4>{{ task.title }}</h4>
    <p>{{ task.description }}</p>
</div>

<script>
function handleTaskClick() {
    // Open task modal
    window.location.href = "{% url 'task_detail' task.id %}";
}
</script>
```

### Pattern: Keyboard-Accessible Dropdown Menu

```html
<div class="dropdown"
     x-data="{ open: false }"
     @keydown.escape="open = false">

    <!-- Trigger button -->
    <button type="button"
            @click="open = !open"
            @keydown.down.prevent="open = true; $nextTick(() => $refs.firstItem.focus())"
            aria-haspopup="true"
            :aria-expanded="open"
            class="dropdown-trigger">
        Actions <i class="fas fa-chevron-down"></i>
    </button>

    <!-- Dropdown menu -->
    <div x-show="open"
         x-cloak
         @click.away="open = false"
         class="dropdown-menu"
         role="menu">

        <a href="{% url 'task_edit' task.id %}"
           x-ref="firstItem"
           @keydown.down.prevent="$refs.secondItem.focus()"
           role="menuitem"
           class="dropdown-item">
            Edit
        </a>

        <a href="{% url 'task_duplicate' task.id %}"
           x-ref="secondItem"
           @keydown.up.prevent="$refs.firstItem.focus()"
           @keydown.down.prevent="$refs.thirdItem.focus()"
           role="menuitem"
           class="dropdown-item">
            Duplicate
        </a>

        <button type="button"
                x-ref="thirdItem"
                @keydown.up.prevent="$refs.secondItem.focus()"
                role="menuitem"
                class="dropdown-item text-red-600">
            Delete
        </button>
    </div>
</div>
```

### Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| Tab | Move to next interactive element |
| Shift+Tab | Move to previous interactive element |
| Enter | Activate button/link |
| Space | Activate button/toggle checkbox |
| Escape | Close modal/dropdown |
| Arrow Keys | Navigate within lists, dropdowns, tabs |

---

## 3. Focus Management

### Principle
Ensure visible focus indicators and manage focus appropriately during interactions.

### Pattern: Visible Focus Indicators

```css
/* Tailwind focus utilities */
.btn {
    @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
}

.form-input {
    @apply focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:ring-opacity-50;
}

/* Custom focus styles for interactive cards */
.kanban-item:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
}

/* Never remove focus styles without providing alternative */
button:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
}
```

### Pattern: Focus Trap in Modals

```html
<!-- Modal with focus trap using Alpine.js -->
<div class="modal-backdrop"
     x-data="{ show: true }"
     x-show="show"
     x-trap.inert.noscroll="show"
     @keydown.escape="show = false">

    <div class="modal-content" @click.stop>
        <!-- Modal content -->
        <button type="button"
                @click="show = false"
                class="close-button">
            Close
        </button>

        <!-- Focusable content -->
        <input type="text" placeholder="Enter text...">

        <button type="submit">Submit</button>
    </div>
</div>
```

### Pattern: Restoring Focus After Modal Close

```javascript
// Store focus before opening modal
let previousFocus = null;

function openModal() {
    previousFocus = document.activeElement;

    // Show modal
    document.getElementById('modal').classList.remove('hidden');

    // Focus first interactive element in modal
    const firstInput = document.querySelector('#modal input, #modal button');
    if (firstInput) {
        firstInput.focus();
    }
}

function closeModal() {
    // Hide modal
    document.getElementById('modal').classList.add('hidden');

    // Restore focus
    if (previousFocus) {
        previousFocus.focus();
    }
}
```

---

## 4. ARIA Labels and Roles

### Principle
Use ARIA attributes to provide additional context for assistive technologies.

### Pattern: ARIA Labels for Icon Buttons

```html
<!-- Button with icon only -->
<button type="button"
        aria-label="Delete task"
        class="btn-icon">
    <i class="fas fa-trash" aria-hidden="true"></i>
</button>

<!-- Button with icon and text -->
<button type="button" class="btn">
    <i class="fas fa-save" aria-hidden="true"></i>
    <span>Save</span>
</button>

<!-- Link with icon -->
<a href="{% url 'task_edit' task.id %}"
   aria-label="Edit task: {{ task.title }}"
   class="btn-link">
    <i class="fas fa-pen" aria-hidden="true"></i>
</a>
```

### Pattern: ARIA Roles for Custom Components

```html
<!-- Tabs Component -->
<div class="tabs" role="tablist" aria-label="Task views">
    <button type="button"
            role="tab"
            aria-selected="true"
            aria-controls="kanban-panel"
            id="kanban-tab"
            class="tab-button">
        Kanban View
    </button>

    <button type="button"
            role="tab"
            aria-selected="false"
            aria-controls="list-panel"
            id="list-tab"
            class="tab-button">
        List View
    </button>
</div>

<div id="kanban-panel"
     role="tabpanel"
     aria-labelledby="kanban-tab">
    <!-- Kanban content -->
</div>

<div id="list-panel"
     role="tabpanel"
     aria-labelledby="list-tab"
     hidden>
    <!-- List content -->
</div>
```

### Pattern: ARIA Expanded for Collapsible Sections

```html
<button type="button"
        aria-expanded="false"
        aria-controls="advanced-filters"
        @click="expanded = !expanded"
        :aria-expanded="expanded.toString()"
        class="filter-toggle">
    Advanced Filters <i class="fas fa-chevron-down"></i>
</button>

<div id="advanced-filters"
     x-show="expanded"
     x-collapse>
    <!-- Filter options -->
</div>
```

---

## 5. Color Contrast

### Principle
Ensure sufficient color contrast ratios for text and interactive elements.

### WCAG AA Requirements
- **Normal text** (< 18px): 4.5:1 contrast ratio
- **Large text** (≥ 18px or ≥ 14px bold): 3:1 contrast ratio
- **UI components and graphics**: 3:1 contrast ratio

### Pattern: Accessible Color Palette

```css
/* Tailwind custom color palette (tailwind.config.js) */
module.exports = {
  theme: {
    extend: {
      colors: {
        // Primary (emerald) - Meets WCAG AA
        'primary-600': '#059669',  // 4.6:1 on white
        'primary-700': '#047857',  // 6.2:1 on white

        // Text colors - Meets WCAG AA
        'gray-900': '#111827',     // 16.3:1 on white
        'gray-700': '#374151',     // 10.9:1 on white
        'gray-600': '#4b5563',     // 7.6:1 on white

        // Status colors with sufficient contrast
        'success-600': '#16a34a',  // 4.5:1 on white
        'warning-700': '#b45309',  // 5.3:1 on white
        'error-600': '#dc2626',    // 5.9:1 on white
        'info-600': '#2563eb',     // 5.1:1 on white
      }
    }
  }
}
```

### Pattern: Accessible Button Styles

```html
<!-- Primary button with sufficient contrast -->
<button class="bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500">
    Submit
</button>

<!-- Secondary button with border for additional contrast -->
<button class="bg-white text-gray-700 border border-gray-300 hover:bg-gray-50">
    Cancel
</button>

<!-- Danger button with high contrast -->
<button class="bg-red-600 text-white hover:bg-red-700">
    Delete
</button>
```

### Testing Tools
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Chrome DevTools (Lighthouse Accessibility Audit)
- [Contrast Ratio Calculator](https://contrast-ratio.com/)

---

## 6. Screen Reader Support

### Principle
Provide clear, descriptive content for screen reader users.

### Pattern: Descriptive Link Text

```html
<!-- Bad: Non-descriptive link -->
<a href="{% url 'task_detail' task.id %}">Click here</a>

<!-- Good: Descriptive link -->
<a href="{% url 'task_detail' task.id %}">View details for task: {{ task.title }}</a>

<!-- Good: Using aria-label for brevity -->
<a href="{% url 'task_detail' task.id %}"
   aria-label="View task: {{ task.title }}">
    View Details
</a>
```

### Pattern: Screen Reader-Only Text

```html
<!-- Visually hidden but accessible to screen readers -->
<style>
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
</style>

<!-- Usage -->
<button type="button">
    <i class="fas fa-trash" aria-hidden="true"></i>
    <span class="sr-only">Delete task</span>
</button>

<!-- Table with screen reader-only headers -->
<table>
    <thead class="sr-only">
        <tr>
            <th>Task Name</th>
            <th>Assigned To</th>
            <th>Due Date</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <!-- Table rows -->
    </tbody>
</table>
```

### Pattern: ARIA Descriptions for Complex Widgets

```html
<!-- Data table with description -->
<div role="region"
     aria-labelledby="tasks-table-title"
     aria-describedby="tasks-table-desc">

    <h2 id="tasks-table-title">Project Tasks</h2>
    <p id="tasks-table-desc" class="sr-only">
        This table shows all tasks for the current project, sorted by due date.
        Use arrow keys to navigate between cells.
    </p>

    <table>
        <!-- Table content -->
    </table>
</div>
```

---

## 7. Form Accessibility

### Principle
Forms must be clearly labeled and provide helpful error messages.

### Pattern: Accessible Form Fields

```html
<form>
    <!-- Text input with label -->
    <div class="form-field">
        <label for="task-title" class="form-label">
            Task Title
            <span class="text-red-500" aria-label="required">*</span>
        </label>
        <input type="text"
               id="task-title"
               name="title"
               required
               aria-required="true"
               aria-describedby="title-hint"
               class="form-input">
        <p id="title-hint" class="form-hint">
            Enter a clear, descriptive title for the task
        </p>
    </div>

    <!-- Select dropdown -->
    <div class="form-field">
        <label for="task-status" class="form-label">Status</label>
        <select id="task-status"
                name="status"
                aria-describedby="status-hint"
                class="form-select">
            <option value="">Select status...</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
        </select>
        <p id="status-hint" class="form-hint">
            Current status of the task
        </p>
    </div>

    <!-- Checkbox with label -->
    <div class="form-field">
        <label class="inline-flex items-center">
            <input type="checkbox"
                   id="is-urgent"
                   name="is_urgent"
                   class="form-checkbox">
            <span class="ml-2">Mark as urgent</span>
        </label>
    </div>

    <!-- Radio buttons with fieldset -->
    <fieldset class="form-field">
        <legend class="form-label">Priority Level</legend>
        <div class="space-y-2">
            <label class="inline-flex items-center">
                <input type="radio" name="priority" value="low" class="form-radio">
                <span class="ml-2">Low</span>
            </label>
            <label class="inline-flex items-center">
                <input type="radio" name="priority" value="medium" class="form-radio">
                <span class="ml-2">Medium</span>
            </label>
            <label class="inline-flex items-center">
                <input type="radio" name="priority" value="high" class="form-radio">
                <span class="ml-2">High</span>
            </label>
        </div>
    </fieldset>
</form>
```

### Pattern: Error Messages

```html
<!-- Field with validation error -->
<div class="form-field">
    <label for="email" class="form-label">Email Address</label>
    <input type="email"
           id="email"
           name="email"
           aria-invalid="true"
           aria-describedby="email-error"
           class="form-input border-red-500">
    <p id="email-error" class="text-red-600 text-sm" role="alert">
        <i class="fas fa-exclamation-circle" aria-hidden="true"></i>
        Please enter a valid email address
    </p>
</div>

<!-- Form-level error summary -->
<div role="alert" class="alert alert-error" aria-live="assertive">
    <h3 class="font-semibold">Please correct the following errors:</h3>
    <ul class="list-disc list-inside">
        <li><a href="#task-title">Task title is required</a></li>
        <li><a href="#due-date">Due date must be in the future</a></li>
    </ul>
</div>
```

---

## 8. Dynamic Content Announcements

### Principle
Announce dynamic content changes to screen reader users.

### Pattern: ARIA Live Regions

```html
<!-- Polite announcement (non-interrupting) -->
<div aria-live="polite"
     aria-atomic="true"
     class="sr-only"
     id="status-message">
    <!-- Dynamically updated messages -->
</div>

<!-- Assertive announcement (interrupting) -->
<div aria-live="assertive"
     aria-atomic="true"
     class="sr-only"
     id="error-message">
    <!-- Critical error messages -->
</div>

<!-- Usage with HTMX -->
<div class="metrics-card"
     hx-get="{% url 'task_count' %}"
     hx-trigger="every 30s"
     hx-swap="innerHTML"
     aria-live="polite"
     aria-atomic="true">
    <span class="count">{{ task_count }}</span>
    <span>Pending Tasks</span>
</div>
```

### Pattern: Toast Notifications

```javascript
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
    toast.textContent = message;

    document.body.appendChild(toast);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Usage
showToast('Task saved successfully', 'success');
showToast('Failed to save task', 'error');
```

---

## 9. Touch Target Sizes

### Principle
Interactive elements must be large enough to tap easily on touch devices.

### WCAG AA Requirements
- Minimum touch target size: **44x44 pixels**
- Adequate spacing between touch targets

### Pattern: Touch-Friendly Buttons

```html
<!-- Minimum 44x44px touch targets -->
<button class="btn min-h-[44px] min-w-[44px] px-4 py-2">
    Click Me
</button>

<!-- Icon-only button with adequate touch target -->
<button class="btn-icon w-11 h-11 flex items-center justify-center"
        aria-label="Delete">
    <i class="fas fa-trash"></i>
</button>

<!-- Mobile menu with adequate spacing -->
<nav class="mobile-menu">
    <a href="/" class="menu-item py-3 px-4 min-h-[44px]">Home</a>
    <a href="/tasks/" class="menu-item py-3 px-4 min-h-[44px]">Tasks</a>
    <a href="/projects/" class="menu-item py-3 px-4 min-h-[44px]">Projects</a>
</nav>
```

---

## 10. Skip Navigation Links

### Principle
Provide skip links to help keyboard users bypass repetitive content.

### Pattern: Skip to Main Content

```html
<!-- At the very top of <body> -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<style>
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #000;
    color: #fff;
    padding: 8px;
    text-decoration: none;
    z-index: 10000;
}

.skip-link:focus {
    top: 0;
}
</style>

<!-- Main content area -->
<main id="main-content" tabindex="-1">
    <!-- Page content -->
</main>
```

---

## Testing Checklist

Use this checklist to verify accessibility compliance:

- [ ] All images have descriptive `alt` text
- [ ] All form fields have associated `<label>` elements
- [ ] All interactive elements are keyboard accessible
- [ ] Focus indicators are clearly visible
- [ ] Color contrast meets WCAG AA standards (4.5:1 for text)
- [ ] ARIA labels present for icon-only buttons
- [ ] Page has clear heading hierarchy (H1 → H2 → H3)
- [ ] Skip navigation link present and functional
- [ ] Dynamic content changes announced to screen readers
- [ ] Touch targets are at least 44x44 pixels
- [ ] Forms provide clear error messages
- [ ] Modals trap focus and restore focus on close
- [ ] Tables have proper headers and captions
- [ ] Links have descriptive text (not "click here")
- [ ] Video/audio content has captions/transcripts

---

## Testing Tools

### Browser Extensions
- [axe DevTools](https://www.deque.com/axe/devtools/) - Comprehensive accessibility testing
- [WAVE](https://wave.webaim.org/extension/) - Visual feedback on accessibility issues
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Built into Chrome DevTools

### Screen Readers
- **macOS**: VoiceOver (Cmd+F5)
- **Windows**: NVDA (free), JAWS
- **iOS**: VoiceOver (Settings → Accessibility)
- **Android**: TalkBack (Settings → Accessibility)

### Keyboard Testing
Test all interactions using only the keyboard:
- Tab / Shift+Tab - Navigate between interactive elements
- Enter / Space - Activate buttons and links
- Arrow keys - Navigate within components
- Escape - Close modals and dropdowns

---

## Related Documentation

- [HTMX Patterns](htmx_patterns.md)
- [Component Library Guide](component_library_guide.md)
- [Mobile Responsiveness](mobile_patterns.md)
