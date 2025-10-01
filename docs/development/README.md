# Development Tools & AI Configuration

This directory contains development guidelines and references for AI-assisted development.

## AI Configuration Files

⚠️ **IMPORTANT:** AI agent configuration files are located in the **project root**, not in this directory.

### Configuration Files (Located in Project Root)
- **[../CLAUDE.md](../../CLAUDE.md)** - Claude AI configuration and project-specific instructions
- **[../GEMINI.md](../../GEMINI.md)** - Google Gemini integration and configuration
- **[../AGENTS.md](../../AGENTS.md)** - Overview of AI agents used in development

**Why in the root?**
These files are **configuration files**, not documentation. AI coding agents (Claude Code, Gemini, etc.) look for these files in the project root to understand how to work with the project. Moving them would break AI functionality.

## AI-Assisted Development

This project leverages AI coding assistants to accelerate development while maintaining code quality and consistency.

### Claude Code
Primary AI assistant for:
- Code generation and refactoring
- Django best practices enforcement
- Documentation generation
- Test writing
- Bug fixing and debugging

**Configuration:** See [../CLAUDE.md](../../CLAUDE.md) in project root.

### Google Gemini
Used for:
- Alternative code suggestions
- Code review and analysis
- Natural language processing tasks
- Data analysis assistance

**Configuration:** See [../GEMINI.md](../../GEMINI.md) in project root.

## Development Best Practices

### Using AI Assistants Effectively

1. **Provide Context:** Always include relevant code context and requirements
2. **Review Output:** Never commit AI-generated code without review
3. **Test Thoroughly:** All AI-generated code must pass tests
4. **Follow Standards:** Ensure AI output follows project conventions

### Project-Specific AI Guidelines

- **Django Patterns:** AI assistants are configured to follow Django best practices
- **Security First:** All code reviews check for security vulnerabilities
- **Test Coverage:** AI-generated code should include test cases
- **Documentation:** All significant changes should include documentation updates

## Configuration Files Read by AI

AI assistants read these project files for context:
- **[CLAUDE.md](../../CLAUDE.md)** - Project-specific Claude instructions (ROOT)
- **[GEMINI.md](../../GEMINI.md)** - Gemini configuration (ROOT)
- **[AGENTS.md](../../AGENTS.md)** - AI agents overview (ROOT)
- `docs/` - Project documentation
- `requirements/` - Python dependencies
- `.env.example` - Environment configuration template

## Getting Started with AI Development

1. **Read Configuration:**
   - [../CLAUDE.md](../../CLAUDE.md) - Primary AI assistant setup
   - [../AGENTS.md](../../AGENTS.md) - Overview of all AI tools

2. **Set Up Environment:**
   - Configure API keys (if needed)
   - Review project-specific instructions in CLAUDE.md
   - Understand coding standards

3. **Start Coding:**
   - Use AI for boilerplate and repetitive tasks
   - Leverage AI for code review and suggestions
   - Always review and test AI-generated code

## Development Workflows

### With Claude Code
1. Describe what you want to build
2. Claude reads CLAUDE.md for project context
3. Claude generates code following project standards
4. Review, test, and refine
5. Commit with descriptive messages

### With Gemini
1. Use for alternative perspectives
2. Gemini reads GEMINI.md for configuration
3. Compare suggestions with Claude's output
4. Choose best approach

## Database Management

### Critical Issue: SQLite Database Location

- **[SQLite Database Location Issue](sqlite-database-location-issue.md)** - Comprehensive troubleshooting guide
  - **Problem**: Django ORM returns empty results despite data existing in SQLite
  - **Root Cause**: Database file location mismatch between Django config and backup files
  - **Solutions**: Automated scripts, path standardization, verification steps
  - **Prevention**: Development best practices and quick reference commands

### Quick Database Commands

#### Check Database Location
```bash
cd src
../venv/bin/python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"
```

#### Backup Database
```bash
./scripts/db_backup.sh  # Automated with verification
```

