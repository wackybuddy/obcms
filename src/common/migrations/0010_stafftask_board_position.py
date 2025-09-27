from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0009_staff_profile_job_design"),
    ]

    operations = [
        migrations.AddField(
            model_name="stafftask",
            name="board_position",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Relative ordering for Kanban board presentation.",
            ),
        ),
    ]
