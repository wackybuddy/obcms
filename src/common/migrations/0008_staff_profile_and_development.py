from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0007_staffteam_stafftask_staffteammembership"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffProfile",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employment_status", models.CharField(choices=[("active", "Active"), ("on_leave", "On Leave"), ("inactive", "Inactive")], default="active", max_length=20)),
                ("employment_type", models.CharField(blank=True, choices=[("regular", "Regular"), ("contractual", "Contractual"), ("consultant", "Consultant"), ("volunteer", "Volunteer")], max_length=20)),
                ("date_joined_organization", models.DateField(blank=True, null=True)),
                ("primary_location", models.CharField(blank=True, max_length=255)),
                ("core_competencies", models.JSONField(blank=True, default=list)),
                ("leadership_competencies", models.JSONField(blank=True, default=list)),
                ("functional_competencies", models.JSONField(blank=True, default=list)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="staff_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["user__last_name", "user__first_name"],
            },
        ),
        migrations.CreateModel(
            name="StaffDevelopmentPlan",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("competency_focus", models.CharField(blank=True, max_length=150)),
                ("target_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("planned", "Planned"), ("in_progress", "In Progress"), ("completed", "Completed")], default="planned", max_length=20)),
                ("support_needed", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("staff_profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="development_plans", to="common.staffprofile")),
            ],
            options={
                "ordering": ["target_date", "title"],
            },
        ),
        migrations.CreateModel(
            name="TrainingProgram",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("category", models.CharField(blank=True, max_length=150)),
                ("description", models.TextField(blank=True)),
                ("delivery_mode", models.CharField(choices=[("in_person", "In Person"), ("virtual", "Virtual"), ("hybrid", "Hybrid")], default="in_person", max_length=20)),
                ("competency_focus", models.JSONField(blank=True, default=list)),
                ("duration_days", models.PositiveIntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="TrainingEnrollment",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("planned", "Planned"), ("ongoing", "Ongoing"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="planned", max_length=20)),
                ("scheduled_date", models.DateField(blank=True, null=True)),
                ("completion_date", models.DateField(blank=True, null=True)),
                ("evidence_url", models.URLField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("program", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="common.trainingprogram")),
                ("staff_profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="training_enrollments", to="common.staffprofile")),
            ],
            options={
                "ordering": ["-scheduled_date", "program__title"],
            },
        ),
        migrations.CreateModel(
            name="PerformanceTarget",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope", models.CharField(choices=[("staff", "Staff"), ("team", "Team")], max_length=10)),
                ("metric_name", models.CharField(max_length=150)),
                ("performance_standard", models.CharField(blank=True, max_length=255)),
                ("target_value", models.DecimalField(decimal_places=2, max_digits=10)),
                ("actual_value", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("unit", models.CharField(blank=True, max_length=50)),
                ("status", models.CharField(choices=[("on_track", "On Track"), ("at_risk", "At Risk"), ("off_track", "Off Track")], default="on_track", max_length=12)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("staff_profile", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="performance_targets", to="common.staffprofile")),
                ("team", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="performance_targets", to="common.staffteam")),
            ],
            options={
                "ordering": ["-period_end", "metric_name"],
            },
        ),
    ]
