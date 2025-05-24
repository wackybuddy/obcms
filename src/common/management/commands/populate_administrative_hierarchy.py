from django.core.management.base import BaseCommand
from django.db import transaction
from common.models import Region, Province, Municipality, Barangay


class Command(BaseCommand):
    """
    Management command to populate the administrative hierarchy with initial data.
    Focus on Regions IX (Zamboanga Peninsula) and XII (SOCCSKSARGEN).
    """
    help = 'Populate administrative hierarchy with Region IX and XII data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing data',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self.populate_regions()
            self.populate_provinces()
            self.populate_municipalities()
            self.populate_sample_barangays()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated administrative hierarchy')
        )

    def populate_regions(self):
        """Populate regions with focus on IX and XII."""
        regions_data = [
            {
                'code': 'IX',
                'name': 'Zamboanga Peninsula',
                'description': 'Region IX encompasses the Zamboanga Peninsula and nearby islands in western Mindanao.'
            },
            {
                'code': 'XII',
                'name': 'SOCCSKSARGEN',
                'description': 'Region XII comprises South Cotabato, Cotabato, Sultan Kudarat, Sarangani, and General Santos City.'
            },
            # Additional regions that may have OBC communities
            {
                'code': 'XI',
                'name': 'Davao Region',
                'description': 'Region XI comprises the provinces of Davao del Norte, Davao del Sur, Davao Oriental, Davao de Oro, and Davao Occidental.'
            },
            {
                'code': 'X',
                'name': 'Northern Mindanao',
                'description': 'Region X comprises the provinces of Bukidnon, Camiguin, Lanao del Norte, Misamis Occidental, and Misamis Oriental.'
            },
        ]

        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                code=region_data['code'],
                defaults={
                    'name': region_data['name'],
                    'description': region_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created region: {region}')
            else:
                self.stdout.write(f'Region already exists: {region}')

    def populate_provinces(self):
        """Populate provinces for Regions IX and XII."""
        provinces_data = [
            # Region IX - Zamboanga Peninsula
            {
                'region_code': 'IX',
                'code': 'ZAM_DEL_NORTE',
                'name': 'Zamboanga del Norte',
                'capital': 'Dipolog City'
            },
            {
                'region_code': 'IX',
                'code': 'ZAM_DEL_SUR',
                'name': 'Zamboanga del Sur',
                'capital': 'Pagadian City'
            },
            {
                'region_code': 'IX',
                'code': 'ZAM_SIBUGAY',
                'name': 'Zamboanga Sibugay',
                'capital': 'Ipil'
            },
            # Region XII - SOCCSKSARGEN
            {
                'region_code': 'XII',
                'code': 'SOUTH_COTABATO',
                'name': 'South Cotabato',
                'capital': 'Koronadal City'
            },
            {
                'region_code': 'XII',
                'code': 'COTABATO',
                'name': 'Cotabato',
                'capital': 'Kidapawan City'
            },
            {
                'region_code': 'XII',
                'code': 'SULTAN_KUDARAT',
                'name': 'Sultan Kudarat',
                'capital': 'Isulan'
            },
            {
                'region_code': 'XII',
                'code': 'SARANGANI',
                'name': 'Sarangani',
                'capital': 'Alabel'
            },
            # Additional provinces in other regions
            {
                'region_code': 'XI',
                'code': 'DAVAO_DEL_NORTE',
                'name': 'Davao del Norte',
                'capital': 'Tagum City'
            },
            {
                'region_code': 'X',
                'code': 'BUKIDNON',
                'name': 'Bukidnon',
                'capital': 'Malaybalay City'
            },
        ]

        for province_data in provinces_data:
            try:
                region = Region.objects.get(code=province_data['region_code'])
                province, created = Province.objects.get_or_create(
                    code=province_data['code'],
                    defaults={
                        'region': region,
                        'name': province_data['name'],
                        'capital': province_data['capital']
                    }
                )
                if created:
                    self.stdout.write(f'Created province: {province}')
                else:
                    self.stdout.write(f'Province already exists: {province}')
            except Region.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Region {province_data["region_code"]} not found')
                )

    def populate_municipalities(self):
        """Populate sample municipalities for each province."""
        municipalities_data = [
            # Zamboanga del Norte
            {
                'province_code': 'ZAM_DEL_NORTE',
                'code': 'DIPOLOG',
                'name': 'Dipolog',
                'municipality_type': 'city'
            },
            {
                'province_code': 'ZAM_DEL_NORTE',
                'code': 'DAPITAN',
                'name': 'Dapitan',
                'municipality_type': 'city'
            },
            {
                'province_code': 'ZAM_DEL_NORTE',
                'code': 'POLANCO',
                'name': 'Polanco',
                'municipality_type': 'municipality'
            },
            # Zamboanga del Sur
            {
                'province_code': 'ZAM_DEL_SUR',
                'code': 'PAGADIAN',
                'name': 'Pagadian',
                'municipality_type': 'city'
            },
            {
                'province_code': 'ZAM_DEL_SUR',
                'code': 'ZAMBOANGA_CITY',
                'name': 'Zamboanga',
                'municipality_type': 'independent_city'
            },
            {
                'province_code': 'ZAM_DEL_SUR',
                'code': 'AURORA',
                'name': 'Aurora',
                'municipality_type': 'municipality'
            },
            # South Cotabato
            {
                'province_code': 'SOUTH_COTABATO',
                'code': 'KORONADAL',
                'name': 'Koronadal',
                'municipality_type': 'city'
            },
            {
                'province_code': 'SOUTH_COTABATO',
                'code': 'GENERAL_SANTOS',
                'name': 'General Santos',
                'municipality_type': 'independent_city'
            },
            {
                'province_code': 'SOUTH_COTABATO',
                'code': 'TBOLI',
                'name': 'Tboli',
                'municipality_type': 'municipality'
            },
            # Cotabato
            {
                'province_code': 'COTABATO',
                'code': 'KIDAPAWAN',
                'name': 'Kidapawan',
                'municipality_type': 'city'
            },
            {
                'province_code': 'COTABATO',
                'code': 'MLANG',
                'name': 'Mlang',
                'municipality_type': 'municipality'
            },
        ]

        for municipality_data in municipalities_data:
            try:
                province = Province.objects.get(code=municipality_data['province_code'])
                municipality, created = Municipality.objects.get_or_create(
                    code=municipality_data['code'],
                    defaults={
                        'province': province,
                        'name': municipality_data['name'],
                        'municipality_type': municipality_data['municipality_type']
                    }
                )
                if created:
                    self.stdout.write(f'Created municipality: {municipality}')
                else:
                    self.stdout.write(f'Municipality already exists: {municipality}')
            except Province.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Province {municipality_data["province_code"]} not found')
                )

    def populate_sample_barangays(self):
        """Populate sample barangays for key municipalities."""
        barangays_data = [
            # Dipolog City
            {
                'municipality_code': 'DIPOLOG',
                'code': 'BIASONG',
                'name': 'Biasong',
                'is_urban': True
            },
            {
                'municipality_code': 'DIPOLOG',
                'code': 'CENTRAL',
                'name': 'Central',
                'is_urban': True
            },
            {
                'municipality_code': 'DIPOLOG',
                'code': 'GALAS',
                'name': 'Galas',
                'is_urban': False
            },
            # Zamboanga City
            {
                'municipality_code': 'ZAMBOANGA_CITY',
                'code': 'CAMPO_ISLAM',
                'name': 'Campo Islam',
                'is_urban': True
            },
            {
                'municipality_code': 'ZAMBOANGA_CITY',
                'code': 'RIO_HONDO',
                'name': 'Rio Hondo',
                'is_urban': True
            },
            {
                'municipality_code': 'ZAMBOANGA_CITY',
                'code': 'SANTA_CATALINA',
                'name': 'Santa Catalina',
                'is_urban': True
            },
            # General Santos City
            {
                'municipality_code': 'GENERAL_SANTOS',
                'code': 'DADIANGAS_NORTH',
                'name': 'Dadiangas North',
                'is_urban': True
            },
            {
                'municipality_code': 'GENERAL_SANTOS',
                'code': 'LABANGAL',
                'name': 'Labangal',
                'is_urban': True
            },
            {
                'municipality_code': 'GENERAL_SANTOS',
                'code': 'TAMBLER',
                'name': 'Tambler',
                'is_urban': False
            },
            # Tboli
            {
                'municipality_code': 'TBOLI',
                'code': 'POBLACION',
                'name': 'Poblacion',
                'is_urban': True
            },
            {
                'municipality_code': 'TBOLI',
                'code': 'KEMATU',
                'name': 'Kematu',
                'is_urban': False
            },
        ]

        for barangay_data in barangays_data:
            try:
                municipality = Municipality.objects.get(code=barangay_data['municipality_code'])
                barangay, created = Barangay.objects.get_or_create(
                    code=barangay_data['code'],
                    defaults={
                        'municipality': municipality,
                        'name': barangay_data['name'],
                        'is_urban': barangay_data['is_urban']
                    }
                )
                if created:
                    self.stdout.write(f'Created barangay: {barangay}')
                else:
                    self.stdout.write(f'Barangay already exists: {barangay}')
            except Municipality.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Municipality {barangay_data["municipality_code"]} not found')
                )