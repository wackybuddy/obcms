# OBCMS Prometheus Alert Rules Reference

This document provides a comprehensive reference for all Prometheus alerting rules configured for OBCMS monitoring.

## Alert Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| **critical** | Service-affecting issue requiring immediate attention | < 15 minutes |
| **warning** | Degraded performance or potential issues | < 1 hour |
| **info** | Informational alerts for awareness | As needed |

## Alert Groups

### 1. Application Alerts (`obcms_application_alerts`)

#### HighErrorRate
**Severity:** Critical
**Threshold:** > 1% of requests returning 5xx errors
**Duration:** 5 minutes
**Impact:** Users experiencing service errors

**Query:**
```promql
(sum(rate(django_http_responses_total_by_status_total{job="obcms",status=~"5.."}[5m]))
/ sum(rate(django_http_responses_total_by_status_total{job="obcms"}[5m]))) > 0.01
```

**Response Actions:**
1. Check application logs: `docker logs obcms_web`
2. Review recent deployments
3. Check database connectivity
4. Verify external service dependencies
5. Review Sentry/error tracking

---

#### SlowResponseTime
**Severity:** Warning
**Threshold:** p95 response time > 1 second
**Duration:** 10 minutes
**Impact:** Degraded user experience

**Query:**
```promql
histogram_quantile(0.95, sum(rate(django_http_requests_latency_seconds_by_view_method_bucket{job="obcms"}[5m])) by (le)) > 1
```

**Response Actions:**
1. Check slow query log
2. Review recent code changes
3. Check database connection pool
4. Monitor cache hit rate
5. Investigate N+1 queries
6. Check external API latency

---

#### CacheFailure
**Severity:** Warning
**Threshold:** Cache hit rate < 50%
**Duration:** 15 minutes
**Impact:** Increased database load, slower responses

**Query:**
```promql
(sum(rate(django_cache_get_hits_total{job="obcms"}[5m]))
/ (sum(rate(django_cache_get_hits_total{job="obcms"}[5m])) + sum(rate(django_cache_get_misses_total{job="obcms"}[5m])))) < 0.5
```

**Response Actions:**
1. Check Redis status: `docker logs obcms_redis`
2. Verify Redis memory: `redis-cli INFO memory`
3. Check cache key patterns
4. Review cache invalidation logic
5. Consider increasing Redis memory

---

#### HighRequestRate
**Severity:** Info
**Threshold:** > 1000 requests/second
**Duration:** 5 minutes
**Impact:** High traffic volume (may be normal)

**Query:**
```promql
sum(rate(django_http_requests_total_by_view_transport_method_total{job="obcms"}[5m])) > 1000
```

**Response Actions:**
1. Verify traffic is legitimate (not DDoS)
2. Check if autoscaling is working
3. Monitor resource utilization
4. Review rate limiting configuration

---

### 2. Database Alerts (`obcms_database_alerts`)

#### DatabaseConnectionPoolExhausted
**Severity:** Critical
**Threshold:** > 90% of connection pool in use
**Duration:** 5 minutes
**Impact:** Request failures due to no available connections

**Query:**
```promql
(django_db_connections_active{job="obcms"} / django_db_connections_total{job="obcms"}) > 0.9
```

**Response Actions:**
1. Identify connection leaks: `SELECT * FROM pg_stat_activity;`
2. Kill idle connections: `SELECT pg_terminate_backend(pid);`
3. Increase `CONN_MAX_AGE` setting
4. Increase connection pool size
5. Review long-running queries

---

#### HighDatabaseConnections
**Severity:** Warning
**Threshold:** > 80 active connections
**Duration:** 10 minutes
**Impact:** Potential connection pool exhaustion

**Query:**
```promql
pg_stat_database_numbackends{datname="obcms"} > 80
```

**Response Actions:**
1. Check active queries: `SELECT * FROM pg_stat_activity WHERE state = 'active';`
2. Identify slow queries
3. Review connection pooling configuration
4. Check for connection leaks in application
5. Consider using pgBouncer

---

