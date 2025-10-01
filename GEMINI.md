# Gemini Contributor Guidelines

Guidance for the Gemini coding agent when contributing to this repository.

## Environment & Tooling
- **Virtual Environment**: Use the Python 3.12 virtualenv located in `venv/`. To set it up, run `./scripts/bootstrap_venv.sh` and then activate it with `source venv/bin/activate`.
- **Dependencies**: Install all necessary development dependencies using `pip install -r requirements/development.txt`.
- **Local Development**: Run all Django `manage.py` commands from the `src/` directory. Use `./manage.py migrate` to apply database migrations and `./manage.py runserver` to start the local development server.

### ⚠️ CRITICAL: Database Protection Policy ⚠️
**NEVER delete `src/db.sqlite3` or any database file under ANY circumstances.** The database contains essential development data, user accounts, test data, and ongoing work that are critical for development continuity. Always apply migrations to the existing database using `./manage.py migrate`.

**If you encounter migration conflicts or errors:**
1. **DO NOT delete the database** - this is absolutely forbidden
2. Resolve conflicts using Django migration tools: `--fake`, `--fake-initial`, or `squashmigrations`
3. Always ask the user before taking any action that could affect the database
4. Remember: Deleting the database destroys all development progress and is completely unacceptable

## Quality, Linting, and Testing
- **Formatting**: Adhere to Black's defaults (88-character line width) and four-space indentation. Run `black src` and `isort src` to format the code.
- **Linting**: Check for style issues with `flake8 src`.
- **Testing**: Execute the test suite with `pytest --ds=obc_management.settings`. For focused tests, use the `-k <pattern>` flag. Before submitting changes, ensure all tests pass and add new tests for any new functionality or bug fixes to prevent regressions.
- **Pre-commit**: Run `pre-commit run --all-files` if hooks are enabled.

## UI & Templates
- **Styling**: Tailwind CSS is used for styling. Reuse existing components to maintain visual consistency.
- **Form Components**: Use the standard form helpers located in `src/templates/components/`:
  - `form_field_select.html`: For dropdowns.
  - `form_field_input.html`: For single-line text inputs.
  - `form_field.html`: For general-purpose inputs like textareas.
  - **Usage**: Include them with `{% include "components/form_field_select.html" with field=form.barangay placeholder="Select barangay..." %}`. This handles labels, errors, and styling automatically.
- **List Pages**: For list or directory screens, use `components/data_table_card.html`. Provide `headers` and `rows` in the context. Each row object should include `view_url`, `edit_url`, and `delete_preview_url` to enable the standard View, Edit, and Delete actions.

### Form Design Standards (MANDATORY)
**When designing or modifying forms, ALWAYS reference existing templates to ensure UI/UX consistency:**

1. **Review existing forms** in `src/templates/` before creating new form markup
2. **Use component templates** from `src/templates/components/` whenever possible
3. **Follow the standard dropdown pattern**:
   - Rounded corners: `rounded-xl`
   - Border style: `border border-gray-200`
   - Focus states: `focus:ring-emerald-500 focus:border-emerald-500`
   - Minimum height: `min-h-[48px]` for accessibility
   - Chevron icon: Right-aligned with `fas fa-chevron-down`
   - Smooth transitions: `transition-all duration-200`

4. **Standard dropdown HTML structure**:
   ```html
   <div class="space-y-1">
       <label for="field-id" class="block text-sm font-medium text-gray-700 mb-2">
           Field Label<span class="text-red-500">*</span>
       </label>
       <div class="relative">
           <select id="field-id" name="field_name"
                   class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200">
               <option value="">Select...</option>
           </select>
           <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
               <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
           </span>
       </div>
   </div>
   ```

5. **Reference templates for consistency**:
   - Check `src/templates/communities/provincial_manage.html` for filter dropdowns
   - Check `src/templates/components/form_field_select.html` for reusable component
   - Check `src/templates/mana/mana_new_assessment.html` for complex form layouts

6. **Maintain consistency** across all forms in:
   - Spacing and padding
   - Color palette (grays, emerald accents)
   - Border styles and radii
   - Interactive states (hover, focus, disabled)
   - Typography hierarchy

