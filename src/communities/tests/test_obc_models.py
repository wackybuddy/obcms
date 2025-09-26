from django.test import TestCase

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity


class OBCCommunityModelTest(TestCase):
    """Behavioural checks for Barangay-level OBC community model helpers."""

    def setUp(self):
        self.region = Region.objects.create(code="R12", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-999",
            name="Test Province",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-999",
            name="Test Municipality",
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-999",
            name="Barangay Zone 1",
        )

    def test_save_normalises_community_names(self):
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Cluster Alpha",
            community_names="Legacy Name",
        )
        community.refresh_from_db()

        self.assertEqual(community.display_name, "Cluster Alpha")
        self.assertEqual(community.community_names, "Cluster Alpha, Legacy Name")

    def test_languages_spoken_derives_from_primary_and_other(self):
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Cluster Bravo",
            primary_language="Tausug",
            other_languages="Tagalog, English, Tausug",
        )
        community.refresh_from_db()

        self.assertEqual(community.languages_spoken, "Tausug, Tagalog, English")

    def test_full_location_appends_specific_location(self):
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Cluster Charlie",
            specific_location="Purok 7",
        )

        self.assertIn("Barangay Zone 1", community.full_location)
        self.assertTrue(community.full_location.endswith("Purok 7"))

    def test_soft_delete_and_restore_cycle(self):
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Cluster Delta",
        )

        self.assertTrue(OBCCommunity.objects.filter(pk=community.pk).exists())

        community.soft_delete()
        community.refresh_from_db()

        self.assertTrue(community.is_deleted)
        self.assertIsNotNone(community.deleted_at)
        self.assertFalse(OBCCommunity.objects.filter(pk=community.pk).exists())
        self.assertTrue(
            OBCCommunity.all_objects.filter(pk=community.pk, is_deleted=True).exists()
        )

        community.restore()
        community.refresh_from_db()

        self.assertFalse(community.is_deleted)
        self.assertIsNone(community.deleted_at)
        self.assertTrue(OBCCommunity.objects.filter(pk=community.pk).exists())
