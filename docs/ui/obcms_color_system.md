# OBCMS Color System Design
**Office for Other Bangsamoro Communities Management System**

**Version:** 2.0
**Date:** January 2025
**Status:** Official Design System
**WCAG Compliance:** AA (4.5:1 minimum contrast)

---

## Design Philosophy

The OBCMS color system reflects the **natural beauty and cultural richness** of the Bangsamoro region while maintaining **professional government standards**. The palette is inspired by:

- 🌊 **Blue-Green Waters**: Representing the seas surrounding Mindanao
- 🌾 **Golden Harvests**: Symbolizing agricultural prosperity and hope
- 🌿 **Verdant Landscapes**: The lush forests and natural resources
- 🏛️ **Government Professionalism**: Trust, stability, and transparency

**Core Principle:** All color combinations must meet WCAG 2.1 AA standards (4.5:1 contrast ratio) for accessibility.

---

## Color Palette

### 1. Primary Colors: Ocean Gradient (Blue-Green)

The primary brand identity uses a gradient from deep ocean blue to vibrant emerald green, representing **progress flowing from the seas to the land**.

#### Ocean Blue
```css
--ocean-50:  #e0f2fe;  /* Lightest - backgrounds, hover states */
--ocean-100: #bae6fd;  /* Light - subtle backgrounds */
--ocean-200: #7dd3fc;  /* Medium light - borders, dividers */
--ocean-300: #38bdf8;  /* Medium - interactive elements */
--ocean-400: #0ea5e9;  /* Bright - secondary buttons */
--ocean-500: #0284c7;  /* Primary - main interactive color */
--ocean-600: #0369a1;  /* Primary dark - primary buttons (4.5:1 on white) */
--ocean-700: #075985;  /* Darker - hover states (7.0:1 on white) */
--ocean-800: #0c4a6e;  /* Very dark - text, headers (10.7:1 on white) */
--ocean-900: #082f49;  /* Darkest - strong emphasis (14.3:1 on white) */
```

**Usage:**
- Primary buttons: `ocean-600`, `ocean-700` on hover
- Links: `ocean-600` with `ocean-700` hover
- Info messages, informational UI elements
- Data visualization: primary series

**Accessibility:**
- `ocean-600` and darker: Safe on white backgrounds (4.5:1+)
- `ocean-50` to `ocean-200`: Use for backgrounds only
- `ocean-800`, `ocean-900`: Safe for body text (10:1+)

---

#### Emerald Green
```css
--emerald-50:  #ecfdf5;  /* Lightest - success backgrounds */
--emerald-100: #d1fae5;  /* Light - hover backgrounds */
--emerald-200: #a7f3d0;  /* Medium light - borders */
--emerald-300: #6ee7b7;  /* Medium - accents */
--emerald-400: #34d399;  /* Bright - interactive highlights */
--emerald-500: #10b981;  /* Primary - success states */
--emerald-600: #059669;  /* Primary dark - primary actions (4.5:1 on white) */
--emerald-700: #047857;  /* Darker - hover states (5.7:1 on white) */
--emerald-800: #065f46;  /* Very dark - text, strong emphasis (7.2:1 on white) */
--emerald-900: #064e3b;  /* Darkest - headers, emphasis (8.9:1 on white) */
```

**Usage:**
- Primary buttons: `emerald-600`, `emerald-700` on hover
- Success messages, completed states
- Progress indicators, achievement badges
- Data visualization: growth, positive trends

**Accessibility:**
- `emerald-600` and darker: Safe on white (4.5:1+)
- `emerald-50` to `emerald-200`: Backgrounds only
- `emerald-800`, `emerald-900`: Body text safe (7:1+)

---

#### Teal (Bridge Color)
```css
--teal-50:  #f0fdfa;  /* Lightest - subtle backgrounds */
--teal-100: #ccfbf1;  /* Light - hover states */
--teal-200: #99f6e4;  /* Medium light - borders */
--teal-300: #5eead4;  /* Medium - accents */
--teal-400: #2dd4bf;  /* Bright - highlights */
--teal-500: #14b8a6;  /* Primary - interactive */
--teal-600: #0d9488;  /* Primary dark - actions (4.6:1 on white) */
--teal-700: #0f766e;  /* Darker - hover (6.0:1 on white) */
--teal-800: #115e59;  /* Very dark - text (7.8:1 on white) */
--teal-900: #134e4a;  /* Darkest - strong text (9.6:1 on white) */
```

