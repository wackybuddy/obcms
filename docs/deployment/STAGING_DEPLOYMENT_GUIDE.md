# OBCMS Staging Deployment Guide

Complete guide for deploying the OBCMS staging environment using Docker Compose.

## Overview

The staging environment is a production-like environment with reduced resources for testing and validation before production deployment. It includes all production services but with scaled-down configurations suitable for 10-20 concurrent users.

### Architecture

**Services:**
- **Database:** Single PostgreSQL 17 instance (no replicas)
- **Connection Pooling:** PgBouncer (single DB backend)
- **Cache:** Single Redis instance (no replication/sentinels)
- **Web Servers:** 2 Django/Gunicorn instances (web1, web2)
- **Background Workers:** 1 Celery worker + 1 Celery Beat scheduler
- **Reverse Proxy:** Nginx with SSL/TLS
- **Monitoring (Optional):** Prometheus + Grafana

**Resource Allocation:**
- **Total Memory:** ~2GB (vs 8GB for production)
- **Total CPU:** ~5.5 cores (vs 16 cores for production)
- **Target Load:** 10-20 concurrent users
- **Purpose:** Testing, validation, UAT

## Prerequisites

### Required Software
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for SSL certificate generation)

### Server Requirements
- **Minimum:** 4 CPU cores, 4GB RAM, 50GB disk
- **Recommended:** 8 CPU cores, 8GB RAM, 100GB disk
- **OS:** Ubuntu 22.04 LTS or similar Linux distribution

## Pre-Deployment Steps

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/obcms.git
cd obcms
```

### 2. Checkout Appropriate Branch

```bash
# For staging, typically use main or develop branch
git checkout main

# Verify you're on the correct branch
git branch
```

### 3. Generate Environment Configuration

```bash
# Copy staging environment template
cp .env.staging.example .env

# Generate a new SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env with your configuration
nano .env  # or vim, code, etc.
```

### 4. Configure Environment Variables

**CRITICAL:** Update the following variables in `.env`:

```bash
# Django Core
SECRET_KEY=your-generated-secret-key-minimum-50-characters
ALLOWED_HOSTS=staging.yourdomain.com,staging-www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://staging.yourdomain.com,https://staging-www.yourdomain.com

# Database
POSTGRES_DB=obcms_staging
POSTGRES_USER=obcms_staging
POSTGRES_PASSWORD=your-strong-database-password

# Application
BASE_URL=https://staging.yourdomain.com
DEFAULT_FROM_EMAIL=OBCMS Staging <staging-noreply@yourdomain.com>
```

### 5. Set Up SSL Certificates

#### Option A: Self-Signed Certificates (Development/Internal Testing)

```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=PH/ST=BARMM/L=Cotabato/O=OOBC/OU=IT/CN=staging.yourdomain.com"

# Verify certificates
openssl x509 -in ssl/cert.pem -text -noout
```

#### Option B: Let's Encrypt Certificates (Public Staging)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificate (requires domain pointing to your server)
sudo certbot certonly --standalone \
  -d staging.yourdomain.com \
  -d staging-www.yourdomain.com

# Copy certificates to ssl directory
mkdir -p ssl
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem ssl/key.pem
sudo chmod 644 ssl/*.pem
```

#### Option C: Wildcard Certificates (Enterprise)

```bash
# If you have wildcard certificates (*.yourdomain.com)
mkdir -p ssl
cp /path/to/wildcard/cert.pem ssl/cert.pem
cp /path/to/wildcard/key.pem ssl/key.pem
chmod 644 ssl/*.pem
```

### 6. Configure PgBouncer (Optional Customization)

The default PgBouncer configuration is suitable for staging. To customize:

```bash
# Edit PgBouncer configuration if needed
nano config/pgbouncer/pgbouncer.ini
```

**Default Staging Settings:**
- `max_client_conn = 200` (vs 1000 for production)
- `default_pool_size = 25` (vs 50 for production)
- `pool_mode = transaction`

### 7. Verify Directory Structure

```bash
# Ensure all required directories exist
ls -la config/nginx/load_balancer_staging.conf
ls -la config/pgbouncer/pgbouncer.ini
ls -la config/pgbouncer/userlist.txt
ls -la ssl/cert.pem
ls -la ssl/key.pem
```

