# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ultrathink

Always use "Ultrathink" whenever you are responding or coding in Claude Code to show your thinking process. No exception.

## Development Environment Setup

**Virtual Environment**: Always work from Python 3.12 `venv/`
```bash
./scripts/bootstrap_venv.sh  # idempotent helper
source venv/bin/activate     # On Windows: venv\Scripts\activate
```

**Working Directory**: All Django commands must be run from the `src/` directory
```bash
cd src
./manage.py [command]
```

## Common Development Commands

### Database Operations

**⚠️ CRITICAL WARNING: NEVER DELETE THE DATABASE ⚠️**

**NEVER run `rm db.sqlite3` or delete the database file.** This database contains valuable development data, user accounts, and test data that are essential for ongoing development. Always apply migrations to the existing database using `./manage.py migrate`.

If you encounter migration issues:
1. **DO NOT delete the database**
2. Fix migration conflicts properly using Django migration tools
3. Use `./manage.py migrate --fake` if needed
4. Ask the user before taking any destructive action

```bash
cd src
./manage.py makemigrations
./manage.py migrate  # Apply migrations to EXISTING database
./manage.py createsuperuser
```

### Development Server
```bash
cd src
./manage.py runserver
# Server runs at http://localhost:8000
# Admin interface: http://localhost:8000/admin/
```

### Code Quality and Testing
```bash
# Code formatting and linting
black .
isort .
flake8

# Testing
pytest
coverage run -m pytest
coverage report
```

### Dependencies
```bash
# Install development dependencies
pip install -r requirements/development.txt

# Install production dependencies only
pip install -r requirements/base.txt
```

## Architecture Overview

### Django Project Structure
- **Main Project**: `src/obc_management/` - Django settings and main configuration
- **Applications**: Each module is a separate Django app with models, views, admin, and migrations
- **Environment**: Uses `django-environ` for environment variable management with `.env` file

### Core Applications
1. **common**: Base models, utilities, and shared functionality
2. **communities**: OBC (Other Bangsamoro Communities) profile and demographic management
3. **mana**: Mapping and Needs Assessment functionality 
4. **coordination**: Multi-stakeholder coordination and partnership management
5. **policies**: Policy recommendation tracking and evidence-based proposals

### Key Technical Components
- **Authentication**: Django built-in auth + JWT (SimpleJWT) for API access
- **API**: Django REST Framework with pagination, filtering, and browsable interface
- **Database**: SQLite for development, configurable for PostgreSQL production
- **Background Tasks**: Celery with Redis broker for async operations
- **Logging**: File and console logging configured, logs written to `src/logs/`

## Domain-Specific Context

### OOBC Mission
This system supports the Office for Other Bangsamoro Communities (OOBC) serving Bangsamoro communities outside BARMM (Bangsamoro Autonomous Region in Muslim Mindanao). 

### Geographic Scope
- Primary focus: Regions IX (Zamboanga Peninsula) and XII (SOCCSKSARGEN)
- Administrative hierarchy: Region > Province > Municipality > Barangay
- Timezone: Asia/Manila

### Cultural Considerations
- Islamic education integration (Madaris, Arabic teachers)
- Halal industry and traditional crafts
- Cultural and religious information management
- Respect for Bangsamoro cultural practices in UI/UX

### Assessment Areas (MANA)
- Education (scholarships, Islamic education)
- Economic Development (Halal industry, MSMEs, agriculture/fisheries)
- Social Development (TABANG, AMBag programs)
- Cultural Development (heritage preservation, traditional crafts)
- Infrastructure (healthcare, utilities, roads)

## Environment Configuration

