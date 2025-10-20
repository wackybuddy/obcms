#!/bin/bash

##############################################################################
# OBCMS Media Files Backup Script
#
# Description: Backs up media files (uploads, documents, images)
# Usage: ./backup-media.sh [daily|weekly|monthly]
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_TYPE="${1:-daily}"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Directories
MEDIA_DIR="${PROJECT_ROOT}/src/media"
BACKUP_BASE_DIR="${PROJECT_ROOT}/backups"
BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_TYPE}"
TEMP_DIR="${BACKUP_BASE_DIR}/temp"

# Backup filename
BACKUP_FILENAME="obcms_media_${BACKUP_TYPE}_${TIMESTAMP}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/backup-$(date +"%Y-%m").log"

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

check_dependencies() {
    log "INFO" "Checking dependencies..."

    if ! command -v tar &> /dev/null; then
        log "ERROR" "tar command not found"
        exit 1
    fi

    log "SUCCESS" "All dependencies satisfied"
}

create_directories() {
    log "INFO" "Creating backup directories..."
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$TEMP_DIR"
    log "SUCCESS" "Directories created"
}

check_media_directory() {
    log "INFO" "Checking media directory..."

    if [ ! -d "$MEDIA_DIR" ]; then
        log "WARNING" "Media directory does not exist: ${MEDIA_DIR}"
        log "WARNING" "Creating empty media directory..."
        mkdir -p "$MEDIA_DIR"
    fi

    # Count files
    local file_count=$(find "$MEDIA_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
    local dir_size=$(du -sh "$MEDIA_DIR" 2>/dev/null | cut -f1)

    log "INFO" "Media directory: ${file_count} files, ${dir_size}"
}

perform_backup() {
    log "INFO" "Starting ${BACKUP_TYPE} media backup..."
    log "INFO" "Output: ${BACKUP_PATH}"

    # Create tarball with compression
    if tar -czf "${BACKUP_PATH}" \
        -C "${PROJECT_ROOT}/src" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.DS_Store' \
        media 2>> "$LOG_FILE"; then

        log "SUCCESS" "Media files archived successfully"
    else
        log "ERROR" "Media backup failed"
        exit 1
    fi
}

verify_backup() {
    log "INFO" "Verifying backup integrity..."

    # Check if backup exists
    if [ ! -f "${BACKUP_PATH}" ]; then
        log "ERROR" "Backup file not found: ${BACKUP_PATH}"
        exit 1
    fi

    # Test tar integrity
    if ! tar -tzf "${BACKUP_PATH}" > /dev/null 2>> "$LOG_FILE"; then
        log "ERROR" "Backup file is corrupted (tar test failed)"
        exit 1
    fi

    # Check file size
    local file_size=$(stat -f%z "${BACKUP_PATH}" 2>/dev/null || stat -c%s "${BACKUP_PATH}" 2>/dev/null)
    local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)

    log "SUCCESS" "Backup verified successfully (${size_mb} MB)"
}

generate_report() {
    log "INFO" "Generating backup report..."

    local file_size=$(stat -f%z "${BACKUP_PATH}" 2>/dev/null || stat -c%s "${BACKUP_PATH}" 2>/dev/null)
    local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)

    # Count files in backup
    local file_count=$(tar -tzf "${BACKUP_PATH}" 2>/dev/null | wc -l | tr -d ' ')

    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║              OBCMS Media Backup Report                       ║
╚══════════════════════════════════════════════════════════════╝

Backup Type:      ${BACKUP_TYPE}
Timestamp:        ${TIMESTAMP}
Media Directory:  ${MEDIA_DIR}

Backup Location:  ${BACKUP_PATH}
File Size:        ${size_mb} MB
Files Archived:   ${file_count}
Status:           SUCCESS ✓

Next Steps:
  - Verify backup: tar -tzf ${BACKUP_PATH} | head
  - Restore backup: ./scripts/restore-backup.sh ${BACKUP_PATH}
  - View logs: tail -f ${LOG_FILE}

╚══════════════════════════════════════════════════════════════╝

EOF

    log "INFO" "Media backup completed successfully"
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          OBCMS Media Backup Script v1.0                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Validate backup type
    if [[ ! "$BACKUP_TYPE" =~ ^(daily|weekly|monthly)$ ]]; then
        log "ERROR" "Invalid backup type: ${BACKUP_TYPE}"
        echo "Usage: $0 [daily|weekly|monthly]"
        exit 1
    fi

    check_dependencies
    create_directories
    check_media_directory
    perform_backup
    verify_backup
    generate_report

    exit 0
}

main "$@"
