# Gemini Contributor Guidelines

Guidance for the Gemini coding agent when contributing to this repository.

## Environment & Tooling
- **Virtual Environment**: Use the Python 3.12 virtualenv located in `venv/`. To set it up, run `./scripts/bootstrap_venv.sh` and then activate it with `source venv/bin/activate`.
- **Dependencies**: Install all necessary development dependencies using `pip install -r requirements/development.txt`.
- **Local Development**: Run all Django `manage.py` commands from the `src/` directory. Use `./manage.py migrate` to apply database migrations and `./manage.py runserver` to start the local development server.

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