### Required Environment Variables
```env
SECRET_KEY=your-secret-key
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///path/to/db (or postgres://...)
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Settings Configuration
- **Debug Toolbar**: Automatically enabled in DEBUG mode
- **CORS**: Configured for localhost development
- **JWT**: 1-hour access tokens, 7-day refresh tokens
- **Pagination**: 20 items per page default

### Static Files Configuration
- **Location**: All static files are in `src/static/` (centralized approach)
- **Configuration**: `STATICFILES_DIRS = [BASE_DIR.parent / "static"]` points to `src/static/`
- **Structure**:
  - `src/static/common/` - Common app assets (CSS, JS, vendor/fullcalendar)
  - `src/static/vendor/` - Shared vendor libraries (Leaflet, localforage, idb)
  - `src/static/admin/` - Admin interface customizations
- **Important**: Server restart required after modifying `STATICFILES_DIRS`
- **See**: [docs/development/README.md](docs/development/README.md#static-files-architecture) for complete documentation

## Development Guidelines

### Model Relationships
- Use timezone-aware datetime fields (`USE_TZ = True`)
- Follow Django naming conventions for models and fields
- Implement proper `__str__` methods for admin interface
- Use foreign keys and many-to-many relationships appropriately for stakeholder connections

### API Development
- All APIs require authentication by default
- Use DRF filtering, searching, and ordering
- Implement proper serializers with validation
- Follow REST principles for URL patterns

### Frontend Integration
- Templates in `src/templates/` with Django template language
- Static files in `src/static/` served during development
- Uses Tailwind CSS for responsive, government-appropriate styling
- Support for dark mode and accessibility (WCAG 2.1 AA)

### Form Component Library
- Reusable form partials are under `src/templates/components/` (`form_field.html`, `form_field_input.html`, `form_field_select.html`).
- Include them in templates instead of duplicating markup, e.g. `{% include "components/form_field_select.html" with field=form.municipality placeholder="Select municipality..." %}` to match the Barangay OBC dropdown styling.
- Widget classes are centralised via `_apply_form_field_styles` (see `src/common/forms/staff.py`); extend there when new input patterns are needed.

### Form Design Standards
**IMPORTANT**: When designing or modifying forms, ALWAYS reference existing templates for UI/UX consistency:
- **Review similar forms** in `src/templates/` to understand established patterns
- **Use component templates** (`src/templates/components/`) for standard form elements
- **Follow dropdown styling**: Use `rounded-xl`, `border-gray-200`, emerald focus rings, chevron icons
- **Standard dropdown pattern**:
  ```html
  <div class="space-y-1">
      <label for="field-id" class="block text-sm font-medium text-gray-700 mb-2">
          Field Label<span class="text-red-500">*</span>
      </label>
      <div class="relative">
          <select id="field-id" name="field_name" class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200">
              <option value="">Select...</option>
          </select>
          <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
              <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
          </span>
      </div>
  </div>
  ```
- **Check reference templates**: `src/templates/communities/provincial_manage.html`, `src/templates/components/form_field_select.html`
- **Maintain consistency** in spacing, colors, borders, and interactive states across all forms

### Data Table Cards
- Directory/list pages should extend `components/data_table_card.html` so Barangay and Municipal OBC lists stay visually aligned.
- Pass a `headers` array and `rows` data with `view_url`, `edit_url`, and `delete_preview_url`. The component already handles the action buttons and the two-step delete confirmation (confirm dialog → redirect to detail for "Review before deletion").

## Instant UI & Smooth User Experience

### Priority: Always Implement Instant UI Updates
When working on this codebase, **always prioritize instant UI responses** and smooth interactions. Users expect modern web app behavior - no full page reloads, immediate feedback, and seamless transitions.

### HTMX Implementation Requirements
- **Consistent Targeting**: All interactive elements must use `data-task-id="{{ item.id }}"` for both kanban cards and table rows
- **Optimistic Updates**: Update the UI immediately when user performs an action, then handle server response
- **Smooth Animations**: Use `hx-swap="outerHTML swap:300ms"` or `delete swap:200ms` for transitions
- **Loading Indicators**: Always show spinners, disabled states, or progress feedback during operations

### Backend Response Standards
All views handling HTMX requests must follow this pattern:
```python
def task_operation_view(request, task_id):
    # ... perform operation ...

    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'task-updated': {'id': task_id, 'action': 'delete'},
                    'show-toast': 'Task updated successfully',
                    'refresh-counters': True
                })
            }
        )
