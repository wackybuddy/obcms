from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0014_migrate_task_assignments_to_stafftask"),
    ]

    operations = [
        migrations.DeleteModel(
            name="MonitoringEntryTaskAssignment",
        ),
    ]
