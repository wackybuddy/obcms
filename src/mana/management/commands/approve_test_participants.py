"""Management command to approve all test participant accounts."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Approve all test participant user accounts for immediate login access"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\n=== Approving Test Participant Accounts ===\n")
        )

        # Get all test users (participants and facilitators)
        test_users = User.objects.filter(username__startswith="test_")

        approved_count = 0
        already_active_count = 0

        for user in test_users:
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
                approved_count += 1
                self.stdout.write(f"  ✅ Approved: {user.username}")
            else:
                already_active_count += 1

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"\n📊 Summary:"))
        self.stdout.write(f"  Total test users: {test_users.count()}")
        self.stdout.write(f"  Newly approved: {approved_count}")
        self.stdout.write(f"  Already active: {already_active_count}")
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                "\n✅ All test accounts are now active and ready for login!\n"
            )
        )
