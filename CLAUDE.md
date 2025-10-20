# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL RULE: No Temporary Fixes

**NEVER use temporary fixes, workarounds, or shortcuts when debugging issues.**

When you encounter an error:
- ❌ DO NOT remove decorators, comment out code, or bypass validation
- ❌ DO NOT use placeholder data or mock implementations
- ❌ DO NOT skip proper migrations or database changes
- ✅ ALWAYS identify and fix the root cause
- ✅ ALWAYS implement the proper, complete solution
- ✅ ALWAYS create missing data, migrations, or configurations

**Examples:**

**WRONG (Temporary Fix):**
```python
# Error: Permission 'oobc_management.manage_users' doesn't exist
@login_required
# @require_permission('oobc_management.manage_users')  # Commented out temporarily
def manage_users(request):
    pass
```

**RIGHT (Proper Fix):**
```python
# 1. Create migration to add the missing permission
# 2. Keep decorator in place
@login_required
@require_permission('oobc_management.manage_users')
def manage_users(request):
    pass
```

This rule is MANDATORY and must be followed at all times.

## CRITICAL RULE: No Assumptions - Research When Unsure

**NEVER make assumptions when you are uncertain. ALWAYS research and verify facts.**

When you encounter uncertainty:
- ❌ DO NOT assume how code works without checking
- ❌ DO NOT guess at solutions based on "likely" behavior
- ❌ DO NOT assume issues are caused by common problems (e.g., "probably cache")
- ✅ ALWAYS use parallel agents/tasks to research thoroughly
- ✅ ALWAYS verify facts by reading actual code, documentation, or searching online
- ✅ ALWAYS state explicitly when you don't know something and need to investigate

**Examples:**

**WRONG (Making Assumptions):**
```
"The issue is probably a cache problem. Users need to clear their browser cookies."
# Made assumption without verifying the actual root cause
```

**RIGHT (Research-Based):**
```
"Let me use parallel agents to investigate:
1. Agent 1: Check RBAC permission logic in rbac_service.py
2. Agent 2: Verify view decorators in mana/views.py
3. Agent 3: Examine template permission checks
[After investigation] The issue is X in file Y at line Z."
```

**When to Research Online:**
- Django/Python best practices you're unsure about
- Library-specific behavior (HTMX, Tailwind, etc.)
- Error messages you haven't seen before
- Performance optimization techniques
- Security considerations

**How to Research:**
- Use WebSearch for current documentation, Stack Overflow solutions
- Use WebFetch for official documentation pages
- Use parallel agents for multi-faceted investigations
- Cross-reference multiple sources before concluding

This rule is MANDATORY and must be followed at all times.

## Time Estimates Policy

**NEVER provide time estimates in hours, days, weeks, or months for implementation tasks.**

With powerful AI coding agents, a year's worth of traditional development work can be completed in a single day. Time estimates create false constraints and are obsolete in AI-assisted development.

**This applies to:**

- ❌ Conversational responses: "This will take 8 hours"
- ❌ Documentation files: "Week 1-2: Implement feature"
- ❌ Phase headers: "Phase 1 (Week 1-2)" or "Phase 2 (Days 3-5)"
- ❌ Implementation plans: Any timeline labels, week ranges, or date estimates
- ❌ Roadmaps: "Q1 2024", "Month 1", "Sprint 1-2"

**Instead, focus on:**

- **Priority**: CRITICAL, HIGH, MEDIUM, or LOW (all caps in phase headers)
- **Complexity**: Simple, Moderate, or Complex
- **Dependencies**: What must be done before this task (e.g., "Requires dashboard metrics view")
- **Prerequisites**: What needs to exist first (e.g., "Model must exist", "API endpoint required")

**Critical:** This policy applies to ALL documentation files under `docs/`, including implementation plans, feature specifications, and phased rollout plans. Never use week ranges, day counts, hour estimates, or any time-based labels.

## Development Environment

### Setup Requirements
- **Virtual Environment**: Python 3.12 `venv/`
- **Working Directory**: All Django commands must be run from `src/` directory
- **Database**: SQLite for development (NEVER delete db.sqlite3)

