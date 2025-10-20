# OBCMS Deployment Troubleshooting Guide

**Purpose:** Solutions for common deployment and operational issues
**Audience:** DevOps Engineers, On-Call Team
**Format:** Problem → Diagnosis → Solution

---

## Table of Contents

1. [Quick Diagnostic Decision Tree](#quick-diagnostic-decision-tree)
2. [Container Startup Issues](#container-startup-issues)
3. [Database Issues](#database-issues)
4. [Redis & Caching Issues](#redis--caching-issues)
5. [Network & Connectivity](#network--connectivity)
6. [Performance Issues](#performance-issues)
7. [Memory & Resource Exhaustion](#memory--resource-exhaustion)
8. [Disk Space Issues](#disk-space-issues)
9. [SSL/HTTPS Issues](#sslhttps-issues)
10. [Application Errors](#application-errors)

---

## Quick Diagnostic Decision Tree

```
Service not responding?
│
├─ Can't access website?
│  ├─ HTTPS error → See [SSL/HTTPS Issues](#sslhttps-issues)
│  ├─ Connection timeout → See [Network & Connectivity](#network--connectivity)
│  └─ 502/503 error → See [Container Startup Issues](#container-startup-issues)
│
├─ Slow performance?
│  ├─ Pages loading slowly → See [Performance Issues](#performance-issues)
│  ├─ Database slow → See [Database Issues](#database-issues)
│  └─ High CPU/memory → See [Memory & Resource Exhaustion](#memory--resource-exhaustion)
│
├─ Application errors?
│  ├─ 500 errors → See [Application Errors](#application-errors)
│  ├─ 403 CSRF errors → See [CSRF Issues](#csrf-protection-issues)
│  └─ Database errors → See [Database Issues](#database-issues)
│
└─ Deployment failed?
   ├─ Build failed → See [Build Issues](#build-failures)
   ├─ Migration failed → See [Migration Failures](#migration-failures)
   └─ Container won't start → See [Container Startup Issues](#container-startup-issues)
```

---

## Container Startup Issues

### Problem: Web Container Won't Start

**Symptoms:**
- `docker-compose ps` shows container as "Restarting" or "Exited"
- Health check never passes
- Deployment stuck on container startup

**Diagnosis:**
```bash
# Check container status
docker-compose -f docker-compose.yml ps web

# View logs
docker-compose -f docker-compose.yml logs web

# Check container inspect
docker inspect obcms-web-1 | grep -A 20 State
```

**Common causes and solutions:**

#### 1. Missing Environment Variables

**Error in logs:**
```
KeyError: 'ALLOWED_HOSTS'
django.core.exceptions.ImproperlyConfigured: ALLOWED_HOSTS must be explicitly set
```

**Solution:**
```bash
# Check .env file exists
ls -la .env.staging

# Verify required variables
grep -E "^(SECRET_KEY|DEBUG|ALLOWED_HOSTS|DATABASE_URL)" .env.staging

# Fix: Add missing variables to .env
nano .env.staging

# Restart container
docker-compose -f docker-compose.yml restart web
```

---

#### 2. Invalid SECRET_KEY

**Error in logs:**
```
ValueError: SECRET_KEY must not be development key
```

**Solution:**
```bash
# Generate new SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update .env file
SECRET_KEY=[paste generated key]

# Restart
docker-compose -f docker-compose.yml restart web
```

---

#### 3. CSRF_TRUSTED_ORIGINS Missing Scheme

**Error in logs:**
```
ValueError: Invalid CSRF_TRUSTED_ORIGINS format: staging.obcms.gov.ph
Each origin must include the scheme (https:// or http://)
```

**Solution:**
```bash
# Fix .env - MUST include https://
CSRF_TRUSTED_ORIGINS=https://staging.obcms.gov.ph,https://www.staging.obcms.gov.ph

# Restart
docker-compose -f docker-compose.yml restart web
```

---

#### 4. Port Already in Use

**Error in logs:**
```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# OR
netstat -tulpn | grep 8000

# Kill the process
kill -9 [PID]

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # External:Internal

# Restart
docker-compose -f docker-compose.yml up -d
```

---

### Problem: Database Container Won't Start

**Symptoms:**
- PostgreSQL container exits immediately
- Web container can't connect to database
- `pg_isready` check fails

**Diagnosis:**
```bash
# Check database container
docker-compose -f docker-compose.yml ps db

# View logs
docker-compose -f docker-compose.yml logs db

# Common errors:
# - "invalid value for parameter 'max_connections'"
# - "data directory has wrong permissions"
# - "could not create shared memory segment"
```

**Solutions:**

#### 1. Data Directory Permissions

```bash
# Check volume permissions
docker volume inspect obcms_postgres_data

# Fix: Remove volume and recreate
docker-compose -f docker-compose.yml down -v
docker volume rm obcms_postgres_data
docker-compose -f docker-compose.yml up -d db

# Wait for database initialization (30-60 seconds)
docker-compose -f docker-compose.yml logs -f db
```

#### 2. Shared Memory Issue

**Error:** `could not create shared memory segment: Invalid argument`

**Solution:**
```yaml
# Add to docker-compose.yml under db service:
shm_size: 256mb
```

---

### Problem: Celery Worker Won't Start

**Symptoms:**
- Celery worker exits or restarts continuously
- Tasks not processing
- "No module named" errors

**Diagnosis:**
```bash
docker-compose -f docker-compose.yml logs celery
```

**Common errors:**

#### 1. Cannot Import Application

**Error:** `ModuleNotFoundError: No module named 'obc_management'`

**Solution:**
```bash
# Ensure PYTHONPATH set correctly in Dockerfile
ENV PYTHONPATH=/app/src

# Or in docker-compose.yml:
environment:
  - PYTHONPATH=/app/src

# Restart
docker-compose -f docker-compose.yml restart celery
```

#### 2. Redis Connection Failed

**Error:** `Error while reading from socket: (104, 'Connection reset by peer')`

**Solution:**
```bash
# Check Redis is running
docker-compose -f docker-compose.yml ps redis

# Test Redis connection
docker-compose -f docker-compose.yml exec redis redis-cli ping

# If Redis down, restart
docker-compose -f docker-compose.yml restart redis

# Then restart Celery
docker-compose -f docker-compose.yml restart celery
```

---

## Database Issues

### Problem: Database Connection Failures

**Symptoms:**
- "could not connect to server" errors
- "Too many connections" errors
- Application won't start

**Diagnosis:**
```bash
# Test connection from web container
docker-compose -f docker-compose.yml exec web \
    sh -c "cd src && python manage.py dbshell"

# Check active connections
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SELECT count(*) FROM pg_stat_activity;"

# Check max connections
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SHOW max_connections;"
```

**Solutions:**

#### 1. Too Many Connections

**Error:** `FATAL: remaining connection slots are reserved for non-replication superuser connections`

**Solution:**
```bash
# Immediate fix: Kill idle connections
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity
     WHERE state = 'idle' AND state_change < NOW() - INTERVAL '10 minutes';"

# Long-term fix: Increase max_connections in docker-compose.yml
environment:
  POSTGRES_MAX_CONNECTIONS: 500

# Or implement connection pooling (PgBouncer)
# See docker-compose.prod.yml for PgBouncer configuration

# Restart database
docker-compose -f docker-compose.yml restart db
```

#### 2. Wrong Database Credentials

**Error:** `FATAL: password authentication failed for user "obcms_user"`

**Solution:**
```bash
# Verify DATABASE_URL matches database credentials
echo $DATABASE_URL
# Should be: postgres://obcms_user:password@db:5432/obcms_staging

# Verify PostgreSQL user/password
# Check .env file:
POSTGRES_USER=obcms_user
POSTGRES_PASSWORD=[same as in DATABASE_URL]

# If mismatch, fix and restart
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d
```

---

### Problem: Migration Failures

**Symptoms:**
- `python manage.py migrate` fails
- Deployment stuck on migration step
- "IntegrityError" or "OperationalError"

**Diagnosis:**
```bash
# Check migration status
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py showmigrations"

# Look for:
# - [ ] Unapplied migrations
# - [X] Applied migrations
# - Conflict warnings
```

**Solutions:**

#### 1. Conflicting Migrations

**Error:** `Conflicting migrations detected`

**Solution:**
```bash
# Option 1: Use --merge to resolve
python manage.py makemigrations --merge

# Option 2: Manually resolve conflicts
# Edit migration files to fix dependencies

# Apply migrations
python manage.py migrate
```

#### 2. Fake Migration Already Applied Manually

**Error:** Migration already applied but Django doesn't know

**Solution:**
```bash
# Fake the migration
python manage.py migrate app_name migration_name --fake

# Example:
python manage.py migrate common 0015_migrate_monitoring --fake
```

#### 3. Data Integrity Error During Migration

**Error:** `IntegrityError: NOT NULL constraint failed`

**Solution:**
```bash
# Option 1: Fix data before migration
python manage.py shell
>>> from app.models import Model
>>> Model.objects.filter(field__isnull=True).update(field='default')

# Option 2: Make field nullable temporarily
# Edit migration file:
operations = [
    migrations.AlterField(
        model_name='model',
        name='field',
        field=models.CharField(max_length=255, null=True),  # Add null=True
    ),
]

# Apply migration
python manage.py migrate
```

---

### Problem: Slow Database Queries

**Symptoms:**
- Pages take > 2 seconds to load
- Database CPU at 100%
- "Lock wait timeout" errors

**Diagnosis:**
```bash
# Check slow queries (requires pg_stat_statements extension)
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SELECT query, calls, total_time, mean_time
     FROM pg_stat_statements
     ORDER BY mean_time DESC LIMIT 10;"

# Check active queries
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SELECT pid, now() - pg_stat_activity.query_start AS duration, query
     FROM pg_stat_activity
     WHERE state = 'active'
     ORDER BY duration DESC;"
```

**Solutions:**

#### 1. Missing Database Indexes

**Identify missing indexes:**
```sql
-- Find tables with seq scans (should have indexes)
SELECT schemaname, tablename, seq_scan, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan AND seq_scan > 10000
ORDER BY seq_scan DESC;
```

**Add indexes:**
```bash
# Create migration for indexes
python manage.py makemigrations --empty app_name

# Edit migration:
operations = [
    migrations.AddIndex(
        model_name='model',
        index=models.Index(fields=['frequently_queried_field']),
    ),
]

# Apply
python manage.py migrate
```

#### 2. N+1 Query Problem

**Symptom:** Hundreds of queries for single page load

**Solution:**
```python
# In views or serializers, use select_related and prefetch_related

# BEFORE (N+1 queries):
assessments = Assessment.objects.all()
# Each assessment.community triggers separate query

# AFTER (2 queries):
assessments = Assessment.objects.select_related('community').all()

# For many-to-many:
assessments = Assessment.objects.prefetch_related('beneficiaries').all()
```

---

## Redis & Caching Issues

### Problem: Redis Connection Failures

**Symptoms:**
- "Connection refused" errors
- Cache operations fail
- Celery tasks not processing

**Diagnosis:**
```bash
# Check Redis is running
docker-compose -f docker-compose.yml ps redis

# Test connection
docker-compose -f docker-compose.yml exec redis redis-cli ping

# Check Redis logs
docker-compose -f docker-compose.yml logs redis
```

**Solutions:**

#### 1. Redis Container Not Running

```bash
# Restart Redis
docker-compose -f docker-compose.yml restart redis

# If fails to start, check logs
docker-compose -f docker-compose.yml logs redis

# Common: Configuration error
# Fix: Verify redis.conf (if custom config used)
```

#### 2. Wrong Redis URL

```bash
# Check REDIS_URL in .env
echo $REDIS_URL
# Should be: redis://redis:6379/0

# Verify connection string format:
redis://[password@]host:port/db

# Fix and restart
docker-compose -f docker-compose.yml restart web celery
```

---

### Problem: Cache Not Working

**Symptoms:**
- Cache always misses
- Data not persisting in cache
- Stale cache data

**Solutions:**

#### 1. Cache Not Persisting Across Restarts

**Issue:** Redis not configured for persistence

**Solution:**
```yaml
# In docker-compose.yml, add to redis service:
command: redis-server --appendonly yes
volumes:
  - redis_data:/data
```

#### 2. Clear Stale Cache

```bash
# Clear entire cache
docker-compose -f docker-compose.yml exec redis redis-cli FLUSHDB

# Clear specific keys
docker-compose -f docker-compose.yml exec redis redis-cli DEL key_pattern*

# From Django:
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

## Network & Connectivity

### Problem: Cannot Access Application from Browser

**Symptoms:**
- Connection timeout
- "This site can't be reached"
- Works on server but not externally

**Diagnosis:**
```bash
# Test from server (should work)
curl http://localhost:8000/health/

# Test from external (may fail)
curl http://server-ip:8000/health/

# Check if port exposed
docker-compose -f docker-compose.yml ps
# Should show: 0.0.0.0:8000->8000/tcp
```

**Solutions:**

#### 1. Firewall Blocking Port

```bash
# Check firewall status
sudo ufw status

# Allow port 80 and 443
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload
```

#### 2. Docker Not Exposing Port

```yaml
# In docker-compose.yml:
services:
  web:
    ports:
      - "8000:8000"  # Ensure this line exists
```

#### 3. Nginx/Reverse Proxy Not Configured

```bash
# If using Nginx, check config
nginx -t

# Check Nginx is running
systemctl status nginx

# Restart Nginx
sudo systemctl restart nginx
```

---

### Problem: 502 Bad Gateway

**Symptoms:**
- Nginx shows 502 error
- Application shows in browser but doesn't respond

**Diagnosis:**
```bash
# Check if backend is running
docker-compose -f docker-compose.yml ps web

# Test backend directly
curl http://localhost:8000/health/

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

**Solutions:**

#### 1. Backend Not Running

```bash
# Restart backend
docker-compose -f docker-compose.yml restart web

# Check health
curl http://localhost:8000/health/
```

#### 2. Nginx Can't Reach Backend

```yaml
# In Nginx config, ensure correct upstream:
upstream obcms_backend {
    server web:8000;  # Use Docker service name, not localhost
}
```

---

## Performance Issues

### Problem: Slow Page Load Times

**Symptoms:**
- Pages take > 2 seconds to load
- Users report application is slow
- Response times degraded

**Diagnosis:**
```bash
# Measure response time
curl -w "Time: %{time_total}s\n" -o /dev/null -s https://staging.obcms.gov.ph/

# Check Django debug toolbar (if enabled in staging)
# Look for slow queries

# Check resource usage
docker stats
```

**Solutions:**

#### 1. Database Queries Too Slow

See [Slow Database Queries](#problem-slow-database-queries)

#### 2. Not Using Cache

```python
# Add caching to views
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def my_view(request):
    ...

# Or use low-level cache API
from django.core.cache import cache

def get_expensive_data():
    data = cache.get('expensive_data')
    if data is None:
        data = expensive_calculation()
        cache.set('expensive_data', data, timeout=3600)
    return data
```

#### 3. Static Files Not Optimized

```bash
# Ensure static files collected
python manage.py collectstatic --noinput

# Use WhiteNoise for static file serving (already configured)
# Verify STATICFILES_STORAGE in settings

# For production, serve static files via Nginx (faster)
```

---

## Memory & Resource Exhaustion

### Problem: Out of Memory (OOM)

**Symptoms:**
- Container killed by Docker
- "Killed" message in logs
- System becomes unresponsive

**Diagnosis:**
```bash
# Check memory usage
free -h

# Check container memory usage
docker stats

# Check OOM kills in system logs
dmesg | grep -i "out of memory"
```

**Solutions:**

#### 1. Increase Container Memory Limit

```yaml
# In docker-compose.yml:
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G  # Increase as needed
```

#### 2. Find Memory Leak

```bash
# Monitor memory usage over time
watch -n 5 docker stats obcms-web-1

# Check application for memory leaks
# Look for growing memory usage without corresponding load
```

#### 3. Add Swap Space

```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Disk Space Issues

### Problem: Disk Full

**Symptoms:**
- "No space left on device" errors
- Cannot write to database
- Application crashes

**Diagnosis:**
```bash
# Check disk usage
df -h

# Find largest directories
du -sh /* | sort -h

# Check Docker disk usage
docker system df
```

**Solutions:**

#### 1. Clean Docker Images/Volumes

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

#### 2. Clean Application Logs

```bash
# Find large log files
find /var/lib/docker/containers -name "*-json.log" -exec du -h {} \; | sort -h

# Truncate large logs
truncate -s 0 /path/to/large/log/file

# Configure log rotation (see MONITORING_SETUP.md)
```

#### 3. Clean Old Backups

```bash
# Keep only last 7 days of backups
find /opt/backups/obcms_staging/ -name "*.sql.gz" -mtime +7 -delete

# Verify
ls -lt /opt/backups/obcms_staging/
```

---

## SSL/HTTPS Issues

### Problem: SSL Certificate Errors

**Symptoms:**
- "Your connection is not private" browser warning
- Certificate expired
- HTTPS not working

**Diagnosis:**
```bash
# Check certificate expiry
echo | openssl s_client -servername staging.obcms.gov.ph \
    -connect staging.obcms.gov.ph:443 2>/dev/null | \
    openssl x509 -noout -dates
```

**Solutions:**

#### 1. Certificate Expired

```bash
# If using Let's Encrypt with Certbot:
sudo certbot renew

# If using Coolify:
# Coolify handles auto-renewal automatically
# Check Coolify logs for renewal issues
```

#### 2. Certificate Not Installed

```bash
# For Nginx, ensure cert paths correct in config:
ssl_certificate /etc/letsencrypt/live/staging.obcms.gov.ph/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/staging.obcms.gov.ph/privkey.pem;

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

---

### Problem: CSRF Protection Issues

**Symptoms:**
- 403 Forbidden on form submissions
- "CSRF verification failed" errors
- Login fails with 403

**Diagnosis:**
```bash
# Check CSRF_TRUSTED_ORIGINS in .env
grep CSRF_TRUSTED_ORIGINS .env.staging
```

**Solutions:**

#### 1. CSRF_TRUSTED_ORIGINS Not Set

```bash
# In .env, MUST include https:// scheme:
CSRF_TRUSTED_ORIGINS=https://staging.obcms.gov.ph,https://www.staging.obcms.gov.ph

# NOT just domain names:
# WRONG: CSRF_TRUSTED_ORIGINS=staging.obcms.gov.ph
# RIGHT: CSRF_TRUSTED_ORIGINS=https://staging.obcms.gov.ph

# Restart application
docker-compose -f docker-compose.yml restart web
```

#### 2. Proxy Headers Not Forwarded

```nginx
# In Nginx config, ensure headers forwarded:
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;

# In Django settings (already configured):
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
```

---

## Application Errors

### Problem: 500 Internal Server Errors

**Symptoms:**
- Generic "Server Error (500)" page
- No helpful error message
- Logs show exception

**Diagnosis:**
```bash
# Check application logs
docker-compose -f docker-compose.yml logs --tail=100 web | grep ERROR

# Look for stack trace
docker-compose -f docker-compose.yml logs web | grep -A 20 "Traceback"
```

**Solutions:**

#### 1. Unhandled Exception

**Check logs for exception type, fix in code**

Common exceptions:
- `DoesNotExist`: Add .filter().first() instead of .get()
- `MultipleObjectsReturned`: Add unique constraint or use .filter()
- `AttributeError`: Check for None values before accessing attributes

#### 2. Template Errors

**Error:** `TemplateDoesNotExist`

```bash
# Verify template exists
ls src/templates/path/to/template.html

# Check TEMPLATES setting in settings.py
# Ensure template directory in DIRS
```

---

### Problem: Static Files Not Loading

**Symptoms:**
- Page loads but no styling
- 404 errors for CSS/JS in browser console
- Images not displaying

**Diagnosis:**
```bash
# Test static file directly
curl -I https://staging.obcms.gov.ph/static/css/output.css

# Check if static files collected
ls -la src/staticfiles/

# Verify STATIC_ROOT and STATIC_URL in settings
```

**Solutions:**

#### 1. Static Files Not Collected

```bash
# Collect static files
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py collectstatic --noinput"

# Verify files collected
docker-compose -f docker-compose.yml run --rm web \
    ls -la /app/src/staticfiles/css/
```

#### 2. Nginx Not Serving Static Files

```nginx
# In Nginx config:
location /static/ {
    alias /path/to/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

## Build Failures

### Problem: Docker Build Fails

**Symptoms:**
- `docker-compose build` fails
- Deployment stuck on build step
- "ERROR: failed to solve" messages

**Diagnosis:**
```bash
# Build with verbose output
docker-compose -f docker-compose.yml build --no-cache --progress=plain
```

**Solutions:**

#### 1. Tailwind CSS Build Fails

**Error:** `ERROR: Tailwind CSS build failed - output.css not found`

**Solution:**
```bash
# Ensure Node.js dependencies installed locally (for troubleshooting)
npm ci

# Test Tailwind build locally
npm run build:css

# Check output created
ls -la src/static/css/output.css

# If successful, rebuild Docker image
docker-compose -f docker-compose.yml build --no-cache
```

#### 2. Python Dependency Install Fails

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Solution:**
```bash
# Update requirements with exact versions
pip freeze > requirements/base.txt

# Or specify version constraints
# In requirements/base.txt:
Django>=5.1,<5.2
psycopg[binary]>=3.2.0
```

---

## Emergency Procedures

### Complete System Unresponsive

**If all else fails:**

```bash
# 1. Stop all services
docker-compose -f docker-compose.yml down

# 2. Clear Docker cache (nuclear option)
docker system prune -a --volumes

# 3. Reboot server
sudo reboot

# 4. After reboot, start fresh
docker-compose -f docker-compose.yml up -d

# 5. Monitor startup
docker-compose -f docker-compose.yml logs -f
```

---

## Getting Help

### Before Escalating

1. [ ] Check this troubleshooting guide
2. [ ] Review application logs
3. [ ] Search for error message online
4. [ ] Check Django/PostgreSQL/Redis documentation

### When to Escalate

Escalate immediately if:
- Service down > 30 minutes
- Data corruption suspected
- Security breach detected
- Multiple fix attempts failed

### Escalation Path

1. **Level 1:** On-call engineer (self)
2. **Level 2:** Senior engineer (30 min)
3. **Level 3:** Technical manager (1 hour)
4. **Level 4:** CTO/Director (major incidents)

See [MONITORING_SETUP.md](./MONITORING_SETUP.md) for contact information

---

## Related Documents

- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md) - Deployment procedures
- [Post-Deployment Verification](./POST_DEPLOYMENT_VERIFICATION.md) - Verification checks
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md) - Emergency rollback
- [Monitoring Setup](./MONITORING_SETUP.md) - Monitoring and alerts

---

**Version:** 1.0
**Last Updated:** October 2025
**Next Review:** After each major incident
**Owner:** DevOps Team / On-Call Engineers

**Note:** Update this guide after resolving new issues not covered here.
