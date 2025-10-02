"""Management command to approve all OOBC staff user accounts."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from common.models import User


class Command(BaseCommand):
    """Approve all OOBC staff accounts that were created with the create_staff_accounts command."""

    help = "Approves all unapproved OOBC staff accounts (username ending with .oobc)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be approved without actually approving accounts",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Get all OOBC staff accounts that are not approved
        staff_users = User.objects.filter(
            user_type="oobc_staff",
            username__endswith=".oobc",
            is_approved=False,
        ).order_by("username")

        if not staff_users.exists():
            self.stdout.write(
                self.style.WARNING(
                    "✓ No unapproved OOBC staff accounts found. All accounts are already approved."
                )
            )
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Found {staff_users.count()} unapproved OOBC staff accounts:"
            )
        )
        for user in staff_users:
            self.stdout.write(f"  - {user.username} ({user.get_full_name()})")

        # Get a superuser or admin to be the approver
        approver = User.objects.filter(is_superuser=True).first()
        if not approver:
            approver = User.objects.filter(user_type="admin", is_approved=True).first()

        if not approver:
            self.stdout.write(
                self.style.ERROR(
                    "\n❌ ERROR: No superuser or approved admin found to approve accounts. "
                    "Please create a superuser first using: ./manage.py createsuperuser"
                )
            )
            return

        self.stdout.write(
            f"\nApprover: {approver.username} ({approver.get_full_name()})"
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🔍 DRY RUN MODE - Would approve {staff_users.count()} accounts"
                )
            )
            return

        # Approve all staff accounts
        approved_count = 0
        with transaction.atomic():
            for user in staff_users:
                user.is_approved = True
                user.approved_by = approver
                user.approved_at = timezone.now()
                user.save()
                approved_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Approved: {user.username} - {user.get_full_name()}"
                    )
                )

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully approved {approved_count} OOBC staff accounts!\n"
                f"   All staff members can now log in to the system."
            )
        )
