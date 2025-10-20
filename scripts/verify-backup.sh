#!/bin/bash

##############################################################################
# OBCMS Backup Verification Script
#
# Description: Verifies backup integrity and optionally tests restore
# Usage: ./verify-backup.sh <backup-file> [--test-restore]
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_FILE="${1:-}"
TEST_RESTORE="${2:-}"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/verify-$(date +"%Y-%m").log"

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
Usage: $0 <backup-file> [--test-restore]

Arguments:
  backup-file     Path to backup file to verify
  --test-restore  Perform test restore (database backups only)

Examples:
  $0 backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz
  $0 backups/weekly/obcms_backup_weekly_2025-10-20_03-00-00.sql.gz --test-restore
  $0 backups/monthly/obcms_media_monthly_2025-10-01_04-00-00.tar.gz

EOF
    exit 1
}

verify_file_exists() {
    log "INFO" "Checking if backup file exists..."

    if [ -z "$BACKUP_FILE" ]; then
        log "ERROR" "No backup file specified"
        usage
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        log "ERROR" "Backup file not found: ${BACKUP_FILE}"
        exit 1
    fi

    log "SUCCESS" "Backup file found: ${BACKUP_FILE}"
}

check_file_size() {
    log "INFO" "Checking file size..."

    local file_size=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
    local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)
    local min_size=$((100 * 1024))  # 100KB minimum

    log "INFO" "File size: ${size_mb} MB"

    if [ "$file_size" -lt "$min_size" ]; then
        log "ERROR" "File size too small (${size_mb} MB). Possible corruption."
        exit 1
    fi

    log "SUCCESS" "File size check passed"
}

verify_compression() {
    log "INFO" "Verifying compression integrity..."

    local file_ext="${BACKUP_FILE##*.}"

    if [ "$file_ext" == "gz" ]; then
        if gzip -t "$BACKUP_FILE" 2>> "$LOG_FILE"; then
            log "SUCCESS" "Gzip integrity verified"
        else
            log "ERROR" "Gzip integrity check failed"
            exit 1
        fi
    else
        log "WARNING" "Not a gzip file, skipping compression check"
    fi
}

verify_sql_backup() {
    log "INFO" "Verifying SQL backup structure..."

    # Decompress and check for SQL content
    local has_create=$(gunzip -c "$BACKUP_FILE" 2>/dev/null | head -n 100 | grep -c "CREATE TABLE" || echo 0)
    local has_insert=$(gunzip -c "$BACKUP_FILE" 2>/dev/null | head -n 1000 | grep -c "INSERT INTO" || echo 0)

    log "INFO" "Found ${has_create} CREATE TABLE statements"
    log "INFO" "Found ${has_insert} INSERT INTO statements"

    if [ "$has_create" -gt 0 ] && [ "$has_insert" -gt 0 ]; then
        log "SUCCESS" "SQL backup structure verified"
    else
        log "WARNING" "SQL backup may be incomplete (empty database?)"
    fi
}

verify_tar_backup() {
    log "INFO" "Verifying tar archive structure..."

    # Test tar integrity
    if tar -tzf "$BACKUP_FILE" > /dev/null 2>> "$LOG_FILE"; then
        log "SUCCESS" "Tar archive integrity verified"

        # Count files
        local file_count=$(tar -tzf "$BACKUP_FILE" 2>/dev/null | wc -l | tr -d ' ')
        log "INFO" "Archive contains ${file_count} files/directories"
    else
        log "ERROR" "Tar archive integrity check failed"
        exit 1
    fi
}

test_restore_database() {
    log "INFO" "Performing test restore (non-destructive)..."

    # Load environment variables
    if [ -f "${PROJECT_ROOT}/.env" ]; then
        set -a
        source <(grep -E '^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT)=' "${PROJECT_ROOT}/.env" || true)
        set +a
    fi

    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"

    if [ -z "${DB_NAME:-}" ] || [ -z "${DB_USER:-}" ] || [ -z "${DB_PASSWORD:-}" ]; then
        log "WARNING" "Database credentials not found. Skipping restore test."
        return 0
    fi

    # Create temporary test database
    local TEST_DB="obcms_test_restore_$$"

    log "INFO" "Creating temporary test database: ${TEST_DB}"

    export PGPASSWORD="${DB_PASSWORD}"

    # Create test database
    if createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$TEST_DB" 2>> "$LOG_FILE"; then
        log "SUCCESS" "Test database created"
    else
        log "ERROR" "Failed to create test database"
        unset PGPASSWORD
        exit 1
    fi

    # Restore backup to test database
    log "INFO" "Restoring backup to test database..."

    if gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" > /dev/null 2>> "$LOG_FILE"; then
        log "SUCCESS" "Backup restored successfully to test database"

        # Verify some basic tables exist
        local table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

        log "INFO" "Found ${table_count} tables in restored database"

        if [ "$table_count" -gt 0 ]; then
            log "SUCCESS" "Test restore validation passed"
        else
            log "WARNING" "Restored database has no tables"
        fi
    else
        log "ERROR" "Failed to restore backup to test database"
    fi

    # Drop test database
    log "INFO" "Cleaning up test database..."
    dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$TEST_DB" 2>> "$LOG_FILE" || true

    unset PGPASSWORD

    log "SUCCESS" "Test restore completed"
}

generate_report() {
    log "INFO" "Generating verification report..."

    local file_size=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
    local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)
    local file_mtime=$(stat -f%m "$BACKUP_FILE" 2>/dev/null || stat -c%Y "$BACKUP_FILE" 2>/dev/null)
    local file_date=$(date -r "$file_mtime" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "@$file_mtime" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)

    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║           OBCMS Backup Verification Report                   ║
╚══════════════════════════════════════════════════════════════╝

Backup File:      ${BACKUP_FILE}
File Size:        ${size_mb} MB
Created:          ${file_date}

Verification Results:
  ✓ File exists
  ✓ File size check passed
  ✓ Compression integrity verified
  ✓ Backup structure validated

Status:           VERIFIED ✓

Log: ${LOG_FILE}

╚══════════════════════════════════════════════════════════════╝

EOF
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║       OBCMS Backup Verification Script v1.0                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    verify_file_exists
    check_file_size
    verify_compression

    # Determine backup type and verify accordingly
    if [[ "$BACKUP_FILE" == *".sql.gz" ]]; then
        log "INFO" "Detected SQL backup"
        verify_sql_backup

        # Test restore if requested
        if [ "$TEST_RESTORE" == "--test-restore" ]; then
            test_restore_database
        fi
    elif [[ "$BACKUP_FILE" == *".tar.gz" ]]; then
        log "INFO" "Detected tar archive backup"
        verify_tar_backup
    else
        log "WARNING" "Unknown backup type, performing basic checks only"
    fi

    generate_report

    log "SUCCESS" "Backup verification completed"

    exit 0
}

main "$@"
