# BMMS Removal Plan

**Status**: Ready for execution
**Created**: 2025-10-20
**Reason**: BMMS has been fully separated into its own system. OBCMS should remain single-tenant (OOBC only).

## Overview

This document outlines the complete removal of all BMMS (Bangsamoro Ministerial Management System) components from OBCMS.

## Pre-Execution Checklist

- [ ] Database backup created: `src/db.sqlite3.backup.pre_bmms_removal_*`
- [ ] Git commit current state
- [ ] Disable auto-formatters/linters temporarily
- [ ] Review this entire document before proceeding

## Phase 1: Disable Apps in Settings

**File**: `src/obc_management/settings/base.py`

### Remove BMMSConfig Import (Line 17)
```python
# REMOVE THIS LINE:
from obc_management.settings.bmms_config import BMMSMode

# REPLACE WITH:
# BMMS config removed - OBCMS is single-tenant (OOBC only)
```

### Update LOCAL_APPS (Lines 83-103)
```python
LOCAL_APPS = [
    "common",
    # BMMS apps removed - OBCMS is single-tenant (OOBC only)
    # "organizations",  # REMOVED
    # "planning",  # REMOVED
    # "budget_preparation",  # REMOVED
    # "budget_execution",  # REMOVED
    # "ocm",  # REMOVED
    "communities",
    "municipal_profiles",
    "monitoring",
    "mana",
    "coordination",
    "recommendations",
    "recommendations.documents",
    "recommendations.policies",
    "recommendations.policy_tracking",
    "data_imports",
    "services",
    "project_central",
    "ai_assistant",
]
```

## Phase 2: Remove URL Routes

**File**: `src/obc_management/urls.py`

Remove these lines:
```python
# Line 53-54: Remove planning URLs
# path("planning/", include("planning.urls")),

# Line 55-56: Remove budget preparation URLs
# path("budget/preparation/", include("budget_preparation.urls")),

# Line 57-58: Remove budget execution URLs
# path("budget/execution/", include("budget_execution.urls")),

# Line 59-60: Remove OCM URLs
# path("ocm/", include(("ocm.urls", "ocm"), namespace="ocm")),
```

## Phase 3: Delete App Directories

Execute these commands from project root:

```bash
# Navigate to src directory
cd src

# Remove BMMS app directories
rm -rf organizations/
rm -rf planning/
rm -rf budget_preparation/
rm -rf budget_execution/
rm -rf ocm/

# Remove BMMS config file
rm obc_management/settings/bmms_config.py
```

## Phase 4: Remove Documentation

```bash
# From project root
rm -rf docs/plans/bmms/
```

**Files removed**: 109 BMMS planning documents

## Phase 5: Update CLAUDE.md

Remove the following sections from `CLAUDE.md`:

### Lines to Remove:

1. **Lines 107-123**: BMMS Critical Definition section
2. **Line 182**: Reference to BMMS Transition Plan
3. **Line 246**: `docs/plans/bmms/` directory reference
4. **Lines 290-312**: Entire "BMMS Implementation" section
5. **Lines 311-313**: BMMS planning links
6. **Line 355**: BMMS Planning link
7. **Line 368**: "Remember: BMMS" reminder

## Phase 6: Remove Organization Dependencies

### Database Schema Changes

The following models have `organization` ForeignKey fields that need removal:

1. **Communities App**: `Community.organization`
2. **MANA App**: `Assessment.organization`, `Need.organization`
3. **Coordination App**: Organization references

### Common App Cleanup

Delete these files (organization infrastructure no longer needed):

```bash
cd src/common

# Middleware
rm middleware/organization_context.py

# Mixins
rm mixins/organization_mixins.py
rm mixins/ocm_mixins.py

# Decorators
rm decorators/organization.py

# Permissions
rm permissions/organization.py
```

### Update Common Imports

Files that import organization code will need updates:
- `common/services/rbac_service.py` - Remove organization logic
- `common/__init__.py` - Remove organization exports

## Phase 7: Generate Migrations

After removing organization fields from models, generate new migrations:

```bash
cd src
python manage.py makemigrations
```

Expected migrations:
- `communities`: Remove `organization` field
- `mana`: Remove `organization` field
- `coordination`: Remove organization references

## Phase 8: Update Tests

### Tests to Remove (82+ files)

All tests in these directories:
```bash
rm -rf src/organizations/tests/
rm -rf src/planning/tests/
rm -rf src/budget_preparation/tests/
rm -rf src/budget_execution/tests/
rm -rf src/ocm/tests/
```

### Tests to Update

Files that import `organizations`:
- `src/common/tests/test_organization_*.py` - Delete these
- `src/tests/test_organization_*.py` - Delete these
- `src/tests/conftest.py` - Remove organization fixtures

## Phase 9: Remove Organization References

### Models to Update

#### communities/models.py
```python
# REMOVE:
organization = models.ForeignKey('organizations.Organization', ...)

# REMOVE from imports:
from organizations.models import Organization
```

#### mana/models.py
```python
# REMOVE organization fields from:
# - Assessment model
# - Need model
```

#### coordination/models.py
```python
# REMOVE organization references
```

### Views to Update

Search for and remove:
- `from organizations import ...`
- `OrganizationMixin` usage
- `@require_organization` decorators

### Forms to Update

Search for and remove:
- Organization field references
- Organization-based filtering

## Phase 10: Verify System

After all changes:

```bash
cd src

# Check for any remaining references
grep -r "from organizations" . --include="*.py" | grep -v "__pycache__" | grep -v "migrations"
grep -r "import organizations" . --include="*.py" | grep -v "__pycache__" | grep -v "migrations"

# Run migrations
python manage.py migrate

# Run tests
pytest

# Start server
python manage.py runserver
```

## Expected Issues & Solutions

### Issue 1: Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'organizations'`
**Solution**: Remove the import statement causing the error

### Issue 2: Migration Conflicts
**Symptom**: Migrations reference removed apps
**Solution**: Create reverse migrations to remove organization fields first

### Issue 3: Template Errors
**Symptom**: Templates reference organization context
**Solution**: Remove organization template tags and variables

### Issue 4: Test Failures
**Symptom**: Tests fail due to missing organization fixtures
**Solution**: Remove or update tests to not use organization features

## Rollback Plan

If you need to rollback:

```bash
# Restore database
cp src/db.sqlite3.backup.pre_bmms_removal_* src/db.sqlite3

# Restore from git
git checkout src/obc_management/settings/base.py
git checkout src/obc_management/urls.py
```

## Post-Removal Verification

- [ ] Server starts without errors
- [ ] No import errors in console
- [ ] Dashboard loads successfully
- [ ] MANA module works
- [ ] Communities module works
- [ ] Coordination module works
- [ ] No organization references in UI
- [ ] Tests pass (excluding removed BMMS tests)

## Summary

**Apps Removed**: 5 (organizations, planning, budget_preparation, budget_execution, ocm)
**Documentation Removed**: 109 files
**Config Files Removed**: 1 (bmms_config.py)
**Common Infrastructure Removed**: Organization middleware, mixins, decorators, permissions
**Database Fields Removed**: organization ForeignKeys from communities, mana, coordination

**Result**: OBCMS is now a clean, single-tenant system focused solely on OOBC operations.

---

**Next Steps**: Execute phases 1-10 sequentially, checking after each phase.
