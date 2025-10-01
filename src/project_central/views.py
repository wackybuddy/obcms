"""Project Central Views provide integrated project management interfaces."""

from datetime import date

from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone

from .models import ProjectWorkflow, Alert, BudgetCeiling, BudgetScenario
from mana.models import Need
from monitoring.models import MonitoringEntry
from common.models import StaffTask
from common.services.task_automation import create_tasks_from_template


# ========== TASK 8: Portfolio Dashboard View ==========

@login_required
def portfolio_dashboard_view(request):
    """
    Integrated portfolio dashboard showing project lifecycle with budget metrics.
    """
    current_year = timezone.now().year

    # Summary metrics
    total_budget = MonitoringEntry.objects.filter(
        fiscal_year=current_year
    ).aggregate(total=Sum('budget_allocation'))['total'] or 0

    active_projects = MonitoringEntry.objects.filter(status='ongoing').count()
    unfunded_needs = Need.objects.filter(linked_ppa__isnull=True, priority_score__gte=4.0).count()
    total_beneficiaries = MonitoringEntry.objects.filter(fiscal_year=current_year).aggregate(total=Sum('obc_slots'))['total'] or 0

    # Pipeline data
    needs_identified = Need.objects.filter(status='identified').count()
    ppas_planning = MonitoringEntry.objects.filter(status='planning').count()
    ppas_ongoing = MonitoringEntry.objects.filter(status='ongoing').count()
    ppas_completed = MonitoringEntry.objects.filter(status='completed').count()

    # Recent alerts
    recent_alerts = Alert.objects.filter(is_active=True, is_acknowledged=False).order_by('-severity', '-created_at')[:5]

    # Recent workflows
    recent_workflows = ProjectWorkflow.objects.all()[:10]

    context = {
        'total_budget': total_budget,
        'active_projects': active_projects,
        'unfunded_needs': unfunded_needs,
        'total_beneficiaries': total_beneficiaries,
        'needs_identified': needs_identified,
        'ppas_planning': ppas_planning,
        'ppas_ongoing': ppas_ongoing,
        'ppas_completed': ppas_completed,
        'recent_alerts': recent_alerts,
        'recent_workflows': recent_workflows,
        'current_year': current_year,
    }

    return render(request, 'project_central/portfolio_dashboard.html', context)


# ========== TASK 9: Project Workflow Detail View ==========

@login_required
def project_workflow_detail(request, workflow_id):
    """Show detailed project workflow with stages, budget approval status, timeline."""
    workflow = get_object_or_404(ProjectWorkflow, id=workflow_id)

    tasks = StaffTask.objects.filter(linked_workflow=workflow).order_by('-created_at')
    alerts = Alert.objects.filter(related_workflow=workflow, is_active=True).order_by('-severity', '-created_at')

    context = {
        'workflow': workflow,
        'need': workflow.primary_need,
        'ppa': workflow.ppa,
        'tasks': tasks,
        'alerts': alerts,
        'stage_history': workflow.stage_history,
    }

    return render(request, 'project_central/workflow_detail.html', context)


@login_required
def project_list_view(request):
    """List all project workflows."""
    workflows = ProjectWorkflow.objects.all().order_by('-initiated_date')

    stage_filter = request.GET.get('stage')
    if stage_filter:
        workflows = workflows.filter(current_stage=stage_filter)

    context = {'workflows': workflows, 'stage_filter': stage_filter, 'stage_choices': ProjectWorkflow.WORKFLOW_STAGES}
    return render(request, 'project_central/project_list.html', context)


@login_required
def create_project_workflow(request):
    messages.info(request, "Create project workflow functionality coming soon.")
    return redirect('project_central:project_list')


@login_required
def edit_project_workflow(request, workflow_id):
    messages.info(request, "Edit project workflow functionality coming soon.")
    return redirect('project_central:project_workflow_detail', workflow_id=workflow_id)


@login_required
def advance_project_stage(request, workflow_id):
    messages.info(request, "Stage advancement functionality coming soon.")
    return redirect('project_central:project_workflow_detail', workflow_id=workflow_id)


# ========== TASK 10: Alert Listing View ==========

