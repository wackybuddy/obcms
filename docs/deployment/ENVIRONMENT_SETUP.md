# OBCMS Environment Configuration Guide

**Purpose:** Complete guide to environment variable configuration
**Audience:** DevOps Engineers, System Administrators
**Environments:** Development, Staging, Production

---

## Table of Contents

1. [Environment Overview](#environment-overview)
2. [Required Variables](#required-variables)
3. [Django Core Configuration](#django-core-configuration)
4. [Database Configuration](#database-configuration)
5. [Redis & Celery Configuration](#redis--celery-configuration)
6. [Email Configuration](#email-configuration)
7. [Security Configuration](#security-configuration)
8. [Application Configuration](#application-configuration)
9. [Environment-Specific Settings](#environment-specific-settings)
10. [Configuration Validation](#configuration-validation)

---

## Environment Overview

### Configuration Files

OBCMS uses different environment configurations:

| Environment | File | Django Settings | DEBUG |
|-------------|------|----------------|-------|
| **Development** | `.env` (local) | `development` or `base` | `1` (True) |
| **Staging** | `.env.staging` | `production` | `0` (False) |
| **Production** | `.env.production` | `production` | `0` (False) |

### Configuration Priority

Django loads configuration in this order:
1. Environment variables (highest priority)
2. `.env` file
3. Settings file defaults (lowest priority)

**Best Practice:** Use `.env` files for environment-specific values

---

## Required Variables

### Critical Variables (MUST be set)

These variables are **required** for the application to run:

```bash
# Django Core
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=[50+ character random string]
DEBUG=0
ALLOWED_HOSTS=staging.obcms.gov.ph,www.staging.obcms.gov.ph
CSRF_TRUSTED_ORIGINS=https://staging.obcms.gov.ph,https://www.staging.obcms.gov.ph

# Database
DATABASE_URL=postgres://obcms_user:password@db:5432/obcms_staging

# Cache
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
```

**Validation:**
```bash
# Check all required variables are set
./scripts/validate-env.sh
```

---

## Django Core Configuration

### DJANGO_SETTINGS_MODULE

**Purpose:** Selects which Django settings file to use

**Values:**
- `obc_management.settings.development` - Development (local)
- `obc_management.settings.production` - Staging and Production

**Example:**
```bash
# Production/Staging
DJANGO_SETTINGS_MODULE=obc_management.settings.production

# Development (optional, defaults to base settings)
DJANGO_SETTINGS_MODULE=obc_management.settings.development
```

---

### SECRET_KEY

**Purpose:** Cryptographic signing key for sessions, CSRF, etc.

**Requirements:**
- 50+ characters minimum
- Cryptographically random
- Different for each environment
- NEVER commit to version control

**Generation:**
```bash
# Generate new SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Example output:
# django-insecure-8a@w$5fk2m9x!p7h3q&n*t1v6z#c4j8l0r2u9y5e3w7k6
```

**Example:**
```bash
SECRET_KEY=8a@w$5fk2m9x!p7h3q&n*t1v6z#c4j8l0r2u9y5e3w7k6b9d1f4g7j
```

**Security:**
- ❌ NEVER use: `django-insecure-*` (development key)
- ❌ NEVER use: Example keys from documentation
- ✅ ALWAYS use: Unique randomly generated key per environment

---

### DEBUG

**Purpose:** Enables/disables debug mode

**Values:**
- `0` (False) - Production/Staging (REQUIRED)
- `1` (True) - Development only

**Example:**
```bash
# Production/Staging - MUST be 0
DEBUG=0

# Development (optional)
DEBUG=1
```

**Security Warning:**
- **NEVER** set `DEBUG=1` in production or staging
- Debug mode exposes sensitive information (settings, SQL queries, file paths)
- Production settings enforce `DEBUG=False` (cannot be overridden)

---

### ALLOWED_HOSTS

**Purpose:** List of hosts allowed to serve the application (security protection)

**Format:** Comma-separated list of domains (no spaces, no https://)

**Example:**
```bash
# Single domain
ALLOWED_HOSTS=staging.obcms.gov.ph

# Multiple domains (include www subdomain)
ALLOWED_HOSTS=staging.obcms.gov.ph,www.staging.obcms.gov.ph

# Development (localhost)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

**Validation:**
Django will raise `SuspiciousOperation` if request host not in ALLOWED_HOSTS

**Common mistakes:**
- ❌ Including `https://` (wrong: `https://staging.obcms.gov.ph`)
- ❌ Including trailing slash (wrong: `staging.obcms.gov.ph/`)
- ✅ Just the domain (correct: `staging.obcms.gov.ph`)

---

### CSRF_TRUSTED_ORIGINS

**Purpose:** List of origins allowed to make CSRF-protected requests

**Format:** Comma-separated URLs with scheme (https:// REQUIRED)

**Example:**
```bash
# MUST include https:// scheme
CSRF_TRUSTED_ORIGINS=https://staging.obcms.gov.ph,https://www.staging.obcms.gov.ph

# Development with HTTP
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

**CRITICAL:**
- **MUST** include `https://` or `http://` scheme
- Without this, ALL form submissions will fail with 403 CSRF error
- Production settings validate format and raise error if scheme missing

**Common mistakes:**
- ❌ Missing scheme (wrong: `CSRF_TRUSTED_ORIGINS=staging.obcms.gov.ph`)
- ❌ Trailing slash (wrong: `https://staging.obcms.gov.ph/`)
- ✅ With scheme, no slash (correct: `https://staging.obcms.gov.ph`)

---

### CORS_ALLOWED_ORIGINS

**Purpose:** Cross-Origin Resource Sharing (CORS) allowed origins

**When needed:**
- API consumed by frontend on different domain
- Mobile app accessing API
- Subdomain architecture (api.obcms.gov.ph)

**Format:** Comma-separated URLs with scheme

**Example:**
```bash
# Allow API access from specific domains
CORS_ALLOWED_ORIGINS=https://app.obcms.gov.ph,https://mobile.obcms.gov.ph

# Single domain
CORS_ALLOWED_ORIGINS=https://staging.obcms.gov.ph
```

**Default:** Empty (no cross-origin requests allowed) - secure default

**Security:**
- **NEVER** set `CORS_ALLOW_ALL_ORIGINS=True` in production
- Only list trusted domains

---

## Database Configuration

### DATABASE_URL

**Purpose:** PostgreSQL connection string

**Format:** `postgres://USER:PASSWORD@HOST:PORT/DATABASE`

**Example:**
```bash
# Docker deployment (internal network)
DATABASE_URL=postgres://obcms_user:strong-password-here@db:5432/obcms_staging

# External PostgreSQL server
DATABASE_URL=postgres://obcms_user:password@postgres.example.com:5432/obcms_prod

# With SSL (recommended for external connections)
DATABASE_URL=postgres://obcms_user:password@postgres.example.com:5432/obcms_prod?sslmode=require
```

**Components:**
- `USER`: Database user (NOT `postgres` superuser)
- `PASSWORD`: Strong password (20+ characters recommended)
- `HOST`: Database server hostname (`db` for Docker, IP/domain for external)
- `PORT`: PostgreSQL port (default: 5432)
- `DATABASE`: Database name (`obcms_staging`, `obcms_prod`, etc.)

**Security:**
- Use strong password (20+ characters, mixed case, numbers, symbols)
- Never commit DATABASE_URL to version control
- Use SSL (`sslmode=require`) for external databases

---

### PostgreSQL Credentials (Docker)

**Purpose:** Docker container configuration for PostgreSQL

**Required for:** `docker-compose.yml` database container

**Example:**
```bash
# Database name (matches DATABASE_URL)
POSTGRES_DB=obcms_staging

# Database user (matches DATABASE_URL)
POSTGRES_USER=obcms_user

# Database password (matches DATABASE_URL)
POSTGRES_PASSWORD=strong-password-here
```

**CRITICAL:** These must match the credentials in `DATABASE_URL`

---

## Redis & Celery Configuration

### REDIS_URL

**Purpose:** Redis server connection for caching

**Format:** `redis://[password@]HOST:PORT/DATABASE`

**Example:**
```bash
# Docker deployment (no password)
REDIS_URL=redis://redis:6379/0

# External Redis with password
REDIS_URL=redis://password@redis.example.com:6379/0

# Redis Sentinel (high availability)
REDIS_URL=redis+sentinel://redis-sentinel:26379/0
```

**Database numbers:**
- `/0` - Main cache (recommended)
- `/1` - Session storage (optional separation)
- `/2-15` - Additional databases (if needed)

---

### CELERY_BROKER_URL

**Purpose:** Message broker for Celery background tasks

**Default:** Usually same as `REDIS_URL`

**Example:**
```bash
# Same as Redis (typical setup)
CELERY_BROKER_URL=redis://redis:6379/0

# Different database for task queue (optional)
CELERY_BROKER_URL=redis://redis:6379/1

# RabbitMQ (alternative broker)
CELERY_BROKER_URL=amqp://user:password@rabbitmq:5672//
```

---

## Email Configuration

### Email Backend

**Purpose:** Email sending method

**Values:**
- `django.core.mail.backends.smtp.EmailBackend` - Production (SMTP)
- `django.core.mail.backends.console.EmailBackend` - Development (prints to console)
- `django.core.mail.backends.dummy.EmailBackend` - Testing (discards emails)

**Example:**
```bash
# Production/Staging - SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Development - Console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

### SMTP Configuration

**Purpose:** SMTP server settings for sending emails

**Required when:** `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`

**Example (Gmail):**
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@obcms.gov.ph
EMAIL_HOST_PASSWORD=app-specific-password
DEFAULT_FROM_EMAIL=OBCMS <noreply@obcms.gov.ph>
```

**Example (Custom SMTP):**
```bash
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=smtp_username
EMAIL_HOST_PASSWORD=smtp_password
DEFAULT_FROM_EMAIL=OBCMS <noreply@yourdomain.com>
```

**Port Options:**
- `587` - TLS (recommended, set `EMAIL_USE_TLS=1`)
- `465` - SSL (set `EMAIL_USE_SSL=1`)
- `25` - Unencrypted (not recommended)

**Gmail Setup:**
1. Enable 2FA on Google account
2. Generate app-specific password (not account password)
3. Use app password in `EMAIL_HOST_PASSWORD`

---

## Security Configuration

### SECURE_SSL_REDIRECT

**Purpose:** Force HTTP requests to redirect to HTTPS

**Values:**
- `1` (True) - Production/Staging (recommended)
- `0` (False) - Development or if reverse proxy handles SSL

**Example:**
```bash
# Production/Staging - Force HTTPS
SECURE_SSL_REDIRECT=1

# Development - Allow HTTP
SECURE_SSL_REDIRECT=0
```

**Note:** Set to `0` if Nginx/Traefik/Coolify handles SSL termination

---

### SECURE_HSTS_SECONDS

**Purpose:** HTTP Strict Transport Security (HSTS) max age

**Recommended:** `31536000` (1 year)

**Example:**
```bash
# Enable after confirming HTTPS works
SECURE_HSTS_SECONDS=31536000
```

**Warning:** Only enable after HTTPS is working correctly
- Once enabled, browser will refuse HTTP for the specified duration
- Cannot be easily reverted
- Test with low value first (e.g., `300` = 5 minutes)

---

### CONTENT_SECURITY_POLICY

**Purpose:** Restricts which resources can load (prevents XSS)

**Default:** Configured in production.py

**Override example:**
```bash
# Custom CSP (single line, semicolons separated)
CONTENT_SECURITY_POLICY="default-src 'self'; script-src 'self' https://cdn.tailwindcss.com; img-src 'self' data: https:;"
```

**Note:** Only override if you need to allow additional CDNs or resources

---

## Application Configuration

### BASE_URL

**Purpose:** Base URL for absolute links (emails, API, etc.)

**Format:** Full URL with scheme, no trailing slash

**Example:**
```bash
# Staging
BASE_URL=https://staging.obcms.gov.ph

# Production
BASE_URL=https://obcms.gov.ph
```

**Used for:**
- Email templates (password reset links, etc.)
- API absolute URLs
- Sitemap generation

---

### LOG_LEVEL

**Purpose:** Logging verbosity

**Values:**
- `DEBUG` - Very verbose (development)
- `INFO` - Normal operations (staging/production)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors
- `CRITICAL` - Only critical errors

**Example:**
```bash
# Production
LOG_LEVEL=INFO

# Development (more verbose)
LOG_LEVEL=DEBUG
```

---

### GUNICORN Configuration

**Purpose:** Gunicorn web server tuning (production)

**Workers formula:** `(2 × CPU cores) + 1`

**Example:**
```bash
# Auto-calculate workers (default in gunicorn.conf.py)
# For 4-core server: (2 × 4) + 1 = 9 workers
GUNICORN_WORKERS=9

# Threads per worker (for I/O-bound apps)
GUNICORN_THREADS=2

# Worker class
GUNICORN_WORKER_CLASS=gthread  # or 'sync', 'gevent'

# Logging
GUNICORN_LOG_LEVEL=info
```

---

## Environment-Specific Settings

### Development Environment

**File:** `.env` (local, not committed to git)

```bash
# Django Core
DJANGO_SETTINGS_MODULE=obc_management.settings.development
SECRET_KEY=django-insecure-dev-key-for-local-use-only
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (SQLite default, or PostgreSQL for testing)
# DATABASE_URL=postgres://obcms:obcms_dev_password@localhost:5432/obcms_dev

# Redis (local)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Email (console - prints to terminal)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Security (relaxed for development)
SECURE_SSL_REDIRECT=0
```

---

### Staging Environment

**File:** `.env.staging`

```bash
# Django Core
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=[unique-50-char-random-string]
DEBUG=0
ALLOWED_HOSTS=staging.obcms.gov.ph,www.staging.obcms.gov.ph
CSRF_TRUSTED_ORIGINS=https://staging.obcms.gov.ph,https://www.staging.obcms.gov.ph

# Database
DATABASE_URL=postgres://obcms_user:[password]@db:5432/obcms_staging
POSTGRES_DB=obcms_staging
POSTGRES_USER=obcms_user
POSTGRES_PASSWORD=[strong-password]

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Email (real SMTP for testing notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply.staging@obcms.gov.ph
EMAIL_HOST_PASSWORD=[app-password]
DEFAULT_FROM_EMAIL=OBCMS Staging <noreply.staging@obcms.gov.ph>

# Security
SECURE_SSL_REDIRECT=1
SECURE_HSTS_SECONDS=31536000

# Application
BASE_URL=https://staging.obcms.gov.ph
LOG_LEVEL=INFO
```

See `.env.staging.example` for complete template

---

### Production Environment

**File:** `.env.production` (on server, never in git)

```bash
# Django Core
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=[unique-50-char-random-string-DIFFERENT-from-staging]
DEBUG=0
ALLOWED_HOSTS=obcms.gov.ph,www.obcms.gov.ph
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph

# Database (production credentials)
DATABASE_URL=postgres://obcms_prod_user:[strong-password]@db:5432/obcms_prod
POSTGRES_DB=obcms_prod
POSTGRES_USER=obcms_prod_user
POSTGRES_PASSWORD=[very-strong-password]

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Email (production SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@obcms.gov.ph
EMAIL_HOST_PASSWORD=[app-password]
DEFAULT_FROM_EMAIL=OBCMS <noreply@obcms.gov.ph>

# Security (strict)
SECURE_SSL_REDIRECT=1
SECURE_HSTS_SECONDS=31536000

# Application
BASE_URL=https://obcms.gov.ph
LOG_LEVEL=INFO

# Gunicorn (8-core server)
GUNICORN_WORKERS=17  # (2 × 8) + 1
GUNICORN_THREADS=2
```

---

## Configuration Validation

### Pre-Deployment Validation Script

**File:** `scripts/validate-env.sh`

```bash
#!/bin/bash
# Validate environment configuration

echo "=== OBCMS Environment Validation ==="

# Required variables
REQUIRED_VARS=(
    "DJANGO_SETTINGS_MODULE"
    "SECRET_KEY"
    "DEBUG"
    "ALLOWED_HOSTS"
    "CSRF_TRUSTED_ORIGINS"
    "DATABASE_URL"
    "REDIS_URL"
)

ERRORS=0

# Check each required variable
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: $var not set"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ $var is set"
    fi
done

# Validate DEBUG is off for production
if [ "$DJANGO_SETTINGS_MODULE" = "obc_management.settings.production" ]; then
    if [ "$DEBUG" != "0" ]; then
        echo "❌ ERROR: DEBUG must be 0 in production"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Validate SECRET_KEY is not default
if [[ "$SECRET_KEY" == *"django-insecure-"* ]]; then
    echo "❌ ERROR: SECRET_KEY must not be development key"
    ERRORS=$((ERRORS + 1))
fi

# Validate CSRF_TRUSTED_ORIGINS has scheme
if [[ "$CSRF_TRUSTED_ORIGINS" != *"https://"* ]] && [[ "$CSRF_TRUSTED_ORIGINS" != *"http://"* ]]; then
    echo "⚠️  WARNING: CSRF_TRUSTED_ORIGINS should include https:// scheme"
fi

# Summary
echo ""
echo "=== Validation Summary ==="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed - Ready for deployment"
    exit 0
else
    echo "❌ $ERRORS error(s) found - Fix before deploying"
    exit 1
fi
```

**Usage:**
```bash
# Make executable
chmod +x scripts/validate-env.sh

# Run validation
./scripts/validate-env.sh

# In deployment pipeline
./scripts/validate-env.sh || exit 1
```

---

### Django Configuration Check

**Run Django's built-in deployment check:**
```bash
# Check for deployment issues
cd src
python manage.py check --deploy

# Example output:
# System check identified no issues (0 silenced).
```

**Common warnings:**
- HSTS not enabled (ignore if first deployment)
- X-Frame-Options not set (configured in middleware)
- CSP not configured (configured in middleware)

---

## Security Best Practices

### Environment Variable Security

**DO:**
- ✅ Use different `SECRET_KEY` for each environment
- ✅ Use strong database passwords (20+ characters)
- ✅ Store `.env` files outside version control
- ✅ Use environment variables or secrets management
- ✅ Rotate secrets regularly (quarterly)

**DON'T:**
- ❌ Commit `.env` files to git
- ❌ Use production credentials in staging
- ❌ Share credentials via email/chat
- ❌ Use weak passwords
- ❌ Hardcode credentials in code

---

### Secrets Management

**Options:**

**Option 1: `.env` files (simple, suitable for most deployments)**
```bash
# .env file on server (not in git)
/opt/obcms/.env.production
```

**Option 2: Docker secrets (Docker Swarm/Kubernetes)**
```yaml
secrets:
  db_password:
    external: true
```

**Option 3: Cloud secrets management**
- AWS Secrets Manager
- Google Cloud Secret Manager
- HashiCorp Vault

**Option 4: Coolify environment variables**
- Stored in Coolify database
- Encrypted at rest
- UI for management

**Recommendation:** Use `.env` files for staging, Coolify or cloud secrets for production

---

## Templates & Examples

### Quick Start Templates

**Staging:** See `.env.staging.example`
**Production:** Copy staging template, update values

**Steps:**
```bash
# 1. Copy template
cp .env.staging.example .env.staging

# 2. Generate SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 3. Edit .env.staging
nano .env.staging

# 4. Update:
#    - SECRET_KEY (paste generated key)
#    - ALLOWED_HOSTS (your domain)
#    - CSRF_TRUSTED_ORIGINS (your domain with https://)
#    - DATABASE_URL (password)
#    - EMAIL_* (your SMTP settings)

# 5. Validate
./scripts/validate-env.sh

# 6. Deploy
docker-compose -f docker-compose.yml up -d
```

---

## Related Documents

- [Staging Deployment Checklist](./STAGING_DEPLOYMENT_CHECKLIST.md) - Pre-deployment checks
- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md) - Deployment procedures
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Environment issues

**Examples:**
- `.env.staging.example` - Staging environment template
- `.env.example` - Complete reference (all variables documented)

---

**Version:** 1.0
**Last Updated:** October 2025
**Next Review:** After Django or dependency major version updates
**Owner:** DevOps Team
