# E2E Test Blocking Issues - Resolution Guide

**Priority:** HIGH
**Impact:** 68 of 171 tests (40%) blocked from execution
**Date:** 2025-10-20

---

## Issue #1: Project Models Deprecated Migration

**Status:** ⚠️ BLOCKED
**Severity:** HIGH
**Tests Affected:** 37 (ProjectActivity, ProjectWorkflow)

### Problem

The test file `tests/test_project_integration.py` references models that were migrated to the WorkItem system on 2025-10-05:

```python
# BROKEN - These imports no longer work
from project_central.models import ProjectWorkflow  # ❌ Deprecated
from coordination.models import Event              # ❌ Deprecated
from common.models import StaffTask                # ❌ Abstract model
```

**Why It Fails:**
- Models marked `abstract=True` - cannot be instantiated
- No database tables exist for these models
- Tests fail during setUp phase before any assertions

### Current Test Structure

**File:** `src/tests/test_project_integration.py` (862 lines)

**Test Classes:**
1. `ProjectActivityIntegrationTest` (11 tests) - Tests project-activity-task integration
2. `ProjectWorkflowPropertyTest` (2 tests) - Tests ProjectWorkflow properties
3. `EnhancedTaskGenerationTest` (11 tests) - Tests auto-task generation
4. `WorkflowSignalTest` (3 tests) - Tests signal handlers

### Solution: Option A - Rewrite to WorkItem Model

**Recommended:** YES - Ensures full coverage of current architecture

**Work Required:**
- 3-4 hours of development
- Complete test file rewrite (~862 lines)
- Update model references
- Verify all test assertions work with new model

**Steps:**

1. **Replace Model Imports**
   ```python
   # FROM:
   from project_central.models import ProjectWorkflow
   from coordination.models import Event
   from common.models import StaffTask

   # TO:
   from common.work_item_model import WorkItem
   ```

2. **Update setUp Methods**
   ```python
   # FROM:
   self.workflow = ProjectWorkflow.objects.create(
       primary_need=self.need,
       current_stage="need_identification",
       priority_level="high",
       project_lead=self.user,
   )

   # TO:
   self.workflow = WorkItem.objects.create(
       work_type=WorkItem.WORK_TYPE_PROJECT,
       title="Test Project",
       project_stage="need_validation",
       project_lead=self.user,
       project_data={'primary_need_id': str(self.need.id)},
   )
   ```

3. **Update Test Assertions**
   ```python
   # FROM:
   self.assertEqual(event.related_project, self.workflow)

   # TO:
   project_activities = WorkItem.objects.filter(
       work_type=WorkItem.WORK_TYPE_ACTIVITY,
       parent_work_item=self.workflow
   )
   self.assertIn(activity, project_activities)
   ```

4. **Rewrite Task Generation Tests**
   - Test uses `StaffTask` → replace with `WorkItem(work_type='task')`
   - Update signal handler tests for new WorkItem signals
   - Verify task hierarchy integration

**Estimated Time:** 3-4 hours

---

### Solution: Option B - Delete Obsolete Tests

**Recommended:** If WorkItem has equivalent coverage

**Criteria:**
- ✅ Proceed if: WorkItem test suite covers project/activity/task workflows
- ❌ Skip if: Need specific project workflow tests not covered elsewhere

**Steps:**
1. Verify WorkItem test coverage includes:
   - Project creation and properties
   - Activity/task generation
   - Signal handlers
   - Task hierarchies

2. If coverage complete: Delete `src/tests/test_project_integration.py`

3. If coverage incomplete: Choose Option A

**Estimated Time:** 5 minutes (verification + deletion)

---

## Issue #2: Playwright E2E Authentication Flow

**Status:** ⚠️ BLOCKED
**Severity:** MEDIUM
**Tests Affected:** 23 (Budget Preparation E2E)

### Problem

Playwright browser automation tests cannot complete login flow:

```
1. Test loads /login/ page ✅
2. Test fills username/password ✅
3. Test submits form ✅
4. Server responds with 302 redirect ⚠️
5. Browser follows redirect to /dashboard/... ⚠️
6. Server returns 302 to /login/ again (login failed)
7. Loop repeats infinitely ❌
```

**Root Causes:**
1. CSRF token not being captured/submitted properly
2. Session cookies not persisting
3. Form field selectors may not match actual form

### Fixed Issues

Already completed:
- ✅ Updated `ALLOWED_HOSTS` to include `localhost`
- ✅ Updated `CSRF_TRUSTED_ORIGINS` for localhost
- ✅ Ran `collectstatic` for 219 static files

### Remaining Issues

**Investigate:**

