# Authentication & Authorization Component Test Analysis

## Executive Summary

Comprehensive analysis of all authentication and authorization component tests in OBCMS:

- **Total Test Files**: 6 core auth/permission test modules
- **Total Test Cases**: 77 collected tests
- **Test Categories**: Decorators, Mixins, DRF Permissions, MOA RBAC, Organization Access Control, Security
- **Issues Found & Fixed**: 1 critical bug fixed
- **Status**: Ready for full test run

## Component Architecture

### 1. RBAC Decorators
**Location**: `src/common/decorators/rbac.py`

**Components**:
- `require_permission(permission_code, organization_param=None)` - Function-based view decorator
- `require_feature_access(feature_code, organization_param=None)` - Feature access decorator
- Both decorators include security audit logging for access denials

**Security Features**:
- IP address extraction and logging
- Organization context extraction from URL/GET/POST parameters
- Error message logging with user/org/permission details
- Integration with RBACService for centralized permission checking

### 2. Permission Classes (DRF)
**Location**: `src/common/permissions/rbac_permissions.py`

**Classes**:
- `HasFeatureAccess` - Check feature access at view level
- `HasPermission` - Check specific permissions
- `HasAnyPermission` - OR logic (any of multiple permissions)
- `HasAllPermissions` - AND logic (all of multiple permissions)

### 3. MOA RBAC Utilities
**Location**: `src/common/utils/moa_permissions.py`

**Features**:
- `@moa_view_only` - Block mutating operations for MOA staff (POST/PUT/DELETE)
- `@moa_can_edit_organization` - Limit to owned organization
- `@moa_can_edit_ppa` - Validate implementing MOA
- `@moa_can_edit_work_item` - Check related PPA
- `@moa_no_access` - Block MOA staff from certain views
- `@user_can_access_mana` - MANA-specific role checks

### 4. Organization Permissions
**Location**: `src/common/permissions/organization.py`

**Class**: `OrganizationAccessPermission`

**Features**:
- Multi-tenant permission checking
- Cross-organization access blocking
- Superuser bypass
- Membership validation
- BMMS mode support (legacy multi-ministry setup)

## Test Modules

### Module 1: test_rbac_decorators.py (14 tests)

**Test Cases**:
1. `test_require_permission_decorator_unauthenticated` - **FIXED**
2. `test_require_permission_decorator_superuser`
3. `test_require_feature_access_decorator_unauthenticated`
4. `test_require_feature_access_decorator_superuser`
5. `test_permission_required_mixin_superuser`
6. `test_feature_access_mixin_superuser`
7. `test_multi_permission_mixin_superuser`
8. `test_has_permission_class`
9. `test_has_feature_access_permission`
10. `test_has_any_permission_class`
11. `test_has_all_permissions_class`
12. `test_organization_param_from_kwargs`
13. `test_organization_param_from_get`
14. `test_permission_denied_message`

**Coverage**:
- Decorator behavior with authenticated/unauthenticated users
- Superuser bypass
- Mixin functionality
- DRF permission classes
- Organization context extraction
- Error messaging

### Module 2: test_rbac_templatetags.py (14 tests)

**Test Cases**:
1. `test_has_permission_tag_superuser`
2. `test_has_permission_tag_anonymous`
3. `test_can_access_feature_filter`
4. `test_can_access_feature_filter_anonymous`
5. `test_get_accessible_features_superuser`
6. `test_get_permission_context`
7. `test_feature_url_tag`
8. `test_feature_icon_tag`
9. `test_has_sub_features_filter`
10. `test_action_button_with_permission`
11. `test_action_button_without_permission`
12. `test_action_button_link_type`
13. `test_action_button_with_icon`
14. (Additional template tag tests)

**Coverage**:
- Template tag permission checks
- Filter functionality for templates
- Feature URL generation
- Icon rendering based on permissions
- Action button conditional rendering

