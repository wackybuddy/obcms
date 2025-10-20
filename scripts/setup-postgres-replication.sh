#!/bin/bash
# ============================================================================
# PostgreSQL Replication Setup Script for OBCMS
# ============================================================================
# This script configures PostgreSQL for streaming replication
# Supports: Staging (1 replica), Production (3 replicas)
#
# Usage:
#   ./setup-postgres-replication.sh [staging|production]
#
# Prerequisites:
#   - PostgreSQL 14+ installed
#   - Root or postgres user access
#   - Network connectivity between primary and replicas
# ============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Environment detection
ENVIRONMENT="${1:-staging}"
POSTGRES_VERSION="${POSTGRES_VERSION:-14}"
DATA_DIR="${PGDATA:-/var/lib/postgresql/${POSTGRES_VERSION}/main}"
POSTGRES_CONF="${DATA_DIR}/postgresql.conf"
PG_HBA_CONF="${DATA_DIR}/pg_hba.conf"

# Replication settings
REPLICATION_USER="replicator"
REPLICATION_PASSWORD="${REPLICATION_PASSWORD:-PLEASE_SET_REPLICATION_PASSWORD}"
MAX_WAL_SENDERS=10
WAL_KEEP_SIZE="1GB"
MAX_REPLICATION_SLOTS=10

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

check_postgres() {
    log_info "Checking PostgreSQL installation..."

    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL client (psql) not found"
        exit 1
    fi

    if ! sudo -u postgres psql -c "SELECT version();" &> /dev/null; then
        log_error "Cannot connect to PostgreSQL. Is the server running?"
        exit 1
    fi

    log_success "PostgreSQL is running"
}

backup_configs() {
    log_info "Backing up configuration files..."

    local backup_dir="/var/backups/postgresql/$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$backup_dir"

    if [ -f "$POSTGRES_CONF" ]; then
        sudo cp "$POSTGRES_CONF" "$backup_dir/postgresql.conf.bak"
    fi

    if [ -f "$PG_HBA_CONF" ]; then
        sudo cp "$PG_HBA_CONF" "$backup_dir/pg_hba.conf.bak"
    fi

    log_success "Backup created at $backup_dir"
}

create_replication_user() {
    log_info "Creating replication user..."

    sudo -u postgres psql << EOF
-- Create replication user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${REPLICATION_USER}') THEN
        CREATE USER ${REPLICATION_USER} WITH REPLICATION LOGIN PASSWORD '${REPLICATION_PASSWORD}';
        RAISE NOTICE 'User ${REPLICATION_USER} created';
    ELSE
        ALTER USER ${REPLICATION_USER} WITH REPLICATION LOGIN PASSWORD '${REPLICATION_PASSWORD}';
        RAISE NOTICE 'User ${REPLICATION_USER} already exists, password updated';
    END IF;
END
\$\$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE obcms TO ${REPLICATION_USER};
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ${REPLICATION_USER};
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO ${REPLICATION_USER};

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ${REPLICATION_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO ${REPLICATION_USER};
EOF

    log_success "Replication user created/updated"
}

configure_primary() {
    log_info "Configuring primary PostgreSQL server for replication..."

    # Update postgresql.conf
    sudo -u postgres psql -c "ALTER SYSTEM SET wal_level = 'replica';"
    sudo -u postgres psql -c "ALTER SYSTEM SET max_wal_senders = ${MAX_WAL_SENDERS};"
    sudo -u postgres psql -c "ALTER SYSTEM SET wal_keep_size = '${WAL_KEEP_SIZE}';"
    sudo -u postgres psql -c "ALTER SYSTEM SET max_replication_slots = ${MAX_REPLICATION_SLOTS};"
    sudo -u postgres psql -c "ALTER SYSTEM SET hot_standby = on;"
    sudo -u postgres psql -c "ALTER SYSTEM SET wal_log_hints = on;"
    sudo -u postgres psql -c "ALTER SYSTEM SET archive_mode = on;"
    sudo -u postgres psql -c "ALTER SYSTEM SET archive_command = '/bin/true';"  # Dummy archive command

    # Checkpoint settings for better replication performance
    sudo -u postgres psql -c "ALTER SYSTEM SET checkpoint_timeout = '15min';"
    sudo -u postgres psql -c "ALTER SYSTEM SET max_wal_size = '4GB';"
    sudo -u postgres psql -c "ALTER SYSTEM SET min_wal_size = '1GB';"

    # Standby feedback (prevents query conflicts on standby)
    sudo -u postgres psql -c "ALTER SYSTEM SET hot_standby_feedback = on;"

    log_success "Primary server configuration updated"
}

configure_pg_hba() {
    log_info "Configuring pg_hba.conf for replication..."

    # Backup original
    if [ ! -f "${PG_HBA_CONF}.orig" ]; then
        sudo cp "$PG_HBA_CONF" "${PG_HBA_CONF}.orig"
    fi

    # Add replication entries
    local hba_entries="
# Replication connections for OBCMS
# Allow replication user from same subnet
host    replication     ${REPLICATION_USER}     10.0.0.0/8          md5
host    replication     ${REPLICATION_USER}     172.16.0.0/12       md5
host    replication     ${REPLICATION_USER}     192.168.0.0/16      md5

# Allow replication user from localhost
host    replication     ${REPLICATION_USER}     127.0.0.1/32        md5
host    replication     ${REPLICATION_USER}     ::1/128             md5
"

    # Check if entries already exist
    if ! sudo grep -q "# Replication connections for OBCMS" "$PG_HBA_CONF"; then
        echo "$hba_entries" | sudo tee -a "$PG_HBA_CONF" > /dev/null
        log_success "pg_hba.conf updated with replication entries"
    else
        log_warning "Replication entries already exist in pg_hba.conf"
    fi
}

create_replication_slots() {
    log_info "Creating replication slots..."

    local num_replicas=1
    if [ "$ENVIRONMENT" = "production" ]; then
        num_replicas=3
    fi

    for i in $(seq 1 $num_replicas); do
        local slot_name="replica_${i}_slot"

        sudo -u postgres psql << EOF
-- Create replication slot if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = '${slot_name}') THEN
        PERFORM pg_create_physical_replication_slot('${slot_name}');
        RAISE NOTICE 'Replication slot ${slot_name} created';
    ELSE
        RAISE NOTICE 'Replication slot ${slot_name} already exists';
    END IF;
END
\$\$;
EOF
    done

    log_success "Replication slots created for $num_replicas replica(s)"
}