1. **Form Field Selectors**
   ```python
   # In test file - may not match actual HTML
   page.get_by_label("Username").fill("playwright")
   page.get_by_label("Password").fill("Playwright123!")
   ```

   **Debug:**
   - Open https://localhost:8000/login/ in browser
   - Inspect form element IDs and labels
   - Verify Playwright selectors match

2. **CSRF Token Handling**
   ```python
   # Check if test captures and includes CSRF token
   csrf_token = page.get_by_name("csrfmiddlewaretoken").input_value()
   # Verify this token is included in form submission
   ```

3. **Session Cookie Persistence**
   ```python
   # Verify cookies set after login
   cookies = page.context.cookies()
   print(f"Cookies: {cookies}")
   # Should include 'sessionid' cookie
   ```

### Solution: Option A - Debug Playwright Login

**Recommended:** If E2E testing is priority

**Steps:**

1. **Enable Playwright Tracing**
   ```python
   async with context.tracing.record_as_har("trace.har"):
       # Run test
       page.goto("http://localhost:8000/login/")
   ```

2. **Capture Screenshots**
   ```python
   page.screenshot(path="login_page.png")
   page.fill("username_field", "playwright")
   page.screenshot(path="filled_form.png")
   page.click("submit_button")
   page.screenshot(path="after_submit.png")
   ```

3. **Add Network Logging**
   ```python
   page.on("response", lambda response:
       print(f"{response.request.method} {response.url} -> {response.status}")
   )
   ```

4. **Test Login Manually First**
   - Start Django dev server: `python manage.py runserver`
   - Open http://localhost:8000/login/ in browser
   - Test login works manually
   - Compare manual flow with Playwright test

**Estimated Time:** 2-4 hours

---

### Solution: Option B - Use Django LiveServerTestCase

**Recommended:** If Playwright debugging is too complex

**Benefits:**
- Eliminates CSRF token issues (Django handles internally)
- Automatic database setup/teardown
- No need for external server
- Built-in session management

**Steps:**

1. **Create LiveServerTestCase**
   ```python
   from django.test import LiveServerTestCase
   from playwright.async_api import async_playwright

   class BudgetE2ETests(LiveServerTestCase):
       async def test_login_and_access(self):
           async with async_playwright() as p:
               browser = await p.chromium.launch()
               context = await browser.new_context()
               page = await context.new_page()

               await page.goto(f"{self.live_server_url}/login/")
               # Test continues...
   ```

2. **Update Test Configuration**
   - Set `ALLOWED_HOSTS = ['testserver', '*']` in test settings
   - LiveServerTestCase provides `testserver` domain

3. **Run Tests**
   ```bash
   python manage.py test budget_preparation.tests.test_e2e_budget_preparation
   ```

**Estimated Time:** 1 hour setup

---

### Solution: Option C - Manual E2E Testing

**Recommended:** If automation troubleshooting isn't priority

**Steps:**
1. Document expected user workflows
2. Create manual testing checklist
3. Test in browser (Chrome/Firefox)
4. Document findings
5. Re-visit automated E2E when time available

**Estimated Time:** 1 hour per workflow

---

## Issue #3: Pytest Configuration - Monitoring Tests

**Status:** ⚠️ BLOCKED
**Severity:** MEDIUM
**Tests Affected:** 8 (Monitoring WorkItem Integration)

### Problem

Tests hang indefinitely during pytest collection/setup:

```
collecting... collected 8 items

[hangs for 10+ minutes - never reaches test execution]
```

**Root Cause:** Pytest environment configuration issue (NOT code issue)

**Evidence:** Manual test confirms code works perfectly:
```python
# Manual test succeeds in < 2 seconds
entry = MonitoringEntry.objects.create(...)
project = entry.create_execution_project(created_by=user)
print(f"SUCCESS - Created project: {project.title}")
# Result: SUCCESS ✓
```

### Issues Identified

1. **Session-scoped Fixtures**
   - `tests/conftest.py` has session-scoped `django_db_setup`
   - Calls `get_or_create_default_organization()` during setup
   - May cause database locks or infinite loops

2. **Stale Pytest Processes**
   - Multiple pytest processes from previous runs
   - Competing for database access
   - Creating locks/timeouts

3. **Pytest Configuration**
   - Coverage plugins may be interfering
   - Test discovery taking too long
   - Cache issues

### Solution: Option A - Use Django Test Runner

**Recommended:** Immediate workaround (fastest)

**Steps:**
```bash
# Run using Django test runner instead of pytest
python manage.py test monitoring.tests.test_workitem_integration -v 2

# Or with specific test class
python manage.py test monitoring.tests.test_workitem_integration.TestMonitoringEntryWorkItemIntegration -v 2
```

