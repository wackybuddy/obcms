"""AI-assisted workshop synthesis service."""

import json
import time
from typing import Dict, List, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from ..models import (
    WorkshopActivity,
    WorkshopResponse,
    WorkshopSynthesis,
)


class AIWorkshopSynthesizer:
    """Synthesize workshop outputs using AI assistance."""

    DEFAULT_PROMPT_TEMPLATE = """You are analyzing responses from a regional MANA (Mapping and Needs Assessment) workshop for Other Bangsamoro Communities (OBCs) in the Philippines.

Workshop: {workshop_title}
Total Responses: {response_count}
Provinces Represented: {provinces}
Stakeholder Types: {stakeholder_types}

RESPONSES:
{responses_text}

Please provide a structured synthesis covering:
1. Key Themes: Identify 3-5 major themes emerging from the responses
2. Patterns by Geography: Any notable patterns across provinces
3. Patterns by Stakeholder: Differences in perspectives by stakeholder type
4. Priority Issues: Top 3-5 priority issues identified
5. Recommendations: Actionable recommendations based on the responses

Format your response in clear sections with headings."""

    def __init__(self, workshop: WorkshopActivity, filters: Optional[Dict] = None):
        """
        Initialize synthesizer for a workshop.

        Args:
            workshop: WorkshopActivity to synthesize
            filters: Optional filters (province, stakeholder_type, etc.)
        """
        self.workshop = workshop
        self.filters = filters or {}

    def _get_responses(self) -> List[WorkshopResponse]:
        """Get responses based on filters."""
        queryset = WorkshopResponse.objects.filter(
            workshop=self.workshop, status="submitted"
        ).select_related("participant__user", "participant__province")

        # Apply filters
        if "province_id" in self.filters:
            queryset = queryset.filter(participant__province_id=self.filters["province_id"])

        if "stakeholder_type" in self.filters:
            queryset = queryset.filter(
                participant__stakeholder_type=self.filters["stakeholder_type"]
            )

        return list(queryset)

    def _format_responses(self, responses: List[WorkshopResponse]) -> str:
        """Format responses for the AI prompt."""
        formatted = []

        for i, response in enumerate(responses, 1):
            participant = response.participant
            formatted.append(
                f"\n--- Response {i} ---\n"
                f"Province: {participant.province.name}\n"
                f"Stakeholder Type: {participant.get_stakeholder_type_display()}\n"
                f"Question: {response.question_id}\n"
                f"Response: {response.response_data}\n"
            )

        return "\n".join(formatted)

    def _get_metadata(self, responses: List[WorkshopResponse]) -> Dict:
        """Extract metadata from responses."""
        provinces = set()
        stakeholder_types = set()

        for response in responses:
            provinces.add(response.participant.province.name)
            stakeholder_types.add(response.participant.get_stakeholder_type_display())

        return {
            "response_count": len(responses),
            "provinces": ", ".join(sorted(provinces)),
            "stakeholder_types": ", ".join(sorted(stakeholder_types)),
        }

    def _build_prompt(self, responses: List[WorkshopResponse]) -> str:
        """Build the AI prompt."""
        metadata = self._get_metadata(responses)
        responses_text = self._format_responses(responses)

        return self.DEFAULT_PROMPT_TEMPLATE.format(
            workshop_title=self.workshop.title,
            response_count=metadata["response_count"],
            provinces=metadata["provinces"],
            stakeholder_types=metadata["stakeholder_types"],
            responses_text=responses_text,
        )

    def _call_ai_provider(self, prompt: str, provider: str = "anthropic") -> Dict:
        """Call the configured AI provider and return a structured payload."""
        start_time = time.time()
        model = getattr(settings, "AI_SYNTHESIS_MODEL", None)

        if provider == "anthropic" and getattr(settings, "ANTHROPIC_API_KEY", None):
            try:
                import anthropic

                client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                selected_model = model or "claude-3-haiku-20240307"
                response = client.messages.create(
                    model=selected_model,
                    max_tokens=900,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}],
                )

                content = ""
                for block in getattr(response, "content", []):
                    text = getattr(block, "text", None) or (
                        block.get("text") if isinstance(block, dict) else None
                    )
                    if text:
                        content += text

                usage = getattr(response, "usage", None)
                tokens_used = getattr(usage, "output_tokens", None) if usage else None

                return self._parse_model_response(
                    content,
                    provider_name="Anthropic Claude",
                    model_name=selected_model,
                    tokens_used=tokens_used,
                    elapsed=time.time() - start_time,
                )
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"Anthropic synthesis failed: {exc}") from exc

        if provider == "openai" and getattr(settings, "OPENAI_API_KEY", None):
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                selected_model = model or "gpt-4o-mini"
                response = client.chat.completions.create(
                    model=selected_model,
                    temperature=0.2,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an analyst synthesising Regional MANA workshop responses into structured insights.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )

                content = response.choices[0].message.content
                usage = getattr(response, "usage", None)
                tokens_used = getattr(usage, "total_tokens", None) if usage else None

                return self._parse_model_response(
                    content,
                    provider_name="OpenAI",
                    model_name=selected_model,
                    tokens_used=tokens_used,
                    elapsed=time.time() - start_time,
                )
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"OpenAI synthesis failed: {exc}") from exc

        # Fallback placeholder when no provider is configured
        return {
            "synthesis_text": (
                "AI synthesis placeholder. Configure ANTHROPIC_API_KEY or OPENAI_API_KEY "
                "to unlock automated consolidation."
            ),
            "key_themes": [],
            "provider": "placeholder",
            "model": model or "n/a",
            "tokens_used": None,
            "processing_time_seconds": time.time() - start_time,
        }

    def _parse_model_response(
        self,
        content: str,
        provider_name: str,
        model_name: str,
        tokens_used: Optional[int],
        elapsed: float,
    ) -> Dict:
        """Parse JSON-friendly LLM responses and fall back to raw text."""
        summary = content
        key_themes: List[str] = []

        try:
            parsed = json.loads(content)
            summary = parsed.get("summary", content)
            key_themes = parsed.get("key_themes", [])
        except (json.JSONDecodeError, TypeError):
            parsed = {}

        return {
            "synthesis_text": summary,
            "key_themes": key_themes,
            "provider": provider_name,
            "model": model_name,
            "tokens_used": tokens_used,
            "processing_time_seconds": elapsed,
        }

    @transaction.atomic
    def synthesize(
        self,
        created_by,
        provider: str = "anthropic",
        custom_prompt: Optional[str] = None,
    ) -> WorkshopSynthesis:
        """
        Generate AI synthesis of workshop responses.

        Args:
            created_by: User requesting the synthesis
            provider: AI provider to use ('anthropic', 'openai', etc.)
            custom_prompt: Optional custom prompt template

        Returns:
            WorkshopSynthesis instance
        """
        # Get responses
        responses = self._get_responses()

        if not responses:
            synthesis = WorkshopSynthesis.objects.create(
                assessment=self.workshop.assessment,
                workshop=self.workshop,
                prompt_template=custom_prompt or self.DEFAULT_PROMPT_TEMPLATE,
                filters=self.filters,
                status="failed",
                error_message="No submitted responses found",
                created_by=created_by,
            )
            return synthesis

        # Build prompt
        prompt = custom_prompt or self._build_prompt(responses)

        # Create synthesis record
        synthesis = WorkshopSynthesis.objects.create(
            assessment=self.workshop.assessment,
            workshop=self.workshop,
            prompt_template=prompt,
            filters=self.filters,
            status="processing",
            created_by=created_by,
        )

        try:
            # Call AI provider
            result = self._call_ai_provider(prompt, provider)

            # Update synthesis with results
            synthesis.synthesis_text = result["synthesis_text"]
            synthesis.key_themes = result["key_themes"]
            synthesis.provider = result["provider"]
            synthesis.model = result["model"]
            synthesis.tokens_used = result["tokens_used"]
            synthesis.processing_time_seconds = result["processing_time_seconds"]
            synthesis.status = "completed"
            synthesis.save()

        except Exception as e:
            synthesis.status = "failed"
            synthesis.error_message = str(e)
            synthesis.save()
            raise

        return synthesis

    @transaction.atomic
    def regenerate_synthesis(
        self, synthesis: WorkshopSynthesis, created_by
    ) -> WorkshopSynthesis:
        """
        Regenerate an existing synthesis.

        Creates a new synthesis record with same filters.
        """
        return self.synthesize(
            created_by=created_by,
            provider=synthesis.provider or "anthropic",
            custom_prompt=synthesis.prompt_template,
        )

    @transaction.atomic
    def approve_synthesis(
        self, synthesis: WorkshopSynthesis, reviewed_by, review_notes: str = ""
    ) -> WorkshopSynthesis:
        """
        Approve a completed synthesis.

        Args:
            synthesis: WorkshopSynthesis to approve
            reviewed_by: User approving the synthesis
            review_notes: Optional notes from reviewer

        Returns:
            Updated WorkshopSynthesis instance
        """
        if synthesis.status != "completed":
            raise ValueError("Can only approve completed syntheses")

        synthesis.status = "approved"
        synthesis.reviewed_by = reviewed_by
        synthesis.review_notes = review_notes
        synthesis.approved_at = timezone.now()
        synthesis.save()

        return synthesis


def synthesize_workshop_async(
    workshop_id: int, filters: Optional[Dict] = None, created_by_id: int = None
):
    """
    Celery task for asynchronous workshop synthesis.

    This should be decorated with @shared_task in production.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        workshop = WorkshopActivity.objects.get(id=workshop_id)
        created_by = User.objects.get(id=created_by_id) if created_by_id else None

        synthesizer = AIWorkshopSynthesizer(workshop, filters)
        synthesis = synthesizer.synthesize(created_by=created_by)

        return {
            "success": True,
            "synthesis_id": synthesis.id,
            "status": synthesis.status,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
