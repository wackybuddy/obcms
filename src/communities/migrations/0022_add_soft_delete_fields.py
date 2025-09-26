"""Add soft-delete fields to community profile models."""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("communities", "0021_add_geographic_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="municipalitycoverage",
            name="deleted_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Timestamp when this record was archived for removal.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="municipalitycoverage",
            name="deleted_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who archived this record for deletion review.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="deleted_municipalitycoverages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="municipalitycoverage",
            name="is_deleted",
            field=models.BooleanField(
                default=False,
                help_text="Indicates whether this record has been archived instead of fully removed.",
            ),
        ),
        migrations.AddField(
            model_name="obccommunity",
            name="deleted_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Timestamp when this record was archived for removal.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="obccommunity",
            name="deleted_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who archived this record for deletion review.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="deleted_obccommunitys",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="obccommunity",
            name="is_deleted",
            field=models.BooleanField(
                default=False,
                help_text="Indicates whether this record has been archived instead of fully removed.",
            ),
        ),
    ]
