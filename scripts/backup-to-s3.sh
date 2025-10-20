#!/bin/bash

##############################################################################
# OBCMS S3 Offsite Backup Script (OPTIONAL)
#
# Description: Uploads backups to AWS S3 for offsite storage
# Usage: ./backup-to-s3.sh [daily|weekly|monthly]
#
# Requirements:
#   - AWS CLI installed: pip install awscli
#   - AWS credentials configured: aws configure
#   - S3 bucket created
#
# Environment Variables:
#   - AWS_S3_BACKUP_BUCKET: S3 bucket name (e.g., obcms-backups)
#   - AWS_REGION: AWS region (e.g., us-west-2)
##############################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_TYPE="${1:-daily}"
BACKUP_BASE_DIR="${PROJECT_ROOT}/backups"
BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_TYPE}"

# AWS Configuration
AWS_S3_BACKUP_BUCKET="${AWS_S3_BACKUP_BUCKET:-}"
AWS_REGION="${AWS_REGION:-us-west-2}"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/s3-backup-$(date +"%Y-%m").log"

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

    if ! command -v aws &> /dev/null; then
        log "ERROR" "AWS CLI is not installed"
        log "ERROR" "Install with: pip install awscli"
        exit 1
    fi

    if [ -z "$AWS_S3_BACKUP_BUCKET" ]; then
        log "ERROR" "AWS_S3_BACKUP_BUCKET is not set"
        log "ERROR" "Set environment variable or update .env file"
        exit 1
    fi

    # Test AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log "ERROR" "AWS credentials not configured"
        log "ERROR" "Run: aws configure"
        exit 1
    fi

    log "SUCCESS" "All dependencies satisfied"
}

upload_to_s3() {
    log "INFO" "Uploading backups to S3..."
    log "INFO" "Bucket: s3://${AWS_S3_BACKUP_BUCKET}/${BACKUP_TYPE}/"

    if [ ! -d "$BACKUP_DIR" ]; then
        log "ERROR" "Backup directory not found: ${BACKUP_DIR}"
        exit 1
    fi

    local file_count=0
    local success_count=0
    local failed_count=0
    local total_size=0

    # Upload all backup files
    while IFS= read -r -d '' backup_file; do
        file_count=$((file_count + 1))

        local file_name=$(basename "$backup_file")
        local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
        local size_mb=$(echo "scale=2; $file_size / 1048576" | bc)

        log "INFO" "Uploading: ${file_name} (${size_mb} MB)"

        # Upload to S3 with server-side encryption
        if aws s3 cp "$backup_file" \
            "s3://${AWS_S3_BACKUP_BUCKET}/${BACKUP_TYPE}/${file_name}" \
            --region "$AWS_REGION" \
            --storage-class STANDARD_IA \
            --server-side-encryption AES256 \
            2>> "$LOG_FILE"; then

            log "SUCCESS" "Uploaded: ${file_name}"
            success_count=$((success_count + 1))
            total_size=$((total_size + file_size))
        else
            log "ERROR" "Failed to upload: ${file_name}"
            failed_count=$((failed_count + 1))
        fi
    done < <(find "$BACKUP_DIR" -type f \( -name "*.sql.gz" -o -name "*.tar.gz" \) -print0 2>/dev/null)

    local total_mb=$(echo "scale=2; $total_size / 1048576" | bc)

    log "INFO" "Upload summary: ${success_count} succeeded, ${failed_count} failed (${total_mb} MB total)"

    if [ "$failed_count" -gt 0 ]; then
        return 1
    fi

    return 0
}

list_s3_backups() {
    log "INFO" "Listing S3 backups..."

    if aws s3 ls "s3://${AWS_S3_BACKUP_BUCKET}/${BACKUP_TYPE}/" --region "$AWS_REGION"; then
        log "SUCCESS" "S3 listing completed"
    else
        log "WARNING" "Failed to list S3 backups"
    fi
}

generate_report() {
    log "INFO" "Generating S3 backup report..."

    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║            OBCMS S3 Offsite Backup Report                    ║
╚══════════════════════════════════════════════════════════════╝

Backup Type:      ${BACKUP_TYPE}
Timestamp:        $(date +"%Y-%m-%d %H:%M:%S")

S3 Configuration:
  Bucket:         s3://${AWS_S3_BACKUP_BUCKET}
  Region:         ${AWS_REGION}
  Storage Class:  STANDARD_IA
  Encryption:     AES256

Status:           SUCCESS ✓

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
    echo "║       OBCMS S3 Offsite Backup Script v1.0                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Validate backup type
    if [[ ! "$BACKUP_TYPE" =~ ^(daily|weekly|monthly)$ ]]; then
        log "ERROR" "Invalid backup type: ${BACKUP_TYPE}"
        echo "Usage: $0 [daily|weekly|monthly]"
        exit 1
    fi

    check_dependencies

    if upload_to_s3; then
        list_s3_backups
        generate_report
        log "SUCCESS" "S3 backup completed successfully"
        exit 0
    else
        log "ERROR" "S3 backup failed"
        exit 1
    fi
}

main "$@"
