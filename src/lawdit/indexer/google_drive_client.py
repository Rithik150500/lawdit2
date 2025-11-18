"""
Google Drive Client for Data Room Access

This module handles authentication and file operations with Google Drive.
"""

from typing import Any, Dict, List

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class GoogleDriveClient:
    """Client for interacting with Google Drive API.

    This client handles authentication and provides methods for listing
    and downloading files from Google Drive. It supports both OAuth2
    credentials (for user access) and service account credentials
    (for automated access).
    """

    def __init__(self, credentials_path: str, use_service_account: bool = True):
        """Initialize the Google Drive client.

        Args:
            credentials_path: Path to your Google Cloud credentials JSON file.
                            For service accounts, this is the service account key.
                            For OAuth2, this is your client secrets file.
            use_service_account: Whether to use service account authentication.
                               Service accounts are recommended for automated systems.
        """
        self.credentials_path = credentials_path
        self.use_service_account = use_service_account
        self.service = self._build_service()

    def _build_service(self):
        """Build the Google Drive API service with appropriate credentials.

        This method handles the complexity of Google authentication, choosing
        between service account credentials (for automated systems) and OAuth2
        credentials (for user-specific access).
        """
        scopes = ["https://www.googleapis.com/auth/drive.readonly"]

        if self.use_service_account:
            # Service accounts are ideal for automated systems because they
            # don't require user interaction for authentication
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=scopes
            )
        else:
            # OAuth2 credentials require user authorization but provide
            # access to user-specific files
            credentials = Credentials.from_authorized_user_file(
                self.credentials_path, scopes=scopes
            )

        return build("drive", "v3", credentials=credentials)

    def list_folder_contents(self, folder_id: str) -> List[Dict[str, Any]]:
        """List all files in a Google Drive folder.

        This method retrieves metadata for all files in a folder, including
        file IDs, names, MIME types, and sizes. This information helps us
        understand what documents exist before we begin processing.

        Args:
            folder_id: The Google Drive folder ID. You can find this in the
                      folder's URL: drive.google.com/drive/folders/FOLDER_ID

        Returns:
            A list of dictionaries containing file metadata. Each dictionary
            includes id, name, mimeType, and size fields.
        """
        try:
            # Query Google Drive API to list files in the folder
            # We use pageToken to handle folders with more files than fit in one response
            results = (
                self.service.files()
                .list(
                    q=f"'{folder_id}' in parents and trashed=false",
                    fields="nextPageToken, files(id, name, mimeType, size)",
                    pageSize=1000,  # Maximum allowed by API
                )
                .execute()
            )

            files = results.get("files", [])

            # Handle pagination if there are more than 1000 files
            while "nextPageToken" in results:
                results = (
                    self.service.files()
                    .list(
                        q=f"'{folder_id}' in parents and trashed=false",
                        fields="nextPageToken, files(id, name, mimeType, size)",
                        pageSize=1000,
                        pageToken=results["nextPageToken"],
                    )
                    .execute()
                )
                files.extend(results.get("files", []))

            return files

        except Exception as e:
            print(f"Error listing folder contents: {e}")
            return []

    def download_file(self, file_id: str, output_path: str) -> bool:
        """Download a file from Google Drive to local storage.

        This method handles the actual file download, managing the streaming
        transfer to avoid loading entire large files into memory at once.

        Args:
            file_id: The Google Drive file ID
            output_path: Local path where the file should be saved

        Returns:
            True if download succeeded, False otherwise
        """
        try:
            # Request file content from Google Drive
            request = self.service.files().get_media(fileId=file_id)

            # Create output file and download in chunks
            # This streaming approach prevents memory issues with large files
            with open(output_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"Download progress: {int(status.progress() * 100)}%")

            return True

        except Exception as e:
            print(f"Error downloading file {file_id}: {e}")
            return False

    def export_as_pdf(self, file_id: str, output_path: str) -> bool:
        """Export a Google Workspace document as PDF.

        Google Docs, Sheets, and Slides are not stored as PDFs natively.
        This method uses Google Drive's export functionality to convert
        them to PDF format, which we can then process with our image
        extraction pipeline.

        Args:
            file_id: The Google Drive file ID of the document to export
            output_path: Local path where the PDF should be saved

        Returns:
            True if export succeeded, False otherwise
        """
        try:
            # Request PDF export from Google Drive
            # The 'application/pdf' MIME type tells Google Drive we want PDF format
            request = self.service.files().export_media(fileId=file_id, mimeType="application/pdf")

            # Download the exported PDF
            with open(output_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            return True

        except Exception as e:
            print(f"Error exporting file {file_id} as PDF: {e}")
            return False
