# MANA Form Design Standards

## Overview
This document outlines the UI/UX design standards for forms in the OBC Management System, established based on the redesign of the MANA Assessment form.

## Standard Dropdown/Select Component

### Visual Design
- **Border Radius**: `rounded-xl` (12px)
- **Border**: `border border-gray-200`
- **Focus State**: `focus:ring-emerald-500 focus:border-emerald-500`
- **Height**: `min-h-[48px]` for accessibility
- **Padding**: `py-3 px-4`
- **Background**: `bg-white`
- **Transitions**: `transition-all duration-200`

### Required Elements
1. **Label**: Small, medium weight, gray-700
2. **Chevron Icon**: Right-aligned, gray-400, Font Awesome `fa-chevron-down`
3. **Placeholder**: First option with empty value
4. **Required Indicator**: Red asterisk (*) when field is required

### HTML Structure
```html
<div class="space-y-1">
    <label for="field-id" class="block text-sm font-medium text-gray-700 mb-2">
        Field Label<span class="text-red-500">*</span>
    </label>
    <div class="relative">
        <select id="field-id" name="field_name"
                class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200">
            <option value="">Select...</option>
            <!-- Options here -->
        </select>
        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
            <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
        </span>
    </div>
</div>
```

## Form Section Containers

### White Card Layout
```html
<div class="bg-white rounded-xl p-6 border border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <i class="fas fa-icon-name text-blue-500 mr-2"></i>
        Section Title
    </h3>
    <!-- Form fields here -->
</div>
```

## Radio Button Groups

### Card-Based Selection
- **Selected State**: `border-2 border-emerald-500 bg-emerald-50`
- **Unselected State**: `border-2 border-gray-200 bg-white`
- **Hover**: `hover:border-gray-300 hover:shadow-md`
- **Border Radius**: `rounded-xl`
- **Padding**: `p-4`

### Example
```html
<label class="flex items-start p-4 border-2 border-emerald-500 bg-emerald-50 rounded-xl cursor-pointer transition-all hover:shadow-md">
    <input type="radio" name="field" value="option1"
           class="mt-1 mr-3 text-emerald-600 focus:ring-emerald-500" checked required>
    <div>
        <div class="font-semibold text-emerald-900">Option Title</div>
        <div class="text-sm text-emerald-700 mt-1">Option description</div>
    </div>
</label>
```

## Color Palette

### Primary Colors
- **Emerald** (primary actions, focus states): `emerald-500`, `emerald-50`, `emerald-700`, `emerald-900`
- **Gray** (borders, text): `gray-200`, `gray-400`, `gray-500`, `gray-700`, `gray-900`

### Semantic Colors
- **Required Fields**: `red-500` for asterisk
- **Info/Blue**: `blue-500`, `blue-50`, `blue-700`
- **Warning/Orange**: `orange-500`, `orange-50`

## Spacing Standards

### Vertical Spacing
- Section margin: `space-y-6` (24px between sections)
- Field spacing within section: `gap-4` (16px)
- Label to input: `mb-2` (8px)

### Padding
- Card padding: `p-6` (24px)
- Input padding: `py-3 px-4` (12px vertical, 16px horizontal)
- Radio card padding: `p-4` (16px)

## Responsive Grid

### Two-Column Layout
```html
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Fields here -->
</div>
```

### Full-Width Fields
```html
<div class="grid grid-cols-1 gap-4">
    <!-- Full-width field -->
</div>
```

## Reference Templates

### Primary References
1. **Provincial Management**: `src/templates/communities/provincial_manage.html`
   - Filter dropdowns at the top
   - Standard dropdown styling with region/province cascade

2. **Form Field Component**: `src/templates/components/form_field_select.html`
   - Reusable dropdown component
   - Handles labels, errors, help text automatically

3. **MANA Assessment Form**: `src/templates/mana/mana_new_assessment.html`
   - Complex multi-section form
   - Team composition with staff filtering
   - Radio button groups for methodology selection

## Staff Member Filtering

When displaying staff members in dropdowns, filter to only active OOBC Staff:

```python
from common.models import StaffProfile

staff_profiles = StaffProfile.objects.filter(
    user__is_active=True,
    employment_status=StaffProfile.STATUS_ACTIVE
).select_related("user").order_by("user__first_name", "user__last_name")

staff_members = [profile.user for profile in staff_profiles]
```

This ensures:
- Only users with `StaffProfile` (OOBC Staff/Executives)
- Only active employment status
- Excludes participants and non-OOBC personnel

## Accessibility

### Required Elements
- **Label association**: Use `for` and `id` attributes
- **Required indicators**: Visual (`*`) and semantic (`required` attribute)
- **Focus states**: Clear emerald ring on all interactive elements
- **Touch targets**: Minimum 48px height for mobile
- **Color contrast**: Meets WCAG 2.1 AA standards

### ARIA Attributes
```html
<select id="field-id"
        name="field_name"
        aria-label="Descriptive label"
        aria-required="true">
```

## Implementation Checklist

When creating or modifying forms:
- [ ] Review existing templates for similar patterns
- [ ] Use component templates when possible
- [ ] Apply standard dropdown styling (rounded-xl, emerald focus)
- [ ] Include chevron icons on all dropdowns
- [ ] Use white card containers for sections
- [ ] Apply proper spacing (gap-4 for fields, space-y-6 for sections)
- [ ] Filter staff dropdowns to OOBC Staff only
- [ ] Add required indicators where applicable
- [ ] Test responsive layout (mobile, tablet, desktop)
- [ ] Verify accessibility (keyboard navigation, screen readers)

## Updated Documentation

The following files have been updated with these standards:
- `CLAUDE.md` - Added "Form Design Standards" section
- `AGENTS.md` - Added "Form Design Standards" section under "Reusable Form Components"
- `GEMINI.md` - Added "Form Design Standards (MANDATORY)" section

All AI agents working on this codebase are now instructed to reference existing templates and follow these standards when designing forms.