## Architecture & Code Organization
- **Core Application**: The main Django project is in `src/`. `obc_management` contains the primary settings and URL configurations.
- **Feature Apps**: Domain-specific logic is organized into apps such as `communities`, `coordination`, `mana`, and `recommendations`.
- **Shared Resources**:
  - `src/common`: For shared models, services, and utilities.
  - `src/templates/`: For shared HTML templates.
  - `src/static/`: For global JS, CSS, and other static assets.
- **Timezones**: Always use timezone-aware datetimes (`USE_TZ = True`).
- **Tests**: Organize tests within `src/<app>/tests/`.

## Commits & Pull Requests
- **Commit Messages**: Write clear, imperative-style commit messages (e.g., "Add user authentication endpoint").
- **Pull Requests**: Keep PRs scoped to a single feature or fix. Provide a summary of the changes, and link any relevant issue trackers. Report the latest test and linting results.

## Security
- **Configuration**: Copy `.env.example` to `.env` for local development and populate it with the required secrets.
- **Secrets**: Never commit secrets or sensitive credentials to the repository.

## Instant UI & Smooth Interactions

### Imperative: Prioritize Instant UI Updates
When contributing to this codebase, **always implement instant UI responses** and smooth user interactions. Modern users expect immediate feedback and seamless experiences without page reloads.

### HTMX Implementation Standards
- **Data Attribute Consistency**: Use `data-task-id="{{ item.id }}"` for all interactive elements (kanban cards, table rows, modal forms)
- **Optimistic UI**: Update the interface immediately upon user action, then handle server response for confirmation or rollback
- **Smooth Transitions**: Implement `hx-swap="outerHTML swap:300ms"` or `delete swap:200ms` for animated state changes
- **Loading Feedback**: Always provide visual indicators (spinners, disabled states) during async operations

### Backend HTMX Response Pattern
Structure your Django views to return HTMX-compatible responses:
```python
def update_task_view(request, task_id):
    # ... perform the operation ...

    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'task-updated': {'id': task_id, 'action': 'update'},
                    'show-toast': 'Task updated successfully',
                    'refresh-counters': True
                })
            }
        )
```

### Animation & Transition Requirements
- **Kanban Task Movements**: 300ms smooth transitions between columns
- **Modal Operations**: Fade with scale transforms for opening/closing
- **Interactive Elements**: Immediate visual feedback on button clicks and form interactions
- **Error States**: Clear visual indicators with recovery paths, never silent failures

### Eliminate Full Page Reloads
- Use HTMX for all CRUD (Create, Read, Update, Delete) operations
- Implement out-of-band swaps (`hx-swap-oob`) for updating multiple UI regions
- Provide fallback behavior for HTMX request failures
- Ensure accessibility compliance with proper ARIA live regions

### Critical Bug to Address
**Current Issue**: Task deletion in the kanban board (`/oobc-management/staff/tasks/`) doesn't instantly remove task cards. The delete form targets `[data-task-row]` but the kanban view uses `[data-task-id]`. This targeting mismatch prevents instant UI updates.

For comprehensive implementation details, consult `docs/improvements/instant_ui_improvements_plan.md`.

## Documentation Guidelines

### Where to Write Documentation

**IMPORTANT: All documentation MUST be placed under the `docs/` directory in the appropriate category.**

#### Documentation Organization
```
docs/
├── deployment/      # Deployment, production setup
├── development/     # Development guidelines
├── testing/        # Testing, verification
├── reference/      # Technical specs, standards
├── improvements/   # Feature plans, implementation tracking
├── guidelines/     # Program guidelines
├── product/       # Roadmap, architecture
├── reports/       # Research, analysis
└── [other categories]
```

#### Key Rules

1. **Never create docs in root** - Use `docs/[category]/filename.md`
2. **Update docs/README.md** - Add new docs to the index
3. **Use relative links** - `[text](../category/file.md)` within docs
4. **Follow naming** - lowercase with underscores

#### Config vs Documentation

**Config files (in ROOT):**
- `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` (AI config)
- `README.md` (project overview)
- `.env.example` (environment template)

**Documentation (in docs/):**
- Implementation plans → `docs/improvements/`
- Deployment guides → `docs/deployment/`
- Testing docs → `docs/testing/`
- User guides → `docs/guidelines/`

**Reference:** [docs/DOCUMENTATION_ORGANIZATION.md](docs/DOCUMENTATION_ORGANIZATION.md)