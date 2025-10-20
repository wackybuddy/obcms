# Mobile Responsiveness Patterns

Comprehensive guide to mobile-responsive design patterns for OBCMS using Tailwind CSS.

## Table of Contents

1. [Responsive Breakpoints](#responsive-breakpoints)
2. [Mobile-First Approach](#mobile-first-approach)
3. [Responsive Grid Layouts](#responsive-grid-layouts)
4. [Mobile Navigation Patterns](#mobile-navigation-patterns)
5. [Responsive Tables](#responsive-tables)
6. [Touch-Friendly Interactions](#touch-friendly-interactions)
7. [Modal Dialogs on Mobile](#modal-dialogs-on-mobile)
8. [Form Layouts](#form-layouts)
9. [Typography Scaling](#typography-scaling)
10. [Testing Across Devices](#testing-across-devices)

---

## Responsive Breakpoints

### Tailwind CSS Breakpoints

OBCMS uses standard Tailwind breakpoints:

| Breakpoint | Min Width | Target Devices |
|------------|-----------|----------------|
| `sm` | 640px | Large phones (landscape) |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large desktops |

### Mobile-First Syntax

Tailwind uses mobile-first responsive design:

```html
<!-- Base (mobile) → sm → md → lg → xl → 2xl -->
<div class="p-4 md:p-6 lg:p-8">
    <!-- Padding: 1rem on mobile, 1.5rem on tablet, 2rem on desktop -->
</div>
```

---

## Mobile-First Approach

### Principle
Design for mobile screens first, then progressively enhance for larger screens.

### Pattern: Container Padding

```html
<div class="container mx-auto px-4 md:px-6 lg:px-8">
    <!-- Content with responsive padding -->
</div>
```

### Pattern: Responsive Font Sizes

```html
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
    Page Title
</h1>

<p class="text-sm md:text-base lg:text-lg">
    Body text that scales appropriately
</p>
```

### Pattern: Hidden Elements by Screen Size

```html
<!-- Show only on mobile -->
<div class="block md:hidden">
    Mobile-only content
</div>

<!-- Hide on mobile, show on tablet+ -->
<div class="hidden md:block">
    Desktop content
</div>

<!-- Show on tablet, hide on mobile and desktop -->
<div class="hidden md:block lg:hidden">
    Tablet-only content
</div>
```

---

## Responsive Grid Layouts

### Pattern: Responsive Column Grid

```html
<!-- 1 column on mobile, 2 on tablet, 3 on desktop, 4 on large desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    <div class="card">Item 1</div>
    <div class="card">Item 2</div>
    <div class="card">Item 3</div>
    <div class="card">Item 4</div>
</div>
```

### Pattern: Responsive Sidebar Layout

```html
<div class="flex flex-col lg:flex-row gap-6">
    <!-- Sidebar: Full width on mobile, 1/4 on desktop -->
    <aside class="w-full lg:w-1/4">
        <nav class="bg-white rounded-lg shadow-sm p-4">
            <!-- Sidebar content -->
        </nav>
    </aside>

    <!-- Main content: Full width on mobile, 3/4 on desktop -->
    <main class="w-full lg:w-3/4">
        <!-- Main content -->
    </main>
</div>
```

### Pattern: Responsive Card Grid

```html
<!-- Responsive card grid with auto-fit -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
    {% for item in items %}
    <div class="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
        <h3 class="text-lg font-semibold mb-2">{{ item.title }}</h3>
        <p class="text-sm text-gray-600">{{ item.description }}</p>
    </div>
    {% endfor %}
</div>
```

---

## Mobile Navigation Patterns

### Pattern: Hamburger Menu

```html
<nav class="bg-white shadow-sm" x-data="{ mobileMenuOpen: false }">
    <div class="container mx-auto px-4">
        <div class="flex items-center justify-between h-16">
            <!-- Logo -->
            <div class="flex-shrink-0">
                <a href="/" class="text-xl font-bold text-emerald-600">OBCMS</a>
            </div>

            <!-- Desktop Navigation (hidden on mobile) -->
            <div class="hidden md:flex md:space-x-4">
                <a href="/" class="nav-link">Home</a>
                <a href="/tasks/" class="nav-link">Tasks</a>
                <a href="/projects/" class="nav-link">Projects</a>
                <a href="/assessments/" class="nav-link">Assessments</a>
            </div>

            <!-- Mobile menu button -->
            <button @click="mobileMenuOpen = !mobileMenuOpen"
                    class="md:hidden p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    aria-label="Toggle menu"
                    :aria-expanded="mobileMenuOpen.toString()">
                <i class="fas fa-bars text-xl" x-show="!mobileMenuOpen"></i>
                <i class="fas fa-times text-xl" x-show="mobileMenuOpen" x-cloak></i>
            </button>
        </div>

        <!-- Mobile Navigation (shown when menu is open) -->
        <div x-show="mobileMenuOpen"
             x-cloak
             x-transition:enter="transition ease-out duration-200"
             x-transition:enter-start="opacity-0 -translate-y-2"
             x-transition:enter-end="opacity-100 translate-y-0"
             x-transition:leave="transition ease-in duration-150"
             x-transition:leave-start="opacity-100 translate-y-0"
             x-transition:leave-end="opacity-0 -translate-y-2"
             class="md:hidden pb-4 space-y-2">
            <a href="/" class="block px-4 py-2 rounded-lg hover:bg-gray-100">Home</a>
            <a href="/tasks/" class="block px-4 py-2 rounded-lg hover:bg-gray-100">Tasks</a>
            <a href="/projects/" class="block px-4 py-2 rounded-lg hover:bg-gray-100">Projects</a>
            <a href="/assessments/" class="block px-4 py-2 rounded-lg hover:bg-gray-100">Assessments</a>
        </div>
    </div>
</nav>

<style>
[x-cloak] { display: none !important; }
</style>
```

### Pattern: Bottom Tab Bar (Mobile Only)

```html
<!-- Fixed bottom navigation for mobile -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
    <div class="grid grid-cols-4 gap-1">
        <a href="/" class="flex flex-col items-center py-3 text-xs hover:bg-gray-50 active:bg-gray-100">
            <i class="fas fa-home text-xl mb-1"></i>
            <span>Home</span>
        </a>
        <a href="/tasks/" class="flex flex-col items-center py-3 text-xs hover:bg-gray-50 active:bg-gray-100">
            <i class="fas fa-tasks text-xl mb-1"></i>
            <span>Tasks</span>
        </a>
        <a href="/projects/" class="flex flex-col items-center py-3 text-xs hover:bg-gray-50 active:bg-gray-100">
            <i class="fas fa-folder text-xl mb-1"></i>
            <span>Projects</span>
        </a>
        <a href="/profile/" class="flex flex-col items-center py-3 text-xs hover:bg-gray-50 active:bg-gray-100">
            <i class="fas fa-user text-xl mb-1"></i>
            <span>Profile</span>
        </a>
    </div>
</nav>

<!-- Add bottom padding to main content to prevent overlap -->
<main class="pb-20 md:pb-6">
    <!-- Page content -->
</main>
```

---

## Responsive Tables

### Pattern: Stack on Mobile

```html
<!-- Desktop: Table format -->
<div class="hidden md:block overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            {% for task in tasks %}
            <tr>
                <td class="px-6 py-4 text-sm">{{ task.title }}</td>
                <td class="px-6 py-4 text-sm">{{ task.get_status_display }}</td>
                <td class="px-6 py-4 text-sm">{{ task.due_date|date:"M d, Y" }}</td>
                <td class="px-6 py-4 text-sm text-right">
                    <a href="{{ task.get_absolute_url }}" class="text-blue-600 hover:underline">View</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- Mobile: Card format -->
<div class="md:hidden space-y-4">
    {% for task in tasks %}
    <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <h3 class="font-semibold text-gray-900 mb-2">{{ task.title }}</h3>

        <dl class="space-y-2 text-sm">
            <div class="flex justify-between">
                <dt class="text-gray-500">Status:</dt>
                <dd class="font-medium">{{ task.get_status_display }}</dd>
            </div>
            <div class="flex justify-between">
                <dt class="text-gray-500">Due Date:</dt>
                <dd class="font-medium">{{ task.due_date|date:"M d, Y" }}</dd>
            </div>
        </dl>

        <div class="mt-4 pt-4 border-t border-gray-200">
            <a href="{{ task.get_absolute_url }}"
               class="block w-full text-center py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                View Details
            </a>
        </div>
    </div>
    {% endfor %}
</div>
```

### Pattern: Horizontal Scroll on Mobile

```html
<div class="overflow-x-auto -mx-4 md:mx-0">
    <div class="inline-block min-w-full align-middle px-4 md:px-0">
        <table class="min-w-full divide-y divide-gray-200">
            <!-- Table content -->
        </table>
    </div>
</div>

<style>
/* Custom scrollbar for mobile tables */
.overflow-x-auto::-webkit-scrollbar {
    height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
    background: #f7fafc;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
}
</style>
```

---

## Touch-Friendly Interactions

### Pattern: Large Touch Targets

```html
<!-- Buttons with minimum 44x44px touch target -->
<button class="btn min-h-[44px] min-w-[44px] px-4 py-2 text-base">
    Submit
</button>

<!-- Icon buttons with adequate spacing -->
<div class="flex items-center gap-3">
    <button class="w-11 h-11 flex items-center justify-center rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100"
            aria-label="Edit">
        <i class="fas fa-pen"></i>
    </button>

    <button class="w-11 h-11 flex items-center justify-center rounded-lg bg-red-50 text-red-600 hover:bg-red-100"
            aria-label="Delete">
        <i class="fas fa-trash"></i>
    </button>
</div>
```

### Pattern: Swipeable Cards (Mobile)

```html
<div class="touch-pan-y overflow-x-auto snap-x snap-mandatory flex gap-4 pb-4 -mx-4 px-4 md:grid md:grid-cols-3 md:overflow-visible">
    {% for item in items %}
    <div class="snap-center flex-shrink-0 w-[85%] md:w-auto">
        <div class="bg-white rounded-lg shadow-sm p-4">
            <!-- Card content -->
        </div>
    </div>
    {% endfor %}
</div>
```

### Pattern: Pull-to-Refresh Indicator

```html
<div id="refresh-indicator"
     class="hidden fixed top-16 left-1/2 transform -translate-x-1/2 bg-emerald-500 text-white px-4 py-2 rounded-full shadow-lg z-50">
    <i class="fas fa-sync-alt animate-spin mr-2"></i>
    Refreshing...
</div>

<script>
let touchStartY = 0;

document.addEventListener('touchstart', function(e) {
    touchStartY = e.touches[0].clientY;
}, { passive: true });

document.addEventListener('touchmove', function(e) {
    const touchY = e.touches[0].clientY;
    const touchDiff = touchY - touchStartY;

    // If scrolled down from top, show refresh indicator
    if (touchDiff > 50 && window.scrollY === 0) {
        document.getElementById('refresh-indicator').classList.remove('hidden');
    }
}, { passive: true });

document.addEventListener('touchend', function() {
    const indicator = document.getElementById('refresh-indicator');

    if (!indicator.classList.contains('hidden')) {
        // Trigger refresh
        window.location.reload();
    }
}, { passive: true });
</script>
```

---

## Modal Dialogs on Mobile

### Pattern: Full-Screen Modals on Mobile

```html
<div class="modal-backdrop fixed inset-0 bg-gray-900 bg-opacity-50 flex items-end md:items-center justify-center z-50 p-0 md:p-4"
     x-data="{ show: true }"
     x-show="show"
     @click.self="show = false">

    <!-- Modal slides up on mobile, centered on desktop -->
    <div class="modal-content bg-white w-full md:max-w-2xl md:rounded-xl
                h-[90vh] md:h-auto md:max-h-[90vh]
                flex flex-col
                rounded-t-xl md:rounded-xl"
         x-show="show"
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="translate-y-full md:translate-y-0 md:opacity-0 md:scale-95"
         x-transition:enter-end="translate-y-0 md:opacity-100 md:scale-100"
         @click.stop>

        <!-- Modal Header -->
        <div class="modal-header flex items-center justify-between px-4 py-4 border-b border-gray-200 flex-shrink-0">
            <h2 class="text-lg md:text-xl font-semibold">{{ title }}</h2>
            <button @click="show = false"
                    class="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-100">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <!-- Modal Body (scrollable) -->
        <div class="modal-body flex-1 overflow-y-auto px-4 py-4">
            <!-- Content -->
        </div>

        <!-- Modal Footer (sticky on mobile) -->
        <div class="modal-footer px-4 py-4 border-t border-gray-200 flex-shrink-0 bg-white">
            <button class="w-full md:w-auto btn btn-primary">
                Submit
            </button>
        </div>
    </div>
</div>
```

---

## Form Layouts

### Pattern: Stacked Forms on Mobile

```html
<form class="space-y-6">
    <!-- Single column on mobile, two columns on desktop -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <div class="form-field">
            <label for="first-name" class="form-label">First Name</label>
            <input type="text" id="first-name" class="form-input">
        </div>

        <div class="form-field">
            <label for="last-name" class="form-label">Last Name</label>
            <input type="text" id="last-name" class="form-input">
        </div>
    </div>

    <!-- Full width field -->
    <div class="form-field">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" id="email" class="form-input">
    </div>

    <!-- Full width on mobile, half on desktop -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <div class="form-field">
            <label for="region" class="form-label">Region</label>
            <select id="region" class="form-select">
                <option>Select region...</option>
            </select>
        </div>

        <div class="form-field">
            <label for="municipality" class="form-label">Municipality</label>
            <select id="municipality" class="form-select">
                <option>Select municipality...</option>
            </select>
        </div>
    </div>

    <!-- Submit button: Full width on mobile -->
    <div class="flex flex-col md:flex-row gap-3 md:justify-end">
        <button type="button" class="btn btn-secondary w-full md:w-auto order-2 md:order-1">
            Cancel
        </button>
        <button type="submit" class="btn btn-primary w-full md:w-auto order-1 md:order-2">
            Submit
        </button>
    </div>
</form>
```

---

## Typography Scaling

### Pattern: Responsive Heading Sizes

```html
<!-- Page title -->
<h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold leading-tight">
    Page Title
</h1>

<!-- Section heading -->
<h2 class="text-xl sm:text-2xl md:text-3xl font-semibold">
    Section Heading
</h2>

<!-- Subsection heading -->
<h3 class="text-lg sm:text-xl md:text-2xl font-semibold">
    Subsection
</h3>

<!-- Body text -->
<p class="text-sm sm:text-base md:text-lg leading-relaxed">
    Body text content
</p>

<!-- Caption text -->
<p class="text-xs sm:text-sm text-gray-600">
    Caption or helper text
</p>
```

### Pattern: Responsive Line Heights

```html
<!-- Tight for headings -->
<h2 class="text-2xl leading-tight md:text-3xl md:leading-tight">
    Heading with Tight Line Height
</h2>

<!-- Relaxed for body text -->
<p class="text-base leading-relaxed md:text-lg md:leading-relaxed">
    Paragraph with comfortable reading line height
</p>
```

---

## Testing Across Devices

### Viewport Meta Tag

Ensure this is in your base template `<head>`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
```

### Device Testing Checklist

| Device Category | Screen Width | Testing Points |
|----------------|--------------|----------------|
| Mobile (portrait) | 375px - 428px | Navigation, forms, cards, touch targets |
| Mobile (landscape) | 667px - 926px | Horizontal scrolling, modals |
| Tablet (portrait) | 768px - 834px | Grid layouts, sidebars |
| Tablet (landscape) | 1024px - 1112px | Desktop features, multi-column |
| Desktop | 1280px+ | Full features, hover states |

### Browser DevTools Testing

**Chrome DevTools**:
1. Press F12 to open DevTools
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Test responsive breakpoints: 320px, 375px, 768px, 1024px, 1280px

**Firefox Responsive Design Mode**:
1. Press F12 to open DevTools
2. Click "Responsive Design Mode" (Ctrl+Shift+M)
3. Select device presets or custom dimensions

### Real Device Testing

Test on actual devices when possible:
- iPhone SE (small screen)
- iPhone 12/13/14 (standard mobile)
- iPad (tablet)
- Android phone (various manufacturers)

---

## Performance Optimization for Mobile

### Pattern: Lazy Load Images

```html
<img src="placeholder.jpg"
     data-src="actual-image.jpg"
     loading="lazy"
     class="w-full h-auto"
     alt="Description">
```

### Pattern: Responsive Images

```html
<img srcset="image-320.jpg 320w,
             image-640.jpg 640w,
             image-960.jpg 960w,
             image-1280.jpg 1280w"
     sizes="(max-width: 640px) 100vw,
            (max-width: 1024px) 50vw,
            33vw"
     src="image-640.jpg"
     alt="Description"
     class="w-full h-auto">
```

### Pattern: Reduce Motion for Accessibility

```css
/* Respect user's motion preference */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Common Mobile Pitfalls to Avoid

### Don't:
- ❌ Use fixed pixel widths
- ❌ Rely on hover states for critical interactions
- ❌ Make touch targets smaller than 44x44px
- ❌ Use tiny font sizes (< 14px for body text)
- ❌ Forget horizontal scrolling on tables
- ❌ Disable zoom (max-scale=1.0)
- ❌ Ignore landscape orientation
- ❌ Use horizontal scrolling for primary content

### Do:
- ✅ Use responsive units (%, vw, rem, em)
- ✅ Provide alternative interactions for mobile
- ✅ Make touch targets large and well-spaced
- ✅ Use readable font sizes (16px+ for body)
- ✅ Stack tables as cards on mobile
- ✅ Allow zoom for accessibility
- ✅ Test both orientations
- ✅ Keep primary content vertically scrollable

---

## Related Documentation

- [Component Library Guide](component_library_guide.md)
- [Accessibility Patterns](accessibility_patterns.md)
- [HTMX Patterns](htmx_patterns.md)
