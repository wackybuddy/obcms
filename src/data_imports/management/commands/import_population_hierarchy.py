"""Import region, province, municipality, and barangay population data."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from common.models import Barangay, Municipality, Province, Region

logger = logging.getLogger(__name__)


REGION_DATASETS: Dict[str, Dict[str, str]] = {
    "IX": {
        "name": "Zamboanga Peninsula",
        "filename": "region_ix_population_raw.txt",
    },
    "X": {
        "name": "Northern Mindanao",
        "filename": "region_x_population_raw.txt",
    },
    "XI": {
        "name": "Davao Region",
        "filename": "region_xi_population_raw.txt",
    },
    "XII": {
        "name": "SOCCSKSARGEN",
        "filename": "region_xii_population_raw.txt",
    },
}


LOWERCASE_WORDS = {
    "And",
    "Of",
    "The",
    "Del",
    "De",
    "Y",
}


@dataclass
class BarangayRecord:
    name: str
    population: Optional[int]


@dataclass
class MunicipalityRecord:
    name: str
    population: Optional[int]
    barangays: List[BarangayRecord] = field(default_factory=list)


@dataclass
class ProvinceRecord:
    name: str
    population: Optional[int]
    municipalities: List[MunicipalityRecord] = field(default_factory=list)


def normalise_name(value: str) -> str:
    """Return a consistently formatted name for display and storage."""

    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return cleaned

    titled = cleaned.title()
    words = titled.split(" ")
    for index, word in enumerate(words):
        if index == 0:
            continue
        if word in LOWERCASE_WORDS:
            words[index] = word.lower()
    return " ".join(words)


def parse_population_value(raw_value: str) -> Optional[int]:
    """Convert raw population string to an integer."""

    if raw_value is None:
        return None
    cleaned = raw_value.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        logger.warning("Unable to parse population value '%s'", raw_value)
        return None


def parse_population_file(file_path: Path) -> List[ProvinceRecord]:
    """Parse a raw population text file into structured province records."""

    provinces: List[ProvinceRecord] = []
    current_province: Optional[ProvinceRecord] = None
    current_municipality: Optional[MunicipalityRecord] = None

    if not file_path.exists():
        raise CommandError(f"Dataset file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip()
            if not line:
                continue

            indent_level = len(line) - len(line.lstrip("\t"))
            content = line.lstrip("\t")

            if "\t" in content:
                name_part, population_part = content.rsplit("\t", 1)
            else:
                name_part, population_part = content, ""
            name = normalise_name(name_part)
            population = parse_population_value(population_part)

            if indent_level == 0:
                current_province = ProvinceRecord(name=name, population=population)
                provinces.append(current_province)
                current_municipality = None
            elif indent_level == 1:
                if current_province is None:
                    raise CommandError(
                        f"Municipality encountered before province on line {line_number}"
                    )
                current_municipality = MunicipalityRecord(
                    name=name, population=population
                )
                current_province.municipalities.append(current_municipality)
            elif indent_level == 2:
                if current_municipality is None:
                    raise CommandError(
                        f"Barangay encountered before municipality on line {line_number}"
                    )
                current_municipality.barangays.append(
                    BarangayRecord(name=name, population=population)
                )
            else:
                raise CommandError(
                    f"Unsupported indentation level {indent_level} on line {line_number}"
                )

    return provinces


def build_code(*parts: str) -> str:
    """Generate a unique hierarchical code limited to 64 characters."""

    slug_parts: List[str] = []
    for part in parts:
        slug = slugify(part)
        if slug:
            slug_parts.append(slug.upper())
    code = "-".join(slug_parts)
    return code[:64]


def infer_municipality_type(name: str) -> str:
    """Infer municipality type based on naming conventions."""

    lowered = name.lower()
    if "city" in lowered:
        return "city"
    return "municipality"


class Command(BaseCommand):
    help = "Import population hierarchy data into Region, Province, Municipality, and Barangay tables."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--regions",
            nargs="+",
            help="Optional list of region codes to import (e.g., IX XI). Defaults to all supported regions.",
        )
        parser.add_argument(
            "--dataset-dir",
            help="Override the default dataset directory (useful for testing or alternative data sources).",
        )

    def handle(self, *args, **options) -> None:
        region_codes = options.get("regions") or REGION_DATASETS.keys()
        region_codes = [code.upper() for code in region_codes]

        dataset_dir_option = options.get("dataset_dir")
        if dataset_dir_option:
            dataset_dir = Path(dataset_dir_option)
        else:
            dataset_dir = Path(settings.BASE_DIR) / "data_imports" / "datasets"

        if not dataset_dir.exists():
            raise CommandError(f"Dataset directory does not exist: {dataset_dir}")

        stats = {
            "regions_created": 0,
            "regions_updated": 0,
            "provinces_created": 0,
            "provinces_updated": 0,
            "municipalities_created": 0,
            "municipalities_updated": 0,
            "barangays_created": 0,
            "barangays_updated": 0,
        }

        with transaction.atomic():
            for code in region_codes:
                config = REGION_DATASETS.get(code)
                if not config:
                    raise CommandError(
                        f"Region code '{code}' is not supported. Supported regions: {', '.join(REGION_DATASETS.keys())}"
                    )

                dataset_file = dataset_dir / config["filename"]
                province_records = parse_population_file(dataset_file)
                self.stdout.write(f"Importing {code} from {dataset_file.name}...")
                self._import_region_data(code, config["name"], province_records, stats)

        self.stdout.write(self.style.SUCCESS("Population hierarchy import completed."))
        self.stdout.write(
            "Created: regions={regions_created}, provinces={provinces_created}, municipalities={municipalities_created}, barangays={barangays_created}".format(
                **stats
            )
        )
        self.stdout.write(
            "Updated: regions={regions_updated}, provinces={provinces_updated}, municipalities={municipalities_updated}, barangays={barangays_updated}".format(
                **stats
            )
        )

    def _import_region_data(
        self,
        region_code: str,
        region_name: str,
        provinces: Iterable[ProvinceRecord],
        stats: Dict[str, int],
    ) -> None:
        region, created = Region.objects.get_or_create(
            code=region_code,
            defaults={"name": region_name, "is_active": True},
        )

        region_updated = False
        if region.name != region_name:
            region.name = region_name
            region_updated = True
        if not region.is_active:
            region.is_active = True
            region_updated = True
        if region_updated:
            region.save()

        if created:
            stats["regions_created"] += 1
        elif region_updated:
            stats["regions_updated"] += 1

        for province_record in provinces:
            province_code = build_code(region.code, province_record.name)
            province, province_created = Province.objects.get_or_create(
                region=region,
                name=province_record.name,
                defaults={
                    "code": province_code,
                    "population_total": province_record.population,
                    "is_active": True,
                },
            )

            province_changed = False
            if province.population_total != province_record.population:
                province.population_total = province_record.population
                province_changed = True
            if not province.is_active:
                province.is_active = True
                province_changed = True
            if not province.code:
                province.code = province_code
                province_changed = True
            if province_changed:
                province.save()

            if province_created:
                stats["provinces_created"] += 1
            elif province_changed:
                stats["provinces_updated"] += 1

            for municipality_record in province_record.municipalities:
                municipality_code = build_code(
                    province.code or province_code, municipality_record.name
                )
                municipality_type = infer_municipality_type(municipality_record.name)
                municipality, municipality_created = Municipality.objects.get_or_create(
                    province=province,
                    name=municipality_record.name,
                    defaults={
                        "code": municipality_code,
                        "municipality_type": municipality_type,
                        "population_total": municipality_record.population,
                        "is_active": True,
                    },
                )

                municipality_changed = False
                if municipality.population_total != municipality_record.population:
                    municipality.population_total = municipality_record.population
                    municipality_changed = True
                if municipality.municipality_type != municipality_type:
                    municipality.municipality_type = municipality_type
                    municipality_changed = True
                if not municipality.is_active:
                    municipality.is_active = True
                    municipality_changed = True
                if not municipality.code:
                    municipality.code = municipality_code
                    municipality_changed = True
                if municipality_changed:
                    municipality.save()

                if municipality_created:
                    stats["municipalities_created"] += 1
                elif municipality_changed:
                    stats["municipalities_updated"] += 1

                for barangay_record in municipality_record.barangays:
                    barangay_code = build_code(
                        municipality.code or municipality_code, barangay_record.name
                    )
                    barangay, barangay_created = Barangay.objects.get_or_create(
                        municipality=municipality,
                        name=barangay_record.name,
                        defaults={
                            "code": barangay_code,
                            "population_total": barangay_record.population,
                            "is_active": True,
                        },
                    )

                    barangay_changed = False
                    if barangay.population_total != barangay_record.population:
                        barangay.population_total = barangay_record.population
                        barangay_changed = True
                    if not barangay.is_active:
                        barangay.is_active = True
                        barangay_changed = True
                    if not barangay.code:
                        barangay.code = barangay_code
                        barangay_changed = True
                    if barangay_changed:
                        barangay.save()

                    if barangay_created:
                        stats["barangays_created"] += 1
                    elif barangay_changed:
                        stats["barangays_updated"] += 1
