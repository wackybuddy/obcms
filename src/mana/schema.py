"""Helpers for loading Regional MANA workshop question schema."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from django.conf import settings
from django.db import transaction

from .models import WorkshopQuestionDefinition

SCHEMA_PATH = (
    Path(__file__).resolve().parent / "data" / "workshop_questions_schema.json"
)
DEFAULT_SCHEMA_VERSION = "participant_v1"


def get_schema_version() -> str:
    """Return the active workshop schema version from settings."""
    return getattr(settings, "MANA_QUESTION_SCHEMA_VERSION", DEFAULT_SCHEMA_VERSION)


@lru_cache(maxsize=1)
def load_workshop_schema() -> Dict[str, List[dict]]:
    """Load the workshop question schema from disk."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Workshop question schema file not found: {SCHEMA_PATH}"
        )

    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        data = json.load(schema_file)

    normalised = {}
    for key, value in data.items():
        if isinstance(value, dict):
            normalised[key] = {
                "title": value.get("title"),
                "questions": value.get("questions", []),
            }
        elif isinstance(value, list):
            normalised[key] = {"title": None, "questions": value}
        else:
            normalised[key] = {"title": None, "questions": []}
    return normalised


def _normalise_questions(questions: List[dict]) -> List[dict]:
    """Ensure question payloads have consistent keys."""
    normalised: List[dict] = []
    for question in questions:
        data = dict(question)
        if "repeater_fields" in data and "fields" not in data:
            data["fields"] = data.get("repeater_fields", [])
        normalised.append(data)
    return normalised


@transaction.atomic
def _ensure_schema_version(workshop_type: str) -> List[dict]:
    """Persist schema-based definitions for the current version."""
    schema = load_workshop_schema()
    questions = schema.get(workshop_type, {}).get("questions", [])
    if not questions:
        return []

    normalised = _normalise_questions(questions)

    version = get_schema_version()

    for order, question in enumerate(normalised):
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

    hydrated = (
        WorkshopQuestionDefinition.objects.filter(
            workshop_type=workshop_type, version=version
        )
        .order_by("order", "question_id")
        .values_list("definition", flat=True)
    )
    return list(hydrated)


def get_questions_for_workshop(workshop_type: str) -> List[dict]:
    """Return the question definitions for a specific workshop."""
    version = get_schema_version()
    definitions = WorkshopQuestionDefinition.objects.filter(
        workshop_type=workshop_type, version=version
    ).order_by("order", "question_id")

    if definitions.exists():
        return list(definitions.values_list("definition", flat=True))

    # Seed the current schema version if missing
    seeded = _ensure_schema_version(workshop_type)
    if seeded:
        return seeded

    # Fallback to latest available version (legacy definitions)
    legacy = (
        WorkshopQuestionDefinition.objects.filter(workshop_type=workshop_type)
        .order_by("-updated_at", "order")
        .values_list("definition", flat=True)
    )
    if legacy:
        return list(legacy)

    # Fallback to schema data without persistence if no definitions exist
    schema = load_workshop_schema()
    questions = schema.get(workshop_type, {}).get("questions", [])
    return _normalise_questions(questions)


def get_all_workshop_types() -> List[str]:
    """Return all workshop types defined in the schema."""
    schema = load_workshop_schema()
    return list(schema.keys())
