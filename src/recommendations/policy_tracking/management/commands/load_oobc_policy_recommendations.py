"""Load the baseline set of OOBC policy recommendations."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from recommendations.policy_tracking.models import PolicyRecommendation

DEFAULT_RECOMMENDATIONS = [
    {
        "reference_number": "OOBC-REC-001",
        "title": "Institutionalise Barangay OBC Desks",
        "category": "governance",
        "priority": "critical",
        "scope": "barangay",
        "description": "Create permanent Barangay OBC Desks with trained focal staff and dedicated operating budgets.",
        "rationale": "Barangay-level contact points accelerate service access and ensure community coordination across ministries.",
    },
    {
        "reference_number": "OOBC-REC-002",
        "title": "Rolling Livelihood Recovery Fund",
        "category": "economic_development",
        "priority": "urgent",
        "scope": "regional",
        "description": "Establish a revolving fund to finance OBC livelihood restoration with technical assistance and results monitoring.",
        "rationale": "Economic shocks and displacement require flexible financing so OBC households can regain income stability.",
    },
    {
        "reference_number": "OOBC-REC-003",
        "title": "Scholarship Support for OBC Youth",
        "category": "social_development",
        "priority": "high",
        "scope": "regional",
        "description": "Provide scholarship slots and allowance support for senior high school and tertiary OBC learners in priority communities.",
        "rationale": "Education pathways remain the strongest driver for long-term OBC development and intergenerational mobility.",
    },
    {
        "reference_number": "OOBC-REC-004",
        "title": "Mobile Civil Registry Missions",
        "category": "protection_of_rights",
        "priority": "high",
        "scope": "municipal",
        "description": "Deploy joint PSA–LGU mobile teams to deliver civil registry and legal identity services in OBC settlements.",
        "rationale": "Legal identity unlocks access to social protection, banking, and participation in governance.",
    },
    {
        "reference_number": "OOBC-REC-005",
        "title": "Resilient Shelter Upgrading Program",
        "category": "rehabilitation_development",
        "priority": "critical",
        "scope": "provincial",
        "description": "Pilot resilient shelter upgrading for high-risk OBC communities including site development and WASH facilities.",
        "rationale": "Climate-exposed settlements require structural upgrades to protect lives and improve living conditions.",
    },
    {
        "reference_number": "OOBC-REC-006",
        "title": "OBC Health Navigation Teams",
        "category": "social_development",
        "priority": "high",
        "scope": "regional",
        "description": "Deploy OBC health navigators to coordinate referrals, PhilHealth membership, and culturally-sensitive services.",
        "rationale": "Navigation support shortens the path from diagnosis to treatment and improves health outcomes.",
    },
    {
        "reference_number": "OOBC-REC-007",
        "title": "Integrated Peacebuilding and Mediation Fund",
        "category": "protection_of_rights",
        "priority": "urgent",
        "scope": "municipal",
        "description": "Create rapid response mechanisms for land, resource, and clan conflict mediation with OBC participation.",
        "rationale": "Sustained peace dividends require responsive mediation services anchored on trusted intermediaries.",
    },
    {
        "reference_number": "OOBC-REC-008",
        "title": "Digital Skills Accelerator for OBC Youth",
        "category": "economic_development",
        "priority": "medium",
        "scope": "regional",
        "description": "Implement digital and soft skills bootcamps linked with ICT firms for internship placement.",
        "rationale": "Future-ready skills open pathways for high-quality employment and entrepreneurship.",
    },
    {
        "reference_number": "OOBC-REC-009",
        "title": "Cultural Heritage Microgrants",
        "category": "cultural_development",
        "priority": "medium",
        "scope": "community",
        "description": "Provide microgrants to document, preserve, and promote OBC cultural practices and knowledge systems.",
        "rationale": "Supporting cultural resilience strengthens identity and social cohesion across communities.",
    },
    {
        "reference_number": "OOBC-REC-010",
        "title": "OBC Data Governance and Interoperability Framework",
        "category": "governance",
        "priority": "high",
        "scope": "regional",
        "description": "Establish unified standards, APIs, and privacy safeguards for OBC data across ministries and LGUs.",
        "rationale": "Integrated data systems enable evidence-based programming while protecting community trust and privacy.",
    },
]


class Command(BaseCommand):
    """Load baseline policy recommendations for quick demonstrations."""

    help = "Load the 10 baseline OOBC policy recommendations if they are absent."

    def handle(self, *args, **options):
        User = get_user_model()
        proposer = (
            User.objects.filter(is_superuser=True).order_by("id").first()
            or User.objects.filter(is_staff=True).order_by("id").first()
        )

        if proposer is None:
            raise CommandError(
                "No approved staff or superuser account available to assign as policy proposer."
            )

        created_count = 0
        today = timezone.now().date()

        with transaction.atomic():
            for payload in DEFAULT_RECOMMENDATIONS:
                recommendation, created = PolicyRecommendation.objects.get_or_create(
                    reference_number=payload["reference_number"],
                    defaults={
                        "title": payload["title"],
                        "category": payload["category"],
                        "priority": payload["priority"],
                        "scope": payload["scope"],
                        "description": payload["description"],
                        "rationale": payload["rationale"],
                        "proposed_by": proposer,
                        "lead_author": proposer,
                        "status": "draft",
                        "submission_date": today,
                    },
                )

                if created:
                    created_count += 1

        if created_count:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Loaded {created_count} OOBC policy recommendations."
                )
            )
        else:
            self.stdout.write(
                "Policy recommendations already present; nothing to load."
            )
