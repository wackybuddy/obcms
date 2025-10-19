# Frontend Component Scaffolder (HTMX/Tailwind) - OBCMS/BMMS

## Overview

This skill provides automated scaffolding for frontend components in the OBCMS/BMMS system, ensuring strict adherence to the established design system, component architecture, and the distinctive Bangsamoro color scheme. The skill generates production-ready HTMX partials, Django templates, and Alpine.js-enhanced components that seamlessly integrate with the existing codebase.

## Purpose

The Frontend Component Scaffolder solves several critical challenges in the OBCMS/BMMS development workflow. First, it guarantees complete consistency across all frontend components by enforcing the custom Bangsamoro color scheme (Ocean Blue to Teal to Emerald gradient) and the established component patterns. Second, it dramatically accelerates development by eliminating the need to write repetitive boilerplate code for modals, data tables, forms, and cards. Third, it reduces human error by automatically applying correct HTMX attributes, Alpine.js directives, and Tailwind utility classes according to proven patterns. Fourth, it ensures accessibility standards are met through proper ARIA attributes and semantic HTML structure. Finally, it maintains a unified design language throughout the entire application, preventing style drift and inconsistencies.

## Design System

### Bangsamoro Color Palette

The OBCMS/BMMS system uses a distinctive color scheme that reflects the natural beauty and cultural identity of the Bangsamoro region. This palette must be strictly adhered to in all generated components.

#### Ocean Blue (Primary Brand Color)
Ocean Blue serves as the primary brand color, representing the waters surrounding the Bangsamoro region. This color should be used for primary actions, headers, and key interactive elements.

```
ocean-50:  #e0f2fe (Lightest backgrounds)
ocean-100: #bae6fd (Subtle backgrounds)
ocean-200: #7dd3fc (Hover states)
ocean-300: #38bdf8 (Active states)
ocean-400: #0ea5e9 (Interactive elements)
ocean-500: #0284c7 (Primary buttons)
ocean-600: #0369a1 (Primary text - WCAG AA compliant)
ocean-700: #075985 (Strong emphasis - WCAG AAA)
ocean-800: #0c4a6e (Body text safe)
ocean-900: #082f49 (Headers - highest contrast)
```

#### Teal (Secondary/Transition Color)
Teal bridges the gap between Ocean Blue and Emerald, creating smooth visual transitions and representing growth and balance.

```
teal-50:  #f0fdfa (Lightest backgrounds)
teal-100: #ccfbf1 (Subtle backgrounds)
teal-200: #99f6e4 (Hover states)
teal-300: #5eead4 (Active states)
teal-400: #2dd4bf (Interactive elements)
teal-500: #14b8a6 (Secondary actions)
teal-600: #0d9488 (Secondary text)
teal-700: #0f766e (Strong emphasis)
teal-800: #115e59 (Body text)
teal-900: #134e4a (Headers)
```

#### Emerald (Success/Growth Color)
Emerald represents prosperity, growth, and successful outcomes. Use this color for success states, completion indicators, and positive feedback.

```
emerald-50:  #ecfdf5 (Lightest backgrounds)
emerald-100: #d1fae5 (Subtle backgrounds)
emerald-200: #a7f3d0 (Hover states)
emerald-300: #6ee7b7 (Active states)
emerald-400: #34d399 (Interactive elements)
emerald-500: #10b981 (Success buttons)
emerald-600: #059669 (Success text)
emerald-700: #047857 (Strong emphasis)
emerald-800: #065f46 (Body text)
emerald-900: #064e3b (Headers)
```

#### Gold/Amber (Warnings & Highlights)
Gold represents prosperity, warnings, and important highlights. Use sparingly for warnings, premium features, or special attention areas.

```
gold-50:  #fffbeb (Lightest backgrounds)
gold-100: #fef3c7 (Subtle backgrounds)
gold-200: #fde68a (Hover states)
gold-300: #fcd34d (Active states)
gold-400: #fbbf24 (Interactive elements)
gold-500: #f59e0b (Warning buttons)
gold-600: #d97706 (Warning text)
gold-700: #b45309 (Strong emphasis)
gold-800: #92400e (Body text)
gold-900: #78350f (Headers)
```

### Gradient Backgrounds

The system includes pre-defined gradients that should be used for headers, cards, and special emphasis areas.

#### Primary Brand Gradient
The signature gradient that should be used for main application headers, hero sections, and primary branding elements.
```css
bg-gradient-primary: linear-gradient(135deg, #0369a1 0%, #0d9488 50%, #059669 100%)
```

#### Ocean Gradients
```css
bg-gradient-ocean: radial-gradient(circle at top left, #0ea5e9 0%, #0284c7 100%)
bg-gradient-ocean-linear: linear-gradient(135deg, #0284c7 0%, #0369a1 100%)
```

#### Emerald Gradients
```css
bg-gradient-emerald: radial-gradient(circle at bottom right, #10b981 0%, #059669 100%)
bg-gradient-emerald-linear: linear-gradient(135deg, #10b981 0%, #059669 100%)
```

