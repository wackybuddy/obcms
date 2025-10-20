# OBCMS Grafana & Prometheus Monitoring - Complete Setup Guide

This guide walks through the complete setup of Grafana dashboards and Prometheus alerting for OBCMS.

## Prerequisites

- Docker and Docker Compose installed
- OBCMS running with Prometheus exporters configured
- Basic understanding of Prometheus and Grafana

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         OBCMS Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Django  │  │PostgreSQL│  │  Redis   │  │  Celery  │   │
│  │   App    │  │    DB    │  │  Cache   │  │ Workers  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │           │
│       │  Metrics    │  Metrics    │  Metrics    │  Metrics  │
│       ▼             ▼             ▼             ▼           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Prometheus Server                         │   │
│  │  - Scrapes metrics every 15s                        │   │
│  │  - Evaluates alert rules every 30s                  │   │
│  │  - Stores time-series data                          │   │
│  └────────────┬─────────────────────┬──────────────────┘   │
│               │                     │                       │
│               ▼                     ▼                       │
│  ┌────────────────────┐  ┌────────────────────┐           │
│  │   Alertmanager     │  │      Grafana       │           │
│  │  - Routes alerts   │  │  - Visualizations  │           │
│  │  - Sends notifs    │  │  - Dashboards      │           │
│  └────────────────────┘  └────────────────────┘           │
│               │                                             │
│               ▼                                             │
│  ┌────────────────────────────────┐                        │
│  │  Notification Channels         │                        │
│  │  - Email, Slack, PagerDuty     │                        │
│  └────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Update Docker Compose Configuration

Add Grafana and Alertmanager to your `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # ... existing services ...

  # Prometheus (if not already added)
  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: obcms_prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./config/prometheus/alert-rules.yml:/etc/prometheus/alert-rules.yml:ro
      - prometheus_data:/prometheus
    networks:
      - obcms_network
    depends_on:
      - alertmanager

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: obcms_alertmanager
    restart: unless-stopped
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    volumes:
      - ./config/prometheus/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    networks:
      - obcms_network
    environment:
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
      - SLACK_WEBHOOK_URL_CRITICAL=${SLACK_WEBHOOK_URL_CRITICAL}
      - PAGERDUTY_SERVICE_KEY=${PAGERDUTY_SERVICE_KEY}

  # Grafana
  grafana:
    image: grafana/grafana:10.2.0
    container_name: obcms_grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      # Security
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_SECURITY_SECRET_KEY=${GRAFANA_SECRET_KEY}

      # Server
      - GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL:-http://localhost:3000}
      - GF_SERVER_DOMAIN=${GRAFANA_DOMAIN:-localhost}

      # Database (for Grafana internal data)
      - GF_DATABASE_TYPE=postgres
      - GF_DATABASE_HOST=postgres:5432
      - GF_DATABASE_NAME=${GRAFANA_DB_NAME:-grafana}
      - GF_DATABASE_USER=${GRAFANA_DB_USER:-grafana}
      - GF_DATABASE_PASSWORD=${GRAFANA_DB_PASSWORD}

      # Auth
      - GF_AUTH_ANONYMOUS_ENABLED=false
      - GF_AUTH_DISABLE_LOGIN_FORM=false

      # Plugins
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource,grafana-piechart-panel

      # SMTP (for email alerts)
      - GF_SMTP_ENABLED=true
      - GF_SMTP_HOST=${SMTP_HOST:-smtp.gmail.com:587}
      - GF_SMTP_USER=${SMTP_USER}
      - GF_SMTP_PASSWORD=${SMTP_PASSWORD}
      - GF_SMTP_FROM_ADDRESS=${SMTP_FROM:-grafana@example.com}
      - GF_SMTP_FROM_NAME=OBCMS Grafana

      # Alerting
      - GF_UNIFIED_ALERTING_ENABLED=true

      # For PostgreSQL data source
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - ./config/grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana_data:/var/lib/grafana
    networks:
      - obcms_network
    depends_on:
      - prometheus
      - postgres

volumes:
  prometheus_data:
    driver: local
  alertmanager_data:
    driver: local
  grafana_data:
    driver: local

networks:
  obcms_network:
    driver: bridge
```

## Step 2: Configure Environment Variables

Add to your `.env` file:

```bash
# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=your-secure-admin-password-here
GRAFANA_SECRET_KEY=your-secret-key-here-32-chars-minimum
GRAFANA_ROOT_URL=http://localhost:3000
GRAFANA_DOMAIN=localhost

# Grafana Database (internal)
GRAFANA_DB_NAME=grafana
GRAFANA_DB_USER=grafana
GRAFANA_DB_PASSWORD=your-grafana-db-password

# SMTP Configuration (for email alerts)
SMTP_HOST=smtp.gmail.com:587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=grafana@example.com

# Slack Integration (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_WEBHOOK_URL_CRITICAL=https://hooks.slack.com/services/YOUR/CRITICAL/URL

# PagerDuty Integration (optional)
PAGERDUTY_SERVICE_KEY=your-pagerduty-service-key

# PostgreSQL (main OBCMS database)
POSTGRES_DB=obcms
POSTGRES_USER=obcms_user
POSTGRES_PASSWORD=your-postgres-password
```

**Generate secure secrets:**

```bash
# Generate Grafana admin password
openssl rand -base64 32

# Generate Grafana secret key
openssl rand -base64 32
```

## Step 3: Create Grafana Database

Grafana needs its own database for storing users, dashboards, etc.

```bash
# Connect to PostgreSQL
docker exec -it obcms_postgres psql -U postgres

# Create Grafana database and user
CREATE DATABASE grafana;
CREATE USER grafana WITH PASSWORD 'your-grafana-db-password';
GRANT ALL PRIVILEGES ON DATABASE grafana TO grafana;
\q
```

## Step 4: Update Prometheus Configuration

Ensure your `config/prometheus/prometheus.yml` includes alerting configuration:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 30s
  external_labels:
    cluster: 'obcms-production'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load alert rules
rule_files:
  - '/etc/prometheus/alert-rules.yml'

scrape_configs:
  # Django application metrics
  - job_name: 'obcms'
    static_configs:
      - targets: ['web:8000']

  # PostgreSQL metrics
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']

  # Redis metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['redis_exporter:9121']

  # Celery metrics
  - job_name: 'celery'
    static_configs:
      - targets: ['celery_exporter:9808']

  # Node exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node_exporter:9100']

  # cAdvisor (container metrics)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

## Step 5: Start the Monitoring Stack

```bash
# Pull latest images
docker-compose pull prometheus alertmanager grafana

# Start services
docker-compose up -d prometheus alertmanager grafana

# Check logs
docker-compose logs -f grafana
docker-compose logs -f prometheus
docker-compose logs -f alertmanager
```

## Step 6: Verify Installation

### Check Prometheus

1. Open http://localhost:9090
2. Go to **Status → Targets**
3. Verify all targets are **UP**
4. Go to **Status → Rules**
5. Verify alert rules are loaded

### Check Alertmanager

1. Open http://localhost:9093
2. Verify configuration is loaded
3. Check for any errors

### Check Grafana

1. Open http://localhost:3000
2. Login with admin credentials
3. Go to **Configuration → Data Sources**
4. Verify Prometheus data source shows green check mark
5. Test PostgreSQL data source connection

## Step 7: Access Dashboards

### Main Application Dashboard
http://localhost:3000/d/obcms-main

**What to expect:**
- All panels should show data within 1-2 minutes
- If "No data" appears, check Prometheus targets
- Refresh rate: 30 seconds

### Database Monitoring Dashboard
http://localhost:3000/d/obcms-database

**What to expect:**
- Connection count should be > 0
- Transaction rate should show activity
- Buffer cache hit ratio should be > 90%

### Infrastructure Dashboard
http://localhost:3000/d/obcms-infrastructure

**What to expect:**
- CPU, Memory, Disk gauges showing current usage
- Container metrics for all OBCMS containers

## Step 8: Configure Alerting

### Update Alertmanager Configuration

Edit `config/prometheus/alertmanager.yml` and replace placeholders:

```yaml
receivers:
  - name: 'default'
    email_configs:
      - to: 'your-ops-email@example.com'  # ← Update this
```

### Reload Alertmanager Configuration

```bash
# Reload without restart
docker exec obcms_alertmanager kill -HUP 1

# Or restart
docker-compose restart alertmanager
```

### Test Email Alerts

```bash
# Send test alert
curl -X POST http://localhost:9093/api/v1/alerts -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "info"
    },
    "annotations": {
      "summary": "This is a test alert",
      "description": "Testing email notifications"
    }
  }
]'
```

Check your email for the test alert.