#### DatabaseReplicationLag
**Severity:** Warning
**Threshold:** > 30 seconds replication lag
**Duration:** 5 minutes
**Impact:** Stale reads on replicas, potential data loss

**Query:**
```promql
pg_replication_lag_seconds > 30
```

**Response Actions:**
1. Check replica status: `SELECT * FROM pg_stat_replication;`
2. Check network connectivity to replica
3. Review write volume on primary
4. Check replica disk I/O
5. Verify replication slot status

---

#### SlowDatabaseQueries
**Severity:** Warning
**Threshold:** Mean query time > 1000ms
**Duration:** 10 minutes
**Impact:** Slow application performance

**Query:**
```promql
rate(pg_stat_statements_mean_exec_time_ms{datname="obcms"}[5m]) > 1000
```

**Response Actions:**
1. Identify slow queries: `SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC;`
2. Review query execution plans: `EXPLAIN ANALYZE`
3. Check missing indexes
4. Update table statistics: `ANALYZE`
5. Consider query optimization

---

#### DatabaseDeadlocks
**Severity:** Warning
**Threshold:** > 0 deadlocks in 10 minutes
**Duration:** 5 minutes
**Impact:** Failed transactions, data consistency issues

**Query:**
```promql
increase(pg_stat_database_deadlocks{datname="obcms"}[10m]) > 0
```

**Response Actions:**
1. Review deadlock logs in PostgreSQL
2. Identify conflicting transactions
3. Review transaction isolation levels
4. Implement retry logic
5. Consider table locking strategy

---

#### LowBufferCacheHitRatio
**Severity:** Warning
**Threshold:** < 90% buffer cache hit ratio
**Duration:** 15 minutes
**Impact:** Increased disk I/O, slower queries

**Query:**
```promql
(rate(pg_stat_database_blks_hit{datname="obcms"}[5m])
/ (rate(pg_stat_database_blks_hit{datname="obcms"}[5m]) + rate(pg_stat_database_blks_read{datname="obcms"}[5m]))) < 0.90
```

**Response Actions:**
1. Increase `shared_buffers` in PostgreSQL config
2. Review query patterns
3. Check working set size
4. Monitor memory usage
5. Consider adding more RAM

---

### 3. Celery Alerts (`obcms_celery_alerts`)

#### HighCeleryQueueDepth
**Severity:** Warning
**Threshold:** > 1000 pending tasks
**Duration:** 10 minutes
**Impact:** Delayed background task processing

**Query:**
```promql
sum(celery_task_queue_depth{job="celery"}) > 1000
```

**Response Actions:**
1. Check worker status: `celery -A obc_management inspect active`
2. Increase worker count
3. Check for stuck tasks
4. Review task execution time
5. Consider horizontal scaling

---

#### NoActiveCeleryWorkers
**Severity:** Critical
**Threshold:** 0 active workers
**Duration:** 5 minutes
**Impact:** Background tasks not processing

**Query:**
```promql
celery_workers_active{job="celery"} == 0
```

**Response Actions:**
1. Restart workers: `docker-compose restart celery_worker`
2. Check worker logs: `docker logs obcms_celery_worker`
3. Check broker connectivity (Redis/RabbitMQ)
4. Verify worker configuration
5. Check resource constraints (OOM)

---

#### HighCeleryTaskFailureRate
**Severity:** Warning
**Threshold:** > 5% task failure rate
**Duration:** 10 minutes
**Impact:** Background processes failing

**Query:**
```promql
(sum(rate(celery_tasks_total{job="celery",state="failure"}[5m]))
/ sum(rate(celery_tasks_total{job="celery"}[5m]))) > 0.05
```

**Response Actions:**
1. Review task logs
2. Check task error messages
3. Verify task dependencies
4. Review recent task changes
5. Implement better error handling

---

### 4. Redis Alerts (`obcms_redis_alerts`)

#### HighRedisMemoryUsage
**Severity:** Warning
**Threshold:** > 80% of max memory
**Duration:** 10 minutes
**Impact:** Cache evictions, potential OOM

