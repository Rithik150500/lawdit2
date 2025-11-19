"""
Tests for PDF processor
"""

import base64
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image

from lawdit.indexer.pdf_processor import PDFProcessor


class TestPDFProcessorInitialization:
    """Tests for PDFProcessor initialization."""

    def test_init_default_dpi(self):
        """Test initialization with default DPI."""
        processor = PDFProcessor()
        assert processor.dpi == 200

    def test_init_custom_dpi(self):
        """Test initialization with custom DPI."""
        processor = PDFProcessor(dpi=300)
        assert processor.dpi == 300

    def test_init_low_dpi(self):
        """Test initialization with low DPI."""
        processor = PDFProcessor(dpi=72)
        assert processor.dpi == 72

    def test_init_high_dpi(self):
        """Test initialization with high DPI."""
        processor = PDFProcessor(dpi=600)
        assert processor.dpi == 600


class TestPDFProcessorExtractPagesAsImages:
    """Tests for extract_pages_as_images method."""

    @patch("lawdit.indexer.pdf_processor.pdf2image.convert_from_path")
    def test_extract_pages_single_page(self, mock_convert):
        """Test extracting a single page from PDF."""
        # Create a mock PIL image
        mock_image = Mock(spec=Image.Image)
        mock_convert.return_value = [mock_image]

        processor = PDFProcessor(dpi=200)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            output_dir = os.path.join(tmpdir, "output")

            # Create a dummy PDF file
            Path(pdf_path).touch()

            image_paths = processor.extract_pages_as_images(pdf_path, output_dir)

            # Verify convert_from_path was called correctly
            mock_convert.assert_called_once_with(pdf_path, dpi=200, fmt="png")

            # Verify image was saved
            mock_image.save.assert_called_once()

            # Verify correct number of images and path format
            assert len(image_paths) == 1
            assert "page_0001.png" in image_paths[0]
            assert output_dir in image_paths[0]

    @patch("lawdit.indexer.pdf_processor.pdf2image.convert_from_path")
    def test_extract_pages_multiple_pages(self, mock_convert):
        """Test extracting multiple pages from PDF."""
        # Create mock PIL images for 3 pages
        mock_images = [Mock(spec=Image.Image) for _ in range(3)]
        mock_convert.return_value = mock_images

        processor = PDFProcessor(dpi=150)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            output_dir = os.path.join(tmpdir, "output")

            Path(pdf_path).touch()

            image_paths = processor.extract_pages_as_images(pdf_path, output_dir)

            # Verify convert_from_path was called with correct DPI
            mock_convert.assert_called_once_with(pdf_path, dpi=150, fmt="png")

            # Verify all images were saved
            for mock_image in mock_images:
                mock_image.save.assert_called_once()

            # Verify correct number of images and proper numbering
            assert len(image_paths) == 3
            assert "page_0001.png" in image_paths[0]
            assert "page_0002.png" in image_paths[1]
            assert "page_0003.png" in image_paths[2]

    @patch("lawdit.indexer.pdf_processor.pdf2image.convert_from_path")
    def test_extract_pages_creates_output_directory(self, mock_convert):
        """Test that extract_pages_as_images creates output directory if it doesn't exist."""
        mock_image = Mock(spec=Image.Image)
        mock_convert.return_value = [mock_image]

        processor = PDFProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            output_dir = os.path.join(tmpdir, "nested", "output", "dir")

            Path(pdf_path).touch()

            # Verify directory doesn't exist
            assert not os.path.exists(output_dir)

            image_paths = processor.extract_pages_as_images(pdf_path, output_dir)

            # Verify directory was created
            assert os.path.exists(output_dir)
            assert os.path.isdir(output_dir)

    @patch("lawdit.indexer.pdf_processor.pdf2image.convert_from_path")
    def test_extract_pages_error_handling(self, mock_convert):
        """Test error handling when PDF conversion fails."""
        mock_convert.side_effect = Exception("PDF conversion failed")

        processor = PDFProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            output_dir = os.path.join(tmpdir, "output")

            Path(pdf_path).touch()

            image_paths = processor.extract_pages_as_images(pdf_path, output_dir)

            # Should return empty list on error
            assert image_paths == []

    @patch("lawdit.indexer.pdf_processor.pdf2image.convert_from_path")
    def test_extract_pages_with_high_dpi(self, mock_convert):
        """Test extracting pages with high DPI setting."""
        mock_image = Mock(spec=Image.Image)
        mock_convert.return_value = [mock_image]

        processor = PDFProcessor(dpi=600)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            output_dir = os.path.join(tmpdir, "output")

            Path(pdf_path).touch()

            processor.extract_pages_as_images(pdf_path, output_dir)

            # Verify high DPI was used
            mock_convert.assert_called_once_with(pdf_path, dpi=600, fmt="png")

    @patch("lawdit.indexer.pdf_processor.pdf2image.convert_from_path")
    def test_extract_pages_saves_as_png(self, mock_convert):
        """Test that pages are saved in PNG format."""
        mock_image = Mock(spec=Image.Image)
        mock_convert.return_value = [mock_image]

        processor = PDFProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            output_dir = os.path.join(tmpdir, "output")

            Path(pdf_path).touch()

            processor.extract_pages_as_images(pdf_path, output_dir)

            # Verify image was saved as PNG
            save_call_args = mock_image.save.call_args
            assert save_call_args[0][0].endswith(".png")
            assert save_call_args[0][1] == "PNG"

    @patch("lawdit.indexer.pdf_processor.pdf2image.convert_from_path")
    def test_extract_pages_many_pages_numbering(self, mock_convert):
        """Test that page numbering works correctly for many pages."""
        # Create 1500 mock images to test 4-digit zero-padding
        mock_images = [Mock(spec=Image.Image) for _ in range(1500)]
        mock_convert.return_value = mock_images

        processor = PDFProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            output_dir = os.path.join(tmpdir, "output")

            Path(pdf_path).touch()

            image_paths = processor.extract_pages_as_images(pdf_path, output_dir)

            # Verify numbering is correct
            assert len(image_paths) == 1500
            assert "page_0001.png" in image_paths[0]
            assert "page_0100.png" in image_paths[99]
            assert "page_1000.png" in image_paths[999]
            assert "page_1500.png" in image_paths[1499]


