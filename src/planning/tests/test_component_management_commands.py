"""Component tests for planning app management commands."""

import pytest

try:
    from django.core.management import call_command
    from io import StringIO
except ImportError:  # pragma: no cover
    pytest.skip(
        "Django is required for planning management command tests",
        allow_module_level=True,
    )

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_generate_sample_programs_command_runs():
    """generate_sample_programs command executes successfully."""
    try:
        out = StringIO()
        call_command("generate_sample_programs", stdout=out)
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")
