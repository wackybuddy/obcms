"""Component tests for organizations management commands."""

import pytest

try:
    from django.core.management import call_command
except ImportError:  # pragma: no cover
    pytest.skip(
        "Django is required for organizations management command tests",
        allow_module_level=True,
    )

from organizations.models import Organization

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_ensure_default_organization_command_creates_organization():
    """Command creates OOBC default organization when missing."""
    Organization.objects.all().delete()

    call_command("ensure_default_organization")

    assert Organization.objects.filter(code="OOBC").exists()
    org = Organization.objects.get(code="OOBC")
    assert org.id is not None
    assert org.code == "OOBC"


@pytest.mark.django_db
def test_ensure_default_organization_command_is_idempotent():
    """Command is safe to run multiple times."""
    Organization.objects.all().delete()

    call_command("ensure_default_organization")
    org_id_first = Organization.objects.get(code="OOBC").id

    call_command("ensure_default_organization")
    org_id_second = Organization.objects.get(code="OOBC").id

    assert org_id_first == org_id_second
    assert Organization.objects.filter(code="OOBC").count() == 1


@pytest.mark.django_db
def test_ensure_default_organization_command_exit_code_success():
    """Command exits without raising exception."""
    try:
        call_command("ensure_default_organization")
        # If we get here, no exception was raised - success
        assert True
    except Exception as e:
        pytest.fail(f"Command raised exception: {e}")


@pytest.mark.django_db
def test_seed_organizations_command_creates_records():
    """seed_organizations command creates organization records."""
    Organization.objects.all().delete()

    call_command("seed_organizations")

    # Should create at least one organization
    assert Organization.objects.count() > 0


@pytest.mark.django_db
def test_ensure_oobc_organization_command():
    """ensure_oobc_organization command creates OOBC org."""
    Organization.objects.all().delete()

    call_command("ensure_oobc_organization")

    # Should create OOBC organization
    assert Organization.objects.filter(code="OOBC").exists()
