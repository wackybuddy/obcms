#!/bin/bash
# ============================================================================
# OBCMS Database Initialization Script
# ============================================================================
# This script initializes the PostgreSQL database for OBCMS
# Creates databases, users, extensions, and runs initial migrations
#
# Usage:
#   ./init-database.sh [staging|production]
#
# Prerequisites:
#   - PostgreSQL 14+ installed and running
#   - Root or postgres user access
#   - Environment variables set (see .env.example)
# ============================================================================

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Environment
ENVIRONMENT="${1:-staging}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Database settings
DB_NAME="${DB_NAME:-obcms}"
DB_USER="${DB_USER:-obcms_app}"
DB_PASSWORD="${DB_PASSWORD:-PLEASE_SET_DB_PASSWORD}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Additional users
REPLICATION_USER="${REPLICATION_USER:-replicator}"
REPLICATION_PASSWORD="${REPLICATION_PASSWORD:-PLEASE_SET_REPLICATION_PASSWORD}"
MONITORING_USER="${MONITORING_USER:-monitoring}"
MONITORING_PASSWORD="${MONITORING_PASSWORD:-PLEASE_SET_MONITORING_PASSWORD}"

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

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL client (psql) not found"
        exit 1
    fi

    # Check PostgreSQL is running
    if ! sudo -u postgres psql -c "SELECT 1" &> /dev/null; then
        log_error "Cannot connect to PostgreSQL. Is the server running?"
        exit 1
    fi

    # Check passwords are set
    if [ "$DB_PASSWORD" = "PLEASE_SET_DB_PASSWORD" ]; then
        log_error "Please set DB_PASSWORD environment variable"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

create_database_user() {
    log_info "Creating database user: $DB_USER..."

    sudo -u postgres psql << EOF
-- Create application user
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${DB_USER}') THEN
        CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
        RAISE NOTICE 'User ${DB_USER} created';
    ELSE
        ALTER USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
        RAISE NOTICE 'User ${DB_USER} already exists, password updated';
    END IF;
END
\$\$;

-- Grant necessary privileges
ALTER USER ${DB_USER} WITH CREATEDB;
EOF

    log_success "Database user created/updated"
}

create_monitoring_user() {
    log_info "Creating monitoring user: $MONITORING_USER..."

    sudo -u postgres psql << EOF
-- Create monitoring user
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${MONITORING_USER}') THEN
        CREATE USER ${MONITORING_USER} WITH PASSWORD '${MONITORING_PASSWORD}';
        RAISE NOTICE 'User ${MONITORING_USER} created';
    ELSE
        ALTER USER ${MONITORING_USER} WITH PASSWORD '${MONITORING_PASSWORD}';
        RAISE NOTICE 'User ${MONITORING_USER} already exists, password updated';
    END IF;
END
\$\$;

-- Grant monitoring privileges (read-only on stats)
GRANT CONNECT ON DATABASE postgres TO ${MONITORING_USER};
GRANT pg_monitor TO ${MONITORING_USER};
EOF

    log_success "Monitoring user created/updated"
}

create_database() {
    log_info "Creating database: $DB_NAME..."

    sudo -u postgres psql << EOF
-- Create database if not exists
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')
\gexec

-- Update ownership
ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};
EOF

    log_success "Database created/updated"
}

configure_database() {
    log_info "Configuring database settings..."

    sudo -u postgres psql -d "$DB_NAME" << EOF
-- Set timezone to Asia/Manila (Philippines)
ALTER DATABASE ${DB_NAME} SET timezone TO 'Asia/Manila';

-- Set statement timeout (prevent long-running queries)
ALTER DATABASE ${DB_NAME} SET statement_timeout TO '300s';

-- Set idle in transaction timeout
ALTER DATABASE ${DB_NAME} SET idle_in_transaction_session_timeout TO '60s';

-- Set search path
ALTER DATABASE ${DB_NAME} SET search_path TO public;

-- Set default text search configuration
ALTER DATABASE ${DB_NAME} SET default_text_search_config TO 'pg_catalog.english';
EOF

    log_success "Database configured"
}

create_extensions() {
    log_info "Creating PostgreSQL extensions..."

    sudo -u postgres psql -d "$DB_NAME" << EOF
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- For better indexing

-- Display enabled extensions
SELECT extname, extversion FROM pg_extension ORDER BY extname;
EOF

    log_success "Extensions created"
}

grant_permissions() {
    log_info "Granting permissions..."

    sudo -u postgres psql -d "$DB_NAME" << EOF
-- Grant all privileges to application user
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
GRANT ALL ON SCHEMA public TO ${DB_USER};
GRANT ALL ON ALL TABLES IN SCHEMA public TO ${DB_USER};
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER};
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO ${DB_USER};

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO ${DB_USER};

