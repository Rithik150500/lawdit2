"""
Tests for Google Drive client
"""

import io
import tempfile
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from lawdit.indexer.google_drive_client import GoogleDriveClient


class TestGoogleDriveClientInitialization:
    """Tests for GoogleDriveClient initialization."""

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_init_with_service_account(self, mock_build, mock_service_account):
        """Test initialization with service account credentials."""
        mock_creds = Mock()
        mock_service_account.Credentials.from_service_account_file.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        client = GoogleDriveClient(
            credentials_path="/path/to/service-account.json", use_service_account=True
        )

        # Verify service account credentials were loaded
        mock_service_account.Credentials.from_service_account_file.assert_called_once_with(
            "/path/to/service-account.json",
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )

        # Verify Drive API service was built
        mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)

        assert client.credentials_path == "/path/to/service-account.json"
        assert client.use_service_account is True
        assert client.service == mock_service

    @patch("lawdit.indexer.google_drive_client.Credentials")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_init_with_oauth2(self, mock_build, mock_credentials):
        """Test initialization with OAuth2 credentials."""
        mock_creds = Mock()
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        client = GoogleDriveClient(
            credentials_path="/path/to/oauth2-credentials.json", use_service_account=False
        )

        # Verify OAuth2 credentials were loaded
        mock_credentials.from_authorized_user_file.assert_called_once_with(
            "/path/to/oauth2-credentials.json",
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )

        # Verify Drive API service was built
        mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)

        assert client.credentials_path == "/path/to/oauth2-credentials.json"
        assert client.use_service_account is False
        assert client.service == mock_service


class TestGoogleDriveClientListFolderContents:
    """Tests for list_folder_contents method."""

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_list_folder_contents_success(self, mock_build, mock_service_account):
        """Test successful listing of folder contents."""
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files_list = Mock()
        mock_service.files.return_value.list.return_value = mock_files_list

        # Mock API response
        mock_response = {
            "files": [
                {"id": "file1", "name": "document1.pdf", "mimeType": "application/pdf", "size": "1024"},
                {"id": "file2", "name": "document2.pdf", "mimeType": "application/pdf", "size": "2048"},
            ]
        }
        mock_files_list.execute.return_value = mock_response

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")
        files = client.list_folder_contents("folder123")

        # Verify API call was made correctly
        mock_service.files.return_value.list.assert_called_once_with(
            q="'folder123' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType, size)",
            pageSize=1000,
        )

        # Verify results
        assert len(files) == 2
        assert files[0]["id"] == "file1"
        assert files[0]["name"] == "document1.pdf"
        assert files[1]["id"] == "file2"
        assert files[1]["name"] == "document2.pdf"

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_list_folder_contents_with_pagination(self, mock_build, mock_service_account):
        """Test listing folder contents with pagination."""
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock first page response
        first_response = {
            "files": [{"id": "file1", "name": "doc1.pdf", "mimeType": "application/pdf", "size": "1024"}],
            "nextPageToken": "token123",
        }

        # Mock second page response
        second_response = {
            "files": [{"id": "file2", "name": "doc2.pdf", "mimeType": "application/pdf", "size": "2048"}]
        }

        mock_files_list = Mock()
        mock_service.files.return_value.list.return_value = mock_files_list
        mock_files_list.execute.side_effect = [first_response, second_response]

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")
        files = client.list_folder_contents("folder123")

        # Verify two API calls were made (one for each page)
        assert mock_service.files.return_value.list.call_count == 2

        # Verify pagination token was used in second call
        second_call_args = mock_service.files.return_value.list.call_args_list[1]
        assert second_call_args[1]["pageToken"] == "token123"

        # Verify all files from both pages were returned
        assert len(files) == 2
        assert files[0]["id"] == "file1"
        assert files[1]["id"] == "file2"

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_list_folder_contents_empty_folder(self, mock_build, mock_service_account):
        """Test listing contents of an empty folder."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files_list = Mock()
        mock_service.files.return_value.list.return_value = mock_files_list
        mock_files_list.execute.return_value = {"files": []}

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")
        files = client.list_folder_contents("empty_folder")

        assert len(files) == 0

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_list_folder_contents_api_error(self, mock_build, mock_service_account):
        """Test handling of API errors when listing folder contents."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_files_list = Mock()
        mock_service.files.return_value.list.return_value = mock_files_list
        mock_files_list.execute.side_effect = Exception("API Error")

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")
        files = client.list_folder_contents("folder123")

        # Should return empty list on error
        assert files == []


