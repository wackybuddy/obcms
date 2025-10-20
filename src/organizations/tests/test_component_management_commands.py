"""Component tests for organizations management commands."""

import pytest

try:
    from django.core.management import call_command
    from django.test import TestCase
except ImportError:  # pragma: no cover
    pytest.skip(
        "Django is required for organizations management command tests",
        allow_module_level=True,
    )

from organizations.models import Organization

pytestmark = pytest.mark.component


class EnsureDefaultOrganizationCommandTests(TestCase):
    """Test the ensure_default_organization management command."""

    def test_command_creates_default_organization(self):
        """Command creates OOBC default organization when missing."""
        Organization.objects.all().delete()

        call_command("ensure_default_organization")

        self.assertTrue(Organization.objects.filter(code="OOBC").exists())
        org = Organization.objects.get(code="OOBC")
        self.assertIsNotNone(org.id)
        self.assertEqual(org.code, "OOBC")

    def test_command_is_idempotent(self):
        """Command is safe to run multiple times."""
        Organization.objects.all().delete()

        call_command("ensure_default_organization")
        org_id_first = Organization.objects.get(code="OOBC").id

        call_command("ensure_default_organization")
        org_id_second = Organization.objects.get(code="OOBC").id

        self.assertEqual(org_id_first, org_id_second)
        self.assertEqual(Organization.objects.filter(code="OOBC").count(), 1)

    def test_command_exit_code_success(self):
        """Command exits with code 0 on success."""
        try:
            call_command("ensure_default_organization")
            # If we get here, no exception was raised - success
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Command raised exception: {e}")


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