reload_postgres() {
    log_info "Reloading PostgreSQL configuration..."

    sudo -u postgres psql -c "SELECT pg_reload_conf();"

    log_success "PostgreSQL configuration reloaded"
}

verify_setup() {
    log_info "Verifying replication setup..."

    echo ""
    echo "=== PostgreSQL Version ==="
    sudo -u postgres psql -c "SELECT version();"

    echo ""
    echo "=== Replication Settings ==="
    sudo -u postgres psql -c "SHOW wal_level; SHOW max_wal_senders; SHOW wal_keep_size;"

    echo ""
    echo "=== Replication User ==="
    sudo -u postgres psql -c "SELECT usename, userepl FROM pg_user WHERE usename = '${REPLICATION_USER}';"

    echo ""
    echo "=== Replication Slots ==="
    sudo -u postgres psql -c "SELECT slot_name, slot_type, active, restart_lsn FROM pg_replication_slots;"

    echo ""
    echo "=== Current WAL Position ==="
    sudo -u postgres psql -c "SELECT pg_current_wal_lsn();"

    log_success "Verification complete"
}

display_next_steps() {
    echo ""
    echo "=========================================================================="
    echo " PostgreSQL Replication Setup Complete!"
    echo "=========================================================================="
    echo ""
    echo "Primary server is now configured for replication."
    echo ""
    echo "NEXT STEPS:"
    echo ""
    echo "1. Set up replica server(s):"
    echo "   - Install PostgreSQL ${POSTGRES_VERSION} on replica server(s)"
    echo "   - Run: pg_basebackup -h PRIMARY_HOST -D /var/lib/postgresql/${POSTGRES_VERSION}/main -U ${REPLICATION_USER} -P -v -R -X stream -C -S replica_1_slot"
    echo ""
    echo "2. Update PgBouncer configuration:"
    echo "   - Edit config/pgbouncer/pgbouncer.ini"
    echo "   - Uncomment replica database entries"
    echo "   - Update userlist.txt with replication user hash"
    echo ""
    echo "3. Configure Django for read replicas:"
    echo "   - Update DATABASE_ROUTERS in settings/production.py"
    echo "   - Test read/write splitting"
    echo ""
    echo "4. Verify replication status:"
    echo "   - On primary: SELECT * FROM pg_stat_replication;"
    echo "   - On replica: SELECT pg_is_in_recovery();"
    echo ""
    echo "REPLICATION USER CREDENTIALS:"
    echo "   Username: ${REPLICATION_USER}"
    echo "   Password: ${REPLICATION_PASSWORD}"
    echo ""
    echo "IMPORTANT: Store credentials securely and update .env files"
    echo "=========================================================================="
    echo ""
}

main() {
    echo ""
    echo "=========================================================================="
    echo " PostgreSQL Replication Setup - OBCMS"
    echo " Environment: ${ENVIRONMENT}"
    echo "=========================================================================="
    echo ""

    # Preflight checks
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi

    if [ "$REPLICATION_PASSWORD" = "PLEASE_SET_REPLICATION_PASSWORD" ]; then
        log_error "Please set REPLICATION_PASSWORD environment variable"
        echo "Example: export REPLICATION_PASSWORD='your_secure_password'"
        exit 1
    fi

    # Execute setup
    check_postgres
    backup_configs
    create_replication_user
    configure_primary
    configure_pg_hba
    create_replication_slots
    reload_postgres
    verify_setup
    display_next_steps
}

# Run main function
main
