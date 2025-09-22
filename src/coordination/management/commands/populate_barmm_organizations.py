"""Management command to populate BARMM Ministries, Offices, and Agencies."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from coordination.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = "Populate BARMM Ministries, Offices, and Agencies based on Bangsamoro Administrative Code"

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing organizations if they already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write("Populating BARMM Ministries, Offices, and Agencies...")

        # Get or create a system user for created_by field
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@bangsamoro.gov.ph',
                'first_name': 'System',
                'last_name': 'User',
                'is_active': True,
            }
        )

        # Ministries established under Bangsamoro Administrative Code
        ministries = [
            ("Office of the Chief Minister", "OCM"),
            ("Ministry of Agriculture, Fisheries and Agrarian Reform", "MAFAR"),
            ("Ministry of Basic, Higher, and Technical Education", "MBHTE"),
            ("Ministry of Environment, Natural Resources and Energy", "MENRE"),
            ("Ministry of Finance, and Budget and Management", "MFBM"),
            ("Ministry of Health", "MOH"),
            ("Ministry of Human Settlements and Development", "MHSD"),
            ("Ministry of Indigenous Peoples' Affairs", "MIPA"),
            ("Ministry of Interior and Local Government", "MILG"),
            ("Ministry of Labor and Employment", "MOLE"),
            ("Ministry of Public Order and Safety", "MPOS"),
            ("Ministry of Public Works", "MPW"),
            ("Ministry of Science and Technology", "MOST"),
            ("Ministry of Social Services and Development", "MSSD"),
            ("Ministry of Trade, Investments, and Tourism", "MTIT"),
            ("Ministry of Transportation and Communications", "MOTC"),
        ]

        # Other agencies, offices, commissions, boards, and authorities
        other_agencies = [
            ("Office of the Wali", "OW"),
            ("Bangsamoro Human Rights Commission", "BHRC"),
            ("Bangsamoro Ports Management Authority", "BPMA"),
            ("Bangsamoro Disaster Risk Reduction and Management Council", "Bangsamoro DRRMC"),
            ("Bangsamoro Economic and Development Council", "BEDC"),
            ("Bangsamoro Regional Peace and Order Council", "BRPOC"),
            ("Bangsamoro Sustainable Development Board", "BSDB"),
            ("Bangsamoro Halal Board", "BHB"),
            ("Bangsamoro Education Board", "BEB"),
            ("Bangsamoro Economic Zone Authority", "BEZA"),
            ("Bangsamoro Maritime Industry Authority", "BMARINA"),
            ("Civil Aeronautics Board of the Bangsamoro", "CABB"),
            ("Civil Aviation Authority of the Bangsamoro", "CAAB"),
        ]

        created_count = 0
        updated_count = 0

        # Process ministries
        for name, acronym in ministries:
            org, created = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'acronym': acronym,
                    'organization_type': 'bmoa',
                    'description': f'BARMM Ministry established under the Bangsamoro Administrative Code',
                    'is_active': True,
                    'created_by': system_user,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created ministry: {name} ({acronym})")
                )
            elif options['update']:
                org.acronym = acronym
                org.organization_type = 'bmoa'
                org.description = f'BARMM Ministry established under the Bangsamoro Administrative Code'
                org.is_active = True
                org.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Updated ministry: {name} ({acronym})")
                )

        # Process other agencies
        for name, acronym in other_agencies:
            org, created = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'acronym': acronym,
                    'organization_type': 'bmoa',
                    'description': f'BARMM Agency/Office/Board/Authority established under the Bangsamoro Administrative Code',
                    'is_active': True,
                    'created_by': system_user,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created agency: {name} ({acronym})")
                )
            elif options['update']:
                org.acronym = acronym
                org.organization_type = 'bmoa'
                org.description = f'BARMM Agency/Office/Board/Authority established under the Bangsamoro Administrative Code'
                org.is_active = True
                org.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Updated agency: {name} ({acronym})")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Created {created_count} organizations, updated {updated_count} organizations."
            )
        )