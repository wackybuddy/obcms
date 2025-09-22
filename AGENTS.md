# Repository Guidelines

## Project Structure & Module Organization
The Django project lives in `src`; `obc_management` owns settings/URLs while feature apps (`communities`, `coordination`, `mana`, `policies`, `documents`, `policy_tracking`, `ai_assistant`) deliver domain logic. Shared utilities stay in `src/common`, import flows in `src/data_imports`, and templates in `src/templates`. Reference docs sit in `docs/`, deployment manifests in `deployment/`, and product briefs in `tasks/`. Keep new code inside the relevant app, park serializers beside their views, and add tests to `src/<app>/tests.py` (break out a `tests/` package when the file grows).

## Build, Test, and Development Commands
- `./scripts/bootstrap_venv.sh && source venv/bin/activate` — create/refresh the Python 3.12 virtualenv.
- `pip install -r requirements/development.txt` — install Django, DRF, pytest, and tooling.
- `cd src && ./manage.py migrate` — apply database schema updates.
- `cd src && ./manage.py runserver` — start the local server on `http://localhost:8000`.
- `black src && isort src && flake8 src` — format code, sort imports, then lint.
- `pytest [-k name]` — run the pytest-django suite with optional filtering.
- `coverage run -m pytest && coverage report` — confirm coverage before merging.

## Coding Style & Naming Conventions
Adopt Black defaults (88-char lines, double quotes) and four-space indentation. Files and modules use `snake_case`; Django models, services, and forms use `PascalCase`. Keep management commands under `<app>/management/commands/`, choose descriptive template blocks such as `{% block community_summary %}`, and centralise shared enums or constants inside `common`. Enable local `pre-commit` hooks when available.

## Testing Guidelines
Leverage pytest and pytest-django fixtures; mirror production scenarios with factory helpers per app. Name tests `test_<behavior>` and prefer `tests/test_<module>.py` when splitting the default `tests.py`. Cover serializers, services, admin actions, and migrations; run `pytest --ds=obc_management.settings` if settings resolution is required. Maintain coverage ≥85% and add regression tests before altering policy logic or data ingestion.

## Commit & Pull Request Guidelines
Follow the existing history: imperative, capitalised subject, no trailing period (e.g., `Enhance MANA module workflow`). Keep commits focused, separating schema, fixture, and UI work. Pull requests must summarize intent, enumerate migrations or scripts, link Jira/issue IDs, and attach screenshots for template changes. State results for `pytest`, `flake8`, and coverage, and request reviews from the relevant module owners.

## Environment & Configuration Tips
Copy `.env.example` to `.env`, populate `SECRET_KEY`, database URLs, Redis endpoints, and third-party tokens, and never commit the filled file. SQLite is acceptable for quick local work, but configure Postgres/Redis for staging and reflect updates in `deployment/`. Document integration specifics alongside the existing admin and UI guides in `docs/`.
