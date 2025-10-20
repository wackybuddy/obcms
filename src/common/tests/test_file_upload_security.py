"""
Security tests for file upload validation.

Tests comprehensive file upload security to prevent:
- Malicious executable uploads
- Web shell attacks
- Oversized file attacks
- Content-type spoofing
- Path traversal attacks
"""

import io
from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from common.validators import (
    sanitize_filename,
    validate_document_file,
    validate_file_content_type,
    validate_file_extension,
    validate_file_size,
    validate_image_file,
)


class FileUploadSecurityTest(TestCase):
    """Test file upload validators prevent malicious uploads."""

    def test_malicious_executable_rejected(self):
        """Test .exe files are rejected by extension validator."""
        malicious_file = SimpleUploadedFile(
            "malware.exe",
            b"MZ\x90\x00",  # PE executable header
            content_type="application/x-msdownload",
        )

        with self.assertRaises(ValidationError) as context:
            validate_file_extension(malicious_file)

        self.assertIn(".exe", str(context.exception))
        self.assertIn("not allowed", str(context.exception))

    def test_php_web_shell_rejected(self):
        """Test PHP web shells are rejected by extension validator."""
        php_shell = SimpleUploadedFile(
            "shell.php",
            b"<?php system($_GET['cmd']); ?>",
            content_type="application/x-php",
        )

        with self.assertRaises(ValidationError) as context:
            validate_file_extension(php_shell)

        self.assertIn(".php", str(context.exception))

    def test_oversized_document_rejected(self):
        """Test files over 10MB are rejected by document validator."""
        # Create 11MB file
        large_file = SimpleUploadedFile(
            "large.pdf", b"0" * (11 * 1024 * 1024), content_type="application/pdf"  # 11MB
        )

        with self.assertRaises(ValidationError) as context:
            validate_document_file(large_file)

        self.assertIn("exceeds maximum allowed size", str(context.exception))

    def test_oversized_image_rejected(self):
        """Test images over 5MB are rejected by image validator."""
        # Create 6MB file
        large_image = SimpleUploadedFile(
            "large.jpg", b"0" * (6 * 1024 * 1024), content_type="image/jpeg"  # 6MB
        )

        with self.assertRaises(ValidationError) as context:
            validate_image_file(large_image)

        self.assertIn("exceeds maximum allowed size", str(context.exception))

    def test_valid_pdf_size_accepted(self):
        """Test valid-sized PDF files pass size validation."""
        valid_pdf = SimpleUploadedFile(
            "document.pdf",
            b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n" * 100,  # Small PDF
            content_type="application/pdf",
        )

        # Should not raise ValidationError
        try:
            validate_file_size(valid_pdf, max_size_mb=10)
        except ValidationError:
            self.fail("Valid PDF size was rejected")

    @patch("common.validators.MAGIC_AVAILABLE", True)
    @patch("common.validators.magic")
    def test_content_type_mismatch_rejected(self, mock_magic):
        """Test files with mismatched content-type are rejected."""
        # Mock magic to return PHP content type
        mock_magic.from_buffer.return_value = "text/x-php"

        fake_pdf = SimpleUploadedFile(
            "fake.pdf",
            b"<?php system($_GET['cmd']); ?>",  # PHP content
            content_type="application/pdf",  # Claims to be PDF
        )

        # Content-type validation should catch this
        with self.assertRaises(ValidationError) as context:
            validate_file_content_type(fake_pdf)

        self.assertIn("text/x-php", str(context.exception))
        self.assertIn("not allowed", str(context.exception))

    @patch("common.validators.MAGIC_AVAILABLE", True)
    @patch("common.validators.magic")
    def test_extension_content_type_mismatch_rejected(self, mock_magic):
        """Test files where extension doesn't match actual content."""
        # Mock magic to return JPEG content type for .pdf file
        mock_magic.from_buffer.return_value = "image/jpeg"

        fake_pdf = SimpleUploadedFile(
            "fake.pdf",
            b"\xff\xd8\xff\xe0\x00\x10JFIF",  # JPEG header
            content_type="application/pdf",
        )

        with self.assertRaises(ValidationError) as context:
            validate_file_content_type(fake_pdf)

        self.assertIn("does not match actual content type", str(context.exception))

    def test_path_traversal_filename_sanitized(self):
        """Test path traversal attempts in filename are sanitized."""
        dangerous_filename = "../../../etc/passwd"
        sanitized = sanitize_filename(dangerous_filename)

        # Should not contain path traversal sequences
        self.assertNotIn("..", sanitized)
        self.assertNotIn("/", sanitized)
        self.assertNotIn("\\", sanitized)

    def test_dangerous_characters_removed_from_filename(self):
        """Test dangerous characters are removed from filenames."""
        dangerous_filename = "file<script>alert('xss')</script>.pdf"
        sanitized = sanitize_filename(dangerous_filename)

        # Should not contain dangerous characters
        self.assertNotIn("<", sanitized)
        self.assertNotIn(">", sanitized)
        self.assertNotIn("script", sanitized)

    def test_null_byte_removed_from_filename(self):
        """Test null bytes are removed from filenames."""
        dangerous_filename = "file.pdf\x00.php"
        sanitized = sanitize_filename(dangerous_filename)

        # Should not contain null bytes
        self.assertNotIn("\x00", sanitized)

    def test_long_filename_truncated(self):
        """Test excessively long filenames are truncated."""
        long_filename = "a" * 200 + ".pdf"
        sanitized = sanitize_filename(long_filename)

        # Should be truncated to reasonable length
        self.assertLessEqual(len(sanitized), 105)  # 100 chars + ".pdf"
        self.assertTrue(sanitized.endswith(".pdf"))

    def test_valid_pdf_extension_accepted(self):
        """Test valid PDF extension is accepted."""
        valid_file = SimpleUploadedFile(
            "document.pdf", b"%PDF-1.4", content_type="application/pdf"
        )

        try:
            validate_file_extension(
                valid_file, allowed_extensions=[".pdf", ".doc", ".docx"]
            )
        except ValidationError:
            self.fail("Valid PDF extension was rejected")

    def test_valid_image_extension_accepted(self):
        """Test valid image extensions are accepted."""
        extensions_to_test = [
            (".jpg", b"\xff\xd8\xff\xe0"),
            (".jpeg", b"\xff\xd8\xff\xe0"),
            (".png", b"\x89PNG"),
            (".gif", b"GIF89a"),
        ]

        for ext, header in extensions_to_test:
            with self.subTest(extension=ext):
                valid_file = SimpleUploadedFile(
                    f"image{ext}", header, content_type=f"image/{ext[1:]}"
                )

                try:
                    validate_file_extension(
                        valid_file, allowed_extensions=[".jpg", ".jpeg", ".png", ".gif"]
                    )
                except ValidationError:
                    self.fail(f"Valid {ext} extension was rejected")

    @patch("common.validators.MAGIC_AVAILABLE", True)
    @patch("common.validators.magic")
    def test_valid_pdf_content_type_accepted(self, mock_magic):
        """Test valid PDF content type is accepted."""
        mock_magic.from_buffer.return_value = "application/pdf"

        valid_pdf = SimpleUploadedFile(
            "document.pdf", b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n", content_type="application/pdf"
        )

        try:
            validate_file_content_type(valid_pdf)
        except ValidationError:
            self.fail("Valid PDF content type was rejected")

    @patch("common.validators.MAGIC_AVAILABLE", True)
    @patch("common.validators.magic")
    def test_valid_image_content_type_accepted(self, mock_magic):
        """Test valid image content types are accepted."""
        mock_magic.from_buffer.return_value = "image/jpeg"

        valid_jpg = SimpleUploadedFile(
            "photo.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF", content_type="image/jpeg"
        )

        try:
            validate_file_content_type(valid_jpg)
        except ValidationError:
            self.fail("Valid JPEG content type was rejected")

    def test_document_validator_comprehensive(self):
        """Test document validator performs all checks."""
        # Test with file that would pass size but fail extension
        invalid_file = SimpleUploadedFile(
            "malware.exe", b"MZ\x90\x00", content_type="application/x-msdownload"
        )

        with self.assertRaises(ValidationError):
            validate_document_file(invalid_file)

    def test_image_validator_comprehensive(self):
        """Test image validator performs all checks."""
        # Test with file that would pass size but fail extension
        invalid_file = SimpleUploadedFile(
            "shell.php", b"<?php system($_GET['cmd']); ?>", content_type="application/x-php"
        )

        with self.assertRaises(ValidationError):
            validate_image_file(invalid_file)

    @patch("common.validators.MAGIC_AVAILABLE", True)
    @patch("common.validators.magic")
    def test_svg_with_javascript_rejected(self, mock_magic):
        """Test SVG files are rejected (XSS risk)."""
        # SVG not in allowed extensions
        mock_magic.from_buffer.return_value = "image/svg+xml"

        svg_xss = SimpleUploadedFile(
            "xss.svg",
            b'<svg><script>alert("XSS")</script></svg>',
            content_type="image/svg+xml",
        )

        with self.assertRaises(ValidationError):
            validate_image_file(svg_xss)

    def test_case_insensitive_extension_validation(self):
        """Test extension validation is case-insensitive."""
        file_upper = SimpleUploadedFile(
            "document.PDF", b"%PDF-1.4", content_type="application/pdf"
        )

        file_mixed = SimpleUploadedFile(
            "document.PdF", b"%PDF-1.4", content_type="application/pdf"
        )

        # Both should pass validation (extensions normalized to lowercase)
        try:
            validate_file_extension(file_upper, allowed_extensions=[".pdf"])
            validate_file_extension(file_mixed, allowed_extensions=[".pdf"])
        except ValidationError:
            self.fail("Case-insensitive extension validation failed")

    def test_empty_filename_handled(self):
        """Test empty filenames are handled gracefully."""
        file_no_name = SimpleUploadedFile("", b"content", content_type="text/plain")

        # Should not crash
        sanitized = sanitize_filename(file_no_name.name)
        self.assertEqual(sanitized, "")

    def test_filename_with_multiple_extensions(self):
        """Test filename with multiple extensions (e.g., .tar.gz)."""
        file_multi_ext = SimpleUploadedFile(
            "archive.tar.gz", b"content", content_type="application/gzip"
        )

        # Extension validator should check the last extension
        with self.assertRaises(ValidationError):
            validate_file_extension(file_multi_ext, allowed_extensions=[".pdf", ".doc"])

    def test_unicode_filename_sanitization(self):
        """Test Unicode characters in filenames are handled."""
        unicode_filename = "文档.pdf"
        sanitized = sanitize_filename(unicode_filename)

        # Should preserve Unicode but ensure filesystem safety
        self.assertIsInstance(sanitized, str)
        self.assertTrue(sanitized.endswith(".pdf"))