#### Teal Gradients
```css
bg-gradient-teal-flow: linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%)
bg-gradient-teal: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)
```

#### Gold Gradients
```css
bg-gradient-gold: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)
bg-gradient-gold-shine: linear-gradient(135deg, #fef3c7 0%, #fbbf24 50%, #f59e0b 100%)
```

#### Special Purpose Gradients
```css
bg-gradient-sunrise: linear-gradient(135deg, #0ea5e9 0%, #14b8a6 33%, #fbbf24 66%, #f59e0b 100%)
bg-gradient-hero: linear-gradient(135deg, #0c4a6e 0%, #075985 50%, #0369a1 100%)
bg-gradient-bg-ocean: linear-gradient(180deg, rgba(14, 165, 233, 0.05) 0%, rgba(20, 184, 166, 0.03) 50%, transparent 100%)
```

## Component Architecture

### Component Types

The OBCMS/BMMS system uses several standard component types, each with specific purposes and patterns.

#### 1. Modals
Modals are overlay dialogs used for focused interactions, forms, confirmations, and detailed views. The system uses Alpine.js for state management and smooth transitions.

**Key Features:**
- Alpine.js-based show/hide state management
- Smooth fade and scale transitions
- Keyboard accessibility (ESC key support)
- Focus trap for accessibility
- Backdrop dismiss capability
- Multiple size options (sm, md, lg, xl, full)
- Automatic scroll lock
- Vanilla JS fallback for non-Alpine environments

**Usage Pattern:**
```django
{% include 'components/modal.html' with modal_id='my-modal' title='Modal Title' size='lg' content_template='path/to/content.html' %}
```

#### 2. Data Table Cards
Data Table Cards present tabular data with consistent styling, actions, and responsive behavior. They support sorting, filtering, and various action buttons.

**Key Features:**
- Responsive column layouts
- Gradient header with custom accent colors
- Configurable action buttons (view, edit, delete, restore)
- Empty state handling
- Custom footer support
- Mobile-responsive design
- HTMX-compatible partial rendering

**Usage Pattern:**
```django
{% include 'components/data_table_card.html' with title='Organizations' icon_class='fas fa-building' accent_class='bg-gradient-ocean' headers=headers rows=rows %}
```

#### 3. Form Components
Form components ensure consistent input styling, validation feedback, and accessibility across the application.

**Key Features:**
- Label and input pairing
- Error state display
- Help text support
- Required field indicators
- Icon integration
- Multiple input types (text, select, textarea, date, etc.)
- HTMX validation support

#### 4. Cards & Stat Cards
Cards are flexible containers for grouping related content, while Stat Cards display key metrics and statistics.

**Key Features:**
- Gradient headers
- Icon support
- Footer actions
- Stat change indicators
- Responsive layouts
- Hover effects

#### 5. HTMX Partials
Partials are reusable template fragments designed for dynamic loading and updates via HTMX.

**Key Features:**
- Self-contained HTML fragments
- HTMX attribute patterns
- Alpine.js reactive state
- Event-driven updates
- OOB swap support
- Optimistic UI updates

## HTMX Patterns & Best Practices

### Core HTMX Attributes

The OBCMS/BMMS system uses specific HTMX patterns for consistency and reliability.

#### Standard Attribute Pattern
```html
<div hx-get="/api/endpoint" 
     hx-target="#result-container"
     hx-swap="innerHTML"
     hx-trigger="load"
     hx-indicator="#loading-spinner">
</div>
```

#### Common Triggers
- `hx-trigger="load"` - Load immediately on page load
- `hx-trigger="click"` - Trigger on click (default for buttons/links)
- `hx-trigger="change"` - Trigger on form field change
- `hx-trigger="keyup changed delay:500ms"` - Search with debounce
- `hx-trigger="revealed"` - Infinite scroll pattern

#### Swap Strategies
- `hx-swap="innerHTML"` - Replace inner content (most common)
- `hx-swap="outerHTML"` - Replace entire element
- `hx-swap="beforebegin"` - Insert before element
- `hx-swap="afterend"` - Insert after element
- `hx-swap="delete"` - Remove element after successful response
- `hx-swap="none"` - Don't swap content (useful for side effects)

#### Out-of-Band Swaps
For updating multiple page sections from a single request:
```html
<!-- In response HTML -->
<div id="main-content">Updated content</div>
<div hx-swap-oob="innerHTML:#notification">New notification</div>
<div hx-swap-oob="innerHTML:#stats">Updated stats</div>
```

### Alpine.js Integration

Alpine.js provides reactive state management and UI interactions.

#### Basic Alpine Component Pattern
```html
<div x-data="{ open: false, selectedItems: [] }" class="component-container">
    <button @click="open = !open" class="toggle-button">
        Toggle Panel
    </button>
    <div x-show="open" 
         x-transition:enter="transition ease-out duration-200"
         x-transition:enter-start="opacity-0 scale-95"
         x-transition:enter-end="opacity-100 scale-100"
         class="panel">
        Panel content
    </div>
</div>
```

