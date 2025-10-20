# Calendar System Deployment Guide

**Version:** 1.0
**Date:** October 1, 2025
**Status:** Production Ready

---

## Overview

This guide provides step-by-step instructions for deploying the integrated calendar system to production.

### System Requirements

**Server:**
- Ubuntu 20.04+ or RHEL 8+
- Python 3.12+
- PostgreSQL 13+
- Redis 6+
- Nginx or Apache
- 2GB RAM minimum (4GB recommended)
- 20GB disk space

**Dependencies:**
```bash
Django==4.2+
celery==5.3+
redis==4.5+
psycopg2-binary==2.9+
qrcode[pil]==7.4+
python-dateutil==2.8+
```

---

## Pre-Deployment Checklist

### 1. Code Preparation

```bash
# Ensure all migrations are created
cd src
./manage.py makemigrations
./manage.py makemigrations common coordination

# Check for issues
./manage.py check --deploy
```

### 2. Environment Variables

Create `.env` file:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=oobc.gov.ph,www.oobc.gov.ph
DATABASE_URL=postgresql://user:pass@localhost/obcms

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@oobc.gov.ph
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@oobc.gov.ph

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Calendar
BASE_URL=https://oobc.gov.ph
CALENDAR_QR_SIZE=10
SHARE_LINK_DEFAULT_EXPIRY_DAYS=30

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 3. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE obcms;
CREATE USER obcms_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE obcms TO obcms_user;
\q

# Run migrations
./manage.py migrate

# Create superuser
./manage.py createsuperuser
```

---

## Installation Steps

### Step 1: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.12 python3.12-venv postgresql redis-server nginx

# RHEL/CentOS
sudo dnf install -y python312 postgresql-server redis nginx
```

### Step 2: Setup Python Environment

```bash
# Create virtual environment
python3.12 -m venv /opt/obcms/venv

# Activate
source /opt/obcms/venv/bin/activate

# Install dependencies
pip install -r requirements/production.txt
```

### Step 3: Install QR Code Library

```bash
pip install qrcode[pil]
```

### Step 4: Configure Static Files

```bash
# Collect static files
./manage.py collectstatic --noinput

# Set permissions
chown -R www-data:www-data /opt/obcms/static
```

---

## Celery Setup

### 1. Install Celery & Redis

```bash
pip install celery[redis]==5.3.4
sudo systemctl start redis
sudo systemctl enable redis
```

### 2. Create Celery Service

Create `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Service
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/opt/obcms/src
Environment="PATH=/opt/obcms/venv/bin"
ExecStart=/opt/obcms/venv/bin/celery -A obc_management worker --loglevel=info --detach
ExecStop=/opt/obcms/venv/bin/celery -A obc_management control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Create Celery Beat Service

Create `/etc/systemd/system/celerybeat.service`:

```ini
[Unit]
Description=Celery Beat Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/obcms/src
Environment="PATH=/opt/obcms/venv/bin"
ExecStart=/opt/obcms/venv/bin/celery -A obc_management beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl start celerybeat
sudo systemctl enable celery
sudo systemctl enable celerybeat

# Check status
sudo systemctl status celery
sudo systemctl status celerybeat
```

---

## Web Server Configuration

### Nginx Configuration

Create `/etc/nginx/sites-available/obcms`:

```nginx
upstream obcms_server {
    server unix:/opt/obcms/obcms.sock fail_timeout=0;
}