@login_required
def alert_list_view(request):
    """Alert listing view with filters and acknowledgment."""
    alerts = Alert.objects.all().order_by('-created_at')

    show_active = request.GET.get('active', 'true') == 'true'
    if show_active:
        alerts = alerts.filter(is_active=True)

    show_unacknowledged = request.GET.get('unacknowledged', 'false') == 'true'
    if show_unacknowledged:
        alerts = alerts.filter(is_acknowledged=False)

    alert_type_filter = request.GET.get('alert_type')
    if alert_type_filter:
        alerts = alerts.filter(alert_type=alert_type_filter)

    severity_filter = request.GET.get('severity')
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)

    severity_counts = Alert.get_unacknowledged_count_by_severity()

    context = {
        'alerts': alerts,
        'severity_counts': severity_counts,
        'alert_types': Alert.ALERT_TYPES,
        'severity_levels': Alert.SEVERITY_LEVELS,
        'show_active': show_active,
        'show_unacknowledged': show_unacknowledged,
        'alert_type_filter': alert_type_filter,
        'severity_filter': severity_filter,
    }

    return render(request, 'project_central/alert_list.html', context)


@login_required
def alert_detail_view(request, alert_id):
    """Show alert details."""
    alert = get_object_or_404(Alert, id=alert_id)
    context = {'alert': alert}
    return render(request, 'project_central/alert_detail.html', context)


@login_required
def acknowledge_alert(request, alert_id):
    """Acknowledge an alert."""
    alert = get_object_or_404(Alert, id=alert_id)

    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        alert.acknowledge(request.user, notes)
        messages.success(request, f"Alert '{alert.title}' has been acknowledged.")
        return redirect('project_central:alert_list')

    return render(request, 'project_central/acknowledge_alert.html', {'alert': alert})


@login_required
def bulk_acknowledge_alerts(request):
    messages.info(request, "Bulk acknowledge functionality coming soon.")
    return redirect('project_central:alert_list')


# ========== TASK 11: Budget Planning Dashboard ==========

@login_required
def budget_planning_dashboard(request):
    """Basic budget planning dashboard - budget allocation, utilization by sector/source."""
    current_year = timezone.now().year
    fiscal_year = request.GET.get('fiscal_year', current_year)

    try:
        fiscal_year = int(fiscal_year)
    except (ValueError, TypeError):
        fiscal_year = current_year

    budget_ceilings = BudgetCeiling.objects.filter(fiscal_year=fiscal_year, is_active=True).order_by('sector', 'funding_source')

    sector_allocation = MonitoringEntry.objects.filter(fiscal_year=fiscal_year).values('sector').annotate(
        total_allocation=Sum('budget_allocation'),
        ppa_count=Count('id')
    ).order_by('-total_allocation')

    source_allocation = MonitoringEntry.objects.filter(fiscal_year=fiscal_year).values('funding_source').annotate(
        total_allocation=Sum('budget_allocation'),
        ppa_count=Count('id')
    ).order_by('-total_allocation')

    total_allocated = MonitoringEntry.objects.filter(fiscal_year=fiscal_year).aggregate(total=Sum('budget_allocation'))['total'] or 0

    scenarios = BudgetScenario.objects.filter(fiscal_year=fiscal_year).order_by('-is_baseline', '-created_at')

    context = {
        'fiscal_year': fiscal_year,
        'current_year': current_year,
        'budget_ceilings': budget_ceilings,
        'sector_allocation': sector_allocation,
        'source_allocation': source_allocation,
        'total_allocated': total_allocated,
        'scenarios': scenarios,
    }

    return render(request, 'project_central/budget_planning_dashboard.html', context)


# ========== Additional View Stubs (Phases 2-8) ==========

@login_required
def me_analytics_dashboard(request):
    """M&E Analytics Dashboard with comprehensive project metrics."""
    from .services import AnalyticsService

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get('fiscal_year', current_year))

    # Get comprehensive dashboard data
    dashboard_data = AnalyticsService.get_dashboard_summary(fiscal_year)

    context = {
        'fiscal_year': fiscal_year,
        'current_year': current_year,
        'budget_by_sector': dashboard_data['budget_by_sector'],
        'budget_by_source': dashboard_data['budget_by_source'],
        'budget_by_region': dashboard_data['budget_by_region'],
        'utilization_rates': dashboard_data['utilization_rates'],
        'cost_effectiveness': dashboard_data['cost_effectiveness'],
        'workflow_performance': dashboard_data['workflow_performance'],
    }

    return render(request, 'project_central/me_analytics_dashboard.html', context)


