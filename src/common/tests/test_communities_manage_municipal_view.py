from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.models import Municipality, Province, Region

from communities.models import MunicipalityCoverage


class ManageMunicipalStatCardsTests(TestCase):
    """Verify that the municipal management dashboard aggregates stat cards correctly."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="staffer",
            password="testpass123",
            user_type="oobc_staff",
        )
        self.client.force_login(self.user)
        self.region = Region.objects.create(code="BAR", name="BARMM Test Region")
        self.province = Province.objects.create(
            region=self.region, code="PROV-01", name="Test Province"
        )

    def _create_municipality(self, code, name):
        return Municipality.objects.create(
            province=self.province,
            code=code,
            name=name,
            municipality_type="municipality",
        )

    def test_stat_cards_present_expected_totals(self):
        MunicipalityCoverage.objects.create(
            municipality=self._create_municipality("MUN-001", "Alpha"),
            total_obc_communities=3,
            estimated_obc_population=1000,
            auto_sync=True,
        )
        MunicipalityCoverage.objects.create(
            municipality=self._create_municipality("MUN-002", "Bravo"),
            total_obc_communities=4,
            estimated_obc_population=2000,
            auto_sync=False,
        )
        MunicipalityCoverage.objects.create(
            municipality=self._create_municipality("MUN-003", "Charlie"),
            total_obc_communities=2,
            estimated_obc_population=1500,
            auto_sync=True,
        )

        response = self.client.get(reverse("common:communities_manage_municipal"))

        self.assertEqual(response.status_code, 200)

        stats = response.context["stats"]
        self.assertEqual(stats["total_coverages"], 3)
        self.assertEqual(stats["total_population"], 4500)
        self.assertEqual(stats["auto_synced"], 2)
        self.assertEqual(stats["manual"], 1)

        stat_cards = response.context["stat_cards"]
        values = [card["value"] for card in stat_cards]
        self.assertEqual(values, [3, 4500, 2, 1])
