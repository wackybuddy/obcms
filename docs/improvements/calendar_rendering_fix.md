# Calendar Rendering Fix - October 1, 2025

## Issue Summary

The OOBC Calendar Management page at `/oobc-management/calendar/` was not displaying the FullCalendar widget despite having all necessary components in place.

## Root Cause

**Static Files Misconfiguration**: The `STATICFILES_DIRS` setting in `src/obc_management/settings/base.py` was pointing to the wrong directory:

```python
# BEFORE (Incorrect)
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Pointed to src/obc_management/static (nearly empty)
]
```

This meant Django was looking for static files in `src/obc_management/static/`, but the actual FullCalendar library and other static assets were located in `src/static/`.

## Solution

### 1. Fixed Static Files Path

**File**: `src/obc_management/settings/base.py:169`

```python
# AFTER (Correct)
STATICFILES_DIRS = [
    BASE_DIR.parent / "static",  # Points to src/static/
]
```

**Explanation**:
- `BASE_DIR` = `src/obc_management/` (where settings.py is located)
- `BASE_DIR.parent` = `src/`
- `BASE_DIR.parent / "static"` = `src/static/` ✅

### 2. Fixed Template Issues

**File**: `src/templates/common/oobc_calendar.html`

**Changes**:
- Removed broken CSS link to non-existent FullCalendar CSS (v6 bundles CSS in JS)
- Removed duplicate calendar initialization from `calendar_widget.html` component
- Added debug logging to diagnose rendering issues
- Directly embedded calendar div instead of using widget component

### 3. Added Documentation

**Files Updated**:
- `docs/development/README.md` - Added "Static Files Architecture" section
- `CLAUDE.md` - Added "Static Files Configuration" reference

## Files Modified

1. ✅ `src/obc_management/settings/base.py` - Fixed STATICFILES_DIRS
2. ✅ `src/templates/common/oobc_calendar.html` - Removed duplicate rendering, added debugging
3. ✅ `docs/development/README.md` - Documented static files architecture
4. ✅ `CLAUDE.md` - Added static files configuration reference

## Verification

### Check Static Files Directory
```bash
cd src
../venv/bin/python manage.py shell -c "from django.conf import settings; import os; static_dir = settings.STATICFILES_DIRS[0]; print('Static dir:', static_dir); print('Exists:', os.path.exists(static_dir)); print('Has fullcalendar:', os.path.exists(static_dir / 'common/vendor/fullcalendar/index.global.min.js'))"
```

**Expected Output**:
```
Static dir: /path/to/obcms/src/static
Exists: True
Has fullcalendar: True
```

### Check Calendar Data
```bash
cd src
../venv/bin/python manage.py shell -c "from common.services.calendar import build_calendar_payload; payload = build_calendar_payload(); print('Total entries:', len(payload['entries']))"
```

**Expected Output**: `Total entries: 12` (or current number of events)

### Visual Verification
1. Navigate to http://localhost:8000/oobc-management/calendar/
2. Calendar widget should render with month/week/list views
3. Module filter checkboxes should toggle event visibility
4. Browser console should show initialization logs (if debug logging enabled)

## Static Files Architecture (Summary)

### Current Structure
```
src/
├── static/                      # ✅ Correct location (centralized)
│   ├── admin/                  # Admin customizations
│   ├── common/
│   │   ├── css/
│   │   ├── js/
│   │   └── vendor/
│   │       └── fullcalendar/   # FullCalendar library
│   ├── communities/
│   ├── coordination/
│   ├── mana/
│   └── vendor/                 # Shared libraries (Leaflet, etc.)
└── obc_management/
    └── static/                 # ❌ Nearly empty (placeholder)
```

### Why Centralized?
1. **Shared resources** - Vendor libraries used across multiple apps
2. **Consistent with templates** - Templates in `src/templates/`, static in `src/static/`
3. **Easier deployment** - Single `collectstatic` source
4. **Better maintenance** - One location for all assets

## Lessons Learned

1. **Always verify static file paths** when JavaScript/CSS doesn't load
2. **BASE_DIR in Django** points to where `settings.py` lives, not the project root
3. **FullCalendar v6** bundles CSS in JS, separate CSS file not needed
4. **Server restart required** after modifying Django settings
5. **Document architecture decisions** to prevent future confusion

## Related Issues

- Similar issues could occur with other static assets if paths are incorrect
- Always check `STATICFILES_DIRS` configuration when static files 404
- Production deployments need `collectstatic` to gather files to `STATIC_ROOT`

## Future Considerations

### Minor Inconsistency (Non-Breaking)
Two vendor directories exist:
- `src/static/common/vendor/` - FullCalendar (app-specific)
- `src/static/vendor/` - Leaflet, localforage, idb (truly shared)

**Decision**: Keep as-is. This minor inconsistency is logical and doesn't cause issues:
- FullCalendar is primarily used in the common app
- Leaflet is used across multiple apps (MANA, coordination)

### Potential Future Cleanup (Optional)
- Could move all vendor libraries to `src/static/vendor/` for consistency
- Would require updating template references
- Not urgent - current structure works well

## References

- [Static Files Architecture Documentation](../development/README.md#static-files-architecture)
- [Django Static Files Documentation](https://docs.djangoproject.com/en/4.2/howto/static-files/)
- [FullCalendar v6 Documentation](https://fullcalendar.io/docs/initialize-globals)

---

**Status**: ✅ **Resolved**
**Date**: October 1, 2025
**Severity**: Medium (Calendar not displaying)
**Impact**: Calendar now renders correctly with all 12 aggregated events from coordination, MANA, staff, policy, and planning modules
