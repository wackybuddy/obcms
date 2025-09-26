import time
import requests
from urllib.parse import quote
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from common.models import Region, Province, Municipality, Barangay


class Command(BaseCommand):
    help = 'Populate center_coordinates for barangays and municipalities using geocoding'

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
            default=1.0,
            help='Delay between API requests in seconds (default: 1.0)',
        )

    def handle(self, *args, **options):
        regions = options.get('regions')
        municipalities_only = options.get('municipalities_only')
        barangays_only = options.get('barangays_only')
        limit = options.get('limit')
        delay = options.get('delay')

        if municipalities_only and barangays_only:
            raise CommandError("Cannot specify both --municipalities-only and --barangays-only")

        # Filter regions if specified
        region_queryset = Region.objects.filter(is_active=True)
        if regions:
            region_queryset = region_queryset.filter(code__in=regions)

        self.stdout.write(self.style.SUCCESS(f'Processing regions: {list(region_queryset.values_list("code", flat=True))}'))

        total_processed = 0

        if not barangays_only:
            self.stdout.write(self.style.SUCCESS('\n=== Processing Municipalities ==='))
            for region in region_queryset:
                municipalities = Municipality.objects.filter(
                    province__region=region,
                    is_active=True,
                    center_coordinates__isnull=True
                ).select_related('province')

                if limit:
                    municipalities = municipalities[:limit - total_processed]

                for municipality in municipalities:
                    if limit and total_processed >= limit:
                        break

                    success = self.geocode_municipality(municipality, delay)
                    if success:
                        total_processed += 1
                        self.stdout.write(f'✓ {municipality.name}, {municipality.province.name}')
                    else:
                        self.stdout.write(self.style.WARNING(f'✗ Failed: {municipality.name}, {municipality.province.name}'))

                if limit and total_processed >= limit:
                    break

        if not municipalities_only:
            self.stdout.write(self.style.SUCCESS('\n=== Processing Barangays ==='))
            for region in region_queryset:
                barangays = Barangay.objects.filter(
                    municipality__province__region=region,
                    is_active=True,
                    center_coordinates__isnull=True
                ).select_related('municipality__province')

                if limit:
                    remaining_limit = limit - total_processed
                    if remaining_limit <= 0:
                        break
                    barangays = barangays[:remaining_limit]

                for barangay in barangays:
                    if limit and total_processed >= limit:
                        break

                    success = self.geocode_barangay(barangay, delay)
                    if success:
                        total_processed += 1
                        self.stdout.write(f'✓ {barangay.name}, {barangay.municipality.name}')
                    else:
                        self.stdout.write(self.style.WARNING(f'✗ Failed: {barangay.name}, {barangay.municipality.name}'))

                if limit and total_processed >= limit:
                    break

        self.stdout.write(self.style.SUCCESS(f'\nCompleted! Processed {total_processed} locations.'))

    def geocode_municipality(self, municipality, delay=1.0):
        """Geocode a municipality and update its center_coordinates."""
        # Build search query: "Municipality, Province, Philippines"
        query = f"{municipality.name}, {municipality.province.name}, Philippines"
        return self.geocode_location(municipality, query, delay)

    def geocode_barangay(self, barangay, delay=1.0):
        """Geocode a barangay and update its center_coordinates."""
        # Build search query: "Barangay Name, Municipality, Province, Philippines"
        query = f"{barangay.name}, {barangay.municipality.name}, {barangay.municipality.province.name}, Philippines"
        return self.geocode_location(barangay, query, delay)

    def geocode_location(self, location_obj, query, delay=1.0):
        """Generic geocoding function using Nominatim API."""
        try:
            time.sleep(delay)  # Rate limiting

            # Use Nominatim API (free, no API key required)
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'ph',  # Philippines only
                'addressdetails': 1
            }

            headers = {
                'User-Agent': 'OOBC-Django/1.0 (https://oobc.gov.ph)'  # Be respectful with user agent
            }

            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            results = response.json()
            if not results:
                return False

            # Get the first result
            result = results[0]
            lat = float(result['lat'])
            lng = float(result['lon'])

            # Update the location object
            with transaction.atomic():
                location_obj.center_coordinates = [lng, lat]  # GeoJSON format: [longitude, latitude]
                location_obj.save(update_fields=['center_coordinates'])

            return True

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Network error for "{query}": {str(e)}'))
            return False
        except (ValueError, KeyError) as e:
            self.stdout.write(self.style.ERROR(f'Parse error for "{query}": {str(e)}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error for "{query}": {str(e)}'))
            return False