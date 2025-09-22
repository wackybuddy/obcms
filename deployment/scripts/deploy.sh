#!/bin/bash

# OBC Management System Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: staging, production

set -e  # Exit on any error

ENVIRONMENT=${1:-staging}
PROJECT_DIR="/var/www/obc-system"
BACKUP_DIR="/var/backups/obc-system"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="obc-gunicorn"
REQUIRED_PYTHON="3.12"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if running as correct user
if [[ $EUID -eq 0 ]]; then
    error "This script should not be run as root"
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    error "Invalid environment. Use 'staging' or 'production'"
fi

log "Starting deployment for $ENVIRONMENT environment"

# Check if project directory exists
if [[ ! -d "$PROJECT_DIR" ]]; then
    error "Project directory $PROJECT_DIR does not exist"
fi

cd "$PROJECT_DIR"

# Ensure virtual environment exists and uses Python 3.12
if [[ ! -d "$VENV_DIR" ]]; then
    log "Virtual environment not found. Creating with python3.12..."
    python3.12 -m venv "$VENV_DIR" || error "Failed to create virtual environment with python3.12"
fi

# Create backup
log "Creating backup..."
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql"

# Backup database
if [[ -f ".env" ]]; then
    source .env
    if [[ -n "$DATABASE_URL" ]]; then
        log "Backing up database..."
        sudo -u postgres pg_dump "$DATABASE_NAME" > "$BACKUP_FILE"
        log "Database backup created: $BACKUP_FILE"
    fi
fi

# Stop services
log "Stopping services..."
sudo systemctl stop "$SERVICE_NAME" || warning "Could not stop $SERVICE_NAME"
sudo systemctl stop nginx || warning "Could not stop nginx"

# Pull latest code
log "Pulling latest code..."
git fetch origin
if [[ "$ENVIRONMENT" == "production" ]]; then
    git checkout main
    git pull origin main
else
    git checkout develop
    git pull origin develop
fi

# Activate virtual environment
log "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

CURRENT_PYTHON="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "$CURRENT_PYTHON" != "$REQUIRED_PYTHON" ]]; then
    deactivate || true
    error "Virtual environment must use Python ${REQUIRED_PYTHON} (found ${CURRENT_PYTHON}). Recreate the venv with python3.12."
fi

# Update dependencies
log "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r "requirements/$ENVIRONMENT.txt"

# Run database migrations
log "Running database migrations..."
cd src
./manage.py migrate --noinput

# Collect static files
log "Collecting static files..."
./manage.py collectstatic --noinput --clear

# Run Django system checks
log "Running system checks..."
./manage.py check --deploy

# Create cache tables if needed
log "Creating cache tables..."
./manage.py createcachetable || true

# Clear cache
log "Clearing cache..."
./manage.py shell -c "from django.core.cache import cache; cache.clear()" || true

# Update file permissions
log "Updating file permissions..."
cd ..
sudo chown -R www-data:www-data .
sudo chmod -R 755 .
sudo chmod -R 644 static/ media/ || true

# Start services
log "Starting services..."
sudo systemctl start "$SERVICE_NAME"
sudo systemctl start nginx

# Wait a moment for services to start
sleep 5

# Check service status
log "Checking service status..."
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    log "✓ $SERVICE_NAME is running"
else
    error "✗ $SERVICE_NAME failed to start"
fi

if sudo systemctl is-active --quiet nginx; then
    log "✓ Nginx is running"
else
    error "✗ Nginx failed to start"
fi

# Health check
log "Performing health check..."
cd src
./manage.py check

# Send deployment notification (if configured)
if [[ -n "$DEPLOYMENT_WEBHOOK" ]]; then
    curl -X POST "$DEPLOYMENT_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"OBC System deployed successfully to $ENVIRONMENT\"}" || true
fi

log "Deployment completed successfully!"
log "Environment: $ENVIRONMENT"
log "Backup: $BACKUP_FILE"
log "Services: $SERVICE_NAME, nginx"

# Show recent logs
log "Recent application logs:"
sudo journalctl -u "$SERVICE_NAME" --no-pager -n 10
