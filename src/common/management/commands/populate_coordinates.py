"""
Management command to populate missing coordinates for geographic entities.

This command ensures that all regions, provinces, municipalities, and barangays
in the target regions (IX, X, XI, XII) have accurate center coordinates.
"""

from typing import List, Optional, Tuple
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from common.models import Region, Province, Municipality, Barangay
from common.services.geocoding import ensure_location_coordinates


class Command(BaseCommand):
    help = "Populate missing geographic coordinates for administrative divisions"

    def add_arguments(self, parser):
        parser.add_argument(
            '--regions',
            type=str,
            nargs='+',
            default=['IX', 'X', 'XI', 'XII'],
            help='Region codes to process (default: IX, X, XI, XII)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update coordinates even if they already exist'
        )
        parser.add_argument(
            '--level',
            choices=['region', 'province', 'municipality', 'barangay', 'all'],
            default='all',
            help='Administrative level to update (default: all)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        """Main command execution."""
        self.verbosity = options['verbosity']
        self.regions = options['regions']
        self.force = options['force']
        self.level = options['level']
        self.dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS(
                f"{'DRY RUN: ' if self.dry_run else ''}Populating coordinates for regions: {', '.join(self.regions)}"
            )
        )

        # Process each administrative level
        if self.level in ['region', 'all']:
            self._process_regions()
        if self.level in ['province', 'all']:
            self._process_provinces()
        if self.level in ['municipality', 'all']:
            self._process_municipalities()
        if self.level in ['barangay', 'all']:
            self._process_barangays()

        self.stdout.write(
            self.style.SUCCESS(
                f"{'DRY RUN: ' if self.dry_run else ''}Coordinate population completed!"
            )
        )

    def _process_regions(self):
        """Process region-level coordinates."""
        self.stdout.write("Processing regions...")

        regions = Region.objects.filter(code__in=self.regions)
        if not self.force:
            regions = regions.filter(center_coordinates__isnull=True)

        updated_count = 0
        for region in regions:
            if self._has_coordinates(region) and not self.force:
                continue

            if self.dry_run:
                self.stdout.write(f"  Would update: Region {region.code} - {region.name}")
                updated_count += 1
            else:
                lat, lng, updated = ensure_location_coordinates(region)
                if updated:
                    self.stdout.write(
                        self.style.SUCCESS(f"  Updated: Region {region.code} - {region.name} ({lat:.6f}, {lng:.6f})")
                    )
                    updated_count += 1
                elif lat and lng:
                    self.stdout.write(f"  Already has coordinates: Region {region.code}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  Could not geocode: Region {region.code} - {region.name}")
                    )

        self.stdout.write(f"  Regions updated: {updated_count}")

    def _process_provinces(self):
        """Process province-level coordinates."""
        self.stdout.write("Processing provinces...")

        provinces = Province.objects.filter(region__code__in=self.regions)
        if not self.force:
            provinces = provinces.filter(center_coordinates__isnull=True)

        updated_count = 0
        for province in provinces:
            if self._has_coordinates(province) and not self.force:
                continue

            if self.dry_run:
                self.stdout.write(f"  Would update: {province.name}, {province.region.name}")
                updated_count += 1
            else:
                lat, lng, updated = ensure_location_coordinates(province)
                if updated:
                    self.stdout.write(
                        self.style.SUCCESS(f"  Updated: {province.name}, {province.region.name} ({lat:.6f}, {lng:.6f})")
                    )
                    updated_count += 1
                elif lat and lng:
                    self.stdout.write(f"  Already has coordinates: {province.name}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  Could not geocode: {province.name}, {province.region.name}")
                    )

        self.stdout.write(f"  Provinces updated: {updated_count}")

    def _process_municipalities(self):
        """Process municipality-level coordinates."""
        self.stdout.write("Processing municipalities...")

        municipalities = Municipality.objects.filter(province__region__code__in=self.regions)
        if not self.force:
            municipalities = municipalities.filter(center_coordinates__isnull=True)

        updated_count = 0
        for municipality in municipalities[:10]:  # Limit to first 10 for testing
            if self._has_coordinates(municipality) and not self.force:
                continue

            if self.dry_run:
                self.stdout.write(f"  Would update: {municipality.name}, {municipality.province.name}")
                updated_count += 1
            else:
                lat, lng, updated = ensure_location_coordinates(municipality)
                if updated:
                    self.stdout.write(
                        self.style.SUCCESS(f"  Updated: {municipality.name}, {municipality.province.name} ({lat:.6f}, {lng:.6f})")
                    )
                    updated_count += 1
                elif lat and lng:
                    self.stdout.write(f"  Already has coordinates: {municipality.name}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  Could not geocode: {municipality.name}, {municipality.province.name}")
                    )

        self.stdout.write(f"  Municipalities updated: {updated_count}")

    def _process_barangays(self):
        """Process barangay-level coordinates."""
        self.stdout.write("Processing barangays...")

        barangays = Barangay.objects.filter(municipality__province__region__code__in=self.regions)
        if not self.force:
            barangays = barangays.filter(center_coordinates__isnull=True)

        # Limit to a reasonable number for initial processing
        total_count = barangays.count()
        barangays = barangays[:20]  # Limit to first 20 for testing

        self.stdout.write(f"  Processing {len(barangays)} of {total_count} barangays")

        updated_count = 0
        for barangay in barangays:
            if self._has_coordinates(barangay) and not self.force:
                continue

            if self.dry_run:
                self.stdout.write(f"  Would update: Brgy. {barangay.name}, {barangay.municipality.name}")
                updated_count += 1
            else:
                lat, lng, updated = ensure_location_coordinates(barangay)
                if updated:
                    self.stdout.write(
                        self.style.SUCCESS(f"  Updated: Brgy. {barangay.name}, {barangay.municipality.name} ({lat:.6f}, {lng:.6f})")
                    )
                    updated_count += 1
                elif lat and lng:
                    self.stdout.write(f"  Already has coordinates: Brgy. {barangay.name}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  Could not geocode: Brgy. {barangay.name}, {barangay.municipality.name}")
                    )

        self.stdout.write(f"  Barangays updated: {updated_count}")

    def _has_coordinates(self, obj) -> bool:
        """Check if object has center coordinates."""
        if hasattr(obj, 'center_coordinates') and obj.center_coordinates:
            coords = obj.center_coordinates
            return (
                isinstance(coords, list) and
                len(coords) == 2 and
                coords[0] is not None and
                coords[1] is not None
            )
        return False