#### Common Alpine Directives
- `x-data` - Component state initialization
- `x-show` - Toggle visibility (keeps element in DOM)
- `x-if` - Conditional rendering (removes from DOM)
- `x-for` - List rendering
- `x-model` - Two-way data binding
- `x-bind` or `:` - Bind attributes
- `x-on` or `@` - Event listeners
- `x-transition` - Enter/leave transitions
- `x-init` - Component initialization logic
- `x-effect` - Reactive side effects

## Using the Scaffolder

### Prerequisites

Before using the scaffolder, ensure you have the following environment set up:

1. Python 3.8 or higher installed
2. Access to the OBCMS/BMMS project directory
3. Write permissions to the `src/templates` directory
4. Basic understanding of Django template syntax
5. Familiarity with HTMX and Alpine.js concepts

### Installation

The scaffolder is already included in your `.claude/skills` directory. No additional installation is required.

### Basic Usage

#### Generating a Standard Modal Component

To generate a new modal component for a specific feature:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type modal \
    --name user_edit_modal \
    --title "Edit User Profile" \
    --size lg \
    --output src/templates/common/partials/
```

This creates a file `src/templates/common/partials/user_edit_modal.html` with:
- Proper modal structure
- Alpine.js state management
- Accessibility attributes
- Custom title
- Large size configuration
- Bangsamoro color scheme

#### Generating a Data Table Card

To generate a data table card for displaying records:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type data_table \
    --name organizations_table \
    --title "Organizations Registry" \
    --icon "fas fa-building" \
    --accent ocean \
    --columns "Name,Type,Location,Status,Members" \
    --output src/templates/coordination/partials/
```

This creates `src/templates/coordination/partials/organizations_table.html` with:
- Table structure with specified columns
- Ocean gradient header
- Building icon
- Standard action buttons
- Responsive layout

#### Generating a Form Component

To generate a comprehensive form:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type form \
    --name partnership_form \
    --title "Create Partnership" \
    --fields "organization:select,contact_person:text,email:email,start_date:date,description:textarea" \
    --submit_text "Create Partnership" \
    --submit_color ocean \
    --output src/templates/coordination/partials/
```

This creates a complete form with:
- All specified fields with proper types
- Label and error handling
- Submit button with Ocean color scheme
- HTMX integration hooks
- Accessibility attributes

#### Generating a Stat Card

To generate a statistics display card:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type stat_card \
    --name active_partnerships_stat \
    --title "Active Partnerships" \
    --icon "fas fa-handshake" \
    --accent emerald \
    --value "142" \
    --change "+12%" \
    --trend up \
    --output src/templates/coordination/partials/
```

This creates a stat card with:
- Emerald gradient styling
- Handshake icon
- Value display
- Trend indicator
- Percentage change

#### Generating an HTMX Partial

To generate a dynamic partial for HTMX loading:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type htmx_partial \
    --name partnership_row \
    --entity partnership \
    --fields "name,organization,status,start_date" \
    --actions "view,edit,delete" \
    --output src/templates/coordination/partials/
```

This creates an HTMX-ready partial with:
- Self-contained row structure
- Dynamic field rendering
- Action buttons with proper URLs
- HTMX attributes for updates
- OOB swap support

### Advanced Usage

#### Custom Component Templates

You can extend the scaffolder with custom templates:

1. Create a template file in `.claude/skills/frontend-component-scaffolder/templates/custom/`
2. Use Jinja2 syntax with the same variables as standard templates
3. Reference it when generating:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type custom \
    --template custom/my_special_component.html.j2 \
    --name my_component \
    --output src/templates/
```

#### Batch Generation

To generate multiple components at once, create a configuration file:

```yaml
# components.yaml
components:
  - type: modal
    name: user_create_modal
    title: "Create New User"
    size: lg
    output: src/templates/common/partials/

  - type: data_table
    name: users_table
    title: "System Users"
    icon: "fas fa-users"
    accent: ocean
    columns: "Username,Email,Role,Status,Last Login"
    output: src/templates/common/partials/

  - type: form
    name: user_form
    title: "User Information"
    fields: "username:text,email:email,role:select,is_active:checkbox"
    output: src/templates/common/partials/
```

Then run:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/batch_generate.py \
    --config components.yaml
```

#### Component Modification

To modify an existing component while preserving custom changes:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/modify_component.py \
    --file src/templates/common/partials/user_modal.html \
    --add-field "phone_number:tel" \
    --change-accent teal \
    --preserve-custom
```

This updates the component while keeping any custom modifications you've made outside the generated sections.

## Component Templates Reference

### Modal Template Variables

