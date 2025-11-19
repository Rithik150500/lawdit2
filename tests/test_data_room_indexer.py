"""
Tests for data room indexer
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from lawdit.indexer.data_room_indexer import DataRoomIndexer


class TestDataRoomIndexerInitialization:
    """Tests for DataRoomIndexer initialization."""

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_init_with_defaults(self, mock_vision, mock_pdf, mock_drive):
        """Test initialization with default parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            working_dir = str(Path(tmpdir) / "work")

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json",
                openai_api_key="test-key",
                working_dir=working_dir,
            )

            # Verify components were initialized
            mock_drive.assert_called_once_with("/path/to/creds.json")
            mock_pdf.assert_called_once_with(dpi=200)
            mock_vision.assert_called_once_with("test-key")

            # Verify working directory was created
            assert Path(working_dir).exists()

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_init_creates_working_directory(self, mock_vision, mock_pdf, mock_drive):
        """Test that initialization creates working directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            working_dir = str(Path(tmpdir) / "nested" / "work" / "dir")

            # Verify directory doesn't exist
            assert not Path(working_dir).exists()

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=working_dir
            )

            # Verify directory was created
            assert Path(working_dir).exists()


class TestDataRoomIndexerProcessDocument:
    """Tests for process_document method."""

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_process_pdf_document_success(self, mock_vision_class, mock_pdf_class, mock_drive_class):
        """Test successful processing of a PDF document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.download_file.return_value = True

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = [
                "/path/to/page_0001.png",
                "/path/to/page_0002.png",
            ]

            mock_vision = Mock()
            mock_vision_class.return_value = mock_vision
            mock_vision.summarize_page_image.side_effect = [
                "Summary of page 1",
                "Summary of page 2",
            ]
            mock_vision.summarize_document_from_pages.return_value = "Overall document summary"

            # Create indexer
            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            # Process document
            result = indexer.process_document(
                file_id="file123", file_name="test_document.pdf", mime_type="application/pdf"
            )

            # Verify download was called
            mock_drive.download_file.assert_called_once()

            # Verify PDF processing was called
            mock_pdf.extract_pages_as_images.assert_called_once()

            # Verify vision summarization was called for each page
            assert mock_vision.summarize_page_image.call_count == 2

            # Verify document-level summary was created
            mock_vision.summarize_document_from_pages.assert_called_once()

            # Verify result structure
            assert result is not None
            assert result["doc_id"] == "file123"
            assert result["file_name"] == "test_document.pdf"
            assert result["mime_type"] == "application/pdf"
            assert result["total_pages"] == 2
            assert result["document_summary"] == "Overall document summary"
            assert len(result["pages"]) == 2

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_process_google_doc_success(self, mock_vision_class, mock_pdf_class, mock_drive_class):
        """Test successful processing of a Google Workspace document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.export_as_pdf.return_value = True

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = ["/path/to/page_0001.png"]

            mock_vision = Mock()
            mock_vision_class.return_value = mock_vision
            mock_vision.summarize_page_image.return_value = "Page summary"
            mock_vision.summarize_document_from_pages.return_value = "Document summary"

            # Create indexer
            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            # Process Google Doc
            result = indexer.process_document(
                file_id="doc123",
                file_name="google_doc.gdoc",
                mime_type="application/vnd.google-apps.document",
            )

            # Verify export_as_pdf was called instead of download_file
            mock_drive.export_as_pdf.assert_called_once()
            mock_drive.download_file.assert_not_called()

            # Verify processing succeeded
            assert result is not None
            assert result["file_name"] == "google_doc.gdoc"

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_process_google_sheet_success(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test successful processing of a Google Sheets document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.export_as_pdf.return_value = True

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = ["/path/to/page_0001.png"]

            mock_vision = Mock()
            mock_vision_class.return_value = mock_vision
            mock_vision.summarize_page_image.return_value = "Page summary"
            mock_vision.summarize_document_from_pages.return_value = "Document summary"

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            result = indexer.process_document(
                file_id="sheet123",
                file_name="spreadsheet.gsheet",
                mime_type="application/vnd.google-apps.spreadsheet",
            )

            # Verify export was called
            mock_drive.export_as_pdf.assert_called_once()
            assert result is not None

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_process_unsupported_file_type(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test handling of unsupported file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            result = indexer.process_document(
                file_id="file123", file_name="video.mp4", mime_type="video/mp4"
            )

            # Should return None for unsupported types
            assert result is None

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_process_download_failure(self, mock_vision_class, mock_pdf_class, mock_drive_class):
        """Test handling of download failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.download_file.return_value = False

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            result = indexer.process_document(
                file_id="file123", file_name="test.pdf", mime_type="application/pdf"
            )

            # Should return None on download failure
            assert result is None

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_process_pdf_extraction_failure(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test handling of PDF extraction failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.download_file.return_value = True

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = []  # Empty list indicates failure

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            result = indexer.process_document(
                file_id="file123", file_name="test.pdf", mime_type="application/pdf"
            )

            # Should return None on extraction failure
            assert result is None

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_process_creates_document_record_json(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test that process_document creates a JSON record file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.download_file.return_value = True

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = ["/path/to/page_0001.png"]

            mock_vision = Mock()
            mock_vision_class.return_value = mock_vision
            mock_vision.summarize_page_image.return_value = "Page summary"
            mock_vision.summarize_document_from_pages.return_value = "Document summary"

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            result = indexer.process_document(
                file_id="file123", file_name="test document.pdf", mime_type="application/pdf"
            )

            # Verify JSON file was created
            expected_dir = Path(tmpdir) / "test_document.pdf"
            json_file = expected_dir / "document_record.json"

            assert json_file.exists()

            # Verify JSON content
            with open(json_file, "r") as f:
                saved_data = json.load(f)

            assert saved_data["doc_id"] == "file123"
            assert saved_data["file_name"] == "test document.pdf"


class TestDataRoomIndexerBuildDataRoomIndex:
    """Tests for build_data_room_index method."""

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_build_data_room_index_success(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test successful building of data room index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.list_folder_contents.return_value = [
                {"id": "file1", "name": "doc1.pdf", "mimeType": "application/pdf"},
                {"id": "file2", "name": "doc2.pdf", "mimeType": "application/pdf"},
            ]
            mock_drive.download_file.return_value = True

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = ["/path/to/page_0001.png"]

            mock_vision = Mock()
            mock_vision_class.return_value = mock_vision
            mock_vision.summarize_page_image.return_value = "Page summary"
            mock_vision.summarize_document_from_pages.side_effect = [
                "Summary of doc1",
                "Summary of doc2",
            ]

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            # Build index
            index_text = indexer.build_data_room_index(folder_id="folder123")

            # Verify listing was called
            mock_drive.list_folder_contents.assert_called_once_with("folder123")

            # Verify both documents were processed
            assert mock_drive.download_file.call_count == 2

            # Verify index contains both documents
            assert "file1" in index_text
            assert "file2" in index_text
            assert "doc1.pdf" in index_text
            assert "doc2.pdf" in index_text
            assert "Summary of doc1" in index_text
            assert "Summary of doc2" in index_text

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_build_data_room_index_saves_to_file(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test that index is saved to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.list_folder_contents.return_value = [
                {"id": "file1", "name": "doc1.pdf", "mimeType": "application/pdf"}
            ]
            mock_drive.download_file.return_value = True

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = ["/path/to/page_0001.png"]

            mock_vision = Mock()
            mock_vision_class.return_value = mock_vision
            mock_vision.summarize_page_image.return_value = "Page summary"
            mock_vision.summarize_document_from_pages.return_value = "Document summary"

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            # Build index with custom output path
            output_path = Path(tmpdir) / "custom_index.txt"
            indexer.build_data_room_index(folder_id="folder123", output_path=str(output_path))

            # Verify file was created
            assert output_path.exists()

            # Verify content
            with open(output_path, "r") as f:
                content = f.read()

            assert "# Data Room Index" in content
            assert "file1" in content
            assert "doc1.pdf" in content

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_build_data_room_index_empty_folder(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test building index from empty folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.list_folder_contents.return_value = []

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            # Build index
            index_text = indexer.build_data_room_index(folder_id="empty_folder")

            # Should still create an index, just empty
            assert "# Data Room Index" in index_text

    @patch("lawdit.indexer.data_room_indexer.GoogleDriveClient")
    @patch("lawdit.indexer.data_room_indexer.PDFProcessor")
    @patch("lawdit.indexer.data_room_indexer.VisionSummarizer")
    def test_build_data_room_index_skips_failed_documents(
        self, mock_vision_class, mock_pdf_class, mock_drive_class
    ):
        """Test that index building skips documents that fail to process."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup mocks
            mock_drive = Mock()
            mock_drive_class.return_value = mock_drive
            mock_drive.list_folder_contents.return_value = [
                {"id": "file1", "name": "doc1.pdf", "mimeType": "application/pdf"},
                {"id": "file2", "name": "bad.pdf", "mimeType": "application/pdf"},
                {"id": "file3", "name": "doc3.pdf", "mimeType": "application/pdf"},
            ]

            # Make middle document fail
            mock_drive.download_file.side_effect = [True, False, True]

            mock_pdf = Mock()
            mock_pdf_class.return_value = mock_pdf
            mock_pdf.extract_pages_as_images.return_value = ["/path/to/page_0001.png"]

            mock_vision = Mock()
            mock_vision_class.return_value = mock_vision
            mock_vision.summarize_page_image.return_value = "Page summary"
            mock_vision.summarize_document_from_pages.side_effect = [
                "Summary of doc1",
                "Summary of doc3",
            ]

            indexer = DataRoomIndexer(
                google_credentials_path="/path/to/creds.json", working_dir=tmpdir
            )

            # Build index
            index_text = indexer.build_data_room_index(folder_id="folder123")

            # Should contain successful documents but not failed one
            assert "file1" in index_text
            assert "doc1.pdf" in index_text
            assert "file3" in index_text
            assert "doc3.pdf" in index_text
            assert "file2" not in index_text  # Failed document should be skipped