**Benefits:**
- Bypasses pytest configuration issues
- Django handles database setup/teardown
- Tests should run in seconds
- No hanging

**Estimated Time:** 1 minute execution

---

### Solution: Option B - Fix Pytest Configuration

**Recommended:** For long-term testing infrastructure

**Steps:**

1. **Kill Stale Processes**
   ```bash
   pkill -f pytest
   ```

2. **Review Session-Scoped Fixtures**
   - Open `src/tests/conftest.py`
   - Check `django_db_setup` fixture
   - Convert from session-scoped to function-scoped:
   ```python
   # FROM:
   @pytest.fixture(scope="session")
   def django_db_setup(django_db_setup):
       ...

   # TO:
   @pytest.fixture(scope="function")
   def django_db_setup(django_db_setup):
       ...
   ```

3. **Disable Coverage During Test Collection**
   ```bash
   pytest monitoring/tests/test_workitem_integration.py -v --no-cov
   ```

4. **Disable Cache**
   ```bash
   pytest monitoring/tests/test_workitem_integration.py -v -p no:cacheprovider
   ```

5. **Run with Timeout**
   ```bash
   timeout 60 pytest monitoring/tests/test_workitem_integration.py -v
   ```

**Estimated Time:** 1-2 hours investigation + fixes

---

### Solution: Option C - Mock Signal Handlers

**Recommended:** If conftest.py changes don't help

**Issue:** `get_or_create_default_organization()` may trigger geocoding signals

**Steps:**

1. **Identify Slow Setup**
   - Add timing to conftest.py setup
   - Check if organization creation is slow

2. **Mock Geocoding Signals**
   ```python
   # In conftest.py
   @pytest.fixture(scope="function")
   def django_db_setup(django_db_setup, monkeypatch):
       # Mock the geocoding signal handlers
       monkeypatch.setattr(
           "common.signals.municipality_post_save",
           lambda: None
       )
       monkeypatch.setattr(
           "common.signals.barangay_post_save",
           lambda: None
       )
   ```

3. **Re-run Tests**
   ```bash
   pytest monitoring/tests/test_workitem_integration.py -v
   ```

**Estimated Time:** 30 minutes

---

## Priority Resolution Order

### Phase 1: Immediate (Today)
1. **Run the 103 ready tests** to verify they pass
2. **Use Option A (Django runner) for Monitoring tests**
   - Unblocks 8 tests in minutes

### Phase 2: Short Term (This Week)
3. **Choose Option A or B for Project tests**
   - Decide: Rewrite or delete?
   - Unblocks 37 tests

4. **Debug Playwright E2E** (Option A)
   - Or use LiveServerTestCase (Option B)
   - Unblocks 23 tests

### Phase 3: Long Term (This Month)
5. **Fix Pytest Configuration**
   - Prevent future issues
   - Improve test reliability

---

## Test Readiness Dashboard

| Module | Tests | Status | Blocker | Resolution |
|--------|-------|--------|---------|------------|
| Budget Execution | 37 | ✅ PASS | None | Run tests |
| Work Items | 13 | ✅ FIXED | None | Run tests |
| Tasks | 17 | ✅ FIXED | None | Run tests |
| Calendar | 2 | ✅ FIXED | None | Run tests |
| Communities | 34 | ✅ FIXED | None | Run tests |
| **Subtotal** | **103** | **✅** | **-** | **Ready** |
| Projects | 37 | ⚠️ BLOCKED | Deprecated models | Option A/B |
| Organizations | 10 | ⚠️ BLOCKED | Deprecated models | Option A/B |
| Budget E2E | 23 | ⚠️ BLOCKED | Auth flow | Option A/B/C |
| Monitoring | 8 | ⚠️ BLOCKED | Pytest config | Option A |
| **Subtotal** | **68** | **⚠️** | **Various** | **1-4 hours** |

---

## Conclusion

**3 blocking issues affecting 68 tests** can be resolved with targeted solutions:

1. **Project tests** - Rewrite to WorkItem (3-4 hours) OR delete (5 minutes)
2. **Playwright E2E** - Debug (2-4 hours) OR use LiveServerTestCase (1 hour)
3. **Monitoring tests** - Use Django runner (immediate) OR fix pytest (1-2 hours)

**Recommended Path:**
1. Run 103 ready tests (verify pass)
2. Use Django runner for Monitoring (unblock 8 tests)
3. Choose Project fix strategy (unblock 37 tests)
4. Choose Playwright fix strategy (unblock 23 tests)

**Timeline:** 1-2 days to fully resolve all blocking issues.
