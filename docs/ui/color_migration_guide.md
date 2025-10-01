# OBCMS Color Migration Guide
**Removing Purple Colors & Implementing New Color System**

**Version:** 1.0
**Date:** January 2025
**Affected Files:** 79 templates
**Estimated Time:** 2-3 hours

---

## Overview

This guide provides step-by-step instructions for migrating from the old color system (with purple) to the new OBCMS color system featuring ocean-blue, emerald-green, teal, and gold accents.

---

## Pre-Migration Checklist

- [ ] Read `docs/ui/obcms_color_system.md` thoroughly
- [ ] Backup database: `./scripts/db_backup.sh`
- [ ] Create git branch: `git checkout -b feature/color-system-migration`
- [ ] Test environment is set up and working
- [ ] Have access to all 79 files identified in analysis

---

## Step 1: Update CSS Custom Properties

### File: `src/static/admin/css/custom.css`

**Lines to Update:** 60-77 (purple color definitions)

**Find and Replace:**

```css
/* OLD - Remove these lines */
--purple-700: #7c3aed;
--purple-800: #6b21a8;
--gradient-card-purple: linear-gradient(135deg, #6b21a8 0%, #7c3aed 100%);
--highlight-indigo: linear-gradient(135deg, rgba(59, 130, 246, 0.16) 0%, rgba(99, 102, 241, 0.08) 100%);
```

```css
/* NEW - Add these lines */
/* Ocean Blue */
--ocean-50: #e0f2fe;
--ocean-100: #bae6fd;
--ocean-200: #7dd3fc;
--ocean-300: #38bdf8;
--ocean-400: #0ea5e9;
--ocean-500: #0284c7;
--ocean-600: #0369a1;
--ocean-700: #075985;
--ocean-800: #0c4a6e;
--ocean-900: #082f49;

/* Teal */
--teal-50: #f0fdfa;
--teal-100: #ccfbf1;
--teal-200: #99f6e4;
--teal-300: #5eead4;
--teal-400: #2dd4bf;
--teal-500: #14b8a6;
--teal-600: #0d9488;
--teal-700: #0f766e;
--teal-800: #115e59;
--teal-900: #134e4a;

/* Gold */
--gold-50: #fffbeb;
--gold-100: #fef3c7;
--gold-200: #fde68a;
--gold-300: #fcd34d;
--gold-400: #fbbf24;
--gold-500: #f59e0b;
--gold-600: #d97706;
--gold-700: #b45309;
--gold-800: #92400e;
--gold-900: #78350f;

/* Update gradients */
--gradient-primary: linear-gradient(135deg, #0369a1 0%, #0d9488 50%, #059669 100%);
--gradient-ocean: radial-gradient(circle at top left, #0ea5e9 0%, #0284c7 100%);
--gradient-teal-flow: linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%);
--gradient-gold: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
--gradient-sunrise: linear-gradient(135deg, #0ea5e9 0%, #14b8a6 33%, #fbbf24 66%, #f59e0b 100%);

/* Replace highlight-indigo */
--highlight-ocean: linear-gradient(135deg, rgba(3, 105, 161, 0.12) 0%, rgba(14, 165, 233, 0.06) 100%);
```

---

## Step 2: Global Find & Replace

Use your IDE's "Find in Files" feature across `src/templates/`:

### Text Colors

```bash
# Primary purple text → ocean
"text-purple-600" → "text-ocean-600"
"text-purple-700" → "text-ocean-700"
"text-purple-500" → "text-ocean-500"
"text-purple-800" → "text-ocean-800"

# Special cases
"text-purple-600" → "text-teal-600"  # For secondary/alternative contexts
"text-purple-600" → "text-emerald-600"  # For success contexts
```

### Background Colors

```bash
# Light backgrounds
"bg-purple-50" → "bg-ocean-50"
"bg-purple-100" → "bg-teal-100"

# Medium backgrounds
"bg-purple-200" → "bg-ocean-200"
"bg-purple-300" → "bg-teal-300"

# Dark backgrounds
"bg-purple-600" → "bg-ocean-600"
"bg-purple-700" → "bg-ocean-700"
"bg-purple-800" → "bg-ocean-800"

# Gradient backgrounds
"bg-purple-gradient" → "bg-gradient-primary"
```

