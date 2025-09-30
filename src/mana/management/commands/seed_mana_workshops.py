from __future__ import annotations

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError

from mana.models import Assessment, WorkshopActivity


WORKSHOP_BLUEPRINT = [
    {
        "type": "workshop_1",
        "title": "Understanding the Community Context",
        "day": "day_2",
        "description": "Establish comprehensive understanding of OBC history, demographics, and socioeconomic conditions.",
        "methodology": "Small group discussions, participatory mapping, historical timeline development, stakeholder identification",
        "expected_outputs": "Community maps, historical timelines, inventory of community strengths, stakeholder maps",
        "duration": 4.0,
        "start_time": "09:00",
        "end_time": "13:00",
    },
    {
        "type": "workshop_2",
        "title": "Community Aspirations and Priorities",
        "day": "day_3",
        "description": "Document community vision for development and identify key needs across sectors.",
        "methodology": "Vision board creation, thematic small group discussions, prioritisation exercises",
        "expected_outputs": "Community vision statements, prioritised needs list",
        "duration": 4.0,
        "start_time": "09:00",
        "end_time": "13:00",
    },
    {
        "type": "workshop_3",
        "title": "Community Collaboration and Empowerment",
        "day": "day_3",
        "description": "Assess community organizations and develop collaboration strategies.",
        "methodology": "Organizational mapping, collaboration assessment matrices, empowerment strategy sessions",
        "expected_outputs": "Organization maps, collaboration gap analysis, empowerment strategies",
        "duration": 4.0,
        "start_time": "14:00",
        "end_time": "18:00",
    },
    {
        "type": "workshop_4",
        "title": "Community Feedback on Existing Initiatives",
        "day": "day_4",
        "description": "Gather feedback on government programs and document lessons learned.",
        "methodology": "Program inventory development, evaluation workshops, recommendation formulation",
        "expected_outputs": "Program inventory with effectiveness assessment, implementation challenges",
        "duration": 3.0,
        "start_time": "09:00",
        "end_time": "12:00",
    },
    {
        "type": "workshop_5",
        "title": "OBCs Needs, Challenges, Factors, and Outcomes",
        "day": "day_4",
        "description": "Analyse priority issues, root causes, and impacts on community segments.",
        "methodology": "Problem tree analysis, impact assessment, factor relationship mapping",
        "expected_outputs": "Problem trees, impact analyses, relationship maps",
        "duration": 3.0,
        "start_time": "13:00",
        "end_time": "16:00",
    },
]


class Command(BaseCommand):
    help = "Seed the default five Regional MANA workshops for an assessment."

    def add_arguments(self, parser):
        parser.add_argument("assessment_id", help="UUID of the assessment")
        parser.add_argument(
            "--start-date",
            help="Start date (YYYY-MM-DD) for the workshop cycle. Defaults to assessment planned start date.",
        )
        parser.add_argument(
            "--target-participants",
            type=int,
            default=30,
            help="Target participant count per workshop",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Delete existing workshops before seeding",
        )

    def handle(self, assessment_id, **options):
        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist as exc:
            raise CommandError(f"Assessment {assessment_id} not found") from exc

        start_date_str = options.get("start_date") or (
            assessment.planned_start_date.isoformat()
            if assessment.planned_start_date
            else None
        )
        if not start_date_str:
            raise CommandError("Provide --start-date or set assessment.planned_start_date")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError as exc:
            raise CommandError("Invalid start date format. Use YYYY-MM-DD") from exc

        if options.get("overwrite"):
            deleted, _ = WorkshopActivity.objects.filter(assessment=assessment).delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted} existing workshops."))

        created = 0
        for blueprint in WORKSHOP_BLUEPRINT:
            if WorkshopActivity.objects.filter(
                assessment=assessment, workshop_type=blueprint["type"]
            ).exists():
                continue

            if blueprint["day"] == "day_2":
                scheduled_date = start_date + timedelta(days=1)
            elif blueprint["day"] == "day_3":
                scheduled_date = start_date + timedelta(days=2)
            elif blueprint["day"] == "day_4":
                scheduled_date = start_date + timedelta(days=3)
            else:
                scheduled_date = start_date

            WorkshopActivity.objects.create(
                assessment=assessment,
                workshop_type=blueprint["type"],
                title=blueprint["title"],
                description=blueprint["description"],
                workshop_day=blueprint["day"],
                scheduled_date=scheduled_date,
                start_time=blueprint["start_time"],
                end_time=blueprint["end_time"],
                duration_hours=blueprint["duration"],
                target_participants=options["target_participants"],
                methodology=blueprint["methodology"],
                expected_outputs=blueprint["expected_outputs"],
                created_by=assessment.created_by,
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} workshops for assessment {assessment_id}."
            )
        )
