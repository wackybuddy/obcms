from __future__ import annotations

import csv
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from mana.models import Assessment, WorkshopParticipantAccount

User = get_user_model()


def ensure_permissions(user: User):
    group, _ = Group.objects.get_or_create(name="mana_regional_participant")
    user.groups.add(group)
    for codename in ["can_access_regional_mana", "can_view_provincial_obc"]:
        try:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.add(permission)
        except Permission.DoesNotExist:
            continue


class Command(BaseCommand):
    help = "Import workshop participants for an assessment from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("assessment_id", help="UUID of the assessment")
        parser.add_argument("csv_path", help="Path to CSV file")
        parser.add_argument(
            "--default-password",
            dest="default_password",
            default=None,
            help="Fallback temporary password when not provided per row",
        )

    def handle(self, assessment_id, csv_path, **options):
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist as exc:
            raise CommandError(f"Assessment {assessment_id} not found") from exc

        created = 0
        skipped = 0

        with csv_file.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"email", "stakeholder_type", "province_id"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise CommandError(
                    f"CSV missing required columns: {', '.join(sorted(missing))}"
                )

            for row in reader:
                email = (row.get("email") or "").strip().lower()
                if not email:
                    skipped += 1
                    continue
                if User.objects.filter(username=email).exists():
                    skipped += 1
                    continue

                password = row.get("password") or options.get("default_password") or User.objects.make_random_password()

                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=row.get("first_name", ""),
                    last_name=row.get("last_name", ""),
                    password=password,
                )
                ensure_permissions(user)

                WorkshopParticipantAccount.objects.create(
                    assessment=assessment,
                    user=user,
                    stakeholder_type=row.get("stakeholder_type", "other"),
                    organization=row.get("organization", ""),
                    province_id=row.get("province_id") or None,
                    municipality_id=row.get("municipality_id") or None,
                    barangay_id=row.get("barangay_id") or None,
                    created_by=assessment.created_by,
                    current_workshop="workshop_1",
                    completed_workshops=[],
                    consent_given=False,
                    profile_completed=False,
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created} participants, skipped {skipped} duplicates or incomplete rows."
            )
        )