@login_required
def sector_analytics(request, sector):
    """Detailed analytics for a specific sector."""
    from .services import AnalyticsService

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get('fiscal_year', current_year))

    # Get sector-specific data
    budget_allocation = AnalyticsService.get_budget_allocation_by_sector(fiscal_year)
    cost_effectiveness = AnalyticsService.get_cost_effectiveness_metrics(sector=sector, fiscal_year=fiscal_year)

    # Filter for this sector
    sector_data = next((s for s in budget_allocation['sectors'] if s['sector'] == sector), None)

    if not sector_data:
        messages.warning(request, f"No data found for sector: {sector}")
        return redirect('project_central:me_analytics_dashboard')

    # Get projects in this sector
    ppas = MonitoringEntry.objects.filter(
        sector=sector,
        fiscal_year=fiscal_year
    ).order_by('-budget_allocation')

    context = {
        'sector': sector,
        'fiscal_year': fiscal_year,
        'sector_data': sector_data,
        'cost_effectiveness': cost_effectiveness,
        'ppas': ppas,
    }

    return render(request, 'project_central/sector_analytics.html', context)


@login_required
def geographic_analytics(request):
    """Geographic distribution of budget and projects."""
    from .services import AnalyticsService

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get('fiscal_year', current_year))

    budget_by_region = AnalyticsService.get_budget_allocation_by_region(fiscal_year)

    context = {
        'fiscal_year': fiscal_year,
        'budget_by_region': budget_by_region,
    }

    return render(request, 'project_central/geographic_analytics.html', context)


@login_required
def policy_analytics(request, policy_id):
    """Analytics for a specific policy recommendation."""
    from policy_tracking.models import PolicyRecommendation

    policy = get_object_or_404(PolicyRecommendation, id=policy_id)

    # Find needs linked to this policy
    linked_needs = policy.linked_needs.all()

    # Find workflows for those needs
    workflows = ProjectWorkflow.objects.filter(primary_need__in=linked_needs)

    # Find PPAs linked to those needs
    ppas = MonitoringEntry.objects.filter(linked_need__in=linked_needs)

    # Calculate budget allocated to this policy
    total_budget = ppas.aggregate(total=Sum('budget_allocation'))['total'] or 0

    context = {
        'policy': policy,
        'linked_needs': linked_needs,
        'workflows': workflows,
        'ppas': ppas,
        'total_budget': total_budget,
        'needs_count': linked_needs.count(),
        'ppas_count': ppas.count(),
    }

    return render(request, 'project_central/policy_analytics.html', context)


@login_required
def report_list_view(request):
    """List of available reports."""
    report_types = [
        {'name': 'Portfolio Performance Report', 'url': 'project_central:generate_portfolio_report'},
        {'name': 'Budget Utilization Report', 'url': 'project_central:generate_budget_execution_report'},
        {'name': 'Workflow Progress Report', 'url': 'project_central:generate_needs_impact_report'},
        {'name': 'Cost-Effectiveness Report', 'url': 'project_central:generate_policy_report'},
    ]

    context = {'report_types': report_types}
    return render(request, 'project_central/report_list.html', context)


