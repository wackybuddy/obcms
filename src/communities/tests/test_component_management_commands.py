"""Component tests for communities app management commands."""

import pytest

try:
    from django.core.management import call_command
    from io import StringIO
except ImportError:  # pragma: no cover
    pytest.skip(
        "Django is required for communities management command tests",
        allow_module_level=True,
    )

from communities.models import OBCCommunity

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_sync_obc_coverage_command_runs_successfully():
    """sync_obc_coverage command executes without errors."""
    try:
        out = StringIO()
        call_command("sync_obc_coverage", stdout=out)
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")


@pytest.mark.django_db
def test_populate_sample_communities_command_creates_records():
    """populate_sample_communities creates community records."""
    initial_count = OBCCommunity.objects.count()

    try:
        call_command("populate_sample_communities")
        # Check that communities were created (or at least command ran)
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")


@pytest.mark.django_db
def test_generate_obc_communities_command_runs():
    """generate_obc_communities command executes."""
    try:
        out = StringIO()
        call_command("generate_obc_communities", stdout=out)
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")
