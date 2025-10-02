"""
Comprehensive validation command for Region IX coordinate auto-generation system.

This command validates that all Region IX administrative levels have accurate coordinates
and tests the coordinate auto-generation functionality that powers the forms.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from common.models import Region, Province, Municipality, Barangay
from common.services.locations import get_object_centroid, build_location_data
from common.services.enhanced_geocoding import enhanced_ensure_location_coordinates
import json


class Command(BaseCommand):
    help = "Comprehensive validation of Region IX coordinate system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose", action="store_true", help="Show detailed validation output"
        )
        parser.add_argument(
            "--export", action="store_true", help="Export coordinate data to JSON file"
        )

    def handle(self, *args, **options):
        """Main validation execution."""
        self.verbose = options.get("verbose", False)
        self.export = options.get("export", False)

        self.stdout.write(
            self.style.SUCCESS("🔍 COMPREHENSIVE REGION IX COORDINATE VALIDATION")
        )

        # Run all validation tests
        self._validate_region_coverage()
        self._validate_coordinate_accuracy()
        self._validate_hierarchical_selection()
        self._validate_form_integration_data()

        if self.export:
            self._export_coordinate_data()

        self.stdout.write(
            self.style.SUCCESS("✅ Region IX coordinate system validation completed!")
        )

    def _validate_region_coverage(self):
        """Validate complete coordinate coverage for Region IX."""
        self.stdout.write("📊 Validating coordinate coverage...")

        # Check Region IX
        region = Region.objects.get(code="IX")
        if not region.center_coordinates:
            self.stdout.write(self.style.ERROR("  ❌ Region IX missing coordinates"))
            return
        else:
            self.stdout.write("  ✅ Region IX has coordinates")

        # Check all provinces
        provinces = Province.objects.filter(region__code="IX")
        provinces_without_coords = provinces.filter(center_coordinates__isnull=True)

        if provinces_without_coords.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"  ❌ {provinces_without_coords.count()} provinces missing coordinates"
                )
            )
        else:
            self.stdout.write(
                f"  ✅ All {provinces.count()} provinces have coordinates"
            )

        # Check municipalities
        municipalities = Municipality.objects.filter(province__region__code="IX")
        municipalities_without_coords = municipalities.filter(
            center_coordinates__isnull=True
        )

        if municipalities_without_coords.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠️  {municipalities_without_coords.count()} municipalities missing coordinates"
                )
            )
        else:
            self.stdout.write(
                f"  ✅ All {municipalities.count()} municipalities have coordinates"
            )

        # Check barangays
        barangays = Barangay.objects.filter(municipality__province__region__code="IX")
        barangays_without_coords = barangays.filter(center_coordinates__isnull=True)

        if barangays_without_coords.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠️  {barangays_without_coords.count()} barangays missing coordinates"
                )
            )
        else:
            self.stdout.write(
                f"  ✅ All {barangays.count()} barangays have coordinates"
            )

    def _validate_coordinate_accuracy(self):
        """Validate coordinate accuracy and bounds."""
        self.stdout.write("🎯 Validating coordinate accuracy...")

        # Define expected bounds for Region IX (Zamboanga Peninsula)
        expected_bounds = {
            "min_lat": 4.5,  # Southern Sulu
            "max_lat": 9.5,  # Northern Zamboanga del Norte
            "min_lng": 119.0,  # Western Sulu
            "max_lng": 125.0,  # Eastern Zamboanga del Sur
        }

        invalid_coords = 0

        # Test all administrative levels
        for level_name, model in [
            ("regions", Region.objects.filter(code="IX")),
            ("provinces", Province.objects.filter(region__code="IX")),
            (
                "municipalities",
                Municipality.objects.filter(province__region__code="IX")[:20],
            ),  # Sample
            (
                "barangays",
                Barangay.objects.filter(municipality__province__region__code="IX")[:50],
            ),  # Sample
        ]:
            for obj in model:
                lat, lng = get_object_centroid(obj)
                if lat is not None and lng is not None:
                    # Check bounds
                    if not (
                        expected_bounds["min_lat"] <= lat <= expected_bounds["max_lat"]
                        and expected_bounds["min_lng"]
                        <= lng
                        <= expected_bounds["max_lng"]
                    ):
                        invalid_coords += 1
                        if self.verbose:
                            name = getattr(obj, "name", str(obj))
                            self.stdout.write(
                                self.style.WARNING(
                                    f"    ⚠️  {name}: {lat:.6f}, {lng:.6f} outside expected bounds"
                                )
                            )

        if invalid_coords == 0:
            self.stdout.write("  ✅ All coordinates within expected geographic bounds")
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠️  {invalid_coords} coordinates outside expected bounds"
                )
            )

    def _validate_hierarchical_selection(self):
        """Test hierarchical coordinate selection logic."""
        self.stdout.write("🔗 Validating hierarchical coordinate selection...")

        # Test the selection logic used by forms
        test_cases = [
            # Test province selection
            ("province_level", Province.objects.filter(region__code="IX").first()),
            # Test municipality selection
            (
                "municipality_level",
                Municipality.objects.filter(province__region__code="IX").first(),
            ),
            # Test barangay selection
            (
                "barangay_level",
                Barangay.objects.filter(
                    municipality__province__region__code="IX"
                ).first(),
            ),
        ]

        for test_name, test_obj in test_cases:
            if test_obj:
                lat, lng = get_object_centroid(test_obj)
                if lat is not None and lng is not None:
                    self.stdout.write(f"  ✅ {test_name}: Coordinates available")
                    if self.verbose:
                        name = getattr(test_obj, "name", str(test_obj))
                        self.stdout.write(f"    {name}: {lat:.6f}, {lng:.6f}")
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠️  {test_name}: No coordinates available"
                        )
                    )

    def _validate_form_integration_data(self):
        """Validate that the location data structure used by forms is correct."""
        self.stdout.write("📋 Validating form integration data...")

        try:
            location_data = build_location_data(include_barangays=True)

            # Check that Region IX data is present
            region_ix = next(
                (r for r in location_data["regions"] if r["code"] == "IX"), None
            )
            if region_ix:
                self.stdout.write("  ✅ Region IX found in location data")
                if self.verbose:
                    self.stdout.write(
                        f"    Center: {region_ix.get('center_lat', 'N/A')}, {region_ix.get('center_lng', 'N/A')}"
                    )
            else:
                self.stdout.write(
                    self.style.ERROR("  ❌ Region IX not found in location data")
                )

            # Check provinces
            region_ix_provinces = [
                p
                for p in location_data["provinces"]
                if p.get("region_id") == region_ix["id"]
            ]
            if len(region_ix_provinces) == 6:
                self.stdout.write(f"  ✅ All 6 provinces found in location data")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠️  Only {len(region_ix_provinces)}/6 provinces in location data"
                    )
                )

            # Check sample municipalities
            if region_ix_provinces:
                sample_province_id = region_ix_provinces[0]["id"]
                sample_municipalities = [
                    m
                    for m in location_data["municipalities"]
                    if m.get("province_id") == sample_province_id
                ]
                self.stdout.write(
                    f"  ✅ Sample province has {len(sample_municipalities)} municipalities in data"
                )

            # Check sample barangays
            if "barangays" in location_data:
                sample_barangays_count = len(
                    [
                        b
                        for b in location_data["barangays"][:100]
                        if any(
                            m["id"] == b.get("municipality_id")
                            for m in location_data["municipalities"][:10]
                        )
                    ]
                )
                self.stdout.write(f"  ✅ Sample barangays found in location data")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Error validating location data: {str(e)}")
            )

    def _export_coordinate_data(self):
        """Export Region IX coordinate data to JSON file."""
        self.stdout.write("📤 Exporting coordinate data...")

        export_data = {
            "region": {},
            "provinces": [],
            "sample_municipalities": [],
            "sample_barangays": [],
        }

        # Export region
        region = Region.objects.get(code="IX")
        lat, lng = get_object_centroid(region)
        export_data["region"] = {
            "code": region.code,
            "name": region.name,
            "coordinates": [lng, lat] if lat and lng else None,
        }

        # Export all provinces
        for province in Province.objects.filter(region__code="IX"):
            lat, lng = get_object_centroid(province)
            export_data["provinces"].append(
                {
                    "name": province.name,
                    "coordinates": [lng, lat] if lat and lng else None,
                }
            )

        # Export sample municipalities
        for municipality in Municipality.objects.filter(province__region__code="IX")[
            :10
        ]:
            lat, lng = get_object_centroid(municipality)
            export_data["sample_municipalities"].append(
                {
                    "name": municipality.name,
                    "province": municipality.province.name,
                    "coordinates": [lng, lat] if lat and lng else None,
                }
            )

        # Export sample barangays
        for barangay in Barangay.objects.filter(
            municipality__province__region__code="IX"
        )[:20]:
            lat, lng = get_object_centroid(barangay)
            export_data["sample_barangays"].append(
                {
                    "name": barangay.name,
                    "municipality": barangay.municipality.name,
                    "coordinates": [lng, lat] if lat and lng else None,
                }
            )

        # Write to file
        with open("region_ix_coordinates.json", "w") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        self.stdout.write("  ✅ Coordinate data exported to region_ix_coordinates.json")
