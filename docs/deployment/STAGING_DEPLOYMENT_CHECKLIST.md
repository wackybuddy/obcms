# OBCMS Staging Deployment Checklist

**Environment:** Staging
**Purpose:** Pre-deployment verification and readiness assessment
**Estimated Time:** 45-60 minutes

---

## Table of Contents

1. [Pre-Deployment Verification](#pre-deployment-verification)
2. [Environment Variables](#environment-variables)
3. [Infrastructure Readiness](#infrastructure-readiness)
4. [Database Readiness](#database-readiness)
5. [Redis Readiness](#redis-readiness)
6. [Network Configuration](#network-configuration)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Resource Availability](#resource-availability)
9. [Backup Verification](#backup-verification)
10. [Final Sign-Off](#final-sign-off)

---

## Pre-Deployment Verification

### Code Quality Checks

- [ ] **All tests passing:** `pytest -v` shows 99%+ pass rate (254/256 minimum)
- [ ] **No critical linter errors:** `flake8 src/` passes
- [ ] **Code formatting verified:** `black --check src/` passes
- [ ] **Import ordering correct:** `isort --check-only src/` passes
- [ ] **Deployment checks pass:** `python manage.py check --deploy` (no errors)

**Command:**
```bash
cd src
python manage.py check --deploy
```

**Expected:** No errors, warnings are acceptable

---

### Version Control

- [ ] **All changes committed:** `git status` shows clean working tree
- [ ] **Branch is up to date:** Latest commits pushed to remote
- [ ] **Deployment branch tagged:** Version tag created (e.g., `v1.2.0-staging`)
- [ ] **Changelog updated:** CHANGELOG.md reflects all changes

**Commands:**
```bash
git status
git log --oneline -5
git tag -a v1.2.0-staging -m "Staging deployment October 2025"
git push origin v1.2.0-staging
```

---

### Documentation Review

- [ ] **Deployment runbook reviewed:** Team familiar with procedures
- [ ] **Rollback procedures accessible:** ROLLBACK_PROCEDURES.md printed/bookmarked
- [ ] **Emergency contacts verified:** Contact list current and tested
- [ ] **Change log documented:** What's being deployed is clear

---

## Environment Variables

### Critical Variables Verification

**Location:** `.env.staging` or Coolify environment settings

#### Django Core Settings

- [ ] **DJANGO_SETTINGS_MODULE:** Set to `obc_management.settings.production`
- [ ] **SECRET_KEY:** Unique 50+ character random string (NOT development key)
- [ ] **DEBUG:** Set to `0` (False)
- [ ] **ALLOWED_HOSTS:** Contains staging domain (e.g., `staging.obcms.gov.ph`)
- [ ] **CSRF_TRUSTED_ORIGINS:** Includes `https://staging.obcms.gov.ph` (with scheme)

**Verification:**
```bash
# Check .env file exists and has required variables
cat .env.staging | grep "SECRET_KEY"
cat .env.staging | grep "DEBUG=0"
cat .env.staging | grep "ALLOWED_HOSTS"
cat .env.staging | grep "CSRF_TRUSTED_ORIGINS"
```

**Critical Checks:**
- [ ] SECRET_KEY is NOT `django-insecure-*` (development key)
- [ ] CSRF_TRUSTED_ORIGINS includes `https://` scheme (not just domain)
- [ ] No placeholder values remain (e.g., `yourdomain.com`)

#### Database Configuration

- [ ] **DATABASE_URL:** PostgreSQL connection string format correct
  ```
  postgres://username:password@host:port/database
  ```
- [ ] **POSTGRES_DB:** Database name (e.g., `obcms_staging`)
- [ ] **POSTGRES_USER:** Database user (NOT `postgres` superuser)
- [ ] **POSTGRES_PASSWORD:** Strong password (20+ chars, mixed case/numbers/symbols)

**Verification:**
```bash
# Test database connection string format
echo $DATABASE_URL | grep "postgres://"
```

#### Redis Configuration

- [ ] **REDIS_URL:** Redis connection string (e.g., `redis://redis:6379/0`)
- [ ] **CELERY_BROKER_URL:** Usually same as REDIS_URL

#### Email Configuration

- [ ] **EMAIL_BACKEND:** `django.core.mail.backends.smtp.EmailBackend`
- [ ] **EMAIL_HOST:** SMTP server (e.g., `smtp.gmail.com`)
- [ ] **EMAIL_PORT:** `587` (TLS) or `465` (SSL)
- [ ] **EMAIL_USE_TLS:** `1` if using port 587
- [ ] **EMAIL_HOST_USER:** SMTP username/email
- [ ] **EMAIL_HOST_PASSWORD:** App-specific password (NOT account password)
- [ ] **DEFAULT_FROM_EMAIL:** Sender email (e.g., `noreply@staging.obcms.gov.ph`)

**Test Command:**
```bash
# Send test email
cd src
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Deployment test', 'noreply@staging.obcms.gov.ph', ['admin@obcms.gov.ph'])
```

#### Security Headers

- [ ] **SECURE_SSL_REDIRECT:** `1` (force HTTPS)
- [ ] **SECURE_HSTS_SECONDS:** `31536000` or commented out initially

**Note:** Set HSTS after confirming HTTPS works properly

---

### Environment Variable Validation Script

Run this validation script:

```bash
#!/bin/bash
# validate-env.sh

echo "=== OBCMS Environment Validation ==="

# Check critical variables exist
REQUIRED_VARS=(
    "DJANGO_SETTINGS_MODULE"
    "SECRET_KEY"
    "DEBUG"
    "ALLOWED_HOSTS"
    "CSRF_TRUSTED_ORIGINS"
    "DATABASE_URL"
    "REDIS_URL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: $var not set"
        exit 1
    else
        echo "OK: $var is set"
    fi
done

# Validate DEBUG is off
if [ "$DEBUG" != "0" ]; then
    echo "ERROR: DEBUG must be 0 in production/staging"
    exit 1
fi

# Validate SECRET_KEY is not default
if [[ "$SECRET_KEY" == *"django-insecure-"* ]]; then
    echo "ERROR: SECRET_KEY must not be development key"
    exit 1
fi

# Validate CSRF_TRUSTED_ORIGINS has scheme
if [[ "$CSRF_TRUSTED_ORIGINS" != *"https://"* ]]; then
    echo "WARNING: CSRF_TRUSTED_ORIGINS should include https:// scheme"
fi

echo "=== Validation Complete ==="
```

---

## Infrastructure Readiness

### Server Specifications (Minimum)

**Staging Environment:**
- [ ] **CPU:** 2 cores minimum, 4 cores recommended
- [ ] **RAM:** 4GB minimum, 8GB recommended
- [ ] **Disk:** 20GB available space (50GB recommended)
- [ ] **OS:** Ubuntu 22.04 LTS or Debian 12

**Verification:**
```bash
# Check system resources
lscpu | grep "CPU(s):"
free -h
df -h
lsb_release -a
```

---

### Docker Installation

- [ ] **Docker installed:** Version 24.0+ (latest stable)
- [ ] **Docker Compose installed:** Version 2.20+
- [ ] **Docker daemon running:** `systemctl status docker`
- [ ] **User has Docker permissions:** Can run `docker ps` without sudo

**Verification:**
```bash
docker --version
docker-compose --version
docker ps
systemctl status docker
```

**Expected:**
```
Docker version 24.0.0 or higher
Docker Compose version v2.20.0 or higher
```

---

### Network Connectivity

- [ ] **Internet access verified:** Can reach Docker Hub
- [ ] **DNS resolution working:** Can resolve domain names
- [ ] **Firewall rules configured:** Required ports open

**Verification:**
```bash
# Test Docker Hub connectivity
docker pull hello-world

# Test DNS
ping -c 3 google.com

# Check firewall status
sudo ufw status
```

---

## Database Readiness

### PostgreSQL Configuration

- [ ] **PostgreSQL container healthy:** `docker-compose ps db` shows "healthy"
- [ ] **Database exists:** Database created with correct name
- [ ] **User has permissions:** Database user can connect and write
- [ ] **Connection pooling configured:** `CONN_MAX_AGE=600` in settings

**Verification:**
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.yml exec db pg_isready -U obcms_user

# Test database connection
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c "SELECT version();"

# Verify migrations table exists
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c "\dt django_migrations"
```

**Expected Output:**
```
/var/run/postgresql:5432 - accepting connections
PostgreSQL 17.x
```

---

### Database Migrations Status

- [ ] **All migrations applied:** No pending migrations
- [ ] **Migration history clean:** No fake migrations or errors

**Verification:**
```bash
cd src
python manage.py showmigrations

# Should show all [X] checkmarks
```

---

### Database Size & Performance

- [ ] **Adequate disk space:** 10GB+ available for database growth
- [ ] **Connection limits appropriate:** max_connections >= 100
- [ ] **Shared buffers configured:** At least 256MB

**Verification:**
```bash
# Check database size
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c "SELECT pg_size_pretty(pg_database_size('obcms_staging'));"

# Check PostgreSQL configuration
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c "SHOW max_connections;"
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c "SHOW shared_buffers;"
```

---

## Redis Readiness

### Redis Configuration

- [ ] **Redis container healthy:** `docker-compose ps redis` shows "healthy"
- [ ] **Redis accepting connections:** Can ping Redis
- [ ] **Redis persistence enabled:** RDB or AOF configured
- [ ] **Memory limit set:** maxmemory configured appropriately

**Verification:**
```bash
# Check Redis is running
docker-compose -f docker-compose.yml exec redis redis-cli ping

# Check Redis info
docker-compose -f docker-compose.yml exec redis redis-cli info server

# Test set/get
docker-compose -f docker-compose.yml exec redis redis-cli SET test "deployment-check"
docker-compose -f docker-compose.yml exec redis redis-cli GET test
docker-compose -f docker-compose.yml exec redis redis-cli DEL test
```

**Expected:** `PONG` response and `deployment-check` retrieved

---

### Cache Functionality

- [ ] **Django cache working:** Can write and read from cache
- [ ] **Celery can connect:** Celery worker can reach Redis broker

**Verification:**
```bash
cd src
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'ok', timeout=60)
>>> cache.get('test')
'ok'
>>> cache.delete('test')
True
```

---

## Network Configuration

### DNS Configuration

- [ ] **Domain registered:** Staging domain exists (e.g., `staging.obcms.gov.ph`)
- [ ] **A record configured:** Points to server IP
- [ ] **DNS propagation complete:** Domain resolves to correct IP

**Verification:**
```bash
# Check DNS resolution
nslookup staging.obcms.gov.ph

# Check from external DNS
dig staging.obcms.gov.ph @8.8.8.8
```

**Expected:** IP matches server IP

---

### Firewall Rules

Required ports must be open:

- [ ] **Port 80 (HTTP):** Open for HTTPS redirect
- [ ] **Port 443 (HTTPS):** Open for secure traffic
- [ ] **Port 5432 (PostgreSQL):** Blocked externally (only internal access)
- [ ] **Port 6379 (Redis):** Blocked externally (only internal access)

**Verification:**
```bash
# Check UFW status (Ubuntu)
sudo ufw status

# Test external port access
nc -zv staging.obcms.gov.ph 80
nc -zv staging.obcms.gov.ph 443
```

**Expected:**
- Ports 80, 443: Connection succeeded
- Ports 5432, 6379: Connection refused (from external)

---

### Load Balancer / Reverse Proxy

- [ ] **Nginx configured:** If using Nginx (or Coolify handles this)
- [ ] **SSL termination working:** HTTPS requests reach application
- [ ] **WebSocket support:** If using real-time features
- [ ] **Request size limits:** `client_max_body_size 100M` (for file uploads)

**Verification:**
```bash
# Check Nginx config (if applicable)
nginx -t

# Check reverse proxy headers
curl -I https://staging.obcms.gov.ph
```

---

## SSL/TLS Configuration

### SSL Certificate

- [ ] **Certificate obtained:** From Let's Encrypt or CA
- [ ] **Certificate installed:** Nginx/Traefik configured
- [ ] **Certificate valid:** Not expired, correct domain
- [ ] **Auto-renewal configured:** Certbot/Coolify auto-renewal enabled

**Verification:**
```bash
# Check certificate expiry
echo | openssl s_client -servername staging.obcms.gov.ph \
    -connect staging.obcms.gov.ph:443 2>/dev/null | \
    openssl x509 -noout -dates

# Check certificate chain
curl -vI https://staging.obcms.gov.ph 2>&1 | grep -A 5 "SSL connection"
```

**Expected:**
- Certificate valid for 60+ days
- No SSL errors

---

### HTTPS Verification

- [ ] **HTTPS works:** Can access `https://staging.obcms.gov.ph`
- [ ] **HTTP redirects to HTTPS:** `http://` automatically redirects
- [ ] **No mixed content warnings:** All resources load over HTTPS
- [ ] **SSL Labs grade A:** (optional, use https://www.ssllabs.com/ssltest/)

**Verification:**
```bash
# Test HTTPS access
curl -I https://staging.obcms.gov.ph

# Test HTTP redirect
curl -I http://staging.obcms.gov.ph

# Should see: Location: https://staging.obcms.gov.ph
```

---

## Resource Availability

### Disk Space

- [ ] **Root filesystem:** 20GB+ available
- [ ] **Docker volume space:** 10GB+ available
- [ ] **Database volume:** 5GB+ available
- [ ] **Backup location:** 10GB+ available

**Verification:**
```bash
# Check disk usage
df -h

# Check Docker volume usage
docker system df

# Critical: Ensure /var/lib/docker has space
df -h /var/lib/docker
```

**Thresholds:**
- Warning: <5GB free
- Critical: <2GB free

---

### Memory Availability

- [ ] **Free RAM:** 2GB+ available before deployment
- [ ] **Swap configured:** At least 2GB swap space
- [ ] **Memory limits set:** Container memory limits configured

**Verification:**
```bash
# Check memory
free -h

# Check swap
swapon --show

# Expected: At least 2GB free RAM + 2GB swap
```

---

### CPU Availability

- [ ] **CPU load acceptable:** Load average < number of CPU cores
- [ ] **No runaway processes:** No processes consuming 100% CPU

**Verification:**
```bash
# Check load average
uptime

# Check top processes
top -bn1 | head -20

# Expected: Load average < 2.0 for 2-core system
```

---

## Backup Verification

### Database Backups

- [ ] **Backup directory exists:** `/opt/backups/obcms_staging/` created
- [ ] **Backup script executable:** `backup.sh` has execute permissions
- [ ] **Latest backup exists:** Backup from last 24 hours present
- [ ] **Backup restoration tested:** Can restore from backup successfully

**Verification:**
```bash
# Check backup directory
ls -lh /opt/backups/obcms_staging/

# List recent backups
ls -lt /opt/backups/obcms_staging/ | head -5

# Verify backup file integrity
gunzip -t /opt/backups/obcms_staging/latest.sql.gz
```

---

### Backup Restoration Test

Perform this BEFORE deployment:

```bash
# 1. Create test database
docker-compose -f docker-compose.yml exec db \
    psql -U postgres -c "CREATE DATABASE obcms_test;"

# 2. Restore backup to test database
gunzip < /opt/backups/obcms_staging/latest.sql.gz | \
    docker-compose -f docker-compose.yml exec -T db \
    psql -U obcms_user obcms_test

# 3. Verify restoration
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user obcms_test -c "SELECT COUNT(*) FROM auth_user;"

# 4. Cleanup
docker-compose -f docker-compose.yml exec db \
    psql -U postgres -c "DROP DATABASE obcms_test;"
```

**Expected:** User count matches production count

---

### Automated Backup Schedule

- [ ] **Cron job configured:** Daily backups scheduled
- [ ] **Retention policy set:** Keep 7 days of backups
- [ ] **Backup notifications:** Email on backup failure (optional)

**Verification:**
```bash
# Check cron jobs
crontab -l | grep backup

# Expected: Daily backup at 2 AM
# 0 2 * * * /opt/scripts/backup-obcms.sh
```

---

## Final Sign-Off

### Pre-Deployment Meeting

- [ ] **Team briefed:** All stakeholders aware of deployment
- [ ] **Deployment window confirmed:** Scheduled time agreed upon
- [ ] **Rollback plan reviewed:** Team knows rollback procedures
- [ ] **Communication plan ready:** User notification prepared

---

### Go/No-Go Decision

**Deployment Approved:**

- [ ] All critical checks passed (no failures in sections above)
- [ ] Team is available during deployment window
- [ ] Rollback procedures accessible and understood
- [ ] Emergency contacts verified

**Sign-Off:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Technical Lead** | ________________ | ________________ | ______ |
| **Database Admin** | ________________ | ________________ | ______ |
| **DevOps Engineer** | ________________ | ________________ | ______ |
| **Project Manager** | ________________ | ________________ | ______ |

---

### Deployment Readiness Score

**Scoring:** 1 point per checked item

| Category | Items | Score | Max |
|----------|-------|-------|-----|
| Pre-Deployment Verification | __ | __ | 10 |
| Environment Variables | __ | __ | 20 |
| Infrastructure Readiness | __ | __ | 10 |
| Database Readiness | __ | __ | 8 |
| Redis Readiness | __ | __ | 5 |
| Network Configuration | __ | __ | 8 |
| SSL/TLS Configuration | __ | __ | 6 |
| Resource Availability | __ | __ | 6 |
| Backup Verification | __ | __ | 6 |
| Final Sign-Off | __ | __ | 4 |
| **TOTAL** | | **__/83** | **83** |

**Readiness Criteria:**
- **READY:** 80-83 points (96%+)
- **REVIEW:** 70-79 points (84-95%) - Address missing items
- **NOT READY:** <70 points (<84%) - Do NOT deploy

---

## Quick Reference Commands

### Health Checks
```bash
# Check all services
docker-compose -f docker-compose.yml ps

# Check database
docker-compose -f docker-compose.yml exec db pg_isready -U obcms_user

# Check Redis
docker-compose -f docker-compose.yml exec redis redis-cli ping

# Check application health
curl https://staging.obcms.gov.ph/health/
curl https://staging.obcms.gov.ph/ready/
```

### Emergency Stop
```bash
# Stop all services
docker-compose -f docker-compose.yml down

# Stop without removing containers (faster restart)
docker-compose -f docker-compose.yml stop
```

---

## Related Documents

- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md) - Step-by-step deployment procedure
- [Post-Deployment Verification](./POST_DEPLOYMENT_VERIFICATION.md) - After deployment checks
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md) - Emergency rollback steps
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
- [Environment Setup](./ENVIRONMENT_SETUP.md) - Detailed environment variable guide

---

**Version:** 1.0
**Last Updated:** October 2025
**Next Review:** After each deployment
**Owner:** DevOps Team
