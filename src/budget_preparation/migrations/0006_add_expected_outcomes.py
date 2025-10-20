from django.db import migrations, models


def column_exists(schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return any(row[1] == column_name for row in cursor.fetchall())


class AddFieldIfMissing(migrations.AddField):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        if column_exists(schema_editor, table_name, self.name):
            return
        super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        if not column_exists(schema_editor, table_name, self.name):
            return
        super().database_backwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):

    dependencies = [
        ('budget_preparation', '0005_programbudget_legacy_fields'),
    ]

    operations = [
        AddFieldIfMissing(
            model_name='programbudget',
            name='expected_outcomes',
            field=models.TextField(
                blank=True,
                help_text='Expected outcomes and beneficiaries',
            ),
        ),
    ]