When generating modals, the following variables are available:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `modal_id` | string | Unique identifier for the modal | `user_edit_modal` |
| `title` | string | Modal title displayed in header | `Edit User Profile` |
| `size` | string | Modal size (sm/md/lg/xl/full) | `lg` |
| `closeable` | boolean | Whether close button is shown | `true` |
| `backdrop_dismiss` | boolean | Whether clicking backdrop closes modal | `true` |
| `content_template` | string | Path to content template | `users/edit_form.html` |
| `footer_template` | string | Path to footer template | `users/modal_footer.html` |
| `show_footer` | boolean | Whether footer is displayed | `true` |

### Data Table Template Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `title` | string | Table card title | `Organizations Registry` |
| `icon_class` | string | FontAwesome icon class | `fas fa-building` |
| `accent_class` | string | Header gradient class | `bg-gradient-ocean` |
| `headers` | list | Column header definitions | See below |
| `rows` | list | Data row definitions | See below |
| `empty_message` | string | Message when no data | `No records found` |
| `show_actions` | boolean | Whether to show action column | `true` |

**Header Structure:**
```python
headers = [
    {'label': 'Organization Name', 'width': 'w-[30%]', 'class': 'font-semibold'},
    {'label': 'Type', 'width': 'w-[15%]'},
    {'label': 'Location', 'width': 'w-[20%]'},
    {'label': 'Status', 'width': 'w-[15%]'},
]
```

**Row Structure:**
```python
rows = [
    {
        'cells': [
            {'content': org.name, 'class': 'font-semibold text-gray-900'},
            {'content': org.get_type_display()},
            {'content': org.location},
            {'content': f'<span class="badge-{org.status}">{org.status}</span>'},
        ],
        'view_url': org.get_absolute_url(),
        'edit_url': reverse('org_edit', args=[org.id]),
        'delete_preview_url': reverse('org_delete', args=[org.id]),
    }
]
```

### Form Template Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `form_id` | string | Unique form identifier | `partnership_form` |
| `form_action` | string | Form submission URL | `/partnerships/create/` |
| `form_method` | string | HTTP method | `POST` |
| `fields` | list | Form field definitions | See below |
| `submit_text` | string | Submit button text | `Create Partnership` |
| `submit_color` | string | Submit button color | `ocean` |
| `cancel_url` | string | Cancel button URL | `/partnerships/` |
| `show_cancel` | boolean | Whether to show cancel button | `true` |

**Field Structure:**
```python
fields = [
    {
        'name': 'organization',
        'type': 'select',
        'label': 'Organization',
        'required': True,
        'help_text': 'Select the partner organization',
        'options': organizations,
    },
    {
        'name': 'contact_person',
        'type': 'text',
        'label': 'Contact Person',
        'required': True,
        'placeholder': 'Enter full name',
    },
    {
        'name': 'email',
        'type': 'email',
        'label': 'Email Address',
        'required': True,
        'icon': 'fas fa-envelope',
    },
]
```

### Stat Card Template Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `title` | string | Stat card title | `Active Partnerships` |
| `icon_class` | string | FontAwesome icon | `fas fa-handshake` |
| `accent` | string | Color scheme | `emerald` |
| `value` | string/number | Main value to display | `142` |
| `change` | string | Change percentage | `+12%` |
| `trend` | string | Trend direction (up/down/neutral) | `up` |
| `subtitle` | string | Additional context | `vs. last month` |
| `link_url` | string | Optional link URL | `/partnerships/` |
| `link_text` | string | Link text | `View all` |

## File Structure

The scaffolder organizes files in a clear, maintainable structure:

```
.claude/skills/frontend-component-scaffolder/
├── SKILL.md                          # This documentation file
├── README.md                         # Quick start guide
├── config.yaml                       # Default configuration
├── scripts/
│   ├── generate_component.py        # Main generation script
│   ├── batch_generate.py            # Batch generation from YAML
│   ├── modify_component.py          # Modify existing components
│   ├── validate_component.py        # Validate generated components
│   └── utils/
│       ├── __init__.py
│       ├── color_utils.py           # Color scheme utilities
│       ├── template_utils.py        # Template rendering
│       └── validation_utils.py      # Component validation
├── templates/
│   ├── modal.html.j2                # Modal template
│   ├── data_table_card.html.j2      # Data table template
│   ├── form.html.j2                 # Form template
│   ├── stat_card.html.j2            # Stat card template
│   ├── htmx_partial.html.j2         # HTMX partial template
│   ├── card.html.j2                 # Generic card template
│   ├── form_field.html.j2           # Individual form field
│   ├── button.html.j2               # Button component
│   ├── badge.html.j2                # Badge component
│   ├── alert.html.j2                # Alert component
│   └── custom/                      # User custom templates
│       └── .gitkeep
├── examples/
│   ├── modal_example.html           # Example modal usage
│   ├── table_example.html           # Example table usage
│   ├── form_example.html            # Example form usage
│   └── complete_page_example.html   # Full page example
└── tests/
    ├── test_generation.py           # Generation tests
    ├── test_validation.py           # Validation tests
    └── fixtures/                    # Test fixtures
        └── sample_components.yaml
```