server {
    listen 80;
    server_name oobc.gov.ph www.oobc.gov.ph;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name oobc.gov.ph www.oobc.gov.ph;

    ssl_certificate /etc/letsencrypt/live/oobc.gov.ph/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/oobc.gov.ph/privkey.pem;

    client_max_body_size 20M;

    location /static/ {
        alias /opt/obcms/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/obcms/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://obcms_server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/obcms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Application Server (Gunicorn)

### 1. Install Gunicorn

```bash
pip install gunicorn
```

### 2. Create Gunicorn Service

Create `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for OBCMS
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/obcms/src
Environment="PATH=/opt/obcms/venv/bin"
ExecStart=/opt/obcms/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/opt/obcms/obcms.sock \
    --timeout 120 \
    obc_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Start Gunicorn

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

---

## Email Configuration

### Gmail SMTP (Development/Testing)

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Generate at myaccount.google.com/apppasswords
```

### SendGrid (Recommended for Production)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

### AWS SES (Enterprise)

```bash
pip install django-ses

# settings.py
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'ap-southeast-1'
```

---

## Post-Deployment Tasks

### 1. Create Initial Data

```bash
./manage.py shell
```

```python
from common.models import CalendarResource

# Create conference rooms
CalendarResource.objects.create(
    name="Conference Room A",
    resource_type="room",
    capacity=20,
    location="Main Office, 2nd Floor",
    status="available"
)

CalendarResource.objects.create(
    name="Conference Room B",
    resource_type="room",
    capacity=10,
    location="Main Office, 3rd Floor",
    status="available"
)

# Create vehicles
CalendarResource.objects.create(
    name="Service Vehicle 1",
    resource_type="vehicle",
    location="Motor Pool",
    status="available"
)
```

### 2. Test Email Notifications

```bash
./manage.py shell
```

```python
from common.tasks import debug_task
result = debug_task.delay()
print(result.get(timeout=10))  # Should print: "Celery is working!"
```

### 3. Test Calendar Features

Visit these URLs:
- https://oobc.gov.ph/oobc-management/calendar/
- https://oobc.gov.ph/oobc-management/calendar/resources/
- https://oobc.gov.ph/oobc-management/calendar/preferences/
- https://oobc.gov.ph/oobc-management/staff/leave/

---

## Monitoring & Logging

### 1. Setup Logging

```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/obcms/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/obcms/celery.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['celery'],
            'level': 'INFO',
        },
    },
}
```

### 2. Monitor Celery

```bash
# View worker status
celery -A obc_management inspect active

# View scheduled tasks
celery -A obc_management inspect scheduled

# Monitor in real-time
celery -A obc_management events
```

### 3. Setup Flower (Celery Monitoring)

```bash
pip install flower

# Run Flower
celery -A obc_management flower --port=5555

# Access at: http://localhost:5555
```

---

## Backup & Restore

### Database Backup

```bash
# Backup
pg_dump obcms > backup_$(date +%Y%m%d).sql

# Restore
psql obcms < backup_20251001.sql
```

### Automated Backups (Cron)

```bash
# Add to crontab
0 2 * * * /usr/bin/pg_dump obcms > /backups/obcms_$(date +\%Y\%m\%d).sql
```

---

## Troubleshooting

### Issue: Celery tasks not running

```bash
# Check Redis
redis-cli ping  # Should return PONG

# Check Celery worker
sudo systemctl status celery
sudo journalctl -u celery -n 50

# Restart services
sudo systemctl restart redis celery celerybeat
```

### Issue: Email not sending

```bash
# Test SMTP connection
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'Test message',
    'noreply@oobc.gov.ph',
    ['your-email@example.com'],
    fail_silently=False,
)
```

### Issue: QR codes not generating

```bash
# Install PIL dependencies
sudo apt install -y python3-pil libjpeg-dev zlib1g-dev

# Reinstall qrcode
pip uninstall qrcode
pip install qrcode[pil]
```

### Issue: Static files not loading

```bash
# Check permissions
ls -la /opt/obcms/static/

# Recollect
./manage.py collectstatic --clear --noinput
```

---

## Security Hardening

### 1. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. Fail2Ban

```bash
sudo apt install fail2ban

# Configure for Nginx
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d oobc.gov.ph -d www.oobc.gov.ph

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Performance Optimization

### 1. Database Indexing

```sql
-- Add indexes for calendar queries
CREATE INDEX idx_event_start_date ON coordination_event(start_datetime);
CREATE INDEX idx_booking_resource ON common_calendarresourcebooking(resource_id);
CREATE INDEX idx_leave_staff ON common_staffleave(staff_id);
```

### 2. Redis Caching

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache calendar payload
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # 5 minutes
def oobc_calendar(request):
    # ...
```

### 3. Gunicorn Workers

```bash
# Calculate workers: (2 x CPU cores) + 1
# For 4 cores: (2 x 4) + 1 = 9 workers

gunicorn --workers 9 --bind unix:/opt/obcms/obcms.sock obc_management.wsgi:application
```

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop services
sudo systemctl stop gunicorn celery celerybeat

# 2. Restore database
psql obcms < backup_before_deploy.sql

# 3. Restore code
git checkout <previous-commit-hash>

# 4. Restart services
sudo systemctl start gunicorn celery celerybeat
```

---

## Maintenance Mode

Create maintenance page:

```nginx
# In Nginx config, add before location /:
if (-f /opt/obcms/maintenance.html) {
    return 503;
}

error_page 503 @maintenance;
location @maintenance {
    root /opt/obcms;
    rewrite ^(.*)$ /maintenance.html break;
}
```

Enable:

```bash
touch /opt/obcms/maintenance.html
```

Disable:

```bash
rm /opt/obcms/maintenance.html
```

---

## Conclusion

The calendar system is now deployed and ready for production use. Monitor logs and performance metrics regularly.

**Support:** For issues, contact the development team or create a ticket in the issue tracker.

**Documentation:** See `/docs/` for feature-specific guides.
