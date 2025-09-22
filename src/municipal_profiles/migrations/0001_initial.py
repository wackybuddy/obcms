from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("common", "0002_region_province_municipality_barangay"),
        ("communities", "0006_remove_obccommunity_employment_opportunities_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MunicipalOBCProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "aggregated_metrics",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Roll-up metrics derived from all barangay OBC records.",
                    ),
                ),
                (
                    "reported_metrics",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Municipal level metrics manually encoded by LGU partners.",
                    ),
                ),
                (
                    "reported_notes",
                    models.TextField(
                        blank=True,
                        help_text="Narrative notes accompanying the latest municipal submission.",
                    ),
                ),
                (
                    "last_aggregated_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Timestamp of the most recent automatic aggregation run.",
                        null=True,
                    ),
                ),
                (
                    "last_reported_update",
                    models.DateTimeField(
                        blank=True,
                        help_text="Timestamp of the most recent manual municipal update.",
                        null=True,
                    ),
                ),
                (
                    "aggregation_version",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Version counter for the aggregation pipeline.",
                    ),
                ),
                (
                    "is_locked",
                    models.BooleanField(
                        default=False,
                        help_text="Lock manual edits while undergoing validation or review.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "municipality",
                    models.OneToOneField(
                        help_text="Municipality or city covered by this profile.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="obc_profile",
                        to="common.municipality",
                    ),
                ),
            ],
            options={
                "verbose_name": "Municipal OBC Profile",
                "verbose_name_plural": "Municipal OBC Profiles",
                "ordering": ["municipality__province__region__code", "municipality__name"],
            },
        ),
        migrations.CreateModel(
            name="MunicipalOBCProfileHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "change_type",
                    models.CharField(
                        choices=[
                            ("reported", "Manual municipal update"),
                            ("aggregated", "Barangay aggregation"),
                            ("import", "Data import"),
                        ],
                        max_length=20,
                    ),
                ),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="municipal_profile_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history_entries",
                        to="municipal_profiles.municipalobcprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "Municipal OBC Profile History",
                "verbose_name_plural": "Municipal OBC Profile History",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OBCCommunityHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                (
                    "snapshot",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("manual", "Manual update"),
                            ("import", "Data import"),
                            ("aggregation", "System aggregation"),
                        ],
                        max_length=20,
                    ),
                ),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="obc_community_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "community",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history_entries",
                        to="communities.obccommunity",
                    ),
                ),
            ],
            options={
                "verbose_name": "OBC Community History",
                "verbose_name_plural": "OBC Community History",
                "ordering": ["-created_at"],
            },
        ),
    ]
