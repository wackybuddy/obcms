from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


def column_exists(schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return any(row[1] == column_name for row in cursor.fetchall())


def add_column_if_missing(schema_editor, table_name, column_name, column_sql):
    if column_exists(schema_editor, table_name, column_name):
        return
    schema_editor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"
    )


def add_strategic_goal_column(apps, schema_editor):
    add_column_if_missing(
        schema_editor,
        'budget_preparation_programbudget',
        'strategic_goal_id',
        'INTEGER REFERENCES planning_strategicgoal(id) DEFERRABLE INITIALLY DEFERRED'
    )


def add_annual_work_plan_column(apps, schema_editor):
    add_column_if_missing(
        schema_editor,
        'budget_preparation_programbudget',
        'annual_work_plan_id',
        'INTEGER REFERENCES planning_annualworkplan(id) DEFERRABLE INITIALLY DEFERRED'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0023_monitoringentry_monitoring_entry_budget_allocation_within_ceiling_and_more'),
        ('planning', '0001_initial'),
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
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_strategic_goal_column, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='programbudget',
                    name='strategic_goal',
                    field=models.ForeignKey(
                        blank=True,
                        help_text='Strategic goal supported by this budget',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='program_budgets',
                        to='planning.strategicgoal',
                    ),
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_annual_work_plan_column, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='programbudget',
                    name='annual_work_plan',
                    field=models.ForeignKey(
                        blank=True,
                        help_text='Annual work plan reference for this program',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='program_budgets',
                        to='planning.annualworkplan',
                    ),
                ),
            ],
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
        migrations.AlterField(
            model_name='programbudget',
            name='justification',
            field=models.TextField(
                blank=True,
                help_text='Justification for budget allocation amount',
            ),
        ),
        migrations.AlterField(
            model_name='programbudget',
            name='expected_outputs',
            field=models.TextField(
                blank=True,
                help_text='Expected deliverables and outputs from this program',
            ),
        ),
        migrations.AddIndex(
            model_name='programbudget',
            index=models.Index(
                fields=['budget_proposal', 'priority_rank'],
                name='budget_prep_budget__priority_rank_idx',
            ),
        ),
        migrations.AlterField(
            model_name='budgetproposal',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('submitted', 'Submitted'),
                    ('under_review', 'Under Review'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='draft',
                help_text='Current status of budget proposal',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='budgetproposal',
            name='fiscal_year',
            field=models.IntegerField(
                help_text='Fiscal year this budget is for (e.g., 2025)',
                validators=[django.core.validators.MinValueValidator(2024)],
            ),
        ),
    ]
