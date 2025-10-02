"""Seed staff management demo data for staging environments."""

from django.core.management.base import BaseCommand

from common.services.staff import ensure_default_staff_teams, seed_staff_demo_data


class Command(BaseCommand):
    help = "Seed OOBC staff teams and demo tasks to exercise management workflows."

    def handle(self, *args, **options):
        self.stdout.write("Ensuring default OOBC teams are available…")
        teams = ensure_default_staff_teams()
        self.stdout.write(self.style.SUCCESS(f"✓ Ensured {len(teams)} teams."))

        self.stdout.write("Seeding demo tasks and memberships…")
        tasks = seed_staff_demo_data()
        if tasks:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created or refreshed {len(tasks)} staff tasks across operational teams."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("No staff users available to assign tasks.")
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Staff management workflows are populated. You can now exercise the quick-action panels in the UI."
            )
        )