@login_required
def generate_portfolio_report(request):
    """Generate portfolio performance report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get('fiscal_year', current_year))
    output_format = request.GET.get('format', 'dict')

    try:
        if output_format == 'csv':
            report_data = ReportGenerator.generate_portfolio_report(fiscal_year, output_format='csv')
            response = HttpResponse(report_data.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="portfolio_report_{fiscal_year}.csv"'
            return response

        else:
            # Display in HTML
            report_data = ReportGenerator.generate_portfolio_report(fiscal_year, output_format='dict')
            context = {
                'report_data': report_data,
                'fiscal_year': fiscal_year,
            }
            return render(request, 'project_central/reports/portfolio_report.html', context)

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect('project_central:report_list')


@login_required
def generate_needs_impact_report(request):
    """Generate workflow progress report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get('fiscal_year', current_year))
    output_format = request.GET.get('format', 'dict')

    try:
        if output_format == 'csv':
            report_data = ReportGenerator.generate_workflow_progress_report(fiscal_year, output_format='csv')
            response = HttpResponse(report_data.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="workflow_progress_{fiscal_year}.csv"'
            return response

        else:
            report_data = ReportGenerator.generate_workflow_progress_report(fiscal_year, output_format='dict')
            context = {
                'report_data': report_data,
                'fiscal_year': fiscal_year,
            }
            return render(request, 'project_central/reports/workflow_progress_report.html', context)

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect('project_central:report_list')


@login_required
def generate_policy_report(request):
    """Generate cost-effectiveness report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get('fiscal_year', current_year))
    output_format = request.GET.get('format', 'dict')

    try:
        if output_format == 'csv':
            report_data = ReportGenerator.generate_cost_effectiveness_report(fiscal_year, output_format='csv')
            response = HttpResponse(report_data.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="cost_effectiveness_{fiscal_year}.csv"'
            return response

        else:
            report_data = ReportGenerator.generate_cost_effectiveness_report(fiscal_year, output_format='dict')
            context = {
                'report_data': report_data,
                'fiscal_year': fiscal_year,
            }
            return render(request, 'project_central/reports/cost_effectiveness_report.html', context)

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect('project_central:report_list')


@login_required
def generate_mao_report(request):
    """Generate MAO coordination report."""
    # Future implementation: MAO-specific reporting
    messages.info(request, "MAO-specific reporting coming soon.")
    return redirect('project_central:report_list')


@login_required
def generate_budget_execution_report(request):
    """Generate budget utilization report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get('fiscal_year', current_year))
    sector = request.GET.get('sector')
    output_format = request.GET.get('format', 'dict')

    try:
        if output_format == 'csv':
            report_data = ReportGenerator.generate_budget_utilization_report(fiscal_year, sector, output_format='csv')
            response = HttpResponse(report_data.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="budget_utilization_{fiscal_year}.csv"'
            return response

        else:
            report_data = ReportGenerator.generate_budget_utilization_report(fiscal_year, sector, output_format='dict')
            context = {
                'report_data': report_data,
                'fiscal_year': fiscal_year,
                'sector': sector,
            }
            return render(request, 'project_central/reports/budget_utilization_report.html', context)

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect('project_central:report_list')


@login_required
def report_detail_view(request, report_id):
    messages.info(request, "Report detail view coming in Phase 5.")
    return redirect('project_central:portfolio_dashboard')


@login_required
def download_report(request, report_id):
    messages.info(request, "Report download coming in Phase 5.")
    return redirect('project_central:portfolio_dashboard')


@login_required
def my_tasks_with_projects(request):
    from django.db.models import Q

    user = request.user
    today = timezone.now().date()

    base_filter = (
        Q(assignees=user)
        | Q(created_by=user)
        | Q(teams__memberships__user=user, teams__memberships__is_active=True)
    )

    tasks_qs = (
        StaffTask.objects.filter(base_filter)
        .filter(Q(linked_workflow__isnull=False) | Q(related_ppa__isnull=False))
        .select_related(
            "linked_workflow",
            "linked_workflow__primary_need",
            "linked_workflow__ppa",
            "related_ppa",
        )
        .prefetch_related("assignees", "teams")
        .distinct()
    )

    status_filter = request.GET.get("status", "")
    stage_filter = request.GET.get("stage", "")
    domain_filter = request.GET.get("domain", "")
    search_query = (request.GET.get("q") or "").strip()
    show_overdue = request.GET.get("overdue") == "1"

    valid_statuses = {value for value, _ in StaffTask.STATUS_CHOICES}
    if status_filter in valid_statuses:
        tasks_qs = tasks_qs.filter(status=status_filter)
    if stage_filter:
        tasks_qs = tasks_qs.filter(linked_workflow__current_stage=stage_filter)
    valid_domains = {value for value, _ in StaffTask.DOMAIN_CHOICES}
    if domain_filter in valid_domains:
        tasks_qs = tasks_qs.filter(domain=domain_filter)
    if show_overdue:
        tasks_qs = tasks_qs.filter(
            due_date__lt=today,
            status__in=[
                StaffTask.STATUS_NOT_STARTED,
                StaffTask.STATUS_IN_PROGRESS,
                StaffTask.STATUS_AT_RISK,
            ],
        )
    if search_query:
        tasks_qs = tasks_qs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(linked_workflow__primary_need__title__icontains=search_query)
            | Q(related_ppa__title__icontains=search_query)
        )

    def sort_key(task: StaffTask):
        due = task.due_date or date.max
        return (due, task.priority, task.title.lower())

    task_list = sorted(tasks_qs, key=sort_key)

    summary = {
        "total": len(task_list),
        "overdue": sum(1 for task in task_list if task.is_overdue),
        "in_progress": sum(1 for task in task_list if task.status == StaffTask.STATUS_IN_PROGRESS),
        "completed": sum(1 for task in task_list if task.status == StaffTask.STATUS_COMPLETED),
    }

    context = {
        "tasks": task_list,
        "summary": summary,
        "status_choices": StaffTask.STATUS_CHOICES,
        "stage_choices": ProjectWorkflow.WORKFLOW_STAGES,
        "domain_choices": StaffTask.DOMAIN_CHOICES,
        "current_filters": {
            "status": status_filter,
            "stage": stage_filter,
            "domain": domain_filter,
            "overdue": "1" if show_overdue else "0",
            "q": search_query,
        },
    }

    if request.headers.get("HX-Request"):
        return render(
            request,
            "project_central/partials/project_task_table.html",
            context,
        )

    return render(request, "project_central/my_tasks.html", context)


