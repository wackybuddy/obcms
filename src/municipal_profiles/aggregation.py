"""Aggregation schema and helpers for municipal OBC rollups."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, Mapping, MutableMapping, Optional, Tuple


@dataclass(frozen=True)
class MetricRule:
    """Configuration for a metric aggregated from barangay data."""

    source: str
    label: str
    aggregation: str = "sum"
    help_text: str | None = None
    formatter: str = "number"
    weight_source: str | None = None


@dataclass(frozen=True)
class SectionRule:
    """Grouping configuration for related metrics."""

    label: str
    metrics: "OrderedDict[str, MetricRule]"
    description: str | None = None


AGGREGATION_SECTIONS: "OrderedDict[str, SectionRule]" = OrderedDict(
    [
        (
            "demographics",
            SectionRule(
                label="Demographics & Households",
                description="Population and household counts aggregated from barangay submissions.",
                metrics=OrderedDict(
                    [
                        (
                            "estimated_obc_population",
                            MetricRule(
                                source="estimated_obc_population",
                                label="Estimated OBC Population",
                                help_text="Sum of barangay-level estimated OBC population",
                            ),
                        ),
                        (
                            "total_barangay_population",
                            MetricRule(
                                source="total_barangay_population",
                                label="Total Population",
                                help_text="Cumulative barangay population for context",
                            ),
                        ),
                        (
                            "households",
                            MetricRule(
                                source="households",
                                label="Households",
                            ),
                        ),
                        (
                            "families",
                            MetricRule(
                                source="families",
                                label="Families",
                            ),
                        ),
                    ]
                ),
            ),
        ),
        (
            "age_groups",
            SectionRule(
                label="Age Distribution",
                description="Population distribution by age cohorts.",
                metrics=OrderedDict(
                    [
                        (
                            "children_0_9",
                            MetricRule(
                                source="children_0_9",
                                label="Children (0-9)",
                            ),
                        ),
                        (
                            "adolescents_10_14",
                            MetricRule(
                                source="adolescents_10_14",
                                label="Adolescents (10-14)",
                            ),
                        ),
                        (
                            "youth_15_30",
                            MetricRule(
                                source="youth_15_30",
                                label="Youth (15-30)",
                            ),
                        ),
                        (
                            "adults_31_59",
                            MetricRule(
                                source="adults_31_59",
                                label="Adults (31-59)",
                            ),
                        ),
                        (
                            "seniors_60_plus",
                            MetricRule(
                                source="seniors_60_plus",
                                label="Seniors (60+)",
                            ),
                        ),
                    ]
                ),
            ),
        ),
        (
            "vulnerable_groups",
            SectionRule(
                label="Vulnerable Sectors",
                description="Totals for identified vulnerable groups across all barangays.",
                metrics=OrderedDict(
                    [
                        (
                            "women_count",
                            MetricRule(
                                source="women_count",
                                label="Women",
                            ),
                        ),
                        (
                            "solo_parents_count",
                            MetricRule(
                                source="solo_parents_count",
                                label="Solo Parents",
                            ),
                        ),
                        (
                            "pwd_count",
                            MetricRule(
                                source="pwd_count",
                                label="Persons with Disabilities",
                            ),
                        ),
                        (
                            "farmers_count",
                            MetricRule(
                                source="farmers_count",
                                label="Farmers",
                            ),
                        ),
                        (
                            "fisherfolk_count",
                            MetricRule(
                                source="fisherfolk_count",
                                label="Fisherfolk",
                            ),
                        ),
                        (
                            "indigenous_peoples_count",
                            MetricRule(
                                source="indigenous_peoples_count",
                                label="Indigenous Peoples",
                            ),
                        ),
                        (
                            "idps_count",
                            MetricRule(
                                source="idps_count",
                                label="Internally Displaced Persons",
                            ),
                        ),
                        (
                            "migrants_transients_count",
                            MetricRule(
                                source="migrants_transients_count",
                                label="Migrants / Transients",
                            ),
                        ),
                        (
                            "unemployed_count",
                            MetricRule(
                                source="unemployed_count",
                                label="Unemployed",
                            ),
                        ),
                        (
                            "csos_count",
                            MetricRule(
                                source="csos_count",
                                label="CSOs",
                            ),
                        ),
                        (
                            "associations_count",
                            MetricRule(
                                source="associations_count",
                                label="Associations",
                            ),
                        ),
                    ]
                ),
            ),
        ),
        (
            "livelihoods",
            SectionRule(
                label="Livelihood & Enterprises",
                metrics=OrderedDict(
                    [
                        (
                            "number_of_employed_obc",
                            MetricRule(
                                source="number_of_employed_obc",
                                label="Employed OBC",
                            ),
                        ),
                        (
                            "number_of_cooperatives",
                            MetricRule(
                                source="number_of_cooperatives",
                                label="Cooperatives",
                            ),
                        ),
                        (
                            "number_of_social_enterprises",
                            MetricRule(
                                source="number_of_social_enterprises",
                                label="Social Enterprises",
                            ),
                        ),
                        (
                            "number_of_micro_enterprises",
                            MetricRule(
                                source="number_of_micro_enterprises",
                                label="Micro Enterprises",
                            ),
                        ),
                        (
                            "number_of_unbanked_obc",
                            MetricRule(
                                source="number_of_unbanked_obc",
                                label="Unbanked OBC",
                            ),
                        ),
                    ]
                ),
            ),
        ),
        (
            "religion_education",
            SectionRule(
                label="Religious & Education Access",
                metrics=OrderedDict(
                    [
                        (
                            "mosques_count",
                            MetricRule(
                                source="mosques_count",
                                label="Mosques",
                            ),
                        ),
                        (
                            "madrasah_count",
                            MetricRule(
                                source="madrasah_count",
                                label="Madrasah",
                            ),
                        ),
                        (
                            "asatidz_count",
                            MetricRule(
                                source="asatidz_count",
                                label="Asatidz / Teachers",
                            ),
                        ),
                        (
                            "religious_leaders_count",
                            MetricRule(
                                source="religious_leaders_count",
                                label="Religious Leaders",
                            ),
                        ),
                    ]
                ),
            ),
        ),
    ]
)


def iter_metric_rules() -> Iterator[Tuple[str, str, MetricRule]]:
    """Yield (section, metric, rule) tuples in configured order."""

    for section_key, section in AGGREGATION_SECTIONS.items():
        for metric_key, rule in section.metrics.items():
            yield section_key, metric_key, rule


def initialise_section_payload() -> Dict[str, Dict[str, int]]:
    """Return a zeroed-out structure matching the schema."""

    payload: Dict[str, Dict[str, int]] = {}
    for section_key, section in AGGREGATION_SECTIONS.items():
        payload[section_key] = {
            metric_key: 0 for metric_key in section.metrics.keys()
        }
    return payload


def normalise_reported_metrics(
    metrics: Optional[Mapping[str, Mapping[str, int]]]
) -> Dict[str, Dict[str, int]]:
    """Ensure reported metrics follow the schema with default values."""

    base = initialise_section_payload()
    if not metrics:
        return base

    if isinstance(metrics, Mapping):
        section_keys = set(AGGREGATION_SECTIONS.keys())
        provided_section_keys = {
            key for key in metrics.keys() if key in section_keys
        }

        if provided_section_keys:
            for section_key in provided_section_keys:
                section_payload = metrics.get(section_key)
                if not isinstance(section_payload, Mapping):
                    continue
                for metric_key, value in section_payload.items():
                    if metric_key in base[section_key] and isinstance(value, (int, float)):
                        numeric_value = float(value)
                        if numeric_value.is_integer():
                            base[section_key][metric_key] = int(numeric_value)
                        else:
                            base[section_key][metric_key] = round(numeric_value, 2)
        else:
            # Handle flattened payloads where metrics are top-level keys.
            for metric_key, value in metrics.items():
                if not isinstance(value, (int, float)):
                    continue
                for section_key, section in AGGREGATION_SECTIONS.items():
                    if metric_key in section.metrics:
                        numeric_value = float(value)
                        if numeric_value.is_integer():
                            base[section_key][metric_key] = int(numeric_value)
                        else:
                            base[section_key][metric_key] = round(numeric_value, 2)
                        break
    return base


def flatten_metrics(metrics: Mapping[str, Mapping[str, int]]) -> Dict[str, int]:
    """Collapse sectioned metrics into a flat mapping."""

    flattened: Dict[str, int] = {}
    for _, section_payload in metrics.items():
        if not isinstance(section_payload, Mapping):
            continue
        for metric_key, value in section_payload.items():
            if isinstance(value, (int, float)):
                numeric_value = float(value)
                if numeric_value.is_integer():
                    flattened[metric_key] = int(numeric_value)
                else:
                    flattened[metric_key] = round(numeric_value, 2)
    return flattened


def build_empty_report() -> Dict[str, Dict[str, int]]:
    """Convenience wrapper for views/forms requiring an empty dataset."""

    return initialise_section_payload()
