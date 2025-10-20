# OBCMS Staging vs Production Environment Comparison

Comprehensive comparison of staging and production Docker Compose configurations.

## Executive Summary

The staging environment provides a production-like environment with **reduced resources** (75% less) while maintaining all critical production services and configurations. This enables thorough testing and validation before production deployment with minimal infrastructure costs.

**Key Metrics:**
- **Memory:** 2GB staging vs 8GB production (75% reduction)
- **CPU:** 5.5 cores staging vs 16 cores production (66% reduction)
- **Target Load:** 10-20 users staging vs 700-1100 users production
- **Cost Savings:** ~80% infrastructure cost reduction

## Service-by-Service Comparison

### Database Layer

#### PostgreSQL

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Instances** | 1 primary only | 1 primary + 2 read replicas | Staging uses single instance |
| **Max Connections** | 100 | 500 | Reduced for lower load |
| **Shared Buffers** | 512MB | 4GB | 87.5% reduction |
| **Effective Cache** | 1536MB | 12GB | 87.2% reduction |
| **Work Memory** | 8MB | 16MB | 50% reduction |
| **Maintenance Work Mem** | 128MB | 512MB | 75% reduction |
| **WAL Size** | 512MB-2GB | 1GB-4GB | Reduced write-ahead log |
| **CPU Limit** | 1.0 core | No limit | Constrained in staging |
| **Memory Limit** | 512MB | No limit | Constrained in staging |
| **High Availability** | No | Yes (replicas) | Testing doesn't need HA |
| **Failover** | Manual | Automatic | Simplified recovery |

**Staging Command:**
```bash
postgres -c max_connections=100 -c shared_buffers=512MB -c effective_cache_size=1536MB
```

**Production Command:**
```bash
postgres -c max_connections=500 -c shared_buffers=4GB -c effective_cache_size=12GB
```

#### PgBouncer (Connection Pooler)

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Backend Databases** | 1 (db only) | 3 (primary + 2 replicas) | No read replica routing |
| **Max Client Connections** | 200 | 1000 | 80% reduction |
| **Default Pool Size** | 25 | 50 | 50% reduction |
| **Pool Mode** | transaction | transaction | Same |
| **CPU Limit** | 0.5 core | No limit | Constrained |
| **Memory Limit** | 128MB | No limit | Constrained |

### Cache Layer

#### Redis

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Architecture** | Single instance | Master + 2 replicas | No replication in staging |
| **Sentinel** | No | 3 sentinels | No automatic failover |
| **Max Memory** | 256MB | 512MB (master) | 50% reduction |
| **Memory Policy** | allkeys-lru | Configured per replica | Simplified |
| **CPU Limit** | 0.5 core | No limit | Constrained |
| **Memory Limit** | 256MB | No limit | Constrained |
| **High Availability** | No | Yes (Sentinel) | Simplified for testing |
| **Automatic Failover** | No | Yes | Manual recovery only |
| **Read Replicas** | No | 2 replicas | No read scaling |

