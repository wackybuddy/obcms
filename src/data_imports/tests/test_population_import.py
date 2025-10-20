"""Tests for the population hierarchy import command."""

import tempfile
from pathlib import Path

import pytest

try:
    from django.core.management import call_command
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for population import tests",
        allow_module_level=True,
    )

from common.models import Barangay, Municipality, Province, Region

pytestmark = pytest.mark.component


@pytest.mark.django_db
def test_import_creates_and_updates_hierarchy() -> None:
    """Verify that the import command builds and updates the location hierarchy."""
    Region.objects.all().delete()
    Province.objects.all().delete()
    Municipality.objects.all().delete()
    Barangay.objects.all().delete()

    with tempfile.TemporaryDirectory() as dataset_tempdir:
        dataset_dir = Path(dataset_tempdir)
        dataset_file = dataset_dir / "region_ix_population_raw.txt"

        # Initial import
        initial_content = (
            "TEST PROVINCE\t100\n"
            "\tSample City\t60\n"
            "\t\tBarangay Uno\t30\n"
            "\t\tBarangay Dos\t30\n"
            "\tSample Town\t40\n"
            "\t\tBarangay Tres\t40\n"
        )
        dataset_file.write_text(initial_content, encoding="utf-8")

        call_command(
            "import_population_hierarchy",
            "--regions",
            "IX",
            "--dataset-dir",
            str(dataset_dir),
        )

        region = Region.objects.get(code="IX")
        assert region.name == "Zamboanga Peninsula"

        province = Province.objects.get(name="Test Province")
        assert province.population_total == 100
        assert province.region == region
        assert province.code

        city = Municipality.objects.get(name="Sample City")
        assert city.population_total == 60
        assert city.municipality_type == "city"

        town = Municipality.objects.get(name="Sample Town")
        assert town.population_total == 40
        assert town.municipality_type == "municipality"

        barangay = Barangay.objects.get(name="Barangay Tres")
        assert barangay.population_total == 40

        # Update import
        updated_content = (
            "TEST PROVINCE\t120\n"
            "\tSample City\t70\n"
            "\t\tBarangay Uno\t35\n"
            "\t\tBarangay Dos\t35\n"
            "\tSample Town\t50\n"
            "\t\tBarangay Tres\t50\n"
        )
        dataset_file.write_text(updated_content, encoding="utf-8")

        call_command(
            "import_population_hierarchy",
            "--regions",
            "IX",
            "--dataset-dir",
            str(dataset_dir),
        )

        province.refresh_from_db()
        assert province.population_total == 120

        city.refresh_from_db()
        assert city.population_total == 70

        barangay.refresh_from_db()
        assert barangay.population_total == 50

        assert Region.objects.count() == 1
        assert Province.objects.count() == 1
        assert Municipality.objects.count() == 2
        assert Barangay.objects.count() == 3
