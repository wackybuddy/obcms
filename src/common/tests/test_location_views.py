"""Tests for location-related helper endpoints."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from common.models import Region


class LocationCentroidViewTests(TestCase):
    """Ensure the centroid lookup endpoint returns stored coordinates."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="centroid-tester",
            email="tester@example.com",
            password="password123",
        )
        self.client.login(username="centroid-tester", password="password123")

    def test_returns_existing_coordinates(self):
        region = Region.objects.create(
            code="ZZ",
            name="Test Region",
            center_coordinates=[120.123456, 7.654321],
        )

        url = reverse("common:location_centroid")
        response = self.client.get(url, {"level": "region", "id": region.id})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["has_location"])
        self.assertAlmostEqual(payload["lat"], 7.654321)
        self.assertAlmostEqual(payload["lng"], 120.123456)
        self.assertEqual(payload["source"], "cached")

    def test_geocodes_when_coordinates_missing(self):
        region = Region.objects.create(
            code="XY",
            name="Another Region",
        )

        url = reverse("common:location_centroid")

        with patch(
            "common.views.communities.enhanced_ensure_location_coordinates",
            return_value=(7.100001, 123.456789, True, "arcgis"),
        ) as mocked_geocode:
            response = self.client.get(url, {"level": "region", "id": region.id})

        mocked_geocode.assert_called_once_with(region)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["has_location"])
        self.assertAlmostEqual(payload["lat"], 7.100001)
        self.assertAlmostEqual(payload["lng"], 123.456789)
        self.assertEqual(payload["source"], "arcgis")
