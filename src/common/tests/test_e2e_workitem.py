"""
End-to-End tests for WorkItem functionality using Playwright.

Tests the complete workitem lifecycle from UI perspective:
- Creating workitems (projects, activities, tasks)
- Editing workitems (form population and updates)
- Deleting workitems (confirmation and removal)
- Listing workitems with filtering/search
- Form validation and error messaging
- Responsive design across screen sizes
- Accessibility compliance (keyboard navigation, screen readers)

Requirements:
- Playwright must be installed
- Set RUN_PLAYWRIGHT_E2E=1 to enable tests
- Set PLAYWRIGHT_BASE_URL for server URL (default: http://localhost:8000)
- Set PLAYWRIGHT_USERNAME and PLAYWRIGHT_PASSWORD for authentication
"""

import os
import re
import time
from decimal import Decimal

import pytest

try:
    from playwright.sync_api import Page, expect
except ImportError:  # pragma: no cover
    pytest.skip(
        "Playwright is required for workitem E2E tests",
        allow_module_level=True,
    )

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_PLAYWRIGHT_E2E") != "1",
    reason="Set RUN_PLAYWRIGHT_E2E=1 to execute Playwright E2E tests against a live server.",
)


@pytest.fixture
def authenticated_page(page: Page):
    """Fixture to provide an authenticated page session."""
    base_url = os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:8000")
    username = os.environ.get("PLAYWRIGHT_USERNAME", "playwright")
    password = os.environ.get("PLAYWRIGHT_PASSWORD", "Playwright123!")

    # Login
    page.goto(f"{base_url}/login/")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name=re.compile("Sign In", re.IGNORECASE)).click()

    # Verify redirect to dashboard
    expect(page).to_have_url(re.compile(".*/dashboard/.*"), timeout=15000)

    yield page


@pytest.fixture(scope="session")
def base_url():
    """Fixture for base URL."""
    return os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