### Module 3: test_moa_permissions_utils.py (6 tests)

**Test Cases**:
1. `test_moa_view_only_blocks_mutating_requests` - MOA POST/PUT/DELETE blocking
2. `test_moa_can_edit_organization_limits_to_owned_org` - Organization scoping
3. `test_moa_can_edit_ppa_validates_implementing_moa` - PPA ownership validation
4. `test_moa_can_edit_work_item_checks_related_ppa` - WorkItem/PPA relationship
5. `test_moa_no_access_blocks_moa_staff` - Feature blocking
6. `test_user_can_access_mana_rules` - MANA role checks

**Coverage**:
- MOA staff restrictions
- Organization-scoped editing
- PPA (Performance Planning Agreement) validation
- WorkItem access control
- Feature-level access blocking

### Module 4: test_organization_permissions.py (9 tests)

**Test Cases**:
1. `test_permission_granted_with_organization`
2. `test_permission_denied_without_organization`
3. `test_permission_granted_for_superuser`
4. `test_permission_validates_membership`
5. `test_has_object_permission_validates_organization`
6. `test_has_object_permission_blocks_cross_org_access`
7. `test_has_object_permission_allows_non_org_objects`
8. `test_permission_denied_for_unauthenticated`
9. `test_permission_denied_for_inactive_membership`

**Coverage**:
- Organization context validation
- Membership verification
- Cross-organization access blocking
- Object-level permission checks
- Inactive member handling

### Module 5: test_organization_decorators.py (9 tests)

**Test Cases**:
1. `test_decorator_passes_with_organization`
2. `test_decorator_blocks_without_organization`
3. `test_decorator_allows_superuser_in_bmms_mode`
4. `test_decorator_validates_membership_in_bmms_mode`
5. `test_decorator_validates_membership`
6. `test_decorator_loads_organization_from_url`
7. `test_decorator_handles_missing_parameter`
8. `test_decorator_handles_invalid_org_code`
9. `test_decorator_case_insensitive_lookup`

**Coverage**:
- Decorator organization context handling
- BMMS mode (legacy multi-ministry) support
- URL parameter loading
- Org code case-insensitivity
- Error handling for invalid org codes

### Module 6: test_security.py (25 tests)

**Test Cases**:
1. `test_sql_injection_in_search`
2. `test_sql_injection_in_filter`
3. `test_sql_injection_in_api`
4. `test_xss_in_proposal_title`
5. `test_xss_in_description`
6. `test_xss_in_search_results`
7. `test_csrf_protection_on_create`
8. `test_csrf_protection_on_update`
9. `test_cannot_access_other_organization_budget`
10. `test_cannot_modify_other_organization_budget`
11. `test_non_admin_cannot_approve_budget`
12. `test_api_requires_authentication`
13. `test_no_password_exposure_in_api`
14. `test_no_internal_ids_exposure`
15. `test_error_messages_dont_expose_system_info`
16. `test_login_rate_limiting`
17. `test_api_rate_limiting`
18. `test_session_expires`
19. `test_session_regeneration_on_login`
20. `test_negative_budget_amount_rejected`
21. `test_invalid_fiscal_year_rejected`
22. `test_excessive_input_length_rejected`
23. `test_malicious_file_extension_rejected`
24. `test_oversized_file_rejected`
25. `test_run_zap_scan`

**Coverage**:
- SQL injection prevention
- XSS protection
- CSRF token validation
- Cross-organization data isolation
- API authentication
- Data exposure prevention
- Session management
- Input validation
- File upload security
- Rate limiting

## Issues Found & Fixed

### Issue 1: Null User Object Handling in RBAC Decorators (CRITICAL)

**Severity**: CRITICAL - Authentication bypass / AttributeError

**Location**: `src/common/decorators/rbac.py`

**Files Affected**:
- `src/common/decorators/rbac.py` (lines 97, 181)