## Deployment

### 1. Build Docker Images

```bash
# Build all images (this may take 5-10 minutes)
docker compose -f docker-compose.staging.yml build

# Verify images were built
docker images | grep obcms
```

### 2. Start Services

```bash
# Start all services in detached mode
docker compose -f docker-compose.staging.yml up -d

# Monitor logs during startup
docker compose -f docker-compose.staging.yml logs -f
```

**Expected startup sequence:**
1. PostgreSQL starts and becomes healthy (~30 seconds)
2. PgBouncer connects to PostgreSQL (~10 seconds)
3. Redis starts (~5 seconds)
4. Migration job runs (creates database schema, collects static files)
5. Web servers start (~40 seconds)
6. Celery workers start
7. Nginx starts and connects to web servers

### 3. Verify Services are Running

```bash
# Check all services status
docker compose -f docker-compose.staging.yml ps

# Should show all services as "Up" or "healthy"
```

**Expected output:**
```
NAME                STATUS              PORTS
obcms-db            Up (healthy)        5432/tcp
obcms-pgbouncer     Up (healthy)        0.0.0.0:6432->6432/tcp
obcms-redis         Up (healthy)        6379/tcp
obcms-web1          Up (healthy)        8000/tcp
obcms-web2          Up (healthy)        8000/tcp
obcms-celery-worker Up                  8000/tcp
obcms-celery-beat   Up                  8000/tcp
obcms-nginx         Up (healthy)        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 4. Create Initial Superuser

```bash
# Access web1 container shell
docker compose -f docker-compose.staging.yml exec web1 sh

# Navigate to src directory and create superuser
cd src
python manage.py createsuperuser

# Enter admin credentials when prompted
# Username: admin
# Email: admin@yourdomain.com
# Password: [strong password]

# Exit container
exit
```

### 5. Verify Application Access

```bash
# Test HTTP redirect
curl -I http://staging.yourdomain.com
# Should return: 301 Moved Permanently

# Test HTTPS access
curl -k -I https://staging.yourdomain.com
# Should return: 200 OK

# Test health endpoint
curl -k https://staging.yourdomain.com/health/
# Should return: {"status": "healthy"}
```

### 6. Access Web Interface

Open browser and navigate to:
- **Frontend:** https://staging.yourdomain.com
- **Admin:** https://staging.yourdomain.com/admin/
- **Health Check:** https://staging.yourdomain.com/health/

**Login with superuser credentials created in Step 4.**

## Post-Deployment Verification

### 1. Run Deployment Checks

```bash
# Execute Django deployment checks
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py check --deploy"
```

**All checks should pass (no warnings/errors).**

### 2. Verify Database Migrations

```bash
# Check migration status
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py showmigrations"

# All migrations should have [X] applied
```

### 3. Test Static Files

```bash
# Check static files are accessible
curl -k -I https://staging.yourdomain.com/static/css/main.css
# Should return: 200 OK

curl -k -I https://staging.yourdomain.com/static/js/main.js
# Should return: 200 OK
```

### 4. Test Background Tasks (Celery)

```bash
# Check Celery worker is running
docker compose -f docker-compose.staging.yml logs celery-worker

# Check Celery Beat scheduler
docker compose -f docker-compose.staging.yml logs celery-beat

# Verify Redis connection
docker compose -f docker-compose.staging.yml exec redis redis-cli ping
# Should return: PONG
```

### 5. Monitor Resource Usage

```bash
# Check container resource usage
docker stats

# Look for:
# - Memory usage should be ~2GB total
# - CPU usage should be low (<20%) when idle
```

### 6. Test Database Connection Pooling

```bash
# Check PgBouncer stats
docker compose -f docker-compose.staging.yml exec pgbouncer psql -p 6432 -U obcms_staging -c "SHOW POOLS;"

# Verify connections are being pooled
```

## Enable Monitoring (Optional)

To enable Prometheus + Grafana monitoring:

```bash
# Start monitoring stack
docker compose -f docker-compose.staging.yml --profile monitoring up -d

# Access Grafana
# URL: http://staging.yourdomain.com:3000
# Default credentials: admin/staging-grafana-password (from .env)

