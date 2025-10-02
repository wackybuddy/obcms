"""
Management command to add official acronyms to BARMM MOA organizations
"""

from django.core.management.base import BaseCommand
from coordination.models import Organization


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
    help = "Add official acronyms to BARMM MOA organizations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update even if organization already has an acronym",
        )

    def handle(self, *args, **options):
        force = options["force"]

        updated_count = 0
        skipped_count = 0
        not_found_count = 0

        self.stdout.write(self.style.SUCCESS("Adding BARMM MOA acronyms..."))
        self.stdout.write("")

        for moa_name, acronym in BARMM_MOA_ACRONYMS.items():
            try:
                org = Organization.objects.get(name__iexact=moa_name)

                # Check if we should update
                if not force and org.acronym:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊘ Skipped: {org.name} (already has acronym "{org.acronym}", use --force to override)'
                        )
                    )
                    skipped_count += 1
                    continue

                # Update the acronym
                old_acronym = org.acronym
                org.acronym = acronym
                org.save()

                if old_acronym:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Updated: {org.name} (changed from "{old_acronym}" to "{acronym}")'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Added: {org.name} ({acronym})")
                    )
                updated_count += 1

            except Organization.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Not found in database: {moa_name}")
                )
                not_found_count += 1
            except Organization.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Multiple organizations found with name: {moa_name}"
                    )
                )
                not_found_count += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Summary:"))
        self.stdout.write(self.style.SUCCESS(f"  • Updated: {updated_count}"))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"  • Skipped: {skipped_count}"))
        if not_found_count > 0:
            self.stdout.write(self.style.ERROR(f"  • Not found: {not_found_count}"))

        if not_found_count > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Organizations not found in database. Please create them first."
                )
            )
