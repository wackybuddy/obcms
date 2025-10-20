#!/bin/bash

##############################################################################
# OBCMS Docker Backup Volume Setup
#
# Description: Configures Docker volumes for backups
# Usage: ./docker-backup-setup.sh
##############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local level="$1"
    shift
    local message="$*"

    case "$level" in
        INFO)
            echo -e "${BLUE}[INFO]${NC} ${message}"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} ${message}"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} ${message}"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} ${message}"
            ;;
    esac
}

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       OBCMS Docker Backup Volume Setup                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

log "INFO" "Checking Docker installation..."

if ! command -v docker &> /dev/null; then
    log "ERROR" "Docker is not installed"
    exit 1
fi

log "SUCCESS" "Docker found"

# Create Docker volume for backups
log "INFO" "Creating Docker volume for backups..."

if docker volume inspect obcms_backups &> /dev/null; then
    log "WARNING" "Volume 'obcms_backups' already exists"
else
    if docker volume create obcms_backups; then
        log "SUCCESS" "Volume 'obcms_backups' created"
    else
        log "ERROR" "Failed to create volume"
        exit 1
    fi
fi

# Show volume info
log "INFO" "Volume information:"
docker volume inspect obcms_backups

# Generate docker-compose backup service
log "INFO" "Generating docker-compose backup configuration..."

cat > docker-compose.backup.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  backup:
    image: postgres:15
    container_name: obcms_backup
    restart: "no"
    volumes:
      - obcms_backups:/backups
      - ./scripts:/scripts:ro
      - ./.env:/app/.env:ro
    environment:
      - TZ=Asia/Manila
    networks:
      - obcms_network
    entrypoint: /scripts/docker-backup-entrypoint.sh
    depends_on:
      - db

volumes:
  obcms_backups:
    external: true

networks:
  obcms_network:
    external: true
COMPOSE_EOF

log "SUCCESS" "Created docker-compose.backup.yml"

# Generate Docker backup entrypoint
log "INFO" "Generating Docker backup entrypoint..."

cat > docker-backup-entrypoint.sh << 'ENTRYPOINT_EOF'
#!/bin/bash

##############################################################################
# Docker Backup Entrypoint
##############################################################################

set -euo pipefail

BACKUP_TYPE="${1:-daily}"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="/backups/${BACKUP_TYPE}"
BACKUP_FILE="${BACKUP_DIR}/obcms_backup_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[INFO] Starting backup: ${BACKUP_TYPE}"
echo "[INFO] Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"

# Perform backup
PGPASSWORD="${DB_PASSWORD}" pg_dump \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --username="${DB_USER}" \
    --dbname="${DB_NAME}" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    --format=plain | gzip > "${BACKUP_FILE}"

if [ -f "${BACKUP_FILE}" ]; then
    FILE_SIZE=$(stat -c%s "${BACKUP_FILE}")
    SIZE_MB=$(echo "scale=2; $FILE_SIZE / 1048576" | bc)
    echo "[SUCCESS] Backup created: ${BACKUP_FILE} (${SIZE_MB} MB)"
    exit 0
else
    echo "[ERROR] Backup failed"
    exit 1
fi
ENTRYPOINT_EOF

chmod +x docker-backup-entrypoint.sh

log "SUCCESS" "Created docker-backup-entrypoint.sh"

# Generate helper scripts for Docker backups
log "INFO" "Generating Docker backup helper scripts..."

cat > docker-backup.sh << 'HELPER_EOF'
#!/bin/bash

##############################################################################
# Docker Backup Helper Script
#
# Usage: ./docker-backup.sh [daily|weekly|monthly]
##############################################################################

set -euo pipefail

BACKUP_TYPE="${1:-daily}"

echo "[INFO] Running Docker backup: ${BACKUP_TYPE}"

if docker-compose -f docker-compose.backup.yml run --rm backup "$BACKUP_TYPE"; then
    echo "[SUCCESS] Backup completed"
else
    echo "[ERROR] Backup failed"
    exit 1
fi
HELPER_EOF

chmod +x docker-backup.sh

log "SUCCESS" "Created docker-backup.sh"

# Final instructions
cat << EOF

╔══════════════════════════════════════════════════════════════╗
║              Docker Backup Setup Complete                    ║
╚══════════════════════════════════════════════════════════════╝

Created Files:
  - docker-compose.backup.yml
  - docker-backup-entrypoint.sh
  - docker-backup.sh

Docker Volume:
  - obcms_backups

Usage:
  1. Run manual backup:
     ./docker-backup.sh daily

  2. Schedule with cron (add to crontab):
     0 2 * * * cd /path/to/obcms && ./docker-backup.sh daily

  3. View backups:
     docker run --rm -v obcms_backups:/backups alpine ls -lh /backups/daily

  4. Copy backup to host:
     docker run --rm -v obcms_backups:/backups -v $(pwd):/host alpine \
       cp /backups/daily/backup-file.sql.gz /host/

Next Steps:
  - Test backup: ./docker-backup.sh daily
  - Set up cron schedule
  - Configure retention policy

╚══════════════════════════════════════════════════════════════╝

EOF

exit 0
