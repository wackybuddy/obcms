"""
Utility functions for data import and migration operations.
"""

import csv
import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from django.core.exceptions import ValidationError
from django.db import models


class DataValidator:
    """
    Data validation utility for import operations.
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return True  # Allow empty emails
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return True  # Allow empty phone numbers
        # Remove common separators
        cleaned = re.sub(r"[-()\s]", "", phone)
        # Check if remaining characters are digits and plus
        return bool(re.match(r"^\+?[0-9]{7,15}$", cleaned))

    @staticmethod
    def validate_year(year: Any) -> bool:
        """Validate year value."""
        if not year:
            return True
        try:
            year_int = int(year)
            return 1800 <= year_int <= 2030
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_choice_field(value: str, choices: List[Tuple[str, str]]) -> bool:
        """Validate that value is in choices."""
        if not value:
            return True
        valid_choices = [choice[0] for choice in choices]
        return value in valid_choices

    @staticmethod
    def clean_numeric_value(value: Any) -> Optional[int]:
        """Clean and convert numeric value."""
        if not value or str(value).strip() == "":
            return None
        try:
            # Remove commas and convert to int
            cleaned = str(value).replace(",", "").strip()
            return int(float(cleaned))  # Convert via float to handle decimals
        except (ValueError, TypeError):
            return None

    @staticmethod
    def clean_decimal_value(
        value: Any, max_digits: int = 10, decimal_places: int = 2
    ) -> Optional[Decimal]:
        """Clean and convert decimal value."""
        if not value or str(value).strip() == "":
            return None
        try:
            cleaned = str(value).replace(",", "").strip()
            decimal_value = Decimal(cleaned)
            # Check precision
            sign, digits, exponent = decimal_value.as_tuple()
            if len(digits) > max_digits or abs(exponent) > decimal_places:
                return None
            return decimal_value
        except (ValueError, TypeError, InvalidOperation):
            return None


class DataCleaner:
    """
    Data cleaning utility for import operations.
    """

    @staticmethod
    def clean_text(text: str, max_length: Optional[int] = None) -> str:
        """Clean text data."""
        if not text:
            return ""

        # Strip whitespace and normalize
        cleaned = str(text).strip()

        # Replace multiple whitespaces with single space
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Truncate if needed
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length].strip()

        return cleaned

    @staticmethod
    def clean_name(name: str) -> str:
        """Clean name fields."""
        if not name:
            return ""

        # Basic cleaning
        cleaned = DataCleaner.clean_text(name)

        # Title case for names
        cleaned = cleaned.title()

        return cleaned

    @staticmethod
    def standardize_location_name(name: str) -> str:
        """Standardize location names."""
        if not name:
            return ""

        cleaned = DataCleaner.clean_text(name)

        # Common standardizations
        replacements = {
            "brgy.": "Barangay",
            "bgy.": "Barangay",
            "bgry.": "Barangay",
            "city of": "City of",
            "municipality of": "Municipality of",
        }

        for old, new in replacements.items():
            cleaned = re.sub(
                rf"\b{re.escape(old)}\b", new, cleaned, flags=re.IGNORECASE
            )

        return cleaned.title()


class FileProcessor:
    """
    File processing utility for different file formats.
    """

    @staticmethod
    def read_csv_file(file_path: str, encoding: str = "utf-8") -> List[Dict[str, Any]]:
        """Read CSV file and return list of dictionaries."""
        try:
            with open(file_path, "r", encoding=encoding) as file:
                reader = csv.DictReader(file)
                return list(reader)
        except UnicodeDecodeError:
            # Try different encodings
            encodings = ["utf-8-sig", "latin1", "cp1252"]
            for enc in encodings:
                try:
                    with open(file_path, "r", encoding=enc) as file:
                        reader = csv.DictReader(file)
                        return list(reader)
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not decode file with any common encoding")

    @staticmethod
    def read_excel_file(
        file_path: str, sheet_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Read Excel file and return list of dictionaries."""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # Replace NaN with None
            df = df.where(pd.notnull(df), None)
            return df.to_dict("records")
        except Exception as e:
            raise ValueError(f"Could not read Excel file: {str(e)}")

    @staticmethod
    def detect_file_encoding(file_path: str) -> str:
        """Detect file encoding."""
        import chardet

        try:
            with open(file_path, "rb") as file:
                raw_data = file.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result["encoding"] or "utf-8"
        except Exception:
            return "utf-8"

    @staticmethod
    def get_file_headers(file_path: str) -> List[str]:
        """Get headers from CSV or Excel file."""
        file_extension = file_path.lower().split(".")[-1]

        if file_extension == "csv":
            with open(
                file_path, "r", encoding=FileProcessor.detect_file_encoding(file_path)
            ) as file:
                reader = csv.reader(file)
                return next(reader, [])
        elif file_extension in ["xlsx", "xls"]:
            df = pd.read_excel(file_path, nrows=0)
            return df.columns.tolist()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")


