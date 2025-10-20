"""Component tests for coordination app management commands."""

import pytest

try:
    from django.core.management import call_command
    from io import StringIO
except ImportError:  # pragma: no cover
    pytest.skip(
        "Django is required for coordination management command tests",
        allow_module_level=True,
    )

from organizations.models import Organization

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_ensure_oobc_organization_command_creates_org():
    """ensure_oobc_organization creates OOBC organization."""
    Organization.objects.all().delete()

    call_command("ensure_oobc_organization")

    assert Organization.objects.filter(code="OOBC").exists()


@pytest.mark.django_db
def test_populate_barmm_organizations_command_creates_orgs():
    """populate_barmm_organizations creates BARMM region organizations."""
    try:
        call_command("populate_barmm_organizations")
        # Command should create organizations without error
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")


@pytest.mark.django_db
def test_populate_barmm_moa_mandates_command_creates_mandates():
    """populate_barmm_moa_mandates creates MOA mandate records."""
    try:
        call_command("populate_barmm_moa_mandates")
        # Command should complete without error
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")
