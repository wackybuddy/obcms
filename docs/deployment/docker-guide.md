# OBCMS Docker Guide

This guide provides comprehensive instructions for dockerizing the OOBC Management System (OBCMS).

## Overview

Dockerizing OBCMS provides several benefits:
- Consistent development and production environments
- Simplified multi-service orchestration (Django + Celery + Redis + PostgreSQL)
- Easy onboarding for new developers
- Reliable government system deployments
- Isolated service dependencies

## Architecture

The dockerized OBCMS consists of:
- **Web**: Django application with DRF API
- **Worker**: Celery background task processor
- **Redis**: Message broker and cache
- **Database**: PostgreSQL (production) or SQLite (development)

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ available memory

## Quick Start

1. **Clone and navigate to project**:
   ```bash
   cd obcms
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Run initial setup**:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**:
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin/

## Docker Configuration Files

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
# Multi-stage build for production optimization
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install -r requirements/base.txt

# Development stage
FROM base as development
RUN pip install -r requirements/development.txt
USER app

# Production stage
FROM base as production
COPY --chown=app:app . /app/
RUN python src/manage.py collectstatic --noinput
USER app

# Default command
CMD ["gunicorn", "--chdir", "src", "--bind", "0.0.0.0:8000", "obc_management.wsgi:application"]
```

### Docker Compose - Development

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: obcms
      POSTGRES_USER: obcms
      POSTGRES_PASSWORD: obcms_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U obcms"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: .
      target: development
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - static_volume:/app/src/staticfiles
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://obcms:obcms_dev_password@db:5432/obcms
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    command: >
      sh -c "cd src &&
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"

  celery:
    build:
      context: .
      target: development
    volumes:
      - .:/app
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://obcms:obcms_dev_password@db:5432/obcms
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    command: >
      sh -c "cd src &&
             celery -A obc_management worker -l info"

  celery-beat:
    build:
      context: .
      target: development
    volumes:
      - .:/app
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://obcms:obcms_dev_password@db:5432/obcms
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    command: >
      sh -c "cd src &&
             celery -A obc_management beat -l info"

volumes:
  postgres_data:
  redis_data:
  static_volume:
```

### Docker Compose - Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - obcms_network

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - obcms_network

  web:
    build:
      context: .
      target: production
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - static_volume:/app/src/staticfiles
      - media_volume:/app/src/media
    environment:
      - DEBUG=0
      - DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    depends_on:
      - redis
      - db
    networks:
      - obcms_network

  celery:
    build:
      context: .
      target: production
    restart: unless-stopped
    volumes:
      - media_volume:/app/src/media
    environment:
      - DEBUG=0
      - DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - redis
      - db
    networks:
      - obcms_network
    command: >
      sh -c "cd src &&
             celery -A obc_management worker -l info"

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - obcms_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  obcms_network:
    driver: bridge
```

## Environment Configuration

### Development Environment (.env)

```env
# Django Settings
SECRET_KEY=your-development-secret-key
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgres://obcms:obcms_dev_password@db:5432/obcms

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Email (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Google AI Services (Optional for development)
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-credentials.json
```

### Production Environment (.env.prod)

```env
# Django Settings
SECRET_KEY=your-production-secret-key-minimum-50-characters
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
POSTGRES_DB=obcms_prod
POSTGRES_USER=obcms_user
POSTGRES_PASSWORD=secure-database-password

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=email-password

# Google AI Services
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-credentials.json
```

## Development Workflow

### Daily Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web
docker-compose logs -f celery

# Run Django commands
docker-compose exec web python src/manage.py makemigrations
docker-compose exec web python src/manage.py migrate
docker-compose exec web python src/manage.py createsuperuser

# Run tests
docker-compose exec web pytest src/

# Access Django shell
docker-compose exec web python src/manage.py shell

# Stop services
docker-compose down
```

### Database Operations

```bash
# Reset database
docker-compose down -v
docker-compose up -d db
docker-compose exec web python src/manage.py migrate

# Backup database
docker-compose exec db pg_dump -U obcms obcms > backup.sql

# Restore database
docker-compose exec -T db psql -U obcms obcms < backup.sql
```

### Code Quality Checks

```bash
# Run linting and formatting
docker-compose exec web black src/
docker-compose exec web isort src/
docker-compose exec web flake8 src/

# Run tests with coverage
docker-compose exec web coverage run --source='src/' -m pytest src/
docker-compose exec web coverage report
```

## Production Deployment

### 1. Server Setup

```bash
# Create production directory
mkdir /opt/obcms
cd /opt/obcms

# Clone repository
git clone <repository-url> .

# Create production environment
cp .env.example .env.prod
# Edit .env.prod with production values
```

### 2. SSL Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream web {
        server web:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://web;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_redirect off;
        }

        location /static/ {
            alias /app/staticfiles/;
        }

        location /media/ {
            alias /app/media/;
        }
    }
}
```

### 3. Deploy

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python src/manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python src/manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python src/manage.py collectstatic --noinput
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check service status
docker-compose ps

# Check service health
docker-compose exec web python src/manage.py check
docker-compose exec redis redis-cli ping
docker-compose exec db pg_isready -U obcms
```

### Log Management

```bash
# View application logs
docker-compose logs -f --tail=100 web
docker-compose logs -f --tail=100 celery

# View system logs
docker-compose logs --timestamps
```

### Updates and Maintenance

```bash
# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Update dependencies
docker-compose build --no-cache
docker-compose down && docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 5432, 6379 are available
2. **Permission issues**: Check file ownership and Docker daemon permissions
3. **Memory issues**: Ensure sufficient memory for all services
4. **Network issues**: Verify Docker network configuration

### Debug Commands

```bash
# Enter container shell
docker-compose exec web bash
docker-compose exec db psql -U obcms

# Inspect container configuration
docker-compose config
docker inspect obcms_web_1

# Check resource usage
docker stats
```

### Performance Optimization

- Use multi-stage builds for smaller production images
- Implement Redis connection pooling
- Configure PostgreSQL for your workload
- Use nginx for static file serving
- Enable gzip compression
- Implement proper logging levels

## Security Considerations

- Use secrets management for production passwords
- Implement proper network segmentation
- Regular security updates for base images
- Use non-root users in containers
- Implement proper backup strategies
- Monitor container vulnerabilities

## Next Steps

1. Implement the Docker configuration files
2. Test in development environment
3. Set up CI/CD pipeline with Docker
4. Configure production environment
5. Implement monitoring and alerting
6. Create backup and disaster recovery procedures

This Docker setup provides a robust, scalable foundation for OBCMS deployment suitable for government requirements.