# Quick Security Deployment Guide

**CRITICAL:** This guide covers the essential security configurations for OBCMS production deployment.

---

## Pre-Deployment (10 minutes)

### 1. Generate Passwords

```bash
# Redis password
REDIS_PASSWORD=$(openssl rand -base64 32)
echo "REDIS_PASSWORD=${REDIS_PASSWORD}"

# Database password
POSTGRES_PASSWORD=$(openssl rand -base64 32)
echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}"

# Save these to your password manager!
```

### 2. Update `.env` File

```bash
# Edit .env file
nano .env

# Add/update these lines:
REDIS_PASSWORD=<paste-generated-password>
POSTGRES_PASSWORD=<paste-generated-password>
DB_SSLMODE=require

# Redis URLs with authentication
REDIS_URL=redis://:${REDIS_PASSWORD}@redis-master:6379/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis-master:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis-master:6379/1
```

### 3. Verify Configuration

```bash
# Check .env is NOT in git
git check-ignore .env
# Should output: .env

# Verify passwords are set
grep "REDIS_PASSWORD" .env
grep "POSTGRES_PASSWORD" .env
```

---

## Deployment (5 minutes)

### 1. Deploy Services

```bash
# Stop existing services
docker-compose -f docker-compose.prod.yml down

# Pull latest code
git pull origin main

# Rebuild with new configurations
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 2. Monitor Logs

```bash
# Watch for errors during startup
docker-compose -f docker-compose.prod.yml logs -f

# Press Ctrl+C to stop watching
```

---

## Verification (5 minutes)

### Quick Tests

```bash
# 1. Test Redis authentication
docker exec obcms-redis-master redis-cli -a "${REDIS_PASSWORD}" ping
# Expected: PONG

# 2. Test database SSL
docker exec obcms-web python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT ssl_is_used()')
print('SSL ENABLED' if cursor.fetchone()[0] else 'SSL DISABLED')
"
# Expected: SSL ENABLED

# 3. Test Celery connection
docker exec obcms-celery-worker celery -A obc_management inspect ping
# Expected: pong response

# 4. Run Django checks
docker exec obcms-web python manage.py check --deploy
# Expected: No critical issues

# 5. Verify web service is accessible
curl -I https://your-domain.com
# Expected: HTTP 200 or 301/302
```

---

## Accessing Monitoring Tools

Grafana and Prometheus now require SSH tunneling:

```bash
# Create SSH tunnels
ssh -L 3000:localhost:3000 -L 9090:localhost:9090 user@your-server.com

# Then open in browser:
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

---

## Troubleshooting

### Redis Connection Error

```bash
# Error: NOAUTH Authentication required

# Check environment variable
docker exec obcms-redis-master env | grep REDIS_PASSWORD

# Restart Redis services
docker-compose restart redis-master redis-replica1 redis-replica2
```

### Database SSL Error

```bash
# Check SSL is enabled
docker exec obcms-db psql -U postgres -c "SHOW ssl;"
# Should show: on

# Restart web services
docker-compose restart web1 web2 web3 web4
```

### Service Won't Start

```bash
# View detailed logs
docker-compose logs <service-name>

# Check healthcheck
docker inspect <container-name> | grep -A 10 Health
```

---

## Emergency Rollback

**Only if critical issues occur:**

```bash
# Find previous working commit
git log --oneline -5

# Checkout previous version
git checkout <commit-hash>

# Redeploy
docker-compose down
docker-compose up -d --build
```

---

## Security Checklist

Before marking deployment as complete:

- [ ] Redis password is set and working
- [ ] Database SSL is enabled
- [ ] All services are healthy (docker-compose ps)
- [ ] No authentication errors in logs
- [ ] Web application is accessible
- [ ] Celery workers are running
- [ ] Django deployment checks pass
- [ ] Monitoring tools accessible via SSH tunnel
- [ ] Passwords saved in password manager
- [ ] `.env` file NOT in git

---

## Support

**Full Documentation:**
- `/docs/security/INFRASTRUCTURE_SECURITY_CONFIG.md`
- `/docs/security/INFRASTRUCTURE_SECURITY_IMPLEMENTATION_SUMMARY.md`

**Contact:**
- Technical: support@oobc.gov.ph
- Security: security@oobc.gov.ph