## Best Practices

### Color Usage Guidelines

When choosing colors for components, follow these principles to maintain consistency and accessibility:

**Primary Actions & Navigation:**
Use Ocean Blue (ocean-600 to ocean-700) for primary buttons, main navigation, and key interactive elements. This creates a strong visual hierarchy and guides users to important actions.

```html
<button class="bg-ocean-600 hover:bg-ocean-700 text-white px-6 py-3 rounded-lg">
    Primary Action
</button>
```

**Success States & Completion:**
Use Emerald (emerald-600 to emerald-700) for success messages, completion indicators, and positive feedback. This provides clear positive reinforcement.

```html
<div class="bg-emerald-50 border-l-4 border-emerald-600 p-4">
    <p class="text-emerald-700">Operation completed successfully!</p>
</div>
```

**Secondary Actions & Information:**
Use Teal (teal-600 to teal-700) for secondary actions, informational elements, and supporting content. This creates visual balance without competing with primary actions.

```html
<button class="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg">
    Secondary Action
</button>
```

**Warnings & Highlights:**
Use Gold/Amber (gold-600 to gold-700) sparingly for warnings, important notices, and premium features. Overuse can reduce its effectiveness.

```html
<div class="bg-gold-50 border-l-4 border-gold-600 p-4">
    <p class="text-gold-700">Important: Please review before proceeding</p>
</div>
```

**Gradient Headers:**
For section headers and card titles, use the predefined gradients to create visual interest while maintaining brand consistency.

```html
<div class="bg-gradient-primary text-white px-6 py-4 rounded-t-2xl">
    <h2 class="text-xl font-semibold">Section Title</h2>
</div>
```

### HTMX Best Practices

**Loading States:**
Always provide visual feedback during HTMX requests using indicators.

```html
<button hx-post="/api/save" 
        hx-indicator="#saving-spinner"
        class="btn-ocean">
    Save
    <span id="saving-spinner" class="htmx-indicator">
        <i class="fas fa-circle-notch fa-spin"></i>
    </span>
</button>
```

**Error Handling:**
Include proper error handling for HTMX requests.

```html
<div hx-get="/api/data"
     hx-trigger="load"
     hx-target="#content"
     hx-on::before-request="showLoading()"
     hx-on::after-request="hideLoading()"
     hx-on::response-error="handleError(event)">
</div>
```

**Progressive Enhancement:**
Ensure forms work without JavaScript by providing proper action attributes.

```html
<form method="POST" 
      action="/partnerships/create/"
      hx-post="/partnerships/create/"
      hx-target="#result">
    {% csrf_token %}
    <!-- Form fields -->
</form>
```

**Debouncing:**
Use debouncing for search and filter inputs to reduce server requests.

```html
<input type="text"
       hx-get="/api/search"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#search-results"
       placeholder="Search...">
```

### Alpine.js Best Practices

**Component Scope:**
Keep Alpine components scoped to their specific functionality.

```html
<!-- GOOD: Scoped component -->
<div x-data="{ showDetails: false }" class="partnership-card">
    <button @click="showDetails = !showDetails">Toggle Details</button>
    <div x-show="showDetails">Details content</div>
</div>

<!-- AVOID: Overly broad scope -->
<div x-data="{ showDetails1: false, showDetails2: false, showDetails3: false }">
    <!-- Multiple unrelated components -->
</div>
```

**State Initialization:**
Initialize state with sensible defaults.

```html
<div x-data="{ 
    selectedTab: 'overview',
    isLoading: false,
    items: [],
    error: null 
}" class="tabbed-interface">
    <!-- Component content -->
</div>
```

**Transitions:**
Use consistent transition patterns across similar components.

```html
<div x-show="isOpen"
     x-transition:enter="transition ease-out duration-200"
     x-transition:enter-start="opacity-0 scale-95"
     x-transition:enter-end="opacity-100 scale-100"
     x-transition:leave="transition ease-in duration-150"
     x-transition:leave-start="opacity-100 scale-100"
     x-transition:leave-end="opacity-0 scale-95">
    Panel content
</div>
```

### Accessibility Best Practices

**ARIA Labels:**
Always include proper ARIA labels for interactive elements.

```html
<button type="button"
        @click="toggleMenu()"
        aria-label="Toggle navigation menu"
        aria-expanded="false"
        aria-controls="main-menu">
    <i class="fas fa-bars" aria-hidden="true"></i>
</button>
```

**Keyboard Navigation:**
Ensure all interactive elements are keyboard accessible.

```html
<div role="tablist" aria-label="Partnership sections">
    <button role="tab"
            aria-selected="true"
            aria-controls="panel-1"
            tabindex="0"
            @keydown.arrow-right="nextTab()"
            @keydown.arrow-left="previousTab()">
        Overview
    </button>
</div>
```

**Focus Management:**
Manage focus appropriately, especially in modals and dynamic content.

