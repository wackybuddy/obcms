#!/bin/bash
# ============================================================================
# PostgreSQL Read Replica Setup Script for OBCMS
# ============================================================================
# This script sets up a PostgreSQL read replica using streaming replication
#
# Usage:
#   ./setup-replica.sh REPLICA_NUMBER PRIMARY_HOST
#
# Example:
#   ./setup-replica.sh 1 10.0.1.10
#
# Prerequisites:
#   - PostgreSQL installed on replica server
#   - Network connectivity to primary server
#   - Replication user created on primary
#   - Replication slot created on primary
# ============================================================================

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Arguments
REPLICA_NUMBER="${1:-}"
PRIMARY_HOST="${2:-}"
PRIMARY_PORT="${3:-5432}"

# Settings
POSTGRES_VERSION="${POSTGRES_VERSION:-14}"
DATA_DIR="${PGDATA:-/var/lib/postgresql/${POSTGRES_VERSION}/main}"
REPLICATION_USER="${REPLICATION_USER:-replicator}"
REPLICATION_PASSWORD="${REPLICATION_PASSWORD:-}"
SLOT_NAME="replica_${REPLICA_NUMBER}_slot"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat << EOF
Usage: $0 REPLICA_NUMBER PRIMARY_HOST [PRIMARY_PORT]

Set up PostgreSQL read replica using streaming replication

ARGUMENTS:
    REPLICA_NUMBER    Replica number (1, 2, 3, etc.)
    PRIMARY_HOST      IP address or hostname of primary server
    PRIMARY_PORT      PostgreSQL port on primary (default: 5432)

ENVIRONMENT VARIABLES:
    REPLICATION_USER      Replication username (default: replicator)
    REPLICATION_PASSWORD  Replication password (required)
    POSTGRES_VERSION      PostgreSQL version (default: 14)
    PGDATA                PostgreSQL data directory

EXAMPLE:
    export REPLICATION_PASSWORD='your_password'
    $0 1 10.0.1.10

EOF
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    if [ -z "$REPLICA_NUMBER" ] || [ -z "$PRIMARY_HOST" ]; then
        log_error "Missing required arguments"
        usage
        exit 1
    fi

    if [ -z "$REPLICATION_PASSWORD" ]; then
        log_error "REPLICATION_PASSWORD environment variable not set"
        exit 1
    fi

    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi

    if ! command -v pg_basebackup &> /dev/null; then
        log_error "pg_basebackup not found. Install PostgreSQL client tools."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

stop_postgres() {
    log_info "Stopping PostgreSQL service..."

    systemctl stop postgresql || true

    log_success "PostgreSQL stopped"
}

backup_existing_data() {
    log_info "Backing up existing data directory..."

    if [ -d "$DATA_DIR" ]; then
        local backup_dir="${DATA_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
        mv "$DATA_DIR" "$backup_dir"
        log_success "Backup created at: $backup_dir"
    else
        log_info "No existing data directory found"
    fi
}

test_primary_connection() {
    log_info "Testing connection to primary server..."

    if PGPASSWORD="$REPLICATION_PASSWORD" psql -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U "$REPLICATION_USER" -d postgres -c "SELECT 1" &> /dev/null; then
        log_success "Connection to primary server successful"
    else
        log_error "Cannot connect to primary server at ${PRIMARY_HOST}:${PRIMARY_PORT}"
        log_error "Please check:"
        log_error "  - Primary server is running"
        log_error "  - Replication user exists"
        log_error "  - pg_hba.conf allows replication connections"
        log_error "  - Network connectivity (firewall rules)"
        exit 1
    fi
}

create_base_backup() {
    log_info "Creating base backup from primary server..."
    log_info "This may take several minutes depending on database size..."

    # Create .pgpass file for authentication
    local pgpass_file="/root/.pgpass"
    echo "${PRIMARY_HOST}:${PRIMARY_PORT}:replication:${REPLICATION_USER}:${REPLICATION_PASSWORD}" > "$pgpass_file"
    chmod 600 "$pgpass_file"

    # Run pg_basebackup
    mkdir -p "$DATA_DIR"

    if pg_basebackup \
        -h "$PRIMARY_HOST" \
        -p "$PRIMARY_PORT" \
        -D "$DATA_DIR" \
        -U "$REPLICATION_USER" \
        -P \
        -v \
        -R \
        -X stream \
        -C \
        -S "$SLOT_NAME"; then
        log_success "Base backup completed"
    else
        log_error "Base backup failed"
        exit 1
    fi

    # Clean up .pgpass
    rm -f "$pgpass_file"
}

