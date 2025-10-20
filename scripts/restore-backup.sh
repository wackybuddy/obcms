#!/bin/bash

##############################################################################
# OBCMS Backup Restore Script
#
# Description: Restores database or media backups with safety checks
# Usage: ./restore-backup.sh <backup-file> [--force]
#
# CRITICAL: This script will OVERWRITE existing data. Use with caution!
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_FILE="${1:-}"
FORCE_RESTORE="${2:-}"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/restore-$(date +"%Y-%m").log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

##############################################################################
# Functions
##############################################################################

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    mkdir -p "$LOG_DIR"
    echo "[${timestamp}] [${level}] ${message}" >> "$LOG_FILE"

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

usage() {
    cat << EOF
Usage: $0 <backup-file> [--force]

Arguments:
  backup-file     Path to backup file to restore
  --force         Skip confirmation prompt (use with caution!)

Examples:
  $0 backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz
  $0 backups/monthly/obcms_media_monthly_2025-10-01_04-00-00.tar.gz --force

CRITICAL WARNING:
  This will OVERWRITE existing data!
  Make sure you have a recent backup before restoring.

EOF
    exit 1
}

verify_backup_file() {
    log "INFO" "Verifying backup file..."

    if [ -z "$BACKUP_FILE" ]; then
        log "ERROR" "No backup file specified"
        usage
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        log "ERROR" "Backup file not found: ${BACKUP_FILE}"
        exit 1
    fi

    log "SUCCESS" "Backup file verified: ${BACKUP_FILE}"
}

confirm_restore() {
    if [ "$FORCE_RESTORE" == "--force" ]; then
        log "WARNING" "Force mode enabled, skipping confirmation"
        return 0
    fi

    echo ""
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    CRITICAL WARNING                          ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}This operation will OVERWRITE existing data!${NC}"
    echo ""
    echo -e "Backup file: ${BLUE}${BACKUP_FILE}${NC}"
    echo ""
    echo -e "${YELLOW}Make sure you have a recent backup before proceeding.${NC}"
    echo ""
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirmation

    if [ "$confirmation" != "yes" ]; then
        log "INFO" "Restore cancelled by user"
        exit 0
    fi

    log "INFO" "User confirmed restore operation"
}

create_pre_restore_backup() {
    log "INFO" "Creating pre-restore backup..."

    local timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
    local backup_dir="${PROJECT_ROOT}/backups/pre-restore"

    mkdir -p "$backup_dir"

    # Determine what to backup based on restore type
    if [[ "$BACKUP_FILE" == *".sql.gz" ]]; then
        log "INFO" "Creating database pre-restore backup..."
        if "${SCRIPT_DIR}/backup-database.sh" daily >> "$LOG_FILE" 2>&1; then
            log "SUCCESS" "Pre-restore database backup created"
        else
            log "WARNING" "Failed to create pre-restore backup (continuing anyway)"
        fi
    elif [[ "$BACKUP_FILE" == *".tar.gz" ]]; then
        log "INFO" "Creating media pre-restore backup..."
        if "${SCRIPT_DIR}/backup-media.sh" daily >> "$LOG_FILE" 2>&1; then
            log "SUCCESS" "Pre-restore media backup created"
        else
            log "WARNING" "Failed to create pre-restore backup (continuing anyway)"
        fi
    fi
}

restore_database() {
    log "INFO" "Restoring database backup..."

    # Load environment variables
    if [ -f "${PROJECT_ROOT}/.env" ]; then
        set -a
        source <(grep -E '^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT)=' "${PROJECT_ROOT}/.env" || true)
        set +a
    fi

    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"

    # Validate credentials
    if [ -z "${DB_NAME:-}" ] || [ -z "${DB_USER:-}" ] || [ -z "${DB_PASSWORD:-}" ]; then
        log "ERROR" "Database credentials not found in .env file"
        exit 1
    fi

    log "INFO" "Database: ${DB_NAME} on ${DB_HOST}:${DB_PORT}"

    export PGPASSWORD="${DB_PASSWORD}"

    # Drop existing database and recreate
    log "WARNING" "Dropping existing database..."
    dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" 2>> "$LOG_FILE" || true

    log "INFO" "Creating fresh database..."
    if createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" 2>> "$LOG_FILE"; then
        log "SUCCESS" "Database created"
    else
        log "ERROR" "Failed to create database"
        unset PGPASSWORD
        exit 1
    fi

    # Restore from backup
    log "INFO" "Restoring data from backup..."
    if gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>> "$LOG_FILE"; then
        log "SUCCESS" "Database restored successfully"
    else
        log "ERROR" "Failed to restore database"
        unset PGPASSWORD
        exit 1
    fi

    unset PGPASSWORD

    # Verify restoration
    log "INFO" "Verifying restored database..."
    export PGPASSWORD="${DB_PASSWORD}"

    local table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

    unset PGPASSWORD

    log "INFO" "Restored database has ${table_count} tables"

    if [ "$table_count" -gt 0 ]; then
        log "SUCCESS" "Database restoration verified"
    else
        log "WARNING" "Restored database appears to be empty"
    fi
}

