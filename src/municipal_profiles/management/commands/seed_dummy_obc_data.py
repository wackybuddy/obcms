from __future__ import annotations

from typing import Dict, List

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity
from municipal_profiles.services import aggregate_and_store, ensure_profile


class Command(BaseCommand):
    help = "Create demo municipal and barangay OBC data for local testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tag",
            default="DMY",
            help="Alphanumeric prefix used when generating demo codes (default: DMY).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing demo communities created with the same tag.",
        )

    def handle(self, *args, **options):
        tag = options["tag"]
        force = options["force"]
        prefix = "".join(ch for ch in tag.upper() if ch.isalnum()) or "DMY"

        region_code = prefix[:10]
        province_code = f"{prefix}-P1"[:64]
        municipality_code = f"{prefix}-M1"[:64]
        barangay_codes = [f"{prefix}-B{i}"[:64] for i in range(1, 4)]

        with transaction.atomic():
            region, _ = Region.objects.get_or_create(
                code=region_code,
                defaults={"name": f"{prefix.title()} Region"},
            )
            province, _ = Province.objects.get_or_create(
                region=region,
                code=province_code,
                defaults={"name": f"{prefix.title()} Province"},
            )
            municipality, _ = Municipality.objects.get_or_create(
                province=province,
                code=municipality_code,
                defaults={"name": f"{prefix.title()} Municipality"},
            )

        barangays: List[Barangay] = []
        for idx, code in enumerate(barangay_codes, start=1):
            barangay, _ = Barangay.objects.get_or_create(
                municipality=municipality,
                code=code,
                defaults={"name": f"Barangay {idx}"},
            )
            barangays.append(barangay)

            if force:
                OBCCommunity.objects.filter(barangay__in=barangays).delete()

            community_payloads: List[Dict[str, object]] = [
                {
                    "estimated_obc_population": 120,
                    "households": 24,
                    "families": 20,
                    "children_0_9": 32,
                    "adolescents_10_14": 18,
                    "youth_15_30": 38,
                    "adults_31_59": 26,
                    "seniors_60_plus": 6,
                    "women_count": 58,
                    "solo_parents_count": 6,
                    "pwd_count": 5,
                    "farmers_count": 18,
                    "fisherfolk_count": 10,
                    "indigenous_peoples_count": 8,
                    "idps_count": 4,
                    "csos_count": 2,
                    "associations_count": 1,
                    "mosques_count": 1,
                    "madrasah_count": 1,
                    "asatidz_count": 1,
                    "religious_leaders_count": 2,
                    "primary_language": "Tausug",
                    "other_languages": "Tagalog, English",
                    "settlement_type": "village",
                    "unemployment_rate": "moderate",
                    "priority_needs": "Access to potable water",
                },
                {
                    "estimated_obc_population": 85,
                    "households": 18,
                    "families": 15,
                    "children_0_9": 20,
                    "adolescents_10_14": 10,
                    "youth_15_30": 22,
                    "adults_31_59": 25,
                    "seniors_60_plus": 8,
                    "women_count": 40,
                    "solo_parents_count": 4,
                    "pwd_count": 3,
                    "farmers_count": 10,
                    "fisherfolk_count": 6,
                    "indigenous_peoples_count": 6,
                    "idps_count": 2,
                    "csos_count": 1,
                    "associations_count": 1,
                    "mosques_count": 1,
                    "madrasah_count": 0,
                    "asatidz_count": 1,
                    "religious_leaders_count": 1,
                    "primary_language": "Yakan",
                    "other_languages": "Cebuano",
                    "settlement_type": "sitio",
                    "unemployment_rate": "high",
                    "priority_needs": "Shelter support",
                },
                {
                    "estimated_obc_population": 150,
                    "households": 32,
                    "families": 28,
                    "children_0_9": 40,
                    "adolescents_10_14": 22,
                    "youth_15_30": 45,
                    "adults_31_59": 32,
                    "seniors_60_plus": 11,
                    "women_count": 70,
                    "solo_parents_count": 8,
                    "pwd_count": 6,
                    "farmers_count": 28,
                    "fisherfolk_count": 12,
                    "indigenous_peoples_count": 10,
                    "idps_count": 5,
                    "csos_count": 3,
                    "associations_count": 2,
                    "mosques_count": 2,
                    "madrasah_count": 1,
                    "asatidz_count": 2,
                    "religious_leaders_count": 3,
                    "primary_language": "Maguindanaon",
                    "other_languages": "Hiligaynon, English",
                    "settlement_type": "purok",
                    "unemployment_rate": "low",
                    "priority_needs": "Livelihood grants",
                },
            ]

            aggregated_totals: Dict[str, int] = {}

            for barangay, payload in zip(barangays, community_payloads):
                numeric_payload = {
                    key: value
                    for key, value in payload.items()
                    if isinstance(value, (int, float))
                }
                defaults = {
                    "name": f"OBC Cluster {barangay.name}",
                    "community_names": f"OBC Cluster {barangay.name}",
                    "specific_location": f"Zone {barangay.name.split()[-1]}",
                    "obc_id": f"{prefix}-{barangay.code}",
                    **payload,
                }
                OBCCommunity.objects.update_or_create(
                    barangay=barangay,
                    defaults=defaults,
                )

                for key, value in numeric_payload.items():
                    aggregated_totals[key] = aggregated_totals.get(key, 0) + int(value)

            profile = ensure_profile(municipality)
            manual_adjustments = {
                "estimated_obc_population": 60,
                "households": 15,
                "families": 10,
                "women_count": 20,
                "pwd_count": 5,
            }

            manual_totals = {
                "sections": {
                    "demographics": {
                        "estimated_obc_population": aggregated_totals.get(
                            "estimated_obc_population", 0
                        )
                        + manual_adjustments["estimated_obc_population"],
                        "households": aggregated_totals.get("households", 0)
                        + manual_adjustments["households"],
                        "families": aggregated_totals.get("families", 0)
                        + manual_adjustments["families"],
                    },
                    "vulnerable_groups": {
                        "women_count": aggregated_totals.get("women_count", 0)
                        + manual_adjustments["women_count"],
                        "pwd_count": aggregated_totals.get("pwd_count", 0)
                        + manual_adjustments["pwd_count"],
                    },
                },
                "provided_fields": [
                    "estimated_obc_population",
                    "households",
                    "families",
                    "women_count",
                    "pwd_count",
                ],
                "metadata": {
                    "notes": "Seeded via seed_dummy_obc_data",
                },
            }
            profile.apply_reported_update(
                reported_payload=manual_totals,
                changed_by=None,
                note="Dummy municipal submission",
                update_notes=False,
            )

            aggregate_and_store(
                municipality=municipality,
                note="Dummy barangay roll-up",
            )

        profile.refresh_from_db()
        aggregated = profile.aggregated_metrics
        metadata = aggregated.get("metadata", {})
        summary = metadata.get("number_with_no_identified_barangay", {})

        self.stdout.write(self.style.SUCCESS("Dummy OBC data seeded successfully."))
        self.stdout.write(f"Region: {region.code} - {region.name}")
        self.stdout.write(f"Province: {province.code} - {province.name}")
        self.stdout.write(f"Municipality: {municipality.code} - {municipality.name}")
        self.stdout.write(f"Barangays created: {len(barangays)}")
        self.stdout.write(
            "Aggregated estimated OBC population: "
            f"{aggregated['sections']['demographics']['estimated_obc_population']}"
        )
        if summary:
            self.stdout.write(
                "Number with no identified barangay total: "
                f"{summary.get('total', 0)}"
            )
        else:
            self.stdout.write("All municipal totals accounted for across barangays.")
