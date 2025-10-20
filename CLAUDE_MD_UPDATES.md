# CLAUDE.md Updates for BMMS Removal

This file contains the exact changes needed for CLAUDE.md after BMMS removal.

## Section 1: Remove BMMS Critical Definition (Lines 107-123)

**DELETE THIS ENTIRE SECTION:**

```markdown
## BMMS Critical Definition

**BMMS = Bangsamoro Ministerial Management System**

**NOT "Bangsamoro Management & Monitoring System"** - This is incorrect!

BMMS is the strategic evolution of OBCMS from a single-organization platform (OOBC) to a comprehensive multi-tenant management system serving all 44 BARMM Ministries, Offices, and Agencies (MOAs).

**Key Points:**
- BMMS serves **MINISTRIES** (hence "Ministerial")
- 44 MOAs (Ministries, Offices, and Agencies)
- Multi-tenant architecture with organization-based data isolation
- Office of the Chief Minister (OCM) - NOT "CMO" - provides centralized oversight

**Always use:** "Bangsamoro Ministerial Management System"
**Never use:** "Bangsamoro Management & Monitoring System"
```

## Section 2: Update Architecture Overview

**Line 129-132: UPDATE THIS:**

From:
```markdown
### Django Project Structure
- **Main Project**: `src/obc_management/` - Django settings and configuration
- **Core Apps**: common, communities, mana, coordination, policies
- **Multi-tenant**: Organization-based data isolation (MOA A cannot see MOA B's data)
```

To:
```markdown
### Django Project Structure
- **Main Project**: `src/obc_management/` - Django settings and configuration
- **Core Apps**: common, communities, mana, coordination, policies
- **Architecture**: Single-tenant system serving OOBC (Office for Other Bangsamoro Communities)
```

## Section 3: Remove BMMS Reference in Model Development (Line 182)

**DELETE THIS LINE:**
```markdown
**See:** [BMMS Transition Plan](docs/plans/bmms/TRANSITION_PLAN.md) for model specifications
```

**REPLACE WITH:**
```markdown
**See:** [Development Guide](docs/development/README.md) for model specifications
```

## Section 4: Update Documentation Organization (Line 246)

**DELETE THIS LINE:**
```markdown
- `docs/plans/bmms/` - BMMS planning documents
```

## Section 5: Remove Entire BMMS Implementation Section (Lines 290-313)

**DELETE THIS ENTIRE SECTION:**

```markdown
## BMMS Implementation

**BMMS Status:** ✅ Planning Complete - Ready for Phase 1

### Phase Order
1. **Phase 1**: Foundation (Organizations App) - CRITICAL
2. **Phase 2**: Planning Module - HIGH
3. **Phase 3**: Budgeting Module (Parliament Bill No. 325) - CRITICAL
4. **Phase 4**: Coordination Enhancement - MEDIUM
5. **Phase 5**: Module Migration (MANA/M&E/Policies) - MEDIUM
6. **Phase 6**: OCM Aggregation - HIGH
7. **Phase 7**: Pilot MOA Onboarding (3 MOAs) - HIGH
8. **Phase 8**: Full Rollout (44 MOAs) - MEDIUM

**Additional Phases:**
- **BEN-I**: Individual Beneficiary Database
- **BEN-O**: Organizational Beneficiary Database
- **URL**: URL Refactoring
- **TEST**: Continuous Testing Strategy

**See:**
- [BMMS Planning Overview](docs/plans/bmms/README.md)
- [BMMS Transition Plan](docs/plans/bmms/TRANSITION_PLAN.md) - Complete implementation guide
- [Task Breakdowns](docs/plans/bmms/tasks/) - Detailed execution tasks
```

## Section 6: Remove BMMS Security Note (Lines 337-340)

**DELETE OR UPDATE THIS:**

From:
```markdown
### Security Standards
- Organization-based data isolation (MOA A cannot see MOA B)
- OCM read-only aggregated access
- Audit logging for sensitive operations
- Data Privacy Act 2012 compliance (beneficiary data)
```

To:
```markdown
### Security Standards
- OOBC-focused data security and access control
- Audit logging for sensitive operations
- Data Privacy Act 2012 compliance (beneficiary data)
- Role-based access control (RBAC) for all modules
```

## Section 7: Update Reference Documentation Quick Links (Line 355)

**DELETE THIS LINE:**
```markdown
- [BMMS Planning](docs/plans/bmms/README.md)
```

## Section 8: Remove Bottom Reminder (Lines 368-369)

**DELETE THESE LINES:**
```markdown
**Remember:** BMMS = Bangsamoro **Ministerial** Management System (serving **Ministries**)
**Remember:** OCM = **Office** of the Chief Minister (NOT "CMO")
```

**REPLACE WITH:**
```markdown
**Remember:** OBCMS focuses exclusively on OOBC (Office for Other Bangsamoro Communities)
```

## Summary of Changes

**Sections Removed**: 7
**Lines Removed**: ~50
**Sections Updated**: 2

**Result**: CLAUDE.md now reflects OBCMS as a single-tenant system focused on OOBC operations only.

---

**To Apply**: Manually edit CLAUDE.md and remove/update the sections listed above.
