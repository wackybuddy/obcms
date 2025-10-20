from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0023_monitoringentry_monitoring_entry_budget_allocation_within_ceiling_and_more'),
        ('budget_preparation', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budgetproposal',
            old_name='total_proposed_budget',
            new_name='total_requested_budget',
        ),
        migrations.AddField(
            model_name='budgetproposal',
            name='total_approved_budget',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Total budget amount approved (₱)',
                max_digits=15,
                null=True,
            ),
        ),
        migrations.RenameField(
            model_name='programbudget',
            old_name='allocated_amount',
            new_name='requested_amount',
        ),
        migrations.AddField(
            model_name='programbudget',
            name='approved_amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Approved budget amount after review (₱)',
                max_digits=15,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='programbudget',
            name='priority_rank',
            field=models.PositiveIntegerField(
                default=1,
                help_text='Rank order for prioritization (1 = highest priority)',
            ),
        ),
        migrations.AddField(
            model_name='programbudget',
            name='monitoring_entry',
            field=models.ForeignKey(
                blank=True,
                help_text='Linked monitoring entry (PPA) for execution tracking',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='program_budgets',
                to='monitoring.monitoringentry',
            ),
        ),
        migrations.AddField(
            model_name='budgetlineitem',
            name='sub_category',
            field=models.CharField(
                blank=True,
                help_text='Optional sub-category (e.g., salaries, supplies)',
                max_length=100,
            ),
        ),
        migrations.AddIndex(
            model_name='programbudget',
            index=models.Index(
                fields=['budget_proposal', 'priority_rank'],
                name='budget_prep_budget__priority_rank_idx',
            ),
        ),
    ]
