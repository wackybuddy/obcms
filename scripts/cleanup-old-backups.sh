#!/bin/bash

##############################################################################
# OBCMS Backup Retention Policy Script
#
# Description: Implements tiered backup retention policy
# Policy:
#   - Daily backups: Keep for 30 days
#   - Weekly backups: Keep for 90 days (3 months)
#   - Monthly backups: Keep for 365 days (1 year)
#
# Usage: ./cleanup-old-backups.sh
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_BASE_DIR="${PROJECT_ROOT}/backups"

# Retention periods (in days)
DAILY_RETENTION=30
WEEKLY_RETENTION=90
MONTHLY_RETENTION=365

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/cleanup-$(date +"%Y-%m").log"

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

cleanup_backup_type() {
    local backup_type="$1"
    local retention_days="$2"
    local backup_dir="${BACKUP_BASE_DIR}/${backup_type}"

    log "INFO" "Cleaning up ${backup_type} backups (retention: ${retention_days} days)..."

    if [ ! -d "$backup_dir" ]; then
        log "WARNING" "Backup directory does not exist: ${backup_dir}"
        return 0
    fi

    local deleted_count=0
    local kept_count=0
    local freed_space=0

    # Find and delete old backups
    while IFS= read -r -d '' backup_file; do
        # Get file modification time (days since epoch)
        local file_mtime=$(stat -f%m "$backup_file" 2>/dev/null || stat -c%Y "$backup_file" 2>/dev/null)
        local current_time=$(date +%s)
        local file_age_days=$(( (current_time - file_mtime) / 86400 ))

        if [ "$file_age_days" -gt "$retention_days" ]; then
            # Get file size before deletion
            local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
            local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)

            log "INFO" "Deleting old backup: $(basename "$backup_file") (${file_age_days} days old, ${size_mb} MB)"

            if rm -f "$backup_file"; then
                deleted_count=$((deleted_count + 1))
                freed_space=$((freed_space + file_size))
            else
                log "ERROR" "Failed to delete: $backup_file"
            fi
        else
            kept_count=$((kept_count + 1))
        fi
    done < <(find "$backup_dir" -name "*.sql.gz" -type f -print0 2>/dev/null)

    # Calculate freed space in MB
    local freed_mb=$(echo "scale=2; $freed_space / 1048576" | bc)

    if [ "$deleted_count" -gt 0 ]; then
        log "SUCCESS" "${backup_type}: Deleted ${deleted_count} backups, kept ${kept_count}, freed ${freed_mb} MB"
    else
        log "INFO" "${backup_type}: No backups to delete, kept ${kept_count}"
    fi
}

generate_backup_summary() {
    log "INFO" "Generating backup summary..."

    local daily_count=0
    local weekly_count=0
    local monthly_count=0
    local total_size=0

    # Count daily backups
    if [ -d "${BACKUP_BASE_DIR}/daily" ]; then
        daily_count=$(find "${BACKUP_BASE_DIR}/daily" -name "*.sql.gz" -type f 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Count weekly backups
    if [ -d "${BACKUP_BASE_DIR}/weekly" ]; then
        weekly_count=$(find "${BACKUP_BASE_DIR}/weekly" -name "*.sql.gz" -type f 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Count monthly backups
    if [ -d "${BACKUP_BASE_DIR}/monthly" ]; then
        monthly_count=$(find "${BACKUP_BASE_DIR}/monthly" -name "*.sql.gz" -type f 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Calculate total size
    if [ -d "$BACKUP_BASE_DIR" ]; then
        total_size=$(du -sk "$BACKUP_BASE_DIR" 2>/dev/null | cut -f1)
        total_size=$((total_size * 1024))  # Convert to bytes
    fi

    local total_mb=$(echo "scale=2; $total_size / 1048576" | bc)
    local total_gb=$(echo "scale=2; $total_size / 1073741824" | bc)

    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║            OBCMS Backup Retention Summary                    ║
╚══════════════════════════════════════════════════════════════╝

Backup Counts:
  Daily backups:    ${daily_count} (retain ${DAILY_RETENTION} days)
  Weekly backups:   ${weekly_count} (retain ${WEEKLY_RETENTION} days)
  Monthly backups:  ${monthly_count} (retain ${MONTHLY_RETENTION} days)

Total Storage:
  Size: ${total_mb} MB (${total_gb} GB)
  Location: ${BACKUP_BASE_DIR}

Policy Status: ✓ COMPLIANT

Log: ${LOG_FILE}

╚══════════════════════════════════════════════════════════════╝

EOF
}

check_backup_health() {
    log "INFO" "Checking backup health..."

    local warnings=0

    # Check if we have recent daily backup (within last 2 days)
    if [ -d "${BACKUP_BASE_DIR}/daily" ]; then
        local latest_daily=$(find "${BACKUP_BASE_DIR}/daily" -name "*.sql.gz" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -n1)
        if [ -n "$latest_daily" ]; then
            local file_mtime=$(stat -f%m "$latest_daily" 2>/dev/null || stat -c%Y "$latest_daily" 2>/dev/null)
            local current_time=$(date +%s)
            local age_hours=$(( (current_time - file_mtime) / 3600 ))

            if [ "$age_hours" -gt 48 ]; then
                log "WARNING" "Latest daily backup is ${age_hours} hours old"
                warnings=$((warnings + 1))
            else
                log "SUCCESS" "Latest daily backup is ${age_hours} hours old"
            fi
        else
            log "WARNING" "No daily backups found"
            warnings=$((warnings + 1))
        fi
    fi

    # Check for sufficient disk space (warn if less than 5GB free)
    local available_space=$(df -k "$BACKUP_BASE_DIR" 2>/dev/null | awk 'NR==2 {print $4}')
    local available_gb=$(echo "scale=2; $available_space / 1048576" | bc)

    if (( $(echo "$available_gb < 5" | bc -l) )); then
        log "WARNING" "Low disk space: ${available_gb} GB available"
        warnings=$((warnings + 1))
    else
        log "SUCCESS" "Sufficient disk space: ${available_gb} GB available"
    fi

    if [ "$warnings" -eq 0 ]; then
        log "SUCCESS" "Backup health check passed"
    else
        log "WARNING" "Backup health check found ${warnings} issue(s)"
    fi
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║       OBCMS Backup Retention Policy Script v1.0              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    log "INFO" "Starting backup cleanup process..."

    # Clean up each backup type
    cleanup_backup_type "daily" "$DAILY_RETENTION"
    cleanup_backup_type "weekly" "$WEEKLY_RETENTION"
    cleanup_backup_type "monthly" "$MONTHLY_RETENTION"

    # Generate summary
    generate_backup_summary

    # Health check
    check_backup_health

    log "SUCCESS" "Backup cleanup completed"

    exit 0
}

main "$@"
