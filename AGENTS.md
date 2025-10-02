# Repository Guidelines

## Time Estimates Policy

**NEVER provide time estimates in hours, days, weeks, or months for implementation tasks.**

With powerful AI coding agents, a year's worth of traditional development work can be completed in a single day. Time estimates create false constraints and are obsolete in AI-assisted development.

**Instead, focus on:**
- **Dependencies**: What must be done before this task (e.g., "Requires dashboard metrics view")
- **Complexity**: Simple, Moderate, or Complex
- **Priority**: Critical, High, Medium, or Low
- **Prerequisites**: What needs to exist first (e.g., "Model must exist", "API endpoint required")

**Examples:**
- ❌ Bad: "This will take 8 hours to implement"
- ❌ Bad: "Week 1, Days 2-3: Enhanced dashboard"
- ✅ Good: "Priority: HIGH | Complexity: Moderate | Requires: dashboard_metrics view"
- ✅ Good: "Prerequisites: Fix task deletion bug first (dependency)"

## Project Structure & Module Organization
The Django project lives in `src/`; `obc_management` supplies settings/URLs while feature apps (`communities`, `coordination`, `mana`, `policies`, `documents`, `policy_tracking`, `ai_assistant`) handle domain logic. Shared utilities belong in `src/common`, imports in `src/data_imports`, and templates in `src/templates`. Author tests in `src/<app>/tests.py` (split into `tests/` when needed); docs sit in `docs/`, deployment manifests in `deployment/`, and briefs in `tasks/`.

## Build, Test, and Development Commands
Run `./scripts/bootstrap_venv.sh && source venv/bin/activate` to create and enter the Python 3.12 virtualenv. `pip install -r requirements/development.txt` brings in Django, DRF, pytest, and tooling. Inside `src/`, use `./manage.py migrate` then `./manage.py runserver` for local development. `black src && isort src && flake8 src` keeps style checks clean; run `pytest --ds=obc_management.settings` (optionally `-k <pattern>`) and `coverage run -m pytest && coverage report` before merging.

### ⚠️ CRITICAL: Database Protection Policy ⚠️
**NEVER delete `src/db.sqlite3` or any database file.** The database contains essential development data, user accounts, test scenarios, and ongoing work. Always apply migrations to the existing database using `./manage.py migrate`. If migration conflicts occur: (1) DO NOT delete the database, (2) resolve conflicts using Django migration tools (`--fake`, `--fake-initial`, `squashmigrations`), (3) ask the user before any destructive action. Deleting the database destroys all development progress and is unacceptable.

## Coding Style & Naming Conventions
Black's defaults (88-character width, four spaces) govern formatting. Modules stay snake_case; models, services, and forms use PascalCase. Keep serializers beside their DRF views, management commands under `<app>/management/commands/`, and shared enums in `src/common`. Use descriptive template blocks such as `{% block community_summary %}` to clarify intent. Trigger `pre-commit run --all-files` when hooks are enabled.

### Reusable Form Components
- Shared Tailwind-ready form partials live in `src/templates/components/` (`form_field.html`, `form_field_input.html`, `form_field_select.html`).
- Prefer `{% include "components/form_field_select.html" with field=form.region placeholder="Select region..." %}` instead of hand-coding select markup so dropdowns match the Barangay OBC UI.
- The helpers already wire help text, errors, and the chevron icon; only pass `label`, `placeholder`, and `extra_classes` when you need overrides.
- Keep widget classes in forms via `_apply_form_field_styles` (e.g., `src/common/forms/staff.py`) so future refactors stay centralized.

### Form Design Standards
**CRITICAL**: When designing or modifying forms, ALWAYS reference existing templates first:
1. **Review similar forms** in `src/templates/` to understand established UI patterns
2. **Use component templates** from `src/templates/components/` for standard elements
3. **Follow dropdown styling standards**:
   - Use `rounded-xl` borders, `border-gray-200` color
   - Apply emerald focus rings: `focus:ring-emerald-500 focus:border-emerald-500`
   - Include chevron icons positioned right
   - Maintain 48px minimum height for touch targets
   - Use smooth transitions: `transition-all duration-200`
