# GEMINI.md

Guidance for the Gemini coding agent when contributing to this repository.

## Environment & Tooling
- Use Python 3.12 virtualenv in `venv/` (`./scripts/bootstrap_venv.sh` then `source venv/bin/activate`).
- Run Django commands from `src/` (`./manage.py migrate`, `runserver`, etc.).
- Install dependencies via `pip install -r requirements/development.txt`.

## Quality Gates
- Format and lint with `black src`, `isort src`, and `flake8 src`.
- Execute `pytest --ds=obc_management.settings` before proposing changes; add focused tests for regressions.
- Report the latest test/linters when handing off work.

## UI & Templates
- Tailwind CSS powers the styling. Reuse shared components to keep parity with the Barangay OBC form.
- Standard form helpers live in `src/templates/components/`:
  - `form_field_select.html` for dropdowns (pre-styled with chevron icon and spacing)
  - `form_field_input.html` for single-line inputs
  - `form_field.html` for textareas/general inputs
- Include them like `{% include "components/form_field_select.html" with field=form.barangay placeholder="Select barangay..." %}` instead of rewriting markup.
- Widget classes are centralized in helpers such as `_apply_form_field_styles` (see `src/common/forms/staff.py`). Extend there when introducing new patterns.
- For list/directory screens, use `components/data_table_card.html` to match the Barangay & Municipal OBC tables. Provide `headers` and `rows` (with `view_url`, `edit_url`, `delete_preview_url`) so the built-in View/Edit/Delete actions and two-step deletion flow (“Review before deletion”) work automatically.

## Architecture Notes
- Core apps: `common`, `communities`, `mana`, `coordination`, `recommendations`.
- Shared assets belong in `src/common` (models, services), `src/templates/` (HTML), `src/static/` (JS/CSS).
- Maintain timezone-aware datetimes (`USE_TZ = True`) and follow the existing test organization in `src/<app>/tests/`.

Keep PRs scoped, favour descriptive commit messages, and document migrations or scripts in their summaries.