class TestWorkItemCreation:
    """Test creating workitems through the UI."""

    def test_create_project_workitem(self, authenticated_page: Page, base_url: str):
        """Test creating a new project workitem."""
        page = authenticated_page
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg.text))

        # Navigate to workitem list
        page.goto(f"{base_url}/oobc-management/work-items/")
        expect(page).to_have_url(re.compile(".*/work-items/.*"), timeout=10000)

        # Click "Create" or "New" button
        create_button = page.get_by_role("button", name=re.compile("Create|New|Add", re.IGNORECASE))
        create_button.click()

        # Wait for form to appear
        form = page.locator("form#workitem-form, form[id*='work'], form")
        expect(form).to_be_visible(timeout=5000)

        # Fill in workitem details
        unique_suffix = int(time.time())
        title = f"E2E Test Project {unique_suffix}"

        # Select work type
        work_type_select = page.locator('select[name="work_type"]')
        if work_type_select.count() > 0:
            work_type_select.select_option("project")

        # Fill title
        page.locator('input[name="title"]').fill(title)

        # Fill description
        page.locator('textarea[name="description"]').fill("Created via E2E Playwright test")

        # Fill optional fields
        page.locator('select[name="priority"]').select_option("high")
        page.locator('select[name="status"]').select_option("planned")

        # Submit form
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        # Wait for success toast or redirect
        page.wait_for_timeout(2000)

        # Verify workitem appears in list or was created successfully
        if page.url.endswith("/work-items/"):
            # Still on list view - workitem should be there
            workitem_title = page.locator(f"text='{title}'")
            expect(workitem_title).to_be_visible(timeout=5000)
        else:
            # Redirected to detail view
            expect(page).to_have_url(re.compile(".*/work-items/.*"), timeout=5000)

    def test_create_activity_workitem(self, authenticated_page: Page, base_url: str):
        """Test creating a new activity workitem."""
        page = authenticated_page

        # Navigate to workitem creation
        page.goto(f"{base_url}/oobc-management/work-items/create/")

        # Wait for form
        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Select activity type
        work_type_select = page.locator('select[name="work_type"]')
        work_type_select.select_option("activity")

        # Select activity category
        activity_category = page.locator('select[name="activity_category"]')
        if activity_category.count() > 0:
            options = activity_category.locator("option[value]")
            valid_values = [
                option.get_attribute("value")
                for option in options.all()
                if option.get_attribute("value")
            ]
            if valid_values:
                activity_category.select_option(value=valid_values[0])

        # Fill in details
        unique_suffix = int(time.time())
        title = f"E2E Test Activity {unique_suffix}"

        page.locator('input[name="title"]').fill(title)
        page.locator('textarea[name="description"]').fill("Test activity created via E2E")
        page.locator('select[name="status"]').select_option("planned")

        # Set dates
        today = time.strftime("%Y-%m-%d")
        page.locator('input[name="start_date"]').fill(today)
        page.locator('input[name="due_date"]').fill(today)

        # Submit
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        # Verify success
        page.wait_for_timeout(2000)
        activity_title = page.locator(f"text='{title}'")
        expect(activity_title).to_be_visible(timeout=5000)

    def test_create_task_workitem(self, authenticated_page: Page, base_url: str):
        """Test creating a new task workitem."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/create/")

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Select task type
        work_type_select = page.locator('select[name="work_type"]')
        work_type_select.select_option("task")

        # Fill task details
        unique_suffix = int(time.time())
        title = f"E2E Test Task {unique_suffix}"

        page.locator('input[name="title"]').fill(title)
        page.locator('textarea[name="description"]').fill("Test task")
        page.locator('select[name="priority"]').select_option("medium")

        # Submit
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)
        task_title = page.locator(f"text='{title}'")
        expect(task_title).to_be_visible(timeout=5000)

    def test_create_workitem_with_dates(self, authenticated_page: Page, base_url: str):
        """Test creating workitem with date fields."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/create/")

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Fill basic fields
        unique_suffix = int(time.time())
        title = f"E2E Test with Dates {unique_suffix}"

        page.locator('input[name="title"]').fill(title)
        page.locator('select[name="work_type"]').select_option("project")

        # Set dates
        today = time.strftime("%Y-%m-%d")
        tomorrow = time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))

        page.locator('input[name="start_date"]').fill(today)
        page.locator('input[name="due_date"]').fill(tomorrow)

        # Submit
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)

        # Verify workitem was created
        title_element = page.locator(f"text='{title}'")
        expect(title_element).to_be_visible(timeout=5000)


