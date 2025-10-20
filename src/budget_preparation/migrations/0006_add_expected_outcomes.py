from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_preparation', '0005_programbudget_legacy_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='programbudget',
            name='expected_outcomes',
            field=models.TextField(
                blank=True,
                help_text='Expected outcomes and beneficiaries',
            ),
        ),
    ]
