"""Management command to seed sample Monitoring & Evaluation records."""

from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.models import Barangay, Municipality, Province, Region, User
from communities.models import OBCCommunity
from coordination.models import Organization
from monitoring.models import MonitoringEntry, MonitoringUpdate


class Command(BaseCommand):
    help = "Populate sample Monitoring & Evaluation data for demos and testing."

    def handle(self, *args, **options):
        """Entry point for the command."""

        user = (
            User.objects.filter(is_superuser=True).order_by("id").first()
            or User.objects.filter(is_approved=True).order_by("id").first()
        )
        if not user:
            raise CommandError(
                "No approved user found. Create at least one approved user before seeding data."
            )

        with transaction.atomic():
            region, _ = Region.objects.get_or_create(
                code="MNE",
                defaults={
                    "name": "Monitoring Sample Region",
                    "description": "Seed data",
                },
            )
            province, _ = Province.objects.get_or_create(
                region=region,
                code="MNE-PROV",
                defaults={"name": "Sample Province", "capital": "Sample Capital"},
            )
            municipality, _ = Municipality.objects.get_or_create(
                province=province,
                code="MNE-MUN",
                defaults={
                    "name": "Sample Municipality",
                    "municipality_type": "municipality",
                },
            )
            barangay, _ = Barangay.objects.get_or_create(
                municipality=municipality,
                code="MNE-BRGY",
                defaults={"name": "Sample Barangay"},
            )
            community, _ = OBCCommunity.objects.get_or_create(
                barangay=barangay,
                name="Sample OBC Community",
                defaults={
                    "settlement_type": "village",
                    "estimated_obc_population": 350,
                    "households": 70,
                },
            )

            lead_moa_org, _ = Organization.objects.get_or_create(
                name="Ministry of Social Services",
                organization_type="bmoa",
                defaults={"created_by": user},
            )
            if not lead_moa_org.created_by:
                lead_moa_org.created_by = user
                lead_moa_org.save(update_fields=["created_by"])

            oobc_support_org, _ = Organization.objects.get_or_create(
                name="OOBC Coordination Team",
                organization_type="bmoa",
                defaults={"created_by": user},
            )
            if not oobc_support_org.created_by:
                oobc_support_org.created_by = user
                oobc_support_org.save(update_fields=["created_by"])

            partner_org, _ = Organization.objects.get_or_create(
                name="Community Development NGO",
                organization_type="ngo",
                defaults={"created_by": user},
            )
            if not partner_org.created_by:
                partner_org.created_by = user
                partner_org.save(update_fields=["created_by"])

            entries_created = 0

            ppa_moa, created = MonitoringEntry.objects.get_or_create(
                title="Mobile Health Caravan",
                category="moa_ppa",
                defaults={
                    "summary": "Joint outreach delivering primary health care services to remote OBCs.",
                    "status": "ongoing",
                    "priority": "high",
                    "progress": 40,
                    "lead_organization": lead_moa_org,
                    "oobc_unit": "Program Coordination",
                    "start_date": date.today() - timedelta(days=30),
                    "target_end_date": date.today() + timedelta(days=45),
                    "milestone_dates": [
                        {
                            "date": (date.today() - timedelta(days=28)).isoformat(),
                            "title": "Initial outreach",
                            "status": "completed",
                        },
                        {
                            "date": (date.today() + timedelta(days=14)).isoformat(),
                            "title": "Mid-cycle evaluation",
                            "status": "upcoming",
                        },
                    ],
                    "budget_allocation": 1250000,
                    "created_by": user,
                    "updated_by": user,
                },
            )
            if created:
                ppa_moa.communities.add(community)
                ppa_moa.supporting_organizations.add(partner_org)
                entries_created += 1

            oobc_entry, created = MonitoringEntry.objects.get_or_create(
                title="OBC Leadership Fellowship",
                category="oobc_ppa",
                defaults={
                    "summary": "Capacity-building series for emerging community leaders.",
                    "status": "planning",
                    "priority": "medium",
                    "progress": 10,
                    "oobc_unit": "Capacity Development Unit",
                    "start_date": date.today() + timedelta(days=15),
                    "target_end_date": date.today() + timedelta(days=120),
                    "milestone_dates": [
                        {
                            "date": (date.today() + timedelta(days=30)).isoformat(),
                            "title": "Cohort onboarding",
                            "status": "upcoming",
                        },
                        {
                            "date": (date.today() + timedelta(days=110)).isoformat(),
                            "title": "Capstone summit",
                            "status": "planned",
                        },
                    ],
                    "budget_allocation": 450000,
                    "created_by": user,
                    "updated_by": user,
                },
            )
            if created:
                oobc_entry.communities.add(community)
                entries_created += 1

            request_entry, created = MonitoringEntry.objects.get_or_create(
                title="Livelihood Starter Kits",
                category="obc_request",
                defaults={
                    "summary": "Barangay leaders propose starter kits for 50 displaced households.",
                    "status": "planning",
                    "request_status": "under_review",
                    "priority": "urgent",
                    "progress": 5,
                    "submitted_by_community": community,
                    "submitted_to_organization": lead_moa_org,
                    "lead_organization": oobc_support_org,
                    "start_date": date.today(),
                    "next_milestone_date": date.today() + timedelta(days=21),
                    "milestone_dates": [
                        {
                            "date": (date.today() + timedelta(days=7)).isoformat(),
                            "title": "Document validation",
                            "status": "upcoming",
                        },
                        {
                            "date": (date.today() + timedelta(days=21)).isoformat(),
                            "title": "OOBC review panel",
                            "status": "upcoming",
                        },
                    ],
                    "support_required": "OOBC endorsement and initial funding release.",
                    "created_by": user,
                    "updated_by": user,
                },
            )
            if created:
                request_entry.communities.add(community)
                request_entry.supporting_organizations.add(partner_org)
                entries_created += 1

            MonitoringUpdate.objects.get_or_create(
                entry=ppa_moa,
                update_type="milestone",
                notes="Initial health caravan conducted in two municipalities with 320 beneficiaries.",
                defaults={
                    "status": "ongoing",
                    "progress": 40,
                    "next_steps": "Coordinate next wave with Ministry of Health.",
                    "follow_up_date": date.today() + timedelta(days=14),
                    "created_by": user,
                },
            )

            MonitoringUpdate.objects.get_or_create(
                entry=oobc_entry,
                update_type="note",
                notes="Curriculum outline drafted; awaiting partner confirmation.",
                defaults={
                    "progress": 10,
                    "created_by": user,
                },
            )

            MonitoringUpdate.objects.get_or_create(
                entry=request_entry,
                update_type="status",
                notes="OOBC review panel scheduled; additional documents requested.",
                defaults={
                    "status": "ongoing",
                    "request_status": "under_review",
                    "progress": 5,
                    "follow_up_date": date.today() + timedelta(days=7),
                    "created_by": user,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Sample Monitoring & Evaluation data populated. "
                f"Entries created or reused: {entries_created}."
            )
        )
