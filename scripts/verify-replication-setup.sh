#!/bin/bash
# ============================================================================
# OBCMS Replication & PgBouncer Setup Verification Script
# ============================================================================
# This script verifies the complete replication and PgBouncer setup
#
# Usage:
#   ./verify-replication-setup.sh
#
# Checks:
#   - PgBouncer configuration files
#   - PostgreSQL replication setup
#   - Read replica status
#   - Connection pooling
#   - Replication lag
# ============================================================================

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Functions
log_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((PASSED++))
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((FAILED++))
}

check_file_exists() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        log_success "$description exists"
        return 0
    else
        log_error "$description not found: $file"
        return 1
    fi
}

check_file_permissions() {
    local file=$1
    local expected=$2
    local description=$3

    if [ ! -f "$file" ]; then
        log_error "$description not found"
        return 1
    fi

    local actual=$(stat -f "%OLp" "$file" 2>/dev/null || stat -c "%a" "$file" 2>/dev/null)

    if [ "$actual" = "$expected" ] || [ "$actual" = "644" ] || [ "$actual" = "640" ]; then
        log_success "$description has correct permissions ($actual)"
        return 0
    else
        log_warning "$description permissions: $actual (expected: $expected)"
        return 0
    fi
}

check_pgbouncer_config() {
    log_header "PgBouncer Configuration"

    local pgbouncer_ini="/Users/saidamenmambayao/apps/obcms/config/pgbouncer/pgbouncer.ini"
    local userlist_txt="/Users/saidamenmambayao/apps/obcms/config/pgbouncer/userlist.txt"

    # Check files exist
    check_file_exists "$pgbouncer_ini" "pgbouncer.ini"
    check_file_exists "$userlist_txt" "userlist.txt"

    # Check permissions
    check_file_permissions "$userlist_txt" "600" "userlist.txt"

    # Check for placeholder values
    if [ -f "$userlist_txt" ]; then
        if grep -q "REPLACE_WITH" "$userlist_txt"; then
            log_warning "userlist.txt contains placeholder hashes (need to run generate-pgbouncer-hashes.sh)"
        else
            log_success "userlist.txt has actual MD5 hashes configured"
        fi

        # Count configured users
        local user_count=$(grep -c '^"[^;#]' "$userlist_txt" 2>/dev/null || echo 0)
        if [ "$user_count" -gt 0 ]; then
            log_info "  Users configured: $user_count"
        fi
    fi

    # Check pgbouncer.ini settings
    if [ -f "$pgbouncer_ini" ]; then
        local pool_mode=$(grep "^pool_mode" "$pgbouncer_ini" | awk '{print $3}' || echo "not set")
        local pool_size=$(grep "^default_pool_size" "$pgbouncer_ini" | awk '{print $3}' || echo "not set")
        local max_clients=$(grep "^max_client_conn" "$pgbouncer_ini" | awk '{print $3}' || echo "not set")

        log_info "  Pool mode: $pool_mode"
        log_info "  Default pool size: $pool_size"
        log_info "  Max client connections: $max_clients"

        if [ "$pool_mode" = "transaction" ]; then
            log_success "Pool mode set to 'transaction' (recommended)"
        else
            log_warning "Pool mode is '$pool_mode' (recommended: transaction)"
        fi
    fi
}

check_scripts() {
    log_header "Setup Scripts"

    local scripts_dir="/Users/saidamenmambayao/apps/obcms/scripts"

    check_file_exists "$scripts_dir/generate-pgbouncer-hashes.sh" "Hash generator script"
    check_file_exists "$scripts_dir/init-database.sh" "Database init script"
    check_file_exists "$scripts_dir/setup-postgres-replication.sh" "Replication setup script"
    check_file_exists "$scripts_dir/setup-replica.sh" "Replica setup script"

    # Check if scripts are executable
    for script in generate-pgbouncer-hashes.sh init-database.sh setup-postgres-replication.sh setup-replica.sh; do
        if [ -x "$scripts_dir/$script" ]; then
            log_success "$script is executable"
        else
            log_warning "$script is not executable (run: chmod +x scripts/$script)"
        fi
    done
}

check_documentation() {
    log_header "Documentation"

    local docs_dir="/Users/saidamenmambayao/apps/obcms/docs/deployment"

    check_file_exists "$docs_dir/DATABASE_REPLICATION_SETUP.md" "Complete setup guide"
    check_file_exists "$docs_dir/PGBOUNCER_REPLICATION_QUICK_REFERENCE.md" "Quick reference"
    check_file_exists "$docs_dir/REPLICATION_README.md" "README"
}

check_postgresql() {
    log_header "PostgreSQL Installation"

    # Check if PostgreSQL is installed
    if command -v psql &> /dev/null; then
        local pg_version=$(psql --version | awk '{print $3}')
        log_success "PostgreSQL client installed (version: $pg_version)"
    else
        log_error "PostgreSQL client (psql) not found"
        return
    fi

    # Check if PostgreSQL server is running (optional - may not be on this machine)
    if command -v pg_isready &> /dev/null; then
        if pg_isready &> /dev/null; then
            log_success "PostgreSQL server is running"

            # Check PostgreSQL version on server
            local server_version=$(psql -U postgres -t -c "SHOW server_version;" 2>/dev/null | xargs || echo "unknown")
            log_info "  Server version: $server_version"
        else
            log_warning "PostgreSQL server not running or not accessible from this machine"
        fi
    fi
}

