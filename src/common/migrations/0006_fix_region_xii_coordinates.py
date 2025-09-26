from django.db import migrations


def _update_province_centroids(apps, schema_editor):
    Province = apps.get_model("common", "Province")

    updates = {
        "Sarangani": {
            "center": [125.275278, 5.874722],
            "bbox": [124.3183654, 5.4700879, 125.5582809, 6.540403],
        },
        "Sultan Kudarat": {
            "center": [124.3271496, 6.5556705],
            "bbox": [123.8845037, 5.9795979, 125.079174, 6.886049],
        },
    }

    for name, payload in updates.items():
        (
            Province.objects.filter(name=name)
            .update(
                center_coordinates=payload["center"],
                bounding_box=payload["bbox"],
            )
        )


def _reverse_province_centroids(apps, schema_editor):
    # No-op: original values were inaccurate and intentionally replaced.
    pass


def _update_barangay_centroids(apps, schema_editor):
    Barangay = apps.get_model("common", "Barangay")

    updates = {
        "XII-COTABATO-MLANG-KATIPUNAN": {
            "center": [124.9211486, 7.0150888],
            "bbox": [124.9011486, 6.9950888, 124.9411486, 7.0350888],
        },
        "XII-COTABATO-ARAKAN-KATIPUNAN": {
            "center": [125.2351242, 7.4223653],
            "bbox": [125.2151242, 7.4023653, 125.2551242, 7.4423653],
        },
        "XII-COTABATO-MATALAM-SANTA-MARIA": {
            "center": [124.9892127, 7.2210551],
            "bbox": [124.9692127, 7.2010551, 125.0092127, 7.2410551],
        },
    }

    for code, payload in updates.items():
        (
            Barangay.objects.filter(code=code)
            .update(
                center_coordinates=payload["center"],
                bounding_box=payload["bbox"],
            )
        )


def _reverse_barangay_centroids(apps, schema_editor):
    # No-op: original values were inaccurate and intentionally replaced.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0005_add_geographic_boundaries"),
    ]

    operations = [
        migrations.RunPython(
            _update_province_centroids,
            reverse_code=_reverse_province_centroids,
        ),
        migrations.RunPython(
            _update_barangay_centroids,
            reverse_code=_reverse_barangay_centroids,
        ),
    ]