4. **Reference templates**: Check `src/templates/communities/provincial_manage.html` and `src/templates/components/form_field_select.html` for examples
5. **Maintain visual consistency** across all forms in spacing, colors, borders, and interactive states

### List/Table Card Template
- Use `components/data_table_card.html` for directory/list pages (Barangay & Municipal OBC tables) to keep the gradient header, column layout, and View/Edit/Delete actions consistent.
- Each row expects `view_url`, `edit_url`, and `delete_preview_url`; the built-in script shows a confirm dialog, then redirects to the detail page with `?review_delete=1` so the red “Review before deletion” banner can render.
- Supply `headers` and `rows` collections from the view context; cell content can be HTML snippets to keep layouts rich (icons, stacked metadata, etc.).

## Testing Guidelines
Pytest with pytest-django drives the suite, supported by factory fixtures. Name tests `test_<behavior>` and mirror production scenarios, especially for policy logic and data imports. Keep coverage at or above 85% and add regression cases before altering critical flows. Execute `pytest --ds=obc_management.settings` for full suites; organize larger suites under `src/<app>/tests/`.

## Commit & Pull Request Guidelines
Commits use imperative, capitalized subjects without trailing periods (e.g., `Enhance MANA module workflow`) and should isolate schema, fixture, and UI edits. Pull requests must summarize intent, flag migrations or scripts, link Jira or issue IDs, and add screenshots for template changes. Always report the most recent `pytest`, `flake8`, and coverage results and request reviews from the owning module team.

## Instant UI & Smooth Interactions
Always prioritize instant UI updates and smooth user interactions. Follow these guidelines:

### HTMX Implementation Standards
- **Target Consistency**: Use `data-task-id="{{ item.id }}"` for all interactive elements (kanban cards, table rows, modals)
- **Optimistic Updates**: Update UI immediately, then handle server response. Revert on errors with clear feedback
- **Smooth Transitions**: Use `hx-swap="outerHTML swap:300ms"` or `delete swap:200ms` for animations
- **Loading States**: Always provide visual feedback during operations (spinners, disabled states)

### Response Patterns
Backend views should return HTMX-friendly responses:
```python
if request.headers.get('HX-Request'):
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                'task-updated': {'id': item_id, 'action': 'delete'},
                'show-toast': 'Operation completed successfully',
                'refresh-counters': True
            })
        }
    )
```

### Animation Requirements
- Task movements between kanban columns: 300ms smooth transitions
- Modal open/close: Fade with scale transform
- Button clicks: Micro-interactions for immediate feedback
- Error states: Red flash with recovery options

### Never Use Full Page Reloads
- Implement HTMX for all CRUD operations
- Use out-of-band swaps for updating multiple UI regions
- Provide fallback mechanisms for HTMX failures
- Ensure accessibility with proper ARIA states

Refer to `docs/improvements/instant_ui_improvements_plan.md` for detailed implementation guidance.

## Security & Configuration Tips
Copy `.env.example` to `.env`, fill `SECRET_KEY`, database, Redis, and third-party credentials, and keep secrets out of git. SQLite suffices for quick checks, but align staging with Postgres and Redis. Document integration details and follow-up notes in `docs/` so future contributors can trace decisions.

## Documentation Organization

**All documentation MUST be placed under `docs/` in appropriate subdirectories:**

```
docs/
├── deployment/      # Deployment, production setup
├── testing/        # Tests, verification reports
├── improvements/   # Feature plans, implementation tracking
├── guidelines/     # Program guides (MANA, policies)
├── reference/      # Technical specs, standards
├── development/    # Development guidelines
└── [other categories]
```

**Critical Rules:**
1. **Never create `.md` docs in project root** (except config files)
2. Choose correct category: deployment, testing, improvements, etc.
3. Update `docs/README.md` index after adding new docs
4. Use relative links within docs: `[text](../category/file.md)`

**Config files that STAY in ROOT:**
- `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` (AI configuration)
- `README.md` (project overview)
- `.env.example` (environment template)

**Reference:** See [docs/DOCUMENTATION_ORGANIZATION.md](docs/DOCUMENTATION_ORGANIZATION.md) for complete organization details.
