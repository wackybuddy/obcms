# SQLite Database Location Issue - Development Guide

**Date**: 2025-10-01
**Status**: Resolved
**Severity**: High (data visibility issue)

## Problem Summary

Django ORM was returning 0 results for geographic data (regions, provinces, municipalities, barangays) even though the SQLite database file contained the data. The issue was caused by a **mismatch between the database file location** used by Django and the backup file location.

## Root Cause

### What Happened

1. **Django Configuration**: Django settings were configured to use:
   ```
   /Users/.../obcms/src/obc_management/db.sqlite3
   ```

2. **Backup Files**: Database backups were stored in:
   ```
   /Users/.../obcms/src/db.sqlite3.backup.*
   ```

3. **Restoration Error**: When restoring a backup, it was copied to:
   ```
   /Users/.../obcms/src/db.sqlite3  ❌ WRONG LOCATION
   ```

4. **Result**: Django was still reading from the empty `obc_management/db.sqlite3` file, while the restored data was in a different location.

### Symptoms

- ✅ Raw SQLite queries showed data exists (`sqlite3 db.sqlite3 "SELECT COUNT(*) FROM common_region;"` → 5 rows)
- ❌ Django ORM queries returned empty results (`Region.objects.count()` → 0)
- ❌ Form dropdowns showed "Select region..." but no options appeared
- ❌ Templates using `form.region.field.queryset` had no data to iterate

## Verification Steps

### 1. Check Django's Database Configuration

```bash
cd src
../venv/bin/python manage.py shell -c "
from django.conf import settings
print('Database PATH:', settings.DATABASES['default']['NAME'])
"
```

Expected output:
```
Database PATH: /Users/.../obcms/src/obc_management/db.sqlite3
```

### 2. Verify Database File Exists and Has Data

```bash
# Check if the Django database file exists
ls -lh /Users/.../obcms/src/obc_management/db.sqlite3

# Check data with raw SQL
sqlite3 /Users/.../obcms/src/obc_management/db.sqlite3 "SELECT COUNT(*) FROM common_region;"
```

### 3. Test Django ORM Access

```bash
../venv/bin/python manage.py shell -c "
from common.models import Region, Province, Municipality, Barangay
print('Regions:', Region.objects.count())
print('Provinces:', Province.objects.count())
print('Municipalities:', Municipality.objects.count())
print('Barangays:', Barangay.objects.count())
"
```

If counts are 0 but raw SQL shows data → **database location mismatch**

## Solution: Restoring Backups to Correct Location

### Step 1: Identify the Correct Database Path

```bash
cd src
../venv/bin/python manage.py shell -c "
from django.conf import settings
print(settings.DATABASES['default']['NAME'])
" | tee /tmp/db_path.txt

DB_PATH=$(cat /tmp/db_path.txt)
echo "Django uses: $DB_PATH"
```

### Step 2: Create Safety Backup

```bash
# Always backup before restoring
cp "$DB_PATH" "${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
```

### Step 3: Restore to Correct Location

```bash
# Replace with actual backup file path
BACKUP_FILE="/Users/.../obcms/src/db.sqlite3.backup.20250930_221241"

# Restore to Django's configured location
cp "$BACKUP_FILE" "$DB_PATH"
```

### Step 4: Verify Restoration

```bash
../venv/bin/python manage.py shell -c "
from common.models import Region
print('Regions after restore:', Region.objects.count())
for r in Region.objects.all():
    print(f'  - {r.code}: {r.name}')
"
```

## Recommended Solutions for Development

### Solution 1: Standardize Database Location (Recommended)

**Update Django settings** to use a consistent, predictable location:

```python
# settings.py or local_settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # ✅ Use project root
    }
}
```

This places the database at: `/Users/.../obcms/db.sqlite3` (project root, not in src/)

### Solution 2: Create Database Management Script

Create `scripts/db_restore.sh`:

```bash
#!/bin/bash
# Database restoration script with automatic path detection

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Get Django's configured database path
DB_PATH=$(cd "$PROJECT_ROOT/src" && ../venv/bin/python manage.py shell -c "
from django.conf import settings
print(settings.DATABASES['default']['NAME'])
" 2>/dev/null)

if [ -z "$DB_PATH" ]; then
    echo "Error: Could not determine database path"
    exit 1
fi

echo "Django database location: $DB_PATH"

# List available backups
echo ""
echo "Available backups:"
ls -lht "$PROJECT_ROOT"/src/*.backup.* 2>/dev/null || echo "No backups found in src/"
ls -lht "$PROJECT_ROOT"/src/obc_management/*.backup.* 2>/dev/null || echo "No backups in src/obc_management/"

if [ -z "$1" ]; then
    echo ""
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 src/db.sqlite3.backup.20250930_221241"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Create safety backup
SAFETY_BACKUP="${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
echo ""
echo "Creating safety backup: $SAFETY_BACKUP"
cp "$DB_PATH" "$SAFETY_BACKUP"

# Restore
echo "Restoring $BACKUP_FILE to $DB_PATH"
cp "$BACKUP_FILE" "$DB_PATH"

# Verify
echo ""
echo "Verification:"
cd "$PROJECT_ROOT/src" && ../venv/bin/python manage.py shell -c "
from common.models import Region, Province, Municipality, Barangay
print(f'✅ Regions: {Region.objects.count()}')
print(f'✅ Provinces: {Province.objects.count()}')
print(f'✅ Municipalities: {Municipality.objects.count()}')
print(f'✅ Barangays: {Barangay.objects.count()}')
"

echo ""
echo "✅ Restoration complete!"
```

