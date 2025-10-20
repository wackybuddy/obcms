# OBCMS Grafana Monitoring Setup

This directory contains Grafana dashboard provisioning and configuration for comprehensive OBCMS monitoring.

## Directory Structure

```
config/grafana/
├── provisioning/
│   ├── dashboards/
│   │   ├── dashboards.yml              # Dashboard provisioning config
│   │   ├── obcms-main.json             # Main application dashboard
│   │   ├── obcms-database.json         # Database monitoring dashboard
│   │   └── infrastructure/
│   │       └── obcms-infrastructure.json  # Infrastructure dashboard
│   └── datasources/
│       └── prometheus.yml              # Prometheus data source config
└── README.md                           # This file
```

## Quick Start

### 1. Docker Compose Integration

Add Grafana to your `docker-compose.yml`:

```yaml
services:
  grafana:
    image: grafana/grafana:10.2.0
    container_name: obcms_grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-changeme}
      - GF_SERVER_ROOT_URL=http://localhost:3000
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
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

volumes:
  grafana_data:
    driver: local
```

### 2. Environment Variables

Add to your `.env` file:

```bash
# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=your-secure-password-here

# PostgreSQL (for direct connection data source)
POSTGRES_DB=obcms
POSTGRES_USER=obcms_user
POSTGRES_PASSWORD=your-postgres-password
```

### 3. Start Grafana

```bash
docker-compose up -d grafana
```

### 4. Access Grafana

- URL: http://localhost:3000
- Username: `admin`
- Password: Value from `GRAFANA_ADMIN_PASSWORD` env variable

## Available Dashboards

### 1. OBCMS Main Application Dashboard
**UID:** `obcms-main`
**URL:** http://localhost:3000/d/obcms-main

**Panels:**
- Request Throughput (req/s)
- Error Rate (5xx responses)
- Cache Hit Rate
- Celery Queue Depth
- Request Latency (p50, p95, p99)
- HTTP Response Codes Over Time
- Database Connection Pool
- Redis Memory Usage
- Celery Worker Availability
- Celery Task Execution Rate

**Refresh:** 30 seconds
**Default Time Range:** Last 6 hours

### 2. OBCMS Database Monitoring Dashboard
**UID:** `obcms-database`
**URL:** http://localhost:3000/d/obcms-database

**Panels:**
- Active Database Connections
- Replication Lag
- Connection Pool Utilization
- Transaction Rate
- Query Execution Time
- Database Connections Over Time
- Database Write Operations (Inserts/Updates/Deletes)
- PostgreSQL Buffer Cache Hit Ratio
- Database Deadlocks
- Database Size

**Refresh:** 30 seconds
**Default Time Range:** Last 6 hours

### 3. OBCMS Infrastructure Dashboard
**UID:** `obcms-infrastructure`
**URL:** http://localhost:3000/d/obcms-infrastructure

**Panels:**
- CPU Usage (Gauge)
- Memory Usage (Gauge)
- Disk Usage (Gauge)
- Docker Volume Usage (Gauge)
- CPU Usage Over Time
- Memory Usage Over Time
- Disk I/O
- Network Traffic
- Container CPU Usage
- Container Memory Usage

**Refresh:** 30 seconds
**Default Time Range:** Last 6 hours

## Dashboard Customization

### Importing Additional Dashboards

#### From Grafana.com