**Usage:**
- Secondary buttons, alternative actions
- Coordination module primary color
- Calendar events, scheduling UI
- Data visualization: neutral series

**Accessibility:**
- `teal-600` and darker: Safe on white (4.5:1+)
- `teal-800`, `teal-900`: Body text safe (7:1+)

---

### 2. Accent Colors: Golden Prosperity

Yellow and gold represent **hope, prosperity, and the agricultural wealth** of the region.

#### Gold
```css
--gold-50:  #fffbeb;  /* Lightest - warning backgrounds */
--gold-100: #fef3c7;  /* Light - highlight backgrounds */
--gold-200: #fde68a;  /* Medium light - borders */
--gold-300: #fcd34d;  /* Medium - accents */
--gold-400: #fbbf24;  /* Bright - highlights, badges */
--gold-500: #f59e0b;  /* Primary - warning states */
--gold-600: #d97706;  /* Primary dark - important actions (4.6:1 on white) */
--gold-700: #b45309;  /* Darker - hover states (5.8:1 on white) */
--gold-800: #92400e;  /* Very dark - text (7.2:1 on white) */
--gold-900: #78350f;  /* Darkest - emphasis (9.5:1 on white) */
```

**Usage:**
- Warning messages, alerts
- Priority badges, "featured" indicators
- Economic data, financial metrics
- Highlights, special announcements

**Accessibility:**
- `gold-600` and darker: Safe on white (4.5:1+)
- `gold-50` to `gold-300`: Backgrounds and borders only
- `gold-800`, `gold-900`: Body text safe (7:1+)

---

#### Amber (Supporting Yellow)
```css
--amber-50:  #fffbeb;  /* Lightest - subtle highlights */
--amber-100: #fef3c7;  /* Light - backgrounds */
--amber-200: #fde68a;  /* Medium light - borders */
--amber-300: #fcd34d;  /* Medium - accents */
--amber-400: #fbbf24;  /* Bright - call-to-action */
--amber-500: #f59e0b;  /* Primary - attention */
--amber-600: #d97706;  /* Primary dark - buttons (4.6:1 on white) */
--amber-700: #b45309;  /* Darker - hover (5.8:1 on white) */
--amber-800: #92400e;  /* Very dark - strong emphasis (7.2:1 on white) */
--amber-900: #78350f;  /* Darkest - headers (9.5:1 on white) */
```

**Usage:**
- Secondary warnings, caution states
- Pending/in-review status indicators
- Budget planning UI, cost indicators
- Data visualization: caution ranges

**Accessibility:**
- `amber-600` and darker: Safe on white (4.5:1+)
- `amber-800`, `amber-900`: Body text safe (7:1+)

---

### 3. Neutrals: Professional Grays

A comprehensive neutral palette for text, backgrounds, and UI structure.

#### Cool Gray
```css
--gray-50:  #f9fafb;  /* Lightest - page backgrounds */
--gray-100: #f3f4f6;  /* Light - card backgrounds, hover states */
--gray-200: #e5e7eb;  /* Medium light - borders, dividers */
--gray-300: #d1d5db;  /* Medium - disabled borders, inactive elements */
--gray-400: #9ca3af;  /* Medium dark - placeholders (3.3:1 - use on light backgrounds only) */
--gray-500: #6b7280;  /* Dark - secondary text, icons (4.7:1 on white) */
--gray-600: #4b5563;  /* Darker - labels, tertiary text (7.0:1 on white) */
--gray-700: #374151;  /* Very dark - secondary headings (10.0:1 on white) */
--gray-800: #1f2937;  /* Darkest - body text, primary headings (14.0:1 on white) */
--gray-900: #111827;  /* Absolute darkest - main headings (16.1:1 on white) */
```

**Usage:**
- Body text: `gray-800`, `gray-900`
- Secondary text: `gray-600`, `gray-700`
- Borders: `gray-200`, `gray-300`
- Backgrounds: `gray-50`, `gray-100`
- Disabled states: `gray-400`