configure_replica() {
    log_info "Configuring replica settings..."

    # Create recovery configuration (PostgreSQL 12+)
    cat > "${DATA_DIR}/standby.signal" << EOF
# Standby signal file
# This file indicates that this server is a standby
EOF

    # Update postgresql.conf for replica
    cat >> "${DATA_DIR}/postgresql.auto.conf" << EOF

# Read Replica Configuration - Added by setup-replica.sh
hot_standby = on
max_standby_streaming_delay = 30s
hot_standby_feedback = on
wal_receiver_status_interval = 10s
EOF

    # Set correct ownership
    chown -R postgres:postgres "$DATA_DIR"
    chmod 700 "$DATA_DIR"

    log_success "Replica configured"
}

start_postgres() {
    log_info "Starting PostgreSQL service..."

    systemctl start postgresql

    # Wait for PostgreSQL to start
    sleep 5

    if systemctl is-active --quiet postgresql; then
        log_success "PostgreSQL started successfully"
    else
        log_error "Failed to start PostgreSQL"
        exit 1
    fi
}

verify_replication() {
    log_info "Verifying replication status..."

    echo ""
    echo "=== Replication Status ==="

    # Check if in recovery mode
    if sudo -u postgres psql -c "SELECT pg_is_in_recovery();" | grep -q "t"; then
        log_success "Server is in recovery mode (replica mode)"
    else
        log_error "Server is NOT in recovery mode"
        exit 1
    fi

    # Show replication status
    echo ""
    echo "=== Replication Details ==="
    sudo -u postgres psql -x -c "SELECT * FROM pg_stat_wal_receiver;"

    echo ""
    echo "=== Current WAL Position ==="
    sudo -u postgres psql -c "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();"

    echo ""
    log_success "Replication verification complete"
}

display_summary() {
    echo ""
    echo "=========================================================================="
    echo " PostgreSQL Read Replica Setup Complete!"
    echo "=========================================================================="
    echo ""
    echo "Replica Information:"
    echo "  Replica Number: ${REPLICA_NUMBER}"
    echo "  Primary Host:   ${PRIMARY_HOST}:${PRIMARY_PORT}"
    echo "  Slot Name:      ${SLOT_NAME}"
    echo "  Data Directory: ${DATA_DIR}"
    echo ""
    echo "Verification Commands:"
    echo ""
    echo "  # Check if replica is in recovery mode"
    echo "  sudo -u postgres psql -c \"SELECT pg_is_in_recovery();\""
    echo ""
    echo "  # View replication status"
    echo "  sudo -u postgres psql -x -c \"SELECT * FROM pg_stat_wal_receiver;\""
    echo ""
    echo "  # Check replication lag"
    echo "  sudo -u postgres psql -c \"SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();\""
    echo ""
    echo "On Primary Server:"
    echo ""
    echo "  # View connected replicas"
    echo "  psql -c \"SELECT * FROM pg_stat_replication;\""
    echo ""
    echo "  # Check replication slots"
    echo "  psql -c \"SELECT * FROM pg_replication_slots;\""
    echo ""
    echo "NEXT STEPS:"
    echo ""
    echo "  1. Verify replication lag is minimal"
    echo "  2. Test read queries on replica"
    echo "  3. Configure PgBouncer to route SELECT queries to replica"
    echo "  4. Set up monitoring for replication lag"
    echo "  5. Document failover procedures"
    echo ""
    echo "IMPORTANT NOTES:"
    echo ""
    echo "  - This is a READ-ONLY replica (no writes allowed)"
    echo "  - Replication is asynchronous (minimal lag expected)"
    echo "  - Primary server must remain available"
    echo "  - Monitor replication lag regularly"
    echo "  - Test failover procedures in staging"
    echo ""
    echo "=========================================================================="
    echo ""
}

main() {
    echo ""
    echo "=========================================================================="
    echo " PostgreSQL Read Replica Setup - OBCMS"
    echo " Replica: ${REPLICA_NUMBER:-N/A}"
    echo " Primary: ${PRIMARY_HOST:-N/A}"
    echo "=========================================================================="
    echo ""

    # Check prerequisites
    check_prerequisites

    # Test connection to primary
    test_primary_connection

    # Stop PostgreSQL
    stop_postgres

    # Backup existing data
    backup_existing_data

    # Create base backup from primary
    create_base_backup

    # Configure replica
    configure_replica

    # Start PostgreSQL
    start_postgres

    # Verify replication
    verify_replication

    # Display summary
    display_summary
}

# Run main function
main
