# OOBC Management System - Coolify Deployment Plan

## Overview

This document provides a comprehensive plan for deploying the Other Bangsamoro Communities (OOBC) Management System using Coolify, a self-hosted Platform-as-a-Service (PaaS) solution. Coolify offers an open-source alternative to cloud platforms like Heroku, with zero-downtime deployments and full control over infrastructure.

## Table of Contents

1. [System Analysis](#system-analysis)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Pre-Deployment Preparation](#pre-deployment-preparation)
4. [Coolify Server Setup](#coolify-server-setup)
5. [Application Containerization](#application-containerization)
6. [Database Configuration](#database-configuration)
7. [Environment Configuration](#environment-configuration)
8. [Deployment Process](#deployment-process)
9. [Post-Deployment Configuration](#post-deployment-configuration)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Backup Strategy](#backup-strategy)
12. [Security Considerations](#security-considerations)

## System Analysis

### Current Architecture
- **Framework**: Django 4.2.x
- **Database**: SQLite (development) → PostgreSQL (production)
- **Background Tasks**: Celery with Redis
- **API**: Django REST Framework with JWT authentication
- **Static Files**: Django's static file handling
- **Media Files**: Local file storage
- **External APIs**: Google Generative AI, Google Cloud AI Platform

### Key Dependencies
```
Django>=4.2.0,<4.3.0
djangorestframework>=3.14.0
django-filter>=23.5
django-cors-headers>=4.3.0
django-crispy-forms>=2.0
django-extensions>=3.2.0
djangorestframework-simplejwt>=5.3.0
celery>=5.3.0
redis>=5.0.0
Pillow>=10.0.0
pandas>=2.0.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
reportlab>=4.0.0
google-generativeai>=0.3.0
google-cloud-aiplatform>=1.38.0
```

### Application Structure
```
obcms/
├── src/                          # Django source code
│   ├── manage.py
│   ├── obc_management/          # Main project
│   ├── common/                  # Shared utilities
│   ├── communities/             # Community management
│   ├── mana/                    # Assessment functionality
│   ├── coordination/            # Multi-stakeholder coordination
│   ├── policies/                # Policy recommendations
│   ├── ai_assistant/            # AI integration
│   └── templates/               # Django templates
├── requirements/
│   ├── base.txt
│   └── development.txt
├── deployment/                  # Deployment configs
└── docs/                       # Documentation
```

## Infrastructure Requirements

### Minimum Server Specifications
- **CPU**: 2 vCPU cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 40GB SSD minimum
- **Bandwidth**: Unmetered or generous limits
- **OS**: Ubuntu 22.04 LTS or similar

### Recommended Providers
- **Hetzner**: CAX11 ARM (4GB RAM, €3.79/month) or CX21 (4GB RAM, €4.90/month)
- **DigitalOcean**: Basic Droplet (4GB RAM, $24/month)
- **Linode**: Nanode 4GB ($24/month)
- **Vultr**: Regular Performance (4GB RAM, $24/month)

### Network Requirements
- **Firewall**: UFW or equivalent
- **SSL**: Automatic via Coolify (Let's Encrypt)
- **Domain**: Custom domain name recommended
- **SSH**: Key-based authentication only

## Pre-Deployment Preparation

### 1. Server Security Setup
```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh

# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Install fail2ban
sudo apt update && sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 2. Automatic Security Updates
```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Git Repository Preparation
Ensure your Git repository includes:
- Production-ready requirements.txt with gunicorn
- Environment variable configuration
- Static file collection setup
- Database migration scripts

## Coolify Server Setup

### 1. Installation
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash
```

### 2. Initial Configuration
- Access Coolify web interface (usually on port 8000)
- Complete initial setup wizard
- Configure Git integration
- Set up SSL certificates

### 3. Server Preparation
- Add your server as a destination
- Configure Docker registry if needed
- Set up backup storage (S3-compatible)

## Application Containerization

### 1. Create Production Requirements File
```bash
# requirements/production.txt
-r base.txt
gunicorn>=21.0.0
psycopg2-binary>=2.9.0
whitenoise>=6.0.0
```

### 2. Dockerfile Creation
```dockerfile
# Dockerfile
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set working directory to Django project
WORKDIR /app/src

# Collect static files
RUN python3.12 manage.py collectstatic --noinput --settings=obc_management.settings

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/login/ || exit 1

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "obc_management.wsgi:application"]
```

### 3. .dockerignore File
```
.git/
.gitignore
venv/
*.pyc
__pycache__/
.env
*.log
docs/
README.md
.pytest_cache/
htmlcov/
.coverage
node_modules/
*.sqlite3
```

## Database Configuration

### 1. PostgreSQL Service Setup
- Create PostgreSQL service in Coolify
- Configure database name: `oobc_management`
- Set strong password
- Note connection details

### 2. Database Migration Strategy
```bash
# Export existing data (if applicable)
python3.12 manage.py dumpdata --natural-foreign --natural-primary \
    --exclude contenttypes --exclude auth.Permission \
    --exclude sessions.session --exclude admin.logentry \
    > data_export.json

# Import to new database
python3.12 manage.py loaddata data_export.json
```

### 3. Production Database Settings
```python
# settings.py production additions
import dj_database_url

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Add to ALLOWED_HOSTS
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# Security settings for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
```

## Environment Configuration

### Essential Environment Variables
```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DATABASE_URL=postgres://username:password@hostname:5432/database_name

# Redis/Celery
REDIS_URL=redis://redis-service:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your-smtp-server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password

# External APIs
GOOGLE_API_KEY=your-google-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# File Storage (optional - for cloud storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region

# Application Settings
SITE_NAME=OOBC Management System
SITE_DESCRIPTION=Other Bangsamoro Communities Management System
```

## Deployment Process

### 1. Coolify Application Setup
1. **Create New Application**:
   - Choose "Git Repository" as source
   - Connect your repository
   - Set base directory to `/` (root of repository)

2. **Build Configuration**:
   - Build Pack: `dockerfile`
   - Dockerfile location: `./Dockerfile`
   - Set build-time environment variables if needed

3. **Runtime Configuration**:
   - Set all environment variables
   - Configure health check endpoint: `/admin/login/`
   - Set restart policy to "always"

### 2. Service Dependencies
1. **PostgreSQL Service**:
   - Create dedicated PostgreSQL service
   - Configure backup schedule
   - Note connection string for `DATABASE_URL`

2. **Redis Service**:
   - Create Redis service for Celery
   - Configure persistence if needed
   - Note connection string for `REDIS_URL`

3. **Celery Worker (Optional)**:
   - Create separate service for background tasks
   - Use same Docker image
   - Override command: `celery -A obc_management worker -l info`

### 3. Initial Deployment
1. **Deploy Application**:
   - Trigger initial build and deployment
   - Monitor build logs for errors
   - Verify successful startup

2. **Database Migration**:
   - Access application container
   - Run: `./manage.py migrate`
   - Create superuser: `./manage.py createsuperuser`

3. **Static Files**:
   - Ensure static files are collected during build
   - Configure web server if needed

### 4. DNS Configuration
- Point your domain to server IP
- Configure SSL certificate (automatic with Coolify)
- Test domain resolution

## Post-Deployment Configuration

### 1. Health Checks
- Configure application health check endpoint
- Set appropriate timeout values
- Test health check functionality

### 2. Logging Configuration
```python
# Enhanced logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'obc_management': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 3. Performance Optimization
- Configure gunicorn workers based on CPU cores
- Set appropriate timeout values
- Optimize database connections
- Configure static file serving

### 4. SSL and Security
- Verify SSL certificate installation
- Configure security headers
- Set up CORS if needed for API access
- Test security headers

## Monitoring and Maintenance

### 1. Application Monitoring
- **Built-in Coolify Monitoring**:
  - Resource usage (CPU, RAM, disk)
  - Application uptime
  - Deployment history

- **Application-Level Monitoring**:
  - Django error logging
  - Database query performance
  - Background task monitoring

### 2. Log Management
- Configure log rotation
- Set up centralized logging if multiple services
- Monitor error patterns

### 3. Performance Monitoring
```python
# Add to settings.py for performance monitoring
if not DEBUG:
    MIDDLEWARE.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 300
    CACHE_MIDDLEWARE_KEY_PREFIX = ''
```

### 4. Regular Maintenance Tasks
- Weekly security updates
- Monthly dependency updates
- Quarterly full system backup tests
- Performance review and optimization

## Backup Strategy

### 1. Database Backups
```bash
# Automated PostgreSQL backup
#!/bin/bash
BACKUP_DIR="/app/backups"
DB_NAME="oobc_management"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump $DATABASE_URL > $BACKUP_DIR/db_backup_$DATE.sql
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
```

### 2. File System Backups
- **Media Files**: Backup uploaded files regularly
- **Configuration**: Version control for all config files
- **Logs**: Archive important logs before rotation

### 3. Cloud Storage Integration
```python
# S3-compatible backup storage
AWS_ACCESS_KEY_ID = env('BACKUP_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = env('BACKUP_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = env('BACKUP_BUCKET_NAME')
```

### 4. Backup Testing
- Monthly restore tests
- Document restore procedures
- Verify backup integrity

## Security Considerations

### 1. Application Security
- **Environment Variables**: Secure secret management
- **Database**: Connection encryption
- **API**: Rate limiting and authentication
- **File Uploads**: Validation and scanning

### 2. Infrastructure Security
- **Firewall**: Restrict unnecessary ports
- **SSH**: Key-based authentication only
- **Updates**: Automated security updates
- **Monitoring**: Intrusion detection

### 3. Data Protection
- **Encryption**: At rest and in transit
- **Access Control**: Role-based permissions
- **Audit Logging**: Track sensitive operations
- **Compliance**: GDPR/data protection requirements

### 4. Backup Security
- **Encryption**: Encrypted backup storage
- **Access Control**: Limited backup access
- **Retention**: Secure deletion of old backups

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Build Failures
- **Python Dependencies**: Check requirements.txt compatibility
- **System Packages**: Verify Dockerfile system dependencies
- **Build Context**: Ensure all required files are included

#### 2. Runtime Errors
- **Environment Variables**: Verify all required variables are set
- **Database Connection**: Check DATABASE_URL format
- **Static Files**: Ensure collectstatic runs successfully

#### 3. Performance Issues
- **Database Queries**: Enable query logging and optimize
- **Memory Usage**: Monitor and adjust worker count
- **Static Files**: Configure proper caching headers

#### 4. Connectivity Issues
- **Health Checks**: Verify endpoint responds correctly
- **DNS**: Check domain configuration
- **SSL**: Verify certificate validity

### Debugging Commands
```bash
# View application logs
docker logs -f container_name

# Access application shell
docker exec -it container_name ./manage.py shell

# Database check
docker exec -it container_name ./manage.py dbshell

# Run management commands
docker exec -it container_name ./manage.py command_name
```

## Rollback Procedures

### 1. Application Rollback
- Coolify provides built-in rollback to previous versions
- Access deployment history in Coolify dashboard
- Select previous successful deployment for rollback

### 2. Database Rollback
- Stop application services
- Restore database from backup
- Run any necessary data migrations
- Restart services

### 3. Configuration Rollback
- Revert environment variables
- Restore configuration files from version control
- Restart affected services

## Scaling Considerations

### 1. Horizontal Scaling
- **Load Balancer**: Configure multiple application instances
- **Database**: Read replicas for heavy read workloads
- **Static Files**: CDN integration for global distribution

### 2. Vertical Scaling
- **Server Resources**: Increase CPU/RAM as needed
- **Database**: Upgrade database instance size
- **Storage**: Expand disk space

### 3. Performance Optimization
- **Caching**: Implement Redis caching
- **Database**: Query optimization and indexing
- **Background Tasks**: Separate Celery workers

## Cost Analysis

### Monthly Operational Costs (Estimated)

| Component | Provider | Specifications | Cost (USD) |
|-----------|----------|----------------|------------|
| Server | Hetzner CAX11 | 4GB RAM, 2 vCPU | $4.20 |
| Domain | Namecheap | .com domain | $1.00 |
| Backup Storage | Cloudflare R2 | 50GB | $0.45 |
| **Total** | | | **$5.65** |

### Additional Considerations
- **Scaling**: Costs increase with server upgrades
- **Bandwidth**: Most providers include generous limits
- **Support**: Community support is free, paid support available

## Migration Timeline

### Phase 1: Infrastructure Setup (Week 1)
- [ ] Server procurement and setup
- [ ] Security hardening
- [ ] Coolify installation and configuration
- [ ] Domain and SSL setup

### Phase 2: Application Preparation (Week 2)
- [ ] Dockerfile and configuration creation
- [ ] Environment variables setup
- [ ] Database service configuration
- [ ] Testing deployment process

### Phase 3: Data Migration (Week 3)
- [ ] Production database setup
- [ ] Data export and import
- [ ] Migration testing
- [ ] Performance validation

### Phase 4: Go-Live (Week 4)
- [ ] Final deployment
- [ ] DNS cutover
- [ ] Monitoring setup
- [ ] Backup verification
- [ ] User acceptance testing

### Phase 5: Post-Launch (Ongoing)
- [ ] Performance monitoring
- [ ] Security updates
- [ ] Backup testing
- [ ] Documentation updates

## Next Steps

1. **Load Region IX population data**: Activate the virtualenv, then run `cd src && ./manage.py populate_administrative_hierarchy --force` to sync the new hierarchy totals into the database.
2. **Smoke-test barangay workflows**: Open the Add Barangay OBC form and pick a Zamboanga Peninsula barangay to ensure both the location cascade and the Total Population auto-fill behave as expected.
3. **Lock in infrastructure**: Approve a hosting provider, provision the Coolify host, and complete the security hardening steps in [Pre-Deployment Preparation](#pre-deployment-preparation).
4. **Finalize container assets**: Add the production requirements file, Dockerfile, and `.dockerignore` to the repository, then confirm they build successfully in CI or a local Docker run.
5. **Provision managed services**: Inside Coolify, create the PostgreSQL and Redis services, noting the connection URLs for later environment variable setup.
6. **Seed deployment configuration**: Create the Coolify application, wire up Git access, and enter the minimum environment variables (database, Redis, Django secrets, email) so the first build can succeed.
7. **Execute first deployment cycle**: Trigger the initial build, run migrations, create the superuser, and validate a smoke-test checklist (login, CRUD, API reachability).
8. **Activate monitoring & backups**: Enable Coolify resource monitoring, schedule database backups, and capture restore instructions while the deployment context is still fresh.

## Success Metrics

### Technical Metrics
- **Uptime**: Target 99.9% availability
- **Response Time**: <2 seconds for page loads
- **Build Time**: <5 minutes for deployments
- **Recovery Time**: <30 minutes for system restore

### Operational Metrics
- **Deployment Frequency**: Enable daily deployments if needed
- **Mean Time to Recovery**: <1 hour for critical issues
- **Backup Success Rate**: 100% successful daily backups
- **Security Updates**: Applied within 48 hours

### Cost Metrics
- **Infrastructure Cost**: <$10/month operational cost
- **Maintenance Time**: <4 hours/month admin overhead
- **Scalability**: Handle 2x traffic without major changes

## Conclusion

This deployment plan provides a comprehensive approach to hosting the OOBC Management System using Coolify. The self-hosted solution offers:

- **Cost Effectiveness**: Significantly lower than cloud alternatives
- **Full Control**: Complete ownership of infrastructure and data
- **Scalability**: Easy scaling as requirements grow
- **Security**: Enhanced security through isolated infrastructure
- **Flexibility**: Customizable to specific organizational needs

The plan balances operational simplicity with production-ready features, making it suitable for government and NGO use cases where data sovereignty and cost control are important considerations.

For questions or support during implementation, consult the Coolify documentation at https://coolify.io/docs/ and the active community forums.
