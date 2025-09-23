# Generated migration for GeographicDataLayer administrative relations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_add_geographic_boundaries'),
        ('mana', '0007_alter_workshopoutput_output_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='geographicdatalayer',
            name='region',
            field=models.ForeignKey(
                blank=True,
                help_text='Region this layer covers or relates to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='geographic_layers',
                to='common.region'
            ),
        ),
        migrations.AddField(
            model_name='geographicdatalayer',
            name='province',
            field=models.ForeignKey(
                blank=True,
                help_text='Province this layer covers or relates to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='geographic_layers',
                to='common.province'
            ),
        ),
        migrations.AddField(
            model_name='geographicdatalayer',
            name='municipality',
            field=models.ForeignKey(
                blank=True,
                help_text='Municipality this layer covers or relates to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='geographic_layers',
                to='common.municipality'
            ),
        ),
        migrations.AddField(
            model_name='geographicdatalayer',
            name='barangay',
            field=models.ForeignKey(
                blank=True,
                help_text='Barangay this layer covers or relates to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='geographic_layers',
                to='common.barangay'
            ),
        ),
    ]