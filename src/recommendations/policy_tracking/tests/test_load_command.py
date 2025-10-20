"""Tests for the load_oobc_policy_recommendations management command."""

import pytest

try:
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for policy tracking command tests",
        allow_module_level=True,
    )

from recommendations.policy_tracking.models import PolicyRecommendation

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_command_creates_default_recommendations():
    """Ensure the management command seeds baseline records."""
    User = get_user_model()
    user = User.objects.create_superuser(
        username="policy_admin",
        email="policy-admin@example.com",
        password="super-secret",
    )

    call_command("load_oobc_policy_recommendations")

    assert PolicyRecommendation.objects.count() == 10

    sample = PolicyRecommendation.objects.get(reference_number="OOBC-REC-001")
    assert sample.proposed_by == user
    assert sample.status == "draft"
    assert sample.description