check_replication_status() {
    log_header "Replication Status (if PostgreSQL is accessible)"

    # Only check if we can connect to PostgreSQL
    if ! command -v psql &> /dev/null; then
        log_warning "PostgreSQL client not installed, skipping replication checks"
        return
    fi

    # Try to connect as postgres user
    if psql -U postgres -c "SELECT 1" &> /dev/null; then
        # Check if replication user exists
        if psql -U postgres -t -c "SELECT usename FROM pg_user WHERE usename = 'replicator';" 2>/dev/null | grep -q "replicator"; then
            log_success "Replication user 'replicator' exists"
        else
            log_warning "Replication user 'replicator' not found (run setup-postgres-replication.sh)"
        fi

        # Check replication slots
        local slot_count=$(psql -U postgres -t -c "SELECT count(*) FROM pg_replication_slots;" 2>/dev/null | xargs || echo 0)
        if [ "$slot_count" -gt 0 ]; then
            log_success "Replication slots configured ($slot_count slots)"
            psql -U postgres -c "SELECT slot_name, active FROM pg_replication_slots;" 2>/dev/null | sed 's/^/  /' || true
        else
            log_warning "No replication slots found (run setup-postgres-replication.sh)"
        fi

        # Check active replicas
        local replica_count=$(psql -U postgres -t -c "SELECT count(*) FROM pg_stat_replication;" 2>/dev/null | xargs || echo 0)
        if [ "$replica_count" -gt 0 ]; then
            log_success "Active replicas: $replica_count"
            psql -U postgres -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;" 2>/dev/null | sed 's/^/  /' || true
        else
            log_info "No active replicas (replicas not yet configured)"
        fi

        # Check replication configuration
        local wal_level=$(psql -U postgres -t -c "SHOW wal_level;" 2>/dev/null | xargs || echo "unknown")
        if [ "$wal_level" = "replica" ] || [ "$wal_level" = "logical" ]; then
            log_success "WAL level configured for replication: $wal_level"
        else
            log_warning "WAL level is '$wal_level' (expected: replica)"
        fi

    else
        log_warning "Cannot connect to PostgreSQL as postgres user (may require sudo or different credentials)"
    fi
}

check_pgbouncer_connection() {
    log_header "PgBouncer Connection (if running)"

    # Check if PgBouncer is listening on port 6432
    if command -v nc &> /dev/null; then
        if nc -z localhost 6432 2>/dev/null; then
            log_success "PgBouncer is listening on port 6432"

            # Try to get pool status (requires credentials)
            log_info "To check pool status, run: psql -h localhost -p 6432 -U pgbouncer pgbouncer -c 'SHOW POOLS;'"
        else
            log_warning "PgBouncer is not running on port 6432 (not started yet)"
        fi
    else
        log_warning "netcat (nc) not installed, cannot check if PgBouncer is running"
    fi
}

check_environment_variables() {
    log_header "Environment Variables"

    # Check if .env file exists
    if [ -f "/Users/saidamenmambayao/apps/obcms/.env" ]; then
        log_success ".env file exists"

        # Check for required variables (without exposing values)
        for var in DB_PASSWORD REPLICATION_PASSWORD MONITORING_PASSWORD DATABASE_URL; do
            if grep -q "^${var}=" /Users/saidamenmambayao/apps/obcms/.env 2>/dev/null; then
                log_success "$var is set in .env"
            else
                log_warning "$var not found in .env"
            fi
        done
    else
        log_warning ".env file not found (recommended for storing credentials)"
    fi
}

display_summary() {
    log_header "Verification Summary"

    echo ""
    echo "Results:"
    echo -e "  ${GREEN}Passed:${NC}   $PASSED"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
    echo -e "  ${RED}Failed:${NC}   $FAILED"
    echo ""

    if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed! Setup is complete.${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Start PgBouncer: docker-compose up -d pgbouncer"
        echo "  2. Test connection: psql -h localhost -p 6432 -U obcms_app -d obcms"
        echo "  3. Configure read replicas (if needed)"
        echo "  4. Update Django settings to use PgBouncer"
    elif [ $FAILED -eq 0 ]; then
        echo -e "${YELLOW}⚠ Setup is mostly complete with some warnings.${NC}"
        echo ""
        echo "Review warnings above and complete any pending setup steps."
    else
        echo -e "${RED}✗ Setup is incomplete. Please address the failed checks.${NC}"
        echo ""
        echo "Common fixes:"
        echo "  - Run: ./scripts/generate-pgbouncer-hashes.sh -i"
        echo "  - Update config/pgbouncer/userlist.txt with generated hashes"
        echo "  - Run: sudo ./scripts/init-database.sh staging"
        echo "  - Run: sudo ./scripts/setup-postgres-replication.sh staging"
    fi

    echo ""
}

main() {
    echo ""
    echo "=========================================================================="
    echo " OBCMS Replication & PgBouncer Setup Verification"
    echo "=========================================================================="
    echo ""

    check_pgbouncer_config
    check_scripts
    check_documentation
    check_postgresql
    check_replication_status
    check_pgbouncer_connection
    check_environment_variables
    display_summary
}

# Run main function
main