```html
<div x-data="{ open: false }"
     x-on:keydown.escape.window="open = false"
     x-trap.inert.noscroll="open">
    <!-- Modal content with proper focus trap -->
</div>
```

**Color Contrast:**
Use the pre-defined color combinations that meet WCAG AA standards.

```html
<!-- GOOD: High contrast (ocean-700 on white = 7.0:1) -->
<p class="text-ocean-700">Important text content</p>

<!-- GOOD: High contrast (white on ocean-600 = 4.5:1) -->
<button class="bg-ocean-600 text-white">Action Button</button>

<!-- AVOID: Low contrast -->
<p class="text-ocean-200">Light gray text</p>
```

### Responsive Design Best Practices

**Mobile-First Approach:**
Design components mobile-first, then enhance for larger screens.

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Card components -->
</div>
```

**Breakpoint Strategy:**
Use Tailwind's standard breakpoints consistently:
- `sm`: 640px - Small tablets
- `md`: 768px - Tablets and small laptops
- `lg`: 1024px - Desktop
- `xl`: 1280px - Large desktop
- `2xl`: 1536px - Extra large screens

**Touch Targets:**
Ensure touch targets are at least 44x44px for mobile usability.

```html
<button class="min-h-[44px] min-w-[44px] px-4 py-3 rounded-lg">
    Mobile-Friendly Button
</button>
```

**Responsive Typography:**
Use responsive text sizes for better readability across devices.

```html
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
    Responsive Heading
</h1>
```

## Troubleshooting

### Common Issues and Solutions

**Issue: Generated component doesn't match color scheme**

Solution: Check that you're using the correct accent parameter. Valid values are: `ocean`, `teal`, `emerald`, `gold`. Regenerate with:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/generate_component.py \
    --type modal \
    --name my_modal \
    --accent ocean \
    --regenerate
```

**Issue: HTMX partial not updating**

Solution: Verify the following:
1. `hx-target` selector is correct
2. Target element exists in the DOM
3. HTMX JavaScript is loaded
4. Server response includes correct HTML

Add debugging:
```html
<div hx-get="/api/endpoint"
     hx-target="#result"
     hx-on::before-request="console.log('Request starting')"
     hx-on::after-request="console.log('Request complete', event.detail)">
</div>
```

**Issue: Alpine.js transitions not working**

Solution: Ensure Alpine.js is loaded before your component. Check that:
1. Alpine.js script is in `<head>` or before component
2. Component has `x-data` attribute
3. Transition classes are properly formatted

```html
<!-- Verify Alpine is loaded -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<!-- Component -->
<div x-data="{ show: false }">
    <div x-show="show" x-transition>
        Content
    </div>
</div>
```

**Issue: Modal not closing on backdrop click**

Solution: Check that `backdrop_dismiss` is not set to `false`. If you need it enabled:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/modify_component.py \
    --file src/templates/common/partials/my_modal.html \
    --set-backdrop-dismiss true
```

**Issue: Form validation not showing errors**

Solution: Ensure your Django form is properly configured and the template is rendering errors:

```django
{% for field in form %}
    <div class="form-field">
        {{ field.label_tag }}
        {{ field }}
        {% if field.errors %}
            <div class="text-rose-600 text-sm mt-1">
                {{ field.errors.0 }}
            </div>
        {% endif %}
    </div>
{% endfor %}
```

**Issue: Gradients not rendering**

Solution: Verify that your `tailwind.config.js` includes the gradient definitions. If missing, add:

```javascript
backgroundImage: {
    'gradient-primary': 'linear-gradient(135deg, #0369a1 0%, #0d9488 50%, #059669 100%)',
    // ... other gradients
}
```

Then rebuild Tailwind:
```bash
npm run build:css
```

### Validation

To validate a generated component:

```bash
python .claude/skills/frontend-component-scaffolder/scripts/validate_component.py \
    --file src/templates/common/partials/my_component.html \
    --check-colors \
    --check-accessibility \
    --check-htmx
```

This validates:
- Color usage matches Bangsamoro palette
- Proper ARIA attributes
- HTMX attribute correctness
- Alpine.js syntax
- Responsive classes
- Template syntax

## Examples

### Complete Page Example

Here's a complete page using multiple generated components:

```django
{% extends 'base.html' %}
{% load static %}

