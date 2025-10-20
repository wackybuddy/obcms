# OBCMS Production Deployment Issues Resolution Plan

**Version:** 2.0
**Date:** January 2025
**Status:** Field-Tested Checklist
**Target Platform:** Coolify with Traefik / Docker Compose / Generic HTTPS Proxy

---

## Executive Summary

This document provides a comprehensive, field-tested checklist for resolving common deployment issues when shipping the **Other Bangsamoro Communities Management System (OBCMS)** to production. It consolidates Django deployment best practices, Docker containerization patterns, and platform-specific configurations for Coolify/Traefik environments.

### Critical Statistics
- **12 Critical Issues** identified in current setup
- **4 Blockers** must be fixed before production launch
- **Research Sources:** Django 5.2 docs, Docker best practices 2025, Coolify/Traefik documentation, GeoDjango deployment guides, production case studies

---

## Issue Severity Legend

| Symbol | Severity | Description | Deployment Impact |
|--------|----------|-------------|-------------------|
| 🔴 | **Critical** | Blocks production deployment, security risk | Must fix before launch |
| 🟠 | **High** | Affects reliability, performance at scale | Fix before scaling |
| 🟡 | **Medium** | Operational excellence, observability | Post-launch improvement |
| 🟢 | **Low** | Future enhancement, nice-to-have | Optional optimization |

---

## Table of Contents

