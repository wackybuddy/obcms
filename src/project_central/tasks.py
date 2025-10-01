"""
Celery Tasks for Project Central

Automated background tasks for project management and monitoring.
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='project_central.generate_daily_alerts')
def generate_daily_alerts_task():
    """
    Generate all daily alerts.

    Called by Celery scheduler daily.

    Returns:
        dict: Summary of alerts generated
    """
    from project_central.services import AlertService

    logger.info("Starting daily alert generation task")

    try:
        results = AlertService.generate_daily_alerts()
        logger.info(f"Daily alert generation completed: {results['total']} total alerts")

        if results['errors']:
            logger.error(f"Alert generation errors: {results['errors']}")

        return results

    except Exception as e:
        logger.error(f"Fatal error in daily alert generation: {e}", exc_info=True)
        raise


@shared_task(name='project_central.deactivate_resolved_alerts')
def deactivate_resolved_alerts_task():
    """
    Deactivate alerts that are no longer relevant.

    Called by Celery scheduler daily (after alert generation).

    Returns:
        int: Number of alerts deactivated
    """
    from project_central.services import AlertService

    logger.info("Starting resolved alert deactivation task")

    try:
        count = AlertService.deactivate_resolved_alerts()
        logger.info(f"Deactivated {count} resolved alerts")
        return count

    except Exception as e:
        logger.error(f"Error deactivating resolved alerts: {e}", exc_info=True)
        raise


@shared_task(name='project_central.cleanup_expired_alerts')
def cleanup_expired_alerts_task():
    """
    Clean up expired alerts.

    Called by Celery scheduler weekly.

    Returns:
        int: Number of alerts cleaned up
    """
    from project_central.models import Alert

    logger.info("Starting expired alert cleanup task")

    try:
        count = Alert.cleanup_expired_alerts()
        logger.info(f"Cleaned up {count} expired alerts")
        return count

    except Exception as e:
        logger.error(f"Error cleaning up expired alerts: {e}", exc_info=True)
        raise


@shared_task(name='project_central.update_budget_ceiling_allocations')
def update_budget_ceiling_allocations_task():
    """
    Update all budget ceiling allocated amounts.

    Called by Celery scheduler daily.

    Returns:
        int: Number of ceilings updated
    """
    from project_central.models import BudgetCeiling

    logger.info("Starting budget ceiling allocation update task")

    try:
        current_year = timezone.now().year
        ceilings = BudgetCeiling.objects.filter(
            fiscal_year=current_year,
            is_active=True,
        )

        count = 0
        for ceiling in ceilings:
            ceiling.update_allocated_amount()
            count += 1

        logger.info(f"Updated {count} budget ceiling allocations")
        return count

    except Exception as e:
        logger.error(f"Error updating budget ceiling allocations: {e}", exc_info=True)
        raise


@shared_task(name='project_central.generate_weekly_workflow_report')
def generate_weekly_workflow_report_task():
    """
    Generate weekly workflow performance report.

    Called by Celery scheduler weekly.

    Returns:
        dict: Report summary
    """
    from project_central.services import WorkflowService

    logger.info("Starting weekly workflow report generation")

    try:
        metrics = WorkflowService.get_workflow_metrics()

        # Email report to administrators
        # (Future: implement email template and distribution)

        logger.info(f"Generated workflow report: {metrics['total_workflows']} workflows")
        return metrics

    except Exception as e:
        logger.error(f"Error generating workflow report: {e}", exc_info=True)
        raise


@shared_task(name='project_central.generate_monthly_budget_report')
def generate_monthly_budget_report_task():
    """
    Generate monthly budget utilization report.

    Called by Celery scheduler monthly.

    Returns:
        dict: Report summary
    """
    from project_central.services import AnalyticsService

    logger.info("Starting monthly budget report generation")

    try:
        current_year = timezone.now().year
        summary = AnalyticsService.get_dashboard_summary(fiscal_year=current_year)

        # Email report to administrators
        # (Future: implement email template and distribution)

        logger.info("Generated monthly budget report")
        return {
            'fiscal_year': current_year,
            'total_budget': summary['budget_by_sector']['totals']['total_budget'],
            'utilization_pct': summary['utilization_rates']['ppa_utilization']['disbursement_rate'],
        }

    except Exception as e:
        logger.error(f"Error generating budget report: {e}", exc_info=True)
        raise


@shared_task(name='project_central.check_workflow_deadlines')
def check_workflow_deadlines_task():
    """
    Check for workflows approaching deadlines.

    Called by Celery scheduler daily.

    Returns:
        int: Number of deadline alerts created
    """
    from project_central.models import ProjectWorkflow, Alert
    from datetime import timedelta

    logger.info("Starting workflow deadline check")

    try:
        # Find workflows with target completion dates within 7 days
        seven_days_from_now = timezone.now().date() + timedelta(days=7)

        approaching_deadline = ProjectWorkflow.objects.filter(
            target_completion_date__lte=seven_days_from_now,
            target_completion_date__gte=timezone.now().date(),
            current_stage__in=[
                'budget_planning',
                'approval',
                'implementation',
                'monitoring',
            ],
        ).exclude(
            current_stage='completion'
        )

        count = 0
        for workflow in approaching_deadline:
            days_remaining = (workflow.target_completion_date - timezone.now().date()).days

            # Check if alert already exists
            existing_alert = Alert.objects.filter(
                alert_type='deadline_approaching',
                related_workflow=workflow,
                is_active=True,
            ).exists()

            if not existing_alert:
                Alert.create_alert(
                    alert_type='deadline_approaching',
                    severity='high' if days_remaining <= 3 else 'medium',
                    title=f"Deadline Approaching: {workflow.primary_need.title}",
                    description=f"This workflow has {days_remaining} days until target completion date ({workflow.target_completion_date}). Current stage: {workflow.get_current_stage_display()}",
                    related_workflow=workflow,
                    action_url=workflow.get_absolute_url(),
                    alert_data={
                        'workflow_id': str(workflow.id),
                        'days_remaining': days_remaining,
                        'target_date': workflow.target_completion_date.isoformat(),
                    },
                    expires_at=timezone.now() + timedelta(days=7),
                )
                count += 1

        logger.info(f"Created {count} deadline approaching alerts")
        return count

    except Exception as e:
        logger.error(f"Error checking workflow deadlines: {e}", exc_info=True)
        raise


@shared_task(name='project_central.sync_workflow_ppa_status')
def sync_workflow_ppa_status_task():
    """
    Synchronize workflow and PPA status fields.

    Ensures workflows and their linked PPAs stay in sync.

    Called by Celery scheduler daily.

    Returns:
        int: Number of syncs performed
    """
    from project_central.models import ProjectWorkflow

    logger.info("Starting workflow-PPA status sync")

    try:
        workflows = ProjectWorkflow.objects.exclude(ppa__isnull=True)

        count = 0
        for workflow in workflows:
            updated = False

            # Sync status
            if workflow.current_stage == 'completion' and workflow.ppa.status != 'completed':
                workflow.ppa.status = 'completed'
                workflow.ppa.save(update_fields=['status'])
                updated = True

            elif workflow.current_stage in ['implementation', 'monitoring'] and workflow.ppa.status != 'ongoing':
                workflow.ppa.status = 'ongoing'
                workflow.ppa.save(update_fields=['status'])
                updated = True

            # Sync approval status
            if workflow.current_stage == 'approval':
                from monitoring.models import MonitoringEntry
                if workflow.ppa.approval_status == MonitoringEntry.APPROVAL_STATUS_DRAFT:
                    workflow.ppa.approval_status = MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
                    workflow.ppa.save(update_fields=['approval_status'])
                    updated = True

            if updated:
                count += 1

        logger.info(f"Synchronized {count} workflow-PPA status fields")
        return count

    except Exception as e:
        logger.error(f"Error syncing workflow-PPA status: {e}", exc_info=True)
        raise
