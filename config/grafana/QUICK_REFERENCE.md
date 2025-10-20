# OBCMS Monitoring Quick Reference

## Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / ${GRAFANA_ADMIN_PASSWORD} |
| **Prometheus** | http://localhost:9090 | No auth (configure in production) |
| **Alertmanager** | http://localhost:9093 | No auth (configure in production) |

## Key Dashboards

| Dashboard | UID | URL | Purpose |
|-----------|-----|-----|---------|
| **OBCMS Main** | obcms-main | /d/obcms-main | Application metrics, request latency, cache, Celery |
| **Database** | obcms-database | /d/obcms-database | PostgreSQL performance, connections, queries |
| **Infrastructure** | obcms-infrastructure | /d/obcms-infrastructure | CPU, memory, disk, containers |

## Quick Commands

### Start/Stop Services

```bash
# Start monitoring stack
docker-compose up -d grafana prometheus alertmanager

# Stop monitoring stack
docker-compose stop grafana prometheus alertmanager

# Restart with new config
docker-compose restart grafana prometheus alertmanager

# View logs
docker-compose logs -f grafana
docker-compose logs -f prometheus
docker-compose logs -f alertmanager
```

### Reload Configurations

```bash
# Reload Prometheus config (without restart)
curl -X POST http://localhost:9090/-/reload

# Reload Alertmanager config (without restart)
docker exec obcms_alertmanager kill -HUP 1

# Reload Grafana provisioning (automatic - wait 10s)
# Or restart: docker-compose restart grafana
```

### Check Health

```bash
# Prometheus health
curl http://localhost:9090/-/healthy

# Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Alertmanager health
curl http://localhost:9093/-/healthy

# Grafana health
curl http://localhost:3000/api/health
```

### Validate Configurations

```bash
# Validate Prometheus config
docker exec obcms_prometheus promtool check config /etc/prometheus/prometheus.yml

# Validate alert rules
docker exec obcms_prometheus promtool check rules /etc/prometheus/alert-rules.yml

# Validate Alertmanager config
docker exec obcms_alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
```

## Common PromQL Queries

### Application Metrics

```promql
# Request rate
sum(rate(django_http_requests_total[5m]))

# Error rate
sum(rate(django_http_responses_total{status=~"5.."}[5m])) / sum(rate(django_http_responses_total[5m]))

# p95 latency
histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m]))

# Cache hit rate
sum(rate(django_cache_get_hits_total[5m])) / (sum(rate(django_cache_get_hits_total[5m])) + sum(rate(django_cache_get_misses_total[5m])))
```

### Database Metrics

```promql
# Active connections
pg_stat_database_numbackends{datname="obcms"}

# Connection pool utilization
django_db_connections_active / django_db_connections_total

# Transaction rate
rate(pg_stat_database_xact_commit[5m])

# Slow queries
rate(pg_stat_statements_mean_exec_time_ms{datname="obcms"}[5m])
```

### Infrastructure Metrics

```promql
# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))

# Disk usage
100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})

# Container CPU
sum(rate(container_cpu_usage_seconds_total{name=~"obcms.*"}[5m])) by (name) * 100
```

## Alert Severity Guide

| Severity | Response Time | Examples |
|----------|--------------|----------|
| **Critical** | < 15 min | Service down, error rate > 1%, no workers, database down |
| **Warning** | < 1 hour | Slow responses, high CPU, disk space < 20%, cache issues |
| **Info** | As needed | High traffic, configuration changes |

## Common Alert Responses

### HighErrorRate (Critical)

1. Check application logs: `docker logs obcms_web --tail 100`
2. Check Sentry for error details
3. Verify database connectivity
4. Check recent deployments
5. Review Grafana dashboard for patterns

### DatabaseConnectionPoolExhausted (Critical)

1. Check active connections: `docker exec obcms_postgres psql -U obcms_user -d obcms -c "SELECT count(*) FROM pg_stat_activity;"`
2. Identify long-running queries: `SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;`
3. Increase connection pool size if needed
4. Kill stuck connections if safe

### HighCeleryQueueDepth (Warning)

1. Check worker status: `docker exec obcms_celery_worker celery -A obc_management inspect active`
2. Check for stuck tasks: `docker logs obcms_celery_worker --tail 50`
3. Scale workers: `docker-compose up -d --scale celery_worker=4`
4. Check task execution time

### HighCPUUsage (Warning)

