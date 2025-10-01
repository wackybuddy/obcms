"""Management command to create MANA Facilitator accounts."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Create a MANA Facilitator account with appropriate permissions"

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="Username for the facilitator account"
        )
        parser.add_argument(
            "email",
            type=str,
            help="Email address for the facilitator account"
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Password for the account (default: changeme123)"
        )
        parser.add_argument(
            "--first-name",
            type=str,
            default="",
            help="First name of the facilitator"
        )
        parser.add_argument(
            "--last-name",
            type=str,
            default="",
            help="Last name of the facilitator"
        )
        parser.add_argument(
            "--all-permissions",
            action="store_true",
            help="Grant all MANA permissions (facilitator + participant + view OBC)"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options.get("password") or "changeme123"
        first_name = options.get("first_name") or ""
        last_name = options.get("last_name") or ""
        all_permissions = options.get("all_permissions") or False

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f'User "{username}" already exists')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        self.stdout.write(f"Created user: {username}")

        # Grant facilitator permission
        try:
            facilitator_perm = Permission.objects.get(
                codename="can_facilitate_workshop"
            )
            user.user_permissions.add(facilitator_perm)
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Granted: can_facilitate_workshop"
                )
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    "Warning: can_facilitate_workshop permission not found"
                )
            )

        # Grant additional MANA permissions if requested
        if all_permissions:
            try:
                regional_perm = Permission.objects.get(
                    codename="can_access_regional_mana"
                )
                user.user_permissions.add(regional_perm)
                self.stdout.write(
                    self.style.SUCCESS(
                        "✓ Granted: can_access_regional_mana"
                    )
                )
            except Permission.DoesNotExist:
                pass

            try:
                obc_perm = Permission.objects.get(
                    codename="can_view_provincial_obc"
                )
                user.user_permissions.add(obc_perm)
                self.stdout.write(
                    self.style.SUCCESS(
                        "✓ Granted: can_view_provincial_obc"
                    )
                )
            except Permission.DoesNotExist:
                pass

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ MANA Facilitator account created successfully!"
            )
        )
        self.stdout.write("")
        self.stdout.write("Account Details:")
        self.stdout.write(f"  Username: {username}")
        self.stdout.write(f"  Email: {email}")
        self.stdout.write(f"  Password: {password}")
        self.stdout.write(f"  Full Name: {user.get_full_name() or '(not set)'}")
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "⚠️  Remember to change the password after first login!"
            )
        )