class MappingEngine:
    """
    Field mapping engine for data transformation.
    """

    def __init__(self, mapping: Dict[str, str]):
        """
        Initialize with field mapping.
        mapping: dict mapping source field names to target field names
        """
        self.mapping = mapping

    def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single record using the mapping."""
        transformed = {}

        for target_field, source_field in self.mapping.items():
            if source_field in record:
                transformed[target_field] = record[source_field]

        return transformed

    def transform_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform multiple records."""
        return [self.transform_record(record) for record in records]

    @staticmethod
    def suggest_mapping(
        source_fields: List[str], target_fields: List[str]
    ) -> Dict[str, str]:
        """Suggest field mapping based on field names."""
        mapping = {}

        # Create normalized versions for comparison
        def normalize_field(field: str) -> str:
            return re.sub(r"[^a-zA-Z0-9]", "", field.lower())

        normalized_target = {normalize_field(field): field for field in target_fields}

        for source_field in source_fields:
            normalized_source = normalize_field(source_field)

            # Exact match
            if normalized_source in normalized_target:
                mapping[normalized_target[normalized_source]] = source_field
                continue

            # Partial matches
            for norm_target, target_field in normalized_target.items():
                if (
                    normalized_source in norm_target
                    or norm_target in normalized_source
                    or abs(len(normalized_source) - len(norm_target)) <= 2
                ):

                    # Simple similarity check
                    common_chars = set(normalized_source) & set(norm_target)
                    if len(common_chars) >= min(
                        3, min(len(normalized_source), len(norm_target))
                    ):
                        mapping[target_field] = source_field
                        break

        return mapping


class ImportProcessor:
    """
    Main processor for handling import operations.
    """

    def __init__(self, import_session, model_class):
        self.import_session = import_session
        self.model_class = model_class
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.errors = []
        self.warnings = []

    def validate_record(
        self, record: Dict[str, Any], row_number: int
    ) -> Tuple[bool, List[str]]:
        """Validate a single record."""
        errors = []

        # Get model fields
        model_fields = {field.name: field for field in self.model_class._meta.fields}

        for field_name, value in record.items():
            if field_name not in model_fields:
                continue

            field = model_fields[field_name]

            # Check required fields
            if not field.blank and not field.null and not value:
                errors.append(f"Required field '{field_name}' is empty")

            # Type-specific validation
            if isinstance(field, models.EmailField):
                if value and not self.validator.validate_email(value):
                    errors.append(
                        f"Invalid email format in field '{field_name}': {value}"
                    )

            elif isinstance(field, models.CharField):
                if value and len(str(value)) > field.max_length:
                    errors.append(
                        f"Value too long for field '{field_name}' (max {field.max_length}): {value}"
                    )

            elif isinstance(field, models.IntegerField):
                if value and self.validator.clean_numeric_value(value) is None:
                    errors.append(
                        f"Invalid integer value for field '{field_name}': {value}"
                    )

        return len(errors) == 0, errors

    def clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single record."""
        cleaned = {}
        model_fields = {field.name: field for field in self.model_class._meta.fields}

        for field_name, value in record.items():
            if field_name not in model_fields:
                continue

            field = model_fields[field_name]

            if isinstance(field, models.CharField):
                cleaned[field_name] = self.cleaner.clean_text(value, field.max_length)
            elif isinstance(field, models.TextField):
                cleaned[field_name] = self.cleaner.clean_text(value)
            elif isinstance(field, models.IntegerField):
                cleaned[field_name] = self.validator.clean_numeric_value(value)
            elif isinstance(field, models.DecimalField):
                cleaned[field_name] = self.validator.clean_decimal_value(
                    value, field.max_digits, field.decimal_places
                )
            else:
                cleaned[field_name] = value

        return cleaned
