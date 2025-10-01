"""
Management command to populate BARMM MOA mandates, functions, and acronyms
"""
from django.core.management.base import BaseCommand
from coordination.models import Organization
from coordination.barmm_moa_mandates import BARMM_MOA_DATA

# Official BARMM MOA Acronyms
BARMM_MOA_ACRONYMS = {
    "Office of the Chief Minister": "OCM",
    "Ministry of Agriculture, Fisheries and Agrarian Reform": "MAFAR",
    "Ministry of Basic, Higher, and Technical Education": "MBHTE",
    "Ministry of Environment, Natural Resources and Energy": "MENRE",
    "Ministry of Finance, and Budget and Management": "MFBM",
    "Ministry of Health": "MOH",
    "Ministry of Human Settlements and Development": "MHSD",
    "Ministry of Indigenous Peoples' Affairs": "MIPA",
    "Ministry of Interior and Local Government": "MILG",
    "Ministry of Labor and Employment": "MOLE",
    "Ministry of Public Order and Safety": "MPOS",
    "Ministry of Public Works": "MPW",
    "Ministry of Science and Technology": "MOST",
    "Ministry of Social Services and Development": "MSSD",
    "Ministry of Trade, Investments, and Tourism": "MTIT",
    "Ministry of Transportation and Communications": "MOTC",
}


class Command(BaseCommand):
    help = 'Populate BARMM Ministry/Office/Agency mandates, powers & functions, and acronyms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-all',
            action='store_true',
            help='Update all matching organizations even if they already have mandates',
        )

    def handle(self, *args, **options):
        update_all = options['update_all']

        updated_count = 0
        not_found_count = 0
        skipped_count = 0

        self.stdout.write(self.style.SUCCESS('Populating BARMM MOA mandates and functions...'))
        self.stdout.write('')

        for moa_name, data in BARMM_MOA_DATA.items():
            # Try to find the organization by name or acronym
            org = None

            # First try exact name match
            try:
                org = Organization.objects.get(name__iexact=moa_name)
            except Organization.DoesNotExist:
                pass
            except Organization.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Multiple organizations found with name: {moa_name}')
                )
                continue

            # If not found, try acronym match
            if not org:
                # Extract acronym from name if it contains parentheses
                if '(' in moa_name:
                    try:
                        acronym = moa_name.split('(')[1].split(')')[0]
                        org = Organization.objects.get(acronym__iexact=acronym)
                    except (Organization.DoesNotExist, IndexError):
                        pass
                    except Organization.MultipleObjectsReturned:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ Multiple organizations found with acronym from: {moa_name}')
                        )
                        continue

            if org:
                # Check if we should update
                if not update_all and (org.mandate or org.powers_and_functions):
                    self.stdout.write(
                        self.style.WARNING(f'  ⊘ Skipped: {org.name} (already has mandate/functions, use --update-all to override)')
                    )
                    skipped_count += 1
                    continue

                # Update the organization
                org.mandate = data.get('mandate', '')
                org.powers_and_functions = data.get('powers_and_functions', '')

                # Also set acronym if available and not already set
                if moa_name in BARMM_MOA_ACRONYMS and not org.acronym:
                    org.acronym = BARMM_MOA_ACRONYMS[moa_name]

                org.save()

                # Build update message
                update_msg = f'  ✓ Updated: {org.name}'
                if moa_name in BARMM_MOA_ACRONYMS:
                    update_msg += f' ({BARMM_MOA_ACRONYMS[moa_name]})'

                self.stdout.write(self.style.SUCCESS(update_msg))
                updated_count += 1
            else:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Not found in database: {moa_name}')
                )
                not_found_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  • Updated: {updated_count}'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'  • Skipped: {skipped_count}'))
        if not_found_count > 0:
            self.stdout.write(self.style.ERROR(f'  • Not found: {not_found_count}'))

        if not_found_count > 0:
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    'Organizations not found in database. Please create them first before running this command.'
                )
            )