{% block title %}Partnership Management{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <!-- Page Header -->
    <div class="bg-gradient-primary text-white rounded-2xl shadow-lg px-8 py-6 mb-8">
        <h1 class="text-3xl font-bold">Partnership Management</h1>
        <p class="text-ocean-50 mt-2">Manage inter-MOA partnerships and collaborations</p>
    </div>

    <!-- Statistics Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {% include 'components/stat_card.html' with title='Active Partnerships' value=stats.active_count icon_class='fas fa-handshake' accent='emerald' change='+12%' trend='up' %}
        {% include 'components/stat_card.html' with title='Pending Approvals' value=stats.pending_count icon_class='fas fa-clock' accent='gold' %}
        {% include 'components/stat_card.html' with title='Total Organizations' value=stats.org_count icon_class='fas fa-building' accent='ocean' %}
        {% include 'components/stat_card.html' with title='This Month' value=stats.month_count icon_class='fas fa-calendar' accent='teal' change='+8%' trend='up' %}
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Partnerships Table -->
        <div class="lg:col-span-2">
            {% include 'components/data_table_card.html' with title='Recent Partnerships' icon_class='fas fa-handshake' accent_class='bg-gradient-ocean' headers=table_headers rows=partnerships %}
        </div>

        <!-- Quick Actions -->
        <div>
            <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div class="space-y-3">
                    <button @click="$dispatch('open-modal', { modal: 'create-partnership' })"
                            class="w-full bg-ocean-600 hover:bg-ocean-700 text-white px-4 py-3 rounded-lg flex items-center gap-2 transition-colors">
                        <i class="fas fa-plus"></i>
                        <span>New Partnership</span>
                    </button>
                    <a href="{% url 'partnerships:pending' %}"
                       class="block w-full bg-gold-600 hover:bg-gold-700 text-white px-4 py-3 rounded-lg flex items-center gap-2 transition-colors text-center">
                        <i class="fas fa-clock"></i>
                        <span>Review Pending</span>
                    </a>
                    <a href="{% url 'partnerships:reports' %}"
                       class="block w-full bg-teal-600 hover:bg-teal-700 text-white px-4 py-3 rounded-lg flex items-center gap-2 transition-colors text-center">
                        <i class="fas fa-chart-bar"></i>
                        <span>View Reports</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Create Partnership Modal -->
{% include 'components/modal.html' with modal_id='create-partnership' title='Create New Partnership' size='lg' content_template='coordination/partials/partnership_form.html' %}
{% endblock %}
```

### HTMX Dynamic Updates Example

```django
<!-- Partnership List Container -->
<div id="partnerships-container"
     hx-get="{% url 'partnerships:list_partial' %}"
     hx-trigger="load, partnershipUpdated from:body"
     hx-swap="innerHTML">
    <!-- Initial loading state -->
    <div class="text-center py-8">
        <i class="fas fa-circle-notch fa-spin text-ocean-600 text-2xl"></i>
        <p class="text-gray-500 mt-2">Loading partnerships...</p>
    </div>
</div>

<!-- Individual Partnership Row (htmx_partial.html) -->
<div class="partnership-row flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors"
     id="partnership-{{ partnership.id }}">
    <div class="w-[40%]">
        <h4 class="font-semibold text-gray-900">{{ partnership.name }}</h4>
        <p class="text-sm text-gray-500">{{ partnership.organization.name }}</p>
    </div>
    <div class="w-[20%]">
        <span class="badge-{{ partnership.status }}">{{ partnership.get_status_display }}</span>
    </div>
    <div class="w-[20%] text-sm text-gray-600">
        {{ partnership.start_date|date:"M d, Y" }}
    </div>
    <div class="w-[20%] flex items-center justify-end gap-2">
        <button hx-get="{% url 'partnerships:detail_modal' partnership.id %}"
                hx-target="body"
                hx-swap="beforeend"
                class="btn-sm btn-ocean">
            <i class="fas fa-eye"></i>
            View
        </button>
        <button hx-get="{% url 'partnerships:edit_modal' partnership.id %}"
                hx-target="body"
                hx-swap="beforeend"
                class="btn-sm btn-teal">
            <i class="fas fa-edit"></i>
            Edit
        </button>
    </div>
</div>

<!-- Edit Modal (loaded dynamically) -->
<div hx-ext="json-enc">
    {% include 'components/modal.html' with modal_id='edit-partnership-'|add:partnership.id title='Edit Partnership' size='lg' content_template='coordination/partials/partnership_edit_form.html' %}
</div>

<!-- Form with HTMX submission -->
<form hx-post="{% url 'partnerships:update' partnership.id %}"
      hx-target="#partnership-{{ partnership.id }}"
      hx-swap="outerHTML"
      hx-on::after-request="if(event.detail.successful) { htmx.trigger('body', 'partnershipUpdated'); closeModal(); }">
    {% csrf_token %}
    <!-- Form fields -->
    <button type="submit" class="btn-ocean">
        <span class="htmx-indicator">
            <i class="fas fa-circle-notch fa-spin"></i>
        </span>
        <span>Update Partnership</span>
    </button>
</form>
```

### Alpine.js Interactive Component Example

```django
<!-- Tabbed Interface with Alpine.js -->
<div x-data="{ 
    activeTab: 'overview',
    tabs: ['overview', 'documents', 'milestones', 'budget'],
    tabTitles: {
        overview: 'Overview',
        documents: 'Documents',
        milestones: 'Milestones',
        budget: 'Budget'
    }
}" class="partnership-tabs">
    <!-- Tab Navigation -->
    <div class="border-b border-gray-200 mb-6">
        <div class="flex gap-2">
            <template x-for="tab in tabs" :key="tab">
                <button @click="activeTab = tab"
                        :class="{
                            'border-ocean-600 text-ocean-700': activeTab === tab,
                            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300': activeTab !== tab
                        }"
                        class="px-4 py-2 border-b-2 font-medium transition-colors"
                        :aria-selected="activeTab === tab"
                        role="tab">
                    <span x-text="tabTitles[tab]"></span>
                </button>
            </template>
        </div>
    </div>

    <!-- Tab Panels -->
    <div class="tab-content">
        <!-- Overview Tab -->
        <div x-show="activeTab === 'overview'"
             x-transition:enter="transition ease-out duration-200"
             x-transition:enter-start="opacity-0 translate-y-2"
             x-transition:enter-end="opacity-100 translate-y-0"
             role="tabpanel">
            {% include 'coordination/partials/partnership_overview.html' %}
        </div>

        <!-- Documents Tab -->
        <div x-show="activeTab === 'documents'"
             x-transition:enter="transition ease-out duration-200"
             x-transition:enter-start="opacity-0 translate-y-2"
             x-transition:enter-end="opacity-100 translate-y-0"
             role="tabpanel"
             hx-get="{% url 'partnerships:documents' partnership.id %}"
             hx-trigger="intersect once"
             hx-swap="innerHTML">
            <div class="text-center py-8">
                <i class="fas fa-circle-notch fa-spin text-ocean-600"></i>
                <p class="text-gray-500 mt-2">Loading documents...</p>
            </div>
        </div>

        <!-- Milestones Tab -->
        <div x-show="activeTab === 'milestones'"
             x-transition:enter="transition ease-out duration-200"
             x-transition:enter-start="opacity-0 translate-y-2"
             x-transition:enter-end="opacity-100 translate-y-0"
             role="tabpanel"
             hx-get="{% url 'partnerships:milestones' partnership.id %}"
             hx-trigger="intersect once"
             hx-swap="innerHTML">
            <div class="text-center py-8">
                <i class="fas fa-circle-notch fa-spin text-ocean-600"></i>
                <p class="text-gray-500 mt-2">Loading milestones...</p>
            </div>
        </div>

        <!-- Budget Tab -->
        <div x-show="activeTab === 'budget'"
             x-transition:enter="transition ease-out duration-200"
             x-transition:enter-start="opacity-0 translate-y-2"
             x-transition:enter-end="opacity-100 translate-y-0"
             role="tabpanel"
             hx-get="{% url 'partnerships:budget' partnership.id %}"
             hx-trigger="intersect once"
             hx-swap="innerHTML">
            <div class="text-center py-8">
                <i class="fas fa-circle-notch fa-spin text-ocean-600"></i>
                <p class="text-gray-500 mt-2">Loading budget information...</p>
            </div>
        </div>
    </div>