@login_required
def generate_workflow_tasks(request, workflow_id):
    workflow = get_object_or_404(ProjectWorkflow, id=workflow_id)
    ppa = workflow.ppa

    from django.db import transaction

    template_map = {
        "need_identification": "project_need_validation",
        "need_validation": "project_need_validation",
        "policy_linkage": "project_policy_integration",
        "mao_coordination": "project_mao_coordination",
        "budget_planning": "project_budget_planning",
        "approval": "project_budget_approval",
        "implementation": "project_implementation",
        "monitoring": "project_monitoring",
        "completion": "project_completion",
    }

    template_name = template_map.get(workflow.current_stage, "project_generic_stage")

    base_filters = {
        "created_from_template__name": template_name,
        "linked_workflow": workflow,
    }

    if StaffTask.objects.filter(**base_filters).exists():
        messages.info(request, "Workflow tasks for this stage already exist.")
        return redirect('project_central:project_workflow_detail', workflow_id=workflow_id)

    start_date = workflow.initiated_date or timezone.now().date()
    context_kwargs = {
        "linked_workflow": workflow,
        "related_ppa": ppa,
        "workflow_stage": workflow.current_stage,
        "created_by": request.user,
        "start_date": start_date,
        "auto_generated": True,
        "idempotency_filter": {"linked_workflow": workflow},
    }

    if workflow.primary_need:
        context_kwargs["related_need"] = workflow.primary_need
        context_kwargs["need_title"] = workflow.primary_need.title

    booking_specs = None
    if request.GET.get("auto_resource") == "1":
        booking_specs = {
            'default': [
                {
                    'resource_name': request.GET.get('resource_name', 'Projector'),
                    'start_offset_days': 0,
                    'start_offset_hours': 2,
                    'duration_hours': 2,
                    'notes': f"Workflow stage: {workflow.get_current_stage_display()}",
                }
            ]
        }
        context_kwargs['resource_bookings'] = booking_specs

    try:
        with transaction.atomic():
            tasks = create_tasks_from_template(template_name, **context_kwargs)
    except ValidationError as exc:
        messages.error(request, f"Task generation failed: {exc}")
    else:
        if tasks:
            messages.success(
                request,
                f"Created {len(tasks)} tasks for stage {workflow.get_current_stage_display()}.",
            )
        else:
            messages.warning(
                request,
                "No tasks were generated for the current workflow stage.",
            )

    return redirect('project_central:project_workflow_detail', workflow_id=workflow_id)