1. [Critical Issues (Must Fix)](#critical-issues-must-fix)
2. [High Priority Issues (Fix Before Scaling)](#high-priority-issues-fix-before-scaling)
3. [Medium Priority Issues (Operational Excellence)](#medium-priority-issues-operational-excellence)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Pre-Deployment Verification Checklist](#pre-deployment-verification-checklist)
6. [Platform-Specific Configurations](#platform-specific-configurations)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [References & Resources](#references--resources)

---

## Critical Issues (Must Fix)

### 🔴 Issue #1: Production Settings Not Locked Down

**Current State:**
- No separate production settings file exists
- `DEBUG` defaults to `True` in [src/obc_management/settings.py](../../src/obc_management/settings.py)
- Missing critical security headers: `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- No `python manage.py check --deploy` in deployment workflow
- `ALLOWED_HOSTS` parsing from CSV may include whitespace

**Risk Impact:**
- ⚠️ Debug mode in production leaks stack traces, environment variables, SQL queries
- ⚠️ Insecure cookies transmitted over HTTP expose session hijacking
- ⚠️ Missing HSTS allows downgrade attacks
- ⚠️ 400 Bad Request errors from misconfigured `ALLOWED_HOSTS`

**Solution:**

#### Step 1: Create Production Settings Module

Create new file: `src/obc_management/settings/production.py`

```python
"""
Production settings for OBCMS.
DO NOT use this in development.
"""
from ..settings import *  # Import base settings

# SECURITY: Force DEBUG off in production (no environment override)
DEBUG = False
TEMPLATE_DEBUG = False

# SECURITY: Allowed hosts (strict validation)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be explicitly set in production")

# SECURITY: CSRF trusted origins (required for HTTPS behind proxy)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if not CSRF_TRUSTED_ORIGINS:
    raise ValueError("CSRF_TRUSTED_ORIGINS must be set for production HTTPS")

# SECURITY: Force HTTPS redirects
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)

# SECURITY: HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SECURITY: Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# SECURITY: Additional headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True

# SECURITY: Proxy SSL header (for Coolify/Traefik/Nginx)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# ADMIN: Restrict admin access by IP if needed
# ALLOWED_ADMIN_IPS = env.list('ALLOWED_ADMIN_IPS', default=[])

# LOGGING: Production logging (stdout/stderr for Docker)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env.str('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# PERFORMANCE: Database connection pooling (if using PgBouncer)
# DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
# DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True  # Required for PgBouncer transaction mode

# EMAIL: Ensure production email backend is configured
if EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    raise ValueError("EMAIL_BACKEND must be configured for production (not console)")
```

#### Step 2: Create Settings Package Structure

```bash
cd src/obc_management
mkdir -p settings
touch settings/__init__.py
mv settings.py settings/base.py
```

Update `settings/__init__.py`:
```python
"""
Settings package for OBCMS.
Default imports from base settings.
"""
from .base import *  # noqa
```

Update `settings/production.py` imports:
```python
from .base import *  # Import from base, not from parent
```

#### Step 3: Update Environment Configuration

Add to `.env.example`:
```env
# Django Settings Module
DJANGO_SETTINGS_MODULE=obc_management.settings.production

# Security Headers (Production REQUIRED)
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=1

# Session Security
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1

# HSTS (enable after confirming HTTPS works)
# SECURE_HSTS_SECONDS=31536000
```

#### Step 4: Add Deployment Checks to Workflow

For Coolify, add to **Pre-Deploy Command**:
```bash
cd src && python manage.py check --deploy --settings=obc_management.settings.production
```

For Docker, update `docker-compose.prod.yml`:
```yaml
migrate:
  build:
    context: .
    target: production
  command: >
    sh -c "cd src &&
           python manage.py check --deploy --settings=obc_management.settings.production &&
           python manage.py migrate --noinput"
  environment:
    DJANGO_SETTINGS_MODULE: obc_management.settings.production
```

**Verification:**
```bash
# Test deployment checks locally
cd src
export DJANGO_SETTINGS_MODULE=obc_management.settings.production
export DEBUG=0
export ALLOWED_HOSTS=localhost,127.0.0.1
export CSRF_TRUSTED_ORIGINS=https://localhost
python manage.py check --deploy
```

**Expected warnings to address:**
- `SECURE_SSL_REDIRECT` check
- `SECURE_HSTS_SECONDS` check
- `SESSION_COOKIE_SECURE` check

**References:**
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Django Security Settings](https://docs.djangoproject.com/en/5.2/topics/security/)
- [DigitalOcean Django Hardening Guide](https://www.digitalocean.com/community/tutorials/how-to-harden-your-production-django-project)

---

### 🔴 Issue #2: Reverse Proxy HTTPS Headers Not Configured

**Current State:**
- No `SECURE_PROXY_SSL_HEADER` setting exists
- No `CSRF_TRUSTED_ORIGINS` configured (will cause 403 CSRF failures)
- No `USE_X_FORWARDED_HOST` for multi-domain support
- Coolify/Traefik forwarded headers not documented

**Risk Impact:**
- ⚠️ Django thinks requests are HTTP when they're actually HTTPS (mixed content errors)
- ⚠️ `request.build_absolute_uri()` returns HTTP URLs in HTTPS context
- ⚠️ CSRF validation fails for HTTPS POST requests (403 Forbidden)
- ⚠️ Secure cookies not set even when using HTTPS

**Solution:**

#### Step 1: Configure Django for Reverse Proxy

Already included in production settings above:
```python
# SECURITY: Proxy SSL header (for Coolify/Traefik/Nginx)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# SECURITY: CSRF trusted origins (required for HTTPS behind proxy)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
```

#### Step 2: Verify Traefik Configuration (Coolify)

Coolify automatically configures Traefik to forward headers. Verify in Coolify dashboard:

**Settings → Server → Proxy → Traefik**

Confirm these Traefik entrypoint settings exist:
```toml
[entryPoints.http]
  address = ":80"
  [entryPoints.http.forwardedHeaders]
    insecure = false  # Should be false for security
    trustedIPs = ["127.0.0.1/32", "10.0.0.0/8"]  # Internal IPs only

[entryPoints.https]
  address = ":443"
  [entryPoints.https.forwardedHeaders]
    insecure = false
    trustedIPs = ["127.0.0.1/32", "10.0.0.0/8"]
```

**⚠️ Security Warning:** Do NOT set `forwardedHeaders.insecure = true` in production. This allows clients to spoof `X-Forwarded-*` headers.

#### Step 3: Configure Cloudflare (if used)

If using Cloudflare in front of Coolify:

1. **Enable Cloudflare Authenticated Origin Pulls:**
   - SSL/TLS → Origin Server → Enable Authenticated Origin Pulls
   - Install Cloudflare origin certificate in Traefik

2. **Update Traefik Trusted IPs:**
   ```toml
   [entryPoints.https.forwardedHeaders]
     trustedIPs = [
       "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",  # Cloudflare IPs
       "104.16.0.0/13", "104.24.0.0/14", "108.162.192.0/18",
       # ... (full Cloudflare IP list)
     ]
   ```

3. **Django Configuration:**
   ```python
   # If using Cloudflare, trust CF-Connecting-IP header
   if env.bool('USE_CLOUDFLARE', default=False):
       MIDDLEWARE.insert(0, 'common.middleware.CloudflareRealIPMiddleware')
   ```

   Create `src/common/middleware.py`:
   ```python
   class CloudflareRealIPMiddleware:
       """Extract real client IP from Cloudflare CF-Connecting-IP header."""
       def __init__(self, get_response):
           self.get_response = get_response

       def __call__(self, request):
           if 'HTTP_CF_CONNECTING_IP' in request.META:
               request.META['REMOTE_ADDR'] = request.META['HTTP_CF_CONNECTING_IP']
           return self.get_response(request)
   ```

#### Step 4: Update Environment Variables

Add to production `.env`:
```env
# CSRF Trusted Origins (MUST include scheme)
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph

# Allowed Hosts
ALLOWED_HOSTS=obcms.gov.ph,www.obcms.gov.ph

# Cloudflare (optional)
USE_CLOUDFLARE=1
```

**Verification:**
```bash
# Test HTTPS detection
docker-compose -f docker-compose.prod.yml exec web python src/manage.py shell

>>> from django.http import HttpRequest
>>> request = HttpRequest()
>>> request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
>>> request.is_secure()
True  # Should be True

# Test CSRF origin validation
>>> from django.conf import settings
>>> settings.CSRF_TRUSTED_ORIGINS
['https://obcms.gov.ph', 'https://www.obcms.gov.ph']
```

**Common Issues:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| CSRF verification failed | Missing `https://` scheme in `CSRF_TRUSTED_ORIGINS` | Add scheme: `https://domain.com` |
| Mixed content warnings | Django generating HTTP URLs | Set `SECURE_PROXY_SSL_HEADER` |
| Redirect loops | Both proxy and Django redirecting | Disable `SECURE_SSL_REDIRECT` or fix proxy config |

**References:**
- [Traefik Forwarded Headers](https://doc.traefik.io/traefik/routing/entrypoints/#forwarded-headers)
- [Django CSRF_TRUSTED_ORIGINS](https://docs.djangoproject.com/en/5.2/ref/settings/#csrf-trusted-origins)
- [Coolify Traefik Overview](https://coolify.io/docs/knowledge-base/proxy/traefik/overview)

---

### 🔴 Issue #3: Static Files Not Production-Ready

**Current State:**
- WhiteNoise not installed (static files will 404 when `DEBUG=False`)
- Using `psycopg2-binary` instead of source `psycopg2` (not recommended for production)
- Dockerfile line 35 references non-existent `settings_minimal`
- No `STORAGES` configuration for Django 4.2+ static file backend

**Risk Impact:**
- ⚠️ All static files (CSS, JS, images) return 404 in production
- ⚠️ Admin interface completely broken (no styling)
- ⚠️ psycopg2-binary has bundled libssl that may conflict with system libraries under concurrency
- ⚠️ Potential segfaults from library version mismatches

**Solution:**

#### Step 1: Add WhiteNoise and Fix Dependencies

Update `requirements/base.txt`:
```diff
  Django>=4.2.0,<4.3.0
  djangorestframework>=3.14.0
  django-filter>=23.5
  django-cors-headers>=4.3.0
  django-crispy-forms>=2.0
  django-extensions>=3.2.0
  djangorestframework-simplejwt>=5.3.0
  celery>=5.3.0
  redis>=5.0.0
  gunicorn>=20.1.0
- psycopg2-binary>=2.9.5
+ psycopg2>=2.9.9
+ whitenoise>=6.6.0
  Pillow>=10.0.0
  python-dotenv>=1.0.0
  django-environ>=0.11.0
  pandas>=2.0.0
  openpyxl>=3.1.0
  xlsxwriter>=3.1.0
  reportlab>=4.0.0
  PyYAML>=6.0
  google-generativeai>=0.3.0
  google-cloud-aiplatform>=1.38.0
```

**Note on psycopg2:** The binary package comes with bundled libpq and libssl. In production, system library upgrades won't update these bundled versions, and the bundled libssl may conflict with other extensions under concurrency, potentially causing segfaults. Source compilation ensures optimal performance and compatibility.

#### Step 2: Configure WhiteNoise in Settings

Update `src/obc_management/settings/base.py`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← Add after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "common.middleware.MANAAccessControlMiddleware",
    "mana.middleware.ManaWorkshopContextMiddleware",
    "mana.middleware.ManaParticipantAccessMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Django 4.2+ STORAGES configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# WhiteNoise configuration
WHITENOISE_AUTOREFRESH = False  # Must be False in production
WHITENOISE_USE_FINDERS = False  # Use STATIC_ROOT only in production
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files with hashes
```

**WhiteNoise Benefits:**
- ✅ Serves static files directly from Django (no Nginx/CDN required for small deployments)
- ✅ Compresses files (gzip/brotli)
- ✅ Adds far-future cache headers automatically
- ✅ Content-addressed filenames (e.g., `styles.a3f8b91c.css`)

#### Step 3: Fix Dockerfile collectstatic Command

Update `Dockerfile` line 35:
```dockerfile
# Production stage
FROM base as production

# Install build dependencies for psycopg2 from source
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=app:app . /app/

# Collect static files (fix settings module reference)
RUN python src/manage.py collectstatic --noinput --settings=obc_management.settings.production

# Clean up build dependencies to reduce image size
RUN apt-get purge -y --auto-remove \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

USER app

# Default command
CMD ["gunicorn", "--chdir", "src", "--bind", "0.0.0.0:8000", "obc_management.wsgi:application"]
```

#### Step 4: Update Docker Build Arguments

For Coolify deployment, add build-time environment variable:
```yaml
# In Coolify → Application → Build Variables
DJANGO_SETTINGS_MODULE=obc_management.settings.production
```

**Verification:**
```bash
# Test static file collection locally
cd src
python manage.py collectstatic --noinput --settings=obc_management.settings.production
ls staticfiles/  # Should see admin/, static/, etc.

# Test WhiteNoise in production mode
DEBUG=0 gunicorn --bind 0.0.0.0:8000 obc_management.wsgi:application
curl http://localhost:8000/static/admin/css/base.css  # Should return CSS
```

**Common Issues:**

| Error | Cause | Fix |
|-------|-------|-----|
| `ValueError: Missing staticfiles manifest entry` | `collectstatic` not run | Run `collectstatic` in Dockerfile or pre-deploy |
| `OSError: no library called "cairo" was found` | Pillow missing system deps | Add `libcairo2-dev` to Dockerfile apt-get |
| Static files 404 | WhiteNoise middleware not added | Check MIDDLEWARE order |

**References:**
- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/en/stable/django.html)
- [psycopg2 Installation](https://www.psycopg.org/docs/install.html)
- [Django Static Files](https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/)

---

### 🔴 Issue #4: Unsafe Database Migration Strategy

**Current State:**
- `docker-compose.yml` lines 54-56 run migrations on every web container start
- Will cause race conditions in multi-replica deployments (Kubernetes, Docker Swarm)
- No migration rollback strategy documented
- Migrations running in parallel can corrupt schema or lock tables indefinitely

**Risk Impact:**
- ⚠️ Concurrent migrations cause deadlocks or schema corruption
- ⚠️ Zero-downtime deployments impossible (migrations block app startup)
- ⚠️ Failed migrations leave database in inconsistent state

**Solution:**

#### Step 1: Create Separate Migration Job (Docker Compose)

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - obcms_network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - obcms_network

  # MIGRATION JOB: Run once per deployment
  migrate:
    build:
      context: .
      target: production
    command: >
      sh -c "cd src &&
             python manage.py migrate --noinput"
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      DJANGO_SETTINGS_MODULE: obc_management.settings.production
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
    restart: "no"  # Critical: Run once only
    networks:
      - obcms_network

  # WEB SERVICE: Does NOT run migrations
  web:
    build:
      context: .
      target: production
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - static_volume:/app/src/staticfiles
      - media_volume:/app/src/media
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      DJANGO_SETTINGS_MODULE: obc_management.settings.production
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
      CSRF_TRUSTED_ORIGINS: ${CSRF_TRUSTED_ORIGINS}
      DEBUG: 0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully  # Wait for migration
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - obcms_network

  # CELERY WORKER
  celery:
    build:
      context: .
      target: production
    restart: unless-stopped
    command: >
      sh -c "cd src &&
             celery -A obc_management worker
             --loglevel=info
             --max-tasks-per-child=1000
             --time-limit=300"
    volumes:
      - media_volume:/app/src/media
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      DJANGO_SETTINGS_MODULE: obc_management.settings.production
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully
    stop_grace_period: 60s  # Graceful shutdown for Celery
    networks:
      - obcms_network

  # CELERY BEAT (Optional - for scheduled tasks)
  celery-beat:
    build:
      context: .
      target: production
    restart: unless-stopped
    command: >
      sh -c "cd src &&
             celery -A obc_management beat --loglevel=info"
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      DJANGO_SETTINGS_MODULE: obc_management.settings.production
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully
    networks:
      - obcms_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  obcms_network:
    driver: bridge
```

**Key Changes:**
- ✅ Separate `migrate` service with `restart: "no"`
- ✅ Web service depends on `migrate` with `condition: service_completed_successfully`
- ✅ Database healthcheck with `start_period: 30s` to avoid race conditions
- ✅ Network isolation for security

#### Step 2: Coolify Pre-Deploy Command

For Coolify deployment, configure **Pre-Deploy Command**:
```bash
cd src && python manage.py migrate --noinput --settings=obc_management.settings.production
```

Coolify runs this command once per deployment before starting the web service.

#### Step 3: Migration Safety Checks

Add migration safety check script: `scripts/check_migrations.sh`
```bash
#!/bin/bash
set -e

cd src

echo "Checking for unapplied migrations..."
python manage.py showmigrations --plan | grep '\[ \]' && {
    echo "❌ ERROR: Unapplied migrations detected!"
    python manage.py showmigrations --plan | grep '\[ \]'
    exit 1
} || {
    echo "✅ All migrations applied"
}

echo "Checking for migration conflicts..."
python manage.py makemigrations --check --dry-run || {
    echo "❌ ERROR: Migration conflicts detected!"
    exit 1
}

echo "✅ Migration checks passed"
```

Add to pre-deploy workflow:
```bash
bash scripts/check_migrations.sh && python manage.py migrate --noinput
```

#### Step 4: Zero-Downtime Migration Strategy

For large tables or long-running migrations:

1. **Use Django's `--plan` flag:**
   ```bash
   python manage.py migrate --plan
   ```

2. **Split migrations into safe/unsafe:**
   - ✅ **Safe (run during deployment):**
     - Adding nullable fields
     - Adding indexes with `CONCURRENTLY` (Django 4.2+)
     - Creating new tables

   - ⚠️ **Unsafe (requires downtime or special handling):**
     - Removing fields (requires 3-step deploy)
     - Renaming fields (requires 2-step deploy with dual-writing)
     - Adding NOT NULL constraints

3. **Use `django-safemigrate` for pre-flight checks:**
   ```bash
   pip install django-safemigrate
   ```

   Add to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       'safemigrate',
       # ... other apps
   ]
   ```

**Verification:**
```bash
# Test migration job
docker-compose -f docker-compose.prod.yml up migrate
docker-compose -f docker-compose.prod.yml logs migrate  # Check for errors

# Verify web service waits for migration
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml ps  # migrate should show "Exit 0"
```

**References:**
- [Django Migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/)
- [Zero-Downtime Migrations](https://medium.com/@fkafri/graceful-termination-of-django-and-celery-worker-pods-in-kubernetes-a5af1203258a)
- [Docker depends_on Conditions](https://docs.docker.com/compose/compose-file/05-services/#depends_on)

---

## High Priority Issues (Fix Before Scaling)

### 🟠 Issue #5: No Health Check Endpoint

**Current State:**
- No `/health/` or `/readiness/` endpoint exists
- Docker/Kubernetes healthchecks can't validate application health
- Load balancers can't detect unhealthy instances
- No liveness/readiness distinction

**Risk Impact:**
- ⚠️ Failed deployments not detected (containers keep running with broken app)
- ⚠️ Database connection issues not reflected in health status
- ⚠️ Load balancers route traffic to unhealthy instances

**Solution:**

#### Step 1: Create Health Check Views

Create `src/common/views/health.py`:
```python
"""
Health check endpoints for monitoring and orchestration.
"""
import logging
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
@never_cache
def health_check(request):
    """
    Liveness probe: Is the application running?
    Used by Docker/Kubernetes to restart failed containers.

    Returns 200 if the app can handle requests (basic check).
    """
    return JsonResponse({
        "status": "healthy",
        "version": getattr(settings, 'VERSION', 'unknown'),
    })


@require_GET
@never_cache
def readiness_check(request):
    """
    Readiness probe: Is the application ready to serve traffic?
    Used by load balancers to route traffic.

    Checks:
    - Database connectivity
    - Redis connectivity (cache)
    - Critical dependencies

    Returns 200 if ready, 503 if not ready.
    """
    checks = {
        "database": check_database(),
        "cache": check_cache(),
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JsonResponse({
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
    }, status=status_code)


def check_database():
    """Check database connectivity."""
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def check_cache():
    """Check Redis connectivity."""
    try:
        cache.set('health_check', 'ok', timeout=10)
        result = cache.get('health_check')
        cache.delete('health_check')
        return result == 'ok'
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return False
```

#### Step 2: Register URLs

Update `src/obc_management/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from common.views.health import health_check, readiness_check

urlpatterns = [
    # Health checks (no authentication required)
    path('health/', health_check, name='health'),
    path('ready/', readiness_check, name='readiness'),

    # Admin
    path('admin/', admin.site.urls),

    # ... rest of URLs
]
```

#### Step 3: Update Docker Healthchecks

Update `docker-compose.prod.yml` web service:
```yaml
web:
  # ... other config
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s  # Allow time for startup
```

Install `curl` in Dockerfile:
```dockerfile
# Production stage
FROM base as production

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# ... rest of Dockerfile
```

#### Step 4: Configure Coolify Healthcheck

In Coolify Application Settings:

**Health Check Path:** `/health/`
**Health Check Port:** `8000`
**Health Check Interval:** `30s`
**Health Check Timeout:** `10s`
**Health Check Retries:** `3`

#### Step 5: Add Monitoring Integration

For external monitoring (UptimeRobot, Pingdom, etc.):
```python
# settings/production.py

# Health check authentication (optional)
HEALTH_CHECK_SECRET = env.str('HEALTH_CHECK_SECRET', default=None)

# In views/health.py
@require_GET
@never_cache
def monitored_health_check(request):
    """External monitoring endpoint with optional authentication."""
    secret = request.GET.get('secret')
    expected_secret = getattr(settings, 'HEALTH_CHECK_SECRET', None)

    if expected_secret and secret != expected_secret:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Run comprehensive checks
    return readiness_check(request)
```

**Verification:**
```bash
# Test health endpoint
curl http://localhost:8000/health/
# Expected: {"status": "healthy", "version": "1.0.0"}

# Test readiness endpoint
curl http://localhost:8000/ready/
# Expected: {"status": "ready", "checks": {"database": true, "cache": true}}

# Test Docker healthcheck
docker-compose -f docker-compose.prod.yml ps
# web should show "(healthy)" status
```

**References:**
- [Kubernetes Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Docker Healthcheck](https://docs.docker.com/engine/reference/builder/#healthcheck)

---

### 🟠 Issue #6: Gunicorn Not Tuned for Production

**Current State:**
- Dockerfile uses Gunicorn defaults (1 worker, 30s timeout)
- No worker/thread optimization
- No access logging
- Will cause timeouts on slow requests (file uploads, reports)

**Risk Impact:**
- ⚠️ Requests timeout after 30s (users see 502 Bad Gateway)
- ⚠️ Single worker = no concurrency (one request blocks all others)
- ⚠️ No request logging for debugging

**Solution:**

#### Step 1: Create Gunicorn Configuration File

Create `gunicorn.conf.py` in project root:
```python
"""
Gunicorn configuration for OBCMS production deployment.
See: https://docs.gunicorn.org/en/stable/settings.html
"""
import multiprocessing
import os

# Server Socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker Processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"  # Use "gthread" for threading, or "gevent" for async
threads = int(os.getenv('GUNICORN_THREADS', 2))  # Threads per worker (if using gthread)
worker_connections = 1000
max_requests = 1000  # Restart worker after N requests (memory leak protection)
max_requests_jitter = 100  # Randomize restart to avoid thundering herd
timeout = 120  # Request timeout (seconds)
graceful_timeout = 30  # Graceful shutdown timeout
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "obcms"

# Server Mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True  # Load app before forking workers (faster startup, shared memory)

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting OBCMS Gunicorn server")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading OBCMS workers")

def worker_int(worker):
    """Called when a worker received SIGINT or SIGQUIT."""
    worker.log.info(f"Worker {worker.pid} received SIGINT/SIGQUIT")

def worker_abort(worker):
    """Called when a worker received SIGABRT (timeout)."""
    worker.log.warning(f"Worker {worker.pid} aborted (timeout)")
```

#### Step 2: Update Dockerfile CMD

Update `Dockerfile` production stage:
```dockerfile
# Production stage
FROM base as production

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=app:app . /app/

# Collect static files
RUN python src/manage.py collectstatic --noinput --settings=obc_management.settings.production

USER app

# Use gunicorn config file
CMD ["gunicorn", "--chdir", "src", "--config", "../gunicorn.conf.py", "obc_management.wsgi:application"]
```

#### Step 3: Add Environment Variables for Tuning

Update `.env.example`:
```env
# Gunicorn Configuration
GUNICORN_WORKERS=4  # Formula: (2 x CPU cores) + 1
GUNICORN_THREADS=2  # Threads per worker (if using gthread)
GUNICORN_LOG_LEVEL=info  # debug, info, warning, error, critical
```

#### Step 4: Worker Scaling Guidelines

Choose worker count based on workload:

| Deployment Size | CPU Cores | Workers Formula | Example |
|----------------|-----------|-----------------|---------|
| Small (1-2 CPU) | 1-2 | `(2 × cores) + 1` | 3-5 workers |
| Medium (4 CPU) | 4 | `(2 × cores) + 1` | 9 workers |
| Large (8+ CPU) | 8+ | `(2 × cores) + 1` | 17+ workers |
| Kubernetes | Variable | `--workers 1` + horizontal scaling | 1 worker per pod |

**Worker Class Selection:**
- **`sync`** (default): CPU-bound tasks, traditional Django views
- **`gthread`**: I/O-bound tasks, database-heavy operations (recommended for OBCMS)
- **`gevent`**: Async I/O, WebSocket support (requires greenlet)
- **`uvicorn.workers.UvicornWorker`**: ASGI (Django Channels, async views)

#### Step 5: Kubernetes/Container Orchestration

For Kubernetes, use **1 worker per pod** and scale horizontally:
```yaml
# gunicorn.conf.py for Kubernetes
workers = 1
threads = 4
worker_class = "gthread"
```

Update deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: obcms-web
spec:
  replicas: 4  # Scale pods, not workers
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
```

**Verification:**
```bash
# Check worker count
docker-compose -f docker-compose.prod.yml logs web | grep "Booting worker"
# Should see: "Booting worker with pid: X" for each worker

# Test concurrent requests
ab -n 100 -c 10 http://localhost:8000/health/
# Should handle concurrent requests without timeouts

# Monitor worker memory
docker stats obcms_web_1
```

**References:**
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [Gunicorn Design](https://docs.gunicorn.org/en/stable/design.html)
- [Django Deployment with Gunicorn](https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/gunicorn/)

---

### 🟠 Issue #7: Celery Not Production-Ready

**Current State:**
- No graceful shutdown configuration
- No worker limits (memory leaks, runaway tasks)
- No timezone configuration
- Docker Compose doesn't allow graceful shutdown time

**Risk Impact:**
- ⚠️ Worker restarts lose in-progress tasks
- ⚠️ Memory leaks from long-running workers
- ⚠️ Timezone mismatches cause scheduled task errors

**Solution:**

#### Step 1: Configure Celery for Production

Update `src/obc_management/settings/base.py`:
```python
# Celery Configuration
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE  # Match Django timezone

# Production settings
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart worker after N tasks (memory leak protection)
CELERY_WORKER_PREFETCH_MULTIPLIER = 4  # Tasks to prefetch per worker
CELERY_TASK_TIME_LIMIT = 300  # Hard timeout (5 minutes)
CELERY_TASK_SOFT_TIME_LIMIT = 240  # Soft timeout (4 minutes)
CELERY_TASK_ACKS_LATE = True  # Acknowledge task after completion (retry on failure)
CELERY_WORKER_DISABLE_RATE_LIMITS = False
CELERY_WORKER_SEND_TASK_EVENTS = True  # Enable monitoring
CELERY_TASK_SEND_SENT_EVENT = True
```

#### Step 2: Enable Graceful Shutdown (Celery 5.5+)

Add to production settings:
```python
# Celery 5.5+ Soft Shutdown (recommended)
CELERY_WORKER_SOFT_SHUTDOWN_TIMEOUT = 60.0  # Seconds to wait for tasks to finish
CELERY_WORKER_ENABLE_SOFT_SHUTDOWN_ON_IDLE = True  # Prevent losing ETA/retry tasks
```

**How it works:**
1. Worker receives SIGTERM
2. Waits up to 60s for running tasks to complete
3. If tasks don't finish, forces shutdown and re-queues them

#### Step 3: Update Docker Compose Celery Configuration

Already included in `docker-compose.prod.yml` above:
```yaml
celery:
  command: >
    sh -c "cd src &&
           celery -A obc_management worker
           --loglevel=info
           --max-tasks-per-child=1000
           --time-limit=300"
  stop_grace_period: 60s  # Critical: Allow graceful shutdown
```

#### Step 4: Add Celery Beat Configuration (Scheduled Tasks)

Create `src/obc_management/celery.py`:
```python
"""
Celery configuration for OBCMS.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')

app = Celery('obc_management')

# Load config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Periodic tasks (Celery Beat)
app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'common.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'send-daily-reports': {
        'task': 'monitoring.tasks.send_daily_reports',
        'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

Update `src/obc_management/__init__.py`:
```python
"""
Django WSGI/ASGI initialization and Celery app loading.
"""
# Load Celery app on Django startup
from .celery import app as celery_app

__all__ = ('celery_app',)
```

#### Step 5: Celery Monitoring (Optional)

Install Flower for real-time monitoring:
```bash
pip install flower
```

Add to `docker-compose.prod.yml`:
```yaml
flower:
  build:
    context: .
    target: production
  restart: unless-stopped
  ports:
    - "5555:5555"
  command: >
    sh -c "cd src &&
           celery -A obc_management flower
           --port=5555
           --basic_auth=${FLOWER_USER}:${FLOWER_PASSWORD}"
  environment:
    CELERY_BROKER_URL: redis://redis:6379/0
  depends_on:
    - redis
  networks:
    - obcms_network
```

Add to `.env`:
```env
FLOWER_USER=admin
FLOWER_PASSWORD=secure-password
```

**Verification:**
```bash
# Test Celery worker startup
docker-compose -f docker-compose.prod.yml logs celery
# Should see: "celery@hostname ready"

# Test graceful shutdown
docker-compose -f docker-compose.prod.yml stop celery
# Should see: "Waiting for tasks to finish..." (not abrupt kill)

# Monitor Flower
open http://localhost:5555
# Login with FLOWER_USER/FLOWER_PASSWORD
```

**References:**
- [Celery Configuration](https://docs.celeryq.dev/en/latest/userguide/configuration.html)
- [Celery Workers Guide](https://docs.celeryq.dev/en/stable/userguide/workers.html)
- [Graceful Shutdown in Kubernetes](https://medium.com/@fkafri/graceful-termination-of-django-and-celery-worker-pods-in-kubernetes-a5af1203258a)

---

## Medium Priority Issues (Operational Excellence)

### 🟡 Issue #8: Media Files Strategy Undefined

**Current State:**
- No documentation on where to store user uploads in production
- Local filesystem storage doesn't work with multiple containers
- No backup strategy for media files

**Risk Impact:**
- ⚠️ User uploads lost on container restart (if not using volumes)
- ⚠️ Multi-replica deployments fail (files on different containers)
- ⚠️ No CDN for large files (slow downloads)

**Solution:**

#### Option A: Docker Volumes (Small Scale)

**When to use:**
- Single-server deployment
- < 10 GB media files
- No multi-region requirements

**Configuration:**
```yaml
# docker-compose.prod.yml
volumes:
  media_volume:/app/src/media

web:
  volumes:
    - media_volume:/app/src/media
```

**Backup strategy:**
```bash
# Backup media files
docker run --rm -v obcms_media_volume:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/media-$(date +%Y%m%d).tar.gz -C /data .

# Restore media files
docker run --rm -v obcms_media_volume:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/media-20250130.tar.gz -C /data
```

#### Option B: S3-Compatible Storage (Production Recommended)

**When to use:**
- Multi-replica deployments
- > 10 GB media files
- Need CDN/global distribution
- Kubernetes/cloud platforms

**Step 1: Install django-storages**

Update `requirements/base.txt`:
```txt
django-storages[s3]>=1.14.0
boto3>=1.34.0
```

**Step 2: Configure S3 Storage**

Create `src/obc_management/settings/storage.py`:
```python
"""
Storage backends configuration for OBCMS.
Supports Amazon S3, DigitalOcean Spaces, MinIO, etc.
"""
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """S3 storage for static files (optional, WhiteNoise recommended)."""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    """S3 storage for media files (user uploads)."""
    location = 'media'
    default_acl = 'private'  # Private by default
    file_overwrite = False
    custom_domain = None  # Use S3 URLs directly
```

Update `src/obc_management/settings/production.py`:
```python
# S3 Storage Configuration
USE_S3 = env.bool('USE_S3', default=False)

if USE_S3:
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default=None)
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 day cache
    }
    AWS_DEFAULT_ACL = 'private'
    AWS_QUERYSTRING_AUTH = True  # Generate signed URLs
    AWS_QUERYSTRING_EXPIRE = 3600  # URL expiry (1 hour)

    # DigitalOcean Spaces (S3-compatible)
    if env.bool('USE_DO_SPACES', default=False):
        AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com"

    # MinIO (self-hosted S3-compatible)
    if env.bool('USE_MINIO', default=False):
        AWS_S3_ENDPOINT_URL = env('MINIO_ENDPOINT_URL')
        AWS_S3_USE_SSL = env.bool('MINIO_USE_SSL', default=True)

    # Storage Backends
    STORAGES = {
        "default": {
            "BACKEND": "obc_management.settings.storage.MediaStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    # Local filesystem storage (development/single-server)
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
```

**Step 3: Add Environment Variables**

Update `.env.example`:
```env
# Media Storage (S3)
USE_S3=1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=obcms-media
AWS_S3_REGION_NAME=us-east-1
# AWS_S3_CUSTOM_DOMAIN=cdn.obcms.gov.ph  # Optional CloudFront

# DigitalOcean Spaces (S3-compatible)
USE_DO_SPACES=0
# AWS_S3_ENDPOINT_URL=https://sgp1.digitaloceanspaces.com

# MinIO (self-hosted)
USE_MINIO=0
# MINIO_ENDPOINT_URL=https://minio.yourdomain.com
# MINIO_USE_SSL=1
```

**Step 4: Create S3 Bucket with Lifecycle Policy**

Create bucket with:
- **Block public access** (enabled)
- **Versioning** (enabled for backup)
- **Lifecycle rules:**
  - Delete incomplete multipart uploads after 7 days
  - Transition to Glacier after 90 days (optional)

**Bucket Policy (private media):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::obcms-media",
        "arn:aws:s3:::obcms-media/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

**IAM Policy (application user):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::obcms-media",
        "arn:aws:s3:::obcms-media/*"
      ]
    }
  ]
}
```

**Verification:**
```python
# Test S3 upload
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Upload test file
path = default_storage.save('test/test.txt', ContentFile(b'Hello S3'))
print(default_storage.url(path))  # Should return S3 URL

# Download test file
content = default_storage.open(path).read()
print(content)  # Should print b'Hello S3'

# Delete test file
default_storage.delete(path)
```

**Cost Estimation (AWS S3):**
- Storage: $0.023/GB/month (first 50 TB)
- Requests: $0.005/1000 PUT, $0.0004/1000 GET
- Data transfer: $0.09/GB out (first 10 TB)

**Example monthly cost for OBCMS:**
- 50 GB storage: $1.15
- 100K uploads (PUT): $0.50
- 1M downloads (GET): $0.40
- 100 GB transfer: $9.00
- **Total: ~$11/month**

**References:**
- [django-storages Documentation](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [Django File Storage](https://docs.djangoproject.com/en/5.2/topics/files/)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

---

### 🟡 Issue #9: Logging Not Docker-Optimized

**Current State:**
- Settings log to files (problematic in containers)
- File logs lost on container restart
- No structured logging for log aggregation

**Risk Impact:**
- ⚠️ Debugging production issues difficult (logs disappear)
- ⚠️ No centralized log aggregation (Grafana Loki, ELK)

**Solution:**

Already implemented in Issue #1 production settings:
```python
# LOGGING: Production logging (stdout/stderr for Docker)
LOGGING = {
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env.str('LOG_LEVEL', default='INFO'),
    },
}
```

**For Coolify:** Logs automatically collected and viewable in dashboard.

**For ELK/Loki:** Add log shipping container:
```yaml
# docker-compose.prod.yml
promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    - ./promtail-config.yml:/etc/promtail/config.yml
  command: -config.file=/etc/promtail/config.yml
```

---

### 🟡 Issue #10: Database Connection Pooling Not Configured

**Current State:**
- Django creates new database connection per request
- High connection churn under load
- PostgreSQL max_connections limit reached quickly

**Risk Impact:**
- ⚠️ "too many connections" errors under load
- ⚠️ Slow connection establishment

**Solution:**

#### Option A: Django Connection Pooling (Built-in)

Add to `settings/production.py`:
```python
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['CONN_HEALTH_CHECKS'] = True  # Django 4.1+
```

#### Option B: PgBouncer (External Pooler - Recommended)

Add to `docker-compose.prod.yml`:
```yaml
pgbouncer:
  image: edoburu/pgbouncer:latest
  environment:
    DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    POOL_MODE: transaction
    MAX_CLIENT_CONN: 1000
    DEFAULT_POOL_SIZE: 80
    MIN_POOL_SIZE: 30
    RESERVE_POOL_SIZE: 10
  depends_on:
    - db
  networks:
    - obcms_network
```

Update web service to connect via PgBouncer:
```yaml
web:
  environment:
    DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:5432/${POSTGRES_DB}
```

Add to `settings/production.py`:
```python
# PgBouncer transaction pooling requires disabling server-side cursors
DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
```

**References:**
- [Django Database Connection Pooling](https://docs.djangoproject.com/en/5.2/ref/databases/#persistent-connections)
- [PgBouncer Best Practices](https://www.pgbouncer.org/config.html)

---

## Implementation Roadmap

### Phase 1: Blockers (Week 1)
**Goal:** Make deployment safe for production

- [ ] **Day 1-2:** Create production settings module (#1)
  - Create `settings/production.py`
  - Add security headers
  - Update `.env.example`
  - Test with `python manage.py check --deploy`

- [ ] **Day 2-3:** Configure reverse proxy headers (#2)
  - Add `SECURE_PROXY_SSL_HEADER`
  - Add `CSRF_TRUSTED_ORIGINS`
  - Test HTTPS detection

- [ ] **Day 3-4:** Implement WhiteNoise (#3)
  - Install WhiteNoise
  - Update middleware
  - Fix Dockerfile collectstatic
  - Replace psycopg2-binary with psycopg2

- [ ] **Day 4-5:** Fix migration strategy (#4)
  - Create separate migration job
  - Update docker-compose.prod.yml
  - Test migration workflow

**Success Criteria:**
- ✅ `python manage.py check --deploy` passes
- ✅ Static files load in production mode
- ✅ Migrations run once per deployment

---

### Phase 2: Pre-Launch (Week 2)
**Goal:** Production reliability and monitoring

- [ ] **Day 6-7:** Add health checks (#5)
  - Create `/health/` and `/ready/` endpoints
  - Configure Docker healthchecks
  - Test Coolify integration

- [ ] **Day 7-8:** Tune Gunicorn (#6)
  - Create `gunicorn.conf.py`
  - Calculate optimal worker count
  - Add access logging

- [ ] **Day 8-9:** Configure Celery (#7)
  - Add production Celery settings
  - Enable graceful shutdown
  - Configure Celery Beat

- [ ] **Day 9-10:** Define media strategy (#8)
  - Choose S3 vs volumes
  - Configure django-storages (if S3)
  - Test file uploads

**Success Criteria:**
- ✅ `/health/` returns 200
- ✅ Gunicorn handles concurrent requests
- ✅ Celery workers shutdown gracefully
- ✅ Media files persist across restarts

---

### Phase 3: Operational Excellence (Week 3)
**Goal:** Monitoring, logging, performance

- [ ] **Day 11:** Optimize logging (#9)
  - Configure stdout/stderr logging
  - Add structured logging
  - Test log aggregation

- [ ] **Day 12:** Add database pooling (#10)
  - Configure PgBouncer or Django pooling
  - Test connection limits

- [ ] **Day 13-14:** Performance testing
  - Load test with `locust` or `ab`
  - Optimize database queries
  - Enable query caching

- [ ] **Day 15:** Security audit
  - Run `python manage.py check --deploy`
  - Review security headers
  - Test HTTPS enforcement

**Success Criteria:**
- ✅ Application handles 100 req/s
- ✅ No security warnings
- ✅ Logs visible in monitoring platform

---

## Pre-Deployment Verification Checklist

### Security
- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is cryptographically random (50+ chars)
- [ ] `ALLOWED_HOSTS` explicitly set (no wildcards)
- [ ] `CSRF_TRUSTED_ORIGINS` includes all domains
- [ ] `SECURE_HSTS_SECONDS = 31536000`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SECURE_PROXY_SSL_HEADER` configured for proxy
- [ ] `python manage.py check --deploy` passes with no errors

### Database
- [ ] PostgreSQL 15+ with daily backups enabled
- [ ] Database password is strong (20+ chars)
- [ ] Migrations run once per deployment (not per container)
- [ ] Connection pooling configured (PgBouncer or Django)
- [ ] Database healthcheck configured with `start_period`

### Static & Media Files
- [ ] WhiteNoise installed and middleware added
- [ ] `STORAGES` configured for Django 4.2+
- [ ] `collectstatic` runs in Dockerfile or pre-deploy
- [ ] Media files stored in S3 or persistent volume
- [ ] Static files compressed (gzip/brotli)

### Application Server
- [ ] Gunicorn workers = `(2 × CPU cores) + 1`
- [ ] Request timeout >= 120s for long requests
- [ ] Access logs enabled and visible
- [ ] Graceful shutdown timeout configured

### Background Tasks
- [ ] Celery broker URL points to Redis
- [ ] Celery `max-tasks-per-child` set (memory leak protection)
- [ ] Celery `stop_grace_period: 60s` in Docker Compose
- [ ] Celery Beat configured for scheduled tasks (if needed)

### Monitoring & Health
- [ ] `/health/` endpoint returns 200
- [ ] `/ready/` endpoint checks database and cache
- [ ] Docker healthcheck configured for web service
- [ ] Coolify/platform healthcheck configured
- [ ] Logs output to stdout/stderr (not files)

### Environment Variables
- [ ] All required variables in `.env` file
- [ ] No secrets committed to git
- [ ] `DJANGO_SETTINGS_MODULE=obc_management.settings.production`
- [ ] Email backend configured (not console)

### Docker & Orchestration
- [ ] Multi-stage Dockerfile (smaller production image)
- [ ] Running as non-root user (`USER app`)
- [ ] Volumes configured for media files
- [ ] Network isolation (not `host` mode)
- [ ] Container restart policy: `unless-stopped`

### Testing
- [ ] Manual smoke tests passed (login, CRUD, API)
- [ ] Load testing completed (100+ concurrent users)
- [ ] Database migrations tested in staging
- [ ] Rollback procedure documented and tested

---

## Platform-Specific Configurations

### Coolify Deployment

#### Step 1: Create Application
1. Go to Coolify → **Applications** → **New Application**
2. Select **Git Repository** source
3. Choose branch: `main` or `production`
4. Build method: **Dockerfile** (select `production` target)

#### Step 2: Environment Variables
```env
# Django Core
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=<generate-50-char-random-string>
DEBUG=0
ALLOWED_HOSTS=obcms.gov.ph,www.obcms.gov.ph
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph

# Database (Coolify provides these)
DATABASE_URL=postgres://<user>:<password>@<postgres-service>:5432/<db>

# Redis (Coolify provides these)
REDIS_URL=redis://<redis-service>:6379/0
CELERY_BROKER_URL=redis://<redis-service>:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@obcms.gov.ph
EMAIL_HOST_PASSWORD=<app-password>

# Storage (if using S3)
USE_S3=1
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
AWS_STORAGE_BUCKET_NAME=obcms-media
AWS_S3_REGION_NAME=ap-southeast-1
```

#### Step 3: Pre-Deploy Command
```bash
cd src && python manage.py migrate --noinput --settings=obc_management.settings.production
```

#### Step 4: Start Command
```
gunicorn --chdir src --config gunicorn.conf.py obc_management.wsgi:application
```

#### Step 5: Health Check
- **Path:** `/health/`
- **Port:** `8000`
- **Interval:** `30s`
- **Timeout:** `10s`
- **Retries:** `3`

#### Step 6: Celery Worker (Separate Application)
Create second application with:
- **Same repository and environment variables**
- **Start command:**
  ```bash
  cd src && celery -A obc_management worker --loglevel=info --max-tasks-per-child=1000
  ```

#### Step 7: SSL Certificate
- **Domain:** Add custom domain
- **SSL:** Enable Let's Encrypt (automatic)
- **Force HTTPS:** Enabled (Traefik handles redirect)

---

### Generic Docker Compose Deployment

For VPS/bare metal deployment:

```bash
# 1. Clone repository
git clone <repo-url> /opt/obcms
cd /opt/obcms

# 2. Create production environment
cp .env.example .env.prod
nano .env.prod  # Edit with production values

# 3. Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Run migrations
docker-compose -f docker-compose.prod.yml run --rm migrate

# 5. Create superuser
docker-compose -f docker-compose.prod.yml exec web python src/manage.py createsuperuser

# 6. Verify deployment
curl http://localhost:8000/health/
```

**Nginx reverse proxy:**
```nginx
server {
    listen 80;
    server_name obcms.gov.ph;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name obcms.gov.ph;

    ssl_certificate /etc/letsencrypt/live/obcms.gov.ph/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/obcms.gov.ph/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Troubleshooting Guide

### Issue: Static files return 404

**Symptoms:**
- Admin interface has no styling
- CSS/JS files return 404

**Diagnosis:**
```bash
docker-compose -f docker-compose.prod.yml exec web python src/manage.py collectstatic --dry-run --noinput
docker-compose -f docker-compose.prod.yml exec web ls -la src/staticfiles/
```

**Fixes:**
1. Run `collectstatic` in Dockerfile
2. Verify WhiteNoise middleware added
3. Check `STATIC_ROOT` and `STORAGES` configuration

---

### Issue: CSRF verification failed

**Symptoms:**
- POST requests return 403 Forbidden
- Error: "CSRF verification failed. Request aborted."

**Diagnosis:**
```python
# In Django shell
from django.conf import settings
print(settings.CSRF_TRUSTED_ORIGINS)
print(settings.SECURE_PROXY_SSL_HEADER)
```

**Fixes:**
1. Add `https://` scheme to `CSRF_TRUSTED_ORIGINS`
2. Set `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
3. Verify proxy forwards `X-Forwarded-Proto` header

---

### Issue: Database connection errors

**Symptoms:**
- "connection refused" or "could not connect to server"
- Intermittent 500 errors

**Diagnosis:**
```bash
docker-compose -f docker-compose.prod.yml exec web python src/manage.py dbshell
docker-compose -f docker-compose.prod.yml logs db
```

**Fixes:**
1. Add database healthcheck with `start_period: 30s`
2. Configure `depends_on` with `condition: service_healthy`
3. Check `DATABASE_URL` environment variable

---

### Issue: Gunicorn worker timeouts

**Symptoms:**
- 502 Bad Gateway errors
- Logs show "Worker with pid X was terminated due to timeout"

**Diagnosis:**
```bash
docker-compose -f docker-compose.prod.yml logs web | grep timeout
```

**Fixes:**
1. Increase `timeout = 120` in `gunicorn.conf.py`
2. Add more workers or threads
3. Profile slow views with `django-silk`

---

### Issue: Celery tasks not processing

**Symptoms:**
- Tasks stuck in "pending" state
- No worker logs

**Diagnosis:**
```bash
docker-compose -f docker-compose.prod.yml logs celery
docker-compose -f docker-compose.prod.yml exec celery celery -A obc_management inspect active
```

**Fixes:**
1. Verify `CELERY_BROKER_URL` points to correct Redis
2. Check Redis connectivity: `redis-cli -u $REDIS_URL ping`
3. Restart workers: `docker-compose -f docker-compose.prod.yml restart celery`

---

## References & Resources

### Official Documentation
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Django Security](https://docs.djangoproject.com/en/5.2/topics/security/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [Celery Configuration](https://docs.celeryq.dev/en/latest/userguide/configuration.html)
- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/en/stable/django.html)
- [django-storages S3](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)

### Platform-Specific
- [Coolify Documentation](https://coolify.io/docs)
- [Traefik Forwarded Headers](https://doc.traefik.io/traefik/routing/entrypoints/#forwarded-headers)
- [Docker Compose Healthchecks](https://docs.docker.com/compose/compose-file/05-services/#healthcheck)

### Security & Best Practices
- [OWASP Django Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)
- [DigitalOcean Django Hardening](https://www.digitalocean.com/community/tutorials/how-to-harden-your-production-django-project)
- [Django Best Practices: Security](https://learndjango.com/tutorials/django-best-practices-security)

### Tutorials & Guides
- [Dockerizing Django with Postgres, Gunicorn, and Nginx](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/)
- [Django Docker Best Practices](https://betterstack.com/community/guides/scaling-python/django-docker-best-practices/)
- [Storing Django Static and Media Files on Amazon S3](https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/)

---

## Appendix: Quick Reference Commands

### Development
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python src/manage.py migrate

# Create superuser
docker-compose exec web python src/manage.py createsuperuser

# Django shell
docker-compose exec web python src/manage.py shell
```

### Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm migrate

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Check deployment settings
docker-compose -f docker-compose.prod.yml exec web python src/manage.py check --deploy

# Restart services
docker-compose -f docker-compose.prod.yml restart web celery
```

### Debugging
```bash
# Access container shell
docker-compose -f docker-compose.prod.yml exec web bash

# Check database connection
docker-compose -f docker-compose.prod.yml exec web python src/manage.py dbshell

# Check Redis connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Inspect Celery workers
docker-compose -f docker-compose.prod.yml exec celery celery -A obc_management inspect active

# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

**Document Maintainer:** OBCMS DevOps Team
**Last Updated:** January 2025
**Next Review:** April 2025

For questions or issues, refer to:
- GitHub Issues: `<repository-url>/issues`
- Internal Documentation: `docs/deployment/`
- Production Runbook: `docs/operations/runbook.md`