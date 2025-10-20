#!/bin/bash

##############################################################################
# OBCMS Backup Monitoring Script
#
# Description: Monitors backup health, generates reports, sends alerts
# Usage: ./backup-monitor.sh [--report|--alert|--status]
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_BASE_DIR="${PROJECT_ROOT}/backups"
MODE="${1:---status}"

# Thresholds
MAX_BACKUP_AGE_HOURS=48  # Alert if latest backup is older than 48 hours
MIN_BACKUP_SIZE_KB=100   # Alert if backup is smaller than 100KB
MIN_FREE_SPACE_GB=5      # Alert if less than 5GB free

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/monitor-$(date +"%Y-%m").log"

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

check_backup_age() {
    local backup_type="$1"
    local backup_dir="${BACKUP_BASE_DIR}/${backup_type}"

    if [ ! -d "$backup_dir" ]; then
        echo "MISSING"
        return
    fi

    local latest_backup=$(find "$backup_dir" -name "*.sql.gz" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -n1)

    if [ -z "$latest_backup" ]; then
        echo "NONE"
        return
    fi

    local file_mtime=$(stat -f%m "$latest_backup" 2>/dev/null || stat -c%Y "$latest_backup" 2>/dev/null)
    local current_time=$(date +%s)
    local age_hours=$(( (current_time - file_mtime) / 3600 ))

    echo "$age_hours"
}

check_backup_size() {
    local backup_type="$1"
    local backup_dir="${BACKUP_BASE_DIR}/${backup_type}"

    if [ ! -d "$backup_dir" ]; then
        echo "0"
        return
    fi

    local latest_backup=$(find "$backup_dir" -name "*.sql.gz" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -n1)

    if [ -z "$latest_backup" ]; then
        echo "0"
        return
    fi

    local file_size=$(stat -f%z "$latest_backup" 2>/dev/null || stat -c%s "$latest_backup" 2>/dev/null)
    echo "$file_size"
}

