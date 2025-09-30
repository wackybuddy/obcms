# Migrating OBCMS to PostgreSQL

## Overview

This guide walks through moving the OOBC Management System (OBCMS) from the default SQLite database to PostgreSQL for both local development and deployed environments. Follow these steps when you need stronger concurrency guarantees, better JSON support, or to match production infrastructure.



PostgreSQL Migration Guide Updated!

  Key Improvements Made:

  Docker Integration:
  - Added quick TL;DR migration steps for Docker users
  - Updated all commands to include docker compose exec variants
  - Referenced our ./docker-start.sh script throughout

  Accurate Configuration:
  - Fixed settings examples to use django-environ (not decouple)
  - Updated environment variable structure to match our .env.example
  - Clarified that psycopg2-binary is already in requirements

  Enhanced Data Migration:
  - Added comprehensive SQLite → PostgreSQL data migration steps
  - Included Docker-specific export/import procedures
  - Added troubleshooting for common migration issues

  Validation & Testing:
  - Docker-specific validation commands
  - Updated database inspection methods
  - Added validation checklist

  Updated Migration Workflow:

  For existing SQLite users:
  1. Backup SQLite data
  2. Export with dumpdata
  3. Switch to .env (PostgreSQL configured)
  4. Run ./docker-start.sh
  5. Import with loaddata

  For fresh installations:
  - Just run ./docker-start.sh - PostgreSQL ready immediately

  The guide now perfectly matches our dockerized setup and provides clear
  paths for all scenarios.




## Quick Migration (Docker)

**TL;DR**: If you're using our Docker setup and want to migrate existing SQLite data:

```bash
# 1. Backup current SQLite data
cp src/db.sqlite3 src/db.sqlite3.backup

# 2. Export existing data (while using SQLite)
source venv/bin/activate
cd src
./manage.py dumpdata --natural-primary --natural-foreign --exclude contenttypes --exclude auth.Permission --exclude sessions --indent 2 > ../data/sqlite_export.json

# 3. Switch to PostgreSQL (Docker automatically configured)
cp .env.example .env

# 4. Start Docker with PostgreSQL
./docker-start.sh

# 5. Import your data
docker compose exec web python src/manage.py loaddata ../data/sqlite_export.json

# 6. Create admin user
docker compose exec web python src/manage.py createsuperuser

# 7. Verify at http://localhost:8000/admin/
```

