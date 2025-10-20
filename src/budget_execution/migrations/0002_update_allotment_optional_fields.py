from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget_execution', '0001_initial'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allotment',
            name='released_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Budget execution user who released the allotment',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='allotments_released',
                to='common.user',
            ),
        ),
        migrations.AlterField(
            model_name='disbursement',
            name='disbursed_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who processed the disbursement',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='disbursements_processed',
                to='common.user',
            ),
        ),
        migrations.AlterField(
            model_name='obligation',
            name='work_item',
            field=models.ForeignKey(
                blank=True,
                help_text='Execution work item covered by this obligation',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='obligations',
                to='budget_execution.workitem',
            ),
        ),
        migrations.AlterField(
            model_name='obligation',
            name='obligated_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who recorded the obligation',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='obligations_recorded',
                to='common.user',
            ),
        ),
        migrations.AlterField(
            model_name='obligation',
            name='payee',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Payee or supplier name',
                max_length=255,
            ),
        ),
    ]
