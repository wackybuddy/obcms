from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0001_initial'),
        ('budget_preparation', '0004_budgetlineitem_add_justification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programbudget',
            name='program',
            field=models.ForeignKey(
                blank=True,
                editable=False,
                help_text='Legacy field retained for compatibility with pre-BMMS workflows',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='legacy_budget_allocations',
                to='planning.workplanobjective',
            ),
        ),
        migrations.AlterField(
            model_name='programbudget',
            name='priority_level',
            field=models.CharField(
                blank=True,
                editable=False,
                help_text='Legacy priority field retained for compatibility',
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='programbudget',
            name='expected_outputs',
            field=models.TextField(
                blank=True,
                editable=False,
                help_text='Legacy expected outputs field',
                null=True,
            ),
        ),
    ]