class FileValidatorIntegrationTest(TestCase):
    """Integration tests for file validators in model contexts."""

    def test_coordination_partnership_document_validation(self):
        """Test file validation for Partnership model documents."""
        from coordination.models import PartnershipDocument

        # This tests that the validator is properly configured on the model
        # We can't fully test without creating model instances, but we verify the validator exists
        file_field = PartnershipDocument._meta.get_field("file")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)

    def test_monitoring_request_document_validation(self):
        """Test file validation for monitoring request documents."""
        from monitoring.models import RequestSupportingDocument

        file_field = RequestSupportingDocument._meta.get_field("file")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)

    def test_monitoring_workflow_document_validation(self):
        """Test file validation for monitoring workflow documents."""
        from monitoring.models import WorkflowDocument

        file_field = WorkflowDocument._meta.get_field("file")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)

    def test_policy_evidence_document_validation(self):
        """Test file validation for policy evidence documents."""
        from recommendations.policy_tracking.models import PolicyEvidence

        file_field = PolicyEvidence._meta.get_field("document")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)

    def test_policy_tracking_document_validation(self):
        """Test file validation for policy tracking documents."""
        from recommendations.policy_tracking.models import PolicyDocument

        file_field = PolicyDocument._meta.get_field("file")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)

    def test_data_import_file_validation(self):
        """Test file validation for data import files."""
        from data_imports.models import DataImport

        file_field = DataImport._meta.get_field("file")
        self.assertTrue(len(file_field.validators) > 0)
        # Should have both FileExtensionValidator and validate_document_file
        self.assertIn(validate_document_file, file_field.validators)

    def test_import_template_file_validation(self):
        """Test file validation for import template files."""
        from data_imports.models import ImportTemplate

        file_field = ImportTemplate._meta.get_field("template_file")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)

    def test_ai_assistant_pdf_validation(self):
        """Test file validation for AI-generated PDF documents."""
        from ai_assistant.models import AIDocument

        file_field = AIDocument._meta.get_field("pdf_file")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)

    def test_ai_assistant_word_validation(self):
        """Test file validation for AI-generated Word documents."""
        from ai_assistant.models import AIDocument

        file_field = AIDocument._meta.get_field("word_file")
        self.assertTrue(len(file_field.validators) > 0)
        self.assertIn(validate_document_file, file_field.validators)


