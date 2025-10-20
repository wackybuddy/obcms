# Prometheus Metrics Integration

This document describes the Prometheus metrics integration for OBCMS using django-prometheus.

## Overview

OBCMS exposes a `/metrics` endpoint that provides comprehensive application metrics in Prometheus format. This enables real-time monitoring of Django application performance, database queries, cache operations, and request patterns.

## Configuration

### 1. Requirements

Added to `requirements/base.txt`:
```
django-prometheus>=2.2.0
```

### 2. Django Settings

Updated `src/obc_management/settings/base.py`:

**INSTALLED_APPS:**
```python
THIRD_PARTY_APPS = [
    "django_prometheus",  # Must be first for metrics collection
    "rest_framework",
    # ... other apps
]
```

**MIDDLEWARE:**
```python
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",  # Must be first
    "django.middleware.security.SecurityMiddleware",
    # ... other middleware
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",  # Must be last
]
```

**PROMETHEUS SETTINGS:**
```python
# Export migration metrics to Prometheus
PROMETHEUS_EXPORT_MIGRATIONS = True
```

### 3. URL Configuration

Updated `src/obc_management/urls.py`:
```python
urlpatterns = [
    # Prometheus metrics endpoint (for monitoring infrastructure)
    path("metrics/", include("django_prometheus.urls")),
    # ... other URLs
]
```

### 4. Prometheus Scrape Configuration

Already configured in `config/prometheus/prometheus.yml`:
```yaml
# Django application servers (custom metrics endpoint)
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

## Available Metrics

The `/metrics` endpoint exposes the following metric categories:

### HTTP Request Metrics
- `django_http_requests_total_by_method_total` - Total HTTP requests by method
- `django_http_requests_total_by_transport_total` - Total HTTP requests by transport
- `django_http_requests_total_by_view_transport_method_total` - Detailed request counts
- `django_http_requests_latency_seconds` - Request latency histograms
- `django_http_requests_before_middlewares_total` - Requests before middleware processing
- `django_http_responses_total_by_status_total` - Responses by HTTP status code
- `django_http_responses_total_by_charset_total` - Responses by charset
- `django_http_responses_streaming_total` - Streaming response count
- `django_http_responses_body_total_bytes` - Total response body bytes

### Database Metrics
- `django_db_query_duration_seconds` - Database query duration histograms
- `django_db_execute_total` - Total database query executions
- `django_db_execute_many_total` - Total bulk query executions
- `django_db_errors_total` - Database error count

### Cache Metrics
- `django_cache_get_total` - Total cache GET operations
- `django_cache_hits_total` - Cache hit count
- `django_cache_misses_total` - Cache miss count
- `django_cache_get_fail_total` - Failed cache GET operations
- `django_cache_set_total` - Total cache SET operations
- `django_cache_delete_total` - Total cache DELETE operations

### Migration Metrics
- `django_migrations_applied_total` - Total applied migrations (when PROMETHEUS_EXPORT_MIGRATIONS = True)
- `django_migrations_unapplied_total` - Total unapplied migrations

### Model Metrics
- `django_model_inserts_total` - Model insert operations
- `django_model_updates_total` - Model update operations
- `django_model_deletes_total` - Model delete operations

## Verification Steps

### 1. Install Dependencies

```bash
cd /Users/saidamenmambayao/apps/obcms
source venv/bin/activate
pip install -r requirements/base.txt
```

### 2. Run Development Server

```bash
cd src
python manage.py runserver
```

### 3. Access Metrics Endpoint

```bash
# View all metrics
curl http://localhost:8000/metrics

# Filter specific metrics
curl http://localhost:8000/metrics | grep django_http_requests_total
curl http://localhost:8000/metrics | grep django_db_query_duration
curl http://localhost:8000/metrics | grep django_cache_hits
```

### 4. Verify Metric Format

Expected output format:
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
```

### 5. Generate Load and Verify Metrics

```bash
# Generate some requests
for i in {1..10}; do
  curl -s http://localhost:8000/health/ > /dev/null
done

# Check request counters increased
curl http://localhost:8000/metrics | grep django_http_requests_total_by_method
```

