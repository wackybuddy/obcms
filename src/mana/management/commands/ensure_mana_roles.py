from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from mana.models import WorkshopParticipantAccount
from django.core.management.base import BaseCommand


MANA_GROUPS = {
    "mana_regional_participant": ["can_access_regional_mana", "can_view_provincial_obc"],
    "mana_facilitator": [
        "can_access_regional_mana",
        "can_view_provincial_obc",
        "can_facilitate_workshop",
    ],
    "mana_admin": [
        "can_access_regional_mana",
        "can_view_provincial_obc",
        "can_facilitate_workshop",
        "add_workshopparticipantaccount",
        "change_workshopparticipantaccount",
        "delete_workshopparticipantaccount",
    ],
}


class Command(BaseCommand):
    """Ensure default Regional MANA groups and permissions exist."""

    help = "Create/update MANA groups with required permissions."

    def handle(self, *args, **options):
        created_groups = 0
        updated_groups = 0

        content_type = ContentType.objects.get_for_model(WorkshopParticipantAccount)

        for group_name, permission_codenames in MANA_GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                created_groups += 1
            else:
                updated_groups += 1

            permissions = Permission.objects.filter(codename__in=permission_codenames)
            missing = set(permission_codenames) - set(permissions.values_list("codename", flat=True))
            for codename in missing:
                permission, _ = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={
                        "name": codename.replace("_", " ").title(),
                    },
                )
                permissions = permissions | Permission.objects.filter(id=permission.id)

            group.permissions.set(permissions)
            group.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Ensured {len(MANA_GROUPS)} MANA groups (created {created_groups}, updated {updated_groups})."
            )
        )
