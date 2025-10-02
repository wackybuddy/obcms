# Production Deployment Guide
## Integrated Calendar, Task Management, and Project Management Systems

**Document Version**: 2.0
**Date**: October 2, 2025
**Status**: Production Ready
**Related**: [Comprehensive Integration Evaluation Plan](../improvements/comprehensive_integration_evaluation_plan.md)

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Steps](#deployment-steps)
3. [Post-Deployment Verification](#post-deployment-verification)
4. [Rollback Procedures](#rollback-procedures)
5. [Monitoring and Alerts](#monitoring-and-alerts)
6. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### 1. Code and Tests

- [ ] **All tests passing**
  ```bash
  cd src
  ../venv/bin/python manage.py test
  ```
  - Expected: All unit tests pass
  - Expected: All integration tests pass
  - Expected: All E2E tests pass

- [ ] **Performance tests completed**
  ```bash
  ../venv/bin/python manage.py test tests.test_performance_load
  ```
  - Calendar aggregation < 2 seconds ✓
  - Task queries < 1 second ✓
  - Portfolio dashboard < 1 second ✓

- [ ] **Code quality checks**
  ```bash
  flake8 --max-line-length=120 --exclude=migrations
  black --check .
  isort --check-only .
  ```

### 2. Database

- [ ] **Backup production database**
  ```bash
  # PostgreSQL
  pg_dump -U postgres -h localhost obcms_production > \
      ~/backups/obcms_$(date +%Y%m%d_%H%M%S).sql

  # SQLite (development)
  cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)
  ```

- [ ] **Verify backup integrity**
  ```bash
  # Check backup file size
  ls -lh ~/backups/obcms_*.sql

  # Test restore to temporary database (optional)
  # createdb obcms_test_restore
  # psql obcms_test_restore < ~/backups/obcms_YYYYMMDD_HHMMSS.sql
  ```

- [ ] **Review pending migrations**
  ```bash
  ../venv/bin/python manage.py showmigrations
  ../venv/bin/python manage.py migrate --plan
  ```

### 3. Configuration

- [ ] **Environment variables configured**
  ```bash
  # Check .env file has all required variables
  grep -E "^(SECRET_KEY|DEBUG|ALLOWED_HOSTS|DATABASE_URL|REDIS_URL)" .env
  ```

  Required variables:
  - `SECRET_KEY` (strong, unique key for production)
  - `DEBUG=False`
  - `ALLOWED_HOSTS` (comma-separated list of domains)
  - `DATABASE_URL` (PostgreSQL connection string)
  - `REDIS_URL` (for Celery and caching)

- [ ] **Static files configuration**
  ```bash
  # Verify STATIC_ROOT is set
  ../venv/bin/python manage.py check --deploy
  ```

- [ ] **Security settings**
  - HTTPS enforced (`SECURE_SSL_REDIRECT=True`)
  - Session cookies secure (`SESSION_COOKIE_SECURE=True`)
  - CSRF cookies secure (`CSRF_COOKIE_SECURE=True`)
  - HSTS enabled (`SECURE_HSTS_SECONDS=31536000`)

### 4. Dependencies

- [ ] **Update dependencies**
  ```bash
  pip install -r requirements/production.txt
  pip list --outdated
  ```

- [ ] **Security audit**
  ```bash
  pip-audit
  ```

### 5. Staging Testing

- [ ] **Deploy to staging environment**
  ```bash
  # Run deployment script in staging
  ./scripts/deploy_staging.sh
  ```

- [ ] **Run smoke tests in staging**
  ```bash
  # Access staging site and verify:
  # - Login works
  # - Calendar loads
  # - Task creation works
  # - PPA creation works
  # - Calendar aggregation includes tasks and PPAs
  ```

- [ ] **Performance test in staging**
  ```bash
  # Run load tests
  ../venv/bin/python manage.py test tests.test_performance_load
  ```

---

## Deployment Steps

### Step 1: Maintenance Mode

Enable maintenance mode to prevent data changes during deployment:

```bash
# Create maintenance mode file
touch /var/www/obcms/MAINTENANCE_MODE

# Or if using custom middleware, set environment variable
export MAINTENANCE_MODE=1
```

**Maintenance Page**: Users will see a friendly "Scheduled Maintenance" message.

### Step 2: Stop Services

```bash
# Stop application services
sudo systemctl stop gunicorn
sudo systemctl stop celery
sudo systemctl stop celery-beat

# Verify services stopped
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celery-beat
```

### Step 3: Pull Latest Code

```bash
cd /var/www/obcms
git fetch origin
git checkout main
git pull origin main

# Verify you're on the correct commit
git log -1 --oneline
```

### Step 4: Update Dependencies

```bash
source ../venv/bin/activate
pip install -r requirements/production.txt
pip freeze > requirements_deployed.txt  # Record what was deployed
```

### Step 5: Run Database Migrations

```bash
cd src

# Review migration plan first
../venv/bin/python manage.py migrate --plan

# Run migrations
../venv/bin/python manage.py migrate

# Verify migrations applied
../venv/bin/python manage.py showmigrations | grep "\[X\]" | wc -l
```

**Critical Migrations** (from integration plan):
- Migration 0013: Calendar models (RecurringEventPattern, CalendarResource, etc.)
- Migration 0014: Task management extension (StaffTask domain FKs)
- Migration 0015: MonitoringEntryTaskAssignment data migration
- Migration 0016: Auto-generation fields
- Migration 0017: Generic FK fixes

### Step 6: Collect Static Files

```bash
# Collect all static files to STATIC_ROOT
../venv/bin/python manage.py collectstatic --noinput

# Verify static files collected
ls -la /var/www/obcms/staticfiles/
```

### Step 7: Clear Caches

```bash
# Clear Django cache
../venv/bin/python manage.py shell << EOF
from django.core.cache import cache
cache.clear()
print("Cache cleared")
EOF

# Clear Redis cache (if using Redis)
redis-cli FLUSHALL

# Clear Nginx cache (if applicable)
sudo rm -rf /var/cache/nginx/*
```

### Step 8: Restart Services

```bash
# Restart application services
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat

# Restart web server
sudo systemctl restart nginx

# Verify all services running
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celery-beat
sudo systemctl status nginx
```

### Step 9: Disable Maintenance Mode

```bash
# Remove maintenance mode file
rm /var/www/obcms/MAINTENANCE_MODE

# Or unset environment variable
unset MAINTENANCE_MODE
```

### Step 10: Verify Deployment

```bash
# Run Django checks
cd /var/www/obcms/src
../venv/bin/python manage.py check --deploy

# Test site is accessible
curl -I https://your-domain.com/

# Check logs for errors
tail -f /var/www/obcms/logs/django.log
tail -f /var/www/obcms/logs/gunicorn.log
tail -f /var/www/obcms/logs/celery.log
```

---

## Post-Deployment Verification

### 1. Smoke Tests

Run these tests to verify core functionality:

#### Test 1: User Authentication
```bash
# Login as admin user
curl -X POST https://your-domain.com/accounts/login/ \
  -d "username=admin&password=your-password" \
  -c cookies.txt

# Verify session created
cat cookies.txt | grep sessionid
```

#### Test 2: Calendar Aggregation
```bash
# Access calendar page
curl -b cookies.txt https://your-domain.com/oobc-management/staff/calendar/

# Check JSON feed
curl -b cookies.txt https://your-domain.com/oobc-management/staff/calendar/feed/json/ \
  | jq '.events | length'

# Expected: Positive number of events
```

#### Test 3: Task Management
```bash
# Create a task
curl -X POST https://your-domain.com/oobc-management/staff/tasks/create/ \
  -b cookies.txt \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -d "title=Test Task&domain=general&status=not_started"

# Verify task created
curl -b cookies.txt https://your-domain.com/oobc-management/staff/tasks/ \
  | grep "Test Task"
```

#### Test 4: Database Integrity
```bash
# Check for orphaned records
../venv/bin/python manage.py shell << EOF
from common.models import StaffTask
from monitoring.models import MonitoringEntry

# Count tasks
task_count = StaffTask.objects.count()
print(f"Total tasks: {task_count}")

# Check for tasks with invalid FKs
invalid_ppas = StaffTask.objects.filter(
    related_ppa__isnull=False
).exclude(
    related_ppa__id__in=MonitoringEntry.objects.values_list('id', flat=True)
).count()

print(f"Invalid PPA references: {invalid_ppas}")
assert invalid_ppas == 0, "Found orphaned task references!"

print("Database integrity check passed ✓")
EOF
```

### 2. Performance Verification

```bash
# Run performance tests
cd /var/www/obcms/src
../venv/bin/python manage.py test tests.test_performance_load.CalendarPerformanceTestCase.test_calendar_aggregation_performance

# Expected output:
# Duration: < 2.0 seconds
# Queries: < 100
# Entries: > 0
```

### 3. Feature Verification Checklist

- [ ] **Calendar System**
  - [ ] Calendar page loads without errors
  - [ ] Events from all modules appear
  - [ ] Task due dates visible on calendar
  - [ ] PPA milestones visible on calendar
  - [ ] Recurring events display correctly
  - [ ] Resource booking works
  - [ ] Module filters work

- [ ] **Task Management**
  - [ ] Task creation form works
  - [ ] Tasks auto-generated for new assessments
  - [ ] Tasks auto-generated for new PPAs
  - [ ] Task assignment works
  - [ ] Task completion updates PPA progress
  - [ ] Domain-specific filtering works

- [ ] **Project Management**
  - [ ] Portfolio dashboard loads
  - [ ] PPA creation works
  - [ ] Budget workflow stages work
  - [ ] Need → PPA linkage works
  - [ ] PPA task integration works

### 4. Integration Verification

Run E2E workflow tests:

```bash
# Full E2E test suite
../venv/bin/python manage.py test tests.test_e2e_integration_workflows

# Expected: All tests pass
```

---

## Rollback Procedures

If deployment fails or critical issues are found, follow these rollback steps:

### Level 1: Quick Rollback (Code Only)

**When to use**: UI bugs, non-critical feature issues

```bash
#!/bin/bash
# rollback_code.sh

set -e

echo "Starting quick rollback (code only)..."

# Enable maintenance mode
touch /var/www/obcms/MAINTENANCE_MODE

# Stop services
sudo systemctl stop gunicorn
sudo systemctl stop celery

# Revert to previous commit
cd /var/www/obcms
git log -5 --oneline  # Review recent commits
git checkout HEAD~1   # Or specific commit hash

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat

# Disable maintenance mode
rm /var/www/obcms/MAINTENANCE_MODE

# Verify
curl -I https://your-domain.com/

echo "Quick rollback complete"
```

### Level 2: Database Rollback (Migrations)

**When to use**: Migration failures, data integrity issues

```bash
#!/bin/bash
# rollback_migrations.sh

set -e

echo "Starting database rollback..."

# Enable maintenance mode
touch /var/www/obcms/MAINTENANCE_MODE

# Stop services
sudo systemctl stop gunicorn
sudo systemctl stop celery
sudo systemctl stop celery-beat

cd /var/www/obcms/src

# List current migrations
../venv/bin/python manage.py showmigrations

# Reverse migrations to specific point
# Replace with actual migration numbers before rollback
../venv/bin/python manage.py migrate common 0012  # Before calendar models
../venv/bin/python manage.py migrate monitoring 0010  # Before task integration

# Verify migration state
../venv/bin/python manage.py showmigrations

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat

# Disable maintenance mode
rm /var/www/obcms/MAINTENANCE_MODE

echo "Database rollback complete"
```

### Level 3: Full System Rollback

**When to use**: Critical failures, data corruption

```bash
#!/bin/bash
# rollback_full.sh

set -e

BACKUP_DATE="20251002_120000"  # Update with actual backup timestamp

echo "Starting full system rollback..."

# Enable maintenance mode
touch /var/www/obcms/MAINTENANCE_MODE

# Stop all services
sudo systemctl stop nginx
sudo systemctl stop gunicorn
sudo systemctl stop celery
sudo systemctl stop celery-beat

# Restore database
echo "Restoring database from backup..."
psql -U postgres -c "DROP DATABASE obcms_production;"
psql -U postgres -c "CREATE DATABASE obcms_production;"
psql -U postgres obcms_production < ~/backups/obcms_${BACKUP_DATE}.sql

# Restore code
cd /var/www/obcms
git reset --hard v1.5.0  # Last stable tag

# Restore static files (if needed)
cp -r ~/backups/static_${BACKUP_DATE}/* /var/www/obcms/staticfiles/

# Clear cache
redis-cli FLUSHALL

# Restart all services
sudo systemctl restart postgresql
sudo systemctl restart redis
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl restart nginx

# Verify system health
cd /var/www/obcms/src
../venv/bin/python manage.py check --deploy

# Disable maintenance mode
rm /var/www/obcms/MAINTENANCE_MODE

echo "Full system rollback complete"
echo "Please verify system functionality"
```

---

## Monitoring and Alerts

### System Health Checks

Create a health check endpoint:

```python
# In common/views/monitoring.py

from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """System health check endpoint."""
    try:
        # Check database
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        db_ok = True
    except:
        db_ok = False

    # Check Redis
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        redis_ok = cache.get('health_check') == 'ok'
    except:
        redis_ok = False

    status = "healthy" if db_ok and redis_ok else "unhealthy"

    return JsonResponse({
        'status': status,
        'database': 'ok' if db_ok else 'error',
        'cache': 'ok' if redis_ok else 'error',
    }, status=200 if status == "healthy" else 503)
```

### Monitoring Checklist

- [ ] **Application logs**
  ```bash
  tail -f /var/www/obcms/logs/django.log
  ```

- [ ] **Error tracking** (if using Sentry)
  - Check for new errors in Sentry dashboard
  - Verify error rate is normal

- [ ] **Performance metrics**
  - Response times < 500ms (95th percentile)
  - Database query time < 100ms average
  - Calendar aggregation < 2 seconds

- [ ] **Resource usage**
  ```bash
  # CPU and memory
  top

  # Disk space
  df -h

  # Database connections
  psql -c "SELECT count(*) FROM pg_stat_activity;"
  ```

### Automated Alerts

Set up monitoring alerts for:

1. **Application errors**
   - 500 errors > 10/minute
   - 404 errors > 100/minute

2. **Performance degradation**
   - Response time > 2 seconds
   - Database query time > 500ms

3. **System resources**
   - CPU > 80% for 5 minutes
   - Memory > 90%
   - Disk space > 85%

4. **Service availability**
   - Gunicorn down
   - Celery down
   - Redis down
   - PostgreSQL down

---

## Troubleshooting

### Common Issues

#### Issue 1: Calendar Not Loading

**Symptoms**: Calendar page blank or shows errors

**Diagnosis**:
```bash
# Check browser console for JavaScript errors
# Check Django logs
tail -100 /var/www/obcms/logs/django.log | grep ERROR

# Test calendar API endpoint
curl -b cookies.txt https://your-domain.com/oobc-management/staff/calendar/feed/json/
```

**Solutions**:
1. Verify FullCalendar library loaded:
   ```bash
   ls -la /var/www/obcms/staticfiles/common/vendor/fullcalendar/
   ```

2. Clear browser cache and Django cache:
   ```bash
   ../venv/bin/python manage.py shell -c "from django.core.cache import cache; cache.clear()"
   ```

3. Check for JavaScript errors in calendar.js

#### Issue 2: Tasks Not Auto-Generating

**Symptoms**: Creating Assessment/PPA doesn't create tasks

**Diagnosis**:
```bash
# Check if signals are connected
../venv/bin/python manage.py shell << EOF
from common.signals import *
import django.db.models.signals as signals

# Check signal handlers
print("Registered signal handlers:")
for handler in signals.post_save.receivers:
    print(f"  {handler}")
EOF
```

**Solutions**:
1. Verify signal handlers in `common/signals.py`
2. Check if task templates exist:
   ```bash
   ../venv/bin/python manage.py shell -c "from common.models import TaskTemplate; print(TaskTemplate.objects.count())"
   ```

3. Test signal manually:
   ```python
   from mana.models import Assessment
   from common.models import StaffTask

   a = Assessment.objects.create(title="Test", methodology="survey")
   tasks = StaffTask.objects.filter(related_assessment=a)
   print(f"Created {tasks.count()} tasks")
   ```

#### Issue 3: PPA Progress Not Updating

**Symptoms**: Completing tasks doesn't update PPA progress

**Diagnosis**:
```bash
# Check signal handler
../venv/bin/python manage.py shell << EOF
from common.models import StaffTask
from monitoring.models import MonitoringEntry

# Find PPA with tasks
ppa = MonitoringEntry.objects.filter(category='oobc_ppa').first()
tasks = StaffTask.objects.filter(related_ppa=ppa)
print(f"PPA: {ppa.title}, Progress: {ppa.progress}, Tasks: {tasks.count()}")

# Complete a task
if tasks.exists():
    task = tasks.first()
    task.status = 'completed'
    task.save()
    ppa.refresh_from_db()
    print(f"After completing task, progress: {ppa.progress}")
EOF
```

**Solutions**:
1. Verify progress update signal in `common/signals.py`
2. Check PPA has related tasks
3. Manually trigger progress recalculation

#### Issue 4: Migration Failures

**Symptoms**: `manage.py migrate` fails

**Diagnosis**:
```bash
# Check migration status
../venv/bin/python manage.py showmigrations

# Check for migration conflicts
../venv/bin/python manage.py makemigrations --check

# Review specific migration
../venv/bin/python manage.py sqlmigrate common 0014
```

**Solutions**:
1. If migration failed partway:
   ```bash
   # Mark as unapplied
   ../venv/bin/python manage.py migrate --fake common 0013

   # Try again
   ../venv/bin/python manage.py migrate
   ```

2. If data migration failed, check for data issues:
   ```bash
   # Verify MonitoringEntryTaskAssignment exists
   ../venv/bin/python manage.py shell -c "from monitoring.models import *; print(MonitoringEntryTaskAssignment.objects.count())"
   ```

3. Restore from backup and retry

---

## Success Criteria

Deployment is successful when:

### Technical Criteria

- ✅ All migrations applied successfully
- ✅ Zero data loss
- ✅ All services running
- ✅ Health check endpoint returns "healthy"
- ✅ No 500 errors in first hour
- ✅ Performance benchmarks met:
  - Calendar aggregation < 2 seconds
  - Task queries < 1 second
  - Page load < 500ms (95th percentile)

### Functional Criteria

- ✅ Users can log in
- ✅ Calendar displays events from all modules
- ✅ Tasks and PPA milestones appear on calendar
- ✅ Creating assessment auto-generates tasks
- ✅ Creating PPA auto-generates tasks
- ✅ Completing tasks updates PPA progress
- ✅ Module filters work correctly
- ✅ Resource booking works
- ✅ Task assignment works

### User Acceptance Criteria

- ✅ Staff can access all features they had before
- ✅ No user complaints of data loss
- ✅ Performance is same or better than before
- ✅ No critical bugs reported in first 24 hours

---

## Post-Deployment Tasks

### Immediate (First Hour)

- [ ] Monitor error logs continuously
- [ ] Watch system resource usage
- [ ] Be available for quick rollback if needed

### First Day

- [ ] Review all error logs
- [ ] Check user feedback
- [ ] Verify all integrations working
- [ ] Document any issues encountered

### First Week

- [ ] Gather user feedback
- [ ] Monitor performance metrics
- [ ] Address any minor issues
- [ ] Plan improvements based on feedback

### First Month

- [ ] Review overall system performance
- [ ] Analyze usage patterns
- [ ] Plan optimizations
- [ ] Update documentation based on learnings

---

## Contact Information

### Support Team

- **Technical Lead**: [Name] - [email]
- **Database Admin**: [Name] - [email]
- **DevOps**: [Name] - [email]

### Emergency Contacts

- **On-Call Engineer**: [Phone]
- **System Admin**: [Phone]

---

## Appendix A: Deployment Script

Full deployment script available at: `scripts/deploy_production.sh`

```bash
#!/bin/bash
# deploy_production.sh

set -e  # Exit on error

echo "================================================================"
echo "OBCMS PRODUCTION DEPLOYMENT - Integrated Systems"
echo "================================================================"
echo ""
echo "This script will deploy:"
echo "  - Integrated Calendar System"
echo "  - Task Management System"
echo "  - Project Management System"
echo ""
read -p "Continue with deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 1
fi

# See scripts/deploy_production.sh for full implementation
```

---

**Document Version**: 2.0
**Last Updated**: October 2, 2025
**Approved By**: [Pending]
**Status**: ✅ Ready for Production Deployment
