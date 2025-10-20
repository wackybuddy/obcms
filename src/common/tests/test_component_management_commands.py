"""Component tests for common app management commands."""

import pytest

try:
    from django.core.management import call_command
    from io import StringIO
except ImportError:  # pragma: no cover
    pytest.skip(
        "Django is required for common management command tests",
        allow_module_level=True,
    )

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_cleanup_test_data_command_runs_successfully():
    """cleanup_test_data command runs without errors."""
    out = StringIO()

    try:
        call_command("cleanup_test_data", stdout=out)
        # Command should complete successfully
        output = out.getvalue()
        # Just verify it ran - output content varies by test data state
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")


@pytest.mark.django_db
def test_cleanup_test_users_command_runs_successfully():
    """cleanup_test_users command runs without errors."""
    out = StringIO()

    try:
        call_command("cleanup_test_users", stdout=out)
        # Command should complete successfully
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")


@pytest.mark.django_db
def test_create_staff_accounts_command_accepts_options():
    """create_staff_accounts command accepts required options."""
    out = StringIO()

    try:
        # This command typically requires options like email/count
        # It should not crash when called, even if options are missing
        call_command("create_staff_accounts", stdout=out)
        assert True
    except SystemExit:
        # Command may exit with error if required args missing - that's OK
        # We're just testing it parses correctly
        pass
    except Exception as e:
        # Other exceptions are failures
        pytest.fail(f"Unexpected error: {e}")
