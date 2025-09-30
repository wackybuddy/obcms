# OBC Management System - UI Design System

## Table of Contents
- [Overview](#overview)
- [Color Palette](#color-palette)
- [Typography](#typography)
- [Components](#components)
- [Layout System](#layout-system)
- [Admin Interface](#admin-interface)
- [Responsive Design](#responsive-design)
- [Accessibility](#accessibility)
- [Development Guidelines](#development-guidelines)

## Overview

The OBC (Office for Other Bangsamoro Communities) Management System features a modern, government-appropriate design system built on Tailwind CSS with custom components. The design emphasizes accessibility, cultural sensitivity, and professional aesthetics suitable for government operations.

### Design Principles
- **Cultural Respect**: Colors and design elements that honor Bangsamoro heritage
- **Accessibility**: WCAG 2.1 AA compliance with proper contrast ratios
- **Professional**: Clean, modern interface suitable for government use
- **Responsive**: Mobile-first design that works across all devices
- **Consistent**: Unified visual language across all modules

## Color Palette

### Primary Colors
The system uses a distinctive blue-to-teal gradient as the primary color scheme, representing stability and trust.

```css
/* Primary Blue-to-Teal Gradient */
--primary-blue: #1e40af;        /* Main brand blue */
--primary-teal: #059669;        /* Main brand teal */
--primary-blue-light: #3b82f6;  /* Lighter blue variant */
--primary-teal-light: #10b981;  /* Lighter teal variant */
--primary-blue-dark: #1d4ed8;   /* Darker blue for hover states */
--primary-teal-dark: #047857;   /* Darker teal for hover states */
```

### Secondary Colors
```css
/* Secondary Palette */
--secondary-coral: #f472b6;     /* Accent coral */
--secondary-purple: #8b5cf6;    /* Accent purple */
--tertiary-amber: #f59e0b;      /* Warning/attention color */
```

### Status Colors
```css
/* Status and Feedback Colors */
--success-green: #10b981;       /* Success messages */
--error-red: #ef4444;           /* Error messages */
--warning-yellow: #f59e0b;      /* Warning messages */
```

### Neutral Colors
```css
/* Neutral Palette */
--neutral-50: #f9fafb;          /* Lightest gray */
--neutral-100: #f3f4f6;         /* Light gray backgrounds */
--neutral-200: #e5e7eb;         /* Borders */
--neutral-300: #d1d5db;         /* Input borders */
--neutral-400: #9ca3af;         /* Placeholder text */
--neutral-500: #6b7280;         /* Secondary text */
--neutral-600: #4b5563;         /* Primary text */
--neutral-700: #374151;         /* Headings */
--neutral-800: #1f2937;         /* Dark text */
--neutral-900: #111827;         /* Darkest text */
```

### Gradient Classes
```css
/* Primary Gradients */
.bg-bangsamoro-gradient {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-teal) 100%);
}

.bg-bangsamoro-reverse {
    background: linear-gradient(135deg, var(--primary-teal) 0%, var(--primary-blue) 100%);
}
```

## Typography

### Font Stack
```css
font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
```

### Text Colors
- **Primary Text**: `text-neutral-800` (#1f2937)
- **Secondary Text**: `text-neutral-600` (#4b5563)
- **Muted Text**: `text-neutral-500` (#6b7280)
- **Brand Text**: `text-bangsamoro` (--primary-blue)

### Heading Styles
```html
<!-- H1 - Page Titles -->
<h1 class="text-3xl font-bold text-neutral-800 mb-6">Page Title</h1>

<!-- H2 - Section Headers -->
<h2 class="text-2xl font-semibold text-neutral-700 mb-4">Section Header</h2>

<!-- H3 - Subsection Headers -->
<h3 class="text-xl font-medium text-neutral-700 mb-3">Subsection Header</h3>
```

## Components

### Buttons

#### Primary Button
```html
<button class="btn-primary px-6 py-3 rounded-lg font-semibold transition-all duration-300 hover:transform hover:translate-y-[-2px] hover:shadow-lg">
    Primary Action
</button>
```

#### Secondary Button
```html
<button class="btn-secondary px-6 py-3 rounded-lg font-semibold transition-all duration-300">
    Secondary Action
</button>
```

#### Button Variants
- **Primary**: Blue-to-teal gradient for main actions
- **Secondary**: Coral-to-purple gradient for secondary actions
- **Tertiary**: Amber for warning/attention actions
- **Success**: Green for positive actions
- **Danger**: Red for destructive actions

### Cards

#### Standard Card
```html
<div class="bg-white rounded-xl shadow-md border border-neutral-200 p-6">
    <h3 class="text-lg font-semibold text-neutral-800 mb-3">Card Title</h3>
    <p class="text-neutral-600">Card content goes here...</p>
</div>
```

#### Gradient Card
```html
<div class="card-gradient rounded-xl shadow-md p-6">
    <h3 class="text-lg font-semibold text-neutral-800 mb-3">Enhanced Card</h3>
    <p class="text-neutral-600">Card with subtle gradient background...</p>
</div>
```

### Forms

#### Input Fields
```html
<div class="mb-4">
    <label class="block text-sm font-medium text-neutral-700 mb-2">Field Label</label>
    <input type="text" 
           class="w-full px-4 py-3 border-2 border-neutral-300 rounded-lg focus:border-primary-blue focus:ring focus:ring-primary-blue focus:ring-opacity-20 transition-all duration-200">
</div>
```

#### Select Dropdowns
```html
<select class="w-full px-4 py-3 border-2 border-neutral-300 rounded-lg focus:border-primary-blue focus:ring focus:ring-primary-blue focus:ring-opacity-20">
    <option value="">Choose an option</option>
    <option value="1">Option 1</option>
</select>
```

### Navigation

#### Main Navigation
The navigation uses a responsive design with mobile-first approach:

```html
<nav class="bg-bangsamoro-gradient shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Navigation content -->
    </div>
</nav>
```

#### Navigation Items
```html
<a href="#" class="nav-item text-white hover:bg-white hover:bg-opacity-10 px-3 py-2 rounded-md transition-all duration-200">
    <i class="fas fa-home mr-2"></i>
    Home
</a>
```

### Status Indicators

#### Success
```html
<div class="status-success px-4 py-2 rounded-lg">
    <i class="fas fa-check-circle mr-2"></i>
    Success message
</div>
```

#### Error
```html
<div class="status-error px-4 py-2 rounded-lg">
    <i class="fas fa-exclamation-triangle mr-2"></i>
    Error message
</div>
```

#### Warning
```html
<div class="status-warning px-4 py-2 rounded-lg">
    <i class="fas fa-exclamation-circle mr-2"></i>
    Warning message
</div>
```

## Layout System

### Container Classes
```html
<!-- Maximum width container -->
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Content -->
</div>

<!-- Content sections -->
<div class="py-8">
    <div class="max-w-4xl mx-auto">
        <!-- Section content -->
    </div>
</div>
```

### Grid System
```html
<!-- 2-column grid -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div>Column 1</div>
    <div>Column 2</div>
</div>

<!-- 3-column grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div>Column 1</div>
    <div>Column 2</div>
    <div>Column 3</div>
</div>
```

### Spacing System
- **xs**: `0.25rem` (4px)
- **sm**: `0.5rem` (8px)
- **md**: `1rem` (16px)
- **lg**: `1.5rem` (24px)
- **xl**: `2rem` (32px)
- **2xl**: `3rem` (48px)

## Admin Interface

The Django admin interface has been extensively customized to match the system's design language.

### Key Features
- **Gradient Headers**: Blue-to-teal gradient for admin headers
- **Modern Cards**: Rounded corners with subtle shadows
- **Enhanced Forms**: Improved input styling with focus states
- **Custom Buttons**: Consistent button styling across admin interface
- **Color-coded Actions**: Status-based color coding for admin actions

### Admin CSS Architecture
```css
/* Admin color variables */
:root {
    --primary-blue: #1e40af;
    --primary-teal: #059669;
    --gradient-primary: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-teal) 100%);
}

/* Header styling */
#header {
    background: var(--gradient-primary) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Module cards */
.module {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--neutral-200);
}
```

## Responsive Design

### Breakpoints
- **sm**: `640px` - Small tablets
- **md**: `768px` - Large tablets
- **lg**: `1024px` - Small desktops
- **xl**: `1280px` - Large desktops
- **2xl**: `1536px` - Extra large screens

### Mobile-First Approach
```html
<!-- Responsive classes -->
<div class="flex flex-col lg:flex-row">
    <div class="w-full lg:w-1/3">Sidebar</div>
    <div class="w-full lg:w-2/3">Main content</div>
</div>
```

### Mobile Navigation
```html
<!-- Mobile menu button -->
<button onclick="toggleMobileMenu()" class="lg:hidden">
    <i class="fas fa-bars"></i>
</button>

<!-- Mobile menu -->
<div id="mobileMenu" class="hidden lg:hidden">
    <!-- Mobile navigation items -->
</div>
```

## Accessibility

### WCAG 2.1 AA Compliance
- **Color Contrast**: All text meets minimum contrast ratios
- **Focus Indicators**: Visible focus states for keyboard navigation
- **Semantic HTML**: Proper heading hierarchy and landmarks
- **Alt Text**: Images include descriptive alt text
- **Screen Reader Support**: ARIA labels and descriptions where needed

### Focus Management
```css
/* Focus states */
.focus-bangsamoro:focus {
    outline: none;
    ring: 2px solid var(--primary-blue);
    border-color: var(--primary-blue);
}
```

### Keyboard Navigation
- **Tab Order**: Logical tab progression through interface
- **Skip Links**: Available for screen reader users
- **Escape Key**: Closes modals and dropdowns

## Development Guidelines

### CSS Architecture
1. **Use CSS Custom Properties**: Leverage CSS variables for consistency
2. **Component-Based**: Build reusable UI components
3. **Mobile-First**: Start with mobile styles, enhance for larger screens
4. **Performance**: Minimize CSS bundle size and optimize loading

### File Structure
```
src/static/css/
├── admin/css/custom.css          # Django admin customization
└── main.css                      # Main application styles

src/templates/
├── base.html                     # Base template with design system
├── admin/                        # Admin template overrides
└── common/                       # Shared UI components
```

### Best Practices

#### CSS
```css
/* Use CSS custom properties */
.component {
    color: var(--primary-blue);
    background: var(--gradient-primary);
}

/* Follow BEM naming convention for custom components */
.card {}
.card__header {}
.card__content {}
.card--featured {}
```

#### HTML
```html
<!-- Use semantic HTML elements -->
<main>
    <section aria-labelledby="section-title">
        <h2 id="section-title">Section Title</h2>
        <!-- Section content -->
    </section>
</main>

<!-- Include proper ARIA attributes -->
<button aria-expanded="false" aria-controls="dropdown-menu">
    Menu
</button>
```

#### Tailwind Classes
```html
<!-- Prefer utility classes for common patterns -->
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
    <!-- Content -->
</div>

<!-- Use custom components for complex patterns -->
<button class="btn-primary">
    Primary Action
</button>
```

### Testing
- **Cross-browser Testing**: Test in Chrome, Firefox, Safari, Edge
- **Device Testing**: Test on various screen sizes and devices
- **Accessibility Testing**: Use screen readers and keyboard navigation
- **Performance Testing**: Monitor CSS bundle size and loading times

### Maintenance
- **Regular Audits**: Review and update design system components
- **Documentation Updates**: Keep documentation current with changes
- **User Feedback**: Incorporate user testing insights
- **Performance Monitoring**: Track and optimize UI performance metrics

---

## Additional Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Django Admin Customization](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)

---

*Last Updated: {{ current_date }}*
*Version: 1.0*