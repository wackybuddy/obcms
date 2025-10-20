# Manual File Updates for BMMS Removal

This document provides exact code changes for files that need manual updates.

## File 1: src/obc_management/settings/base.py

### Change 1: Remove BMMS Config Import (Line 17)

**Before:**
```python
import os
from pathlib import Path
import environ

from obc_management.settings.bmms_config import BMMSMode

# Initialize environment variables
```

**After:**
```python
import os
from pathlib import Path
import environ

# BMMS config removed - OBCMS is single-tenant (OOBC only)

# Initialize environment variables
```

### Change 2: Update LOCAL_APPS (Lines 83-103)

**Before:**
```python
LOCAL_APPS = [
    "common",
    "organizations",  # Phase 1: BMMS multi-tenant foundation (44 MOAs)
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
    "services",  # Phase 3: Service catalog and applications
    "project_central",  # Integrated project management system
    "ai_assistant",  # AI assistant with vector search and semantic similarity
    "planning",  # Phase 1: Strategic planning module (BMMS)
    "budget_preparation",  # Phase 2A: Budget Preparation (Parliament Bill No. 325)
    "budget_execution",  # Phase 2B: Budget Execution (Parliament Bill No. 325 Section 78)
    "ocm",  # Phase 6: OCM aggregation layer
]
```

**After:**
```python
LOCAL_APPS = [
    "common",
    # BMMS apps removed - OBCMS is single-tenant (OOBC only)
    # See BMMS_REMOVAL_PLAN.md for details
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
    "project_central",  # Integrated project management system
    "ai_assistant",  # AI assistant with vector search and semantic similarity
]
```

---

## File 2: src/obc_management/urls.py

### Remove BMMS URL Routes (Lines 53-60)

**Before:**
```python
    path("monitoring/", include("monitoring.urls")),
    # Planning Module (Phase 1: Strategic Planning - BMMS)
    path("planning/", include("planning.urls")),
    # Budget Preparation Module (Phase 2A: Budget Preparation - Parliament Bill No. 325)
    path("budget/preparation/", include("budget_preparation.urls")),
    # Budget Execution Module (Phase 2B: Budget Execution - Parliament Bill No. 325)
    path("budget/execution/", include("budget_execution.urls")),
    # OCM Aggregation Layer (Phase 6: Office of the Chief Minister - BMMS)
    path("ocm/", include(("ocm.urls", "ocm"), namespace="ocm")),
    # =========================================================================
```

**After:**
```python
    path("monitoring/", include("monitoring.urls")),
    # BMMS URL routes removed - see BMMS_REMOVAL_PLAN.md
    # =========================================================================
```

---

## File 3: src/common/services/rbac_service.py

### Remove Organization Logic

**Search for and remove:**
- Any imports from `organizations`
- Any `organization` parameter handling
- Any organization-based filtering logic

This file will need careful review as it may have significant organization logic.

**Action:** Review the file and remove all organization-related code. The service should work with roles and permissions without organization scoping.

---

## File 4: src/communities/models.py

### Remove Organization Field

**Find and remove:**
```python
from organizations.models import Organization

# In Community model:
organization = models.ForeignKey(
    'organizations.Organization',
    on_delete=models.PROTECT,
    ...
)
```

**After removal**, run:
```bash
cd src
python manage.py makemigrations communities
```

This will create a migration to remove the `organization` field.

---

## File 5: src/mana/models.py

### Remove Organization Fields

**Find and remove organization fields from these models:**
- `Assessment`
- `Need`
- Any other model with `organization` ForeignKey

**After removal**, run:
```bash
cd src
python manage.py makemigrations mana
```

---

## File 6: src/coordination/models.py

### Remove Organization References

**Find and remove:**
- Organization imports
- Organization fields
- Organization-based filtering

**After removal**, run:
```bash
cd src
python manage.py makemigrations coordination
```

---

## File 7: src/common/__init__.py

### Remove Organization Exports

**Find and remove any exports of:**
- `OrganizationMixin`
- `OrganizationContext`
- Organization decorators
- Organization permissions

---

## File 8: src/mana/forms.py

### Remove Planning References

The grep search found planning references in this file. Review and remove any:
```python
from planning import ...
```

---

## Checklist for Manual Updates

- [ ] Updated `src/obc_management/settings/base.py` (2 changes)
- [ ] Updated `src/obc_management/urls.py` (removed 4 URL routes)
- [ ] Updated `src/common/services/rbac_service.py`
- [ ] Updated `src/communities/models.py` (removed organization field)
- [ ] Updated `src/mana/models.py` (removed organization fields)
- [ ] Updated `src/coordination/models.py` (removed organization references)
- [ ] Updated `src/common/__init__.py` (removed organization exports)
- [ ] Updated `src/mana/forms.py` (removed planning references)
- [ ] Ran `python manage.py makemigrations`
- [ ] Ran `python manage.py migrate`
- [ ] Ran tests: `pytest`
- [ ] Started server: `python manage.py runserver`

---

## Important Notes

1. **Disable Auto-Formatters**: Turn off auto-save and format-on-save before making these changes
2. **Work in Order**: Complete each file before moving to the next
3. **Test After Each Change**: Run the server after each major change to catch issues early
4. **Database Migrations**: Don't skip the makemigrations/migrate steps
5. **Keep Backups**: Your database backup is in `src/db.sqlite3.backup.bmms_removal_*`

---

**Next**: After completing all manual updates, see BMMS_REMOVAL_PLAN.md Phase 10 for verification steps.
