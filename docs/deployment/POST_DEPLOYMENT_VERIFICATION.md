# OBCMS Post-Deployment Verification

**Purpose:** Comprehensive verification checklist after deployment
**Duration:** 15-20 minutes (staging), 20-30 minutes (production)
**When to run:** Immediately after deployment completes

---

## Table of Contents

1. [Service Health Verification](#service-health-verification)
2. [Database Verification](#database-verification)
3. [Cache & Redis Verification](#cache--redis-verification)
4. [Application Functionality Tests](#application-functionality-tests)
5. [Performance Verification](#performance-verification)
6. [Security Verification](#security-verification)
7. [Monitoring & Logging](#monitoring--logging)
8. [Sample User Workflows](#sample-user-workflows)
9. [Sign-Off](#sign-off)

---

## Service Health Verification

### Container Status

**Time:** 2 minutes

**Check all containers running:**
```bash
# All services should show "Up" and "healthy" status
docker-compose -f docker-compose.yml ps
```

**Expected Output:**
```
NAME                STATUS           PORTS
obcms-web-1         Up (healthy)     0.0.0.0:8000->8000/tcp
obcms-db-1          Up (healthy)     5432/tcp
obcms-redis-1       Up (healthy)     6379/tcp
obcms-celery-1      Up               (no ports exposed)
obcms-celery-beat-1 Up               (no ports exposed)
```

**Verification checklist:**
- [ ] **Web container:** Status "Up (healthy)"
- [ ] **Database container:** Status "Up (healthy)"
- [ ] **Redis container:** Status "Up (healthy)"
- [ ] **Celery worker:** Status "Up"
- [ ] **Celery beat:** Status "Up"

**If any container shows "Restarting" or "Unhealthy":**
- Check logs: `docker-compose logs [service_name]`
- See [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

### Health Endpoints

**Time:** 2 minutes

**Liveness check (basic application running):**
```bash
curl -f https://staging.obcms.gov.ph/health/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "obcms",
  "version": "1.0.0"
}
```

**Readiness check (all dependencies available):**
```bash
curl -f https://staging.obcms.gov.ph/ready/
```

**Expected Response:**
```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "cache": true
  },
  "service": "obcms"
}
```

**Verification checklist:**
- [ ] `/health/` returns HTTP 200
- [ ] `/ready/` returns HTTP 200
- [ ] `status: "healthy"` and `status: "ready"`
- [ ] `database: true` in readiness check
- [ ] `cache: true` in readiness check

**If health checks fail:**
- HTTP 503: Dependencies not ready (wait 30-60 seconds and retry)
- HTTP 500: Application error (check logs immediately)

---

### Response Time Check

**Time:** 1 minute

```bash
# Measure response time for critical endpoints
curl -w "\nTime: %{time_total}s\n" -o /dev/null -s https://staging.obcms.gov.ph/
curl -w "\nTime: %{time_total}s\n" -o /dev/null -s https://staging.obcms.gov.ph/admin/
curl -w "\nTime: %{time_total}s\n" -o /dev/null -s https://staging.obcms.gov.ph/health/
```

**Acceptable response times:**
- **Excellent:** < 300ms
- **Good:** 300-500ms
- **Acceptable:** 500ms-1s
- **Investigate:** > 1s

**Verification checklist:**
- [ ] Homepage loads in < 500ms
- [ ] Admin page loads in < 500ms
- [ ] Health endpoint responds in < 100ms

---

## Database Verification

### Database Connectivity

**Time:** 2 minutes

**Check PostgreSQL is accepting connections:**
```bash
docker-compose -f docker-compose.yml exec db \
    pg_isready -U obcms_user -d obcms_staging
```

**Expected:** `/var/run/postgresql:5432 - accepting connections`

**Test database queries:**
```bash
# Count users (should return number, not error)
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c "SELECT COUNT(*) FROM auth_user;"

# Verify migrations table exists
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c "SELECT COUNT(*) FROM django_migrations;"
```

**Expected:**
- User count: > 0 (at least superuser exists)
- Migration count: ~120 (all migrations applied)

**Verification checklist:**
- [ ] Database accepting connections
- [ ] Can query `auth_user` table
- [ ] Can query `django_migrations` table
- [ ] User count matches pre-deployment count

---

### Migration Status

**Time:** 1 minute

**Check all migrations applied:**
```bash
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py showmigrations"
```

**Expected:** All migrations marked with `[X]`

**Look for:**
- No `[ ]` (unapplied migrations)
- All apps show migrations applied
- No conflicts or errors

**Verification checklist:**
- [ ] All common migrations: `[X]`
- [ ] All communities migrations: `[X]`
- [ ] All mana migrations: `[X]`
- [ ] All coordination migrations: `[X]`
- [ ] No unapplied migrations `[ ]`

---

### Database Size & Growth

**Time:** 1 minute

```bash
# Check database size
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SELECT pg_size_pretty(pg_database_size('obcms_staging'));"

# Check table sizes (top 10)
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SELECT schemaname, tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
     FROM pg_tables
     WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
     ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
     LIMIT 10;"
```

**Expected:**
- Staging: 5-50MB (varies by test data)
- Production: 50MB-500MB (grows over time)

**Verification checklist:**
- [ ] Database size reasonable (not unexpectedly large)
- [ ] Largest table identified (for performance monitoring)

---

## Cache & Redis Verification

### Redis Connectivity

**Time:** 2 minutes

**Test Redis connection:**
```bash
# Ping Redis
docker-compose -f docker-compose.yml exec redis redis-cli ping

# Expected: PONG
```

**Test cache read/write:**
```bash
# Set test key
docker-compose -f docker-compose.yml exec redis \
    redis-cli SET deployment_test "$(date +%Y%m%d_%H%M%S)"

# Get test key
docker-compose -f docker-compose.yml exec redis \
    redis-cli GET deployment_test

# Delete test key
docker-compose -f docker-compose.yml exec redis \
    redis-cli DEL deployment_test
```

**Expected:** Returns timestamp value set above

**Verification checklist:**
- [ ] Redis responds to PING
- [ ] Can SET and GET keys
- [ ] Cache persistence working (if configured)

---

### Django Cache Verification

**Time:** 2 minutes

**Test Django cache backend:**
```bash
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py shell" <<EOF
from django.core.cache import cache
cache.set('deployment_test', 'success', timeout=60)
result = cache.get('deployment_test')
print(f"Cache test: {result}")
cache.delete('deployment_test')
exit()
EOF
```

**Expected Output:** `Cache test: success`

**Verification checklist:**
- [ ] Django can connect to cache backend
- [ ] Can write and read from cache
- [ ] Cache operations don't raise errors

---

### Celery Verification

**Time:** 2 minutes

**Check Celery worker is processing:**
```bash
# View Celery worker logs (should show "ready" state)
docker-compose -f docker-compose.yml logs --tail=20 celery

# Check Celery task queue length (should be low)
docker-compose -f docker-compose.yml exec redis \
    redis-cli LLEN celery
```

**Expected:**
- Celery logs show: `celery@worker ready`
- Queue length: 0-5 tasks (not hundreds)

**Test Celery task execution (optional):**
```python
# In Django shell
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py shell" <<EOF
from celery import current_app
result = current_app.send_task('celery.ping')
print(f"Task ID: {result.id}")
print(f"Task state: {result.state}")
exit()
EOF
```

**Verification checklist:**
- [ ] Celery worker running
- [ ] Celery beat running (scheduled tasks)
- [ ] Task queue not backed up
- [ ] Test task executes successfully (optional)

---

## Application Functionality Tests

### Authentication & Access

**Time:** 3 minutes

**1. Admin login page loads:**
```bash
# Should return HTTP 200
curl -I https://staging.obcms.gov.ph/admin/login/
```

**2. Manual login test:**
- [ ] Navigate to: `https://staging.obcms.gov.ph/admin/login/`
- [ ] Enter superuser credentials
- [ ] Verify successful login
- [ ] Dashboard loads without errors
- [ ] Navigation menu displays

**3. Logout works:**
- [ ] Click logout
- [ ] Redirected to login page
- [ ] Session cleared (cannot access admin without re-login)

**Verification checklist:**
- [ ] Admin login page loads (HTTP 200)
- [ ] Can login with test credentials
- [ ] Dashboard displays correctly
- [ ] Logout clears session

---

### Homepage & Public Pages

**Time:** 2 minutes

**Homepage:**
```bash
# Test homepage loads
curl -f -I https://staging.obcms.gov.ph/

# Check for common errors
curl -s https://staging.obcms.gov.ph/ | grep -i "error\|exception\|500"
```

**Expected:**
- HTTP 200 response
- No error messages in HTML
- Page loads in browser

**Verification checklist:**
- [ ] Homepage loads (HTTP 200)
- [ ] No visible errors or stack traces
- [ ] Static files load (CSS, JS, images)
- [ ] Navigation functional

---

### API Endpoints

**Time:** 2 minutes

**Test DRF API root (if enabled):**
```bash
# API root should be accessible
curl -I https://staging.obcms.gov.ph/api/

# Authentication required for most endpoints
curl -I https://staging.obcms.gov.ph/api/communities/
```

**Expected:**
- API root returns HTTP 200 or 403 (if auth required)
- Browsable API disabled in production (JSON only)

**Verification checklist:**
- [ ] API endpoints respond
- [ ] Authentication enforced (HTTP 403 without credentials)
- [ ] JSON responses returned (not HTML browsable API)

---

### Static Files

**Time:** 2 minutes

**Check static files serving:**
```bash
# CSS file loads
curl -f -I https://staging.obcms.gov.ph/static/css/output.css

# Admin CSS loads
curl -f -I https://staging.obcms.gov.ph/static/admin/css/base.css

# JavaScript loads (if used)
curl -f -I https://staging.obcms.gov.ph/static/js/htmx.min.js
```

**Expected:** All static files return HTTP 200

**Browser verification:**
- [ ] Open homepage in browser
- [ ] Check browser console (F12)
- [ ] No 404 errors for static files
- [ ] Styling applied correctly (Tailwind CSS loaded)

**Verification checklist:**
- [ ] Tailwind CSS loads (output.css)
- [ ] Admin static files load
- [ ] No 404 errors in browser console
- [ ] Page styling renders correctly

---

## Performance Verification

### Response Time Benchmarks

**Time:** 3 minutes

**Run performance benchmarks:**
```bash
#!/bin/bash
# performance-check.sh

DOMAIN="https://staging.obcms.gov.ph"

echo "=== Performance Check ==="

# Homepage
TIME=$(curl -w "%{time_total}" -o /dev/null -s ${DOMAIN}/)
echo "Homepage: ${TIME}s"

# Admin login
TIME=$(curl -w "%{time_total}" -o /dev/null -s ${DOMAIN}/admin/login/)
echo "Admin login: ${TIME}s"

# Health endpoint
TIME=$(curl -w "%{time_total}" -o /dev/null -s ${DOMAIN}/health/)
echo "Health check: ${TIME}s"

# Readiness endpoint
TIME=$(curl -w "%{time_total}" -o /dev/null -s ${DOMAIN}/ready/)
echo "Readiness check: ${TIME}s"
```

**Performance thresholds:**

| Endpoint | Excellent | Good | Acceptable | Investigate |
|----------|-----------|------|------------|-------------|
| Homepage | < 300ms | < 500ms | < 1s | > 1s |
| Admin | < 500ms | < 1s | < 2s | > 2s |
| Health | < 100ms | < 200ms | < 500ms | > 500ms |
| Readiness | < 200ms | < 500ms | < 1s | > 1s |

**Verification checklist:**
- [ ] All endpoints respond within acceptable times
- [ ] No endpoints timing out
- [ ] Response times consistent across multiple requests

---

### Database Query Performance

**Time:** 2 minutes

**Check for slow queries in logs:**
```bash
# Django slow query warnings (if enabled)
docker-compose -f docker-compose.yml logs web | grep "slow query"

# PostgreSQL slow queries (if logging enabled)
docker-compose -f docker-compose.yml exec db \
    psql -U obcms_user -d obcms_staging -c \
    "SELECT query, calls, total_time, mean_time
     FROM pg_stat_statements
     ORDER BY mean_time DESC LIMIT 10;"
```

**Note:** `pg_stat_statements` extension required for query stats

**Verification checklist:**
- [ ] No excessive slow query warnings
- [ ] Most common queries < 100ms average
- [ ] No runaway queries consuming resources

---

### Resource Usage

**Time:** 2 minutes

**Check container resource usage:**
```bash
# Real-time stats (press Ctrl+C to exit)
docker stats --no-stream

# Check specific container
docker stats --no-stream obcms-web-1
```

**Expected resource usage (staging/light load):**

| Service | CPU | Memory | Threshold |
|---------|-----|--------|-----------|
| Web | 0-10% | 200-500MB | Alert if > 1GB |
| Database | 0-5% | 100-300MB | Alert if > 1GB |
| Redis | 0-2% | 10-50MB | Alert if > 500MB |
| Celery | 0-5% | 100-300MB | Alert if > 1GB |

**Verification checklist:**
- [ ] No containers using > 80% CPU consistently
- [ ] Memory usage within expected ranges
- [ ] No containers in restart loop
- [ ] Disk I/O not saturated

---

## Security Verification

### HTTPS & SSL

**Time:** 2 minutes

**Check SSL certificate:**
```bash
# Certificate expiry check
echo | openssl s_client -servername staging.obcms.gov.ph \
    -connect staging.obcms.gov.ph:443 2>/dev/null | \
    openssl x509 -noout -dates

# Check SSL grade (requires external service)
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=staging.obcms.gov.ph
```

**HTTP to HTTPS redirect:**
```bash
# Should redirect to HTTPS
curl -I http://staging.obcms.gov.ph/

# Expected: HTTP 301 or 302, Location: https://...
```

**Verification checklist:**
- [ ] SSL certificate valid (not expired)
- [ ] Certificate expiry > 30 days
- [ ] HTTP redirects to HTTPS (301/302)
- [ ] HTTPS loads without browser warnings
- [ ] No mixed content warnings

---

### Security Headers

**Time:** 2 minutes

**Check security headers present:**
```bash
curl -I https://staging.obcms.gov.ph/ | grep -E "(Strict-Transport|X-Frame|X-Content|Content-Security)"
```

**Expected headers:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src 'self'; ...
```

**Verification checklist:**
- [ ] HSTS header present (after HTTPS confirmed working)
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] Content-Security-Policy configured

---

### CSRF Protection

**Time:** 1 minute

**Verify CSRF protection active:**
```bash
# Attempt POST without CSRF token (should fail)
curl -X POST https://staging.obcms.gov.ph/admin/login/ \
    -d "username=test&password=test"

# Expected: HTTP 403 Forbidden (CSRF verification failed)
```

**Verification checklist:**
- [ ] CSRF protection enforced on POST requests
- [ ] CSRF_TRUSTED_ORIGINS configured correctly
- [ ] Forms include CSRF token in HTML

---

## Monitoring & Logging

### Application Logs

**Time:** 3 minutes

**Check recent logs for errors:**
```bash
# Last 100 lines from web container
docker-compose -f docker-compose.yml logs --tail=100 web

# Filter for errors
docker-compose -f docker-compose.yml logs --tail=200 web | grep -i "error\|exception\|critical"

# Check Celery logs
docker-compose -f docker-compose.yml logs --tail=50 celery
```

**Acceptable log entries:**
- INFO level messages
- Request logs (GET/POST)
- Database connection pool messages

**Investigate immediately:**
- ERROR or CRITICAL level messages
- Stack traces or exceptions
- Database connection failures
- Authentication errors (brute force attempts)

**Verification checklist:**
- [ ] No ERROR level messages (except expected)
- [ ] No unhandled exceptions
- [ ] No database connection errors
- [ ] Log volume reasonable (not flooding)

---

### Error Tracking

**Time:** 2 minutes

**Check for repeated errors:**
```bash
# Count error types in last 500 log lines
docker-compose -f docker-compose.yml logs --tail=500 web | \
    grep ERROR | \
    cut -d' ' -f5- | \
    sort | uniq -c | sort -rn | head -10
```

**Expected:** No repeated error patterns

**Verification checklist:**
- [ ] No single error appearing > 10 times
- [ ] Error patterns identified and documented
- [ ] Critical errors investigated

---

### Monitoring Endpoints

**Time:** 1 minute (if Prometheus/Grafana configured)

**Check monitoring services:**
```bash
# Prometheus metrics endpoint (if enabled)
curl -I https://staging.obcms.gov.ph/metrics/

# Grafana dashboard (if deployed)
curl -I https://monitoring.staging.obcms.gov.ph/
```

**Verification checklist:**
- [ ] Prometheus scraping metrics (if configured)
- [ ] Grafana dashboards accessible (if deployed)
- [ ] Alerts configured and active

---

## Sample User Workflows

### Workflow 1: Admin User Management

**Time:** 3 minutes

**Test adding a user:**
1. [ ] Login to admin: `https://staging.obcms.gov.ph/admin/`
2. [ ] Navigate to: Users → Add user
3. [ ] Create test user: `deployment-test-user`
4. [ ] Set password and save
5. [ ] Verify user appears in user list
6. [ ] Delete test user
7. [ ] Verify deletion successful

**Expected:** All CRUD operations work without errors

---

### Workflow 2: Dashboard Access

**Time:** 2 minutes

**Test main dashboard:**
1. [ ] Login as admin user
2. [ ] Navigate to homepage/dashboard
3. [ ] Verify stat cards display numbers (not errors)
4. [ ] Check navigation menu loads
5. [ ] Click through main menu items
6. [ ] No JavaScript errors in console

**Expected:** Dashboard loads, data displays, navigation works

---

### Workflow 3: MANA Assessment (if deployed)

**Time:** 3 minutes

**Test MANA module:**
1. [ ] Navigate to MANA section
2. [ ] List assessments loads
3. [ ] Click "View" on an assessment
4. [ ] Assessment detail displays
5. [ ] Data renders correctly (demographics, health, etc.)
6. [ ] No server errors (500)

**Expected:** MANA module fully functional

---

### Workflow 4: Email Sending

**Time:** 2 minutes (optional)

**Test email functionality:**
```bash
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py shell" <<EOF
from django.core.mail import send_mail
result = send_mail(
    'Deployment Test',
    'This email confirms SMTP is working.',
    'noreply@staging.obcms.gov.ph',
    ['admin@obcms.gov.ph'],
    fail_silently=False,
)
print(f"Email sent: {result}")
exit()
EOF
```

**Expected:** Email delivered (check inbox)

**Verification checklist:**
- [ ] Email sent without errors
- [ ] Email received in inbox (may take 1-2 minutes)
- [ ] Email formatting correct
- [ ] From address correct

---

## Sign-Off

### Verification Summary

**Total Checks:** Calculate based on checkboxes above

**Scoring:**
- **PASS:** 95%+ checks passed (< 5% failures, all non-critical)
- **CONDITIONAL PASS:** 85-94% (minor issues, fix forward acceptable)
- **FAIL:** < 85% (critical issues, rollback recommended)

**Critical failures (immediate rollback):**
- [ ] Health/readiness checks failing
- [ ] Database connectivity broken
- [ ] Authentication not working
- [ ] Major features completely broken
- [ ] Data corruption detected

**Non-critical failures (fix forward):**
- [ ] Minor UI issues
- [ ] Non-essential features broken
- [ ] Performance slightly degraded
- [ ] Email sending fails (but not critical)

---

### Verification Checklist Summary

Print and complete:

```
POST-DEPLOYMENT VERIFICATION

Environment: [ ] Staging  [ ] Production
Date: _____________  Time: _____________
Version: _____________

SERVICE HEALTH:
[ ] All containers healthy
[ ] Health endpoints respond
[ ] Response times acceptable

DATABASE:
[ ] Database connectivity verified
[ ] All migrations applied
[ ] Data integrity confirmed

CACHE & REDIS:
[ ] Redis responding
[ ] Django cache working
[ ] Celery processing tasks

APPLICATION:
[ ] Authentication working
[ ] Static files loading
[ ] API endpoints responding

PERFORMANCE:
[ ] Response times acceptable
[ ] No slow queries
[ ] Resource usage normal

SECURITY:
[ ] HTTPS working
[ ] Security headers present
[ ] CSRF protection active

USER WORKFLOWS:
[ ] Admin functions working
[ ] Dashboard accessible
[ ] Core features functional

MONITORING:
[ ] Logs reviewed (no critical errors)
[ ] Monitoring active

OVERALL STATUS:
[ ] PASS - Deploy to production / Continue monitoring
[ ] CONDITIONAL - Fix issues, continue monitoring
[ ] FAIL - Rollback immediately

VERIFIED BY:
Name: _______________________
Role: _______________________
Signature: __________________
Date/Time: __________________

ISSUES FOUND:
1. _________________________________
2. _________________________________
3. _________________________________

ACTION ITEMS:
1. _________________________________
2. _________________________________
3. _________________________________
```

---

## Next Steps

### If Verification Passes

**Staging:**
1. [ ] Notify stakeholders: Deployment successful
2. [ ] Begin UAT period (5-7 days)
3. [ ] Monitor for issues
4. [ ] Schedule production deployment

**Production:**
1. [ ] Notify stakeholders: Deployment successful
2. [ ] Monitor for 2-4 hours
3. [ ] Update documentation
4. [ ] Plan next release

---

### If Verification Fails

**Minor Issues (fix forward):**
1. [ ] Document all issues found
2. [ ] Create tickets for fixes
3. [ ] Deploy hotfix if critical
4. [ ] Continue monitoring

**Critical Issues (rollback):**
1. [ ] Activate rollback procedure
2. [ ] See [ROLLBACK_PROCEDURES.md](./ROLLBACK_PROCEDURES.md)
3. [ ] Restore previous version
4. [ ] Investigate root cause

---

## Related Documents

- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md) - Deployment execution steps
- [Staging Deployment Checklist](./STAGING_DEPLOYMENT_CHECKLIST.md) - Pre-deployment checks
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md) - Emergency rollback
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Problem resolution

---

**Version:** 1.0
**Last Updated:** October 2025
**Next Review:** After each deployment
**Owner:** QA Team / DevOps Team