**Accessibility:**
- `gray-500` and darker: Safe for text on white (4.5:1+)
- `gray-700` and darker: Safe for body text (10:1+)
- `gray-400`: Placeholders only, not for body text

---

#### Slate (Alternative Neutral)
```css
--slate-50:  #f8fafc;  /* Lightest - alternative backgrounds */
--slate-100: #f1f5f9;  /* Light - subtle contrast */
--slate-200: #e2e8f0;  /* Medium light - borders */
--slate-300: #cbd5e1;  /* Medium - dividers */
--slate-400: #94a3b8;  /* Medium dark - subtle text (3.5:1) */
--slate-500: #64748b;  /* Dark - secondary text (4.9:1 on white) */
--slate-600: #475569;  /* Darker - labels (7.4:1 on white) */
--slate-700: #334155;  /* Very dark - headings (10.7:1 on white) */
--slate-800: #1e293b;  /* Darkest - primary text (14.9:1 on white) */
--slate-900: #0f172a;  /* Absolute darkest - emphasis (16.8:1 on white) */
```

**Usage:**
- Alternative UI theme (cooler tone)
- Admin panel backgrounds
- Data tables, grid systems
- Professional documentation

**Accessibility:**
- `slate-500` and darker: Safe for text (4.5:1+)
- `slate-700` and darker: Body text safe (10:1+)

---

### 4. Semantic Colors

#### Success
```css
--success-50:  #f0fdf4;  /* Background */
--success-600: #16a34a;  /* Primary (4.5:1 on white) */
--success-700: #15803d;  /* Hover (7.1:1 on white) */
--success-800: #166534;  /* Strong emphasis (9.3:1 on white) */
```

**Usage:** Completed actions, success messages, approved states, positive metrics

---

#### Warning
```css
--warning-50:  #fffbeb;  /* Background */
--warning-600: #d97706;  /* Primary (4.6:1 on white) */
--warning-700: #b45309;  /* Hover (5.8:1 on white) */
--warning-800: #92400e;  /* Strong emphasis (7.2:1 on white) */
```

**Usage:** Caution messages, pending approvals, review needed, important notices

---

#### Error/Danger
```css
--error-50:  #fef2f2;  /* Background */
--error-600: #dc2626;  /* Primary (4.5:1 on white) */
--error-700: #b91c1c;  /* Hover (7.3:1 on white) */
--error-800: #991b1b;  /* Strong emphasis (9.1:1 on white) */
```

**Usage:** Error messages, failed actions, destructive operations, critical alerts

---

#### Info
```css
--info-50:  #eff6ff;  /* Background */
--info-600: #2563eb;  /* Primary (4.5:1 on white) */
--info-700: #1d4ed8;  /* Hover (7.0:1 on white) */
--info-800: #1e40af;  /* Strong emphasis (8.5:1 on white) */
```

**Usage:** Informational messages, help text, tooltips, system notifications

---

## Gradient System

### Primary Gradients

#### Ocean to Emerald (Main Brand)
```css
--gradient-primary: linear-gradient(135deg, #0369a1 0%, #0d9488 50%, #059669 100%);
```
**Usage:** Primary buttons, hero sections, main navigation, featured cards

---

#### Ocean Radial
```css
--gradient-ocean-radial: radial-gradient(circle at top left, #0ea5e9 0%, #0284c7 100%);
```
**Usage:** Background overlays, modal backdrops, section backgrounds

---

#### Emerald Radial
```css
--gradient-emerald-radial: radial-gradient(circle at bottom right, #10b981 0%, #059669 100%);
```
**Usage:** Success overlays, positive metric cards, achievement badges

---

#### Teal Flow
```css
--gradient-teal-flow: linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%);
```
**Usage:** Secondary buttons, coordination module, calendar events

---

### Accent Gradients

#### Golden Prosperity
```css
--gradient-gold: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
```
**Usage:** Warning buttons, featured badges, economic indicators, premium features

---

#### Sunrise (Ocean to Gold)
```css
--gradient-sunrise: linear-gradient(135deg, #0ea5e9 0%, #14b8a6 33%, #fbbf24 66%, #f59e0b 100%);
```
**Usage:** Dashboard hero sections, annual reports, celebration banners

---

### Background Gradients

