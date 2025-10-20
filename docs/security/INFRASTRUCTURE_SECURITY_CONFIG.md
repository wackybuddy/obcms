# Infrastructure Security Configuration

**CRITICAL SECURITY UPDATES: Redis Password Authentication, PostgreSQL SSL, and Service Port Hardening**

This document describes the infrastructure security configurations implemented to protect OBCMS production deployments.

---

## Table of Contents

1. [Redis Security](#redis-security)
2. [PostgreSQL SSL/TLS](#postgresql-ssltls)
3. [Service Port Exposure](#service-port-exposure)
4. [Security Checklist](#security-checklist)
5. [Verification Commands](#verification-commands)

---

## Redis Security

### Overview

Redis is configured with password authentication to prevent unauthorized access. By default, Redis runs WITHOUT password protection, making it vulnerable to:

- **CVE-2025-49844** (CVSS 10.0): Remote Code Execution via unauthenticated Redis access
- Data exfiltration from cache (sessions, task queues)
- Cache poisoning attacks
- Denial of service

### Configuration Files

**Master Configuration:** `/Users/saidamenmambayao/apps/obcms/config/redis/master.conf`

```conf
# Replication configuration (master settings)
# SECURITY: Require password for all Redis operations
requirepass ${REDIS_PASSWORD}
masterauth ${REDIS_PASSWORD}
```

**Replica Configuration:** `/Users/saidamenmambayao/apps/obcms/config/redis/replica.conf`

```conf
# Authentication (REQUIRED: master requires password)
masterauth ${REDIS_PASSWORD}
requirepass ${REDIS_PASSWORD}
```

**Sentinel Configuration:** `/Users/saidamenmambayao/apps/obcms/config/redis/sentinel.conf`

```conf
# Authentication (REQUIRED: Redis requires password)
sentinel auth-pass bmms-master ${REDIS_PASSWORD}
sentinel auth-user bmms-master default
```

### Environment Variables

**Generate a strong Redis password:**

```bash
# Generate 32-byte base64-encoded password
openssl rand -base64 32

# Example output:
# 8x7Kp2mN+Qw9vF3sT1aZ6eR4yU5oI8pL7nB0vC2xH1g=
```

**Set in `.env` file:**

```bash
# Redis Password (CRITICAL: Set strong password for production)
REDIS_PASSWORD=8x7Kp2mN+Qw9vF3sT1aZ6eR4yU5oI8pL7nB0vC2xH1g=

# Redis Connection URLs (include password)
REDIS_URL=redis://:${REDIS_PASSWORD}@redis-master:6379/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis-master:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis-master:6379/1
```

### Docker Compose Configuration

All Redis services require the `REDIS_PASSWORD` environment variable:

```yaml
redis-master:
  image: redis:7-alpine
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}
  healthcheck:
    test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
```

### Django Settings

**Base Settings:** `src/obc_management/settings/base.py`

```python
# Celery uses Redis URLs with authentication
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=env("REDIS_URL", default="redis://localhost:6379/0"))
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=env("REDIS_URL", default="redis://localhost:6379/1"))

# SECURITY: Ensure Redis connection uses password from URL
CELERY_BROKER_USE_SSL = CELERY_BROKER_URL.startswith('rediss://')
CELERY_REDIS_BACKEND_USE_SSL = CELERY_RESULT_BACKEND.startswith('rediss://')
```

### Verification

**Test Redis authentication:**

```bash
# Should fail without password
docker exec obcms-redis-master redis-cli ping
# (error) NOAUTH Authentication required.

# Should succeed with password
docker exec obcms-redis-master redis-cli -a "${REDIS_PASSWORD}" ping
# PONG

# Verify from Django/Celery connection
docker exec obcms-web python manage.py shell -c "from django.core.cache import cache; cache.set('test', 1); print('OK' if cache.get('test') == 1 else 'FAIL')"
# OK

# Test Celery connection
docker exec obcms-celery-worker celery -A obc_management inspect ping
# -> pong
```

---

## PostgreSQL SSL/TLS

### Overview

PostgreSQL connections are encrypted using SSL/TLS to protect data in transit. This is especially important when:

- Database is on a separate server
- Using cloud-hosted databases (AWS RDS, Azure Database, etc.)
- Network traffic could be intercepted

### SSL Modes

| Mode | Description | Certificate Required |
|------|-------------|---------------------|
| `disable` | No encryption (NOT recommended for production) | No |
| `allow` | Try SSL, fallback to unencrypted | No |
| `prefer` | Prefer SSL, fallback to unencrypted | No |
| `require` | Require SSL, no certificate verification (recommended minimum) | No |
| `verify-ca` | Require SSL + verify server certificate | Yes |
| `verify-full` | Require SSL + verify server certificate + hostname | Yes |

**Production Recommendation:** Use `require` as the minimum. Use `verify-ca` or `verify-full` if you have CA certificates from your database provider.

### Configuration

**Environment Variables (`.env`):**

```bash
# PostgreSQL SSL/TLS (Production Recommended)
DB_SSLMODE=require

# Optional: Path to CA certificate (for verify-ca or verify-full)
# DB_SSL_CERT=/path/to/ca-certificate.crt
```

**Django Production Settings:** `src/obc_management/settings/production.py`

```python
# PostgreSQL SSL/TLS encryption for production security
if 'postgres' in DATABASES['default']['ENGINE']:
    # SSL mode: require, verify-ca, or verify-full
    db_sslmode = env.str('DB_SSLMODE', default='require')

    # Only configure SSL options if not using verify-none/disable
    if db_sslmode not in ['disable', 'allow', 'prefer']:
        DATABASES['default']['OPTIONS'] = DATABASES['default'].get('OPTIONS', {})
        DATABASES['default']['OPTIONS'].update({
            'sslmode': db_sslmode,
        })

        # Add SSL certificate if using verify-ca or verify-full
        if db_sslmode in ['verify-ca', 'verify-full']:
            db_ssl_cert = env.str('DB_SSL_CERT', default='')
            if db_ssl_cert:
                DATABASES['default']['OPTIONS']['sslrootcert'] = db_ssl_cert
            else:
                # Use system CA certificates
                DATABASES['default']['OPTIONS']['sslrootcert'] = '/etc/ssl/certs/ca-certificates.crt'
```

### Cloud Database SSL Configuration

**AWS RDS:**

```bash
# Download RDS CA certificate
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -O /app/certs/rds-ca-bundle.pem

# Set environment variables
DB_SSLMODE=verify-full
DB_SSL_CERT=/app/certs/rds-ca-bundle.pem
```

**Azure Database for PostgreSQL:**

```bash
# Download Azure CA certificate
wget https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem -O /app/certs/azure-ca.pem

# Set environment variables
DB_SSLMODE=verify-full
DB_SSL_CERT=/app/certs/azure-ca.pem
```

### Verification

**Check SSL connection in Django:**

```bash
docker exec obcms-web python manage.py shell
```

```python
from django.db import connection

# Check if SSL is enabled
cursor = connection.cursor()
cursor.execute("SHOW ssl")
print(cursor.fetchone())
# ('on',)

# Check SSL cipher (only available if SSL is active)
cursor.execute("SELECT ssl_cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
print(cursor.fetchone())
# ('ECDHE-RSA-AES256-GCM-SHA384',)  # Example cipher
```

**Direct PostgreSQL check:**

```bash
docker exec obcms-db psql -U obcms_user -d obcms_prod -c "SELECT ssl_is_used();"
#  ssl_is_used
# -------------
#  t
# (1 row)
```

---

## Service Port Exposure

### Security Principle

Only publicly-required services should expose ports. Internal services should communicate via Docker networks only.

### Port Restrictions

**Removed External Exposure:**

| Service | Old Port | New Configuration | Access Method |
|---------|----------|-------------------|---------------|
| PgBouncer | `6432:6432` | Internal only | SSH tunnel |
| Prometheus | `9090:9090` | `127.0.0.1:9090:9090` | SSH tunnel |
| Grafana | `3000:3000` | `127.0.0.1:3000:3000` | SSH tunnel |

**Still Exposed (Required):**

| Service | Port | Purpose |
|---------|------|---------|
| Nginx | `80:80`, `443:443` | Public web access (HTTP/HTTPS) |

### Docker Compose Changes

**PgBouncer (Connection Pooler):**

```yaml
pgbouncer:
  image: edoburu/pgbouncer:latest
  # SECURITY: Port removed - internal Docker network only
  # Use SSH tunnel for external access: ssh -L 6432:localhost:6432 user@server
  # ports:
  #   - "6432:6432"  # REMOVED
  networks:
    - obcms_network
```

**Prometheus (Metrics):**

```yaml
prometheus:
  image: prom/prometheus:latest
  # SECURITY: Restrict to localhost only - use SSH tunnel for remote access
  ports:
    - "127.0.0.1:9090:9090"  # Changed from "9090:9090"
```

**Grafana (Dashboards):**

```yaml
grafana:
  image: grafana/grafana:latest
  # SECURITY: Restrict to localhost only - use SSH tunnel for remote access
  ports:
    - "127.0.0.1:3000:3000"  # Changed from "3000:3000"
```

### Accessing Restricted Services

Use SSH tunneling to access localhost-only services from your local machine:

**SSH Tunnel Commands:**

```bash
# Access Grafana (dashboards)
ssh -L 3000:localhost:3000 user@obcms-server.com
# Then open: http://localhost:3000

# Access Prometheus (metrics)
ssh -L 9090:localhost:9090 user@obcms-server.com
# Then open: http://localhost:9090

# Access PgBouncer (database connection pool)
ssh -L 6432:localhost:6432 user@obcms-server.com
# Then connect: psql -h localhost -p 6432 -U obcms_user obcms_prod

# Multiple tunnels at once
ssh -L 3000:localhost:3000 -L 9090:localhost:9090 -L 6432:localhost:6432 user@obcms-server.com
```

**Configure SSH for easier access (`~/.ssh/config`):**

```
Host obcms-prod
    HostName obcms-server.com
    User deploy
    Port 22
    LocalForward 3000 localhost:3000
    LocalForward 9090 localhost:9090
    LocalForward 6432 localhost:6432
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Then simply: `ssh obcms-prod` (tunnels automatically created)

---

## Security Checklist

### Pre-Deployment

- [ ] Generate strong Redis password: `openssl rand -base64 32`
- [ ] Set `REDIS_PASSWORD` in production `.env`
- [ ] Generate strong database password: `openssl rand -base64 32`
- [ ] Set `POSTGRES_PASSWORD` in production `.env`
- [ ] Configure PostgreSQL SSL mode: `DB_SSLMODE=require` (minimum)
- [ ] Download CA certificates if using `verify-ca` or `verify-full`
- [ ] Verify `.env` file is NOT committed to git (in `.gitignore`)
- [ ] Review `docker-compose.prod.yml` for exposed ports
- [ ] Set up SSH key authentication for server access
- [ ] Configure firewall to allow only SSH (22), HTTP (80), HTTPS (443)

### Post-Deployment

- [ ] Verify Redis authentication works (see verification commands)
- [ ] Test database SSL connection (see verification commands)
- [ ] Confirm PgBouncer is NOT externally accessible: `nmap -p 6432 your-server.com`
- [ ] Confirm Prometheus requires SSH tunnel: `curl http://your-server.com:9090` (should fail)
- [ ] Confirm Grafana requires SSH tunnel: `curl http://your-server.com:3000` (should fail)
- [ ] Test SSH tunneling to access Grafana/Prometheus
- [ ] Update all service healthchecks with Redis password
- [ ] Monitor logs for authentication errors: `docker-compose logs -f`
- [ ] Run security audit: `docker exec obcms-web python manage.py check --deploy`

### Regular Maintenance

- [ ] Rotate Redis password quarterly
- [ ] Rotate database password quarterly
- [ ] Review PostgreSQL SSL certificate expiry (if using verify-ca/verify-full)
- [ ] Audit service port exposure: `docker-compose ps`
- [ ] Review Docker network security
- [ ] Update Redis to latest stable version
- [ ] Update PostgreSQL to latest stable version
- [ ] Review and update firewall rules
- [ ] Check for CVEs affecting Redis, PostgreSQL, Docker

---

## Verification Commands

### Redis Security

```bash
# Test Redis password authentication
docker exec obcms-redis-master redis-cli -a "${REDIS_PASSWORD}" ping
# Expected: PONG

# Test Redis connection from Django
docker exec obcms-web python manage.py shell -c "
from django.core.cache import cache
cache.set('security_test', 'OK', 60)
print('PASS' if cache.get('security_test') == 'OK' else 'FAIL')
"
# Expected: PASS

# Test Celery worker connection
docker exec obcms-celery-worker celery -A obc_management inspect ping
# Expected: pong response

# Verify Redis password is set in master config
docker exec obcms-redis-master redis-cli -a "${REDIS_PASSWORD}" CONFIG GET requirepass
# Expected: requirepass, <password-hash>

# Check Redis Sentinel authentication
docker exec obcms-redis-sentinel1 redis-cli -p 26379 SENTINEL masters
# Should list bmms-master without errors
```

### PostgreSQL SSL

```bash
# Check SSL is enabled in PostgreSQL
docker exec obcms-db psql -U obcms_user -d obcms_prod -c "SHOW ssl;"
# Expected: on

# Check Django database connection uses SSL
docker exec obcms-web python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT ssl_is_used()')
print('SSL Enabled' if cursor.fetchone()[0] else 'SSL DISABLED')
"
# Expected: SSL Enabled

# View SSL cipher being used
docker exec obcms-db psql -U obcms_user -d obcms_prod -c "
SELECT datname, usename, ssl, ssl_version, ssl_cipher
FROM pg_stat_ssl
JOIN pg_stat_activity ON pg_stat_ssl.pid = pg_stat_activity.pid
WHERE datname = 'obcms_prod';"
```

### Port Exposure

```bash
# Verify PgBouncer is NOT publicly accessible
nmap -p 6432 your-server.com
# Expected: filtered or closed

# Verify Prometheus is NOT publicly accessible
curl http://your-server.com:9090
# Expected: Connection refused or timeout

# Verify Grafana is NOT publicly accessible
curl http://your-server.com:3000
# Expected: Connection refused or timeout

# Verify Nginx IS publicly accessible
curl -I http://your-server.com
# Expected: HTTP 200 or 301/302 redirect

# List all exposed ports
docker-compose ps
# Only nginx should show 80:80 and 443:443

# Check what's listening on server
sudo netstat -tulpn | grep LISTEN
# Should show: 22 (SSH), 80 (HTTP), 443 (HTTPS)
# Should NOT show: 3000, 6432, 9090
```

### Complete Security Audit

```bash
# Run Django deployment checks
docker exec obcms-web python manage.py check --deploy
# Expected: No critical security issues

# Verify SECRET_KEY is strong
docker exec obcms-web python manage.py shell -c "
from django.conf import settings
key = settings.SECRET_KEY
print('PASS' if len(key) >= 50 and not key.startswith('django-insecure') else 'FAIL: Weak SECRET_KEY')
"

# Check Redis memory usage and health
docker exec obcms-redis-master redis-cli -a "${REDIS_PASSWORD}" INFO memory | head -20

# Check database connection pool status
docker exec obcms-pgbouncer psql -h localhost -p 6432 -U obcms_user -d pgbouncer -c "SHOW POOLS;"

# Review recent security-related logs
docker-compose logs --tail=100 | grep -i "auth\|security\|error\|fail"
```

---

## Troubleshooting

### Redis Connection Errors

**Error:** `NOAUTH Authentication required`

**Solution:**

1. Verify `REDIS_PASSWORD` is set in `.env`
2. Check Redis configuration has `requirepass ${REDIS_PASSWORD}`
3. Restart Redis services: `docker-compose restart redis-master redis-replica1 redis-replica2`
4. Verify Django `REDIS_URL` includes password: `redis://:password@redis-master:6379/0`

**Error:** `Connection refused`

**Solution:**

1. Check Redis is running: `docker-compose ps redis-master`
2. Check Redis healthcheck: `docker inspect obcms-redis-master | grep Health -A 10`
3. View Redis logs: `docker-compose logs redis-master`

### PostgreSQL SSL Errors

**Error:** `SSL connection is required`

**Solution:**

1. Set `DB_SSLMODE=require` in `.env`
2. Restart web services: `docker-compose restart web1 web2 web3 web4`
3. Verify database supports SSL: `docker exec obcms-db psql -U postgres -c "SHOW ssl;"`

**Error:** `Root certificate file does not exist`

**Solution:**

1. Download CA certificate for your database provider
2. Mount certificate in Docker: `-v ./certs:/app/certs:ro`
3. Set `DB_SSL_CERT=/app/certs/ca-certificate.pem`

### Port Access Issues

**Error:** Cannot access Grafana/Prometheus remotely

**Solution:**

This is by design. Use SSH tunneling:

```bash
ssh -L 3000:localhost:3000 -L 9090:localhost:9090 user@your-server.com
```

Then access `http://localhost:3000` (Grafana) and `http://localhost:9090` (Prometheus).

---

## References

- [Redis Security Documentation](https://redis.io/docs/management/security/)
- [PostgreSQL SSL Documentation](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [Django Database SSL](https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

**Last Updated:** 2025-10-20

**Security Contact:** security@oobc.gov.ph