Make executable:
```bash
chmod +x scripts/db_restore.sh
```

Usage:
```bash
./scripts/db_restore.sh src/db.sqlite3.backup.20250930_221241
```

### Solution 3: Create Automated Backup Script

Create `scripts/db_backup.sh`:

```bash
#!/bin/bash
# Automatic database backup with proper path detection

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Get Django's configured database path
DB_PATH=$(cd "$PROJECT_ROOT/src" && ../venv/bin/python manage.py shell -c "
from django.conf import settings
print(settings.DATABASES['default']['NAME'])
" 2>/dev/null)

if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database not found at $DB_PATH"
    exit 1
fi

# Create backup directory if needed
BACKUP_DIR="$PROJECT_ROOT/backups"
mkdir -p "$BACKUP_DIR"

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db.sqlite3.backup.$TIMESTAMP"

echo "Backing up: $DB_PATH"
echo "        to: $BACKUP_FILE"

cp "$DB_PATH" "$BACKUP_FILE"

# Verify backup
ORIGINAL_SIZE=$(wc -c < "$DB_PATH")
BACKUP_SIZE=$(wc -c < "$BACKUP_FILE")

if [ "$ORIGINAL_SIZE" -eq "$BACKUP_SIZE" ]; then
    echo "✅ Backup successful! ($BACKUP_SIZE bytes)"

    # Show backup contents summary
    sqlite3 "$BACKUP_FILE" "
        SELECT 'Users: ' || COUNT(*) FROM auth_user
        UNION ALL
        SELECT 'Regions: ' || COUNT(*) FROM common_region
        UNION ALL
        SELECT 'Provinces: ' || COUNT(*) FROM common_province
        UNION ALL
        SELECT 'Communities: ' || COUNT(*) FROM communities_obc_community;
    "
else
    echo "❌ Backup verification failed!"
    exit 1
fi

# Clean old backups (keep last 10)
echo ""
echo "Cleaning old backups (keeping last 10)..."
ls -t "$BACKUP_DIR"/db.sqlite3.backup.* | tail -n +11 | xargs rm -f 2>/dev/null || true

echo ""
echo "Recent backups:"
ls -lht "$BACKUP_DIR"/db.sqlite3.backup.* | head -n 5
```

Make executable:
```bash
chmod +x scripts/db_backup.sh
```

### Solution 4: Environment Variable Configuration

Add to `.env`:

```bash
# Database Configuration
DATABASE_PATH=/Users/.../obcms/src/obc_management/db.sqlite3
```

Update settings:

```python
# settings.py
import os
from pathlib import Path

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DATABASE_PATH', BASE_DIR / 'db.sqlite3'),
    }
}
```

## Prevention Checklist

When working with SQLite in development:

- [ ] **Know your database location**: Run `python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"`
- [ ] **Create backups in a dedicated directory**: Use `backups/` folder, not scattered across `src/`
- [ ] **Use automated scripts**: Leverage `db_backup.sh` and `db_restore.sh` for consistency
- [ ] **Verify after restore**: Always run Django ORM queries to confirm data visibility
- [ ] **Document database location**: Add to project README and `.env.example`
- [ ] **Use relative paths**: Configure `BASE_DIR / 'db.sqlite3'` instead of hardcoded paths

## Quick Reference Commands

```bash
# Find Django's database location
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"

# Create backup with timestamp
cp "$(python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])")" "backup.$(date +%Y%m%d_%H%M%S).sqlite3"

# Verify data exists
python manage.py shell -c "from common.models import Region; print(Region.objects.count())"

# List all database files in project
find . -name "*.sqlite3" -o -name "*.db"
```

## Related Files

- Settings: `src/obc_management/settings.py`
- Database location: Check `DATABASES['default']['NAME']`
- Backup scripts: `scripts/db_backup.sh`, `scripts/db_restore.sh`
- Geographic models: `src/common/models.py` (Region, Province, Municipality, Barangay)

## See Also

- [Django Database Configuration](https://docs.djangoproject.com/en/stable/ref/settings/#databases)
- [SQLite in Django](https://docs.djangoproject.com/en/stable/ref/databases/#sqlite-notes)
- Project docs: `docs/development/README.md`