#### Restore Database
```bash
./scripts/db_restore.sh backups/db.sqlite3.backup.20250930_221241
```

#### Verify Data
```bash
cd src
../venv/bin/python manage.py shell -c "
from common.models import Region, Province, Municipality, Barangay
print(f'Regions: {Region.objects.count()}')
print(f'Provinces: {Province.objects.count()}')
print(f'Municipalities: {Municipality.objects.count()}')
print(f'Barangays: {Barangay.objects.count()}')
"
```

## Static Files Architecture

### Directory Structure

The project uses a **centralized static files approach** with all static assets in `src/static/`:

```
src/
├── static/                    # Project-wide static files (configured)
│   ├── admin/                # Admin interface customizations
│   │   ├── css/custom.css
│   │   └── js/custom.js
│   ├── common/               # Common app-specific assets
│   │   ├── css/
│   │   ├── js/
│   │   └── vendor/           # App-specific vendor libraries
│   │       └── fullcalendar/ # FullCalendar (used primarily in common)
│   ├── communities/
│   ├── coordination/
│   ├── mana/
│   └── vendor/               # Shared vendor libraries
│       ├── leaflet/          # Map library (used across apps)
│       ├── localforage/      # Offline storage
│       └── idb/              # IndexedDB wrapper
└── obc_management/
    └── static/               # Empty (placeholder only)
```

### Configuration

**Settings:** `src/obc_management/settings/base.py`
```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR.parent / "static",  # Points to src/static/
]
```

### Why This Structure?

1. ✅ **Centralized management** - All static files in one location
2. ✅ **Better for shared resources** - Vendor libraries used across multiple apps
3. ✅ **Consistent with templates** - Templates in `src/templates/`, static in `src/static/`
4. ✅ **Easier deployment** - Single source for `collectstatic`

### Vendor Library Organization

**Two vendor directories exist:**
- `src/static/common/vendor/` - FullCalendar (primarily used by common app)
- `src/static/vendor/` - Truly shared libraries (Leaflet, localforage, idb)

This minor inconsistency is intentional and doesn't cause issues.

### Common Static Files Issues

#### FullCalendar Not Loading
- **Symptom**: Calendar widget doesn't render, JavaScript not loading
- **Cause**: `STATICFILES_DIRS` pointing to wrong directory (e.g., `obc_management/static` instead of `src/static`)
- **Solution**: Ensure `STATICFILES_DIRS = [BASE_DIR.parent / "static"]` in settings
- **Verification**:
  ```bash
  cd src
  ../venv/bin/python manage.py shell -c "from django.conf import settings; print(settings.STATICFILES_DIRS)"
  ```

#### 404 on Static Files
- **During Development**: Check `STATICFILES_DIRS` points to `src/static/`
- **In Production**: Run `./manage.py collectstatic` to gather files to `STATIC_ROOT`
- **Restart Required**: Changes to `settings.py` require server restart

## Common Development Issues

### Empty Dropdowns in Forms
- **Symptom**: Location dropdowns show "Select region..." but no options
- **Cause**: Database location mismatch or missing geographic data
- **Solution**: See [SQLite Database Location Issue](sqlite-database-location-issue.md)

### Migration Conflicts
- **Never delete the database** - contains valuable development data
- Use `./manage.py migrate --fake` for conflicts
- Restore from backup: `./scripts/db_restore.sh`

## Scripts Reference

Located in `scripts/` directory:

- **db_backup.sh** - Create timestamped database backup with verification
- **db_restore.sh** - Restore database from backup (with confirmation)
- **bootstrap_venv.sh** - Set up Python virtual environment

## Related Documentation
- [Development Environment Setup](../env/development.md)
- [Improvement Plan Template](../improvements/improvement_plan_template.md)
- [UI Design System](../ui/ui-design-system.md)
- [Testing Guidelines](../testing/README.md)

---

**Note:** This directory is for development guidelines and documentation. AI configuration files remain in the project root for proper agent functionality.