# Access Prometheus
# URL: http://staging.yourdomain.com:9090
```

**Configure Grafana:**
1. Login to Grafana
2. Add Prometheus data source (http://prometheus:9090)
3. Import pre-configured dashboards from `config/grafana/dashboards/`

## SSL Certificate Renewal

### Let's Encrypt Certificates

```bash
# Certificates auto-renew via certbot cron job
# To manually renew:
sudo certbot renew

# Copy renewed certificates
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem ssl/key.pem

# Reload Nginx
docker compose -f docker-compose.staging.yml exec nginx nginx -s reload
```

### Self-Signed Certificates

```bash
# Regenerate self-signed certificate (annual)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=PH/ST=BARMM/L=Cotabato/O=OOBC/OU=IT/CN=staging.yourdomain.com"

# Restart Nginx
docker compose -f docker-compose.staging.yml restart nginx
```

## Backup and Restore

### Database Backup

```bash
# Create backup
docker compose -f docker-compose.staging.yml exec db pg_dump -U obcms_staging obcms_staging > backups/staging_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backups/

# Automated backups (cron job example)
# Add to crontab: crontab -e
# Daily backup at 2 AM:
# 0 2 * * * cd /path/to/obcms && docker compose -f docker-compose.staging.yml exec -T db pg_dump -U obcms_staging obcms_staging > backups/staging_$(date +\%Y\%m\%d).sql
```

### Database Restore

```bash
# Stop web servers to prevent writes
docker compose -f docker-compose.staging.yml stop web1 web2 celery-worker

# Restore from backup
cat backups/staging_20251020.sql | docker compose -f docker-compose.staging.yml exec -T db psql -U obcms_staging obcms_staging

# Restart services
docker compose -f docker-compose.staging.yml start web1 web2 celery-worker
```

### Media Files Backup

```bash
# Backup media files
docker compose -f docker-compose.staging.yml exec web1 tar -czf /tmp/media_backup.tar.gz -C /app/src media/
docker cp $(docker compose -f docker-compose.staging.yml ps -q web1):/tmp/media_backup.tar.gz backups/media_$(date +%Y%m%d).tar.gz

# Restore media files
docker cp backups/media_20251020.tar.gz $(docker compose -f docker-compose.staging.yml ps -q web1):/tmp/media_backup.tar.gz
docker compose -f docker-compose.staging.yml exec web1 tar -xzf /tmp/media_backup.tar.gz -C /app/src
```

## Updating/Redeployment

### Pull Latest Changes

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker compose -f docker-compose.staging.yml build

# Restart services with new images
docker compose -f docker-compose.staging.yml up -d

# Run migrations (if any)
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py migrate"

# Collect static files (if changed)
docker compose -f docker-compose.staging.yml exec web1 sh -c "cd src && python manage.py collectstatic --noinput"
```

### Zero-Downtime Update

```bash
# Update one web server at a time
docker compose -f docker-compose.staging.yml up -d --no-deps --build web1
# Wait for web1 to be healthy
docker compose -f docker-compose.staging.yml up -d --no-deps --build web2

# Update Celery worker
docker compose -f docker-compose.staging.yml up -d --no-deps --build celery-worker
```

## Troubleshooting

### Services Won't Start

```bash
# View logs
docker compose -f docker-compose.staging.yml logs

# View specific service logs
docker compose -f docker-compose.staging.yml logs db
docker compose -f docker-compose.staging.yml logs web1
docker compose -f docker-compose.staging.yml logs nginx

# Check service health
docker compose -f docker-compose.staging.yml ps
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker compose -f docker-compose.staging.yml exec db psql -U obcms_staging -d obcms_staging -c "SELECT 1;"

# Test PgBouncer connection
docker compose -f docker-compose.staging.yml exec pgbouncer psql -p 6432 -U obcms_staging -d obcms_staging -c "SELECT 1;"

# Check PgBouncer logs
docker compose -f docker-compose.staging.yml logs pgbouncer
```

### 403 CSRF Errors

```bash
# Verify CSRF_TRUSTED_ORIGINS in .env
cat .env | grep CSRF_TRUSTED_ORIGINS

# Must include https:// scheme and match your domain
# Correct: CSRF_TRUSTED_ORIGINS=https://staging.yourdomain.com
# Wrong: CSRF_TRUSTED_ORIGINS=staging.yourdomain.com

# Restart after fixing
docker compose -f docker-compose.staging.yml restart web1 web2
```