**Fresh installation?** Just run `./docker-start.sh` - PostgreSQL is configured by default.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Choose a PostgreSQL Instance](#choose-a-postgresql-instance)
3. [Install Client Tooling](#install-client-tooling)
4. [Update Python Dependencies](#update-python-dependencies)
5. [Configure Environment Variables](#configure-environment-variables)
6. [Verify Django Database Settings](#verify-django-database-settings)
7. [Run Schema Migrations](#run-schema-migrations)
8. [Migrate Existing Data](#migrate-existing-data)
9. [Validate the Migration](#validate-the-migration)
10. [Production Cutover Checklist](#production-cutover-checklist)
11. [Troubleshooting Tips](#troubleshooting-tips)

## Prerequisites

### For Docker Migration (Recommended)

- Docker Desktop installed and running
- Access to the repository root (`obcms/`)
- Optional: backup of the existing SQLite database (`src/db.sqlite3`)

### For Local Development Migration

- Working Python 3.12 virtual environment (`./scripts/bootstrap_venv.sh && source venv/bin/activate`)
- Access to the repository root (`obcms/`)
- Ability to install PostgreSQL locally (Homebrew, apt, etc.)
- Optional: backup of the existing SQLite database (`src/db.sqlite3`)

**Recommendation**: Use the Docker approach for consistent, isolated development environment that matches production.

## Choose a PostgreSQL Instance

PostgreSQL can run locally, inside Docker, or as a managed cloud service. Pick one option per environment.

### Local development

- **Docker Compose (Recommended)**
  ```bash
  # Uses our integrated docker-compose setup
  ./docker-start.sh
  # PostgreSQL automatically configured with Redis, Celery, and Django
  ```

- **Homebrew (macOS)**
  ```bash
  brew install postgresql@16
  brew services start postgresql@16
  createdb obcms
  createuser obcms --pwprompt
  ```

- **Standalone Docker container**
  ```bash
  docker run \
    --name obcms-postgres \
    -e POSTGRES_DB=obcms \
    -e POSTGRES_USER=obcms \
    -e POSTGRES_PASSWORD=obcms_dev_password \
    -p 5432:5432 \
    -d postgres:15-alpine
  ```

### Managed service (staging/production)

Provision a managed PostgreSQL instance (Render, Railway, Fly.io, AWS RDS, etc.). Record the hostname, port, database name, user, and password. Ensure outbound connections from your app host can reach the database and that SSL is enabled if required by the provider.

## Install Client Tooling

Install `psql` so you can connect to the database for sanity checks.

```bash
# macOS (Homebrew)
brew install libpq
brew link --force libpq

# Debian/Ubuntu
sudo apt update && sudo apt install postgresql-client
```

Verify access:

```bash
psql "postgresql://obcms:change-me@127.0.0.1:5432/obcms"
```

## Update Python Dependencies

PostgreSQL requires a database driver. OBCMS already includes `psycopg2-binary` in its requirements.

### For Docker Users

Dependencies are automatically installed in the Docker image - no action needed.

### For Local Development

If you're not using Docker, ensure you have the PostgreSQL driver:

```bash
# Dependencies already included in requirements/base.txt:
# psycopg2-binary>=2.9

# Reinstall to ensure you have the driver
source venv/bin/activate
pip install -r requirements/development.txt
```

**Note**: `psycopg2-binary` is already included in:
- `requirements/base.txt` (for all environments)
- `deployment/requirements/production.txt` (for production deployment)

For production images or CI, the existing `psycopg2-binary>=2.9.5` provides the PostgreSQL driver.

## Configure Environment Variables

OBCMS uses `django-environ` for configuration. Copy `.env.example` to `.env` and configure your database settings.

### For Docker Development (Recommended)

```bash
# Copy the template
cp .env.example .env

# Edit .env - PostgreSQL is pre-configured for Docker
DATABASE_URL=postgres://obcms:obcms_dev_password@db:5432/obcms
```

### For Local PostgreSQL

```bash
# In .env file
DATABASE_URL=postgres://obcms:your_password@localhost:5432/obcms

# Or use individual variables (if needed)
POSTGRES_DB=obcms
POSTGRES_USER=obcms
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### For Production

```bash
# In production .env
DATABASE_URL=postgres://user:password@your_host:5432/production_db
POSTGRES_DB=production_db
POSTGRES_USER=production_user
POSTGRES_PASSWORD=secure_production_password
```

Apply the same values to your hosting provider's dashboard or secret manager for deployed environments.

## Verify Django Database Settings

Open `src/obc_management/settings.py` and confirm the configuration uses `django-environ`. The current setup should look like this:

```python
import environ

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)

# Database configuration using django-environ
DATABASES = {
    'default': env.db(default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
}
```

The `env.db()` method automatically:
- Parses `DATABASE_URL` environment variable
- Sets the correct PostgreSQL backend (`django.db.backends.postgresql`)
- Configures connection parameters (host, port, user, password, database name)

When `DATABASE_URL` is set to a PostgreSQL URL, Django will automatically use PostgreSQL. When not set, it falls back to SQLite. Update any custom database routers or raw SQL queries that assume SQLite-specific behavior.

## Run Schema Migrations

Once the environment variables point to PostgreSQL, create the schema.

### Using Docker (Recommended)

```bash
# Start PostgreSQL and all services
./docker-start.sh

# Migrations run automatically, but you can run them manually:
docker compose exec web python src/manage.py migrate
```

### Using Local Development

```bash
source venv/bin/activate
cd src
./manage.py migrate
```

Django will recreate all tables and apply historical migrations. If migrations reference SQLite-only SQL, retrofit them before continuing.

## Migrate Existing Data

If you have useful data in SQLite (`src/db.sqlite3`), migrate it to PostgreSQL using Django's data export/import tools.

### Method 1: Docker Migration (Recommended)

1. **Backup your current SQLite data**:
   ```bash
   cp src/db.sqlite3 src/db.sqlite3.backup
   ```

2. **Export data from SQLite** (while still using SQLite):
   ```bash
   # Ensure you're using SQLite first (no .env file or comment out DATABASE_URL)
   source venv/bin/activate
   cd src
   ./manage.py dumpdata \
     --natural-primary \
     --natural-foreign \
     --exclude contenttypes \
     --exclude auth.Permission \
     --exclude sessions \
     --indent 2 > ../data/sqlite_export.json

   # Create data directory if it doesn't exist
   mkdir -p ../data
   ```

3. **Switch to PostgreSQL configuration**:
   ```bash
   # Create/update .env with PostgreSQL settings
   cp .env.example .env
   # DATABASE_URL is already set to PostgreSQL in .env
   ```

4. **Start Docker services and migrate**:
   ```bash
   ./docker-start.sh

   # Import data into PostgreSQL
   docker compose exec web python src/manage.py loaddata ../data/sqlite_export.json
   ```

5. **Create superuser account**:
   ```bash
   docker compose exec web python src/manage.py createsuperuser
   ```

### Method 2: Local PostgreSQL Migration

1. **Export from SQLite** (with no DATABASE_URL set):
   ```bash
   source venv/bin/activate
   cd src
   ./manage.py dumpdata --natural-primary --natural-foreign --exclude contenttypes --exclude auth.Permission > ../data/sqlite_export.json
   ```

2. **Switch to PostgreSQL** and load data:
   ```bash
   # Set DATABASE_URL to your PostgreSQL instance
   export DATABASE_URL="postgres://obcms:password@localhost:5432/obcms"
   cd src
   ./manage.py migrate
   ./manage.py loaddata ../data/sqlite_export.json
   ```

### Data Migration Notes

- **Large datasets**: Consider specialized tools (pgloader, AWS DMS) or CSV export per table
- **User passwords**: Exported passwords remain hashed and will work in PostgreSQL
- **File uploads**: Media files in `src/media/` are preserved across database changes
- **Custom data**: Complex data types may need manual migration or custom management commands

### Troubleshooting Data Migration

- **Foreign key errors**: Ensure all related models are included in export
- **Permission errors**: Exclude `contenttypes` and `auth.Permission` as shown above
- **Large datasets**: Use `--chunk-size=1000` for loaddata if you encounter memory issues
- **Encoding issues**: SQLite to PostgreSQL encoding differences are handled automatically by Django

## Validate the Migration

### Using Docker (Recommended)

- **Test the web application**:
  ```bash
  # Application should be running at http://localhost:8000
  curl -I http://localhost:8000

  # Check admin interface
  open http://localhost:8000/admin/
  ```

- **Run the test suite**:
  ```bash
  docker compose exec web pytest src/
  ```

- **Inspect the database**:
  ```bash
  # Connect to PostgreSQL directly
  docker compose exec db psql -U obcms -d obcms -c "\dt"

  # Or check from Django
  docker compose exec web python src/manage.py dbshell
  ```

- **Check services status**:
  ```bash
  docker compose ps
  docker compose logs web
  ```

### Using Local Development

- **Run the test suite**:
  ```bash
  source venv/bin/activate
  cd src
  pytest --ds=obc_management.settings
  ```

- **Start the development server**:
  ```bash
  cd src
  ./manage.py runserver
  ```

- **Inspect the database**:
  ```bash
  psql $DATABASE_URL -c "\dt"
  ```

### Validation Checklist

- [ ] Django admin interface loads without errors
- [ ] User authentication works (login/logout)
- [ ] All models visible in admin interface
- [ ] Data from SQLite appears correctly
- [ ] Celery tasks can be queued (if using background tasks)
- [ ] Static files serve correctly
- [ ] No database-specific errors in logs

## Production Cutover Checklist

- Provision managed PostgreSQL with backups enabled and document retention policies.
- Update infrastructure as code or deployment manifests with the new connection string.
- Rotate Django `SECRET_KEY` and any credentials stored alongside the database URL.
- Schedule a maintenance window, put the site in read-only mode (if needed), and repeat the dump/load flow.
- Rebuild Docker images or redeploy the service so the new environment variables take effect.
- Monitor logs and metrics (connection counts, slow queries) after cutover.

## Troubleshooting Tips

- **`psycopg2.OperationalError: could not connect`** – check host/port firewall rules and whether PostgreSQL is listening on all interfaces (`listen_addresses` in `postgresql.conf`).
- **`FATAL: password authentication failed`** – verify credentials and that the role has privileges on the target database (`GRANT ALL ON DATABASE obcms TO obcms;`).
- **Migration errors referencing SQLite syntax** – update affected migrations with `RunPython` guards or conditional SQL per backend.
- **`django.db.utils.ProgrammingError` during `loaddata`** – ensure all migrations ran before loading data and that fixtures do not reference deleted models.
- **Performance issues** – add indexes via migrations, enable `CONN_MAX_AGE` in Django settings for connection pooling, and consider `pg_stat_statements` for tuning.

Document any environment-specific deviations in `docs/` so future deploys follow the same pattern.