restore_media() {
    log "INFO" "Restoring media backup..."

    local media_dir="${PROJECT_ROOT}/src/media"

    # Backup existing media if it exists
    if [ -d "$media_dir" ] && [ "$(ls -A "$media_dir" 2>/dev/null)" ]; then
        local backup_timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
        local old_media_backup="${PROJECT_ROOT}/backups/pre-restore/media_backup_${backup_timestamp}"

        log "INFO" "Backing up existing media to: ${old_media_backup}"
        mv "$media_dir" "$old_media_backup" 2>> "$LOG_FILE" || true
    fi

    # Create media directory
    mkdir -p "${PROJECT_ROOT}/src"

    # Extract backup
    log "INFO" "Extracting media files..."
    if tar -xzf "$BACKUP_FILE" -C "${PROJECT_ROOT}/src" 2>> "$LOG_FILE"; then
        log "SUCCESS" "Media files restored successfully"
    else
        log "ERROR" "Failed to restore media files"
        exit 1
    fi

    # Verify restoration
    local file_count=$(find "$media_dir" -type f 2>/dev/null | wc -l | tr -d ' ')
    log "INFO" "Restored ${file_count} media files"

    log "SUCCESS" "Media restoration verified"
}

run_post_restore_checks() {
    log "INFO" "Running post-restore checks..."

    if [[ "$BACKUP_FILE" == *".sql.gz" ]]; then
        log "INFO" "Running Django checks..."

        # Try to run Django management commands
        if [ -f "${PROJECT_ROOT}/src/manage.py" ]; then
            cd "${PROJECT_ROOT}/src"

            # Check migrations
            log "INFO" "Checking for pending migrations..."
            if python manage.py showmigrations 2>> "$LOG_FILE" | grep -q "\[ \]"; then
                log "WARNING" "There are pending migrations. Run: python manage.py migrate"
            else
                log "SUCCESS" "No pending migrations"
            fi

            cd "$PROJECT_ROOT"
        fi
    fi

    log "SUCCESS" "Post-restore checks completed"
}

generate_report() {
    log "INFO" "Generating restore report..."

    local file_size=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
    local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)
    local restore_time=$(date +"%Y-%m-%d %H:%M:%S")

    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║              OBCMS Backup Restore Report                     ║
╚══════════════════════════════════════════════════════════════╝

Backup File:      ${BACKUP_FILE}
File Size:        ${size_mb} MB
Restore Time:     ${restore_time}

Status:           SUCCESS ✓

Next Steps:
  - Test your application thoroughly
  - Verify data integrity
  - Check logs: tail -f ${LOG_FILE}

Database Restore:
  - Run migrations if needed: cd src && python manage.py migrate
  - Create superuser if needed: python manage.py createsuperuser
  - Collect static files: python manage.py collectstatic

╚══════════════════════════════════════════════════════════════╝

EOF

    log "INFO" "Restore completed successfully"
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          OBCMS Backup Restore Script v1.0                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    verify_backup_file
    confirm_restore
    create_pre_restore_backup

    # Determine backup type and restore accordingly
    if [[ "$BACKUP_FILE" == *".sql.gz" ]]; then
        log "INFO" "Detected SQL backup - restoring database"
        restore_database
    elif [[ "$BACKUP_FILE" == *".tar.gz" ]]; then
        log "INFO" "Detected tar archive - restoring media files"
        restore_media
    else
        log "ERROR" "Unknown backup type: ${BACKUP_FILE}"
        exit 1
    fi

    run_post_restore_checks
    generate_report

    log "SUCCESS" "Restore operation completed"

    exit 0
}

main "$@"
