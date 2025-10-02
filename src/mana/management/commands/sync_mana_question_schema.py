from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from mana.models import WorkshopQuestionDefinition


class Command(BaseCommand):
    """Sync workshop questions from the canonical JSON schema into the database."""

    help = "Import workshop question definitions from workshop_questions_schema.json into WorkshopQuestionDefinition records."

    def add_arguments(self, parser):
        parser.add_argument(
            "schema_path",
            nargs="?",
            default=None,
            help="Optional path to schema JSON (defaults to app data/workshop_questions_schema.json)",
        )
        parser.add_argument(
            "--schema-version",
            dest="schema_version",
            default="v1",
            help="Version label to assign to imported question set",
        )
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete existing definitions for the provided version before import",
        )

    def handle(self, *args, **options):
        schema_path = options["schema_path"]
        version = options["schema_version"]

        if schema_path is None:
            schema_path = (
                Path(__file__).resolve().parent.parent.parent
                / "data"
                / "workshop_questions_schema.json"
            )
        else:
            schema_path = Path(schema_path)

        if not schema_path.exists():
            raise CommandError(f"Schema file not found: {schema_path}")

        with schema_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if options["purge"]:
            deleted, _ = WorkshopQuestionDefinition.objects.filter(
                version=version
            ).delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Removed {deleted} definitions for version {version}."
                )
            )

        total = 0
        for workshop_type, payload in data.items():
            questions = []
            if isinstance(payload, dict):
                questions = payload.get("questions", [])
            elif isinstance(payload, list):
                questions = payload

            for order, question in enumerate(questions):
                question_id = question.get("id")
                if not question_id:
                    continue
                WorkshopQuestionDefinition.objects.update_or_create(
                    workshop_type=workshop_type,
                    question_id=question_id,
                    version=version,
                    defaults={
                        "order": order,
                        "definition": question,
                    },
                )
                total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {total} workshop question definitions into version {version}."
            )
        )
