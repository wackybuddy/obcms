from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0011_monitoringentry_approval_history_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="monitoringentry",
            name="milestone_dates",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text=(
                    "Structured milestone entries: "
                    '[{"date": "2025-10-15", "title": "Technical hearing", "status": "upcoming"}]'
                ),
            ),
        ),
    ]