**Staging Command:**
```bash
redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

**Production Command:**
```bash
# Master: redis-server /usr/local/etc/redis/redis.conf
# Replicas: redis-server /usr/local/etc/redis/redis.conf --replicaof redis-master 6379
# Sentinels: redis-sentinel /usr/local/etc/redis/sentinel.conf
```

### Application Layer

#### Django Web Servers

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Instances** | 2 (web1, web2) | 4 (web1-web4) | 50% reduction |
| **Gunicorn Workers** | 4 per instance | 17 per instance | 76% reduction |
| **Gunicorn Threads** | 2 per worker | 2 per worker | Same |
| **Total Workers** | 8 (4×2) | 68 (17×4) | 88% reduction |
| **CPU Limit** | 1.0 core each | No limit | Constrained |
| **Memory Limit** | 512MB each | No limit | Constrained |
| **Settings Module** | staging | production | Different configs |
| **Total Capacity** | ~16 concurrent requests | ~136 concurrent requests | 88% reduction |

**Worker Formula:**
- Staging: `GUNICORN_WORKERS=4` (reduced for resource constraints)
- Production: `GUNICORN_WORKERS=17` (optimal for (2 × 8 cores) + 1)

#### Celery Workers

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Worker Instances** | 1 | 2 | 50% reduction |
| **Concurrency** | 2 tasks | 4 tasks per worker | 50% reduction |
| **Total Concurrency** | 2 tasks | 8 tasks (4×2) | 75% reduction |
| **CPU Limit** | 1.0 core | No limit | Constrained |
| **Memory Limit** | 512MB | No limit | Constrained |
| **Task Timeout** | 300s | 300s | Same |
| **Soft Timeout** | 240s | 240s | Same |
| **Max Tasks/Child** | 1000 | 1000 | Same |

#### Celery Beat (Scheduler)

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Instances** | 1 | 1 | Same (only need one) |
| **CPU Limit** | 0.5 core | No limit | Constrained |
| **Memory Limit** | 256MB | No limit | Constrained |
| **Configuration** | Same | Same | Identical setup |

### Reverse Proxy Layer

#### Nginx

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Configuration File** | load_balancer_staging.conf | load_balancer.conf | Separate configs |
| **Upstream Backends** | 2 (web1, web2) | 4 (web1-web4) | 50% reduction |
| **Keepalive Connections** | 16 | 32 | 50% reduction |
| **Max Connections/IP** | 5 | 10 | 50% reduction |
| **API Rate Limit** | 200 req/min | 100 req/min | 2× more lenient |
| **Login Rate Limit** | 10 req/min | 5 req/min | 2× more lenient |
| **API Burst** | 40 requests | 20 requests | 2× more lenient |
| **Login Burst** | 5 requests | 3 requests | 67% more lenient |
| **Client Max Body** | 50MB | 100MB | 50% reduction |
| **CPU Limit** | 0.5 core | No limit | Constrained |
| **Memory Limit** | 256MB | No limit | Constrained |
| **Custom Header** | X-Environment: staging | (none) | Identifies environment |

### Monitoring Stack (Optional)

#### Prometheus

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Enabled By** | `--profile monitoring` flag | Always on | Optional in staging |
| **Retention Period** | 7 days | 30 days | 76% reduction |
| **CPU Limit** | 0.5 core | No limit | Constrained |
| **Memory Limit** | 256MB | No limit | Constrained |

#### Grafana

| Aspect | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Enabled By** | `--profile monitoring` flag | Always on | Optional in staging |
| **CPU Limit** | 0.5 core | No limit | Constrained |
| **Memory Limit** | 256MB | No limit | Constrained |

## Resource Allocation Summary

### Memory Allocation

| Service | Staging | Production | Reduction |
|---------|---------|------------|-----------|
| PostgreSQL (total) | 512MB | No limit (~6GB) | ~92% |
| PgBouncer | 128MB | No limit (~256MB) | 50% |
| Redis (total) | 256MB | No limit (~1.5GB) | ~83% |
| Web Servers (total) | 1024MB (512×2) | No limit (~8GB) | ~87% |
| Celery Workers (total) | 512MB | No limit (~4GB) | ~87% |
| Celery Beat | 256MB | No limit (~512MB) | 50% |
| Nginx | 256MB | No limit (~512MB) | 50% |
| **TOTAL** | **~2GB** | **~20GB** | **90%** |

### CPU Allocation

| Service | Staging | Production | Notes |
|---------|---------|------------|-------|
| PostgreSQL (total) | 1.0 core | No limit (~8 cores) | Reduced |
| PgBouncer | 0.5 core | No limit (~1 core) | Reduced |
| Redis (total) | 0.5 core | No limit (~2 cores) | Reduced |
| Web Servers (total) | 2.0 cores (1×2) | No limit (~12 cores) | Reduced |
| Celery Workers (total) | 1.0 core | No limit (~4 cores) | Reduced |
| Celery Beat | 0.5 core | No limit (~1 core) | Reduced |
| Nginx | 0.5 core | No limit (~2 cores) | Reduced |
| **TOTAL** | **~5.5 cores** | **~30 cores** | **82%** |

## Configuration Differences

### Environment Variables

| Variable | Staging | Production |
|----------|---------|------------|
| `DJANGO_SETTINGS_MODULE` | `obc_management.settings.staging` | `obc_management.settings.production` |
| `ALLOWED_HOSTS` | `staging.domain.com` | `domain.com,www.domain.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://staging.domain.com` | `https://domain.com,https://www.domain.com` |
| `BASE_URL` | `https://staging.domain.com` | `https://domain.com` |
| `POSTGRES_DB` | `obcms_staging` | `obcms_prod` |
| `POSTGRES_USER` | `obcms_staging` | `obcms_user` |
| `EMAIL_BACKEND` | `console.EmailBackend` (default) | `smtp.EmailBackend` |
| `FEATURE_PILOT_MODE` | `true` | `false` (optional) |
| `BACKUP_RETENTION_DAYS` | `7` | `30` |

### Docker Compose Files

| Aspect | Staging | Production |
|--------|---------|------------|
| **Filename** | `docker-compose.staging.yml` | `docker-compose.prod.yml` |
| **Services Count** | 9 core + 5 monitoring | 20 core + 6 monitoring |
| **Volumes** | 6 volumes | 11 volumes |
| **Networks** | 1 (obcms_network) | 1 (obcms_network) |
| **Logging** | JSON file, 10m, 3 files | JSON file, 10m, 3 files |
| **Resource Limits** | All services limited | No limits (use all available) |
| **Profiles** | monitoring (optional) | None (all always on) |

### Security Settings

| Setting | Staging | Production | Notes |
|---------|---------|------------|-------|
| **DEBUG** | False (0) | False (0) | Same |
| **SECURE_SSL_REDIRECT** | True | True | Same |
| **SECURE_HSTS_SECONDS** | 604800 (7 days) | 31536000 (1 year) | Reduced for testing |
| **SESSION_COOKIE_SECURE** | True | True | Same |
| **CSRF_COOKIE_SECURE** | True | True | Same |
| **Admin IP Restriction** | No | Optional | More accessible for testing |
| **SSL Certificates** | Self-signed or Let's Encrypt | Let's Encrypt or Enterprise | Flexible in staging |

