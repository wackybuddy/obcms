"""Accuracy checks for Region XII location metadata."""

from unittest import SkipTest

from django.test import TestCase

from common.models import Barangay, Municipality, Region
from common.services.locations import build_location_data


class RegionXIILocationDataTests(TestCase):
    """Validate that Region XII centroid data is present and plausible."""

    @classmethod
    def setUpTestData(cls):
        try:
            cls.region = Region.objects.get(code="XII")
        except Region.DoesNotExist as error:
            raise SkipTest("Region XII seed data is not available") from error
        cls.location_data = build_location_data()
        cls.municipality_lookup = {
            payload["id"]: payload for payload in cls.location_data["municipalities"]
        }
        cls.barangay_lookup = {
            payload["id"]: payload for payload in cls.location_data.get("barangays", [])
        }

    def test_all_region_xii_municipalities_have_plausible_coordinates(self):
        municipalities = Municipality.objects.filter(province__region=self.region)

        self.assertTrue(municipalities.exists())

        for municipality in municipalities:
            payload = self.municipality_lookup.get(municipality.id)
            self.assertIsNotNone(
                payload, msg=f"Missing location payload for {municipality}"
            )
            self._assert_coordinate_payload(municipality.full_path, payload)

    def test_all_region_xii_barangays_have_plausible_coordinates(self):
        barangays = Barangay.objects.filter(municipality__province__region=self.region)

        self.assertTrue(barangays.exists())

        for barangay in barangays:
            payload = self.barangay_lookup.get(barangay.id)
            self.assertIsNotNone(
                payload, msg=f"Missing location payload for {barangay}"
            )
            self._assert_coordinate_payload(barangay.full_path, payload)

    def _assert_coordinate_payload(self, label, payload):
        lat = payload.get("center_lat")
        lng = payload.get("center_lng")

        self.assertIsNotNone(lat, msg=f"Latitude missing for {label}")
        self.assertIsNotNone(lng, msg=f"Longitude missing for {label}")

        # Region XII (SOCCSKSARGEN) spans approximately 4°N–8.5°N, 123°E–126.5°E.
        self.assertGreaterEqual(lat, 4.0, msg=f"Latitude out of range for {label}")
        self.assertLessEqual(lat, 8.5, msg=f"Latitude out of range for {label}")
        self.assertGreaterEqual(lng, 123.0, msg=f"Longitude out of range for {label}")
        self.assertLessEqual(lng, 126.5, msg=f"Longitude out of range for {label}")
