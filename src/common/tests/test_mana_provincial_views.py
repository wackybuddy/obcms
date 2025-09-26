"""Regression tests for MANA provincial overview and card detail views."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity
from mana.models import Assessment, AssessmentCategory, MANAReport, Need, NeedsCategory


class ProvincialViewTests(TestCase):
    """Ensure provincial overview filtering and detail pages behave as expected."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="provincial_tester",
            email="tester@example.com",
            password="strong-password",
        )
        self.client.force_login(self.user)

        self.region = Region.objects.create(code="R11", name="Davao Region")
        self.province = Province.objects.create(
            region=self.region,
            code="R11-DDS",
            name="Davao del Sur",
            is_active=True,
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="R11-DDS-DIG",
            name="Digos City",
            municipality_type="city",
            is_active=True,
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="R11-DDS-DIG-001",
            name="San Jose",
            is_active=True,
        )
        self.community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="San Jose OBC",
        )

        self.assessment_category = AssessmentCategory.objects.create(
            name="Provincial Workshop",
            category_type="needs_assessment",
            description="Test category",
            icon="fas fa-users",
            color="#0052cc",
        )
        self.needs_category = NeedsCategory.objects.create(
            name="Water and Sanitation",
            sector="social_development",
            description="Access to clean water and sanitation facilities",
            icon="fas fa-tint",
            color="#10b981",
        )

        self.assessment = Assessment.objects.create(
            title="Provincial Rapid Assessment",
            category=self.assessment_category,
            description="Initial scan of priority areas",
            objectives="Catalogue immediate support requirements",
            assessment_level="provincial",
            primary_methodology="survey",
            community=self.community,
            status="planning",
            priority="high",
            planned_start_date=date.today(),
            planned_end_date=date.today(),
            lead_assessor=self.user,
            created_by=self.user,
        )

        self.need = Need.objects.create(
            title="Potable Water Access",
            description="Communities require additional potable water sources.",
            category=self.needs_category,
            assessment=self.assessment,
            community=self.community,
            affected_population=150,
            affected_households=30,
            geographic_scope="Barangay-wide",
            urgency_level="immediate",
            impact_severity=4,
            feasibility="high",
            status="validated",
            evidence_sources="Community consultation notes",
            identified_by=self.user,
            is_validated=True,
        )

        self.report = MANAReport.objects.create(
            assessment=self.assessment,
            title="Provincial Assessment Report",
            report_status="final",
            created_by=self.user,
        )

    def test_overview_default_listing(self):
        """Default view should list active provinces with aggregated metrics."""

        response = self.client.get(reverse("common:mana_provincial_overview"))

        self.assertEqual(response.status_code, 200)
        province_rows = response.context["province_rows"]
        self.assertEqual(len(province_rows), 1)
        self.assertEqual(province_rows[0]["province"], self.province)
        self.assertEqual(response.context["province_count"], 1)
        self.assertEqual(response.context["page_size"], 5)
        self.assertIsNotNone(response.context["province_page"])
        self.assertTrue(response.context["selection_active"])
        self.assertEqual(response.context["global_stats"]["total_assessments"], 1)

    def test_overview_filters_by_region_and_search(self):
        """Region and search filters should refine the provincial listing."""

        other_region = Region.objects.create(code="R12", name="SOCCSKSARGEN")
        Province.objects.create(
            region=other_region,
            code="R12-TST",
            name="Test Province",
            is_active=True,
        )

        response = self.client.get(
            reverse("common:mana_provincial_overview"),
            {"region": self.region.id, "search": "Davao"},
        )

        self.assertEqual(response.status_code, 200)
        province_rows = response.context["province_rows"]
        self.assertEqual(len(province_rows), 1)
        self.assertEqual(province_rows[0]["province"].name, "Davao del Sur")
        self.assertEqual(response.context["province_count"], 1)

    def test_overview_respects_page_size_and_pagination(self):
        """Page size selector should limit rows and expose additional pages."""

        for index in range(1, 7):
            Province.objects.create(
                region=self.region,
                code=f"R11-ADD-{index}",
                name=f"Additional Province {index}",
                is_active=True,
            )

        response = self.client.get(
            reverse("common:mana_provincial_overview"),
            {"page_size": 5},
        )

        self.assertEqual(response.status_code, 200)
        page_obj = response.context["province_page"]
        self.assertIsNotNone(page_obj)
        self.assertEqual(page_obj.paginator.count, 7)
        self.assertEqual(len(response.context["province_rows"]), 5)
        self.assertTrue(page_obj.has_next())

        response_page_two = self.client.get(
            reverse("common:mana_provincial_overview"),
            {"page_size": 5, "page": 2},
        )

        self.assertEqual(response_page_two.status_code, 200)
        second_page = response_page_two.context["province_page"]
        self.assertEqual(second_page.number, 2)
        self.assertEqual(len(response_page_two.context["province_rows"]), 2)

    def test_provincial_card_detail_view(self):
        """Detail page should surface metrics, needs, and assessments for the province."""

        response = self.client.get(
            reverse("common:mana_provincial_card_detail", args=[self.province.id])
        )

        self.assertEqual(response.status_code, 200)
        card = response.context["card"]
        self.assertEqual(card["province"], self.province)
        self.assertEqual(card["assessments"]["total"], 1)
        self.assertIn(self.assessment, response.context["detailed_assessments"])
        self.assertIn(self.need, response.context["critical_needs"])
        self.assertIn(self.report, response.context["latest_reports"])

    def test_province_edit_updates_records(self):
        """Editing a province should persist the provided fields."""

        url = reverse("common:mana_province_edit", args=[self.province.id])
        response = self.client.post(
            url,
            {
                "code": "R11-EDIT",
                "name": "Davao del Sur (Updated)",
                "capital": "Digos",
                "population_total": 12345,
                "is_active": True,
                "next": reverse("common:mana_provincial_overview"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.province.refresh_from_db()
        self.assertEqual(self.province.code, "R11-EDIT")
        self.assertEqual(self.province.name, "Davao del Sur (Updated)")
        self.assertEqual(self.province.population_total, 12345)

    def test_province_delete_sets_inactive(self):
        """Deleting via the management view should archive the province."""

        url = reverse("common:mana_province_delete", args=[self.province.id])
        response = self.client.post(
            url,
            {"next": reverse("common:mana_provincial_overview")},
        )

        self.assertEqual(response.status_code, 302)
        self.province.refresh_from_db()
        self.assertFalse(self.province.is_active)
