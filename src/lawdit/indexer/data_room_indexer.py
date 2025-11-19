"""
Data Room Indexer - Main Orchestration Module

Coordinates the complete pipeline from Google Drive to structured index.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from lawdit.indexer.google_drive_client import GoogleDriveClient
from lawdit.indexer.pdf_processor import PDFProcessor
from lawdit.indexer.vision_summarizer import VisionSummarizer


class DataRoomIndexer:
    """Main orchestrator for building the data room index.

    This class coordinates all the pieces: downloading from Google Drive,
    converting to images, analyzing pages, creating document summaries,
    and compiling the final index. It represents the complete pipeline
    from raw files to structured index.
    """

    def __init__(
        self,
        google_credentials_path: str,
        openai_api_key: str = None,
        working_dir: str = "./data_room_processing",
    ):
        """Initialize the data room indexer.

        Args:
            google_credentials_path: Path to Google Cloud credentials
            openai_api_key: OpenAI API key (optional, can use env var)
            working_dir: Directory for storing temporary files during processing
        """
        self.drive_client = GoogleDriveClient(google_credentials_path)
        self.pdf_processor = PDFProcessor(dpi=200)
        self.vision_summarizer = VisionSummarizer(openai_api_key)
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)

    def process_document(
        self, file_id: str, file_name: str, mime_type: str
    ) -> Dict[str, Any] | None:
        """Process a single document from Google Drive.

        This method handles the complete workflow for one document:
        download, convert to PDF if needed, extract pages, analyze each
        page, and create document summary.

        Args:
            file_id: Google Drive file ID
            file_name: Name of the file
            mime_type: MIME type of the file

        Returns:
            Dictionary containing document metadata and summaries
        """
        print(f"\n{'='*70}")
        print(f"Processing: {file_name}")
        print(f"{'='*70}")

        # Create a unique directory for this document
        doc_slug = file_name.replace(" ", "_").replace("/", "_")
        doc_dir = self.working_dir / doc_slug
        doc_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = doc_dir / f"{doc_slug}.pdf"

        # Step 1: Download or export the document as PDF
        print("Step 1: Downloading document...")
        if mime_type == "application/pdf":
            # Already a PDF, just download it
            success = self.drive_client.download_file(file_id, str(pdf_path))
        elif mime_type in [
            "application/vnd.google-apps.document",
            "application/vnd.google-apps.spreadsheet",
            "application/vnd.google-apps.presentation",
        ]:
            # Google Workspace document, export as PDF
            success = self.drive_client.export_as_pdf(file_id, str(pdf_path))
        else:
            print(f"Unsupported file type: {mime_type}")
            return None

        if not success:
            print(f"Failed to download {file_name}")
            return None

        # Step 2: Extract pages as images
        print("Step 2: Extracting pages as images...")
        pages_dir = doc_dir / "pages"
        image_paths = self.pdf_processor.extract_pages_as_images(str(pdf_path), str(pages_dir))

        if not image_paths:
            print(f"Failed to extract pages from {file_name}")
            return None

        # Step 3: Analyze each page with vision
        print(f"Step 3: Analyzing {len(image_paths)} pages with vision...")
        page_summaries = []
        for page_num, image_path in enumerate(image_paths, start=1):
            summary = self.vision_summarizer.summarize_page_image(image_path, page_num)
            page_summaries.append(
                {"page_num": page_num, "summary": summary, "image_path": image_path}
            )

        # Step 4: Create document-level summary
        print("Step 4: Creating document-level summary...")
        document_summary = self.vision_summarizer.summarize_document_from_pages(
            page_summaries, file_name
        )

        # Compile the complete document record
        document_record = {
            "doc_id": file_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "total_pages": len(page_summaries),
            "document_summary": document_summary,
            "pages": page_summaries,
        }

        # Save the document record to JSON for reference
        record_path = doc_dir / "document_record.json"
        with open(record_path, "w") as f:
            # Remove image_path from pages before saving (not needed in JSON)
            record_for_json = {
                **document_record,
                "pages": [
                    {k: v for k, v in p.items() if k != "image_path"}
                    for p in document_record["pages"]
                ],
            }
            json.dump(record_for_json, f, indent=2)

        print(f"Completed processing: {file_name}")
        return document_record

    def build_data_room_index(self, folder_id: str, output_path: str = None) -> str:
        """Build a complete data room index from a Google Drive folder.

        This is the main entry point for the indexing pipeline. It processes
        all documents in a folder and compiles them into a formatted index
        that can be used by the legal analysis agent.

        Args:
            folder_id: Google Drive folder ID containing the data room documents
            output_path: Optional path to save the index. If not provided,
                        saves to working_dir/data_room_index.txt

        Returns:
            The formatted data room index as a string
        """
        print(f"\n{'='*70}")
        print("BUILDING DATA ROOM INDEX")
        print(f"{'='*70}\n")

        # Step 1: List all files in the folder
        print("Step 1: Listing files in Google Drive folder...")
        files = self.drive_client.list_folder_contents(folder_id)
        print(f"Found {len(files)} files to process\n")

        # Step 2: Process each document
        print("Step 2: Processing documents...")
        document_records = []
        for idx, file in enumerate(files, start=1):
            print(f"\nProcessing file {idx}/{len(files)}")
            record = self.process_document(file["id"], file["name"], file["mimeType"])
            if record:
                document_records.append(record)

        # Step 3: Format the index
        print(f"\n{'='*70}")
        print("Step 3: Formatting data room index...")
        print(f"{'='*70}\n")

        index_lines = ["# Data Room Index\n"]

        # List all documents in a simple format
        for doc in document_records:
            index_lines.append(f"- **{doc['doc_id']}**: {doc['file_name']}")
            index_lines.append(f"  Summary: {doc['document_summary']}\n")

        index_text = "\n".join(index_lines)

        # Save the index
        if output_path is None:
            output_path = self.working_dir / "data_room_index.txt"

        with open(output_path, "w") as f:
            f.write(index_text)

        print(f"Data room index saved to: {output_path}")
        print(f"Total documents indexed: {len(document_records)}")

        return index_text