## Performance Characteristics

### Expected Throughput

| Metric | Staging | Production | Notes |
|--------|---------|------------|-------|
| **Concurrent Users** | 10-20 | 700-1100 | 98% reduction |
| **Requests/Second** | ~50 | ~500 | 90% reduction |
| **Database Queries/Sec** | ~100 | ~2000 | 95% reduction |
| **Page Load Time** | <2s | <1s | Slightly slower |
| **API Response Time** | <500ms | <200ms | Slightly slower |

### Resource Utilization

| Resource | Staging Idle | Staging Load | Production Idle | Production Load |
|----------|--------------|--------------|-----------------|------------------|
| **CPU** | 5-10% | 40-60% | 5-10% | 50-70% |
| **Memory** | ~1.5GB | ~2GB | ~8GB | ~16GB |
| **Disk I/O** | Low | Moderate | Moderate | High |
| **Network** | Low | Moderate | Moderate | Very High |

## Use Cases

### When to Use Staging

✅ **Appropriate:**
- Feature testing before production
- User acceptance testing (UAT)
- Integration testing
- Performance testing (small scale)
- Security testing and audits
- Training and demonstrations
- Development team testing
- Stakeholder previews
- Bug reproduction and debugging

❌ **Not Appropriate:**
- Load testing at production scale
- Stress testing beyond 20 concurrent users
- Performance benchmarking (use production-like resources)
- High-volume data processing
- Production workload simulation

### When to Use Production

✅ **Required:**
- Live production traffic
- Real user workloads
- 700-1100 concurrent users
- High-volume data processing
- 24/7 availability requirements
- Automatic failover and HA
- Performance benchmarking
- Compliance and audit requirements

## Migration Path: Staging → Production

### Promotion Checklist

1. **Testing Complete:**
   - [ ] All features tested in staging
   - [ ] UAT sign-off received
   - [ ] Performance tests passed
   - [ ] Security audit completed
   - [ ] Bug fixes verified

2. **Configuration Ready:**
   - [ ] Production `.env` configured
   - [ ] SSL certificates obtained (Let's Encrypt or enterprise)
   - [ ] Database credentials generated
   - [ ] Email SMTP configured
   - [ ] Domain DNS configured

3. **Infrastructure Ready:**
   - [ ] Production server provisioned (16+ cores, 32+ GB RAM)
   - [ ] Backup strategy implemented
   - [ ] Monitoring configured
   - [ ] Disaster recovery plan documented
   - [ ] Rollback plan prepared

4. **Deployment:**
   - [ ] Deploy to production using `docker-compose.prod.yml`
   - [ ] Run migrations
   - [ ] Verify all services healthy
   - [ ] Test critical user flows
   - [ ] Monitor for 24 hours

### Zero-Downtime Promotion

```bash
# 1. Backup staging data
docker compose -f docker-compose.staging.yml exec db pg_dump -U obcms_staging obcms_staging > staging_final.sql

# 2. Deploy production environment
cd production-server
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 3. Restore staging data to production
cat staging_final.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U obcms_user obcms_prod

# 4. Verify production
curl https://domain.com/health/
```

## Cost Analysis

### Infrastructure Costs (Estimated)

| Environment | CPU | Memory | Disk | Monthly Cost |
|-------------|-----|--------|------|--------------|
| **Staging** | 6 cores | 4-8GB | 50GB | $30-60/month |
| **Production** | 16 cores | 32GB | 200GB | $200-400/month |

**Savings:** Staging costs 70-85% less than production.

### Cloud Provider Estimates

| Provider | Staging Instance | Production Instance | Monthly Cost Difference |
|----------|------------------|---------------------|-------------------------|
| **AWS** | t3.large | m5.4xlarge | ~$70 vs ~$560 = $490 saved |
| **DigitalOcean** | 4GB/2vCPU | 32GB/16vCPU | ~$24 vs ~$320 = $296 saved |
| **Google Cloud** | n1-standard-2 | n1-standard-16 | ~$70 vs ~$570 = $500 saved |

## Command Reference

### Start Services

```bash
# Staging
docker compose -f docker-compose.staging.yml up -d

# Production
docker compose -f docker-compose.prod.yml up -d

# Staging with monitoring
docker compose -f docker-compose.staging.yml --profile monitoring up -d
```

### View Status

```bash
# Staging
docker compose -f docker-compose.staging.yml ps

# Production
docker compose -f docker-compose.prod.yml ps
```

### View Logs

```bash
# Staging
docker compose -f docker-compose.staging.yml logs -f

# Production
docker compose -f docker-compose.prod.yml logs -f
```

### Resource Monitoring

```bash
# Both environments
docker stats
```

## Conclusion

The staging environment provides a **cost-effective, production-like testing environment** with:
- **75% less memory** (2GB vs 8GB)
- **66% fewer CPU cores** (5.5 vs 16)
- **50% fewer web servers** (2 vs 4)
- **80% cost savings** compared to production

This enables **comprehensive testing and validation** before production deployment while minimizing infrastructure costs.

**Recommendation:** Use staging for all testing, validation, and UAT before promoting to production.