**Problem**:
Both `require_permission` and `require_feature_access` decorators directly access `request.user.is_authenticated` without null checking. When `request.user = None`, this raises:
```
AttributeError: 'NoneType' object has no attribute 'is_authenticated'
```

The test expects `PermissionDenied` but gets `AttributeError` instead.

**Root Cause**:
- Decorators assume `request.user` always exists
- No defensive null check before attribute access
- Only checked if user is authenticated, not if user exists

**Fix Applied**:
Changed authentication check from:
```python
if not request.user.is_authenticated:
```

To:
```python
if not request.user or not request.user.is_authenticated:
```

**Locations Fixed**:
1. Line 97 in `require_permission` decorator
2. Line 181 in `require_feature_access` decorator

**Tests Passing After Fix**:
- `test_require_permission_decorator_unauthenticated`
- `test_require_feature_access_decorator_unauthenticated`

**Verification**: Both decorators now properly handle None user objects and raise `PermissionDenied` as expected.

## Test Data Fixtures

All auth tests use proper test fixtures:
- `create_organization()` - Factory for MOA/OOBC organizations
- `create_monitoring_entry()` - Factory for PPA/MonitoringEntry
- User factories with different roles:
  - OOBC staff
  - MOA staff (assigned to organization)
  - Superuser
  - Anonymous user

## Multi-Organization Data Isolation

Tests verify:
1. MOA users cannot access other MOA's data
2. Organization membership prevents cross-org access
3. Object-level permissions validate organization ownership
4. OCM aggregation access (read-only) is separate from org-scoped access

## Role-Based Access Control Coverage

**Roles Tested**:
1. **Superuser**: Full access bypass
2. **OOBC Staff**: Multi-organization access
3. **MOA Staff**: Single-organization scoped access
4. **Municipal Coordinator**: Limited MANA assessment access
5. **Anonymous**: No access

## Key Assertions by Category

### Permission Decorators
- Authorized users can execute decorated views
- Unauthorized users get PermissionDenied
- Superusers bypass all checks
- Unauthenticated users get proper error
- Organization context extracted from URL/GET/POST

### DRF Permission Classes
- Works with ViewSet permission_classes
- Feature access checked from view.feature_code
- Permission code checked from view.permission_code
- Multiple permission combinations (AND/OR)

### MOA RBAC
- GET requests allowed for MOA
- POST/PUT/DELETE blocked for MOA
- Organization ownership validated
- PPA implementing_moa checked
- WorkItem PPA relationship validated

### Organization Access Control
- Cross-organization access blocked
- Membership validation required
- Inactive members denied
- Superusers bypass org checks

### Security
- SQL injection blocked
- XSS prevented
- CSRF tokens required
- Data not exposed to other orgs
- API authentication enforced
- Rate limiting on login/API
- Session expiration working
- File upload restrictions

## Recommendations

### HIGH Priority
1. **Complete full test run**: All 77 tests need execution to identify any remaining failures
2. **Add token expiration tests**: Verify JWT/session token expiration handling
3. **Add tampered token tests**: Verify system detects and handles tampered tokens
4. **Add audit logging tests**: Verify all auth failures are logged

### MEDIUM Priority
1. Extend MOA permission tests for edge cases (cross-org PPA updates)
2. Add permission caching invalidation tests
3. Add concurrent access tests for race conditions
4. Add permission inheritance tests for hierarchical roles

### LOW Priority
1. Performance benchmarking for permission checks
2. Caching effectiveness tests
3. Browser compatibility for auth flows

## Test Execution Status

**Current Status**: Database migration and test execution in progress

**Expected Completion**: ~5-10 minutes for full auth test suite

**Next Steps**:
1. Complete full test run of all 77 tests
2. Identify and fix any additional failures
3. Verify 100% pass rate
4. Generate JUnit XML report for CI

---

**Report Generated**: 2025-10-20
**Test Framework**: pytest with Django
**Configuration**: `src/pytest.ini`