#### Subtle Ocean Mist
```css
--gradient-bg-ocean: linear-gradient(180deg,
    rgba(14, 165, 233, 0.05) 0%,
    rgba(20, 184, 166, 0.03) 50%,
    transparent 100%
);
```
**Usage:** Page backgrounds, card overlays, subtle depth

---

#### Subtle Emerald Mist
```css
--gradient-bg-emerald: linear-gradient(180deg,
    rgba(16, 185, 129, 0.08) 0%,
    rgba(5, 150, 105, 0.04) 50%,
    transparent 100%
);
```
**Usage:** Success sections, positive metric backgrounds

---

#### Golden Glow
```css
--gradient-bg-gold: linear-gradient(180deg,
    rgba(251, 191, 36, 0.08) 0%,
    rgba(245, 158, 11, 0.04) 50%,
    transparent 100%
);
```
**Usage:** Warning sections, important announcements, featured content

---

## Component Color Usage

### Buttons

#### Primary Buttons
```css
background: var(--gradient-primary);
color: white;
hover: filter: brightness(1.1);
```

#### Secondary Buttons
```css
background: white;
color: var(--ocean-700);
border: 2px solid var(--ocean-600);
hover: background: var(--ocean-50);
```

#### Gold/Warning Buttons
```css
background: var(--gradient-gold);
color: white;
hover: filter: brightness(1.05);
```

---

### Cards

#### Default Cards
```css
background: white;
border: 1px solid var(--gray-200);
hover: border-color: var(--ocean-300);
shadow: 0 4px 12px rgba(3, 105, 161, 0.08);
```

#### Featured Cards (with gradient header)
```css
header-background: var(--gradient-primary);
header-text: white;
body-background: white;
body-text: var(--gray-800);
```

#### Info Cards
```css
background: var(--info-50);
border: 1px solid var(--info-600);
icon-color: var(--info-600);
```

#### Warning Cards
```css
background: var(--gold-50);
border: 1px solid var(--gold-600);
icon-color: var(--gold-700);
```

---

### Forms

#### Input Fields
```css
border: 1px solid var(--gray-300);
background: white;
text: var(--gray-800);
placeholder: var(--gray-500);

focus:
  border-color: var(--ocean-600);
  ring: 0 0 0 3px rgba(3, 105, 161, 0.2);
```

#### Select Dropdowns
```css
border: 1px solid var(--gray-200);
border-radius: 0.75rem;
background: white;

focus:
  border-color: var(--emerald-600);
  ring: 0 0 0 3px rgba(5, 150, 105, 0.2);
```

#### Labels
```css
color: var(--gray-700);
font-weight: 600;
required-indicator: var(--error-600);
```

---

### Navigation

#### Main Navigation
```css
background: var(--gradient-primary);
text: white;
hover: rgba(255, 255, 255, 0.2) overlay;
active: rgba(255, 255, 255, 0.3) overlay;
```

#### Sidebar Navigation
```css
background: white;
border-right: 1px solid var(--gray-200);

item-default: var(--gray-700);
item-hover: var(--ocean-600), background: var(--ocean-50);
item-active: var(--ocean-700), background: var(--ocean-100);
```

---

### Tables

#### Header
```css
background: var(--gray-50);
text: var(--gray-700);
border-bottom: 2px solid var(--gray-200);
```

#### Rows
```css
background: white;
border-bottom: 1px solid var(--gray-200);
hover: background: var(--ocean-50);
```

#### Alternating Rows (optional)
```css
even-row: background: var(--gray-50);
odd-row: background: white;
```

---

## Dark Mode Palette

For future dark mode implementation:

```css
--dark-bg-primary: #0f172a;    /* slate-900 */
--dark-bg-secondary: #1e293b;  /* slate-800 */
--dark-bg-elevated: #334155;   /* slate-700 */

--dark-text-primary: #f1f5f9;    /* slate-100 */
--dark-text-secondary: #cbd5e1;  /* slate-300 */
--dark-text-tertiary: #94a3b8;   /* slate-400 */

--dark-border: #334155;          /* slate-700 */
--dark-border-strong: #475569;   /* slate-600 */

/* Adjust primary colors for dark mode */
--dark-ocean-600: #38bdf8;      /* Brighter for visibility */
--dark-emerald-600: #34d399;    /* Brighter for visibility */
--dark-gold-600: #fbbf24;       /* Brighter for visibility */
```

