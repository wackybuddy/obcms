"""Management command to reset the OOBC staff directory."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from common.constants import STAFF_USER_TYPES
from common.models import User


STAFF_DIRECTORY_ENTRIES = [
    "Executive Director",
    "Deputy Executive Director",
    "Executive Assistant / Admin Officer",
    "Development Management Officer (DMO) IV - Head of Knowledge Management Division",
    "Development Management Officer (DMO) III - Heal of Monitoring and Evaluation Unit",
    "Planning Officer",
    "Budget Officer",
    "Community Development Officer",
    "Procurement Officer",
    "Information Systems Analyst",
    "Staff (for General Staff Functions)",
]


class Command(BaseCommand):
    """Replace existing staff users with the provided directory entries."""

    help = (
        "Deletes existing staff users (admin and OOBC staff types) and recreates "
        "the directory with the configured entries."
    )

    def handle(self, *args, **options):
        staff_types = set(STAFF_USER_TYPES)
        directory_entries = STAFF_DIRECTORY_ENTRIES

        with transaction.atomic():
            deleted_count, _ = User.objects.filter(user_type__in=staff_types).delete()

            created_users: list[User] = []
            for label in directory_entries:
                username_base = slugify(label) or "staff"
                username = username_base
                suffix = 2
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{suffix}"
                    suffix += 1

                user = User.objects.create(
                    username=username,
                    first_name=label,
                    last_name="",
                    user_type="oobc_staff",
                    email=f"{username}@oobc.local",
                    position=label,
                    organization="Office of the Bangsamoro Chief Minister",
                    is_active=True,
                    is_staff=True,
                    is_approved=True,
                )
                user.set_unusable_password()
                user.save(update_fields=["password"])
                created_users.append(user)

        created_list = ", ".join(user.first_name for user in created_users)
        self.stdout.write(
            self.style.SUCCESS(
                "Staff directory reset complete. Deleted "
                f"{deleted_count} staff users and created {len(created_users)} entries:"
            )
        )
        self.stdout.write(created_list)
