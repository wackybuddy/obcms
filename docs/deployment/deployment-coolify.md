# Coolify Deployment Plan

This document outlines how to deploy the OBC Management System to a Coolify-managed environment without introducing a custom Dockerfile. It assumes you already have a Coolify instance (self-hosted or managed) connected to the git repository that contains this project.

## Goals
- Deliver a repeatable deployment workflow for staging and production.
- Use Coolify's managed services (build packs, Postgres, Redis, storage) instead of bespoke infrastructure.
- Keep Django-specific operations (`migrate`, `collectstatic`, superuser creation) scripted and observable.

## Prerequisites
- Coolify v4+ with access to the "Applications" and "Services" modules.
- Git repository access token with read permissions to the branch you will deploy.
- Domain name ready (optional during staging, required for production) with control over DNS.
- SMTP account for transactional email and an S3-compatible bucket (or other object storage) if you do not want to serve media from the app container.
- Secrets for Django (`SECRET_KEY`, service credentials) stored in a password manager ready to be copied into Coolify.

## Target Architecture on Coolify
- **PostgreSQL Service**: Managed database created through Coolify, version 14 or higher. Enable daily backups in Coolify and record the connection URL.
- **Redis Service**: Managed Redis (v6+) for Celery and caching. Configure password authentication.
- **Application Service (Buildpack)**: Coolify Python buildpack using Paketo. Command entrypoint runs `gunicorn obc_management.wsgi:application` behind Coolify's Traefik reverse proxy.
- **Volume Mounts**:
  - `/workspace/staticfiles` (ephemeral) – populated during deploy via `collectstatic`.
  - `/workspace/media` (persistent) – optional if you prefer S3. Use a Coolify volume attached to the app container.
- **Ancillary Jobs**: Optional Coolify "Job" resources for scheduled tasks (e.g., nightly Celery beat). Alternatively, run `celery -A obc_management.celery_app worker` in a dedicated worker application if background jobs are required in production.

## Implementation Steps

### 1. Prepare the Repository
1. Enable WhiteNoise or object storage for static files (static assets are collected to `STATIC_ROOT = src/staticfiles`).
2. Confirm `.env.example` contains all required production settings: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `REDIS_URL`, `EMAIL_*`, `CELERY_BROKER_URL`, etc.
3. Add a `Procfile`-style start command to project docs (Coolify buildpack expects a valid launch command; we'll pass it via the UI).
4. Commit any migrations and run tests locally before the first deployment.

### 2. Provision Data Services in Coolify
1. In Coolify, create a **PostgreSQL** service. Record the auto-generated `POSTGRES_USER`, `POSTGRES_PASSWORD`, and internal hostname. Enable backups and set retention to match organizational policy.
2. Create a **Redis** service. Configure a strong password and note the internal URL (`redis://:<password>@<host>:6379/0`).
3. (Optional) Provision an **Object Storage** service (MinIO/S3) through Coolify or another provider if you plan to store user-uploaded media outside the application container.

### 3. Create the Django Application Service
1. Add a new **Application** in Coolify and select **Source: Git Repository**. Connect the repository and choose the branch/tag to deploy.
2. Choose **Buildpack** as the deployment method. Set build environment variables:
   - `BP_PYTHON_VERSION=3.12.x`
   - `BP_NODE_VERSION` only if compiling frontend assets.
3. Under **Environment Variables**, add:
   - `SECRET_KEY=<production secret>`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=<domain,comma,separated>`
   - `DATABASE_URL=postgres://<user>:<password>@<postgres-service>:5432/<db>`
   - `REDIS_URL=redis://:<password>@<redis-service>:6379/0`
   - `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` pointing to Redis.
   - Email/S3 credentials, `DJANGO_SETTINGS_MODULE=obc_management.settings`, and any third-party API keys.
4. Configure **Advanced**:
   - Build command: leave blank (Coolify buildpack handles dependency install).
   - Start command: `web: gunicorn obc_management.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120`
   - Pre-deploy command: `./manage.py migrate && ./manage.py collectstatic --noinput`
5. Attach volumes under **Persistent Storage** if you keep media locally (`/workspace/media`). Static files can remain ephemeral since they are rebuilt every deploy.
6. Trigger the initial deployment. Monitor build logs for dependency installation, migrations, and static asset compilation.

### 4. Post-Deployment Tasks
1. Run `./manage.py createsuperuser` from the Coolify console (one-off command) to seed the first admin user.
2. Configure Celery workers:
   - Option A: Create a second Coolify **Application** using the same repository and buildpack, but set the start command to `worker: celery -A obc_management.celery_app worker --loglevel=info`.
   - Option B: Add a **Job** that runs `celery -A obc_management.celery_app beat` for scheduled tasks.
3. Add a domain under the application settings and create DNS `A`/`CNAME` records pointing to Coolify's proxy.
4. Enable HTTPS with Let's Encrypt from within Coolify once DNS propagates.
5. Smoke test critical flows (login, CRUD operations, API endpoints) before promoting to production.

## Environment Variable Reference
| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django cryptographic secret |
| `DEBUG` | Must be `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hostnames served by Django |
| `DATABASE_URL` | Postgres connection URL from Coolify service |
| `REDIS_URL` | Redis connection for caching and Celery |
| `CELERY_BROKER_URL` | Usually same as `REDIS_URL` |
| `CELERY_RESULT_BACKEND` | Redis URL or other backend |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_PORT` | Outbound email |
| `DEFAULT_FROM_EMAIL` | Email sender address |
| `SITE_NAME`, `SITE_DESCRIPTION` | Branding overrides |
| `DJANGO_SETTINGS_MODULE` | Should remain `obc_management.settings` |
| `GOOGLE_APPLICATION_CREDENTIALS`, etc. | Any AI integrations already used in development |

## Operations Checklist
- **Backup Testing**: Validate Coolify-managed Postgres backups monthly. Export Redis snapshots if Celery needs persistence.
- **Migrations**: Always run migrations through the pre-deploy command or manually via the Coolify console before releasing.
- **Static Assets**: If you switch to S3, set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_STORAGE_BUCKET_NAME`, and update storage backend settings.
- **Monitoring**: Enable Coolify's built-in metrics. Optionally ship logs to an external service (Grafana/Loki) through Coolify's log shipping settings.
- **Scaling**: Increase container size or replicas directly from Coolify. Add a load balancer rule if deploying multiple replicas.
- **Disaster Recovery**: Document how to redeploy from scratch using this plan, including secret retrieval and DNS updates.

## Next Steps and Enhancements
- Automate staging deployments using Coolify's auto-deploy on push with protected branches.
- Add status checks (`./manage.py check --deploy`) to the pre-deploy command for additional safety.
- Incorporate integration tests or smoke tests into Coolify's post-deploy hooks.
- Evaluate using Coolify's object storage adapter once media upload volume scales beyond what a single volume can handle.