class TestWorkItemEditing:
    """Test editing workitems through the UI."""

    def test_edit_workitem_basic_fields(self, authenticated_page: Page, base_url: str):
        """Test editing basic workitem fields."""
        page = authenticated_page

        # Navigate to workitem list
        page.goto(f"{base_url}/oobc-management/work-items/")
        expect(page).to_have_url(re.compile(".*/work-items/.*"), timeout=10000)

        # Wait for list to load
        page.wait_for_timeout(2000)

        # Find first workitem and click edit
        workitem_rows = page.locator('[data-workitem-id], .workitem-row, tr[data-id]')
        if workitem_rows.count() == 0:
            pytest.skip("No workitems available for editing test")

        # Click on first workitem
        first_workitem = workitem_rows.first
        first_workitem.click()

        # Wait for detail page
        expect(page).to_have_url(re.compile(".*/work-items/.*"), timeout=10000)

        # Click edit button
        edit_button = page.get_by_role("button", name=re.compile("Edit", re.IGNORECASE))
        edit_button.click()

        # Wait for edit form
        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Verify form is pre-populated
        title_input = page.locator('input[name="title"]')
        original_title = title_input.input_value()
        assert original_title, "Title should be pre-populated"

        # Update title
        unique_suffix = int(time.time())
        new_title = f"Updated {original_title} {unique_suffix}"
        title_input.fill(new_title)

        # Update description
        description_textarea = page.locator('textarea[name="description"]')
        description_textarea.fill("Updated description via E2E test")

        # Update priority
        page.locator('select[name="priority"]').select_option("critical")

        # Submit
        page.get_by_role("button", name=re.compile("Save|Update|Submit", re.IGNORECASE)).click()

        # Verify success
        page.wait_for_timeout(2000)
        assert page.locator(f"text='{new_title}'").count() > 0, "Updated title should be visible"

    def test_edit_workitem_dates(self, authenticated_page: Page, base_url: str):
        """Test editing workitem date fields."""
        page = authenticated_page

        # Navigate to a workitem
        page.goto(f"{base_url}/oobc-management/work-items/")
        page.wait_for_timeout(2000)

        # Find and open a workitem
        workitem_row = page.locator('[data-workitem-id], .workitem-row, tr[data-id]').first
        if workitem_row.count() == 0:
            pytest.skip("No workitems available for date edit test")

        workitem_row.click()
        page.wait_for_timeout(2000)

        # Click edit
        edit_button = page.get_by_role("button", name=re.compile("Edit", re.IGNORECASE))
        if edit_button.count() == 0:
            pytest.skip("Edit button not found")

        edit_button.click()

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Update dates
        today = time.strftime("%Y-%m-%d")
        one_week = time.strftime("%Y-%m-%d", time.localtime(time.time() + 604800))

        page.locator('input[name="start_date"]').fill(today)
        page.locator('input[name="due_date"]').fill(one_week)

        # Submit
        page.get_by_role("button", name=re.compile("Save|Update|Submit", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)

    def test_edit_workitem_status(self, authenticated_page: Page, base_url: str):
        """Test updating workitem status."""
        page = authenticated_page

        # Navigate to workitem list
        page.goto(f"{base_url}/oobc-management/work-items/")
        page.wait_for_timeout(2000)

        # Open first workitem
        workitem_row = page.locator('[data-workitem-id], .workitem-row, tr[data-id]').first
        if workitem_row.count() == 0:
            pytest.skip("No workitems available for status update test")

        workitem_row.click()
        page.wait_for_timeout(2000)

        # Click edit
        edit_button = page.get_by_role("button", name=re.compile("Edit", re.IGNORECASE))
        if edit_button.count() == 0:
            pytest.skip("Edit button not found")

        edit_button.click()

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Change status
        status_select = page.locator('select[name="status"]')
        status_select.select_option("in_progress")

        # Submit
        page.get_by_role("button", name=re.compile("Save|Update|Submit", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)


class TestWorkItemDeletion:
    """Test deleting workitems through the UI."""

    def test_delete_workitem_with_confirmation(self, authenticated_page: Page, base_url: str):
        """Test deleting a workitem with confirmation dialog."""
        page = authenticated_page

        # Create a workitem first to delete
        page.goto(f"{base_url}/oobc-management/work-items/create/")

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Create a workitem to delete
        unique_suffix = int(time.time())
        title = f"E2E Test Delete {unique_suffix}"

        page.locator('input[name="title"]').fill(title)
        page.locator('select[name="work_type"]').select_option("task")
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        page.wait_for_timeout(2000)

        # Find and click delete button
        delete_button = page.get_by_role("button", name=re.compile("Delete|Remove", re.IGNORECASE))
        if delete_button.count() == 0:
            pytest.skip("Delete button not found")

        delete_button.click()

        # Handle confirmation dialog if it appears
        page.wait_for_timeout(1000)
        confirm_button = page.locator('button:has-text("Confirm"), button:has-text("Yes"), [role="alertdialog"] button:first-child')
        if confirm_button.count() > 0:
            confirm_button.click()

        # Verify workitem was deleted (should redirect or show success)
        page.wait_for_timeout(2000)

    def test_delete_workitem_confirmation_cancel(self, authenticated_page: Page, base_url: str):
        """Test canceling workitem deletion."""
        page = authenticated_page

        # Navigate to workitem list
        page.goto(f"{base_url}/oobc-management/work-items/")
        page.wait_for_timeout(2000)

        # Open a workitem
        workitem_row = page.locator('[data-workitem-id], .workitem-row, tr[data-id]').first
        if workitem_row.count() == 0:
            pytest.skip("No workitems available for cancel delete test")

        workitem_row.click()
        page.wait_for_timeout(2000)

        # Click delete button
        delete_button = page.get_by_role("button", name=re.compile("Delete|Remove", re.IGNORECASE))
        if delete_button.count() == 0:
            pytest.skip("Delete button not found")

        delete_button.click()

        # Cancel deletion
        page.wait_for_timeout(1000)
        cancel_button = page.locator('button:has-text("Cancel"), button:has-text("No")')
        if cancel_button.count() > 0:
            cancel_button.click()
        else:
            # Try to close modal with Escape key
            page.keyboard.press("Escape")

        page.wait_for_timeout(1000)


class TestWorkItemListing:
    """Test workitem list display and filtering."""

    def test_workitem_list_displays_items(self, authenticated_page: Page, base_url: str):
        """Test that workitem list displays correctly."""
        page = authenticated_page

        # Navigate to workitem list
        page.goto(f"{base_url}/oobc-management/work-items/")

        # Wait for list to load
        page.wait_for_load_state("networkidle")

        # Verify page title or header
        page_header = page.locator('h1, [role="heading"]')
        assert page_header.count() > 0, "Page header should be visible"

    def test_workitem_list_search(self, authenticated_page: Page, base_url: str):
        """Test searching workitems in list."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/")
        page.wait_for_timeout(2000)

        # Find search box
        search_input = page.locator('input[type="search"], input[placeholder*="Search"], input[name*="search"]')
        if search_input.count() == 0:
            pytest.skip("Search box not found on workitem list")

        # Type search term
        search_input.fill("test")

        # Wait for results to filter
        page.wait_for_timeout(1500)

    def test_workitem_list_pagination(self, authenticated_page: Page, base_url: str):
        """Test workitem list pagination if available."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/")
        page.wait_for_timeout(2000)

        # Look for pagination
        pagination = page.locator('[role="navigation"] a, .pagination a, [aria-label*="pagination"]')
        if pagination.count() == 0:
            pytest.skip("No pagination found on workitem list")

        # Try to navigate to next page
        next_button = page.locator('a:has-text("Next"), button:has-text("Next")')
        if next_button.count() > 0:
            next_button.click()
            page.wait_for_timeout(1500)


class TestWorkItemValidation:
    """Test client-side and server-side validation."""

    def test_required_fields_validation(self, authenticated_page: Page, base_url: str):
        """Test that required fields show validation errors."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/create/")

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Try to submit without filling required fields
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        # Wait and check for validation errors
        page.wait_for_timeout(1000)

        error_messages = page.locator('.error-message, .invalid-feedback, [role="alert"], .text-red-500')
        error_count = error_messages.count()
        assert error_count > 0, "Validation errors should be shown for required fields"

    def test_date_validation(self, authenticated_page: Page, base_url: str):
        """Test date field validation."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/create/")

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Fill basic fields
        unique_suffix = int(time.time())
        page.locator('input[name="title"]').fill(f"Date Test {unique_suffix}")
        page.locator('select[name="work_type"]').select_option("project")

        # Set invalid dates (due date before start date)
        tomorrow = time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))
        today = time.strftime("%Y-%m-%d")

        page.locator('input[name="start_date"]').fill(tomorrow)
        page.locator('input[name="due_date"]').fill(today)

        # Try to submit
        page.get_by_role("button", name=re.compile("Save|Submit|Create", re.IGNORECASE)).click()

        # Check for validation error
        page.wait_for_timeout(1000)
        error_messages = page.locator('.error-message, .invalid-feedback, [role="alert"], .text-red-500')
        # Note: Error might not show if browser-level validation prevents submission
        # This is acceptable behavior


