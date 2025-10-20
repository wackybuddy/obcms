#!/bin/bash
# ============================================================================
# PgBouncer Password Hash Generator for OBCMS
# ============================================================================
# This script generates MD5 password hashes for PgBouncer userlist.txt
#
# Usage:
#   ./generate-pgbouncer-hashes.sh
#
# MD5 Hash Format for PostgreSQL/PgBouncer:
#   1. Concatenate: password + username
#   2. Calculate MD5 hash
#   3. Prefix with "md5"
#   Example: "MyPass123" + "obcms_app" = md5("MyPass123obcms_app")
# ============================================================================

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

generate_hash() {
    local password="$1"
    local username="$2"

    # Concatenate password + username
    local combined="${password}${username}"

    # Generate MD5 hash
    local hash
    if command -v md5sum &> /dev/null; then
        hash=$(echo -n "$combined" | md5sum | cut -d' ' -f1)
    elif command -v md5 &> /dev/null; then
        hash=$(echo -n "$combined" | md5 -r | cut -d' ' -f1)
    else
        echo "ERROR: Neither md5sum nor md5 command found"
        exit 1
    fi

    # Prefix with md5
    echo "md5${hash}"
}

interactive_mode() {
    echo ""
    echo "=========================================================================="
    echo " PgBouncer Password Hash Generator"
    echo "=========================================================================="
    echo ""
    echo "This script will generate MD5 hashes for PgBouncer userlist.txt"
    echo ""

    # Array to store generated entries
    declare -a userlist_entries

    # Generate hashes for each user
    local users=("postgres" "obcms_app" "replicator" "monitoring" "pgbouncer")

    for username in "${users[@]}"; do
        echo ""
        log_info "Generating hash for user: ${username}"
        echo -n "Enter password for ${username}: "
        read -s password
        echo ""

        if [ -z "$password" ]; then
            log_warning "Empty password, skipping ${username}"
            continue
        fi

        local hash=$(generate_hash "$password" "$username")

        # Store entry
        userlist_entries+=("\"${username}\" \"${hash}\"")

        log_success "Hash generated for ${username}"
    done

    # Display results
    echo ""
    echo "=========================================================================="
    echo " Generated PgBouncer Userlist Entries"
    echo "=========================================================================="
    echo ""
    echo "Add these entries to config/pgbouncer/userlist.txt:"
    echo ""

    for entry in "${userlist_entries[@]}"; do
        echo "$entry"
    done

    echo ""
    echo "=========================================================================="
    echo ""

    # Ask if user wants to save
    echo -n "Save to file? (y/N): "
    read -r save_choice

    if [[ "$save_choice" =~ ^[Yy]$ ]]; then
        local output_file="/tmp/pgbouncer_userlist_$(date +%Y%m%d_%H%M%S).txt"

        {
            echo ";; Generated PgBouncer Userlist - $(date)"
            echo ";; SECURITY WARNING: Keep this file secure!"
            echo ""
            for entry in "${userlist_entries[@]}"; do
                echo "$entry"
            done
        } > "$output_file"

        log_success "Saved to: $output_file"
        echo ""
        echo "Copy this file to: config/pgbouncer/userlist.txt"
        echo "IMPORTANT: Delete this temp file after copying!"
    fi
}

batch_mode() {
    local passwords_file="$1"

    if [ ! -f "$passwords_file" ]; then
        echo "ERROR: Passwords file not found: $passwords_file"
        exit 1
    fi

    log_info "Reading passwords from: $passwords_file"
    echo ""

    # Read passwords file
    # Expected format: username:password
    while IFS=: read -r username password; do
        # Skip comments and empty lines
        [[ "$username" =~ ^#.*$ ]] && continue
        [[ -z "$username" ]] && continue

        local hash=$(generate_hash "$password" "$username")
        echo "\"${username}\" \"${hash}\""
    done < "$passwords_file"
}

example_mode() {
    echo ""
    echo "=========================================================================="
    echo " Example: Generating Hash for 'obcms_app' user"
    echo "=========================================================================="
    echo ""

    local example_password="SecurePass123"
    local example_username="obcms_app"

    echo "Username: ${example_username}"
    echo "Password: ${example_password}"
    echo ""

    local hash=$(generate_hash "$example_password" "$example_username")

    echo "Step 1: Concatenate password + username"
    echo "  Result: ${example_password}${example_username}"
    echo ""

    echo "Step 2: Calculate MD5 hash"
    echo "  Command: echo -n '${example_password}${example_username}' | md5sum"
    echo ""

    echo "Step 3: Add 'md5' prefix"
    echo "  Final hash: ${hash}"
    echo ""

    echo "Userlist entry:"
    echo "  \"${example_username}\" \"${hash}\""
    echo ""
    echo "=========================================================================="
    echo ""
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Generate MD5 password hashes for PgBouncer userlist.txt

OPTIONS:
    -i, --interactive       Interactive mode (prompt for each user)
    -f, --file FILE        Batch mode (read from file)
    -e, --example          Show example hash generation
    -h, --help             Display this help message

EXAMPLES:
    # Interactive mode (recommended)
    $0 -i

    # Batch mode from file
    $0 -f passwords.txt

    # Show example
    $0 -e

FILE FORMAT (for batch mode):
    username:password
    obcms_app:SecurePass123
    monitoring:MonitorPass456
    # Comments are supported

SECURITY NOTES:
    - Never commit passwords.txt to version control
    - Store passwords securely (use password manager)
    - Delete temporary files after use
    - Use strong passwords (minimum 16 characters)
    - Include uppercase, lowercase, numbers, and symbols

EOF
}

main() {
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        usage
        exit 0
    fi

    case "$1" in
        -i|--interactive)
            interactive_mode
            ;;
        -f|--file)
            if [ -z "${2:-}" ]; then
                echo "ERROR: File path required for -f option"
                usage
                exit 1
            fi
            batch_mode "$2"
            ;;
        -e|--example)
            example_mode
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
