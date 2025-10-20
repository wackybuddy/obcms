# Prometheus Metrics - Quick Reference

## Installation Summary

### 1. Updated Files

**requirements/base.txt:**
```
django-prometheus>=2.2.0
```

**src/obc_management/settings/base.py:**
- Added `"django_prometheus"` to INSTALLED_APPS (first position)
- Added `PrometheusBeforeMiddleware` to MIDDLEWARE (first position)
- Added `PrometheusAfterMiddleware` to MIDDLEWARE (last position)
- Added `PROMETHEUS_EXPORT_MIGRATIONS = True`

**src/obc_management/urls.py:**
```python
path("metrics/", include("django_prometheus.urls")),
```

**config/prometheus/prometheus.yml:**
- Django scrape job already configured at lines 56-66

### 2. Verification Commands

```bash
# Install dependency
cd /Users/saidamenmambayao/apps/obcms
source venv/bin/activate
pip install django-prometheus>=2.2.0

# Run development server
cd src
python manage.py runserver

# Access metrics endpoint
curl http://localhost:8000/metrics

# Filter specific metrics
curl http://localhost:8000/metrics | grep django_http_requests_total
curl http://localhost:8000/metrics | grep django_db_query_duration
curl http://localhost:8000/metrics | grep django_cache_hits
curl http://localhost:8000/metrics | grep django_migrations
```

## Key Metrics Categories

### HTTP Metrics
- `django_http_requests_total_by_method_total` - Request counts by method
- `django_http_requests_latency_seconds` - Request latency histograms
- `django_http_responses_total_by_status_total` - Response counts by status

### Database Metrics
- `django_db_query_duration_seconds` - Query duration histograms
- `django_db_execute_total` - Total query executions
- `django_db_errors_total` - Database errors

### Cache Metrics (Redis)
- `django_cache_hits_total` - Cache hits
- `django_cache_misses_total` - Cache misses
- `django_cache_get_total` - Total GET operations
- `django_cache_set_total` - Total SET operations

### Migration Metrics
- `django_migrations_applied_total` - Applied migrations
- `django_migrations_unapplied_total` - Pending migrations

## Prometheus Scrape Job

Already configured in `config/prometheus/prometheus.yml`:

```yaml
- job_name: 'django-app'
  static_configs:
    - targets:
        - 'web1:8000'
        - 'web2:8000'
        - 'web3:8000'
        - 'web4:8000'
      labels:
        service: 'django'
  metrics_path: '/metrics'
  scrape_interval: 30s
```

## Expected Metric Format

```
# HELP django_http_requests_total_by_method_total Count of requests by method
# TYPE django_http_requests_total_by_method_total counter
django_http_requests_total_by_method_total{method="GET"} 42.0
django_http_requests_total_by_method_total{method="POST"} 13.0

# HELP django_http_requests_latency_seconds Histogram of request latency
# TYPE django_http_requests_latency_seconds histogram
django_http_requests_latency_seconds_bucket{le="0.005"} 15.0
django_http_requests_latency_seconds_bucket{le="0.01"} 28.0
django_http_requests_latency_seconds_sum 5.123
django_http_requests_latency_seconds_count 42.0

# HELP django_db_query_duration_seconds Histogram of database query duration
# TYPE django_db_query_duration_seconds histogram
django_db_query_duration_seconds_bucket{le="0.001"} 120.0
django_db_query_duration_seconds_sum 2.456
django_db_query_duration_seconds_count 150.0
```

## Testing Metrics Collection

```bash
# 1. Start server
cd src
python manage.py runserver

# 2. Generate test traffic
for i in {1..50}; do
  curl -s http://localhost:8000/health/ > /dev/null
done

# 3. Check request metrics
curl http://localhost:8000/metrics | grep django_http_requests_total_by_method

# 4. Verify database metrics (trigger some DB queries)
curl -s http://localhost:8000/dashboard/ > /dev/null
curl http://localhost:8000/metrics | grep django_db_query_duration

# 5. Verify cache metrics
curl http://localhost:8000/metrics | grep django_cache
```

## Common PromQL Queries

### Request Rate (requests per second)
```promql
rate(django_http_requests_total_by_method_total[5m])
```

### Error Rate (5xx errors per second)
```promql
rate(django_http_responses_total_by_status_total{status=~"5.."}[5m])
```

### 95th Percentile Latency
```promql
histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m]))
```

### Cache Hit Rate
```promql
rate(django_cache_hits_total[5m]) /
(rate(django_cache_hits_total[5m]) + rate(django_cache_misses_total[5m]))
```

### Database Query Performance (p95)
```promql
histogram_quantile(0.95, rate(django_db_query_duration_seconds_bucket[5m]))
```

## Production Security

### Option 1: Nginx IP Whitelist
```nginx
location /metrics/ {
    allow 10.0.0.0/8;      # Internal network
    allow 172.16.0.0/12;   # Prometheus server
    deny all;
    proxy_pass http://django;
}
```

### Option 2: Django Authentication
Add middleware to require authentication for `/metrics` endpoint in production.

## Documentation

See detailed documentation: `docs/monitoring/PROMETHEUS_INTEGRATION.md`