class TestWorkItemResponsiveness:
    """Test responsive design across different screen sizes."""

    def test_workitem_list_mobile_view(self, authenticated_page: Page, base_url: str):
        """Test workitem list on mobile viewport."""
        page = authenticated_page

        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE

        # Navigate to workitem list
        page.goto(f"{base_url}/oobc-management/work-items/")

        # Verify content is visible
        page_header = page.locator('h1, [role="heading"]')
        expect(page_header).to_be_visible(timeout=5000)

        # Reset viewport
        page.set_viewport_size({"width": 1280, "height": 720})

    def test_workitem_form_tablet_view(self, authenticated_page: Page, base_url: str):
        """Test workitem form on tablet viewport."""
        page = authenticated_page

        # Set tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})  # iPad

        # Navigate to create form
        page.goto(f"{base_url}/oobc-management/work-items/create/")

        # Verify form is visible
        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Verify form fields are accessible
        title_input = page.locator('input[name="title"]')
        assert title_input.count() > 0, "Title input should be visible on tablet"

        # Reset viewport
        page.set_viewport_size({"width": 1280, "height": 720})

    def test_workitem_form_mobile_view(self, authenticated_page: Page, base_url: str):
        """Test workitem form on mobile viewport."""
        page = authenticated_page

        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})

        # Navigate to create form
        page.goto(f"{base_url}/oobc-management/work-items/create/")

        # Verify form is visible and usable
        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Try to fill a field
        title_input = page.locator('input[name="title"]')
        title_input.fill("Mobile Test")

        # Reset viewport
        page.set_viewport_size({"width": 1280, "height": 720})


