# OBCMS Staging Environment - Quick Start Guide

Fast-track guide to deploy OBCMS staging environment in 10 minutes.

## Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- Server with 4+ CPU cores, 4+ GB RAM, 50+ GB disk
- Domain name pointing to your server (for SSL)

## Quick Deployment (10 Steps)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/obcms.git
cd obcms
```

### 2. Configure Environment

```bash
# Copy template
cp .env.staging.example .env

# Generate SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env - Update these CRITICAL variables:
nano .env
```

**Required changes in `.env`:**
```bash
SECRET_KEY=<paste-generated-key-here>
ALLOWED_HOSTS=staging.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://staging.yourdomain.com
POSTGRES_PASSWORD=your-strong-database-password-here
BASE_URL=https://staging.yourdomain.com
```

### 3. Generate SSL Certificates

**Option A: Self-Signed (Testing)**
```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/C=PH/ST=BARMM/O=OOBC/CN=staging.yourdomain.com"
```

**Option B: Let's Encrypt (Public)**
```bash
sudo certbot certonly --standalone -d staging.yourdomain.com
mkdir -p ssl
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem ssl/key.pem
sudo chmod 644 ssl/*.pem
```

### 4. Build and Start Services

```bash
# Build images (5-10 minutes)
docker compose -f docker-compose.staging.yml build

# Start all services
docker compose -f docker-compose.staging.yml up -d

# Monitor startup logs
docker compose -f docker-compose.staging.yml logs -f
```

Wait for all services to show "healthy" status (2-3 minutes).

### 5. Verify Services Running

```bash
# Check status
docker compose -f docker-compose.staging.yml ps

# All services should show "Up (healthy)"
```

### 6. Create Admin User

```bash
# Enter web1 container
docker compose -f docker-compose.staging.yml exec web1 sh

# Create superuser
cd src
python manage.py createsuperuser
# Username: admin
# Email: admin@yourdomain.com
# Password: [your-strong-password]

# Exit container
exit
```

### 7. Test Application

```bash
# Test health endpoint
curl -k https://staging.yourdomain.com/health/
# Should return: {"status": "healthy"}

# Open browser
# URL: https://staging.yourdomain.com
# Login: admin / [password from step 6]
```

### 8. Run Deployment Checks

```bash
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py check --deploy"
# All checks should pass
```

### 9. Verify Background Tasks

```bash
# Check Celery worker
docker compose -f docker-compose.staging.yml logs celery-worker | tail -20

# Check Redis
docker compose -f docker-compose.staging.yml exec redis redis-cli ping
# Should return: PONG
```

### 10. Set Up Backups (Optional)

```bash
# Create backup directory
mkdir -p backups

# Manual database backup
docker compose -f docker-compose.staging.yml exec db pg_dump -U obcms_staging obcms_staging > backups/staging_$(date +%Y%m%d).sql

# Automated daily backup (add to crontab)
crontab -e
# Add line:
# 0 2 * * * cd /path/to/obcms && docker compose -f docker-compose.staging.yml exec -T db pg_dump -U obcms_staging obcms_staging > backups/staging_$(date +\%Y\%m\%d).sql
```

## Common Commands

### View Logs

```bash
# All services
docker compose -f docker-compose.staging.yml logs -f

# Specific service
docker compose -f docker-compose.staging.yml logs -f web1
docker compose -f docker-compose.staging.yml logs -f db
docker compose -f docker-compose.staging.yml logs -f nginx
```

### Restart Services

```bash
# All services
docker compose -f docker-compose.staging.yml restart

# Specific service
docker compose -f docker-compose.staging.yml restart web1
docker compose -f docker-compose.staging.yml restart nginx
```

### Stop/Start Environment

```bash
# Stop all services
docker compose -f docker-compose.staging.yml stop

# Start all services
docker compose -f docker-compose.staging.yml start

# Shutdown and remove containers (preserves data)
docker compose -f docker-compose.staging.yml down

# Start fresh
docker compose -f docker-compose.staging.yml up -d
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.staging.yml up -d --build

# Run new migrations
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py migrate"
```

### Database Access

```bash
# PostgreSQL shell
docker compose -f docker-compose.staging.yml exec db psql -U obcms_staging -d obcms_staging

# Via PgBouncer
docker compose -f docker-compose.staging.yml exec pgbouncer psql -p 6432 -U obcms_staging -d obcms_staging
```

### Django Management Commands

```bash
# Enter Django shell
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py shell"

# Create additional users
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py createsuperuser"

# Collect static files
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py collectstatic --noinput"
```

## Enable Monitoring (Optional)

```bash
# Start Prometheus + Grafana
docker compose -f docker-compose.staging.yml --profile monitoring up -d

# Access Grafana: http://staging.yourdomain.com:3000
# Default login: admin / staging-grafana-password (from .env)

# Access Prometheus: http://staging.yourdomain.com:9090
```

## Resource Usage

**Expected resource consumption:**
- **Memory:** ~2GB total
  - PostgreSQL: 512MB
  - Redis: 256MB
  - Web servers (2x): 512MB each
  - Celery: 512MB
  - Other services: 256MB
- **CPU:** ~5.5 cores
- **Disk:** 10-20GB (depends on media files)

**Monitor resources:**
```bash
docker stats
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose -f docker-compose.staging.yml logs

# Verify .env configuration
cat .env | grep -E "SECRET_KEY|ALLOWED_HOSTS|CSRF_TRUSTED_ORIGINS|POSTGRES_PASSWORD"

# Check SSL certificates
ls -la ssl/cert.pem ssl/key.pem
```

### 403 CSRF Errors

```bash
# Verify CSRF_TRUSTED_ORIGINS includes https:// scheme
cat .env | grep CSRF_TRUSTED_ORIGINS
# Should be: CSRF_TRUSTED_ORIGINS=https://staging.yourdomain.com

# Restart web servers
docker compose -f docker-compose.staging.yml restart web1 web2
```

### Database Connection Errors

```bash
# Test database
docker compose -f docker-compose.staging.yml exec db psql -U obcms_staging -d obcms_staging -c "SELECT 1;"

# Check PgBouncer
docker compose -f docker-compose.staging.yml logs pgbouncer

# Restart database layer
docker compose -f docker-compose.staging.yml restart db pgbouncer
```

### SSL Certificate Errors

```bash
# Regenerate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/C=PH/ST=BARMM/O=OOBC/CN=staging.yourdomain.com"

# Restart Nginx
docker compose -f docker-compose.staging.yml restart nginx
```

## Architecture Overview

```
Internet
    ↓
Nginx (SSL/TLS Termination, Load Balancer)
    ↓
Web1, Web2 (Django/Gunicorn) ←→ Redis (Cache)
    ↓                              ↓
PgBouncer (Connection Pool)    Celery Worker (Background Tasks)
    ↓                              ↓
PostgreSQL (Database)          Celery Beat (Scheduler)
```

## Service Details

| Service | Purpose | Resources |
|---------|---------|-----------|
| **db** | PostgreSQL 17 database | 1 CPU, 512MB RAM |
| **pgbouncer** | Connection pooling | 0.5 CPU, 128MB RAM |
| **redis** | Cache & Celery broker | 0.5 CPU, 256MB RAM |
| **web1, web2** | Django application servers | 1 CPU, 512MB RAM each |
| **celery-worker** | Background task processing | 1 CPU, 512MB RAM |
| **celery-beat** | Scheduled task scheduler | 0.5 CPU, 256MB RAM |
| **nginx** | Reverse proxy, SSL, load balancer | 0.5 CPU, 256MB RAM |

## Key Differences from Production

| Feature | Staging | Production |
|---------|---------|------------|
| **Web Servers** | 2 instances | 4 instances |
| **Celery Workers** | 1 worker | 2 workers |
| **PostgreSQL** | Single instance | Primary + 2 replicas |
| **Redis** | Single instance | Master + 2 replicas + 3 sentinels |
| **Memory** | 2GB total | 8GB total |
| **CPU** | 5.5 cores | 16 cores |
| **Target Users** | 10-20 concurrent | 700-1100 concurrent |
| **Purpose** | Testing, UAT | Production workload |

## Next Steps

1. **Load test data** - Import sample data for testing
2. **User acceptance testing** - Invite stakeholders to test
3. **Performance testing** - Run load tests
4. **Security review** - Audit configuration and access controls
5. **Documentation** - Document any customizations
6. **Plan production deployment** - Schedule production cutover

## Documentation Links

- **Full Deployment Guide:** [docs/deployment/STAGING_DEPLOYMENT_GUIDE.md](docs/deployment/STAGING_DEPLOYMENT_GUIDE.md)
- **Production Deployment:** [docs/deployment/deployment-coolify.md](docs/deployment/deployment-coolify.md)
- **Environment Configuration:** [docs/env/staging-complete.md](docs/env/staging-complete.md)

## Support

For issues or questions:
1. Check logs: `docker compose -f docker-compose.staging.yml logs`
2. Review [STAGING_DEPLOYMENT_GUIDE.md](docs/deployment/STAGING_DEPLOYMENT_GUIDE.md)
3. Check [troubleshooting section](#troubleshooting)
4. Contact DevOps team

---

**Staging environment ready! Access at:** https://staging.yourdomain.com