### Border Colors

```bash
"border-purple-200" → "border-ocean-200"
"border-purple-300" → "border-teal-300"
"border-purple-600" → "border-ocean-600"
"border-purple-700" → "border-ocean-700"
```

### Hover States

```bash
"hover:bg-purple-600" → "hover:bg-ocean-600"
"hover:bg-purple-100" → "hover:bg-ocean-100"
"hover:text-purple-600" → "hover:text-ocean-600"
"hover:border-purple-600" → "hover:border-ocean-600"
```

### Focus States

```bash
"focus:ring-purple-500" → "focus:ring-emerald-500"
"focus:border-purple-500" → "focus:border-emerald-500"
```

---

## Step 3: Context-Specific Replacements

Some purple colors need different replacements based on context:

### Dashboard Cards (Admin Index)

**File:** `src/templates/admin/index.html`

```html
<!-- OLD -->
<div class="obc-dashboard-highlight--indigo">...</div>

<!-- NEW - Choose based on content type -->
<!-- For info/general -->
<div class="obc-dashboard-highlight--ocean">...</div>

<!-- For success/completed -->
<div class="obc-dashboard-highlight--emerald">...</div>

<!-- For warnings/pending -->
<div class="obc-dashboard-highlight--gold">...</div>
```

### Quick Action Cards

**Files:** Various dashboard home templates

```html
<!-- OLD -->
<a class="obc-quick-card--magenta">
  <div class="obc-quick-card__icon" style="background: var(--secondary-purple)">
    <i class="fas fa-users"></i>
  </div>
  ...
</a>

<!-- NEW -->
<a class="obc-quick-card--ocean">
  <div class="obc-quick-card__icon" style="background: var(--ocean-600)">
    <i class="fas fa-users"></i>
  </div>
  ...
</a>
```

### Badges & Pills

```html
<!-- OLD -->
<span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
  Status
</span>

<!-- NEW - Info/General -->
<span class="bg-ocean-100 text-ocean-800 px-3 py-1 rounded-full">
  Status
</span>

<!-- NEW - Important/Featured -->
<span class="bg-gold-100 text-gold-800 px-3 py-1 rounded-full">
  Featured
</span>
```

### Buttons

```html
<!-- OLD -->
<button class="bg-purple-600 hover:bg-purple-700 text-white">
  Submit
</button>

<!-- NEW - Primary Actions -->
<button class="bg-ocean-600 hover:bg-ocean-700 text-white">
  Submit
</button>

<!-- NEW - Alternative Actions -->
<button class="bg-teal-600 hover:bg-teal-700 text-white">
  Alternative Action
</button>

<!-- NEW - Warning/Important -->
<button class="bg-gold-600 hover:bg-gold-700 text-white">
  Important Action
</button>
```

---

## Step 4: Update Gradient Classes

### Find Gradient References

Search for:
- `var(--gradient-card-purple)`
- `--gradient-card-purple`
- `.obc-quick-card--magenta`

### Replace With

```css
/* OLD */
.obc-quick-card--magenta {
  background: var(--gradient-card-purple);
}

/* NEW - Option 1: Primary gradient */
.obc-quick-card--ocean {
  background: var(--gradient-primary);
}

/* NEW - Option 2: Teal flow */
.obc-quick-card--teal {
  background: var(--gradient-teal-flow);
}

/* NEW - Option 3: Gold (for warnings/important) */
.obc-quick-card--gold {
  background: var(--gradient-gold);
}
```

---

## Step 5: File-by-File Manual Review

After global replacements, manually review these high-traffic files:

### Priority 1: Admin & Dashboard

1. **`src/templates/admin/base.html`**
   - Check header gradient (should use `--gradient-primary`)
   - Verify navigation colors

2. **`src/templates/admin/index.html`**
   - Update dashboard cards
   - Check highlight colors
   - Verify metric cards

3. **`src/templates/common/dashboard.html`**
   - Hero section gradient
   - Quick action cards
   - Stat cards

