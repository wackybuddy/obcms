#!/bin/bash
#
# BMMS Removal Script
# Removes all BMMS (Bangsamoro Ministerial Management System) components from OBCMS
#
# Usage: ./scripts/remove_bmms.sh
#
# IMPORTANT: Run this from the project root directory
# IMPORTANT: Disable auto-formatters before running
# IMPORTANT: Review BMMS_REMOVAL_PLAN.md before executing
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}================================================${NC}"
echo -e "${YELLOW}BMMS Removal Script${NC}"
echo -e "${YELLOW}================================================${NC}"
echo ""

# Confirm execution
read -p "Have you read BMMS_REMOVAL_PLAN.md and created a backup? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Aborted. Please review BMMS_REMOVAL_PLAN.md first.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Starting BMMS removal...${NC}"
echo ""

# Phase 1: Backup database
echo -e "${YELLOW}[Phase 1] Creating database backup...${NC}"
if [ -f "src/db.sqlite3" ]; then
    backup_name="src/db.sqlite3.backup.bmms_removal_$(date +%Y%m%d_%H%M%S)"
    cp src/db.sqlite3 "$backup_name"
    echo -e "${GREEN}✓ Database backed up to: $backup_name${NC}"
else
    echo -e "${YELLOW}⚠ No database file found (this is OK for fresh installs)${NC}"
fi

# Phase 2: Delete BMMS app directories
echo ""
echo -e "${YELLOW}[Phase 2] Removing BMMS app directories...${NC}"

apps_to_remove=(
    "src/organizations"
    "src/planning"
    "src/budget_preparation"
    "src/budget_execution"
    "src/ocm"
)

for app in "${apps_to_remove[@]}"; do
    if [ -d "$app" ]; then
        rm -rf "$app"
        echo -e "${GREEN}✓ Removed: $app${NC}"
    else
        echo -e "${YELLOW}⚠ Not found: $app (already removed?)${NC}"
    fi
done

# Phase 3: Remove BMMS config file
echo ""
echo -e "${YELLOW}[Phase 3] Removing BMMS config file...${NC}"
if [ -f "src/obc_management/settings/bmms_config.py" ]; then
    rm src/obc_management/settings/bmms_config.py
    echo -e "${GREEN}✓ Removed: bmms_config.py${NC}"
else
    echo -e "${YELLOW}⚠ bmms_config.py not found (already removed?)${NC}"
fi

# Phase 4: Remove BMMS documentation
echo ""
echo -e "${YELLOW}[Phase 4] Removing BMMS documentation...${NC}"
if [ -d "docs/plans/bmms" ]; then
    file_count=$(find docs/plans/bmms -type f | wc -l | tr -d ' ')
    rm -rf docs/plans/bmms
    echo -e "${GREEN}✓ Removed: docs/plans/bmms/ ($file_count files)${NC}"
else
    echo -e "${YELLOW}⚠ docs/plans/bmms/ not found (already removed?)${NC}"
fi

# Phase 5: Remove organization infrastructure from common app
echo ""
echo -e "${YELLOW}[Phase 5] Removing organization infrastructure...${NC}"

org_files=(
    "src/common/middleware/organization_context.py"
    "src/common/mixins/organization_mixins.py"
    "src/common/mixins/ocm_mixins.py"
    "src/common/decorators/organization.py"
    "src/common/permissions/organization.py"
)

for file in "${org_files[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}✓ Removed: $file${NC}"
    else
        echo -e "${YELLOW}⚠ Not found: $file${NC}"
    fi
done

# Phase 6: Remove organization-related tests
echo ""
echo -e "${YELLOW}[Phase 6] Removing organization-related tests...${NC}"

test_files=(
    "src/common/tests/test_organization_permissions.py"
    "src/common/tests/test_organization_mixins.py"
    "src/common/tests/test_organization_decorators.py"
    "src/common/tests/test_organization_context.py"
    "src/tests/test_organization_scoping.py"
    "src/tests/test_view_organization_context.py"
    "src/tests/test_middleware.py"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}✓ Removed: $file${NC}"
    else
        echo -e "${YELLOW}⚠ Not found: $file${NC}"
    fi
done

# Phase 7: Check for remaining references
echo ""
echo -e "${YELLOW}[Phase 7] Checking for remaining BMMS references...${NC}"
echo ""

echo "Searching for 'from organizations' imports..."
org_imports=$(grep -r "from organizations" src --include="*.py" 2>/dev/null | grep -v "__pycache__" | grep -v "migrations" || true)
if [ -n "$org_imports" ]; then
    echo -e "${YELLOW}⚠ Found organization imports that need manual removal:${NC}"
    echo "$org_imports"
else
    echo -e "${GREEN}✓ No organization imports found${NC}"
fi

echo ""
echo "Searching for 'from planning' imports..."
planning_imports=$(grep -r "from planning" src --include="*.py" 2>/dev/null | grep -v "__pycache__" | grep -v "migrations" || true)
if [ -n "$planning_imports" ]; then
    echo -e "${YELLOW}⚠ Found planning imports that need manual removal:${NC}"
    echo "$planning_imports"
else
    echo -e "${GREEN}✓ No planning imports found${NC}"
fi

echo ""
echo "Searching for 'from budget_' imports..."
budget_imports=$(grep -r "from budget_" src --include="*.py" 2>/dev/null | grep -v "__pycache__" | grep -v "migrations" || true)
if [ -n "$budget_imports" ]; then
    echo -e "${YELLOW}⚠ Found budget imports that need manual removal:${NC}"
    echo "$budget_imports"
else
    echo -e "${GREEN}✓ No budget imports found${NC}"
fi

echo ""
echo "Searching for 'from ocm' imports..."
ocm_imports=$(grep -r "from ocm" src --include="*.py" 2>/dev/null | grep -v "__pycache__" | grep -v "migrations" || true)
if [ -n "$ocm_imports" ]; then
    echo -e "${YELLOW}⚠ Found OCM imports that need manual removal:${NC}"
    echo "$ocm_imports"
else
    echo -e "${GREEN}✓ No OCM imports found${NC}"
fi

# Summary
echo ""
echo -e "${YELLOW}================================================${NC}"
echo -e "${GREEN}BMMS Removal Complete (Automated Phase)${NC}"
echo -e "${YELLOW}================================================${NC}"
echo ""
echo -e "${YELLOW}MANUAL STEPS REQUIRED:${NC}"
echo ""
echo "1. Update src/obc_management/settings/base.py:"
echo "   - Comment out BMMS apps in LOCAL_APPS"
echo "   - Comment out 'from obc_management.settings.bmms_config import BMMSMode'"
echo ""
echo "2. Update src/obc_management/urls.py:"
echo "   - Remove planning, budget_preparation, budget_execution, ocm URL routes"
echo ""
echo "3. Update CLAUDE.md:"
echo "   - Remove BMMS sections (see BMMS_REMOVAL_PLAN.md for line numbers)"
echo ""
echo "4. Remove organization fields from models:"
echo "   - communities/models.py"
echo "   - mana/models.py"
echo "   - coordination/models.py"
echo ""
echo "5. Fix any imports shown above (if any)"
echo ""
echo "6. Run migrations:"
echo "   cd src && python manage.py makemigrations"
echo "   cd src && python manage.py migrate"
echo ""
echo "7. Run tests:"
echo "   cd src && pytest"
echo ""
echo -e "${GREEN}See BMMS_REMOVAL_PLAN.md for detailed instructions${NC}"
echo ""