```

### UI Animation Standards
- **Task Movements**: 300ms smooth transitions between kanban columns
- **Modal Interactions**: Fade with scale transform for open/close
- **Button Feedback**: Immediate visual response to clicks (color change, disable state)
- **Error Handling**: Clear error states with recovery options, no silent failures

### Critical: Never Use Full Page Reloads
- Implement HTMX for all CRUD operations (Create, Read, Update, Delete)
- Use out-of-band swaps (`hx-swap-oob`) for updating multiple UI regions simultaneously
- Provide graceful fallback mechanisms when HTMX fails
- Maintain accessibility with proper ARIA live regions and state updates

### Current Issue to Fix
**Known Bug**: Task deletion in kanban view (`/oobc-management/staff/tasks/`) doesn't remove cards instantly. The modal targets `[data-task-row]` but kanban uses `[data-task-id]`. This must be fixed to ensure instant UI updates.

For detailed implementation guidance, refer to `docs/improvements/instant_ui_improvements_plan.md`.

## Documentation Guidelines

### Where to Write Documentation

**CRITICAL: All documentation files MUST be placed under the `docs/` directory.**

#### Documentation Organization Structure
```
docs/
├── deployment/          # Deployment guides, production setup
├── development/         # Development guidelines (NOT AI config)
├── testing/            # Testing guides, verification reports
├── reference/          # Technical reference (coordinates, standards)
├── improvements/       # Implementation tracking, improvement plans
├── guidelines/         # Program guidelines (MANA, policies)
├── product/           # Product roadmap, architecture
├── reports/           # Research, analysis reports
├── env/               # Environment-specific configs
├── admin-guide/       # Admin operations
└── ui/                # UI/UX documentation
```

#### Documentation Rules

1. **NEVER create documentation in project root**
   - ❌ Wrong: `NEW_FEATURE_GUIDE.md` in root
   - ✅ Correct: `docs/development/NEW_FEATURE_GUIDE.md`

2. **Choose the appropriate category:**
   - Implementation tracking → `docs/improvements/`
   - Deployment instructions → `docs/deployment/`
   - Testing procedures → `docs/testing/`
   - User guides → `docs/guidelines/`
   - Technical specs → `docs/reference/`

3. **Update the main index:**
   - After creating new docs, add them to `docs/README.md`
   - Include in the appropriate category section

4. **Use relative links:**
   - Within docs/: `[link](../other-category/file.md)`
   - From root to docs: `[link](docs/category/file.md)`

#### Configuration Files vs Documentation

**Configuration files stay in ROOT:**
- ✅ `CLAUDE.md` - AI configuration (ROOT)
- ✅ `GEMINI.md` - AI configuration (ROOT)
- ✅ `AGENTS.md` - AI configuration (ROOT)
- ✅ `README.md` - Project overview (ROOT)
- ✅ `.env.example` - Environment template (ROOT)

**Documentation files go in docs/:**
- ✅ `docs/development/README.md` - Development guide
- ✅ `docs/deployment/production-guide.md` - Deployment docs
- ✅ `docs/improvements/feature-plan.md` - Implementation plans

#### Example: Creating New Documentation

When implementing a new feature:

```bash
# ❌ WRONG - Don't create in root
echo "# New Feature" > AWESOME_FEATURE.md

# ✅ CORRECT - Create in appropriate docs/ subdirectory
echo "# New Feature" > docs/improvements/awesome_feature_implementation.md

# Update the index
# Add entry to docs/README.md under appropriate section
```

### Documentation Checklist

When creating or updating documentation:
- [ ] File is in appropriate `docs/` subdirectory
- [ ] Added to `docs/README.md` index
- [ ] Uses relative links correctly
- [ ] Follows naming convention (lowercase, underscores)
- [ ] Includes metadata (date, status, author if applicable)

**Reference:** See [docs/DOCUMENTATION_ORGANIZATION.md](docs/DOCUMENTATION_ORGANIZATION.md) for organization details.
