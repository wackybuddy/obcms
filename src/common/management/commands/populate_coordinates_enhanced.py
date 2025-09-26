"""Enhanced coordinate population using Google Maps API with Nominatim fallback."""

import time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from common.models import Region, Province, Municipality, Barangay
from common.services.enhanced_geocoding import enhanced_ensure_location_coordinates


class Command(BaseCommand):
    help = 'Populate coordinates using enhanced geocoding (Google Maps + Nominatim fallback)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--regions',
            nargs='+',
            help='Specify region codes to process (e.g., IX XII). If not specified, processes all regions.',
        )
        parser.add_argument(
            '--municipalities-only',
            action='store_true',
            help='Only populate municipality coordinates, skip barangays',
        )
        parser.add_argument(
            '--barangays-only',
            action='store_true',
            help='Only populate barangay coordinates, skip municipalities',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of records to process (for testing)',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.2,
            help='Delay between requests in seconds (default: 0.2 for Google API)',
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Update coordinates even if they already exist',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )

    def handle(self, *args, **options):
        regions = options.get('regions')
        municipalities_only = options.get('municipalities_only')
        barangays_only = options.get('barangays_only')
        limit = options.get('limit')
        delay = options.get('delay')
        force_update = options.get('force_update')
        dry_run = options.get('dry_run')

        if municipalities_only and barangays_only:
            raise CommandError("Cannot specify both --municipalities-only and --barangays-only")

        # Check if Google Maps API is configured
        google_api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        if google_api_key:
            self.stdout.write(self.style.SUCCESS('✓ Google Maps API configured - using enhanced geocoding'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Google Maps API not configured - will use Nominatim only'))

        # Filter regions if specified
        region_queryset = Region.objects.filter(is_active=True)
        if regions:
            region_queryset = region_queryset.filter(code__in=regions)

        self.stdout.write(self.style.SUCCESS(f'Processing regions: {list(region_queryset.values_list("code", flat=True))}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        total_processed = 0
        success_count = 0
        google_count = 0
        nominatim_count = 0
        cached_count = 0

        if not barangays_only:
            self.stdout.write(self.style.SUCCESS('\n=== Processing Municipalities ==='))
            for region in region_queryset:
                municipalities = Municipality.objects.filter(
                    province__region=region,
                    is_active=True
                ).select_related('province')

                if not force_update:
                    municipalities = municipalities.filter(center_coordinates__isnull=True)

                if limit:
                    municipalities = municipalities[:limit - total_processed]

                for municipality in municipalities:
                    if limit and total_processed >= limit:
                        break

                    if dry_run:
                        self.stdout.write(f'Would process: {municipality.name}, {municipality.province.name}')
                        total_processed += 1
                        continue

                    success, source = self.process_location(municipality, delay)
                    total_processed += 1

                    if success:
                        success_count += 1
                        if source == 'google':
                            google_count += 1
                        elif source == 'nominatim':
                            nominatim_count += 1
                        elif source == 'cached':
                            cached_count += 1

                        self.stdout.write(f'✓ {municipality.name}, {municipality.province.name} ({source})')
                    else:
                        self.stdout.write(self.style.WARNING(f'✗ Failed: {municipality.name}, {municipality.province.name}'))

                if limit and total_processed >= limit:
                    break

        if not municipalities_only:
            self.stdout.write(self.style.SUCCESS('\n=== Processing Barangays ==='))
            for region in region_queryset:
                barangays = Barangay.objects.filter(
                    municipality__province__region=region,
                    is_active=True
                ).select_related('municipality__province')

                if not force_update:
                    barangays = barangays.filter(center_coordinates__isnull=True)

                if limit:
                    remaining_limit = limit - total_processed
                    if remaining_limit <= 0:
                        break
                    barangays = barangays[:remaining_limit]

                for barangay in barangays:
                    if limit and total_processed >= limit:
                        break

                    if dry_run:
                        self.stdout.write(f'Would process: {barangay.name}, {barangay.municipality.name}')
                        total_processed += 1
                        continue

                    success, source = self.process_location(barangay, delay)
                    total_processed += 1

                    if success:
                        success_count += 1
                        if source == 'google':
                            google_count += 1
                        elif source == 'nominatim':
                            nominatim_count += 1
                        elif source == 'cached':
                            cached_count += 1

                        self.stdout.write(f'✓ {barangay.name}, {barangay.municipality.name} ({source})')
                    else:
                        self.stdout.write(self.style.WARNING(f'✗ Failed: {barangay.name}, {barangay.municipality.name}'))

                if limit and total_processed >= limit:
                    break

        # Summary report
        self.stdout.write(self.style.SUCCESS(f'\n=== SUMMARY ==='))
        if dry_run:
            self.stdout.write(f'Would process: {total_processed} locations')
        else:
            self.stdout.write(f'Total processed: {total_processed}')
            self.stdout.write(f'Successful: {success_count}')
            self.stdout.write(f'Failed: {total_processed - success_count}')
            if google_count > 0:
                self.stdout.write(self.style.SUCCESS(f'Google Maps: {google_count}'))
            if nominatim_count > 0:
                self.stdout.write(f'Nominatim: {nominatim_count}')
            if cached_count > 0:
                self.stdout.write(f'Cached: {cached_count}')

            if google_count > 0:
                estimated_cost = google_count * 0.005  # $0.005 per request after free tier
                self.stdout.write(f'Estimated Google API cost: ${estimated_cost:.2f} (after free tier)')

    def process_location(self, location_obj, delay=0.2):
        """Process a single location and return (success, source)."""
        try:
            if delay > 0:
                time.sleep(delay)

            lat, lng, updated, source = enhanced_ensure_location_coordinates(location_obj)

            if lat is not None and lng is not None:
                return True, source
            else:
                return False, 'failed'

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing {location_obj}: {str(e)}'))
            return False, 'error'