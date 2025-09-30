from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coordination", "0004_partnership_partnershipsignatory_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who created this organization record",
                null=True,
                on_delete=models.PROTECT,
                related_name="created_organizations",
                to="common.user",
            ),
        ),
    ]