count_backups() {
    local backup_type="$1"
    local backup_dir="${BACKUP_BASE_DIR}/${backup_type}"

    if [ ! -d "$backup_dir" ]; then
        echo "0"
        return
    fi

    local count=$(find "$backup_dir" -name "*.sql.gz" -o -name "*.tar.gz" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "$count"
}

calculate_total_size() {
    if [ ! -d "$BACKUP_BASE_DIR" ]; then
        echo "0"
        return
    fi

    local total_size=$(du -sk "$BACKUP_BASE_DIR" 2>/dev/null | cut -f1)
    echo "$total_size"
}

check_disk_space() {
    local available_space=$(df -k "$BACKUP_BASE_DIR" 2>/dev/null | awk 'NR==2 {print $4}')
    echo "$available_space"
}

generate_status_report() {
    log "INFO" "Generating backup status report..."

    # Collect metrics
    local daily_age=$(check_backup_age "daily")
    local weekly_age=$(check_backup_age "weekly")
    local monthly_age=$(check_backup_age "monthly")

    local daily_count=$(count_backups "daily")
    local weekly_count=$(count_backups "weekly")
    local monthly_count=$(count_backups "monthly")

    local total_size_kb=$(calculate_total_size)
    local total_size_mb=$(echo "scale=2; $total_size_kb / 1024" | bc)
    local total_size_gb=$(echo "scale=2; $total_size_kb / 1048576" | bc)

    local free_space_kb=$(check_disk_space)
    local free_space_gb=$(echo "scale=2; $free_space_kb / 1048576" | bc)

    # Determine health status
    local health_status="HEALTHY"
    local warnings=0

    if [ "$daily_age" != "MISSING" ] && [ "$daily_age" != "NONE" ] && [ "$daily_age" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
        health_status="WARNING"
        warnings=$((warnings + 1))
    fi

    if [ "$daily_age" == "NONE" ]; then
        health_status="CRITICAL"
        warnings=$((warnings + 1))
    fi

    if (( $(echo "$free_space_gb < $MIN_FREE_SPACE_GB" | bc -l) )); then
        health_status="WARNING"
        warnings=$((warnings + 1))
    fi

    # Generate report
    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║           OBCMS Backup Monitoring Report                     ║
╚══════════════════════════════════════════════════════════════╝

Generated: $(date +"%Y-%m-%d %H:%M:%S")
Health Status: ${health_status}

Backup Age (hours since last backup):
  Daily:    ${daily_age}
  Weekly:   ${weekly_age}
  Monthly:  ${monthly_age}

Backup Counts:
  Daily:    ${daily_count} backups
  Weekly:   ${weekly_count} backups
  Monthly:  ${monthly_count} backups

Storage:
  Total Used:     ${total_size_mb} MB (${total_size_gb} GB)
  Free Space:     ${free_space_gb} GB
  Location:       ${BACKUP_BASE_DIR}

Thresholds:
  Max Backup Age:       ${MAX_BACKUP_AGE_HOURS} hours
  Min Backup Size:      ${MIN_BACKUP_SIZE_KB} KB
  Min Free Space:       ${MIN_FREE_SPACE_GB} GB

EOF

    # Show warnings if any
    if [ "$warnings" -gt 0 ]; then
        echo "Warnings:"

        if [ "$daily_age" != "MISSING" ] && [ "$daily_age" != "NONE" ] && [ "$daily_age" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
            echo "  - Daily backup is ${daily_age} hours old (threshold: ${MAX_BACKUP_AGE_HOURS} hours)"
        fi

        if [ "$daily_age" == "NONE" ]; then
            echo "  - No daily backups found!"
        fi

        if (( $(echo "$free_space_gb < $MIN_FREE_SPACE_GB" | bc -l) )); then
            echo "  - Low disk space: ${free_space_gb} GB (threshold: ${MIN_FREE_SPACE_GB} GB)"
        fi

        echo ""
    fi

    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

generate_detailed_report() {
    log "INFO" "Generating detailed backup report..."

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         OBCMS Detailed Backup Report                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    for backup_type in daily weekly monthly; do
        echo "=== ${backup_type^^} BACKUPS ==="
        echo ""

        local backup_dir="${BACKUP_BASE_DIR}/${backup_type}"

        if [ ! -d "$backup_dir" ]; then
            echo "  Directory not found: ${backup_dir}"
            echo ""
            continue
        fi

        # List database backups
        echo "  Database Backups:"
        if [ "$(find "$backup_dir" -name "*.sql.gz" -type f 2>/dev/null | wc -l | tr -d ' ')" -gt 0 ]; then
            find "$backup_dir" -name "*.sql.gz" -type f -print0 2>/dev/null | xargs -0 ls -lh 2>/dev/null | tail -n 10 | awk '{printf "    %s  %s  %s\n", $5, $6" "$7, $9}'
        else
            echo "    None"
        fi

        echo ""

        # List media backups
        echo "  Media Backups:"
        if [ "$(find "$backup_dir" -name "*.tar.gz" -type f 2>/dev/null | wc -l | tr -d ' ')" -gt 0 ]; then
            find "$backup_dir" -name "*.tar.gz" -type f -print0 2>/dev/null | xargs -0 ls -lh 2>/dev/null | tail -n 10 | awk '{printf "    %s  %s  %s\n", $5, $6" "$7, $9}'
        else
            echo "    None"
        fi

        echo ""
    done

    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

check_alerts() {
    log "INFO" "Checking for backup alerts..."

    local alerts=()

    # Check daily backup age
    local daily_age=$(check_backup_age "daily")

    if [ "$daily_age" == "NONE" ]; then
        alerts+=("CRITICAL: No daily backups found")
    elif [ "$daily_age" != "MISSING" ] && [ "$daily_age" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
        alerts+=("WARNING: Daily backup is ${daily_age} hours old (threshold: ${MAX_BACKUP_AGE_HOURS})")
    fi

    # Check disk space
    local free_space_kb=$(check_disk_space)
    local free_space_gb=$(echo "scale=2; $free_space_kb / 1048576" | bc)

    if (( $(echo "$free_space_gb < $MIN_FREE_SPACE_GB" | bc -l) )); then
        alerts+=("WARNING: Low disk space - ${free_space_gb} GB available (threshold: ${MIN_FREE_SPACE_GB} GB)")
    fi

    # Display alerts
    if [ ${#alerts[@]} -gt 0 ]; then
        echo ""
        echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                    BACKUP ALERTS                             ║${NC}"
        echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""

        for alert in "${alerts[@]}"; do
            echo -e "${YELLOW}  • ${alert}${NC}"
            log "WARNING" "$alert"
        done

        echo ""
        return 1
    else
        log "SUCCESS" "No backup alerts"
        return 0
    fi
}

##############################################################################
# Main Execution
##############################################################################

main() {
    case "$MODE" in
        --status)
            generate_status_report
            ;;
        --report)
            generate_detailed_report
            ;;
        --alert)
            check_alerts
            ;;
        *)
            echo "Usage: $0 [--status|--report|--alert]"
            echo ""
            echo "Options:"
            echo "  --status   Show backup health status (default)"
            echo "  --report   Generate detailed backup report"
            echo "  --alert    Check for alerts and warnings"
            exit 1
            ;;
    esac

    exit 0
}

main "$@"