**Query:**
```promql
(redis_memory_used_bytes{job="redis"} / redis_memory_max_bytes{job="redis"}) > 0.80
```

**Response Actions:**
1. Check memory usage: `redis-cli INFO memory`
2. Review large keys: `redis-cli --bigkeys`
3. Check eviction policy: `redis-cli CONFIG GET maxmemory-policy`
4. Clear unnecessary keys
5. Increase Redis memory allocation

---

#### RedisDown
**Severity:** Critical
**Threshold:** Redis not responding
**Duration:** 2 minutes
**Impact:** Cache unavailable, session loss

**Query:**
```promql
up{job="redis"} == 0
```

**Response Actions:**
1. Restart Redis: `docker-compose restart redis`
2. Check Redis logs: `docker logs obcms_redis`
3. Verify persistence (RDB/AOF)
4. Check disk space
5. Review Redis configuration

---

#### HighRedisEvictionRate
**Severity:** Warning
**Threshold:** > 100 evictions/second
**Duration:** 10 minutes
**Impact:** Frequent cache misses, poor performance

**Query:**
```promql
rate(redis_evicted_keys_total{job="redis"}[5m]) > 100
```

**Response Actions:**
1. Check eviction policy
2. Increase Redis memory
3. Review key TTLs
4. Analyze cache patterns
5. Consider Redis cluster

---

### 5. Infrastructure Alerts (`obcms_infrastructure_alerts`)

#### HighCPUUsage
**Severity:** Warning
**Threshold:** > 80% CPU usage
**Duration:** 10 minutes
**Impact:** Slow application performance

