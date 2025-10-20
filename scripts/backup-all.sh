#!/bin/bash

##############################################################################
# OBCMS Complete Backup Script
#
# Description: Orchestrates full backup (database + media)
# Usage: ./backup-all.sh [daily|weekly|monthly]
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_TYPE="${1:-daily}"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/backup-all-$(date +"%Y-%m").log"

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

backup_database() {
    log "INFO" "Running database backup..."

    if "${SCRIPT_DIR}/backup-database.sh" "$BACKUP_TYPE" 2>&1 | tee -a "$LOG_FILE"; then
        log "SUCCESS" "Database backup completed"
        return 0
    else
        log "ERROR" "Database backup failed"
        return 1
    fi
}

backup_media() {
    log "INFO" "Running media backup..."

    if "${SCRIPT_DIR}/backup-media.sh" "$BACKUP_TYPE" 2>&1 | tee -a "$LOG_FILE"; then
        log "SUCCESS" "Media backup completed"
        return 0
    else
        log "ERROR" "Media backup failed"
        return 1
    fi
}

cleanup_old_backups() {
    log "INFO" "Running backup cleanup..."

    if "${SCRIPT_DIR}/cleanup-old-backups.sh" 2>&1 | tee -a "$LOG_FILE"; then
        log "SUCCESS" "Backup cleanup completed"
        return 0
    else
        log "WARNING" "Backup cleanup had issues"
        return 1
    fi
}

generate_final_report() {
    log "INFO" "Generating final backup report..."

    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║           OBCMS Complete Backup Report                       ║
╚══════════════════════════════════════════════════════════════╝

Backup Type:      ${BACKUP_TYPE}
Timestamp:        $(date +"%Y-%m-%d %H:%M:%S")

Backup Operations:
  ✓ Database backup completed
  ✓ Media backup completed
  ✓ Old backups cleaned up

Status:           SUCCESS ✓

View detailed logs: tail -f ${LOG_FILE}

╚══════════════════════════════════════════════════════════════╝

EOF
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║       OBCMS Complete Backup Script v1.0                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Validate backup type
    if [[ ! "$BACKUP_TYPE" =~ ^(daily|weekly|monthly)$ ]]; then
        log "ERROR" "Invalid backup type: ${BACKUP_TYPE}"
        echo "Usage: $0 [daily|weekly|monthly]"
        exit 1
    fi

    log "INFO" "Starting complete ${BACKUP_TYPE} backup..."

    local failed=0

    # Run backups
    if ! backup_database; then
        failed=$((failed + 1))
    fi

    if ! backup_media; then
        failed=$((failed + 1))
    fi

    # Cleanup regardless of backup success
    cleanup_old_backups || true

    # Check results
    if [ "$failed" -eq 0 ]; then
        generate_final_report
        log "SUCCESS" "Complete backup finished successfully"
        exit 0
    else
        log "ERROR" "Complete backup finished with ${failed} error(s)"
        exit 1
    fi
}

main "$@"