**See:** [Development Setup Guide](docs/development/README.md) for complete instructions

### Key Tools
- Django management commands (migrations, runserver, tests)
- Code quality: Black, isort, flake8
- Testing: pytest with coverage
- Dependencies: requirements/development.txt, requirements/base.txt

**See:** [Development Guide](docs/development/README.md#common-commands) for command reference

## Architecture Overview

### Django Project Structure
- **Main Project**: `src/obc_management/` - Django settings and configuration
- **Core Apps**: common, communities, mana, coordination, policies
- **Architecture**: Multi-organizational system supporting OOBC and partner ministries with data isolation

### Technical Stack
- Django + DRF (REST APIs)
- SQLite (dev) / PostgreSQL (production)
- Celery + Redis (background tasks)
- HTMX + Tailwind CSS (frontend)
- Leaflet.js (maps), FullCalendar (scheduling)

**See:** [Architecture Documentation](docs/product/) for detailed specifications

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

### Use Cases
- Ministry of Health: Health assessments in OBC communities
- Ministry of Education: Education programs and school planning
- Ministry of Social Services: Livelihood and social development programs
- OOBC: Cross-cutting coordination and strategic oversight

## Domain Context

### OOBC Mission
This system supports the Office for Other Bangsamoro Communities (OOBC) serving Bangsamoro communities outside BARMM (Bangsamoro Autonomous Region in Muslim Mindanao).

### Geographic Scope
- Primary focus: Regions IX, X, XI, XII (Mindanao)
- Administrative hierarchy: Region > Province > Municipality/City > Barangay
- Timezone: Asia/Manila

**See:** [BARMM Terminology & Architecture](docs/product/BARMM_TERMINOLOGY_AND_ARCHITECTURE_FINDINGS.md)

## Development Guidelines

### Database Operations
**⚠️ CRITICAL: NEVER delete db.sqlite3** - Contains valuable development data. Always apply migrations to existing database.

**See:** [Database Migration Guide](docs/deployment/POSTGRESQL_MIGRATION_SUMMARY.md)

### Model Development
- Use timezone-aware datetime fields
- Follow Django naming conventions
- Implement proper `__str__` methods
- Use organization-scoped queries for multi-tenancy

**See:** [Architecture Documentation](docs/product/) for model specifications

### API Development
- All APIs require authentication by default
- Use DRF filtering, searching, ordering
- Implement proper serializers with validation
- Follow REST principles

**See:** [API Documentation](docs/development/README.md#api-development)

### Frontend Development
- Templates in `src/templates/` with Django template language
- Static files in `src/static/` (centralized approach)
- Tailwind CSS for responsive styling
- WCAG 2.1 AA accessibility compliance

**See:** [Static Files Architecture](docs/development/README.md#static-files-architecture)

## UI/UX Standards

**CRITICAL**: All UI components MUST follow official OBCMS UI standards.

**📚 PRIMARY REFERENCE:** [OBCMS UI Standards Master Guide](docs/ui/OBCMS_UI_STANDARDS_MASTER.md) ⭐ **OFFICIAL**

### Component Guidelines
- **Stat Cards**: 3D milk white design with semantic colors
- **Forms**: Standardized dropdowns, inputs, buttons
- **Tables**: Blue-to-teal gradient headers
- **Accessibility**: WCAG 2.1 AA compliance (touch targets 48px minimum)

**When creating or modifying UI:**
1. ✅ Always check UI Standards guide first
2. ✅ Copy from existing reference templates
3. ✅ Follow semantic color guidelines
4. ✅ Test on mobile, tablet, desktop
5. ✅ Verify accessibility compliance

**See:**
- [OBCMS UI Standards Master](docs/ui/OBCMS_UI_STANDARDS_MASTER.md)
- [Stat Card Template](docs/improvements/UI/STATCARD_TEMPLATE.md)
- [Form Components](src/templates/components/)

## HTMX & Instant UI

**Priority: Always implement instant UI responses** - no full page reloads.

### Requirements
- Consistent element targeting with data attributes
- Optimistic updates with smooth animations
- Loading indicators for all operations
- Out-of-band swaps for multi-region updates

**See:** [Instant UI Improvements Plan](docs/improvements/instant_ui_improvements_plan.md)

## Documentation Organization

**CRITICAL: All documentation files MUST be placed under `docs/` directory.**

### Directory Structure
- `docs/deployment/` - Deployment guides, production setup
- `docs/development/` - Development guidelines
- `docs/testing/` - Testing guides, verification reports
- `docs/improvements/` - Implementation tracking
- `docs/ui/` - UI/UX documentation

### Documentation Rules
1. ❌ NEVER create documentation in project root
2. ✅ Choose appropriate category under `docs/`
3. ✅ Update `docs/README.md` index
4. ✅ Use relative links within documentation

**Configuration files in ROOT:** CLAUDE.md, AGENTS.md, GEMINI.md, README.md, .env.example

**See:** [Documentation Organization Guide](docs/DOCUMENTATION_ORGANIZATION.md)

## Production Deployment

### Pre-Deployment Requirements

**⚠️ CRITICAL: Review ALL deployment documentation before deploying**

### Essential Reading (in order)
1. **[PostgreSQL Migration Summary](docs/deployment/POSTGRESQL_MIGRATION_SUMMARY.md)** ⭐ START HERE
2. **[PostgreSQL Migration Review](docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md)** ⭐ TECHNICAL DETAILS
3. **[Staging Environment Guide](docs/env/staging-complete.md)** - 12-step procedure
4. **[Case-Sensitive Query Audit](docs/deployment/CASE_SENSITIVE_QUERY_AUDIT.md)** - 100% compatible
5. **[Geographic Data Implementation](docs/improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md)** - No PostGIS needed

### Key Decisions
- **Database**: PostgreSQL (NO PostGIS extension required)
- **Geographic Data**: JSONField with GeoJSON (not PostGIS)
- **Text Search**: Case-insensitive lookups verified (100% compatible)
- **Deployment**: Staging → Production (never direct to production)

### Platform Options
- **Option A**: Coolify (Recommended) - See [Coolify Deployment Checklist](docs/deployment/deployment-coolify.md)
- **Option B**: Docker Compose - See [Docker Guide](docs/deployment/docker-guide.md)

### Critical Reminders
- ✅ Test in staging first
- ✅ Never delete production database
- ✅ Generate new SECRET_KEY for production
- ✅ Run `python manage.py check --deploy`
- ✅ Verify all environment variables

**See:** [Full Deployment Documentation Index](docs/deployment/)

## Testing Requirements

### Test Coverage
- Unit tests: 99.2% passing (254/256 tests)
- Performance tests: 83% passing (10/12 tests)
- Accessibility: WCAG 2.1 AA compliance required
- Data isolation: 100% pass rate required

### Testing Tools
- pytest + coverage
- Selenium/Playwright (browser testing)
- Locust (load testing)
- Axe DevTools (accessibility)

**See:**
- [Performance Test Results](docs/testing/PERFORMANCE_TEST_RESULTS.md)

## Security & Compliance

### Security Standards
- Organization-based data isolation (each organization has isolated data access)
- Role-based permissions enforced
- Audit logging for sensitive operations
- Data Privacy Act 2012 compliance (beneficiary data)

### Production Security
- HSTS, SSL redirect, secure cookies
- Connection pooling (CONN_MAX_AGE = 600)
- CSP headers configured
- JWT authentication (1-hour access, 7-day refresh)

**See:** [Production Settings](src/obc_management/settings/production.py)

## Reference Documentation

### Complete Documentation Index
- [docs/README.md](docs/README.md) - Full documentation index

### Quick Links
- [UI Standards](docs/ui/OBCMS_UI_STANDARDS_MASTER.md)
- [Deployment Guides](docs/deployment/)
- [Development Guidelines](docs/development/README.md)
- [Testing Documentation](docs/testing/)

### Configuration Files
- [AGENTS.md](AGENTS.md) - Agent-specific guidelines
- [GEMINI.md](GEMINI.md) - Gemini-specific guidelines
- [README.md](README.md) - Project overview

---

**Remember:** OBCMS is a multi-organizational system focused on OOBC operations with partner ministry support