**Query:**
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
```

**Response Actions:**
1. Identify CPU-intensive processes: `top`, `htop`
2. Check for runaway processes
3. Review recent deployments
4. Scale horizontally
5. Optimize application code

---

#### HighMemoryUsage
**Severity:** Warning
**Threshold:** > 85% memory usage
**Duration:** 10 minutes
**Impact:** Potential OOM kills, swapping

**Query:**
```promql
100 * (1 - ((node_memory_MemAvailable_bytes) / (node_memory_MemTotal_bytes))) > 85
```

**Response Actions:**
1. Identify memory hogs: `ps aux --sort=-%mem | head`
2. Check for memory leaks
3. Review container memory limits
4. Clear caches if safe
5. Add more RAM or scale

---

#### LowDiskSpace
**Severity:** Warning
**Threshold:** > 80% disk usage
**Duration:** 10 minutes
**Impact:** Service failures, log loss

**Query:**
```promql
100 - ((node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"} * 100)
/ node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"}) > 80
```

**Response Actions:**
1. Clean Docker images: `docker system prune -a`
2. Clean logs: `find /var/log -type f -name "*.log" -mtime +30 -delete`
3. Clean old backups
4. Review disk usage: `du -sh /* | sort -h`
5. Add disk space

---

#### CriticalDiskSpace
**Severity:** Critical
**Threshold:** > 90% disk usage
**Duration:** 5 minutes
**Impact:** Immediate service failure risk

**Query:**
```promql
100 - ((node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"} * 100)
/ node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"}) > 90
```

**Response Actions:**
1. **URGENT:** Free disk space immediately
2. Stop non-critical services
3. Delete large files: `find / -type f -size +100M`
4. Clean temp files: `rm -rf /tmp/*`
5. Emergency disk expansion

---

#### HighDiskIO
**Severity:** Warning
**Threshold:** > 80% disk I/O time
**Duration:** 15 minutes
**Impact:** Slow database, application performance

**Query:**
```promql
rate(node_disk_io_time_seconds_total[5m]) > 0.8
```

**Response Actions:**
1. Identify I/O intensive processes: `iotop`
2. Check database query patterns
3. Review disk performance: `iostat -x 1`
4. Consider SSD upgrade
5. Optimize queries

---

#### NodeDown
**Severity:** Critical
**Threshold:** Node not responding
**Duration:** 5 minutes
**Impact:** Complete service outage

**Query:**
```promql
up{job="node"} == 0
```

**Response Actions:**
1. Check node status
2. Restart server if needed
3. Check network connectivity
4. Review system logs
5. Failover to backup if available

---

### 6. Container Alerts (`obcms_container_alerts`)

#### HighContainerCPUUsage
**Severity:** Warning
**Threshold:** > 80% CPU in container
**Duration:** 10 minutes
**Impact:** Container throttling, slow performance

**Query:**
```promql
sum(rate(container_cpu_usage_seconds_total{name=~"obcms.*"}[5m])) by (name) * 100 > 80
```

**Response Actions:**
1. Check container logs
2. Review CPU limits in docker-compose
3. Increase CPU allocation
4. Optimize application code
5. Scale out containers

---

#### HighContainerMemoryUsage
**Severity:** Warning
**Threshold:** > 85% of container memory limit
**Duration:** 10 minutes
**Impact:** OOM kills, container restarts

**Query:**
```promql
(container_memory_usage_bytes{name=~"obcms.*"} / container_spec_memory_limit_bytes{name=~"obcms.*"}) * 100 > 85
```

**Response Actions:**
1. Check for memory leaks
2. Review memory limits
3. Increase memory allocation
4. Analyze heap dumps
5. Restart container if needed

---

#### ContainerRestartLoop
**Severity:** Warning
**Threshold:** Multiple restarts in 15 minutes
**Duration:** 10 minutes
**Impact:** Service instability, data loss

**Query:**
```promql
rate(container_last_seen{name=~"obcms.*"}[15m]) > 0
```

**Response Actions:**
1. Check container logs: `docker logs <container>`
2. Review exit codes
3. Check resource limits
4. Verify configuration
5. Check for application crashes

---

## Alert Configuration

### Updating Alert Thresholds

Edit `config/prometheus/alert-rules.yml`:

```yaml
- alert: HighErrorRate
  expr: |
    (sum(rate(django_http_responses_total_by_status_total{job="obcms",status=~"5.."}[5m]))
    / sum(rate(django_http_responses_total_by_status_total{job="obcms"}[5m]))) > 0.01  # Change threshold here
  for: 5m  # Change duration here
```

### Adding New Alerts

```yaml
- alert: CustomAlert
  expr: your_promql_query > threshold
  for: duration
  labels:
    severity: warning|critical|info
    component: application|database|infrastructure
  annotations:
    summary: "Brief description"
    description: "Detailed description with {{ $value }}"
    dashboard: "http://grafana:3000/d/dashboard-uid"
```

### Testing Alerts

**Check alert syntax:**
```bash
promtool check rules config/prometheus/alert-rules.yml
```

**View active alerts:**
```
http://localhost:9090/alerts
```

**Force alert to fire (for testing):**
```bash
# Adjust thresholds temporarily to trigger alert
docker-compose restart prometheus
```

## Notification Channels

### Email Notifications

Configure in `config/prometheus/alertmanager.yml`:

```yaml
receivers:
  - name: email
    email_configs:
      - to: ops-team@example.com
        from: alerts@example.com
        smarthost: smtp.gmail.com:587
        auth_username: alerts@example.com
        auth_password: ${SMTP_PASSWORD}
```

### Slack Notifications

```yaml
receivers:
  - name: slack
    slack_configs:
      - api_url: ${SLACK_WEBHOOK_URL}
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

### PagerDuty Integration

```yaml
receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: ${PAGERDUTY_SERVICE_KEY}
        description: '{{ .CommonAnnotations.summary }}'
```

## Best Practices

1. **Tune alert thresholds** based on baseline metrics
2. **Set appropriate for durations** to avoid flapping
3. **Use severity levels** consistently
4. **Include actionable information** in annotations
5. **Link to dashboards** for quick context
6. **Test alerts** before deploying to production
7. **Review and update** alerts regularly
8. **Avoid alert fatigue** - fewer, meaningful alerts
9. **Document response procedures** for each alert
10. **Implement alert routing** to appropriate teams

## Resources

- [Prometheus Alerting Documentation](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
