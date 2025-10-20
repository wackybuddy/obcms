# START HERE: OBCMS Cleanup Guide

**Question**: Should you remove BMMS components from OBCMS?

**Answer**: Yes, but **keep the multi-org infrastructure**. OOBC needs it!

## The Key Insight

**OBCMS is not single-tenant!**

OOBC (Office for Other Bangsamoro Communities) doesn't work alone. It:
- Partners with Ministry of Health on health programs
- Collaborates with Ministry of Education on education initiatives
- Coordinates with Ministry of Social Services on livelihood projects
- Works with NGOs and local government units

Each partner organization needs:
- Access to OBCMS
- See only THEIR data (not other orgs' data)
- Role-based permissions
- Ability to plan and budget for their OOBC programs

## What You Should Do

### ✅ Recommended: Minimal Cleanup

**Remove**: BMMS-specific components only
- OCM app (Office of Chief Minister aggregation)
- BMMS documentation (109 files)
- BMMS-centric comments

**Keep**: Essential OBCMS features
- Organizations app (multi-org support)
- Planning module (strategic planning)
- Budget modules (financial management)
- RBAC system (role permissions)
- Data isolation (security)

**Time**: 30 minutes
**Risk**: Low
**File**: [MINIMAL_CLEANUP_PLAN.md](MINIMAL_CLEANUP_PLAN.md)

### ⚠️ Not Recommended: Full Removal

**Removes**: Everything BMMS-related
- Organizations, planning, budgeting, RBAC
- Multi-org infrastructure
- Data isolation

**Problems**:
- Partner ministries can't access OBCMS
- No strategic planning capability
- No budget management
- No data isolation (security risk)
- Breaks OOBC operations

**Time**: 1-2 hours
**Risk**: High

## Quick Start

```bash
# Step 1: Read the comparison
cat docs/obcmsonly/COMPARISON_GUIDE.md

# Step 2: Execute minimal cleanup
cat docs/obcmsonly/MINIMAL_CLEANUP_PLAN.md

# Step 3: Remove OCM and BMMS docs
rm -rf src/ocm/
rm -rf docs/plans/bmms/

# Step 4: Update settings.py and urls.py
# (See MINIMAL_CLEANUP_PLAN.md for exact changes)

# Step 5: Test
cd src && python manage.py runserver
```

## File Guide

| File | When to Read |
|------|--------------|
| **START_HERE.md** | ⭐ You are here - overview |
| **COMPARISON_GUIDE.md** | To understand the two approaches |
| **MINIMAL_CLEANUP_PLAN.md** | ✅ To execute the recommended cleanup |

## Real Example

**Before** (OBCMS with BMMS components):
```
Apps: organizations, planning, budget_*, ocm ← BMMS aggregation
Docs: docs/plans/bmms/ (109 files) ← BMMS planning
Comments: "BMMS multi-tenant foundation (44 MOAs)" ← BMMS-centric
```

**After** (Clean OBCMS):
```
Apps: organizations, planning, budget_* ← Keep for OOBC
No OCM: ← Removed (BMMS-specific)
No BMMS docs: ← Removed (not needed)
Comments: "Multi-organizational support (OOBC + partners)" ← OBCMS-centric
```

## Why This Matters

### Real Scenario: Health Assessment

**With multi-org (correct)**:
1. MOH health coordinator logs in
2. Sees only MOH health assessments
3. Can create strategic health plan for OBC communities
4. Tracks MOH budget for OOBC health programs
5. Coordinates with OOBC on interventions

**Without multi-org (broken)**:
1. No MOH access (they're not in the system)
2. No data isolation (everyone sees everything)
3. No planning capability
4. No budget tracking
5. No coordination possible

## Decision Tree

```
Do partner ministries access OBCMS?
├─ YES → Use MINIMAL CLEANUP
│         Keep: organizations, planning, budgeting
│         Remove: OCM, BMMS docs
│
└─ NO → Consider full removal
          (But verify this is really your situation)
```

## Next Steps

1. **Read**: [COMPARISON_GUIDE.md](COMPARISON_GUIDE.md) (10 minutes)
2. **Execute**: [MINIMAL_CLEANUP_PLAN.md](MINIMAL_CLEANUP_PLAN.md) (30 minutes)
3. **Test**: Run server and verify functionality

## Summary

- **BMMS**: Separate system for 44 BARMM ministries ✅ Separated
- **OBCMS**: Multi-org system for OOBC operations ✅ Keep multi-org support
- **Cleanup**: Remove OCM + BMMS docs only ✅ Minimal and safe

**Recommended Action**: Follow [MINIMAL_CLEANUP_PLAN.md](MINIMAL_CLEANUP_PLAN.md)

---

**Questions?** Read [COMPARISON_GUIDE.md](COMPARISON_GUIDE.md) for detailed analysis.