-- Grant monitoring user read-only access
GRANT CONNECT ON DATABASE ${DB_NAME} TO ${MONITORING_USER};
GRANT USAGE ON SCHEMA public TO ${MONITORING_USER};
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ${MONITORING_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ${MONITORING_USER};
EOF

    log_success "Permissions granted"
}

run_migrations() {
    log_info "Running Django migrations..."

    # Check if Django project exists
    if [ ! -f "$PROJECT_ROOT/src/manage.py" ]; then
        log_warning "Django manage.py not found, skipping migrations"
        return
    fi

    cd "$PROJECT_ROOT/src"

    # Activate virtual environment if exists
    if [ -d "$PROJECT_ROOT/venv" ]; then
        source "$PROJECT_ROOT/venv/bin/activate"
    fi

    # Run migrations
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput

    log_success "Migrations completed"
}

create_database_backup() {
    log_info "Creating initial database backup..."

    local backup_dir="/var/backups/postgresql/obcms"
    local backup_file="${backup_dir}/init_backup_$(date +%Y%m%d_%H%M%S).sql"

    sudo mkdir -p "$backup_dir"

    sudo -u postgres pg_dump "$DB_NAME" | sudo tee "$backup_file" > /dev/null
    sudo gzip "$backup_file"

    log_success "Initial backup created: ${backup_file}.gz"
}

verify_setup() {
    log_info "Verifying database setup..."

    echo ""
    echo "=== Database Information ==="
    sudo -u postgres psql -d "$DB_NAME" << EOF
SELECT
    current_database() as database,
    current_user as user,
    version() as version;
EOF

    echo ""
    echo "=== Database Size ==="
    sudo -u postgres psql -d "$DB_NAME" << EOF
SELECT pg_size_pretty(pg_database_size('${DB_NAME}')) as size;
EOF

    echo ""
    echo "=== Extensions ==="
    sudo -u postgres psql -d "$DB_NAME" << EOF
SELECT extname, extversion FROM pg_extension ORDER BY extname;
EOF

    echo ""
    echo "=== Users ==="
    sudo -u postgres psql << EOF
SELECT usename, usecreatedb, userepl FROM pg_user WHERE usename IN ('${DB_USER}', '${MONITORING_USER}', '${REPLICATION_USER}');
EOF

    echo ""
    echo "=== Connection Test ==="
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 'Connection successful!' as status;" 2>&1; then
        log_success "Connection test passed"
    else
        log_error "Connection test failed"
    fi

    echo ""
    log_success "Verification complete"
}

display_summary() {
    echo ""
    echo "=========================================================================="
    echo " OBCMS Database Initialization Complete!"
    echo "=========================================================================="
    echo ""
    echo "Environment: ${ENVIRONMENT}"
    echo ""
    echo "DATABASE CREDENTIALS:"
    echo "  Host:     ${DB_HOST}"
    echo "  Port:     ${DB_PORT}"
    echo "  Database: ${DB_NAME}"
    echo "  User:     ${DB_USER}"
    echo "  Password: ${DB_PASSWORD}"
    echo ""
    echo "MONITORING CREDENTIALS:"
    echo "  User:     ${MONITORING_USER}"
    echo "  Password: ${MONITORING_PASSWORD}"
    echo ""
    echo "CONNECTION STRING:"
    echo "  postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    echo ""
    echo "DJANGO SETTINGS:"
    echo "  Add to .env file:"
    echo "  DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    echo ""
    echo "NEXT STEPS:"
    echo "  1. Update .env file with database credentials"
    echo "  2. Configure PgBouncer (scripts/setup-pgbouncer.sh)"
    echo "  3. Set up replication (scripts/setup-postgres-replication.sh)"
    echo "  4. Test Django connection: python src/manage.py dbshell"
    echo "  5. Create superuser: python src/manage.py createsuperuser"
    echo ""
    echo "SECURITY REMINDER:"
    echo "  - Store credentials securely (use .env, not version control)"
    echo "  - Update passwords for production"
    echo "  - Configure firewall rules"
    echo "  - Enable SSL/TLS for production"
    echo ""
    echo "=========================================================================="
    echo ""
}

main() {
    echo ""
    echo "=========================================================================="
    echo " OBCMS Database Initialization Script"
    echo " Environment: ${ENVIRONMENT}"
    echo "=========================================================================="
    echo ""

    # Check prerequisites
    check_prerequisites

    # Create users
    create_database_user
    create_monitoring_user

    # Create and configure database
    create_database
    configure_database
    create_extensions
    grant_permissions

    # Run migrations
    run_migrations

    # Create backup
    create_database_backup

    # Verify
    verify_setup

    # Display summary
    display_summary
}

# Run main function
main
