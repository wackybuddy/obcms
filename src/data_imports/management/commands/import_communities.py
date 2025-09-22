import csv
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity
from data_imports.models import DataImport, ImportLog


class Command(BaseCommand):
    help = "Import OBC communities from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--import-session", type=str, help="Import session ID for tracking"
        )
        parser.add_argument(
            "--mapping", type=str, help="JSON string with field mapping"
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Dry run without saving data"
        )
        parser.add_argument(
            "--update-existing", action="store_true", help="Update existing communities"
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        import_session_id = options.get("import_session")
        mapping_str = options.get("mapping")
        dry_run = options["dry_run"]
        update_existing = options["update_existing"]

        # Get or create import session
        import_session = None
        if import_session_id:
            try:
                import_session = DataImport.objects.get(id=import_session_id)
                if not dry_run:
                    import_session.status = "processing"
                    import_session.started_at = timezone.now()
                    import_session.save()
            except DataImport.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Import session {import_session_id} not found")
                )
                return

        # Parse field mapping
        field_mapping = {}
        if mapping_str:
            try:
                field_mapping = json.loads(mapping_str)
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR("Invalid JSON mapping"))
                return

        # Default field mapping
        default_mapping = {
            "name": "community_name",
            "region": "region_name",
            "province": "province_name",
            "municipality": "municipality_name",
            "barangay": "barangay_name",
            "population": "population",
            "households": "households",
            "cultural_background": "cultural_background",
            "primary_language": "primary_language",
            "established_year": "established_year",
            "settlement_type": "settlement_type",
            "development_status": "development_status",
        }

        # Merge with provided mapping
        field_mapping = {**default_mapping, **field_mapping}

        def log_message(level, message, row_number=None, record_data=None):
            if import_session:
                ImportLog.objects.create(
                    import_session=import_session,
                    level=level,
                    message=message,
                    row_number=row_number,
                    record_data=record_data or {},
                )
            self.stdout.write(self.style.SUCCESS(f"{level.upper()}: {message}"))

        try:
            with open(csv_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                total_rows = 0
                imported = 0
                updated = 0
                errors = 0
                skipped = 0

                # Count total rows
                if import_session:
                    temp_reader = csv.DictReader(open(csv_file, "r", encoding="utf-8"))
                    total_count = sum(1 for _ in temp_reader)
                    import_session.records_total = total_count
                    import_session.save()

                for row_number, row in enumerate(
                    reader, start=2
                ):  # Start at 2 to account for header
                    total_rows += 1

                    try:
                        # Extract fields using mapping
                        community_name = row.get(
                            field_mapping.get("name", ""), ""
                        ).strip()
                        region_name = row.get(
                            field_mapping.get("region", ""), ""
                        ).strip()
                        province_name = row.get(
                            field_mapping.get("province", ""), ""
                        ).strip()
                        municipality_name = row.get(
                            field_mapping.get("municipality", ""), ""
                        ).strip()
                        barangay_name = row.get(
                            field_mapping.get("barangay", ""), ""
                        ).strip()

                        if not all(
                            [
                                community_name,
                                region_name,
                                province_name,
                                municipality_name,
                                barangay_name,
                            ]
                        ):
                            log_message(
                                "warning",
                                f"Missing required fields in row {row_number}",
                                row_number,
                                row,
                            )
                            skipped += 1
                            continue

                        if not dry_run:
                            with transaction.atomic():
                                # Get or create region
                                region, _ = Region.objects.get_or_create(
                                    name=region_name,
                                    defaults={
                                        "code": region_name[:10],
                                        "description": f"Auto-imported region: {region_name}",
                                    },
                                )

                                # Get or create province
                                province, _ = Province.objects.get_or_create(
                                    name=province_name,
                                    region=region,
                                    defaults={"code": province_name[:10]},
                                )

                                # Get or create municipality
                                municipality, _ = Municipality.objects.get_or_create(
                                    name=municipality_name,
                                    province=province,
                                    defaults={"code": municipality_name[:10]},
                                )

                                # Get or create barangay
                                barangay, _ = Barangay.objects.get_or_create(
                                    name=barangay_name,
                                    municipality=municipality,
                                    defaults={"code": barangay_name[:10]},
                                )

                                # Prepare community data
                                community_data = {
                                    "population": self._safe_int(
                                        row.get(field_mapping.get("population", ""), "")
                                    ),
                                    "households": self._safe_int(
                                        row.get(field_mapping.get("households", ""), "")
                                    ),
                                    "cultural_background": row.get(
                                        field_mapping.get("cultural_background", ""), ""
                                    ),
                                    "primary_language": row.get(
                                        field_mapping.get("primary_language", ""), ""
                                    ),
                                    "established_year": self._safe_int(
                                        row.get(
                                            field_mapping.get("established_year", ""),
                                            "",
                                        )
                                    ),
                                    "settlement_type": row.get(
                                        field_mapping.get("settlement_type", ""),
                                        "village",
                                    ),
                                    "development_status": row.get(
                                        field_mapping.get("development_status", ""),
                                        "developing",
                                    ),
                                }

                                # Remove None values
                                community_data = {
                                    k: v
                                    for k, v in community_data.items()
                                    if v is not None
                                }

                                # Create or update community
                                community, created = OBCCommunity.objects.get_or_create(
                                    name=community_name,
                                    barangay=barangay,
                                    defaults=community_data,
                                )

                                if created:
                                    log_message(
                                        "info",
                                        f"Created community: {community.name}",
                                        row_number,
                                    )
                                    imported += 1
                                elif update_existing:
                                    for key, value in community_data.items():
                                        setattr(community, key, value)
                                    community.save()
                                    log_message(
                                        "info",
                                        f"Updated community: {community.name}",
                                        row_number,
                                    )
                                    updated += 1
                                else:
                                    log_message(
                                        "warning",
                                        f"Community already exists: {community.name}",
                                        row_number,
                                    )
                                    skipped += 1
                        else:
                            # Dry run - just validate
                            log_message(
                                "info",
                                f"Would import community: {community_name}",
                                row_number,
                            )
                            imported += 1

                        # Update progress
                        if import_session:
                            import_session.records_processed = total_rows
                            import_session.records_imported = imported
                            import_session.records_updated = updated
                            import_session.records_skipped = skipped
                            import_session.records_failed = errors
                            import_session.save()

                    except Exception as e:
                        log_message(
                            "error",
                            f"Error importing row {row_number}: {str(e)}",
                            row_number,
                            row,
                        )
                        errors += 1
                        if import_session:
                            import_session.records_failed = errors
                            import_session.save()

                # Final status update
                if import_session and not dry_run:
                    import_session.status = "completed" if errors == 0 else "partial"
                    import_session.completed_at = timezone.now()
                    import_session.records_processed = total_rows
                    import_session.records_imported = imported
                    import_session.records_updated = updated
                    import_session.records_skipped = skipped
                    import_session.records_failed = errors
                    import_session.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Import completed. Total: {total_rows}, Imported: {imported}, "
                        f"Updated: {updated}, Skipped: {skipped}, Errors: {errors}"
                    )
                )

        except FileNotFoundError:
            error_msg = f"CSV file not found: {csv_file}"
            if import_session:
                import_session.status = "failed"
                import_session.error_log = error_msg
                import_session.save()
            raise CommandError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if import_session:
                import_session.status = "failed"
                import_session.error_log = error_msg
                import_session.save()
            raise CommandError(error_msg)

    def _safe_int(self, value):
        """Safely convert string to integer."""
        if not value or not str(value).strip():
            return None
        try:
            return int(str(value).strip().replace(",", ""))
        except (ValueError, TypeError):
            return None