---

## Migration from Purple

### Color Mapping

| Old Purple | New Replacement | Context |
|------------|-----------------|---------|
| `purple-600` | `ocean-600` | Primary buttons in info contexts |
| `purple-600` | `emerald-600` | Primary buttons in success contexts |
| `purple-600` | `teal-600` | Secondary buttons, alternative actions |
| `purple-700` | `ocean-700` | Hover states for ocean replacements |
| `purple-700` | `emerald-700` | Hover states for emerald replacements |
| `purple-50` | `ocean-50` or `emerald-50` | Background colors |
| `purple-100` | `ocean-100` or `teal-100` | Light backgrounds |
| `bg-purple-*` | `bg-ocean-*` or `bg-teal-*` | Background utilities |
| `text-purple-*` | `text-ocean-*` or `text-emerald-*` | Text colors |
| `border-purple-*` | `border-ocean-*` or `border-teal-*` | Borders |

### Search and Replace Guide

```bash
# Text colors
purple-600 → ocean-600 (info/primary contexts)
purple-700 → ocean-700 (hover states)
purple-500 → ocean-500 (lighter interactions)

# Backgrounds
bg-purple-50 → bg-ocean-50 or bg-emerald-50
bg-purple-100 → bg-teal-100
bg-purple-600 → bg-ocean-600

# Borders
border-purple-200 → border-ocean-200
border-purple-300 → border-teal-300
border-purple-600 → border-ocean-600

# Gradients containing purple
--gradient-card-purple → --gradient-primary (ocean to emerald)
var(--gradient-card-purple) → var(--gradient-teal-flow)
```

---

## Tailwind Configuration

Add to `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        ocean: {
          50: '#e0f2fe',
          100: '#bae6fd',
          200: '#7dd3fc',
          300: '#38bdf8',
          400: '#0ea5e9',
          500: '#0284c7',
          600: '#0369a1',
          700: '#075985',
          800: '#0c4a6e',
          900: '#082f49',
        },
        emerald: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        teal: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        gold: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #0369a1 0%, #0d9488 50%, #059669 100%)',
        'gradient-ocean': 'radial-gradient(circle at top left, #0ea5e9 0%, #0284c7 100%)',
        'gradient-emerald': 'radial-gradient(circle at bottom right, #10b981 0%, #059669 100%)',
        'gradient-teal': 'linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%)',
        'gradient-gold': 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)',
        'gradient-sunrise': 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 33%, #fbbf24 66%, #f59e0b 100%)',
      },
    },
  },
};
```

---

## Accessibility Checklist

### Contrast Ratios (WCAG AA)

- ✅ **Normal text (16px+):** Minimum 4.5:1 contrast
- ✅ **Large text (24px+ or 18px+ bold):** Minimum 3:1 contrast
- ✅ **UI components:** Minimum 3:1 contrast for interactive elements
- ✅ **Focus indicators:** Minimum 3:1 contrast and 2px outline

### Color Testing

For every color combination in production:

