from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_preparation', '0003_budgetproposal_schema_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetlineitem',
            name='justification',
            field=models.TextField(
                blank=True,
                help_text='Why this line item is required',
            ),
        ),
    ]
