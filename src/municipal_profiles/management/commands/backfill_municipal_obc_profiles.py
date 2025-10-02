from __future__ import annotations

from django.core.management.base import BaseCommand

from common.models import Municipality
from municipal_profiles.services import aggregate_and_store, ensure_profile


class Command(BaseCommand):
    help = "Create municipal OBC profiles for all municipalities and compute initial aggregates."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for municipality in Municipality.objects.select_related(
            "province__region"
        ).all():
            profile = ensure_profile(municipality)
            was_created = (
                profile.aggregation_version == 0 and not profile.aggregated_metrics
            )
            aggregate_and_store(municipality=municipality, note="Backfill command")
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Processed municipal profiles. Created/initialised: {created}, refreshed: {updated}"
            )
        )