### SSL Certificate Issues

```bash
# Verify certificates exist
ls -la ssl/cert.pem ssl/key.pem

# Test certificate validity
openssl x509 -in ssl/cert.pem -noout -dates

# Check Nginx SSL configuration
docker compose -f docker-compose.staging.yml exec nginx nginx -T | grep ssl

# Restart Nginx
docker compose -f docker-compose.staging.yml restart nginx
```

### High Memory Usage

```bash
# Check container memory usage
docker stats

# If PostgreSQL memory is high:
# - Reduce shared_buffers in docker-compose.staging.yml
# - Restart: docker compose -f docker-compose.staging.yml restart db

# If web servers memory is high:
# - Reduce GUNICORN_WORKERS in .env
# - Restart: docker compose -f docker-compose.staging.yml restart web1 web2
```

### Celery Worker Not Processing Tasks

```bash
# Check worker logs
docker compose -f docker-compose.staging.yml logs celery-worker

# Restart worker
docker compose -f docker-compose.staging.yml restart celery-worker

# Check Redis connection
docker compose -f docker-compose.staging.yml exec redis redis-cli ping

# Verify Celery can connect to Redis
docker compose -f docker-compose.staging.yml exec celery-worker sh -c "cd src && python manage.py shell -c 'from django_celery_beat.models import PeriodicTask; print(PeriodicTask.objects.count())'"
```

## Maintenance

### Log Rotation

Logs are automatically rotated using Docker's JSON file driver:
- Max size: 10MB per file
- Max files: 3 files
- Total log storage: ~30MB per service

### Clean Up Old Images

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (CAUTION: Don't delete active volumes)
docker volume prune
```

### Update Docker Images

```bash
# Pull latest base images
docker compose -f docker-compose.staging.yml pull

# Rebuild with new base images
docker compose -f docker-compose.staging.yml build --pull

# Restart services
docker compose -f docker-compose.staging.yml up -d
```

## Resource Scaling

### Increase Memory Limits

Edit `docker-compose.staging.yml`:

```yaml
services:
  db:
    deploy:
      resources:
        limits:
          memory: 1G  # Increase from 512M
```

### Add More Web Servers

Edit `docker-compose.staging.yml` to add `web3`:

```yaml
  web3:
    # Copy web2 configuration
    # Update nginx upstream in config/nginx/load_balancer_staging.conf
```

## Security Considerations

1. **Change Default Passwords:** Update all default passwords in `.env`
2. **Restrict Database Access:** Use firewall rules to limit database port access
3. **Enable HSTS:** Verify SECURE_HSTS_SECONDS is set in `.env`
4. **Regular Updates:** Keep Docker images and base OS updated
5. **Monitor Logs:** Regularly review logs for suspicious activity
6. **Backup Encryption:** Encrypt backup files if stored off-site

## Support and Documentation

- **Main Documentation:** [docs/deployment/](./README.md)
- **Production Deployment:** [docs/deployment/deployment-coolify.md](./deployment-coolify.md)
- **PostgreSQL Migration:** [docs/deployment/POSTGRESQL_MIGRATION_SUMMARY.md](./POSTGRESQL_MIGRATION_SUMMARY.md)
- **Environment Guide:** [docs/env/staging-complete.md](../env/staging-complete.md)

## Summary Checklist

- [ ] Clone repository and checkout correct branch
- [ ] Copy `.env.staging.example` to `.env`
- [ ] Generate and set SECRET_KEY
- [ ] Configure ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS
- [ ] Set database credentials (POSTGRES_USER, POSTGRES_PASSWORD)
- [ ] Generate SSL certificates (self-signed or Let's Encrypt)
- [ ] Verify config files exist (nginx, pgbouncer)
- [ ] Build Docker images
- [ ] Start services with `docker compose up -d`
- [ ] Create superuser account
- [ ] Verify application access via browser
- [ ] Run deployment checks
- [ ] Test static files serving
- [ ] Test Celery background tasks
- [ ] Set up automated backups
- [ ] Configure monitoring (optional)
- [ ] Document credentials in secure location

**Staging environment is now ready for testing and validation!**
