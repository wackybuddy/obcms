"""Workshop access management service for sequential workshop unlocks."""

from typing import List, Optional

from django.db import transaction
from django.utils import timezone

from ..models import (
    Assessment,
    WorkshopAccessLog,
    WorkshopActivity,
    WorkshopParticipantAccount,
)


class WorkshopAccessManager:
    """Manages sequential workshop access for regional MANA assessments."""

    # Workshop progression order
    WORKSHOP_SEQUENCE = [
        "workshop_1",
        "workshop_2",
        "workshop_3",
        "workshop_4",
        "workshop_5",
    ]

    def __init__(self, assessment: Assessment):
        """Initialize the access manager for an assessment."""
        self.assessment = assessment

    def get_allowed_workshops(
        self, participant: WorkshopParticipantAccount
    ) -> List[str]:
        """
        Get list of workshop types that participant can currently access.

        Access model:
        - All previously completed workshops remain accessible for review
        - The participant's current workshop is unlocked for active editing
        - No other workshops are accessible until marked complete
        """
        completed = list(participant.completed_workshops or [])

        current = participant.current_workshop
        if not current:
            current = self.WORKSHOP_SEQUENCE[0]

        if current not in completed:
            completed.append(current)

        ordered_allowed = [
            workshop_type
            for workshop_type in self.WORKSHOP_SEQUENCE
            if workshop_type in completed
        ]

        return ordered_allowed

    def is_workshop_accessible(
        self, participant: WorkshopParticipantAccount, workshop_type: str
    ) -> bool:
        """Check if a specific workshop is accessible to participant."""
        return workshop_type in self.get_allowed_workshops(participant)

    @transaction.atomic
    def unlock_workshop(
        self, participant: WorkshopParticipantAccount, workshop_type: str, by_user
    ) -> bool:
        """
        Manually unlock a workshop for a participant (facilitator action).

        Returns True if unlocked, False if already accessible.
        """
        if self.is_workshop_accessible(participant, workshop_type):
            return False

        # Add to current workshop
        participant.current_workshop = workshop_type
        participant.save(update_fields=["current_workshop", "updated_at"])

        # Log the unlock action
        workshop = WorkshopActivity.objects.filter(
            assessment=self.assessment, workshop_type=workshop_type
        ).first()

        if workshop:
            WorkshopAccessLog.objects.create(
                participant=participant,
                workshop=workshop,
                action_type="unlock",
                metadata={
                    "unlocked_by": by_user.get_full_name(),
                    "reason": "manual_unlock",
                },
            )

        return True

    def auto_unlock_due_workshops(self) -> int:
        """Automatically unlock workshops that have reached their scheduled time."""

        updated = 0
        now = timezone.now()

        participants = WorkshopParticipantAccount.objects.filter(
            assessment=self.assessment
        ).select_related("user")

        activity_map = {
            activity.workshop_type: activity
            for activity in self.assessment.workshop_activities.all()
        }

        for participant in participants:
            allowed = self.get_allowed_workshops(participant)
            if not allowed:
                continue

            target_workshop_type = allowed[-1]
            if target_workshop_type == participant.current_workshop:
                continue

            participant.current_workshop = target_workshop_type
            participant.save(update_fields=["current_workshop", "updated_at"])
            updated += 1

            workshop = activity_map.get(target_workshop_type)
            if workshop:
                WorkshopAccessLog.objects.create(
                    participant=participant,
                    workshop=workshop,
                    action_type="unlock",
                    metadata={
                        "unlocked_by": "system",
                        "reason": "scheduled_unlock",
                        "timestamp": now.isoformat(),
                    },
                )

        return updated

    @transaction.atomic
    def mark_workshop_complete(
        self,
        participant: WorkshopParticipantAccount,
        workshop_type: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Mark a workshop as completed for a participant.

        Returns True if marked complete, False if already completed.
        """
        if workshop_type in participant.completed_workshops:
            return False

        # Add to completed workshops
        completed = participant.completed_workshops or []
        completed.append(workshop_type)
        participant.completed_workshops = completed

        # Update current workshop to next in sequence
        try:
            current_index = self.WORKSHOP_SEQUENCE.index(workshop_type)
            if current_index < len(self.WORKSHOP_SEQUENCE) - 1:
                participant.current_workshop = self.WORKSHOP_SEQUENCE[current_index + 1]
            else:
                participant.current_workshop = ""  # All workshops completed
        except ValueError:
            pass

        participant.save(update_fields=["completed_workshops", "current_workshop", "updated_at"])

        # Log completion
        workshop = WorkshopActivity.objects.filter(
            assessment=self.assessment, workshop_type=workshop_type
        ).first()

        if workshop:
            WorkshopAccessLog.objects.create(
                participant=participant,
                workshop=workshop,
                action_type="complete",
                metadata=metadata or {},
            )

        return True

    @transaction.atomic
    def advance_all_participants(self, workshop_type: str, by_user) -> int:
        """
        Advance all participants to a specific workshop (facilitator bulk action).

        Returns count of participants advanced.
        """
        participants = WorkshopParticipantAccount.objects.filter(
            assessment=self.assessment
        )

        count = 0
        for participant in participants:
            if self.unlock_workshop(participant, workshop_type, by_user):
                count += 1

        return count

    @transaction.atomic
    def reset_participant_progress(
        self, participant: WorkshopParticipantAccount, by_user
    ) -> bool:
        """
        Reset a participant's workshop progress (facilitator action).

        Returns True if reset successful.
        """
        participant.completed_workshops = []
        participant.current_workshop = "workshop_1"
        participant.save(update_fields=["completed_workshops", "current_workshop", "updated_at"])

        # Log the reset
        workshop = WorkshopActivity.objects.filter(
            assessment=self.assessment, workshop_type="workshop_1"
        ).first()

        if workshop:
            WorkshopAccessLog.objects.create(
                participant=participant,
                workshop=workshop,
                action_type="unlock",
                metadata={
                    "reset_by": by_user.get_full_name(),
                    "reason": "progress_reset",
                },
            )

        return True

    def get_progress_summary(self, participant: WorkshopParticipantAccount) -> dict:
        """
        Get a summary of participant's progress through workshops.

        Returns:
            {
                'completed_count': int,
                'total_workshops': int,
                'current_workshop': str,
                'next_workshop': str or None,
                'completion_percentage': float,
            }
        """
        completed_count = len(participant.completed_workshops or [])
        total_workshops = len(self.WORKSHOP_SEQUENCE)
        completion_percentage = (completed_count / total_workshops) * 100

        # Find next workshop
        next_workshop = None
        if participant.current_workshop and participant.current_workshop in self.WORKSHOP_SEQUENCE:
            current_index = self.WORKSHOP_SEQUENCE.index(participant.current_workshop)
            if current_index < len(self.WORKSHOP_SEQUENCE) - 1:
                next_workshop = self.WORKSHOP_SEQUENCE[current_index + 1]

        return {
            "completed_count": completed_count,
            "total_workshops": total_workshops,
            "current_workshop": participant.current_workshop or "workshop_1",
            "next_workshop": next_workshop,
            "completion_percentage": round(completion_percentage, 1),
        }

    def get_assessment_progress_summary(self) -> dict:
        """
        Get progress summary for all participants in the assessment.

        Returns:
            {
                'total_participants': int,
                'by_workshop': {
                    'workshop_1': {'completed': int, 'in_progress': int},
                    ...
                },
                'fully_completed': int,
            }
        """
        participants = WorkshopParticipantAccount.objects.filter(
            assessment=self.assessment
        )

        total_participants = participants.count()
        by_workshop = {}
        fully_completed = 0

        for workshop_type in self.WORKSHOP_SEQUENCE:
            completed = participants.filter(
                completed_workshops__contains=[workshop_type]
            ).count()
            in_progress = participants.filter(current_workshop=workshop_type).count()

            by_workshop[workshop_type] = {
                "completed": completed,
                "in_progress": in_progress,
            }

        # Count fully completed participants
        fully_completed = sum(
            1
            for p in participants
            if len(p.completed_workshops or []) == len(self.WORKSHOP_SEQUENCE)
        )

        return {
            "total_participants": total_participants,
            "by_workshop": by_workshop,
            "fully_completed": fully_completed,
        }