class TestGoogleDriveClientDownloadFile:
    """Tests for download_file method."""

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    @patch("lawdit.indexer.google_drive_client.MediaIoBaseDownload")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_file_success(self, mock_file, mock_download, mock_build, mock_service_account):
        """Test successful file download."""
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_request = Mock()
        mock_service.files.return_value.get_media.return_value = mock_request

        # Mock downloader to simulate download progress
        mock_downloader = Mock()
        mock_download.return_value = mock_downloader

        # Simulate download progress: first chunk 50%, second chunk 100%
        mock_status_1 = Mock()
        mock_status_1.progress.return_value = 0.5
        mock_status_2 = Mock()
        mock_status_2.progress.return_value = 1.0

        mock_downloader.next_chunk.side_effect = [
            (mock_status_1, False),
            (mock_status_2, True),
        ]

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")

        with tempfile.NamedTemporaryFile() as tmpfile:
            result = client.download_file("file123", tmpfile.name)

        # Verify API call was made
        mock_service.files.return_value.get_media.assert_called_once_with(fileId="file123")

        # Verify download was successful
        assert result is True

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_download_file_api_error(self, mock_build, mock_service_account):
        """Test handling of API errors during file download."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_service.files.return_value.get_media.side_effect = Exception("Download failed")

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")

        with tempfile.NamedTemporaryFile() as tmpfile:
            result = client.download_file("file123", tmpfile.name)

        # Should return False on error
        assert result is False


class TestGoogleDriveClientExportAsPdf:
    """Tests for export_as_pdf method."""

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    @patch("lawdit.indexer.google_drive_client.MediaIoBaseDownload")
    @patch("builtins.open", new_callable=mock_open)
    def test_export_as_pdf_success(self, mock_file, mock_download, mock_build, mock_service_account):
        """Test successful PDF export."""
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_request = Mock()
        mock_service.files.return_value.export_media.return_value = mock_request

        # Mock downloader
        mock_downloader = Mock()
        mock_download.return_value = mock_downloader
        mock_downloader.next_chunk.return_value = (Mock(), True)

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")

        with tempfile.NamedTemporaryFile() as tmpfile:
            result = client.export_as_pdf("doc123", tmpfile.name)

        # Verify API call was made with correct MIME type
        mock_service.files.return_value.export_media.assert_called_once_with(
            fileId="doc123", mimeType="application/pdf"
        )

        # Verify export was successful
        assert result is True

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    def test_export_as_pdf_api_error(self, mock_build, mock_service_account):
        """Test handling of API errors during PDF export."""
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_service.files.return_value.export_media.side_effect = Exception("Export failed")

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")

        with tempfile.NamedTemporaryFile() as tmpfile:
            result = client.export_as_pdf("doc123", tmpfile.name)

        # Should return False on error
        assert result is False

    @patch("lawdit.indexer.google_drive_client.service_account")
    @patch("lawdit.indexer.google_drive_client.build")
    @patch("lawdit.indexer.google_drive_client.MediaIoBaseDownload")
    @patch("builtins.open", new_callable=mock_open)
    def test_export_as_pdf_multi_chunk_download(
        self, mock_file, mock_download, mock_build, mock_service_account
    ):
        """Test PDF export with multiple download chunks."""
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service

        mock_request = Mock()
        mock_service.files.return_value.export_media.return_value = mock_request

        # Mock downloader with multiple chunks
        mock_downloader = Mock()
        mock_download.return_value = mock_downloader

        # Simulate three chunks
        mock_downloader.next_chunk.side_effect = [
            (Mock(), False),
            (Mock(), False),
            (Mock(), True),
        ]

        client = GoogleDriveClient(credentials_path="/path/to/creds.json")

        with tempfile.NamedTemporaryFile() as tmpfile:
            result = client.export_as_pdf("doc123", tmpfile.name)

        # Verify three chunks were downloaded
        assert mock_downloader.next_chunk.call_count == 3

        # Verify export was successful
        assert result is True
