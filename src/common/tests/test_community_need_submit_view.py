"""Tests for the community need submission workflow."""

from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from common.models import Region, Province, Municipality, Barangay
from communities.models import OBCCommunity
from mana.models import Need, NeedsCategory


class CommunityNeedSubmitViewTests(TestCase):
    """Ensure community leaders can submit needs and see their history."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="community_lead",
            email="lead@example.com",
            password="strong-pass-123",
        )
        self.client.force_login(self.user)

        self.region = Region.objects.create(code="R12", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="R12-COT",
            name="Cotabato",
            is_active=True,
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="R12-COT-001",
            name="Kidapawan City",
            municipality_type="city",
            is_active=True,
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="R12-COT-001-001",
            name="Poblacion",
            is_active=True,
        )
        self.community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Poblacion Bangsamoro Community",
        )
        self.category = NeedsCategory.objects.create(
            name="Livelihood Support",
            sector="economic_development",
            description="Support for livelihood restoration",
            icon="fas fa-briefcase",
            color="#059669",
        )

    def test_get_renders_form(self):
        """GET request should render the submission form successfully."""

        response = self.client.get(reverse("common:community_need_submit"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertContains(response, "Submit a Community Need")

    def test_post_creates_community_submitted_need(self):
        """Submitting valid data should persist a community-submitted need."""

        payload = {
            "title": "Post-harvest facility support",
            "description": "Local farmers require milling equipment to reduce losses.",
            "community": str(self.community.id),
            "category": str(self.category.id),
            "geographic_scope": "Barangay Poblacion",
            "affected_population": "250",
            "affected_households": "50",
            "urgency_level": "short_term",
            "impact_severity": "4",
            "feasibility": "high",
            "estimated_cost": "500000",
            "evidence_sources": "Community consultations held on %s"
            % date.today().isoformat(),
        }

        response = self.client.post(
            reverse("common:community_need_submit"), data=payload
        )

        self.assertRedirects(response, reverse("common:community_needs_summary"))
        need = Need.objects.get(title="Post-harvest facility support")
        self.assertEqual(need.submission_type, "community_submitted")
        self.assertEqual(need.submitted_by_user, self.user)
        self.assertEqual(need.identified_by, self.user)
        self.assertEqual(need.community, self.community)
        self.assertEqual(need.category, self.category)
        self.assertEqual(need.affected_population, 250)
        self.assertEqual(need.impact_severity, 4)
        self.assertEqual(need.feasibility, "high")
        self.assertIsNotNone(need.priority_score)
        self.assertEqual(need.status, "identified")
        self.assertIsNotNone(need.submission_date)