class FileValidatorEdgeCasesTest(TestCase):
    """Test edge cases and corner scenarios for file validation."""

    def test_zero_byte_file(self):
        """Test handling of zero-byte files."""
        empty_file = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")

        # Zero-byte files should pass size validation
        try:
            validate_file_size(empty_file, max_size_mb=10)
        except ValidationError:
            self.fail("Zero-byte file was rejected")

    def test_file_with_no_extension(self):
        """Test handling of files with no extension."""
        no_ext_file = SimpleUploadedFile("README", b"content", content_type="text/plain")

        with self.assertRaises(ValidationError):
            validate_file_extension(no_ext_file, allowed_extensions=[".pdf", ".doc"])

    def test_file_with_only_extension(self):
        """Test handling of files with only extension (e.g., '.pdf')."""
        only_ext_file = SimpleUploadedFile(".pdf", b"content", content_type="application/pdf")

        # Should still validate extension correctly
        try:
            validate_file_extension(only_ext_file, allowed_extensions=[".pdf"])
        except ValidationError:
            self.fail("File with only extension was rejected")

    def test_file_size_exactly_at_limit(self):
        """Test files exactly at the size limit."""
        # Create file exactly 10MB
        exact_size_file = SimpleUploadedFile(
            "exact.pdf", b"0" * (10 * 1024 * 1024), content_type="application/pdf"  # Exactly 10MB
        )

        # Should pass validation (at limit, not over)
        try:
            validate_file_size(exact_size_file, max_size_mb=10)
        except ValidationError:
            self.fail("File exactly at size limit was rejected")

    def test_file_size_one_byte_over_limit(self):
        """Test files one byte over the size limit."""
        # Create file 1 byte over 10MB
        over_limit_file = SimpleUploadedFile(
            "over.pdf",
            b"0" * (10 * 1024 * 1024 + 1),  # 10MB + 1 byte
            content_type="application/pdf",
        )

        with self.assertRaises(ValidationError):
            validate_file_size(over_limit_file, max_size_mb=10)