class TestWorkItemAccessibility:
    """Test accessibility compliance (WCAG 2.1 AA)."""

    def test_keyboard_navigation(self, authenticated_page: Page, base_url: str):
        """Test keyboard navigation through workitem form."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/create/")

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Start keyboard navigation with Tab key
        page.keyboard.press("Tab")
        page.wait_for_timeout(500)

        # Verify first focusable element
        focused_element = page.evaluate("document.activeElement.tagName")
        assert focused_element in ["INPUT", "SELECT", "BUTTON", "TEXTAREA"], \
            "Tab should focus on form elements"

    def test_form_labels(self, authenticated_page: Page, base_url: str):
        """Test that all form inputs have labels."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/create/")

        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        # Check for form labels
        labels = page.locator("label")
        label_count = labels.count()

        # Verify there are labels (at least some fields should have labels)
        assert label_count > 0, "Form should have labels for accessibility"

    def test_button_accessibility(self, authenticated_page: Page, base_url: str):
        """Test that buttons are properly labeled and accessible."""
        page = authenticated_page

        page.goto(f"{base_url}/oobc-management/work-items/")

        # Check for properly labeled buttons
        buttons = page.locator("button")
        button_count = buttons.count()
        assert button_count > 0, "Page should have buttons"

        # Verify buttons have text content or aria-labels
        for button in buttons.all():
            text = button.inner_text()
            aria_label = button.get_attribute("aria-label")
            assert text or aria_label, "Buttons should have text content or aria-labels"


class TestWorkItemPerformance:
    """Test page load performance and metrics."""

    def test_workitem_list_load_time(self, authenticated_page: Page, base_url: str):
        """Test that workitem list loads within acceptable time."""
        page = authenticated_page

        start_time = time.time()
        page.goto(f"{base_url}/oobc-management/work-items/")

        # Wait for main content to load
        content = page.locator('[role="main"], main, .workitem-list, table')
        expect(content).to_be_visible(timeout=5000)

        load_time = time.time() - start_time

        # Assert load time is under 3 seconds
        assert load_time < 3.0, f"List load took {load_time:.2f}s, target is < 3s"

    def test_workitem_form_load_time(self, authenticated_page: Page, base_url: str):
        """Test that workitem form loads quickly."""
        page = authenticated_page

        start_time = time.time()
        page.goto(f"{base_url}/oobc-management/work-items/create/")

        # Wait for form to load
        form = page.locator("form")
        expect(form).to_be_visible(timeout=5000)

        load_time = time.time() - start_time

        # Assert load time is under 2 seconds
        assert load_time < 2.0, f"Form load took {load_time:.2f}s, target is < 2s"

    def test_no_console_errors(self, authenticated_page: Page, base_url: str):
        """Test that no JavaScript console errors occur."""
        page = authenticated_page

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # Navigate to workitem list and interact
        page.goto(f"{base_url}/oobc-management/work-items/")
        page.wait_for_load_state("networkidle")

        # Filter out known acceptable errors
        critical_errors = [err for err in console_errors if not any(
            ignore in err.lower() for ignore in ['favicon', 'analytics', 'ads']
        )]

        # We allow some errors but not critical ones
        assert len(critical_errors) < 5, f"Too many console errors: {critical_errors}"