### Configure Slack Notifications

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add webhook URL to `.env`:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```
3. Restart Alertmanager:
   ```bash
   docker-compose restart alertmanager
   ```
4. Test Slack notification (same curl command as email)

## Step 9: Customize Dashboards

### Add Panels to Existing Dashboards

1. Open dashboard in Grafana
2. Click **Add panel** button (top right)
3. Select **Add a new panel**
4. Configure query, visualization, thresholds
5. Click **Apply**
6. **Save dashboard** (disk icon)
7. Export JSON for persistence

### Import Community Dashboards

**PostgreSQL Dashboard (ID: 9628):**

1. Go to **Dashboards → Import**
2. Enter dashboard ID: `9628`
3. Click **Load**
4. Select Prometheus data source
5. Click **Import**

**Node Exporter Dashboard (ID: 1860):**

1. Go to **Dashboards → Import**
2. Enter dashboard ID: `1860`
3. Select Prometheus data source
4. Click **Import**

## Step 10: Set Up Monitoring Alerts in Grafana

### Create Alert Notification Channel

1. Go to **Alerting → Notification channels**
2. Click **Add channel**
3. Configure:
   - **Name:** Email Ops Team
   - **Type:** Email
   - **Addresses:** ops@example.com
4. Click **Test** to verify
5. Click **Save**

### Add Alert to Panel

1. Edit any panel in a dashboard
2. Click **Alert** tab
3. Click **Create Alert**
4. Configure conditions:
   ```
   WHEN avg() OF query(A, 5m) IS ABOVE 80
   ```
5. Under **Notifications**, select channel
6. Click **Save**

## Step 11: Monitor Alert Health

### Prometheus Alerts UI

http://localhost:9090/alerts

**Status meanings:**
- **Green (Inactive):** Alert condition not met
- **Yellow (Pending):** Condition met but waiting for `for` duration
- **Red (Firing):** Alert actively firing

### Alertmanager UI

http://localhost:9093

**Features:**
- View active alerts
- Silence alerts temporarily
- See notification history
- Check routing tree

### Grafana Alerting

http://localhost:3000/alerting/list

- View all Grafana-native alerts
- See alert state history
- Manage notification policies

## Step 12: Production Checklist

Before deploying to production:

- [ ] Change default Grafana admin password
- [ ] Configure HTTPS/TLS for Grafana
- [ ] Set up proper authentication (LDAP/OAuth)
- [ ] Configure email SMTP settings
- [ ] Test all notification channels
- [ ] Verify all alert rules fire correctly
- [ ] Set appropriate alert thresholds for production
- [ ] Configure backup for Grafana dashboards
- [ ] Set up Prometheus remote storage (if needed)
- [ ] Document runbooks for each alert
- [ ] Train team on dashboard usage
- [ ] Establish on-call rotation for critical alerts

## Troubleshooting

### No Data in Dashboards

**Check Prometheus targets:**
```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

**Check if metrics exist:**
```bash
curl -s http://localhost:9090/api/v1/label/__name__/values | jq '.data[] | select(. | startswith("django"))'
```

**Verify Grafana data source:**
```bash
docker exec obcms_grafana grafana-cli admin data-migration encrypt-datasource-passwords
```

### Alerts Not Firing

**Check Prometheus rules:**
```bash
promtool check rules config/prometheus/alert-rules.yml
```

**Verify Alertmanager config:**
```bash
docker exec obcms_alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
```

**Check Alertmanager routing:**
```bash
docker exec obcms_alertmanager amtool config routes
```

### Email Notifications Not Working

**Test SMTP connection:**
```bash
docker exec obcms_grafana grafana-cli admin reset-admin-password --homepath /usr/share/grafana test123
```

**Check Alertmanager logs:**
```bash
docker logs obcms_alertmanager | grep -i smtp
```

### High Memory Usage

**Reduce Prometheus retention:**
```yaml
command:
  - '--storage.tsdb.retention.time=15d'  # Reduce from 30d
```

**Configure memory limits:**
```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          memory: 4G
```

## Maintenance

### Backup Grafana Data

```bash
# Backup Grafana database
docker exec obcms_postgres pg_dump -U grafana grafana > grafana-backup-$(date +%Y%m%d).sql

# Backup dashboards
docker exec obcms_grafana tar czf - /var/lib/grafana > grafana-data-$(date +%Y%m%d).tar.gz
```

### Backup Prometheus Data

```bash
# Snapshot Prometheus data
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Backup data directory
docker run --rm -v obcms_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup-$(date +%Y%m%d).tar.gz /data
```

### Update Dashboards

```bash
# Export all dashboards
./scripts/export-grafana-dashboards.sh

# Import dashboards after update
docker-compose restart grafana
```

## Next Steps

1. **Tune alert thresholds** based on baseline metrics
2. **Create custom dashboards** for specific use cases
3. **Set up recording rules** for expensive queries
4. **Configure retention policies** based on storage
5. **Implement log aggregation** (Loki + Grafana)
6. **Add distributed tracing** (Jaeger/Tempo)
7. **Set up SLO/SLA tracking**

## Resources

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [OBCMS Monitoring Guide](config/grafana/README.md)
- [Alert Rules Reference](config/prometheus/ALERT_RULES_REFERENCE.md)