</div>
```

## Updates and Maintenance

### Updating the Skill

To update the scaffolder with new component types or templates:

1. Add new template file to `templates/` directory
2. Update `config.yaml` with new component type
3. Update this `SKILL.md` documentation
4. Run validation tests

### Contributing Custom Templates

To contribute custom templates back to the skill:

1. Create template in `templates/custom/`
2. Document usage in comments within template
3. Add example to `examples/` directory
4. Submit for review

### Version History

- **v1.0.0** (Initial Release)
  - Core component types (Modal, Data Table, Form, Stat Card, HTMX Partial)
  - Bangsamoro color scheme implementation
  - Basic generation scripts
  - Alpine.js and HTMX integration patterns

## Support and Resources

### Documentation Resources
- Django Templates: https://docs.djangoproject.com/en/stable/topics/templates/
- HTMX Documentation: https://htmx.org/docs/
- Alpine.js Documentation: https://alpinejs.dev/
- Tailwind CSS Documentation: https://tailwindcss.com/docs

### Internal Resources
- OBCMS/BMMS Style Guide: `docs/ui/style-guide.md`
- Component Library: `docs/ui/component-library.md`
- HTMX Patterns: `docs/development/htmx-patterns.md`

### Getting Help

For issues or questions about the Frontend Component Scaffolder:
1. Check this documentation thoroughly
2. Review example files in `examples/` directory
3. Validate your components using the validation script
4. Consult the OBCMS/BMMS development team

## Conclusion

The Frontend Component Scaffolder dramatically improves development velocity while maintaining the highest standards of consistency, accessibility, and design quality in the OBCMS/BMMS system. Through automated generation of components that strictly adhere to the Bangsamoro color scheme and established patterns, developers can focus on business logic rather than repetitive markup. The scaffolder's comprehensive template library, combined with powerful generation scripts, ensures that every component integrates seamlessly with HTMX and Alpine.js while maintaining visual harmony across the entire application.

The investment in learning and using this skill pays immediate dividends through reduced development time, fewer bugs, and a more cohesive user experience. As the OBCMS/BMMS system evolves, the scaffolder provides a solid foundation for maintaining design system integrity while enabling rapid iteration on new features and modules.
