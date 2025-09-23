from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import Barangay
from communities.models import (CommunityInfrastructure, CommunityLivelihood,
                                OBCCommunity)


class Command(BaseCommand):
    """
    Management command to populate sample OBC communities with realistic data.
    """

    help = "Populate sample OBC communities with comprehensive data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update existing data",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self.create_sample_communities()

        self.stdout.write(
            self.style.SUCCESS("Successfully populated sample OBC communities")
        )

    def create_sample_communities(self):
        """Create sample OBC communities with comprehensive data."""

        # Sample communities data
        communities_data = [
            {
                "barangay_code": "CAMPO_ISLAM",
                "name": "Campo Islam Tausug Community",
                "specific_location": "Sitio Tausug",
                "settlement_type": "village",
                "population": 150,
                "households": 32,
                "families": 30,
                "children_0_9": 30,
                "adolescents_10_14": 15,
                "youth_15_30": 55,
                "adults_31_59": 35,
                "seniors_60_plus": 15,
                "primary_language": "Tausug",
                "other_languages": "Chavacano, Cebuano, Filipino",
                "cultural_background": "Tausug cultural practices and traditions from Sulu. Strong maritime culture with emphasis on fishing and trade.",
                "religious_practices": "Sunni Islam, daily prayers, Friday congregational prayers, observance of Ramadan and Islamic holidays.",
                "mosques_count": 1,
                "madrasah_count": 1,
                "religious_leaders_count": 2,
                "established_year": 1985,
                "origin_story": "Families migrated from Sulu in the early 1980s seeking better economic opportunities and education for their children.",
                "migration_history": "Originally from Jolo, Sulu. Moved to Zamboanga due to conflict and seeking livelihood opportunities.",
                "unemployment_rate": "low",
                "needs_assessment_date": date.today() - timedelta(days=180),
                "priority_needs": "Skills training for youth, improved water supply, livelihood support for fishing activities",
                "community_leader": "Haji Abdullah Jamalul",
                "leader_contact": "+639123456789",
                "notes": "Active community with strong cultural identity. Participates in local government activities.",
                "livelihoods": [
                    {
                        "livelihood_type": "fishing",
                        "specific_activity": "Small-scale fishing",
                        "description": "Traditional fishing using bancas and nets",
                        "households_involved": 20,
                        "percentage_of_community": 62.50,
                        "is_primary_livelihood": True,
                        "seasonal": False,
                        "income_level": "low",
                        "challenges": "Competition from commercial fishing, weather dependency",
                        "opportunities": "Fish processing, boat building skills training",
                    },
                    {
                        "livelihood_type": "trade",
                        "specific_activity": "Sari-sari store operation",
                        "description": "Small convenience stores serving the community",
                        "households_involved": 8,
                        "percentage_of_community": 25.00,
                        "is_primary_livelihood": False,
                        "seasonal": False,
                        "income_level": "moderate",
                        "challenges": "Limited capital, competition",
                        "opportunities": "Microfinance access, business training",
                    },
                ],
                "infrastructure": [
                    {
                        "infrastructure_type": "water",
                        "availability_status": "limited",
                        "description": "Shared deep well with manual pump",
                        "coverage_percentage": 70.00,
                        "condition": "fair",
                        "priority_for_improvement": "high",
                        "notes": "Water quality testing needed",
                    },
                    {
                        "infrastructure_type": "electricity",
                        "availability_status": "available",
                        "description": "Connected to main grid",
                        "coverage_percentage": 85.00,
                        "condition": "good",
                        "priority_for_improvement": "low",
                        "notes": "Regular supply, some illegal connections",
                    },
                    {
                        "infrastructure_type": "religious",
                        "availability_status": "available",
                        "description": "Small mosque and madrasah",
                        "coverage_percentage": 100.00,
                        "condition": "good",
                        "priority_for_improvement": "medium",
                        "notes": "Needs expansion for growing community",
                    },
                ],
            },
            {
                "barangay_code": "DADIANGAS_NORTH",
                "name": "Maguindanao Settlers Community",
                "specific_location": "Purok 5",
                "settlement_type": "subdivision",
                "population": 220,
                "households": 48,
                "families": 45,
                "children_0_9": 45,
                "adolescents_10_14": 25,
                "youth_15_30": 80,
                "adults_31_59": 50,
                "seniors_60_plus": 20,
                "primary_language": "Maguindanao",
                "other_languages": "Cebuano, Filipino, Ilocano",
                "cultural_background": "Maguindanao traditions with agricultural background. Emphasis on extended family structures and community cooperation.",
                "religious_practices": "Sunni Islam, community prayers, traditional Islamic celebrations, Quran recitation sessions.",
                "mosques_count": 2,
                "madrasah_count": 0,
                "religious_leaders_count": 1,
                "established_year": 1992,
                "origin_story": "Families relocated from Maguindanao province seeking better opportunities in General Santos City.",
                "migration_history": "Originally from Cotabato and Maguindanao, moved due to economic opportunities in GenSan.",
                "unemployment_rate": "very_low",
                "needs_assessment_date": date.today() - timedelta(days=90),
                "priority_needs": "Youth education scholarships, halal food production training, community center construction",
                "community_leader": "Ustadz Ibrahim Salagunting",
                "leader_contact": "+639987654321",
                "notes": "Well-organized community with active participation in city programs.",
                "livelihoods": [
                    {
                        "livelihood_type": "agriculture",
                        "specific_activity": "Vegetable farming",
                        "description": "Small-scale vegetable production for local markets",
                        "households_involved": 25,
                        "percentage_of_community": 52.08,
                        "is_primary_livelihood": True,
                        "seasonal": True,
                        "income_level": "moderate",
                        "challenges": "Water access for irrigation, pest management",
                        "opportunities": "Organic farming, direct market access",
                    },
                    {
                        "livelihood_type": "services",
                        "specific_activity": "Tricycle/Jeepney driving",
                        "description": "Public transportation services",
                        "households_involved": 15,
                        "percentage_of_community": 31.25,
                        "is_primary_livelihood": False,
                        "seasonal": False,
                        "income_level": "moderate",
                        "challenges": "Vehicle maintenance costs, competition",
                        "opportunities": "Driving cooperatives, vehicle financing",
                    },
                ],
                "infrastructure": [
                    {
                        "infrastructure_type": "roads",
                        "availability_status": "available",
                        "description": "Paved road access to main highway",
                        "coverage_percentage": 90.00,
                        "condition": "good",
                        "priority_for_improvement": "low",
                        "notes": "Good connectivity to city center",
                    },
                    {
                        "infrastructure_type": "education",
                        "availability_status": "limited",
                        "description": "Elementary school nearby, no secondary",
                        "coverage_percentage": 60.00,
                        "condition": "fair",
                        "priority_for_improvement": "high",
                        "notes": "Need secondary education facility",
                    },
                ],
            },
            {
                "barangay_code": "KEMATU",
                "name": "Tboli-Muslim Community",
                "specific_location": "Sitio Riverside",
                "settlement_type": "compound",
                "population": 85,
                "households": 18,
                "families": 16,
                "children_0_9": 15,
                "adolescents_10_14": 10,
                "youth_15_30": 30,
                "adults_31_59": 20,
                "seniors_60_plus": 10,
                "primary_language": "Tboli",
                "other_languages": "Cebuano, Filipino",
                "cultural_background": "Mixed Tboli indigenous and Muslim converts. Blend of traditional Tboli practices with Islamic faith.",
                "religious_practices": "Islam with some traditional Tboli spiritual practices. Community prayers and Islamic observances.",
                "mosques_count": 0,
                "madrasah_count": 0,
                "religious_leaders_count": 1,
                "established_year": 1998,
                "origin_story": "Indigenous Tboli families who converted to Islam through interaction with Muslim settlers.",
                "migration_history": "Original inhabitants of the area, some intermarriage with Muslim families.",
                "unemployment_rate": "moderate",
                "needs_assessment_date": date.today() - timedelta(days=300),
                "priority_needs": "Religious education facilities, livelihood training, health services access",
                "community_leader": "Datu Mohammad Silwang",
                "leader_contact": "+639555123456",
                "notes": "Small community working to balance traditional and Islamic practices.",
                "livelihoods": [
                    {
                        "livelihood_type": "agriculture",
                        "specific_activity": "Rice farming",
                        "description": "Traditional rice cultivation using local varieties",
                        "households_involved": 12,
                        "percentage_of_community": 66.67,
                        "is_primary_livelihood": True,
                        "seasonal": True,
                        "income_level": "low",
                        "challenges": "Limited market access, traditional methods",
                        "opportunities": "Modern farming techniques, cooperative formation",
                    },
                    {
                        "livelihood_type": "handicrafts",
                        "specific_activity": "Traditional weaving",
                        "description": "Tboli traditional textile and crafts production",
                        "households_involved": 8,
                        "percentage_of_community": 44.44,
                        "is_primary_livelihood": False,
                        "seasonal": False,
                        "income_level": "very_low",
                        "challenges": "Limited market, competition from machine-made products",
                        "opportunities": "Tourism market, cultural preservation programs",
                    },
                ],
                "infrastructure": [
                    {
                        "infrastructure_type": "water",
                        "availability_status": "poor",
                        "description": "River water source, no treatment",
                        "coverage_percentage": 40.00,
                        "condition": "poor",
                        "priority_for_improvement": "critical",
                        "notes": "Water quality concerns, seasonal availability",
                    },
                    {
                        "infrastructure_type": "health",
                        "availability_status": "none",
                        "description": "No health facility in community",
                        "coverage_percentage": 0.00,
                        "condition": "very_poor",
                        "priority_for_improvement": "critical",
                        "notes": "Nearest health center is 15km away",
                    },
                ],
            },
        ]

        for community_data in communities_data:
            try:
                barangay = Barangay.objects.get(code=community_data["barangay_code"])

                # Extract nested data and barangay_code
                livelihoods_data = community_data.pop("livelihoods", [])
                infrastructure_data = community_data.pop("infrastructure", [])
                community_data.pop(
                    "barangay_code"
                )  # Remove barangay_code as it's not a model field

                # Create or update community
                community, created = OBCCommunity.objects.get_or_create(
                    name=community_data["name"],
                    barangay=barangay,
                    defaults=community_data,
                )

                if created:
                    self.stdout.write(f"Created community: {community}")

                    # Create livelihoods
                    for livelihood_data in livelihoods_data:
                        livelihood = CommunityLivelihood.objects.create(
                            community=community, **livelihood_data
                        )
                        self.stdout.write(
                            f"  - Added livelihood: {livelihood.specific_activity}"
                        )

                    # Create infrastructure
                    for infra_data in infrastructure_data:
                        infrastructure = CommunityInfrastructure.objects.create(
                            community=community, **infra_data
                        )
                        self.stdout.write(
                            f"  - Added infrastructure: {infrastructure.get_infrastructure_type_display()}"
                        )
                else:
                    self.stdout.write(f"Community already exists: {community}")

            except Barangay.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'Barangay {community_data["barangay_code"]} not found'
                    )
                )