4. **`src/templates/base.html`**
   - Update CSS variables
   - Check navigation

### Priority 2: Module Home Pages

5. **`src/templates/communities/communities_home.html`**
6. **`src/templates/coordination/coordination_home.html`**
7. **`src/templates/mana/mana_home.html`**
8. **`src/templates/recommendations/recommendations_home.html`**

For each:
- Hero sections should use `bg-gradient-primary` or `bg-ocean-600`
- Feature cards should use ocean/teal/emerald based on context
- CTAs should use primary gradient or solid ocean-600

### Priority 3: Forms

9. **All form templates**
   - Focus rings: `focus:ring-emerald-500`
   - Primary buttons: `bg-ocean-600 hover:bg-ocean-700`
   - Secondary buttons: `border-ocean-600 text-ocean-700`

### Priority 4: Data Tables

10. **All `*_manage.html` files**
    - Header backgrounds: `bg-ocean-50` or gradient
    - Row hover: `hover:bg-ocean-50`
    - Action buttons: ocean or teal colors

---

## Step 6: Component Updates

### Update Reusable Components

#### `src/templates/components/data_table_card.html`

```html
<!-- OLD -->
<div class="bg-gradient-to-r from-purple-600 to-indigo-600 ...">

<!-- NEW -->
<div class="bg-gradient-primary ...">
```

#### Form Components

Check all form components for purple references:
- `src/templates/components/form_field.html`
- `src/templates/components/form_field_select.html`
- `src/templates/components/form_field_input.html`

Update focus states:
```html
<!-- OLD -->
class="focus:ring-purple-500 focus:border-purple-500"

<!-- NEW -->
class="focus:ring-emerald-500 focus:border-emerald-500"
```

---

## Step 7: Testing Checklist

After replacements, test each module:

### Visual Testing

- [ ] Admin dashboard loads correctly
- [ ] All module home pages render properly
- [ ] Forms show correct focus states
- [ ] Buttons have proper hover states
- [ ] Cards display with correct colors
- [ ] Gradients render smoothly
- [ ] No purple colors visible anywhere

### Functional Testing

- [ ] Click all buttons (verify hover/active states)
- [ ] Tab through forms (verify focus indicators)
- [ ] Hover over interactive elements
- [ ] Check responsive behavior on mobile
- [ ] Test dark mode (if enabled)

### Accessibility Testing

- [ ] Run WCAG contrast checker on all text/background combinations
- [ ] Verify focus indicators are visible (3:1 contrast minimum)
- [ ] Test with screen reader
- [ ] Check keyboard navigation
- [ ] Verify all interactive elements are distinguishable

### Browser Testing

- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers (iOS Safari, Chrome Android)

---

## Step 8: Update Documentation

After successful migration:

1. **Update README.md**
   - Link to new color system docs
   - Remove purple color references

2. **Update CLAUDE.md**
   - Update color system section
   - Add ocean/teal/gold as primary colors

3. **Update component documentation**
   - Replace purple examples
   - Add ocean/teal/gold examples

---

## Rollback Plan

If issues arise, rollback using:

```bash
# Revert git changes
git checkout main -- src/templates/
git checkout main -- src/static/

# Restore database backup
./scripts/db_restore.sh db.sqlite3.backup_[timestamp]

# Restart server
./manage.py runserver
```

---

## Common Issues & Solutions

### Issue 1: Gradient Not Displaying

**Symptom:** Gradient shows as solid color or transparent

**Solution:**
```css
/* Make sure gradient is defined in :root */
:root {
  --gradient-primary: linear-gradient(135deg, #0369a1 0%, #0d9488 50%, #059669 100%);
}

/* Use var() to reference */
background: var(--gradient-primary);
```

### Issue 2: Focus Ring Not Visible

**Symptom:** Focus indicator too faint or wrong color

**Solution:**
```html
<!-- Ensure proper focus classes -->
<input class="focus:ring-4 focus:ring-emerald-500/20 focus:border-emerald-600" />
```

### Issue 3: Text Contrast Insufficient

**Symptom:** Text hard to read, fails WCAG

