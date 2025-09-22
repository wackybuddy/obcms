from django.db import connection, migrations, models


def ensure_population_fields(apps, schema_editor):
    """Add population_total columns when they are missing due to legacy databases."""

    cursor = connection.cursor()
    introspection = connection.introspection

    def column_exists(table_name: str, column_name: str) -> bool:
        try:
            description = introspection.get_table_description(cursor, table_name)
        except Exception:
            return False
        return any(col.name == column_name for col in description)

    def add_column_if_missing(model_label: str, table_name: str, field_name: str):
        if column_exists(table_name, field_name):
            return

        model = apps.get_model("common", model_label)
        field = models.PositiveIntegerField(default=0)
        field.set_attributes_from_name(field_name)
        schema_editor.add_field(model, field)

        # Ensure nulls are backfilled to zero for compatibility
        cursor.execute(f"UPDATE {table_name} SET {field_name} = 0 WHERE {field_name} IS NULL")

    add_column_if_missing("Barangay", "common_barangay", "population_total")
    add_column_if_missing("Municipality", "common_municipality", "population_total")
    add_column_if_missing("Province", "common_province", "population_total")


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0003_add_population_fields"),
    ]

    operations = [migrations.RunPython(ensure_population_fields, migrations.RunPython.noop)]
