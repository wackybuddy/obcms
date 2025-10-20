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

from organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_generate_sample_programs_command_runs():
    """generate_sample_programs command executes successfully."""
    # Create a test organization if one doesn't exist
    org, _ = Organization.objects.get_or_create(
        code="TEST",
        defaults={
            "name": "Test Organization",
            "org_type": "ministry",
        }
    )

    # Ensure at least one superuser exists
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )

    try:
        out = StringIO()
        call_command("generate_sample_programs", "--organization", org.code, stdout=out)
        assert True
    except Exception as e:
        pytest.fail(f"Command failed: {e}")