@login_required
def budget_approval_dashboard(request):
    """Budget approval dashboard showing PPAs at each approval stage."""
    from .services import BudgetApprovalService

    # Get PPAs in each approval stage
    technical_review = MonitoringEntry.objects.filter(
        approval_status=MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
    ).order_by('-created_at')

    budget_review = MonitoringEntry.objects.filter(
        approval_status=MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW
    ).order_by('-created_at')

    stakeholder_consultation = MonitoringEntry.objects.filter(
        approval_status=MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION
    ).order_by('-created_at')

    executive_approval = MonitoringEntry.objects.filter(
        approval_status=MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL
    ).order_by('-created_at')

    # Get approval metrics
    total_pending = (
        technical_review.count() +
        budget_review.count() +
        stakeholder_consultation.count() +
        executive_approval.count()
    )

    recently_approved = MonitoringEntry.objects.filter(
        approval_status__in=[
            MonitoringEntry.APPROVAL_STATUS_APPROVED,
            MonitoringEntry.APPROVAL_STATUS_ENACTED,
        ]
    ).order_by('-executive_approved_at')[:10]

    context = {
        'technical_review': technical_review,
        'budget_review': budget_review,
        'stakeholder_consultation': stakeholder_consultation,
        'executive_approval': executive_approval,
        'total_pending': total_pending,
        'recently_approved': recently_approved,
    }

    return render(request, 'project_central/budget_approval_dashboard.html', context)


@login_required
def review_budget_approval(request, ppa_id):
    """Review a PPA for budget approval."""
    from .services import BudgetApprovalService

    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)

    # Validate budget ceiling compliance
    is_valid, errors = BudgetApprovalService.validate_budget_ceiling(ppa)

    # Get approval history
    approval_history = ppa.approval_history if ppa.approval_history else []

    context = {
        'ppa': ppa,
        'is_ceiling_compliant': is_valid,
        'ceiling_errors': errors,
        'approval_history': approval_history,
        'can_approve': BudgetApprovalService.can_advance_approval_stage(ppa, request.user),
    }

    return render(request, 'project_central/review_budget_approval.html', context)


@login_required
def approve_budget(request, ppa_id):
    """Approve a PPA and advance approval stage."""
    from .services import BudgetApprovalService

    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)

    if request.method == 'POST':
        notes = request.POST.get('notes', '')

        # Determine next stage based on current status
        next_stage_map = {
            MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW: MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW,
            MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW: MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION,
            MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION: MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL,
            MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL: MonitoringEntry.APPROVAL_STATUS_APPROVED,
        }

        next_stage = next_stage_map.get(ppa.approval_status)

        if next_stage:
            try:
                BudgetApprovalService.advance_approval_stage(ppa, next_stage, request.user, notes)
                messages.success(request, f"PPA '{ppa.title}' has been approved and advanced to next stage.")
                return redirect('project_central:budget_approval_dashboard')
            except ValueError as e:
                messages.error(request, f"Approval failed: {str(e)}")
                return redirect('project_central:review_budget_approval', ppa_id=ppa_id)
        else:
            messages.error(request, "Cannot determine next approval stage.")
            return redirect('project_central:review_budget_approval', ppa_id=ppa_id)

    return redirect('project_central:review_budget_approval', ppa_id=ppa_id)


@login_required
def reject_budget(request, ppa_id):
    """Reject a PPA with reason."""
    from .services import BudgetApprovalService

    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')

        if not reason:
            messages.error(request, "Rejection reason is required.")
            return redirect('project_central:review_budget_approval', ppa_id=ppa_id)

        try:
            BudgetApprovalService.reject_approval(ppa, request.user, reason)
            messages.success(request, f"PPA '{ppa.title}' has been rejected.")
            return redirect('project_central:budget_approval_dashboard')
        except Exception as e:
            messages.error(request, f"Rejection failed: {str(e)}")
            return redirect('project_central:review_budget_approval', ppa_id=ppa_id)

    return redirect('project_central:review_budget_approval', ppa_id=ppa_id)
