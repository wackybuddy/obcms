"""Service for calculating and recording workshop success metrics."""

from decimal import Decimal
from typing import Dict, List
from django.db.models import Avg, Count, Q
from django.utils import timezone

from ..models import (
    Assessment,
    WorkshopActivity,
    WorkshopParticipantAccount,
    WorkshopResponse,
    WorkshopSynthesis,
)
from ..models_metrics import (
    OnboardingTracker,
    PerformanceLog,
    WorkshopMetricsSnapshot,
)


class MetricsTracker:
    """Calculate and track workshop success metrics."""

    # Success targets from plan
    TARGET_ONBOARDING_RATE = Decimal("90.00")  # ≥90%
    TARGET_SUBMISSION_RATE = Decimal("85.00")  # ≥85%
    TARGET_REVIEW_TIME_REDUCTION = Decimal("40.00")  # ≥40%
    TARGET_EXPORT_TIME_100_ROWS = Decimal("10.0")  # <10 seconds
    TARGET_SYNTHESIS_TIME = Decimal("30.0")  # <30 seconds average
    TARGET_AUDIT_COVERAGE = Decimal("100.00")  # 100%

    def __init__(self, assessment: Assessment):
        """Initialize tracker for an assessment."""
        self.assessment = assessment

    def calculate_onboarding_completion_rate(self) -> Dict:
        """
        Calculate onboarding completion rate.

        Target: ≥90% of invited participants complete onboarding before Workshop 1.

        Returns:
            dict with rate, target, meets_target, and breakdown
        """
        participants = WorkshopParticipantAccount.objects.filter(
            assessment=self.assessment
        )
        total_invited = participants.count()

        if total_invited == 0:
            return {
                "rate": Decimal("0.00"),
                "target": self.TARGET_ONBOARDING_RATE,
                "meets_target": False,
                "total_invited": 0,
                "completed": 0,
            }

        completed = participants.filter(
            consent_given=True, profile_completed=True
        ).count()

        rate = Decimal((completed / total_invited) * 100).quantize(Decimal("0.01"))
        meets_target = rate >= self.TARGET_ONBOARDING_RATE

        return {
            "rate": rate,
            "target": self.TARGET_ONBOARDING_RATE,
            "meets_target": meets_target,
            "total_invited": total_invited,
            "completed": completed,
        }

    def calculate_submission_rate(self, workshop: WorkshopActivity) -> Dict:
        """
        Calculate on-schedule submission rate for a workshop.

        Target: ≥85% of participants submit responses for each workshop on schedule.

        Returns:
            dict with rate, target, meets_target, and breakdown
        """
        participants = WorkshopParticipantAccount.objects.filter(
            assessment=self.assessment,
            consent_given=True,
            profile_completed=True,
        )
        total_participants = participants.count()

        if total_participants == 0:
            return {
                "rate": Decimal("0.00"),
                "target": self.TARGET_SUBMISSION_RATE,
                "meets_target": False,
                "total_participants": 0,
                "submitted": 0,
            }

        # Count participants who submitted at least one response for this workshop
        submitted = (
            WorkshopResponse.objects.filter(
                workshop=workshop, status="submitted", participant__in=participants
            )
            .values("participant")
            .distinct()
            .count()
        )

        rate = Decimal((submitted / total_participants) * 100).quantize(Decimal("0.01"))
        meets_target = rate >= self.TARGET_SUBMISSION_RATE

        return {
            "rate": rate,
            "target": self.TARGET_SUBMISSION_RATE,
            "meets_target": meets_target,
            "total_participants": total_participants,
            "submitted": submitted,
        }

    def calculate_review_time_savings(self) -> Dict:
        """
        Calculate facilitator review time reduction via aggregation and AI synthesis.

        Target: ≥40% reduction in review time.

        Returns:
            dict with reduction percentage, target, meets_target
        """
        # Get review time logs
        review_logs = PerformanceLog.objects.filter(
            assessment=self.assessment,
            operation_type="review",
            success=True,
            duration_seconds__isnull=False,
        ).order_by("start_time")

        if review_logs.count() < 2:
            return {
                "reduction": Decimal("0.00"),
                "target": self.TARGET_REVIEW_TIME_REDUCTION,
                "meets_target": False,
                "baseline_time": None,
                "current_time": None,
                "sample_count": review_logs.count(),
            }

        # Calculate baseline (first 3 reviews) vs current (last 3 reviews)
        baseline_logs = review_logs[:3]
        current_logs = review_logs.reverse()[:3]

        baseline_avg = baseline_logs.aggregate(avg=Avg("duration_seconds"))[
            "avg"
        ] or Decimal("0")
        current_avg = current_logs.aggregate(avg=Avg("duration_seconds"))[
            "avg"
        ] or Decimal("0")

        if baseline_avg == 0:
            reduction = Decimal("0.00")
        else:
            reduction = (
                (baseline_avg - current_avg) / baseline_avg * Decimal("100")
            ).quantize(Decimal("0.01"))

        meets_target = reduction >= self.TARGET_REVIEW_TIME_REDUCTION

        return {
            "reduction": reduction,
            "target": self.TARGET_REVIEW_TIME_REDUCTION,
            "meets_target": meets_target,
            "baseline_time": float(baseline_avg),
            "current_time": float(current_avg),
            "sample_count": review_logs.count(),
        }

    def calculate_export_performance(self) -> Dict:
        """
        Calculate export generation performance.

        Target: Exports complete in under 10 seconds for 100 responses.

        Returns:
            dict with average time, target, meets_target
        """
        # Get export logs for ~100 items
        export_logs = PerformanceLog.objects.filter(
            assessment=self.assessment,
            operation_type="export",
            success=True,
            item_count__gte=80,  # Allow some variance
            item_count__lte=120,
            duration_seconds__isnull=False,
        )

        if not export_logs.exists():
            return {
                "avg_time": None,
                "target": self.TARGET_EXPORT_TIME_100_ROWS,
                "meets_target": False,
                "sample_count": 0,
            }

        avg_time = export_logs.aggregate(avg=Avg("duration_seconds"))["avg"]
        avg_time = Decimal(str(avg_time)).quantize(Decimal("0.01"))
        meets_target = avg_time <= self.TARGET_EXPORT_TIME_100_ROWS

        return {
            "avg_time": avg_time,
            "target": self.TARGET_EXPORT_TIME_100_ROWS,
            "meets_target": meets_target,
            "sample_count": export_logs.count(),
        }

    def calculate_synthesis_performance(self) -> Dict:
        """
        Calculate AI synthesis performance.

        Target: Synthesis completes within 30 seconds average.

        Returns:
            dict with average time, target, meets_target
        """
        syntheses = WorkshopSynthesis.objects.filter(
            assessment=self.assessment,
            status="completed",
            processing_time_seconds__isnull=False,
        )

        if not syntheses.exists():
            return {
                "avg_time": None,
                "target": self.TARGET_SYNTHESIS_TIME,
                "meets_target": False,
                "sample_count": 0,
            }

        avg_time = syntheses.aggregate(avg=Avg("processing_time_seconds"))["avg"]
        avg_time = Decimal(str(avg_time)).quantize(Decimal("0.01"))
        meets_target = avg_time <= self.TARGET_SYNTHESIS_TIME

        return {
            "avg_time": avg_time,
            "target": self.TARGET_SYNTHESIS_TIME,
            "meets_target": meets_target,
            "sample_count": syntheses.count(),
        }

    def calculate_audit_coverage(self) -> Dict:
        """
        Calculate audit log coverage.

        Target: 100% of view/submit/synthesis actions captured.

        Returns:
            dict with coverage percentage, target, meets_target
        """
        from ..models import WorkshopAccessLog

        # Count expected actions (responses + syntheses)
        responses = WorkshopResponse.objects.filter(
            workshop__assessment=self.assessment, status="submitted"
        ).count()
        syntheses = WorkshopSynthesis.objects.filter(assessment=self.assessment).count()
        expected_actions = responses + syntheses

        if expected_actions == 0:
            return {
                "coverage": Decimal("100.00"),
                "target": self.TARGET_AUDIT_COVERAGE,
                "meets_target": True,
                "expected_actions": 0,
                "logged_actions": 0,
            }

        # Count logged actions
        logged_actions = WorkshopAccessLog.objects.filter(
            workshop__assessment=self.assessment, action_type__in=["submit", "complete"]
        ).count()

        coverage = Decimal((logged_actions / expected_actions) * 100).quantize(
            Decimal("0.01")
        )
        meets_target = coverage >= self.TARGET_AUDIT_COVERAGE

        return {
            "coverage": coverage,
            "target": self.TARGET_AUDIT_COVERAGE,
            "meets_target": meets_target,
            "expected_actions": expected_actions,
            "logged_actions": logged_actions,
        }

    def snapshot_all_metrics(self) -> List[WorkshopMetricsSnapshot]:
        """
        Create snapshots for all metrics at current point in time.

        Returns:
            list of created WorkshopMetricsSnapshot objects
        """
        snapshots = []

        # Onboarding rate
        onboarding = self.calculate_onboarding_completion_rate()
        snapshots.append(
            WorkshopMetricsSnapshot.objects.create(
                assessment=self.assessment,
                metric_type="onboarding",
                target_value=onboarding["target"],
                actual_value=onboarding["rate"],
                sample_size=onboarding["total_invited"],
                metadata={"completed": onboarding["completed"]},
            )
        )

        # Submission rates per workshop
        workshops = WorkshopActivity.objects.filter(assessment=self.assessment)
        for workshop in workshops:
            submission = self.calculate_submission_rate(workshop)
            snapshots.append(
                WorkshopMetricsSnapshot.objects.create(
                    assessment=self.assessment,
                    workshop=workshop,
                    metric_type="submission",
                    target_value=submission["target"],
                    actual_value=submission["rate"],
                    sample_size=submission["total_participants"],
                    metadata={"submitted": submission["submitted"]},
                )
            )

        # Review time reduction
        review_time = self.calculate_review_time_savings()
        if review_time["sample_count"] >= 2:
            snapshots.append(
                WorkshopMetricsSnapshot.objects.create(
                    assessment=self.assessment,
                    metric_type="review_time",
                    target_value=review_time["target"],
                    actual_value=review_time["reduction"],
                    sample_size=review_time["sample_count"],
                    metadata={
                        "baseline_time": review_time["baseline_time"],
                        "current_time": review_time["current_time"],
                    },
                )
            )

        # Export performance
        export_perf = self.calculate_export_performance()
        if export_perf["sample_count"] > 0:
            snapshots.append(
                WorkshopMetricsSnapshot.objects.create(
                    assessment=self.assessment,
                    metric_type="export_performance",
                    target_value=export_perf["target"],
                    actual_value=export_perf["avg_time"],
                    sample_size=export_perf["sample_count"],
                )
            )

        # Synthesis performance
        synth_perf = self.calculate_synthesis_performance()
        if synth_perf["sample_count"] > 0:
            snapshots.append(
                WorkshopMetricsSnapshot.objects.create(
                    assessment=self.assessment,
                    metric_type="synthesis_performance",
                    target_value=synth_perf["target"],
                    actual_value=synth_perf["avg_time"],
                    sample_size=synth_perf["sample_count"],
                )
            )

        # Audit coverage
        audit = self.calculate_audit_coverage()
        snapshots.append(
            WorkshopMetricsSnapshot.objects.create(
                assessment=self.assessment,
                metric_type="audit_coverage",
                target_value=audit["target"],
                actual_value=audit["coverage"],
                sample_size=audit["expected_actions"],
                metadata={"logged_actions": audit["logged_actions"]},
            )
        )

        return snapshots

    def get_success_dashboard(self) -> Dict:
        """
        Get comprehensive success metrics dashboard.

        Returns:
            dict with all metrics and overall success status
        """
        onboarding = self.calculate_onboarding_completion_rate()
        review_time = self.calculate_review_time_savings()
        export_perf = self.calculate_export_performance()
        synth_perf = self.calculate_synthesis_performance()
        audit = self.calculate_audit_coverage()

        # Calculate per-workshop submission rates
        workshops = WorkshopActivity.objects.filter(assessment=self.assessment)
        workshop_submissions = []
        for workshop in workshops:
            submission = self.calculate_submission_rate(workshop)
            workshop_submissions.append(
                {
                    "workshop": workshop.get_workshop_type_display(),
                    "rate": submission["rate"],
                    "meets_target": submission["meets_target"],
                }
            )

        # Count how many targets are met
        targets_met = sum(
            [
                onboarding["meets_target"],
                review_time["meets_target"],
                export_perf["meets_target"],
                synth_perf["meets_target"],
                audit["meets_target"],
            ]
            + [ws["meets_target"] for ws in workshop_submissions]
        )
        total_targets = 5 + len(workshop_submissions)

        return {
            "onboarding": onboarding,
            "workshop_submissions": workshop_submissions,
            "review_time": review_time,
            "export_performance": export_perf,
            "synthesis_performance": synth_perf,
            "audit_coverage": audit,
            "overall": {
                "targets_met": targets_met,
                "total_targets": total_targets,
                "success_rate": Decimal(
                    (targets_met / total_targets) * 100 if total_targets > 0 else 0
                ).quantize(Decimal("0.01")),
            },
        }