class TestPDFProcessorImageToBase64:
    """Tests for image_to_base64 method."""

    def test_image_to_base64_success(self):
        """Test successful conversion of image to base64."""
        processor = PDFProcessor()

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmpfile:
            # Create a simple 1x1 pixel image
            img = Image.new("RGB", (1, 1), color="red")
            img.save(tmpfile.name, "PNG")
            tmpfile_path = tmpfile.name

        try:
            # Convert to base64
            base64_string = processor.image_to_base64(tmpfile_path)

            # Verify it's a valid base64 string
            assert isinstance(base64_string, str)
            assert len(base64_string) > 0

            # Verify we can decode it back
            decoded = base64.b64decode(base64_string)
            assert len(decoded) > 0

        finally:
            os.unlink(tmpfile_path)

    def test_image_to_base64_nonexistent_file(self):
        """Test handling of non-existent file."""
        processor = PDFProcessor()

        base64_string = processor.image_to_base64("/nonexistent/file.png")

        # Should return empty string on error
        assert base64_string == ""

    def test_image_to_base64_empty_file(self):
        """Test handling of empty file."""
        processor = PDFProcessor()

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmpfile:
            # Create an empty file
            tmpfile_path = tmpfile.name

        try:
            base64_string = processor.image_to_base64(tmpfile_path)

            # Empty file should produce empty base64 or handle gracefully
            assert isinstance(base64_string, str)

        finally:
            os.unlink(tmpfile_path)

    def test_image_to_base64_actual_image_data(self):
        """Test that base64 encoding preserves image data."""
        processor = PDFProcessor()

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmpfile:
            # Create a recognizable pattern
            img = Image.new("RGB", (10, 10), color="blue")
            img.save(tmpfile.name, "PNG")
            tmpfile_path = tmpfile.name

        try:
            # Read original file
            with open(tmpfile_path, "rb") as f:
                original_data = f.read()

            # Convert to base64 and back
            base64_string = processor.image_to_base64(tmpfile_path)
            decoded_data = base64.b64decode(base64_string)

            # Verify data is preserved
            assert decoded_data == original_data

        finally:
            os.unlink(tmpfile_path)

    def test_image_to_base64_different_image_formats(self):
        """Test base64 encoding with different image formats."""
        processor = PDFProcessor()

        formats = [("PNG", ".png"), ("JPEG", ".jpg")]

        for fmt, ext in formats:
            with tempfile.NamedTemporaryFile(mode="wb", suffix=ext, delete=False) as tmpfile:
                img = Image.new("RGB", (5, 5), color="green")
                img.save(tmpfile.name, fmt)
                tmpfile_path = tmpfile.name

            try:
                base64_string = processor.image_to_base64(tmpfile_path)

                # Verify successful encoding
                assert isinstance(base64_string, str)
                assert len(base64_string) > 0

                # Verify it's valid base64
                decoded = base64.b64decode(base64_string)
                assert len(decoded) > 0

            finally:
                os.unlink(tmpfile_path)
