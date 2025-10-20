# OBCMS Monitoring & Alerting Setup

**Purpose:** Configure monitoring, dashboards, and alerts for OBCMS
**Environment:** Staging and Production
**Stack:** Prometheus + Grafana (docker-compose.prod.yml)

---

## Table of Contents

1. [Monitoring Architecture](#monitoring-architecture)
2. [Grafana Access & Setup](#grafana-access--setup)
3. [Dashboard Overview](#dashboard-overview)
4. [Alert Configuration](#alert-configuration)
5. [Log Monitoring](#log-monitoring)
6. [Performance Metrics](#performance-metrics)
7. [On-Call Procedures](#on-call-procedures)
8. [Escalation Procedures](#escalation-procedures)

---

## Monitoring Architecture

### Components

OBCMS uses the following monitoring stack (configured in `docker-compose.prod.yml`):

```
┌─────────────────────────────────────────────────┐
│                   Grafana                       │
│         (Dashboards & Visualization)            │
│         http://monitoring.domain.com:3000       │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│                Prometheus                       │
│           (Metrics Collection)                  │
│         http://monitoring.domain.com:9090       │
└──┬────────┬────────┬────────┬──────────────────┘
   │        │        │        │
   ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐
│ Web  │ │  DB  │ │Redis │ │ Celery │
│Exporter Exporter Exporter Exporter
└──────┘ └──────┘ └──────┘ └────────┘
```

### Metrics Exporters

Configured in `docker-compose.prod.yml`:

| Service | Exporter | Port | Metrics |
|---------|----------|------|---------|
| **Django App** | Django Prometheus | 8000/metrics | Request rate, latency, errors |
| **PostgreSQL** | postgres_exporter | 9187 | Connections, queries, locks |
| **Redis** | redis_exporter | 9121 | Memory, commands, keys |
| **System** | node_exporter | 9100 | CPU, memory, disk, network |

---

## Grafana Access & Setup

### Initial Access

**Staging:**
- URL: `https://monitoring.staging.obcms.gov.ph` (or `http://server-ip:3000`)
- Default username: `admin`
- Default password: Set via `GRAFANA_ADMIN_PASSWORD` in `.env`

**Production:**
- URL: `https://monitoring.obcms.gov.ph`
- Username: `admin`
- Password: **Change immediately after first login**

### First Login Setup

**Time:** 10 minutes

1. **Access Grafana:**
   ```bash
   # Get Grafana container URL
   docker-compose -f docker-compose.prod.yml ps grafana

   # Access in browser
   open https://monitoring.staging.obcms.gov.ph:3000
   ```

2. **Login:**
   - Username: `admin`
   - Password: From `GRAFANA_ADMIN_PASSWORD` env var

3. **Change Default Password:**
   - Click gear icon (⚙️) → Preferences
   - Change password → Save
   - **Document new password in password manager**

4. **Verify Data Sources:**
   - Navigate to: Configuration → Data Sources
   - Should see: **Prometheus** (configured automatically)
   - Test connection → Should return "Data source is working"

5. **Import Dashboards:**
   - See [Dashboard Setup](#dashboard-setup) below

---

### Dashboard Setup

**Time:** 15 minutes

**Import pre-configured dashboards:**

#### 1. System Overview Dashboard

```bash
# Dashboard ID: 1860 (Node Exporter Full)
# Navigate to: + → Import
# Enter ID: 1860
# Select Prometheus data source
# Click Import
```

**Metrics shown:**
- CPU usage (per core and total)
- Memory usage (used/free/cached)
- Disk I/O (read/write)
- Network traffic (in/out)

---

#### 2. PostgreSQL Dashboard

```bash
# Dashboard ID: 9628 (PostgreSQL Database)
# Navigate to: + → Import
# Enter ID: 9628
# Select Prometheus data source
# Click Import
```

**Metrics shown:**
- Active connections
- Query duration (p50, p95, p99)
- Database size
- Transaction rate
- Lock contention

---

#### 3. Redis Dashboard

```bash
# Dashboard ID: 763 (Redis Dashboard)
# Navigate to: + → Import
# Enter ID: 763
# Select Prometheus data source
# Click Import
```

**Metrics shown:**
- Memory usage
- Command rate
- Hit rate
- Connected clients
- Keyspace

---

#### 4. OBCMS Application Dashboard

**Create custom dashboard for Django app:**

```bash
# Navigate to: + → Create → Dashboard
# Add Panel → Query

# Panel 1: Request Rate
Metric: rate(django_http_requests_total[5m])
Title: HTTP Requests per Second

# Panel 2: Response Time
Metric: django_http_request_duration_seconds{quantile="0.95"}
Title: 95th Percentile Response Time

# Panel 3: Error Rate
Metric: rate(django_http_requests_total{status=~"5.."}[5m])
Title: Server Errors (5xx) per Second

# Panel 4: Database Query Time
Metric: django_db_query_duration_seconds{quantile="0.95"}
Title: Database Query Duration (p95)

# Save dashboard as: "OBCMS Application Metrics"
```

---

## Dashboard Overview

### Key Dashboards

#### 1. System Overview

**Purpose:** Monitor server health
**Refresh:** 30 seconds
**URL:** `/d/node-exporter/`

**Key panels:**
- **CPU Usage:** Should stay < 70% average
- **Memory Usage:** Should stay < 80% used
- **Disk Usage:** Alert if > 80% full
- **Network I/O:** Monitor for spikes

**Thresholds:**
- ⚠️ Warning: CPU > 70%, Memory > 80%, Disk > 75%
- 🚨 Critical: CPU > 90%, Memory > 95%, Disk > 90%

---

#### 2. PostgreSQL Dashboard

**Purpose:** Monitor database performance
**Refresh:** 1 minute
**URL:** `/d/postgres/`

**Key panels:**
- **Active Connections:** Should be < 80% of max_connections (500)
- **Query Duration:** p95 should be < 100ms
- **Database Size:** Track growth over time
- **Lock Waits:** Should be near zero

**Thresholds:**
- ⚠️ Warning: Connections > 400, Query p95 > 100ms
- 🚨 Critical: Connections > 450, Query p95 > 500ms

---

#### 3. Redis Dashboard

**Purpose:** Monitor cache performance
**Refresh:** 30 seconds
**URL:** `/d/redis/`

**Key panels:**
- **Memory Usage:** Should stay < 80% of maxmemory
- **Hit Rate:** Should be > 80%
- **Command Rate:** Monitor for spikes
- **Evicted Keys:** Should be low (< 100/min)

**Thresholds:**
- ⚠️ Warning: Memory > 80%, Hit rate < 70%
- 🚨 Critical: Memory > 95%, Hit rate < 50%

---

#### 4. Application Metrics

**Purpose:** Monitor Django application
**Refresh:** 1 minute
**URL:** `/d/obcms-app/`

**Key panels:**
- **Request Rate:** Monitor traffic patterns
- **Response Time:** p95 should be < 500ms
- **Error Rate:** Should be < 1% of total requests
- **Celery Queue:** Should stay < 100 tasks

**Thresholds:**
- ⚠️ Warning: Response time > 500ms, Error rate > 1%
- 🚨 Critical: Response time > 2s, Error rate > 5%

---

## Alert Configuration

### Alert Rules Setup

**Time:** 20 minutes

**1. Create Notification Channel:**

```bash
# In Grafana UI:
# Alerting → Notification channels → Add channel

Name: OBCMS Ops Team
Type: Email
Addresses: ops@obcms.gov.ph, oncall@obcms.gov.ph
Send test: ✓
```

**Supported channels:**
- Email (recommended for ops team)
- Slack (for real-time notifications)
- PagerDuty (for on-call rotations)
- Webhook (for custom integrations)

---

### Critical Alerts

**Configure these alerts immediately:**

#### Alert 1: High Error Rate

```yaml
Name: High Error Rate
Condition:
  - Metric: rate(django_http_requests_total{status=~"5.."}[5m])
  - IS ABOVE: 0.05 (5% error rate)
  - FOR: 5 minutes

Message: |
  Server error rate is {{ $value }}% over the last 5 minutes.
  This may indicate application issues.

Notifications: OBCMS Ops Team
Severity: Critical
```

---

#### Alert 2: Database Connection Exhaustion

```yaml
Name: Database Connections High
Condition:
  - Metric: pg_stat_database_numbackends
  - IS ABOVE: 400
  - FOR: 3 minutes

Message: |
  PostgreSQL connections: {{ $value }} (max: 500)
  System may run out of database connections soon.

Notifications: OBCMS Ops Team
Severity: Warning
```

---

#### Alert 3: Disk Space Low

```yaml
Name: Disk Space Low
Condition:
  - Metric: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100
  - IS BELOW: 15 (15% free)
  - FOR: 5 minutes

Message: |
  Disk space: {{ $value }}% free
  Cleanup required urgently to prevent outage.

Notifications: OBCMS Ops Team
Severity: Critical
```

---

#### Alert 4: Container Down

```yaml
Name: Container Down
Condition:
  - Metric: up{job="docker"}
  - IS BELOW: 1
  - FOR: 2 minutes

Message: |
  Container {{ $labels.container }} is down.
  Service may be unavailable.

Notifications: OBCMS Ops Team
Severity: Critical
```

---

#### Alert 5: High Response Time

```yaml
Name: Slow Response Times
Condition:
  - Metric: django_http_request_duration_seconds{quantile="0.95"}
  - IS ABOVE: 2.0 (2 seconds)
  - FOR: 10 minutes

Message: |
  95th percentile response time: {{ $value }}s
  Users experiencing slow page loads.

Notifications: OBCMS Ops Team
Severity: Warning
```

---

#### Alert 6: Celery Queue Backed Up

```yaml
Name: Celery Queue Backlog
Condition:
  - Metric: celery_queue_length
  - IS ABOVE: 500
  - FOR: 15 minutes

Message: |
  Celery queue length: {{ $value }} tasks
  Background tasks not processing fast enough.

Notifications: OBCMS Ops Team
Severity: Warning
```

---

### Alert Severity Levels

| Level | Response Time | Example |
|-------|--------------|---------|
| **Critical** | Immediate (5-15 min) | Service down, high error rate, disk full |
| **Warning** | 1-2 hours | High resource usage, slow responses |
| **Info** | Next business day | Deployment notifications, backups |

---

## Log Monitoring

### Viewing Logs

**Real-time log viewing:**

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f web

# Filter for errors
docker-compose -f docker-compose.prod.yml logs web | grep ERROR

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 web
```

---

### Log Aggregation (Optional)

**For production, consider:**

**Option 1: ELK Stack (Elasticsearch + Logstash + Kibana)**
- Full-text search across all logs
- Log aggregation and analysis
- Retention policies
- Resource intensive (requires dedicated server)

**Option 2: Loki + Grafana**
- Lightweight alternative to ELK
- Integrates with existing Grafana
- Lower resource usage
- Good for moderate log volumes

**Option 3: Cloud Logging**
- AWS CloudWatch Logs
- Google Cloud Logging
- Azure Monitor
- Managed service (additional cost)

**For staging:** Simple Docker logs sufficient
**For production:** Implement Option 1 or 2 when log volume grows

---

### Log Retention

**Configure log rotation:**

```yaml
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
```

**Restart Docker after changes:**
```bash
sudo systemctl restart docker
```

**Result:** Each container keeps max 5 files × 10MB = 50MB logs

---

## Performance Metrics

### Key Performance Indicators (KPIs)

**Application Performance:**

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **Response Time (p95)** | < 500ms | > 1s | > 2s |
| **Error Rate** | < 0.1% | > 1% | > 5% |
| **Uptime** | 99.9% | < 99.5% | < 99% |
| **Database Queries (p95)** | < 50ms | > 100ms | > 500ms |

**Infrastructure Performance:**

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **CPU Usage** | < 50% | > 70% | > 90% |
| **Memory Usage** | < 70% | > 80% | > 95% |
| **Disk Usage** | < 70% | > 80% | > 90% |
| **Network Latency** | < 50ms | > 100ms | > 200ms |

---

### Performance Baselines

**Establish baselines after deployment:**

```bash
# Week 1: Record normal operating metrics
# Track daily for 7 days during normal usage
```

**Example baseline (staging):**
- Average response time: 300ms
- Peak request rate: 50 req/s
- Database connections: 20-50
- Memory usage: 40-60%
- CPU usage: 10-30%

**Use baselines to:**
- Detect performance degradation
- Plan capacity upgrades
- Set appropriate alert thresholds

---

## On-Call Procedures

### On-Call Schedule

**Rotation:** Weekly (Monday 9 AM - Monday 9 AM)

**On-call responsibilities:**
1. Monitor alerts (Grafana, email, Slack)
2. Respond to critical alerts within 15 minutes
3. Escalate to senior engineer if needed
4. Document incidents in incident log

---

### Alert Response Workflow

```
┌─────────────────────┐
│  Alert Received     │
│  (Email/Slack/SMS)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Acknowledge Alert   │
│ (Within 5 minutes)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Assess Severity   │
│  Critical/Warning?  │
└──────┬──────┬───────┘
       │      │
       │      └──────────────┐
       ▼                     ▼
┌──────────────┐      ┌─────────────┐
│   CRITICAL   │      │   WARNING   │
│ Act Now      │      │ Investigate │
└──────┬───────┘      └──────┬──────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌─────────────┐
│ Follow       │      │ Log Issue   │
│ Runbook      │      │ Fix in 1-2h │
└──────┬───────┘      └──────┬──────┘
       │                     │
       └──────────┬──────────┘
                  ▼
         ┌────────────────┐
         │ Document       │
         │ Incident       │
         └────────────────┘
```

---

### Incident Response Checklist

**When alert fires:**

1. **Acknowledge (1 minute):**
   - [ ] Open Grafana dashboard
   - [ ] Identify affected service
   - [ ] Check severity level

2. **Assess (2-3 minutes):**
   - [ ] Is service down or degraded?
   - [ ] How many users affected?
   - [ ] Is data at risk?

3. **Respond (varies):**

   **Critical alerts:**
   - [ ] Notify team immediately (Slack/call)
   - [ ] Begin troubleshooting (see runbooks)
   - [ ] Consider rollback if recent deployment

   **Warning alerts:**
   - [ ] Log issue in incident tracker
   - [ ] Investigate root cause
   - [ ] Plan remediation

4. **Communicate:**
   - [ ] Update status page (if user-facing)
   - [ ] Notify stakeholders
   - [ ] Set expectations for resolution time

5. **Resolve:**
   - [ ] Fix issue or rollback
   - [ ] Verify metrics return to normal
   - [ ] Monitor for 30 minutes

6. **Document:**
   - [ ] Write incident report
   - [ ] Update runbooks if needed
   - [ ] Schedule post-mortem (for major incidents)

---

## Escalation Procedures

### Escalation Levels

**Level 1: On-Call Engineer (Primary Response)**
- First responder to all alerts
- Handles routine issues (known problems, documented fixes)
- Response time: 5-15 minutes

**Level 2: Senior Engineer (Subject Matter Expert)**
- Escalate if issue not resolved in 30 minutes
- Handles complex technical issues
- Response time: 15-30 minutes

**Level 3: Technical Manager (Decision Authority)**
- Escalate for major outages or rollback decisions
- Approves emergency changes
- Response time: 30-60 minutes

**Level 4: CTO/Director (Executive)**
- Major incidents affecting all users
- Security breaches
- Data loss events
- Response time: 1-2 hours

---

### Escalation Criteria

**Escalate to Level 2 if:**
- Issue not resolved within 30 minutes
- Unfamiliar error or system behavior
- Multiple services affected
- Requires code changes or deployment

**Escalate to Level 3 if:**
- Service down > 1 hour
- Database corruption suspected
- Rollback decision needed
- Multiple failed fix attempts

**Escalate to Level 4 if:**
- Total system outage > 2 hours
- Data breach or security incident
- Data loss affecting users
- Legal or compliance implications

---

### Contact Information

**Emergency Contacts:**

| Role | Name | Phone | Email | Backup |
|------|------|-------|-------|--------|
| **On-Call (L1)** | [Rotate weekly] | +63-XXX-XXX-XXXX | oncall@obcms.gov.ph | - |
| **Senior Eng (L2)** | [Name] | +63-XXX-XXX-XXXX | senior@obcms.gov.ph | [Backup name] |
| **Tech Manager (L3)** | [Name] | +63-XXX-XXX-XXXX | techmgr@obcms.gov.ph | [Backup name] |
| **CTO (L4)** | [Name] | +63-XXX-XXX-XXXX | cto@obcms.gov.ph | - |

**Update this table with actual contact information**

---

## Monitoring Best Practices

### Daily Monitoring Tasks

**Every morning (10 minutes):**
- [ ] Check Grafana dashboards (all green?)
- [ ] Review overnight alerts (any incidents?)
- [ ] Check error logs (any new error patterns?)
- [ ] Verify backups completed successfully

### Weekly Monitoring Tasks

**Every Monday (30 minutes):**
- [ ] Review performance trends (week over week)
- [ ] Check disk space usage (cleanup if needed)
- [ ] Review alert history (any patterns?)
- [ ] Update on-call schedule

### Monthly Monitoring Tasks

**First of each month (1-2 hours):**
- [ ] Review SLA compliance (uptime, performance)
- [ ] Analyze capacity trends (CPU, memory, disk)
- [ ] Update alert thresholds (based on baselines)
- [ ] Archive old logs (retention policy)
- [ ] Test monitoring system (simulate alerts)

---

## Troubleshooting Monitoring Issues

### Grafana Not Loading

```bash
# Check Grafana container
docker-compose -f docker-compose.prod.yml ps grafana

# Check logs
docker-compose -f docker-compose.prod.yml logs grafana

# Restart Grafana
docker-compose -f docker-compose.prod.yml restart grafana
```

---

### Prometheus Not Scraping Metrics

```bash
# Check Prometheus targets
# Navigate to: http://server-ip:9090/targets
# All targets should show "UP" status

# If target is "DOWN", check exporter:
docker-compose -f docker-compose.prod.yml logs postgres-exporter
```

---

### Missing Metrics

**Verify exporters running:**
```bash
docker-compose -f docker-compose.prod.yml ps | grep exporter
```

**Check if metrics endpoint responding:**
```bash
# Node exporter
curl http://localhost:9100/metrics

# PostgreSQL exporter
curl http://localhost:9187/metrics

# Redis exporter
curl http://localhost:9121/metrics
```

---

## Related Documents

- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md) - Deployment procedures
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md) - Emergency rollback
- [Post-Deployment Verification](./POST_DEPLOYMENT_VERIFICATION.md) - After deployment checks

---

**Version:** 1.0
**Last Updated:** October 2025
**Next Review:** Quarterly
**Owner:** DevOps Team / On-Call Engineers