**Solution:**
```html
<!-- Use darker shades for text on white -->
<!-- ❌ BAD -->
<p class="text-ocean-400">Hard to read</p>

<!-- ✅ GOOD -->
<p class="text-ocean-700">Easy to read</p>
```

### Issue 4: Tailwind Classes Not Working

**Symptom:** Custom ocean/teal/gold colors not recognized

**Solution:**
1. Ensure Tailwind config updated (see Step 9)
2. Rebuild Tailwind: `npm run build:css` (if using build process)
3. Clear browser cache
4. Restart dev server

---

## Step 9: Update Tailwind Configuration

### File: `tailwind.config.js`

If project has a Tailwind config file (check if it exists):

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Add ocean colors
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
        // Teal (if not in default Tailwind)
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
        // Add gold colors
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
        'gradient-teal-flow': 'linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%)',
        'gradient-gold': 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)',
        'gradient-sunrise': 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 33%, #fbbf24 66%, #f59e0b 100%)',
      },
    },
  },
  plugins: [],
};
```

**If no config file exists:** The project uses Tailwind CDN. Custom colors should be defined in CSS variables (already done in Step 1).

---

## Step 10: Verification Script

Run this script to find any remaining purple references:

```bash
#!/bin/bash
# find_purple_colors.sh

echo "Searching for purple color references..."
echo "========================================"

# Search in templates
echo -e "\n📄 Templates:"
grep -r "purple" src/templates/ --include="*.html" | wc -l

# Search in CSS
echo -e "\n🎨 CSS Files:"
grep -r "purple" src/static/ --include="*.css" | wc -l

# Search in JS
echo -e "\n⚙️  JavaScript Files:"
grep -r "purple" src/static/ --include="*.js" | wc -l

# List specific files with purple references
echo -e "\n📋 Files still containing 'purple':"
grep -r "purple" src/templates/ src/static/ --include="*.html" --include="*.css" --include="*.js" -l

echo -e "\n✅ If count is 0, migration is complete!"
```

Save as `scripts/find_purple_colors.sh`, make executable:

```bash
chmod +x scripts/find_purple_colors.sh
./scripts/find_purple_colors.sh
```

---

## Completion Checklist

Mark as complete when:

- [ ] All 79 template files reviewed
- [ ] CSS custom properties updated
- [ ] No purple colors found in verification script
- [ ] All visual tests pass
- [ ] All functional tests pass
- [ ] WCAG contrast ratios verified
- [ ] Documentation updated
- [ ] Git commit created with clear message
- [ ] Pull request created and reviewed
- [ ] Changes deployed to staging
- [ ] Staging tested by team
- [ ] Changes deployed to production

---

## Git Commit Message Template

```
feat(ui): Migrate to new OBCMS color system

Remove all purple colors and implement new ocean-blue,
emerald-green, teal, and gold color palette.

Breaking changes:
- Removed all purple color variables
- Updated 79 template files
- Changed gradient definitions
- Updated focus ring colors

New features:
- Ocean blue primary color (WCAG AA compliant)
- Emerald green success states
- Teal for secondary actions
- Gold for warnings and highlights

Accessibility:
- All colors tested for WCAG AA compliance
- Improved contrast ratios on all text
- Enhanced focus indicators

Closes #[issue-number]
```

---

## Post-Migration Tasks

After successful deployment:

1. **Monitor for Issues**
   - Watch error logs for CSS issues
   - Check user feedback channels
   - Monitor accessibility reports

2. **Update Style Guide**
   - Create visual style guide with examples
   - Update Figma/design files
   - Train team on new colors

3. **Archive Old System**
   - Document old purple system for reference
   - Keep backup of old CSS for 30 days
   - Update changelog

4. **Celebrate!** 🎉
   - The new color system is live!
   - Improved accessibility
   - Better brand alignment
   - More professional appearance

---

## Support

For issues during migration:

1. Check this guide first
2. Review `docs/ui/obcms_color_system.md`
3. Test with WebAIM Contrast Checker
4. Check browser DevTools for CSS errors
5. Consult with UX/frontend team

**Remember:** Take your time, test thoroughly, and prioritize accessibility!
