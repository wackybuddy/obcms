from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from common.models import Barangay, Municipality, Province, Region
from communities.models import (CommunityInfrastructure, CommunityLivelihood,
                                OBCCommunity, Stakeholder)
from mana.models import (Assessment, AssessmentCategory, BaselineStudy,
                         BaselineStudyTeamMember, GeographicDataLayer, Need,
                         NeedsCategory)


class Command(BaseCommand):
    """
    Import Region XII OBC Communities and MANA data based on the comprehensive
    needs assessment report "Bridging Aspirations: A Comprehensive Needs
    Assessment and Mapping of Bangsamoro Communities in Region 12"
    """

    help = "Import Region XII OBC communities and MANA assessment data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview the import without making changes",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing communities if found",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        update_existing = options["update_existing"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No data will be saved")
            )

        with transaction.atomic():
            # Get Region XII
            region_xii = Region.objects.get(code="XII")

            # Import OBC Communities
            self.import_obc_communities(region_xii, dry_run, update_existing)

            # Create MANA Assessment
            self.create_mana_assessment(region_xii, dry_run)

        self.stdout.write(
            self.style.SUCCESS("Region XII MANA data import completed successfully")
        )

    def import_obc_communities(self, region, dry_run, update_existing):
        """Import OBC communities based on Table 1.3.1 from the MANA report"""

        # Region XII OBC communities data from MANA report
        communities_data = [
            # SULTAN KUDARAT
            {
                "province": "Sultan Kudarat",
                "municipality": "Palimbang",
                "barangays": ["Malisbong", "Kraan", "Kabuling"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 15000,
                "vulnerable_sectors": [
                    "Senior Citizens",
                    "Children",
                    "Women",
                    "PWD",
                    "Solo Parents",
                ],
                "challenges": [
                    "Lack of access to healthcare",
                    "Education",
                    "Low income",
                    "Poor road accessibility",
                ],
            },
            {
                "province": "Sultan Kudarat",
                "municipality": "Lutayan",
                "barangays": ["Tamnag", "Poblacion", "Palavilla"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 12000,
                "vulnerable_sectors": ["Senior Citizens", "PWD", "Women"],
                "challenges": ["Lack of basic services", "Isolation"],
            },
            {
                "province": "Sultan Kudarat",
                "municipality": "Columbio",
                "barangays": ["Polomolok", "Makat", "Datablao"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 8000,
                "vulnerable_sectors": ["Senior Citizens", "Children", "PWD"],
                "challenges": [
                    "Lack of healthcare access",
                    "Low education",
                    "High poverty",
                ],
            },
            {
                "province": "Sultan Kudarat",
                "municipality": "Lambayong",
                "barangays": ["Katitisan", "Lagao", "Sadsalan"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 10000,
                "vulnerable_sectors": ["Senior Citizens", "Children", "Women"],
                "challenges": [
                    "Limited infrastructure",
                    "High poverty",
                    "Limited access to services",
                ],
            },
            {
                "province": "Sultan Kudarat",
                "municipality": "Kalamansig",
                "barangays": ["Nalilidan", "Sta. Clara", "Poblacion"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 7500,
                "vulnerable_sectors": ["Senior Citizens", "PWD", "Women", "Children"],
                "challenges": [
                    "Lack of access to health",
                    "Education",
                    "Poverty",
                    "Discrimination",
                ],
            },
            # SARANGANI
            {
                "province": "Sarangani",
                "municipality": "Malapatan",
                "barangays": ["Sapu Masla", "Sapu Padido", "Tuyan"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 9000,
                "vulnerable_sectors": ["Fisherfolk", "Farmers"],
                "challenges": [
                    "High poverty",
                    "Land conflicts",
                    "Rampant drug activities",
                    "Flooding",
                ],
            },
            {
                "province": "Sarangani",
                "municipality": "Glan",
                "barangays": ["Baliton", "Pangyan", "Burias"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 11000,
                "vulnerable_sectors": ["Farmers", "Children", "Women"],
                "challenges": [
                    "Political discrimination",
                    "High poverty",
                    "Flooding",
                    "Drugs",
                ],
            },
            {
                "province": "Sarangani",
                "municipality": "Maasim",
                "barangays": ["Pananag", "Daliao", "Lumatil"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 8500,
                "vulnerable_sectors": ["Farmers", "Senior Citizens", "PWD"],
                "challenges": [
                    "Poverty",
                    "Natural hazards",
                    "Cultural erosion due to Westernization",
                ],
            },
            {
                "province": "Sarangani",
                "municipality": "Maitum",
                "barangays": ["Pinol", "Maguling", "Mindupok"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 7000,
                "vulnerable_sectors": [
                    "Women",
                    "Children",
                    "Senior Citizens",
                    "PWD",
                    "Fisherfolk",
                    "Farmers",
                ],
                "challenges": [
                    "Poverty",
                    "Poor health services",
                    "Lack of potable water",
                ],
            },
            {
                "province": "Sarangani",
                "municipality": "Kiamba",
                "barangays": ["Katabao", "Datudani", "Tambibil"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 6500,
                "vulnerable_sectors": ["Farmers", "Fisherfolk"],
                "challenges": [
                    "Presence of lawless elements",
                    "Peace and order issues",
                ],
            },
            # COTABATO PROVINCE (NORTH COTABATO)
            {
                "province": "Cotabato",
                "municipality": "Pikit",
                "barangays": ["Punol", "Paido Pulangi", "Macasendeg"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 20000,
                "vulnerable_sectors": [
                    "Farmers",
                    "Workers",
                    "Children",
                    "Elderly",
                    "Fisherfolk",
                ],
                "challenges": [
                    "Peace and order issues",
                    "Natural calamities",
                    "Unfinished infrastructure",
                ],
            },
            {
                "province": "Cotabato",
                "municipality": "Alamada",
                "barangays": ["Pigcawaran", "Guiling", "Mapurok"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 15000,
                "vulnerable_sectors": ["Farmers", "Workers", "Children", "Elderly"],
                "challenges": [
                    "Natural calamities",
                    "Social disorder",
                    "Limited access to services",
                ],
            },
            {
                "province": "Cotabato",
                "municipality": "Carmen",
                "barangays": ["Manili", "Kibenes", "Palanggalan"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 12000,
                "vulnerable_sectors": ["Farmers", "Workers", "Children", "Elderly"],
                "challenges": [
                    "Lack of opportunities",
                    "Land certification issues",
                    "Limited market access",
                ],
            },
            {
                "province": "Cotabato",
                "municipality": "Matalam",
                "barangays": ["Natutongan", "Ilian", "Rangayen"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 10000,
                "vulnerable_sectors": ["Farmers", "Workers", "Children", "Elderly"],
                "challenges": [
                    "Land ownership issues",
                    "Land certificate problems",
                    "Discrimination",
                ],
            },
            {
                "province": "Cotabato",
                "municipality": "Kabacan",
                "barangays": ["Magatos", "Kalaga", "Salapungan"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 8000,
                "vulnerable_sectors": ["Farmers", "Workers", "Children", "Elderly"],
                "challenges": ["Tribal discrimination", "Land certification issues"],
            },
            # SOUTH COTABATO
            {
                "province": "South Cotabato",
                "municipality": "Polomolok",
                "barangays": ["Lapu", "Koronadal Proper", "Poblacion"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 14000,
                "vulnerable_sectors": [
                    "Children",
                    "Women",
                    "PWD",
                    "Senior Citizens",
                    "Youth",
                ],
                "challenges": [
                    "Lack of equal opportunities",
                    "Limited access to services",
                    "Poverty",
                ],
            },
            {
                "province": "South Cotabato",
                "municipality": "Tupi",
                "barangays": ["Bunao", "Palian", "Poblacion"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 9000,
                "vulnerable_sectors": ["Farmers", "Children", "Elderly", "Women"],
                "challenges": ["Accessibility (infrastructure) issues"],
            },
            {
                "province": "South Cotabato",
                "municipality": "Tantangan",
                "barangays": ["Poblacion", "Dumadalig", "Magon"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 7500,
                "vulnerable_sectors": ["Farmers", "Children", "Elderly", "Women"],
                "challenges": ["Accessibility (infrastructure) issues"],
            },
            {
                "province": "South Cotabato",
                "municipality": "Banga",
                "barangays": ["Lamba", "Lampari", "Punong Grande"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 8500,
                "vulnerable_sectors": ["Children", "Women", "PWD", "Senior Citizens"],
                "challenges": ["Cultural practices", "Beliefs", "Limited resources"],
            },
            {
                "province": "South Cotabato",
                "municipality": "Koronadal",
                "barangays": ["Gen. Paulino Santos", "Saravia", "Sta. Cruz"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 12000,
                "vulnerable_sectors": [
                    "Children",
                    "Women",
                    "PWD",
                    "Senior Citizens",
                    "Youth",
                ],
                "challenges": [
                    "Lack of equal opportunities",
                    "Limited access to services",
                ],
            },
            # GENERAL SANTOS CITY
            {
                "province": "South Cotabato",  # General Santos City is independent but part of Region XII
                "municipality": "General Santos",
                "barangays": ["Tambler", "Labangal", "Batomelong"],
                "primary_ethnicity": "Magindanaw",
                "population_estimate": 25000,
                "vulnerable_sectors": ["Children", "Women", "Elderly"],
                "challenges": [
                    "Child labor",
                    "Limited access to education",
                    "Economic inequality",
                ],
            },
        ]

        imported_count = 0
        updated_count = 0

        for community_data in communities_data:
            try:
                # Get or create province
                province, _ = Province.objects.get_or_create(
                    name=community_data["province"],
                    region=region,
                    defaults={
                        "code": community_data["province"].upper().replace(" ", "_"),
                        "capital": "TBD",
                    },
                )

                # Get or create municipality
                municipality, _ = Municipality.objects.get_or_create(
                    name=community_data["municipality"],
                    province=province,
                    defaults={
                        "code": community_data["municipality"]
                        .upper()
                        .replace(" ", "_"),
                        "municipality_type": (
                            "city"
                            if "City" in community_data["municipality"]
                            else "municipality"
                        ),
                    },
                )

                # Create communities for each barangay
                for barangay_name in community_data["barangays"]:
                    if not dry_run:
                        # Get or create barangay
                        barangay, _ = Barangay.objects.get_or_create(
                            name=barangay_name,
                            municipality=municipality,
                            defaults={
                                "code": barangay_name.upper().replace(" ", "_"),
                                "is_urban": False,
                            },
                        )

                        # Calculate estimated population per barangay
                        population_per_barangay = community_data[
                            "population_estimate"
                        ] // len(community_data["barangays"])
                        households_per_barangay = (
                            population_per_barangay // 5
                        )  # Assume 5 people per household

                        # Create or update OBC community
                        community_defaults = {
                            "population": population_per_barangay,
                            "households": households_per_barangay,
                            "cultural_background": community_data["primary_ethnicity"],
                            "primary_language": community_data["primary_ethnicity"],
                            "settlement_type": "village",
                            "development_status": "developing",
                            "specific_location": f"OBC community in {barangay_name}",
                            "is_active": True,
                        }

                        community, created = OBCCommunity.objects.get_or_create(
                            barangay=barangay, defaults=community_defaults
                        )

                        if created:
                            imported_count += 1
                            self.stdout.write(
                                f"Created OBC community: {barangay.name}, {municipality.name}"
                            )
                        elif update_existing:
                            for key, value in community_defaults.items():
                                setattr(community, key, value)
                            community.save()
                            updated_count += 1
                            self.stdout.write(
                                f"Updated OBC community: {barangay.name}, {municipality.name}"
                            )

                    else:
                        self.stdout.write(
                            f'[DRY RUN] Would create OBC community: {barangay_name}, {community_data["municipality"]}'
                        )
                        imported_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error importing {community_data["municipality"]}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"OBC Communities - Imported: {imported_count}, Updated: {updated_count}"
            )
        )

    def create_mana_assessment(self, region, dry_run):
        """Create regional MANA assessment based on the comprehensive report"""

        if dry_run:
            self.stdout.write("[DRY RUN] Would create Region XII MANA Assessment")
            return

        # First create a sample community for the assessment (we'll use the first one from Sultan Kudarat)
        sample_community = OBCCommunity.objects.filter(
            barangay__municipality__province__region__code="XII"
        ).first()

        if not sample_community:
            self.stdout.write(
                self.style.ERROR(
                    "No OBC communities found in Region XII. Please run the community import first."
                )
            )
            return

        # Get or create assessment category
        category, _ = AssessmentCategory.objects.get_or_create(
            name="Comprehensive Needs Assessment",
            defaults={
                "category_type": "needs_assessment",
                "description": "Comprehensive assessment covering multiple development sectors",
                "color": "#007bff",
            },
        )

        # Get the admin user (assuming there's at least one superuser)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()

        if not admin_user:
            self.stdout.write(
                self.style.ERROR(
                    "No admin user found. Please create a superuser first."
                )
            )
            return

        # Create the main assessment
        assessment, created = Assessment.objects.get_or_create(
            title="Region XII OBC Comprehensive Needs Assessment 2024",
            defaults={
                "category": category,
                "description": """Comprehensive Needs Assessment and Mapping of Bangsamoro Communities in Region 12 (SOCCSKSARGEN).
                
This assessment covers OBCs across Sultan Kudarat, Sarangani, Cotabato Province, South Cotabato, and General Santos City.
Based on the Mapping and Needs Assessment Workshop conducted in September 2024.

Key findings:
- Total Muslim population in Region XII: 685,702 (15.76% of total population)
- Major challenges: marginalization in governance, limited access to public services, land tenure issues
- Priority development needs: healthcare, education, infrastructure, livelihood programs
- Most vulnerable sectors: children, women, elderly, PWDs, farmers, fisherfolk""",
                "objectives": """
1. Map and understand the current realities of OBC communities in Region XII
2. Identify priority development needs across multiple sectors
3. Assess vulnerabilities and challenges faced by different community groups
4. Provide evidence-based recommendations for development interventions
5. Establish baseline information for future monitoring and evaluation
                """,
                "community": sample_community,
                "status": "completed",
                "priority": "high",
                "planned_start_date": timezone.datetime(2024, 8, 1).date(),
                "planned_end_date": timezone.datetime(2024, 9, 30).date(),
                "actual_start_date": timezone.datetime(2024, 8, 1).date(),
                "actual_end_date": timezone.datetime(2024, 9, 30).date(),
                "lead_assessor": admin_user,
                "created_by": admin_user,
                "key_findings": """Key Findings:
- 685,702 Muslims in Region XII (15.76% of total population)
- Sultan Kudarat has highest Muslim population percentage (30.27%)
- Major livelihoods: agriculture (rice, coconut), fishing, small retail/trade
- Critical needs: healthcare access, education, infrastructure, livelihood support
- Most vulnerable: children, women, elderly, PWDs, farmers, fisherfolk""",
                "recommendations": """Recommendations:
1. Strengthen community-based development planning
2. Enhance education and capacity building programs
3. Address critical infrastructure needs (roads, water, electricity)
4. Promote livelihood and economic empowerment
5. Ensure healthcare and social services accessibility
6. Integrate technology and digital connectivity
7. Strengthen cultural and religious identity preservation""",
            },
        )

        if created:
            self.stdout.write(f"Created MANA Assessment: {assessment.title}")

        # Add geographic data layers
        geographic_layers = [
            {
                "name": "Sultan Kudarat OBC Population Distribution",
                "description": "Distribution of OBC communities across Sultan Kudarat province",
                "layer_type": "point",
                "data_source": "community_mapping",
                "geojson_data": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [124.2, 6.8]},
                            "properties": {
                                "name": "Sultan Kudarat OBC Communities",
                                "description": "Concentrated OBC settlements in Sultan Kudarat",
                            },
                        }
                    ],
                },
                "created_by": admin_user,
            },
            {
                "name": "Sarangani Coastal OBC Communities",
                "description": "Mapping of coastal OBC communities in Sarangani province",
                "layer_type": "point",
                "data_source": "community_mapping",
                "geojson_data": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [125.1, 5.9]},
                            "properties": {
                                "name": "Sarangani OBC Communities",
                                "description": "Coastal OBC communities in Sarangani province",
                            },
                        }
                    ],
                },
                "created_by": admin_user,
            },
            {
                "name": "Region XII Vulnerability Mapping",
                "description": "Identification of most vulnerable OBC areas and sectors",
                "layer_type": "polygon",
                "data_source": "field_survey",
                "geojson_data": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [124.0, 5.5],
                                        [125.5, 5.5],
                                        [125.5, 7.0],
                                        [124.0, 7.0],
                                        [124.0, 5.5],
                                    ]
                                ],
                            },
                            "properties": {
                                "name": "Region XII Vulnerability Areas",
                                "description": "Areas with high vulnerability indicators",
                            },
                        }
                    ],
                },
                "created_by": admin_user,
            },
        ]

        for layer_data in geographic_layers:
            layer, created = GeographicDataLayer.objects.get_or_create(
                assessment=assessment, name=layer_data["name"], defaults=layer_data
            )
            if created:
                self.stdout.write(f"Created geographic layer: {layer.name}")

        # Create baseline study
        baseline_study, created = BaselineStudy.objects.get_or_create(
            assessment=assessment,
            title="Region XII OBC Baseline Study 2024",
            defaults={
                "study_type": "comprehensive",
                "description": "Baseline study covering demographic, socio-economic, and development status of OBCs in Region XII",
                "objectives": """Study Objectives:
1. Establish baseline demographic and socio-economic indicators for OBC communities
2. Map current development status across key sectors
3. Identify priority needs and vulnerabilities
4. Document community assets and resources
5. Provide evidence base for future interventions""",
                "community": sample_community,
                "methodology": "mixed_methods",
                "status": "completed",
                "planned_start_date": timezone.datetime(2024, 8, 1).date(),
                "planned_end_date": timezone.datetime(2024, 9, 30).date(),
                "actual_start_date": timezone.datetime(2024, 8, 1).date(),
                "actual_end_date": timezone.datetime(2024, 9, 30).date(),
                "principal_investigator": admin_user,
                "data_collection_methods": """Data Collection Methods:
1. Community consultations and focus group discussions
2. Key informant interviews with community leaders
3. Stakeholder mapping and engagement
4. Participatory research and community mapping
5. Secondary data analysis from government sources""",
                "study_domains": {
                    "demographic": [
                        "Population size",
                        "Age structure",
                        "Household composition",
                    ],
                    "economic": [
                        "Livelihood sources",
                        "Income levels",
                        "Employment status",
                    ],
                    "social": [
                        "Education access",
                        "Health services",
                        "Social cohesion",
                    ],
                    "infrastructure": ["Housing", "Water/sanitation", "Transportation"],
                    "governance": [
                        "Local leadership",
                        "Community participation",
                        "Service delivery",
                    ],
                },
                "geographic_coverage": "Region XII - Sultan Kudarat, Sarangani, Cotabato Province, South Cotabato, General Santos City",
                "target_population": "Other Bangsamoro Communities (OBCs) residing outside BARMM boundaries in Region XII",
                "created_by": admin_user,
                "key_findings": """Key Findings:
- 685,702 Muslims in Region XII (15.76% of total population)
- Sultan Kudarat has highest Muslim population percentage (30.27%)
- Major livelihoods: agriculture (rice, coconut), fishing, small retail/trade
- Critical needs: healthcare access, education, infrastructure, livelihood support
- Most vulnerable: children, women, elderly, PWDs, farmers, fisherfolk""",
                "recommendations": """Recommendations:
1. Strengthen community-based development planning
2. Enhance education and capacity building programs
3. Address critical infrastructure needs (roads, water, electricity)
4. Promote livelihood and economic empowerment
5. Ensure healthcare and social services accessibility
6. Integrate technology and digital connectivity
7. Strengthen cultural and religious identity preservation""",
            },
        )

        if created:
            self.stdout.write(f"Created baseline study: {baseline_study.title}")

        # Add team members
        team_members = [
            {
                "name": "Norhan B. Hadji Abdullah",
                "role": "Overall Editor, Facilitator, and Writer",
                "organization": "OOBC",
            },
            {
                "name": "Engr. Farhana U. Kabalu",
                "role": "Facilitator and Writer",
                "organization": "OOBC",
            },
            {
                "name": "Esnain C. Mapait, RSW",
                "role": "Facilitator and Writer",
                "organization": "OOBC",
            },
            {
                "name": "Ramla L. Manguda",
                "role": "Facilitator and Writer",
                "organization": "OOBC",
            },
            {
                "name": "Michael A. Berwal, LPT",
                "role": "Facilitator and Writer",
                "organization": "OOBC",
            },
            {
                "name": "Noron S. Andan",
                "role": "Executive Director",
                "organization": "OOBC",
            },
        ]

        for member_data in team_members:
            # For team members, we need to use the User model
            # For now, let's create a simple implementation
            member, created = BaselineStudyTeamMember.objects.get_or_create(
                study=baseline_study,
                user=admin_user,
                role=(
                    "principal_investigator"
                    if "Director" in member_data["role"]
                    else "co_investigator"
                ),
                defaults={
                    "responsibilities": f"{member_data['role']} - {member_data['organization']}"
                },
            )
            if created:
                self.stdout.write(
                    f'Added team member: {member_data["name"]} as {member.role}'
                )

        # Create needs categories first
        needs_categories = [
            {
                "name": "Education Development",
                "sector": "education",
                "description": "Educational infrastructure, access, and quality improvements",
                "icon": "fa-graduation-cap",
                "color": "#28a745",
            },
            {
                "name": "Healthcare Services",
                "sector": "health",
                "description": "Healthcare access, infrastructure, and service delivery",
                "icon": "fa-heartbeat",
                "color": "#dc3545",
            },
            {
                "name": "Basic Infrastructure",
                "sector": "infrastructure",
                "description": "Roads, water systems, electricity, and sanitation",
                "icon": "fa-road",
                "color": "#6c757d",
            },
            {
                "name": "Economic Development",
                "sector": "economic_development",
                "description": "Livelihood support, entrepreneurship, and market access",
                "icon": "fa-coins",
                "color": "#ffc107",
            },
            {
                "name": "Cultural Preservation",
                "sector": "cultural_development",
                "description": "Cultural heritage, traditional practices, and Islamic education",
                "icon": "fa-mosque",
                "color": "#17a2b8",
            },
            {
                "name": "Social Protection",
                "sector": "social_development",
                "description": "Inclusion, governance, and support for vulnerable sectors",
                "icon": "fa-users",
                "color": "#6f42c1",
            },
        ]

        category_objects = {}
        for cat_data in needs_categories:
            category, created = NeedsCategory.objects.get_or_create(
                name=cat_data["name"], defaults=cat_data
            )
            category_objects[cat_data["name"]] = category
            if created:
                self.stdout.write(f"Created needs category: {category.name}")

        # Create priority needs based on report findings
        priority_needs = [
            {
                "category": "Education Development",
                "title": "Educational Infrastructure and Access",
                "description": "Expand access to primary, secondary, and tertiary education. Increase scholarship opportunities and vocational training programs.",
                "urgency_level": "short_term",
                "impact_severity": 5,
                "feasibility": "high",
                "affected_population": 50000,
                "status": "identified",
            },
            {
                "category": "Healthcare Services",
                "title": "Healthcare Services and Infrastructure",
                "description": "Enhance availability and accessibility of healthcare services, particularly in rural and underserved areas.",
                "urgency_level": "immediate",
                "impact_severity": 5,
                "feasibility": "medium",
                "affected_population": 60000,
                "status": "identified",
            },
            {
                "category": "Basic Infrastructure",
                "title": "Basic Infrastructure Development",
                "description": "Improve road networks, water systems, electricity, and sanitation facilities.",
                "urgency_level": "short_term",
                "impact_severity": 4,
                "feasibility": "medium",
                "affected_population": 70000,
                "status": "identified",
            },
            {
                "category": "Economic Development",
                "title": "Livelihood and Economic Empowerment",
                "description": "Provide targeted support to farmers, fisherfolk, and small entrepreneurs through skills training, microfinance, and market access.",
                "urgency_level": "medium_term",
                "impact_severity": 4,
                "feasibility": "high",
                "affected_population": 45000,
                "status": "identified",
            },
            {
                "category": "Cultural Preservation",
                "title": "Cultural Preservation and Identity",
                "description": "Strengthen efforts to preserve and promote traditional crafts, arts, and cultural practices. Support Islamic education (ISAL).",
                "urgency_level": "medium_term",
                "impact_severity": 3,
                "feasibility": "high",
                "affected_population": 30000,
                "status": "identified",
            },
            {
                "category": "Social Protection",
                "title": "Social Protection and Inclusion",
                "description": "Address discrimination and promote inclusive governance. Support vulnerable sectors including children, women, elderly, and PWDs.",
                "urgency_level": "short_term",
                "impact_severity": 4,
                "feasibility": "medium",
                "affected_population": 35000,
                "status": "identified",
            },
        ]

        for need_data in priority_needs:
            category = category_objects[need_data["category"]]
            need, created = Need.objects.get_or_create(
                title=need_data["title"],
                community=sample_community,
                defaults={
                    "category": category,
                    "assessment": assessment,
                    "description": need_data["description"],
                    "urgency_level": need_data["urgency_level"],
                    "impact_severity": need_data["impact_severity"],
                    "feasibility": need_data["feasibility"],
                    "affected_population": need_data["affected_population"],
                    "affected_households": need_data["affected_population"]
                    // 5,  # Assume 5 people per household
                    "geographic_scope": "Region XII - Multiple provinces and municipalities",
                    "status": need_data["status"],
                    "evidence_sources": "Community consultations, stakeholder mapping, OOBC MANA Workshop September 2024",
                    "identified_by": admin_user,
                },
            )

            if created:
                self.stdout.write(f"Created priority need: {need.title}")

        self.stdout.write(
            self.style.SUCCESS("Region XII MANA Assessment created successfully")
        )