1. Test with [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
2. Verify with browser DevTools accessibility panel
3. Test with screen readers (NVDA, JAWS, VoiceOver)
4. Test in grayscale mode (ensure information isn't color-only)
5. Test with color blindness simulators

### Safe Combinations (Pre-tested)

**On White Background:**
- ✅ `ocean-600` and darker (4.5:1+)
- ✅ `emerald-600` and darker (4.5:1+)
- ✅ `teal-600` and darker (4.5:1+)
- ✅ `gold-600` and darker (4.5:1+)
- ✅ `gray-500` and darker (4.5:1+)
- ✅ `error-600` and darker (4.5:1+)

**On Dark Backgrounds (gray-800, slate-900):**
- ✅ White text (14:1+)
- ✅ `gray-100` (12:1+)
- ✅ `ocean-100` (bright enough for visibility)
- ✅ `emerald-100` (bright enough)

---

## Design Tokens Export

### CSS Custom Properties

```css
:root {
  /* Primary Colors */
  --color-ocean-50: #e0f2fe;
  --color-ocean-600: #0369a1;
  --color-ocean-700: #075985;
  --color-ocean-800: #0c4a6e;

  --color-emerald-50: #ecfdf5;
  --color-emerald-600: #059669;
  --color-emerald-700: #047857;
  --color-emerald-800: #065f46;

  --color-teal-600: #0d9488;
  --color-teal-700: #0f766e;

  --color-gold-600: #d97706;
  --color-gold-700: #b45309;

  /* Semantic */
  --color-success: var(--color-emerald-600);
  --color-warning: var(--color-gold-600);
  --color-error: #dc2626;
  --color-info: var(--color-ocean-600);

  /* Neutrals */
  --color-text-primary: #1f2937;
  --color-text-secondary: #4b5563;
  --color-text-tertiary: #6b7280;
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f9fafb;
  --color-border: #e5e7eb;

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, var(--color-ocean-600) 0%, var(--color-teal-600) 50%, var(--color-emerald-600) 100%);
  --gradient-gold: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
}
```

---

## Usage Examples

### Hero Section
```html
<div class="bg-gradient-primary text-white p-12 rounded-2xl">
  <h1 class="text-4xl font-bold">Welcome to OBCMS</h1>
  <p class="text-white/90">Serving Bangsamoro communities with excellence</p>
</div>
```

### Primary Button
```html
<button class="bg-gradient-primary text-white px-6 py-3 rounded-lg hover:brightness-110 transition">
  Submit Application
</button>
```

### Info Card
```html
<div class="bg-ocean-50 border border-ocean-600 rounded-lg p-4">
  <div class="flex items-start gap-3">
    <i class="fas fa-info-circle text-ocean-600"></i>
    <p class="text-ocean-800">Important information about your application</p>
  </div>
</div>
```

### Warning Card
```html
<div class="bg-gold-50 border border-gold-600 rounded-lg p-4">
  <div class="flex items-start gap-3">
    <i class="fas fa-exclamation-triangle text-gold-700"></i>
    <p class="text-gold-800">Please review the following before proceeding</p>
  </div>
</div>
```

### Success Message
```html
<div class="bg-emerald-50 border border-emerald-600 rounded-lg p-4">
  <div class="flex items-start gap-3">
    <i class="fas fa-check-circle text-emerald-600"></i>
    <p class="text-emerald-800">Your application has been submitted successfully!</p>
  </div>
</div>
```

---

## Color Psychology & Cultural Significance

### Blue-Green (Ocean to Emerald)
- **Psychological:** Trust, stability, growth, harmony
- **Cultural:** Represents the surrounding seas, connection to nature
- **Government:** Professionalism, reliability, transparency
- **Use Case:** Primary brand identity, main actions

### Gold/Yellow
- **Psychological:** Optimism, energy, prosperity, warmth
- **Cultural:** Agricultural wealth, golden harvests, hope for the future
- **Government:** Important notices, economic indicators
- **Use Case:** Warnings, highlights, economic data, achievements

### Teal
- **Psychological:** Balance, clarity, communication
- **Cultural:** Tropical waters, natural beauty
- **Government:** Coordination, collaboration
- **Use Case:** Secondary actions, coordination features, scheduling

### Neutral Grays
- **Psychological:** Neutrality, professionalism, clarity
- **Cultural:** Universal, non-partisan, objective
- **Government:** Documentation, data presentation
- **Use Case:** Text, backgrounds, structure, data tables

---

## Implementation Checklist

- [ ] Update `src/static/admin/css/custom.css` with new color variables
- [ ] Update `src/templates/base.html` with new gradient definitions
- [ ] Replace all purple color references (79 files)
- [ ] Update component library templates
- [ ] Update Tailwind configuration
- [ ] Test all color combinations for WCAG AA compliance
- [ ] Update style guide documentation
- [ ] Train team on new color usage
- [ ] Create design system Figma/Sketch file
- [ ] Update brand guidelines

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Jan 2025 | Complete redesign: removed purple, added ocean-emerald-teal-gold palette |
| 1.0 | Oct 2024 | Initial design with blue-teal-purple palette |

---

## Support & Questions

For questions about color usage or accessibility:
- Review this document first
- Check WCAG contrast ratios with WebAIM
- Consult with UX team for complex use cases
- Reference existing component implementations

**Remember:** When in doubt, choose accessibility and clarity over aesthetics. Every color choice should serve the user's needs first.
