from django.contrib.auth import get_user_model
from django.test import TestCase

from common.models import Barangay, Municipality, Province, Region

from ..models import MunicipalityCoverage, OBCCommunity
from ..serializers import MunicipalityCoverageSerializer

User = get_user_model()


class MunicipalityCoverageModelTest(TestCase):
    """Tests for the MunicipalityCoverage model helpers."""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
            municipality_type="municipality",
        )
        self.user = User.objects.create_user(
            username="encoder",
            password="testpass123",
            user_type="oobc_staff",
        )
        self.coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=3,
            estimated_obc_population=2500,
            key_barangays="Barangay A, Barangay B",
            created_by=self.user,
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.coverage),
            "Isulan Bangsamoro Coverage",
        )

    def test_region_and_province_properties(self):
        self.assertEqual(self.coverage.region, self.region)
        self.assertEqual(self.coverage.province, self.province)

    def test_display_name_property(self):
        self.assertEqual(
            self.coverage.display_name,
            "Isulan, Sultan Kudarat",
        )


class MunicipalityCoverageSerializerTest(TestCase):
    """Ensure the serializer exposes derived attributes."""

    def setUp(self):
        region = Region.objects.create(code="IX", name="Zamboanga Peninsula")
        province = Province.objects.create(
            region=region, code="PROV-002", name="Zamboanga City"
        )
        municipality = Municipality.objects.create(
            province=province,
            code="MUN-002",
            name="Zamboanga City",
            municipality_type="independent_city",
        )
        self.coverage = MunicipalityCoverage.objects.create(
            municipality=municipality,
            total_obc_communities=5,
            estimated_obc_population=5400,
            key_barangays="Barangay Baliwasan",
        )

    def test_serializer_output(self):
        serializer = MunicipalityCoverageSerializer(instance=self.coverage)
        data = serializer.data
        self.assertEqual(data["municipality_name"], "Zamboanga City")
        self.assertEqual(data["province_name"], "Zamboanga City")
        self.assertEqual(data["region_name"], "Zamboanga Peninsula")
        self.assertEqual(data["total_obc_communities"], 5)
        self.assertTrue(data["auto_sync"])


class MunicipalityCoverageSyncTest(TestCase):
    """Validate automatic aggregation between barangay communities and coverage."""

    def setUp(self):
        self.region = Region.objects.create(code="BAR", name="BARMM Edge")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-123",
            name="Test Province",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-123",
            name="Sample Municipality",
        )
        self.barangay_a = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay Uno",
        )
        self.barangay_b = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay Dos",
        )

    def test_coverage_created_and_updated_from_communities(self):
        # Initial community creation should spawn coverage automatically
        OBCCommunity.objects.create(
            barangay=self.barangay_a,
            community_names="Community A",
            estimated_obc_population=150,
            households=30,
            women_count=60,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertTrue(coverage.auto_sync)
        self.assertEqual(coverage.total_obc_communities, 1)
        self.assertEqual(coverage.estimated_obc_population, 150)
        self.assertEqual(coverage.households, 30)
        self.assertEqual(coverage.women_count, 60)
        self.assertIn("Barangay Uno", coverage.key_barangays)

        OBCCommunity.objects.create(
            barangay=self.barangay_b,
            community_names="Community B",
            estimated_obc_population=200,
            households=40,
            women_count=80,
        )

        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 2)
        self.assertEqual(coverage.estimated_obc_population, 350)
        self.assertEqual(coverage.households, 70)
        self.assertEqual(coverage.women_count, 140)
        self.assertIn("Barangay Dos", coverage.key_barangays)

        # Removing a community should resync totals
        coverage.auto_sync = True
        coverage.save(update_fields=["auto_sync"])
        OBCCommunity.objects.filter(barangay=self.barangay_a).delete()
        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 1)
        self.assertEqual(coverage.estimated_obc_population, 200)
        self.assertEqual(coverage.households, 40)
        self.assertEqual(coverage.women_count, 80)

    def test_auto_sync_can_be_disabled(self):
        OBCCommunity.objects.create(
            barangay=self.barangay_a,
            community_names="Community A",
            estimated_obc_population=120,
        )
        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        MunicipalityCoverage.objects.filter(pk=coverage.pk).update(
            auto_sync=False,
            total_obc_communities=99,
            estimated_obc_population=9999,
            key_barangays="Custom Entry",
        )
        coverage.refresh_from_db()
        self.assertFalse(coverage.auto_sync)

        OBCCommunity.objects.create(
            barangay=self.barangay_b,
            community_names="Community B",
            estimated_obc_population=80,
        )

        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 99)
        self.assertEqual(coverage.estimated_obc_population, 9999)
        self.assertEqual(coverage.key_barangays, "Custom Entry")
