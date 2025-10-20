# OBCMS Minimal Cleanup Plan

**Purpose**: Remove BMMS-specific components while preserving multi-organizational infrastructure needed for OOBC operations.

**Key Insight**: OOBC is NOT single-tenant. It coordinates with multiple ministries and organizations, so multi-tenant infrastructure is essential.

## What OBCMS Actually Needs

OBCMS supports:
- ✅ Multiple organizations accessing the system (OOBC, partner ministries, NGOs)
- ✅ Data isolation (each org sees only their data)
- ✅ Role-based access control (Executive, Manager, Staff, Field Worker)
- ✅ Strategic planning for OOBC
- ✅ Budget planning and execution for OOBC programs
- ✅ Coordination across organizations

## What to Remove (BMMS-Specific Only)

### 1. Remove OCM App
The Office of Chief Minister (OCM) aggregation layer is BMMS-specific and not needed for OOBC.

```bash
# Remove OCM app
rm -rf src/ocm/

# Remove from settings.py
# Delete line: "ocm",  # Phase 6: OCM aggregation layer

# Remove from urls.py
# Delete line: path("ocm/", include(("ocm.urls", "ocm"), namespace="ocm")),
```

### 2. Remove BMMS Documentation

```bash
# Remove BMMS planning docs (109 files)
rm -rf docs/plans/bmms/
```

### 3. Update Configuration Comments

**File**: `src/obc_management/settings/base.py`

Change comments from BMMS-centric to OBCMS-centric:

```python
# BEFORE:
"organizations",  # Phase 1: BMMS multi-tenant foundation (44 MOAs)
"planning",  # Phase 1: Strategic planning module (BMMS)
"budget_preparation",  # Phase 2A: Budget Preparation (Parliament Bill No. 325)
"budget_execution",  # Phase 2B: Budget Execution (Parliament Bill No. 325 Section 78)

# AFTER:
"organizations",  # Multi-organizational support (OOBC + partner ministries)
"planning",  # Strategic planning module for OOBC operations
"budget_preparation",  # Budget preparation for OOBC programs
"budget_execution",  # Budget execution and financial tracking
```

### 4. Update CLAUDE.md

Remove BMMS-specific sections:
- Section: "BMMS Critical Definition" (Lines 107-123)
- Section: "BMMS Implementation" (Lines 290-312)
- Section: "Remember: BMMS" reminder (Line 368)

Replace with OBCMS multi-organizational context:

```markdown
## OBCMS Multi-Organizational Architecture

OBCMS supports multiple organizations working with OOBC:
- **Primary Organization**: OOBC (Office for Other Bangsamoro Communities)
- **Partner Ministries**: Health, Education, Social Services, etc.
- **Collaborating Organizations**: NGOs, local government units

### Data Isolation
- Each organization has isolated data access
- Cross-organizational coordination supported
- Role-based permissions enforced

### Key Modules
- **Organizations**: Multi-tenant organization management
- **Planning**: Strategic planning for OOBC operations
- **Budgeting**: Budget preparation and execution for programs
- **MANA**: Multi-sectoral needs assessment (health, education, livelihood)
- **Coordination**: Cross-organizational collaboration
```

### 5. Remove BMMS Config (Optional)

The `bmms_config.py` can be simplified or removed since there's no "mode switching":

```python
# src/obc_management/settings/bmms_config.py
# Can be removed - OBCMS is always multi-organizational

# If keeping for future flexibility:
class SystemMode:
    """System operational mode"""
    MULTI_ORG = 'multi_org'  # Default: Multiple organizations
    SINGLE_ORG = 'single_org'  # Legacy: OOBC-only mode
```

## What to Keep (Essential for OOBC)

### ✅ Keep: Organizations App
**Why**: OOBC works with multiple ministries and organizations.

**Use Cases**:
- Ministry of Health collaborates on health assessments
- Ministry of Education partners on education programs
- OOBC staff manage cross-cutting programs
- Partner NGOs contribute to community development

### ✅ Keep: Planning Module
**Why**: OOBC needs strategic planning for its operations.

**Use Cases**:
- OOBC 3-5 year strategic plan
- Annual work plans aligned with BARMM priorities
- Goal tracking for OBC community development
- Budget-aligned planning

### ✅ Keep: Budget Preparation
**Why**: OOBC must prepare annual budgets for programs.

**Use Cases**:
- Program-based budgeting (health, education, livelihood)
- Alignment with strategic plans
- Financial planning for community interventions
- Budget proposal generation

