#!/bin/bash

##############################################################################
# OBCMS Database Backup Script
#
# Description: Creates transaction-safe PostgreSQL backup with compression
# Usage: ./backup-database.sh [daily|weekly|monthly]
#
# Environment Variables Required:
#   - DB_NAME: Database name
#   - DB_USER: Database user
#   - DB_PASSWORD: Database password
#   - DB_HOST: Database host (default: localhost)
#   - DB_PORT: Database port (default: 5432)
##############################################################################

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_TYPE="${1:-daily}"  # daily, weekly, or monthly
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
DATE_ONLY=$(date +"%Y-%m-%d")

# Backup directories
BACKUP_BASE_DIR="${PROJECT_ROOT}/backups"
BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_TYPE}"
TEMP_DIR="${BACKUP_BASE_DIR}/temp"

# Backup filename
BACKUP_FILENAME="obcms_backup_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/backup-$(date +"%Y-%m").log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

##############################################################################
# Functions
##############################################################################

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    # Create log directory if it doesn't exist
    mkdir -p "$LOG_DIR"

    # Log to file
    echo "[${timestamp}] [${level}] ${message}" >> "$LOG_FILE"

    # Print to console with color
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
        *)
            echo "[${level}] ${message}"
            ;;
    esac
}

check_dependencies() {
    log "INFO" "Checking dependencies..."

    local missing_deps=()

    if ! command -v pg_dump &> /dev/null; then
        missing_deps+=("pg_dump (PostgreSQL client)")
    fi

    if ! command -v gzip &> /dev/null; then
        missing_deps+=("gzip")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "ERROR" "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi

    log "SUCCESS" "All dependencies satisfied"
}

load_env_vars() {
    log "INFO" "Loading environment variables..."

    # Try to load from .env file if it exists
    if [ -f "${PROJECT_ROOT}/.env" ]; then
        # Export variables from .env (only DB-related)
        set -a
        source <(grep -E '^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT)=' "${PROJECT_ROOT}/.env" || true)
        set +a
        log "INFO" "Loaded environment from .env file"
    fi

    # Set defaults
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"

    # Validate required variables
    if [ -z "${DB_NAME:-}" ]; then
        log "ERROR" "DB_NAME is not set"
        exit 1
    fi

    if [ -z "${DB_USER:-}" ]; then
        log "ERROR" "DB_USER is not set"
        exit 1
    fi

    if [ -z "${DB_PASSWORD:-}" ]; then
        log "ERROR" "DB_PASSWORD is not set"
        exit 1
    fi

    log "SUCCESS" "Environment variables loaded"
    log "INFO" "Database: ${DB_NAME} on ${DB_HOST}:${DB_PORT}"
}

create_directories() {
    log "INFO" "Creating backup directories..."

    mkdir -p "$BACKUP_DIR"
    mkdir -p "$TEMP_DIR"
    mkdir -p "$LOG_DIR"

    log "SUCCESS" "Directories created"
}

perform_backup() {
    log "INFO" "Starting ${BACKUP_TYPE} database backup..."
    log "INFO" "Output: ${BACKUP_PATH}"

    # Create temporary uncompressed backup
    local temp_backup="${TEMP_DIR}/obcms_temp_${TIMESTAMP}.sql"

    # Set PGPASSWORD for pg_dump
    export PGPASSWORD="${DB_PASSWORD}"

    # Perform backup with transaction-safe options
    if pg_dump \
        --host="${DB_HOST}" \
        --port="${DB_PORT}" \
        --username="${DB_USER}" \
        --dbname="${DB_NAME}" \
        --clean \
        --if-exists \
        --no-owner \
        --no-privileges \
        --format=plain \
        --file="${temp_backup}" \
        2>> "$LOG_FILE"; then

        log "SUCCESS" "Database dump completed"
    else
        log "ERROR" "Database dump failed"
        rm -f "${temp_backup}"
        exit 1
    fi

    # Unset PGPASSWORD
    unset PGPASSWORD

    # Compress the backup
    log "INFO" "Compressing backup..."
    if gzip -c "${temp_backup}" > "${BACKUP_PATH}"; then
        log "SUCCESS" "Backup compressed successfully"
        rm -f "${temp_backup}"
    else
        log "ERROR" "Compression failed"
        rm -f "${temp_backup}"
        exit 1
    fi
}

verify_backup() {
    log "INFO" "Verifying backup integrity..."

    # Check if backup file exists
    if [ ! -f "${BACKUP_PATH}" ]; then
        log "ERROR" "Backup file not found: ${BACKUP_PATH}"
        exit 1
    fi

    # Check file size (must be > 100KB)
    local file_size=$(stat -f%z "${BACKUP_PATH}" 2>/dev/null || stat -c%s "${BACKUP_PATH}" 2>/dev/null)
    local min_size=$((100 * 1024))  # 100KB in bytes

    if [ "$file_size" -lt "$min_size" ]; then
        log "ERROR" "Backup file is too small (${file_size} bytes). Possible corruption."
        exit 1
    fi

    # Test gzip integrity
    if ! gzip -t "${BACKUP_PATH}" 2>> "$LOG_FILE"; then
        log "ERROR" "Backup file is corrupted (gzip test failed)"
        exit 1
    fi

    # Calculate file size in MB
    local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)

    log "SUCCESS" "Backup verified successfully (${size_mb} MB)"
}

generate_report() {
    log "INFO" "Generating backup report..."

    local file_size=$(stat -f%z "${BACKUP_PATH}" 2>/dev/null || stat -c%s "${BACKUP_PATH}" 2>/dev/null)
    local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)

    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║              OBCMS Database Backup Report                    ║
╚══════════════════════════════════════════════════════════════╝

Backup Type:      ${BACKUP_TYPE}
Timestamp:        ${TIMESTAMP}
Database:         ${DB_NAME}
Host:             ${DB_HOST}:${DB_PORT}

Backup Location:  ${BACKUP_PATH}
File Size:        ${size_mb} MB
Status:           SUCCESS ✓

Next Steps:
  - Verify backup: ./scripts/verify-backup.sh ${BACKUP_PATH}
  - Restore backup: ./scripts/restore-backup.sh ${BACKUP_PATH}
  - View logs: tail -f ${LOG_FILE}

╚══════════════════════════════════════════════════════════════╝

EOF

    log "INFO" "Backup completed successfully"
}

cleanup_temp() {
    log "INFO" "Cleaning up temporary files..."
    rm -rf "${TEMP_DIR:?}"/*
    log "SUCCESS" "Cleanup completed"
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          OBCMS Database Backup Script v1.0                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Validate backup type
    if [[ ! "$BACKUP_TYPE" =~ ^(daily|weekly|monthly)$ ]]; then
        log "ERROR" "Invalid backup type: ${BACKUP_TYPE}"
        echo "Usage: $0 [daily|weekly|monthly]"
        exit 1
    fi

    check_dependencies
    load_env_vars
    create_directories
    perform_backup
    verify_backup
    cleanup_temp
    generate_report

    exit 0
}

# Run main function
main "$@"