## Security Considerations

### Production Deployment

In production environments, you should restrict access to the `/metrics` endpoint:

**Option 1: IP Whitelist (Nginx)**
```nginx
location /metrics/ {
    allow 10.0.0.0/8;      # Internal network
    allow 172.16.0.0/12;   # Prometheus server
    deny all;

    proxy_pass http://django;
}
```

**Option 2: Authentication (Django)**
Create a custom middleware or decorator to require authentication:

```python
# In settings/production.py
PROMETHEUS_REQUIRE_AUTH = True

# In custom middleware
if request.path == '/metrics/':
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden()
```

**Option 3: Separate Internal Port**
Run metrics endpoint on a separate internal-only port using Django management command.

## Monitoring Best Practices

### Key Metrics to Alert On

1. **High Error Rate**
   - `django_http_responses_total_by_status_total{status="500"}` > threshold

2. **Slow Requests**
   - `django_http_requests_latency_seconds_bucket{le="1.0"}` / total requests < 0.95 (95th percentile > 1s)

3. **Database Performance**
   - `django_db_query_duration_seconds` p95 > 0.5 seconds
   - `django_db_errors_total` increasing

4. **Cache Performance**
   - Cache hit rate: `django_cache_hits_total` / (`django_cache_hits_total` + `django_cache_misses_total`) < 0.8

5. **Database Connection Pool**
   - Monitor connection exhaustion

### Sample Grafana Dashboard Queries

**Request Rate:**
```promql
rate(django_http_requests_total_by_method_total[5m])
```

**Error Rate:**
```promql
rate(django_http_responses_total_by_status_total{status=~"5.."}[5m])
```

**95th Percentile Request Latency:**
```promql
histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m]))
```

**Cache Hit Rate:**
```promql
rate(django_cache_hits_total[5m]) /
(rate(django_cache_hits_total[5m]) + rate(django_cache_misses_total[5m]))
```

**Database Query Performance:**
```promql
histogram_quantile(0.95, rate(django_db_query_duration_seconds_bucket[5m]))
```

## Troubleshooting

### Metrics Endpoint Returns 404

**Check:**
1. Verify `django_prometheus` is in INSTALLED_APPS
2. Verify `/metrics/` path is in urlpatterns
3. Check if URL routing has conflicts

```bash
cd src
python manage.py show_urls | grep metrics
```

### No Metrics Data Appearing

**Check:**
1. PrometheusBeforeMiddleware is first in MIDDLEWARE
2. PrometheusAfterMiddleware is last in MIDDLEWARE
3. Generate some requests to populate metrics

```bash
# Generate test traffic
for i in {1..100}; do curl -s http://localhost:8000/health/ > /dev/null; done

# Verify metrics
curl http://localhost:8000/metrics | grep django_http
```

### Prometheus Not Scraping Metrics

**Check Prometheus configuration:**
```bash
# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="django-app")'

# Verify connectivity from Prometheus container
docker exec prometheus wget -qO- http://web1:8000/metrics
```

**Common issues:**
- Network connectivity between Prometheus and Django containers
- Incorrect target URLs in prometheus.yml
- Django container not listening on expected port
- Firewall blocking scrape requests

## Integration with OBCMS Infrastructure

The Prometheus metrics endpoint integrates with the existing OBCMS monitoring infrastructure:

1. **Prometheus Server**: Scrapes `/metrics` every 30 seconds from all Django web workers (web1-web4)
2. **Grafana Dashboards**: Visualize Django metrics alongside PostgreSQL, Redis, and Nginx metrics
3. **Alertmanager**: Configured to send alerts based on threshold violations
4. **Service Labels**: All metrics tagged with `service: 'django'` for filtering

## References

- [django-prometheus Documentation](https://github.com/korfuri/django-prometheus)
- [Prometheus Metric Types](https://prometheus.io/docs/concepts/metric_types/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Django Dashboard](https://grafana.com/grafana/dashboards/7752-django-application/)
