# OBCMS Deployment Runbook

**Environment:** Staging and Production
**Purpose:** Step-by-step deployment execution guide
**Estimated Total Time:** 12-15 minutes (staging), 15-20 minutes (production)

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Phase](#pre-deployment-phase)
3. [Deployment Execution](#deployment-execution)
4. [Post-Deployment Verification](#post-deployment-verification)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)

---

## Overview

### Deployment Strategy

**Approach:** Blue-Green deployment with Docker containers
- **Staging First:** Always deploy to staging environment first
- **User Acceptance Testing:** 5-7 days minimum in staging
- **Production Deployment:** Only after staging verification

### Deployment Windows

**Staging:**
- Anytime during business hours
- No user notification required

**Production:**
- **Preferred:** Saturday 2:00 AM - 4:00 AM PHT (low traffic)
- **Alternative:** Wednesday 11:00 PM - 1:00 AM PHT
- **User notification:** 48 hours advance notice

### Team Roles

| Role | Responsibilities | Required for Deployment |
|------|------------------|-------------------------|
| **Deployment Lead** | Execute deployment, coordinate team | REQUIRED |
| **Database Admin** | Monitor database, handle migrations | REQUIRED |
| **QA Engineer** | Execute smoke tests, verify functionality | REQUIRED |
| **Technical Manager** | Approve deployment, escalation point | REQUIRED |
| **Support Team** | Monitor user reports, handle issues | On-call |

---

## Pre-Deployment Phase

**Duration:** 30-45 minutes (done before deployment window)

### Step 1: Verify Readiness Checklist

**Time:** 5 minutes

- [ ] **Staging deployment checklist** completed (80/83 points minimum)
- [ ] **All tests passing** on deployment branch
- [ ] **Database backup** created (within last 4 hours)
- [ ] **Rollback plan** accessible and reviewed

**Verification:**
```bash
# Check test results
pytest -v --tb=short

# Verify backup exists
ls -lh /opt/backups/obcms_staging/ | head -3
```

---

### Step 2: Team Communication

**Time:** 5 minutes

- [ ] **Deployment channel active:** Slack/Teams channel open
- [ ] **Team members online:** All required roles available
- [ ] **User notification sent:** (Production only) 2 hours before window

**Communication Template:**
```
DEPLOYMENT STARTING
Environment: [Staging/Production]
Time: [Current time]
Lead: [Name]
Expected Duration: 15 minutes
Rollback available: Yes
```

---

### Step 3: Create Pre-Deployment Snapshot

**Time:** 5 minutes

**Database Snapshot:**
```bash
# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ENV="staging"  # or "production"

docker-compose -f docker-compose.yml exec db \
    pg_dump -U obcms_user obcms_${ENV} | \
    gzip > /opt/backups/obcms_${ENV}/pre_deploy_${TIMESTAMP}.sql.gz

# Verify backup created
ls -lh /opt/backups/obcms_${ENV}/pre_deploy_${TIMESTAMP}.sql.gz
```

**Expected:** Backup file size > 1MB (contains data)

**Container State:**
```bash
# Save current running containers list
docker-compose -f docker-compose.yml ps > /tmp/pre_deploy_state.txt

# Save current image IDs
docker images | grep obcms >> /tmp/pre_deploy_state.txt
```

---

### Step 4: Verify Environment Configuration

**Time:** 3 minutes

```bash
# Check environment file exists
ls -l .env.staging  # or .env.production

# Verify critical variables (without exposing values)
grep -E "^(DJANGO_SETTINGS_MODULE|DEBUG|ALLOWED_HOSTS|DATABASE_URL)" .env.staging | \
    sed 's/=.*/=***/' | head -10

# Verify SECRET_KEY is not development key
grep SECRET_KEY .env.staging | grep -v "django-insecure" && \
    echo "OK: Production SECRET_KEY" || \
    echo "ERROR: Using development SECRET_KEY"
```

**Expected:** All critical variables present, SECRET_KEY is production value

---

## Deployment Execution

**Duration:** 8-12 minutes

### Phase 1: Pull Latest Code

**Time:** 2 minutes

**For Git-based deployment (Coolify/Manual):**
```bash
# Navigate to application directory
cd /opt/obcms

# Fetch latest changes
git fetch origin

# Checkout deployment branch/tag
git checkout v1.2.0-staging  # Use specific tag or branch

# Verify commit
git log --oneline -1
```

**Expected:** Commit hash matches intended deployment

**For Docker image deployment:**
```bash
# Pull latest image
docker pull your-registry/obcms:v1.2.0-staging
```

---

### Phase 2: Build Application Containers

**Time:** 3-5 minutes

**Build Docker images:**
```bash
# Build production images
docker-compose -f docker-compose.yml build --no-cache web celery

# Verify images built successfully
docker images | grep obcms
```

**Expected Output:**
```
obcms_web         latest    [IMAGE_ID]    About a minute ago    500MB
obcms_celery      latest    [IMAGE_ID]    About a minute ago    500MB
```

**Note:** Build time varies based on changes (CSS rebuild, dependency updates)

---

### Phase 3: Run Database Migrations

**Time:** 2-5 minutes

**CRITICAL:** Migrations run BEFORE restarting application containers

```bash
# Run migration container (docker-compose.prod.yml includes this step)
# For manual deployments:
docker-compose -f docker-compose.yml run --rm migrate

# Or run migrations manually:
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py migrate --noinput"
```

**Monitor output:**
- Look for: `Running migrations:` followed by applied migrations
- Expected: `No migrations to apply.` or list of applied migrations
- **Stop if:** Any migration fails with error

**Verify migrations:**
```bash
# Check migration status
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py showmigrations"
```

**Expected:** All migrations marked with `[X]`

---

### Phase 4: Collect Static Files

**Time:** 1 minute

**Already done in migrate step, but verify:**
```bash
# Manual collection if needed
docker-compose -f docker-compose.yml run --rm web \
    sh -c "cd src && python manage.py collectstatic --noinput"
```

**Expected:**
```
X static files copied to '/app/src/staticfiles'
```

---

### Phase 5: Restart Application Services

**Time:** 2 minutes

**Rolling restart strategy:**

```bash
# Restart services with downtime minimized
# Using docker-compose recreate (blue-green deployment)
docker-compose -f docker-compose.yml up -d --force-recreate web celery celery-beat

# Monitor container startup
docker-compose -f docker-compose.yml logs -f web
```

**Watch for:**
- ✅ `Booting worker with pid: XXXX`
- ✅ `Listening at: http://0.0.0.0:8000`
- ❌ Any Python exceptions or errors

**For Coolify:**
- Click "Deploy" button in Coolify dashboard
- Monitor deployment logs in real-time
- Wait for "Deployment successful" message

---

### Phase 6: Verify Service Health

**Time:** 1 minute

**Check all containers running:**
```bash
# All services should be "Up" and "healthy"
docker-compose -f docker-compose.yml ps
```

**Expected Output:**
```
NAME            STATUS           PORTS
obcms-web-1     Up (healthy)     0.0.0.0:8000->8000/tcp
obcms-db-1      Up (healthy)     5432/tcp
obcms-redis-1   Up (healthy)     6379/tcp
obcms-celery-1  Up               (no ports)
```

**Check health endpoints:**
```bash
# Liveness check
curl -f http://localhost:8000/health/ || echo "FAILED"

# Readiness check (verifies database and Redis)
curl -f http://localhost:8000/ready/ || echo "FAILED"

# Expected: {"status":"healthy"} and {"status":"ready"}
```

**If health checks fail:** Proceed to [Troubleshooting](#troubleshooting)

---

## Post-Deployment Verification

**Duration:** 5-10 minutes

### Critical Smoke Tests

**Time:** 5 minutes

See [POST_DEPLOYMENT_VERIFICATION.md](./POST_DEPLOYMENT_VERIFICATION.md) for complete checklist.

**Quick smoke test:**
```bash
#!/bin/bash
# smoke-test.sh

DOMAIN="https://staging.obcms.gov.ph"  # Change for production

echo "=== OBCMS Smoke Test ==="

# 1. Homepage loads
echo "Testing homepage..."
curl -f -s -o /dev/null -w "%{http_code}" ${DOMAIN}/ || echo "FAILED"

# 2. Admin login page loads
echo "Testing admin..."
curl -f -s -o /dev/null -w "%{http_code}" ${DOMAIN}/admin/login/ || echo "FAILED"

# 3. API health check
echo "Testing API health..."
curl -f ${DOMAIN}/health/ | grep "healthy" || echo "FAILED"

# 4. Database connectivity
echo "Testing database..."
curl -f ${DOMAIN}/ready/ | grep "ready" || echo "FAILED"

echo "=== Smoke Test Complete ==="
```

**Run smoke test:**
```bash
bash smoke-test.sh
```

**Expected:** All tests return HTTP 200 or expected JSON

---

### Manual User Workflow Test

**Time:** 5 minutes

**Critical user paths:**

1. **Login Flow**
   - [ ] Navigate to admin login: `https://domain/admin/`
   - [ ] Enter credentials for test user
   - [ ] Verify successful login to dashboard
   - [ ] Logout

2. **Dashboard Access**
   - [ ] Homepage loads without errors
   - [ ] Navigation menu displays correctly
   - [ ] Stat cards show data

3. **MANA Module** (if deployed)
   - [ ] List assessments loads
   - [ ] Can view assessment detail
   - [ ] No JavaScript errors in console

**If any test fails:** Document issue and decide: Fix forward or rollback

---

### Performance Verification

**Time:** 2 minutes

```bash
# Check response times (should be < 500ms)
curl -w "Time: %{time_total}s\n" -o /dev/null -s https://staging.obcms.gov.ph/

# Check database query counts (should be optimized)
# Monitor application logs for slow queries
docker-compose -f docker-compose.yml logs web | grep "slow query"
```

**Thresholds:**
- **Good:** < 500ms response time
- **Acceptable:** 500ms - 1s
- **Investigate:** > 1s

---

### Log Verification

**Time:** 2 minutes

```bash
# Check for errors in last 100 log lines
docker-compose -f docker-compose.yml logs --tail=100 web | grep -i error

# Check Celery workers
docker-compose -f docker-compose.yml logs --tail=50 celery | grep -i error

# Expected: No critical errors
```

**Acceptable logs:**
- INFO level messages
- Database connection pooling messages
- Static file serving (if DEBUG=True in staging)

**Investigate:**
- ERROR level messages
- Stack traces
- Database connection failures

---

## Post-Deployment Actions

### Update Documentation

**Time:** 5 minutes

- [ ] **Tag deployment in git:** `git tag production-2025-10-20`
- [ ] **Update changelog:** Document deployed changes
- [ ] **Record deployment:** Add to deployment log

**Deployment log entry:**
```
Date: 2025-10-20 02:30 PHT
Environment: Production
Version: v1.2.0
Lead: [Name]
Duration: 14 minutes
Issues: None
Rollback: Not required
Status: Success
```

---

### Communication

**Time:** 2 minutes

**Notify stakeholders:**
```
DEPLOYMENT COMPLETE ✓
Environment: [Staging/Production]
Version: v1.2.0
Completed: [Time]
Duration: 14 minutes
Status: All systems operational
Issues: None

Deployed Changes:
- [Feature 1]
- [Feature 2]
- [Bug fix 1]

Next Steps:
- Monitoring for 2 hours
- UAT to begin [date] (staging only)
```

---

### Monitoring Period

**Duration:** 2 hours (minimum)

**Monitoring checklist:**

- [ ] **Error rates:** Check application logs every 15 minutes
- [ ] **Response times:** Monitor average response time
- [ ] **User reports:** Check support channels for issues
- [ ] **Database performance:** Watch for slow queries
- [ ] **Celery tasks:** Verify background tasks processing

**Monitoring commands:**
```bash
# Watch logs in real-time
docker-compose -f docker-compose.yml logs -f --tail=50 web

# Check Celery task queue
docker-compose -f docker-compose.yml exec redis redis-cli LLEN celery

# Monitor resource usage
docker stats
```

**Escalation criteria:**
- Error rate > 5% of requests
- Response time > 2 seconds sustained
- Database connection failures
- Critical feature broken

**If escalation criteria met:** Activate [Rollback Procedures](#rollback-procedures)

---

## Troubleshooting

### Container Startup Failures

**Symptom:** `docker-compose ps` shows containers not healthy or restarting

**Diagnosis:**
```bash
# Check container logs
docker-compose -f docker-compose.yml logs web

# Check specific container
docker logs obcms-web-1
```

**Common causes:**

1. **Environment variable missing:**
   - Look for: `KeyError: 'ALLOWED_HOSTS'`
   - Fix: Add missing variable to `.env`

2. **Database connection failure:**
   - Look for: `could not connect to server`
   - Fix: Check `DATABASE_URL`, verify PostgreSQL running

3. **Migration failure:**
   - Look for: `django.db.migrations.exceptions.MigrationSchemaMissing`
   - Fix: Run `python manage.py migrate` manually

**Resolution:**
```bash
# Fix environment variables
nano .env.staging

# Restart services
docker-compose -f docker-compose.yml restart web
```

---

### Health Check Failures

**Symptom:** `/health/` or `/ready/` endpoints return 503 or timeout

**Diagnosis:**
```bash
# Check readiness endpoint details
curl -v https://staging.obcms.gov.ph/ready/

# Check container health status
docker inspect obcms-web-1 | grep -A 10 Health
```

**Common causes:**

1. **Database not ready:**
   - Check: `docker-compose ps db` shows "unhealthy"
   - Fix: Wait for database initialization (30-60 seconds)

2. **Redis not ready:**
   - Check: `docker-compose exec redis redis-cli ping` fails
   - Fix: Restart Redis: `docker-compose restart redis`

---

### Migration Failures

**Symptom:** Migration command fails with error

**Diagnosis:**
```bash
# Check migration status
python manage.py showmigrations

# Check specific app migrations
python manage.py showmigrations common
```

**Common causes:**

1. **Conflicting migrations:**
   - Look for: `Conflicting migrations detected`
   - Fix: Resolve conflicts using `--merge`

2. **Data integrity errors:**
   - Look for: `IntegrityError`, `NOT NULL constraint failed`
   - Fix: Correct data before migration, or use data migration

**Resolution:**
```bash
# Fake migration if already applied manually
python manage.py migrate app_name migration_name --fake

# Or rollback to previous migration
python manage.py migrate app_name previous_migration_name
```

---

### Performance Degradation

**Symptom:** Slow response times (> 2 seconds)

**Diagnosis:**
```bash
# Check database query performance
docker-compose -f docker-compose.yml logs web | grep "query"

# Check resource usage
docker stats obcms-web-1
```

**Common causes:**

1. **Missing database indexes:** Add indexes for frequently queried fields
2. **N+1 queries:** Use `select_related()` and `prefetch_related()`
3. **Insufficient resources:** Scale up container resources

---

## Rollback Procedures

**See:** [ROLLBACK_PROCEDURES.md](./ROLLBACK_PROCEDURES.md) for complete guide

### Quick Rollback (5-10 minutes)

**Decision point:** Rollback if critical issues occur within 2 hours of deployment

**Fastest method - Docker image rollback:**

```bash
# 1. Stop current containers
docker-compose -f docker-compose.yml down

# 2. Checkout previous stable tag
git checkout v1.1.0-staging  # Previous version tag

# 3. Restart with previous configuration
docker-compose -f docker-compose.yml up -d

# 4. Verify health
curl http://localhost:8000/health/

# Total time: ~5 minutes
```

**For Coolify:**
1. Go to Deployments tab
2. Find previous successful deployment
3. Click "Redeploy"
4. Monitor logs for successful startup

**Database rollback (use only if migrations caused issues):**

```bash
# Restore database from pre-deployment backup
TIMESTAMP="20251020_023000"  # From pre-deployment snapshot

gunzip < /opt/backups/obcms_staging/pre_deploy_${TIMESTAMP}.sql.gz | \
    docker-compose -f docker-compose.yml exec -T db \
    psql -U obcms_user obcms_staging
```

**Verification after rollback:**
- [ ] All containers healthy: `docker-compose ps`
- [ ] Health check passes: `curl /health/`
- [ ] Login works
- [ ] Critical features functional

---

## Deployment Checklist (Print This)

**Pre-Deployment:**
```
[ ] Staging checklist completed (80+ points)
[ ] Tests passing (99%+)
[ ] Database backup created
[ ] Team communication sent
[ ] Rollback plan reviewed
```

**Deployment Execution:**
```
[ ] Pull latest code (2 min)
[ ] Build containers (3-5 min)
[ ] Run migrations (2-5 min)
[ ] Collect static files (1 min)
[ ] Restart services (2 min)
[ ] Verify health checks (1 min)
```

**Post-Deployment:**
```
[ ] Smoke tests pass (5 min)
[ ] User workflow verified (5 min)
[ ] Performance acceptable (2 min)
[ ] Logs reviewed (2 min)
[ ] Stakeholders notified
[ ] Monitoring active (2 hours)
```

**Sign-Off:**
```
Deployed by: _______________________
Date/Time: ________________________
Duration: ____ minutes
Status: [  ] Success  [  ] Rollback
Issues: ___________________________
```

---

## Deployment Time Breakdown

**Staging Deployment:**
| Phase | Duration | Cumulative |
|-------|----------|------------|
| Pre-deployment snapshot | 5 min | 5 min |
| Pull code | 2 min | 7 min |
| Build containers | 3-5 min | 10-12 min |
| Run migrations | 2-5 min | 12-17 min |
| Restart services | 2 min | 14-19 min |
| Health verification | 1 min | 15-20 min |
| **Total (Execution)** | **10-15 min** | **15-20 min** |
| Smoke tests | 5 min | 20-25 min |
| **Total (with verification)** | **15-20 min** | **20-25 min** |

**Production Deployment:**
- Add 3-5 minutes for additional verification
- **Total:** 18-25 minutes (including all checks)

**Rollback:**
- Docker rollback: 5-10 minutes
- Database rollback: 30-45 minutes

---

## Quick Reference Commands

### Health Checks
```bash
# Application health
curl https://staging.obcms.gov.ph/health/

# Readiness (database + Redis)
curl https://staging.obcms.gov.ph/ready/

# Container status
docker-compose -f docker-compose.yml ps

# View logs
docker-compose -f docker-compose.yml logs -f web
```

### Emergency Commands
```bash
# Stop all services
docker-compose -f docker-compose.yml down

# Restart specific service
docker-compose -f docker-compose.yml restart web

# View recent errors
docker-compose -f docker-compose.yml logs --tail=100 web | grep ERROR
```

---

## Related Documents

- [Staging Deployment Checklist](./STAGING_DEPLOYMENT_CHECKLIST.md) - Pre-deployment verification
- [Post-Deployment Verification](./POST_DEPLOYMENT_VERIFICATION.md) - After deployment checks
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md) - Emergency rollback steps
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Detailed problem resolution

---

**Version:** 1.0
**Last Updated:** October 2025
**Next Review:** After each deployment
**Owner:** DevOps Team