### ✅ Keep: Budget Execution
**Why**: OOBC tracks budget utilization and expenditures.

**Use Cases**:
- Allotment release tracking
- Obligation monitoring
- Disbursement recording
- Financial reporting

### ✅ Keep: Organization-Based RBAC
**Why**: Different roles need different access levels.

**Roles**:
- **OOBC Executive**: Full system access
- **Program Manager**: Program-specific access
- **Field Staff**: Community-level access
- **Partner Org User**: Limited collaboration access

**Permissions**:
- Data isolation by organization
- Module-level permissions
- Action-level permissions (view, add, edit, delete)

### ✅ Keep: Data Isolation Infrastructure
**Why**: Organizations must not see each other's data.

**Components**:
- Organization middleware (sets context)
- Organization mixins (filters queries)
- Organization decorators (enforces access)
- Organization fields (foreign keys on models)

## Execution Plan

### Step 1: Remove OCM App

```bash
cd /Users/saidamenmambayao/apps/obcms

# Backup
cp src/db.sqlite3 "src/db.sqlite3.backup.ocm_removal_$(date +%Y%m%d_%H%M%S)"

# Remove OCM
rm -rf src/ocm/
```

### Step 2: Update Settings

Edit `src/obc_management/settings/base.py`:

```python
LOCAL_APPS = [
    "common",
    "organizations",  # Multi-organizational support (OOBC + partner ministries)
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
    "planning",  # Strategic planning for OOBC operations
    "budget_preparation",  # Budget preparation for OOBC programs
    "budget_execution",  # Budget execution and financial tracking
    # "ocm",  # REMOVED: BMMS-specific OCM aggregation
]
```

### Step 3: Update URLs

Edit `src/obc_management/urls.py`:

```python
# Remove this line:
# path("ocm/", include(("ocm.urls", "ocm"), namespace="ocm")),
```

### Step 4: Remove BMMS Documentation

```bash
rm -rf docs/plans/bmms/
```

### Step 5: Update CLAUDE.md

See sections above for specific changes.

### Step 6: Test

```bash
cd src

# Check for OCM references
grep -r "from ocm" . --include="*.py" | grep -v migrations | grep -v __pycache__

# Run server
python manage.py runserver

# Run tests
pytest
```

## Configuration Examples

### Example 1: OOBC Organization Setup

```python
# Create OOBC organization
oobc = Organization.objects.create(
    code='OOBC',
    name='Office for Other Bangsamoro Communities',
    org_type='office',
    enable_mana=True,
    enable_planning=True,
    enable_budgeting=True,
    enable_coordination=True
)
```

### Example 2: Partner Ministry Setup

```python
# Create Ministry of Health as partner
moh = Organization.objects.create(
    code='MOH',
    name='Ministry of Health',
    org_type='ministry',
    enable_mana=True,  # Health assessments
    enable_coordination=True,  # Collaborate with OOBC
    enable_planning=False,  # Use their own planning system
    enable_budgeting=False  # Use their own budget system
)
```

### Example 3: User Access Setup

```python
# OOBC Program Manager
oobc_manager = User.objects.create(
    username='maria.santos',
    organization=oobc,
    role='program_manager'
)
# Can access OOBC planning, budgeting, all OOBC data

# MOH Health Coordinator
moh_coordinator = User.objects.create(
    username='dr.ahmad',
    organization=moh,
    role='coordinator'
)
# Can access only MOH health assessments, coordination with OOBC
```

## Benefits of This Approach

### 1. Preserves Multi-Organizational Support
OOBC can effectively coordinate with partner ministries and organizations.

### 2. Maintains Planning & Budgeting
OOBC has tools for strategic planning and financial management.

### 3. Data Isolation
Partner organizations see only their data, ensuring privacy and security.

### 4. Role-Based Access
Flexible permission system supports different user roles.

### 5. Removes BMMS Bloat
Eliminates OCM aggregation and BMMS documentation while keeping useful features.

## Summary

**What's Removed**:
- OCM app (BMMS-specific aggregation)
- BMMS documentation (109 files)
- BMMS-centric comments and references

**What's Kept**:
- Multi-organizational infrastructure ✅
- Planning module ✅
- Budget preparation ✅
- Budget execution ✅
- Organization-based RBAC ✅
- Data isolation ✅

**Result**: Clean, focused OBCMS that supports OOBC's multi-organizational operations without BMMS overhead.

---

**Estimated Time**: 30 minutes (much simpler than full removal)