1. Browse dashboards at https://grafana.com/grafana/dashboards/
2. Find a dashboard (e.g., PostgreSQL Dashboard #9628)
3. In Grafana UI: **Dashboards → Import**
4. Enter dashboard ID or upload JSON
5. Select Prometheus data source
6. Click **Import**

#### Recommended Community Dashboards

**PostgreSQL:**
- [PostgreSQL Database](https://grafana.com/grafana/dashboards/9628) - ID: 9628
- [PostgreSQL Overview](https://grafana.com/grafana/dashboards/455) - ID: 455

**Redis:**
- [Redis Dashboard](https://grafana.com/grafana/dashboards/11835) - ID: 11835
- [Redis Overview](https://grafana.com/grafana/dashboards/763) - ID: 763

**Django:**
- [Django Metrics](https://grafana.com/grafana/dashboards/14159) - ID: 14159

**Node Exporter:**
- [Node Exporter Full](https://grafana.com/grafana/dashboards/1860) - ID: 1860
- [Node Exporter for Prometheus](https://grafana.com/grafana/dashboards/11074) - ID: 11074

**Docker:**
- [Docker and System Monitoring](https://grafana.com/grafana/dashboards/893) - ID: 893
- [Docker Container & Host Metrics](https://grafana.com/grafana/dashboards/10619) - ID: 10619

**Celery:**
- [Celery Monitoring](https://grafana.com/grafana/dashboards/13183) - ID: 13183

### Exporting Custom Dashboards

1. Open dashboard in Grafana
2. Click **Settings** (gear icon)
3. Click **JSON Model** in left sidebar
4. Copy JSON
5. Save to `config/grafana/provisioning/dashboards/custom-dashboard.json`
6. Restart Grafana or wait for auto-reload

### Modifying Existing Dashboards

#### Method 1: Through Grafana UI (Recommended for Testing)

1. Open dashboard
2. Click **Settings** → **Make editable** (if provisioned)
3. Edit panels, add queries, adjust thresholds
4. Click **Save dashboard**
5. Export JSON for persistence (see above)

#### Method 2: Direct JSON Editing

1. Edit JSON file in `config/grafana/provisioning/dashboards/`
2. Modify panel configurations, queries, thresholds
3. Save file
4. Grafana will auto-reload (within 10 seconds)

**Example: Changing Error Rate Threshold**

```json
{
  "thresholds": {
    "mode": "absolute",
    "steps": [
      {"color": "green", "value": null},
      {"color": "yellow", "value": 0.5},  // Changed from 0.5 to 0.3
      {"color": "red", "value": 1}        // Changed from 1 to 0.5
    ]
  }
}
```

## Panel Query Examples

### Django Metrics

**Request Rate by View:**
```promql
sum(rate(django_http_requests_total_by_view_transport_method_total{job="obcms"}[5m])) by (view)
```

**Average Response Time:**
```promql
avg(rate(django_http_requests_latency_seconds_sum{job="obcms"}[5m]) / rate(django_http_requests_latency_seconds_count{job="obcms"}[5m]))
```

**Error Rate by Status Code:**
```promql
sum(rate(django_http_responses_total_by_status_total{job="obcms"}[5m])) by (status)
```

### Database Metrics

**Slow Queries:**
```promql
topk(10, rate(pg_stat_statements_mean_exec_time_ms{datname="obcms"}[5m]))
```

**Database Size Growth:**
```promql
deriv(pg_database_size_bytes{datname="obcms"}[1h])
```

### Celery Metrics

**Tasks Completed Per Hour:**
```promql
sum(increase(celery_tasks_total{job="celery",state="success"}[1h]))
```

**Task Queue by Queue Name:**
```promql
sum(celery_task_queue_depth{job="celery"}) by (queue_name)
```

### Infrastructure Metrics

**Container Restart Count:**
```promql
sum(kube_pod_container_status_restarts_total{namespace="obcms"}) by (container)
```

**Network Bandwidth:**
```promql
sum(rate(node_network_receive_bytes_total[5m]) + rate(node_network_transmit_bytes_total[5m]))
```

## Templating Variables

### Adding a Time Range Variable

1. **Dashboard Settings → Variables → Add variable**
2. **Type:** Custom
3. **Name:** `interval`
4. **Label:** Time Interval
5. **Values:** `1m,5m,15m,30m,1h`
6. **Default:** `5m`

### Using Variables in Queries

Replace hardcoded intervals:
```promql
# Before
rate(django_http_requests_total[5m])

# After
rate(django_http_requests_total[$interval])
```

### Environment Variable

**Example: Multi-Organization Filter**

```promql
django_http_requests_total{organization="$organization"}
```

## Alert Integration

Alerts are configured in Prometheus (see `config/prometheus/alert-rules.yml`), but you can view them in Grafana:

1. **Alerting → Alert rules**
2. View firing alerts
3. Configure notification channels (email, Slack, PagerDuty)

### Adding Grafana Alerts to Panels

1. Edit panel
2. Click **Alert** tab
3. **Create Alert**
4. Set conditions (e.g., "WHEN avg() OF query(A, 5m) IS ABOVE 100")
5. Configure notifications
6. **Save**

## Troubleshooting

### Dashboards Not Loading

**Check provisioning path:**
```bash
docker exec obcms_grafana ls -la /etc/grafana/provisioning/dashboards/
```

**Check Grafana logs:**
```bash
docker logs obcms_grafana | grep -i "provisioning"
```

### No Data in Panels

**Verify Prometheus data source:**
1. **Configuration → Data Sources → Prometheus**
2. Click **Test** button
3. Should see "Data source is working"

**Check Prometheus targets:**
- http://localhost:9090/targets
- All targets should be **UP**

**Verify metrics exist:**
```bash
curl -s http://localhost:9090/api/v1/label/__name__/values | jq '.data[] | select(. | startswith("django"))'
```

### Missing Metrics

**Ensure exporters are running:**
```bash
docker-compose ps prometheus postgres_exporter redis_exporter node_exporter
```

**Check metric names:**
```bash
# List all available metrics
curl -s http://localhost:9090/api/v1/label/__name__/values | jq '.data[]'
```

### Permission Issues

**Fix volume permissions:**
```bash
sudo chown -R 472:472 grafana_data/
```

## Performance Optimization

### Dashboard Performance

1. **Limit time range:** Use shorter default ranges (6h instead of 24h)
2. **Reduce panel count:** Split heavy dashboards
3. **Optimize queries:** Use recording rules for complex queries
4. **Increase scrape interval:** If data volume is too high

### Query Optimization

**Use recording rules in Prometheus:**

```yaml
# config/prometheus/recording-rules.yml
groups:
  - name: obcms_recording_rules
    interval: 30s
    rules:
      - record: job:django_http_request_rate:5m
        expr: sum(rate(django_http_requests_total[5m])) by (job)
```

**Then use in Grafana:**
```promql
job:django_http_request_rate:5m{job="obcms"}
```

## Backup and Restore

### Backup Dashboards

**Export all dashboards:**
```bash
docker exec obcms_grafana grafana-cli admin export-dashboard > dashboards-backup.json
```

**Backup Grafana data:**
```bash
docker run --rm -v obcms_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

### Restore Dashboards

1. Copy JSON files to `config/grafana/provisioning/dashboards/`
2. Restart Grafana: `docker-compose restart grafana`

## Security Best Practices

1. **Change default admin password** immediately
2. **Use strong passwords** (min 16 characters)
3. **Enable HTTPS** in production
4. **Restrict network access** (firewall rules)
5. **Use read-only data sources** where possible
6. **Regular backups** of Grafana data
7. **Audit user access** regularly

## Advanced Configuration

### LDAP/OAuth Integration

Edit `grafana.ini` or use environment variables:

```yaml
environment:
  - GF_AUTH_LDAP_ENABLED=true
  - GF_AUTH_LDAP_CONFIG_FILE=/etc/grafana/ldap.toml
```

### SMTP for Alerting

```yaml
environment:
  - GF_SMTP_ENABLED=true
  - GF_SMTP_HOST=smtp.gmail.com:587
  - GF_SMTP_USER=alerts@example.com
  - GF_SMTP_PASSWORD=${SMTP_PASSWORD}
  - GF_SMTP_FROM_ADDRESS=grafana@example.com
```

### Anonymous Access (Read-Only)

```yaml
environment:
  - GF_AUTH_ANONYMOUS_ENABLED=true
  - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
```

## Resources

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/dashboard-management/)
- [PromQL Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Community Dashboards](https://grafana.com/grafana/dashboards/)

## Support

For OBCMS-specific monitoring questions:
1. Check OBCMS documentation: `docs/deployment/`
2. Review Prometheus configuration: `config/prometheus/`
3. Check alert rules: `config/prometheus/alert-rules.yml`