1. Identify process: `docker exec obcms_web top -b -n 1 | head -20`
2. Check for infinite loops or runaway processes
3. Review recent code changes
4. Scale horizontally if legitimate load

### LowDiskSpace (Warning/Critical)

1. Check disk usage: `docker exec obcms_web df -h`
2. Clean Docker: `docker system prune -a --volumes`
3. Clean logs: `find /var/log -name "*.log" -mtime +30 -delete`
4. Clean old backups
5. Add disk space if needed

## Dashboard Customization

### Add New Panel

1. Open dashboard
2. Click "Add panel" (top right)
3. Select visualization type
4. Write PromQL query
5. Configure thresholds
6. Click "Apply"
7. Save dashboard

### Export Dashboard

1. Dashboard settings (gear icon)
2. JSON Model
3. Copy JSON
4. Save to `config/grafana/provisioning/dashboards/`

### Import Dashboard

1. Dashboards → Import
2. Enter dashboard ID or upload JSON
3. Select data source
4. Click Import

## Notification Channels

### Email

```yaml
receivers:
  - name: email
    email_configs:
      - to: team@example.com
```

### Slack

```yaml
receivers:
  - name: slack
    slack_configs:
      - api_url: ${SLACK_WEBHOOK_URL}
        channel: '#alerts'
```

### PagerDuty

```yaml
receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: ${PAGERDUTY_SERVICE_KEY}
```

## Backup Commands

### Backup Grafana

```bash
# Backup database
docker exec obcms_postgres pg_dump -U grafana grafana > grafana-backup.sql

# Backup dashboards
docker exec obcms_grafana tar czf - /var/lib/grafana > grafana-data.tar.gz
```

### Backup Prometheus

```bash
# Create snapshot
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Backup data
docker run --rm -v obcms_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data
```

## Troubleshooting Steps

### No Data in Dashboards

```bash
# 1. Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq

# 2. Check if metrics exist
curl http://localhost:9090/api/v1/label/__name__/values | jq '.data[] | select(startswith("django"))'

# 3. Test Grafana data source
curl -u admin:${GRAFANA_ADMIN_PASSWORD} http://localhost:3000/api/datasources

# 4. Check scrape errors
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'
```

### Alerts Not Firing

```bash
# 1. Check alert rules
curl http://localhost:9090/api/v1/rules | jq

# 2. Check Alertmanager config
docker exec obcms_alertmanager amtool config show

# 3. Check alert routing
docker exec obcms_alertmanager amtool config routes

# 4. Test alert
curl -X POST http://localhost:9093/api/v1/alerts -d '[{"labels":{"alertname":"Test"}}]'
```

### High Memory Usage

```bash
# Check container memory
docker stats --no-stream

# Reduce Prometheus retention
# Edit prometheus command: --storage.tsdb.retention.time=15d

# Clean old data
docker exec obcms_prometheus promtool tsdb list /prometheus
```

## Performance Tips

1. **Limit dashboard time range** to 6-12 hours for faster loading
2. **Use recording rules** for expensive PromQL queries
3. **Increase scrape intervals** if too much data (e.g., 30s instead of 15s)
4. **Enable query caching** in Grafana data source settings
5. **Reduce panel refresh rate** for less critical dashboards
6. **Archive old metrics** using remote storage

## Security Checklist

- [ ] Change default Grafana admin password
- [ ] Configure HTTPS for Grafana in production
- [ ] Set up authentication (LDAP/OAuth)
- [ ] Restrict Prometheus/Alertmanager network access
- [ ] Use read-only data source connections
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption

## Useful Links

- **Grafana Docs:** https://grafana.com/docs/grafana/latest/
- **Prometheus Docs:** https://prometheus.io/docs/
- **PromQL Cheatsheet:** https://promlabs.com/promql-cheat-sheet/
- **Dashboard Gallery:** https://grafana.com/grafana/dashboards/
- **OBCMS Setup Guide:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Alert Reference:** [../prometheus/ALERT_RULES_REFERENCE.md](../prometheus/ALERT_RULES_REFERENCE.md)

## Getting Help

1. **Check logs:** `docker-compose logs <service>`
2. **Review documentation:** `config/grafana/README.md`
3. **Test connectivity:** `curl` commands above
4. **Validate configs:** `promtool` and `amtool` commands
5. **Community forums:** Grafana and Prometheus communities

---

**Last Updated:** 2025-10-20
**OBCMS Version:** Latest
