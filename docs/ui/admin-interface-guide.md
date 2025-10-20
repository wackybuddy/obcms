# OBC Management System - Admin Interface Guide

## Table of Contents
- [Overview](#overview)
- [Admin Customization Architecture](#admin-customization-architecture)
- [Visual Design](#visual-design)
- [Component Styling](#component-styling)
- [Responsive Features](#responsive-features)
- [Development Guidelines](#development-guidelines)
- [Troubleshooting](#troubleshooting)

## Overview

The OBC Management System features a completely redesigned Django admin interface that aligns with the main system's design language. The admin interface maintains all Django admin functionality while providing a modern, professional appearance suitable for government operations.

### Key Features
- **Consistent Branding**: Matches the main system's blue-to-teal gradient theme
- **Modern UI**: Card-based layouts with rounded corners and shadows
- **Enhanced UX**: Improved form styling, button design, and visual hierarchy
- **Responsive Design**: Mobile-friendly admin interface
- **Accessibility**: WCAG 2.1 AA compliant with proper focus states
- **Dark Mode Support**: Automatic dark mode detection and styling

## Admin Customization Architecture

### File Structure
```
src/
├── static/admin/css/
│   └── custom.css                 # Main admin customization file
├── templates/admin/
│   ├── base_site.html            # Admin base template override
│   ├── base.html                 # Admin layout customization
│   ├── change_form.html          # Form page customization
│   ├── change_list.html          # List page customization
│   └── index.html                # Admin dashboard customization
```

### CSS Variables System
The admin interface uses the same CSS custom properties as the main system:

```css
:root {
    /* Primary Colors */
    --primary-blue: #1e40af;
    --primary-teal: #059669;
    --gradient-primary: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-teal) 100%);
    
    /* Status Colors */
    --success-green: #10b981;
    --error-red: #ef4444;
    --warning-yellow: #f59e0b;
    
    /* Neutral Palette */
    --neutral-50: #f9fafb;
    --neutral-100: #f3f4f6;
    --neutral-800: #1f2937;
    --neutral-900: #111827;
}
```

## Visual Design

### Header and Branding
```css
/* Admin header with gradient background */
#header {
    background: var(--gradient-primary) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    border-bottom: none;
}

/* Site name styling */
#site-name a {
    color: white;
    font-weight: 700;
    font-size: 1.5rem;
    display: flex;
    align-items: center;
}
```

### Cards and Modules
```css
/* Modern card styling for admin modules */
.module, .inline-group, .results {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--neutral-200);
    margin-bottom: 2rem;
    overflow: hidden;
}

/* Module headers with gradient */
.module h2, .inline-group h2 {
    background: var(--gradient-primary);
    color: white;
    padding: 1rem 1.5rem;
    font-weight: 600;
    font-size: 1.125rem;
}
```

### Navigation Enhancement
```html
<!-- Enhanced admin navigation with icons -->
<div id="user-tools">
    <a href="{% url 'common:dashboard' %}">
        <i class="fas fa-external-link-alt mr-1"></i>
        View System
    </a>
    <a href="{% url 'admin:password_change' %}">
        <i class="fas fa-key mr-1"></i>
        Change password
    </a>
    <a href="{% url 'admin:logout' %}">
        <i class="fas fa-sign-out-alt mr-1"></i>
        Log out
    </a>
</div>
```

## Component Styling

### Buttons

#### Primary Buttons
```css
.button, input[type=submit], input[type=button] {
    background: var(--gradient-primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.button:hover, input[type=submit]:hover {
    background: var(--gradient-primary-hover) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
}
```

#### Specialized Buttons
```css
/* Save button */
.submit-row input[name="_save"] {
    background: var(--success-green) !important;
    border: 2px solid var(--primary-teal-dark) !important;
}

/* Delete button */
.deletelink {
    background: var(--error-red) !important;
    border: 2px solid #dc2626 !important;
}

/* Add button */
.addlink, .object-tools a {
    background: var(--success-green) !important;
    color: white !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem 1.5rem !important;
    text-decoration: none !important;
    font-weight: 600 !important;
}

.addlink:before, .object-tools a:before {
    content: "➕" !important;
}
```

### Forms and Inputs

#### Input Fields
```css
input[type="text"], input[type="email"], input[type="number"], 
input[type="password"], textarea, select {
    border: 2px solid var(--neutral-300) !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.875rem !important;
    transition: all 0.2s ease !important;
    background-color: white !important;
    color: var(--neutral-800) !important;
}

/* Focus states */
input:focus, textarea:focus, select:focus {
    border-color: var(--primary-blue) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1) !important;
    background-color: var(--neutral-50) !important;
}
```

#### Form Rows
```css
.form-row {
    border-bottom: 1px solid var(--neutral-100) !important;
    padding: 1.25rem 1.5rem !important;
    transition: background-color 0.2s ease !important;
}

.form-row:hover {
    background-color: var(--neutral-50) !important;
}

.form-row label {
    font-weight: 600 !important;
    color: var(--neutral-700) !important;
    margin-bottom: 0.5rem !important;
    display: block !important;
    font-size: 0.875rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
```

### Tables

#### Table Headers
```css
thead th {
    background: var(--gradient-primary) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 1rem 1.5rem !important;
    text-align: left !important;
    font-size: 0.875rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 10 !important;
}
```

#### Table Rows
```css
tbody tr {
    border-bottom: 1px solid var(--neutral-200) !important;
    transition: background-color 0.2s ease !important;
}

tbody tr:hover {
    background-color: var(--neutral-50) !important;
}

tbody td {
    padding: 1rem 1.5rem !important;
    vertical-align: top !important;
    border: none !important;
}
```

### Filter Sidebar
```css
#changelist-filter {
    background: white !important;
    border-radius: 0.75rem !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid var(--neutral-200) !important;
    padding: 0 !important;
    margin-left: 1.5rem !important;
}

#changelist-filter h3 {
    background: var(--gradient-secondary) !important;
    color: white !important;
    padding: 1rem 1.5rem !important;
    margin: 0 !important;
    font-weight: 600 !important;
    border-radius: 0.75rem 0.75rem 0 0 !important;
}
```

### Search Bar
```css
#changelist-search {
    background: white !important;
    border-radius: 0.75rem !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid var(--neutral-200) !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

#searchbar {
    border: 2px solid var(--neutral-300) !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.875rem !important;
    width: 300px !important;
    margin-right: 1rem !important;
}
```

## Responsive Features

### Mobile Adaptations
```css
@media (max-width: 768px) {
    #content {
        padding: 1rem !important;
    }
    
    .form-row {
        padding: 1rem !important;
    }
    
    .module h2, .inline-group h2 {
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    #changelist-filter {
        margin-left: 0 !important;
        margin-top: 1.5rem !important;
    }
    
    .actions {
        flex-direction: column !important;
        gap: 1rem !important;
    }
}
```

### Touch Device Optimizations
```css
.touch-device .nav-item {
    padding: 0.75rem 1rem;
}

.touch-device .user-dropdown button {
    width: 2.5rem;
    height: 2.5rem;
}
```

## Development Guidelines

### Adding Custom Admin Styles

#### Step 1: Extend base_site.html
```html
<!-- src/templates/admin/base_site.html -->
{% extends "admin/base.html" %}
{% load i18n static %}

{% block extrastyle %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="{% static 'admin/css/custom.css' %}">
{% endblock %}
```

#### Step 2: Add Custom CSS Rules
```css
/* Add to src/static/admin/css/custom.css */
.custom-admin-component {
    background: var(--gradient-primary);
    color: white;
    border-radius: 0.5rem;
    padding: 1rem;
}
```

#### Step 3: Override Admin Templates
```html
<!-- src/templates/admin/change_form.html -->
{% extends "admin/change_form.html" %}

{% block submit_buttons_bottom %}
<div class="submit-row custom-submit-row">
    {{ block.super }}
    <button type="button" class="btn-secondary">Custom Action</button>
</div>
{% endblock %}
```

### Custom Admin Actions Styling

#### Colored Status Display
```python
# In admin.py
def colored_status(self, obj):
    """Display development status with color coding."""
    colors = {
        'developing': 'orange',
        'established': 'green',
        'vulnerable': 'red',
        'thriving': 'blue',
    }
    color = colors.get(obj.development_status, 'black')
    return format_html(
        '<span style="color: {}; font-weight: bold;">{}</span>',
        color,
        obj.get_development_status_display()
    )
colored_status.short_description = 'Status'
```

#### Enhanced List Display
```python
class OBCCommunityAdmin(admin.ModelAdmin):
    list_display = ('barangay', 'municipality', 'province', 'region', 
                   'estimated_obc_population', 'households', 'colored_status')
    
    def colored_status(self, obj):
        # Custom color-coded status display
        pass
```

### Working with Fieldsets
```python
fieldsets = (
    ('Basic Information', {
        'fields': ('name', 'type', 'status'),
        'classes': ('wide',)  # Makes fieldset wider
    }),
    ('Advanced Options', {
        'fields': ('advanced_field_1', 'advanced_field_2'),
        'classes': ('collapse',)  # Makes fieldset collapsible
    }),
)
```

## Accessibility Features

### Focus Management
```css
/* Enhanced focus states for accessibility */
button:focus, input:focus, select:focus, textarea:focus, a:focus {
    outline: 2px solid var(--primary-blue) !important;
    outline-offset: 2px !important;
}

.button:focus-visible, input[type="submit"]:focus-visible {
    outline: 2px solid white !important;
    outline-offset: 2px !important;
}
```

### High Contrast Mode
```css
@media (prefers-contrast: high) {
    .button, input[type=submit], input[type=button] {
        border: 2px solid var(--neutral-800) !important;
    }
    
    input[type="text"], input[type="email"], textarea, select {
        border-width: 3px !important;
    }
}
```

### Dark Mode Support
```css
@media (prefers-color-scheme: dark) {
    body {
        background-color: var(--neutral-900) !important;
        color: var(--neutral-200) !important;
    }
    
    .module, .inline-group, .results {
        background: var(--neutral-800) !important;
        border-color: var(--neutral-700) !important;
    }
    
    input[type="text"], textarea, select {
        background-color: var(--neutral-800) !important;
        border-color: var(--neutral-600) !important;
        color: var(--neutral-200) !important;
    }
}
```

## Troubleshooting

### Common Issues

#### CSS Not Loading
**Problem**: Custom admin styles not appearing
**Solution**: 
1. Check that `{% load static %}` is at the top of your template
2. Verify the CSS file path in `{% static 'admin/css/custom.css' %}`
3. Run `./manage.py collectstatic` if using static file serving
4. Clear browser cache

#### Responsive Issues
**Problem**: Admin interface not responsive on mobile
**Solution**:
1. Ensure viewport meta tag is present in base template
2. Check media queries are properly formatted
3. Test across different device sizes

#### Button Styling Conflicts
**Problem**: Buttons not inheriting custom styles
**Solution**:
1. Use `!important` declarations for admin overrides
2. Check CSS specificity - admin styles may need higher specificity
3. Verify button selectors match Django's admin HTML structure

### Browser Compatibility
- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support (webkit prefixes included)
- **Edge**: Full support
- **Internet Explorer**: Not supported (uses modern CSS features)

### Performance Considerations
- **CSS Bundle Size**: Keep custom CSS minimal and focused
- **Render Performance**: Use CSS transforms for animations
- **Mobile Performance**: Optimize for touch interactions
- **Loading Speed**: Minimize external dependencies

---

## Quick Reference

### CSS Classes for Common Tasks
```css
/* Status indicators */
.status-success    /* Green background for success */
.status-error      /* Red background for errors */
.status-warning    /* Yellow background for warnings */
.status-info       /* Blue gradient for information */

/* Interactive elements */
.hover-lift        /* Adds lift effect on hover */
.hover-gradient    /* Changes to gradient on hover */
.nav-item          /* Navigation item styling */

/* Layout utilities */
.card-gradient     /* Card with subtle gradient */
.card-teal-gradient /* Card with teal gradient */
```

### Essential Admin Selectors
```css
#header            /* Admin header */
#site-name         /* Site branding */
#user-tools        /* User navigation */
.module            /* Admin content modules */
.form-row          /* Form field rows */
.submit-row        /* Form submission area */
#changelist-filter /* Filter sidebar */
#changelist-search /* Search bar */
```

---

*For more information, see the main [UI Design System Guide](ui-design-system.md)*

*Last Updated: {{ current_date }}*
*Version: 1.0*
