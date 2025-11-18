"""
Document Retrieval Tools

Tools for accessing indexed documents and their content.
"""

import base64
import json
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.tools import tool


class DocumentStore:
    """Store for managing indexed documents and their content."""

    def __init__(self, index_path: str, working_dir: str = "./data_room_processing"):
        """Initialize the document store.

        Args:
            index_path: Path to the data room index file
            working_dir: Directory containing processed documents
        """
        self.index_path = Path(index_path)
        self.working_dir = Path(working_dir)
        self.documents: Dict[str, Dict[str, Any]] = {}
        self._load_documents()

    def _load_documents(self) -> None:
        """Load document records from the working directory."""
        if not self.working_dir.exists():
            print(f"Warning: Working directory not found: {self.working_dir}")
            return

        # Find all document_record.json files
        for record_file in self.working_dir.glob("*/document_record.json"):
            try:
                with open(record_file, "r") as f:
                    doc_record = json.load(f)
                    doc_id = doc_record.get("doc_id")
                    if doc_id:
                        # Store path to the document directory
                        doc_record["_dir_path"] = str(record_file.parent)
                        self.documents[doc_id] = doc_record
            except Exception as e:
                print(f"Error loading document record {record_file}: {e}")

        print(f"Loaded {len(self.documents)} documents from {self.working_dir}")

    def get_document_summary(self, doc_id: str) -> str:
        """Get the complete summary of a document.

        Args:
            doc_id: Document identifier

        Returns:
            Combined summary of the document
        """
        if doc_id not in self.documents:
            return f"Error: Document {doc_id} not found in store"

        doc = self.documents[doc_id]
        summary_parts = [
            f"Document: {doc['file_name']}",
            f"Type: {doc['mime_type']}",
            f"Pages: {doc['total_pages']}",
            f"\nDocument Summary:",
            doc["document_summary"],
            f"\nPage-by-Page Summaries:",
        ]

        for page in doc.get("pages", []):
            summary_parts.append(f"\nPage {page['page_num']}: {page['summary']}")

        return "\n".join(summary_parts)

    def get_document_pages(self, doc_id: str, page_nums: List[int]) -> str:
        """Get images of specific pages from a document.

        Args:
            doc_id: Document identifier
            page_nums: List of page numbers to retrieve

        Returns:
            Base64-encoded images with metadata
        """
        if doc_id not in self.documents:
            return f"Error: Document {doc_id} not found in store"

        doc = self.documents[doc_id]
        doc_dir = Path(doc.get("_dir_path", ""))

        if not doc_dir.exists():
            return f"Error: Document directory not found for {doc_id}"

        pages_dir = doc_dir / "pages"
        if not pages_dir.exists():
            return f"Error: Pages directory not found for {doc_id}"

        result_parts = [f"Document: {doc['file_name']}", f"Requested pages: {page_nums}\n"]

        for page_num in page_nums:
            # Find the page image file
            page_file = pages_dir / f"page_{page_num:04d}.png"

            if not page_file.exists():
                result_parts.append(f"\nPage {page_num}: Not found")
                continue

            try:
                # Read and encode the image
                with open(page_file, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")

                # Get the summary for this page if available
                page_summary = ""
                for page in doc.get("pages", []):
                    if page["page_num"] == page_num:
                        page_summary = page["summary"]
                        break

                result_parts.append(
                    f"\nPage {page_num}:\n"
                    f"Summary: {page_summary}\n"
                    f"Image (base64, first 100 chars): {image_data[:100]}..."
                    f"\n[Full image data: {len(image_data)} characters]"
                )

            except Exception as e:
                result_parts.append(f"\nPage {page_num}: Error reading image - {e}")

        return "\n".join(result_parts)


# Global document store instance
_document_store: DocumentStore = None


def initialize_document_store(index_path: str, working_dir: str = "./data_room_processing"):
    """Initialize the global document store.

    Args:
        index_path: Path to the data room index file
        working_dir: Directory containing processed documents
    """
    global _document_store
    _document_store = DocumentStore(index_path, working_dir)


def get_document_store() -> DocumentStore:
    """Get the global document store instance.

    Returns:
        The document store instance

    Raises:
        RuntimeError: If document store not initialized
    """
    if _document_store is None:
        raise RuntimeError(
            "Document store not initialized. Call initialize_document_store() first."
        )
    return _document_store


@tool
def get_document(doc_id: str) -> str:
    """Retrieve the complete summary of a document by combining all page summaries.

    This tool returns a comprehensive text summary that synthesizes information
    from all pages of the specified document. Use this when you need an overview
    of the entire document without examining individual pages.

    Args:
        doc_id: The unique identifier for the document (from the Data Room Index)

    Returns:
        Combined summary description covering all pages of the document

    Example:
        To get an overview of the Share Purchase Agreement:
        get_document(doc_id="SPA-2024-001")
    """
    try:
        store = get_document_store()
        return store.get_document_summary(doc_id)
    except Exception as e:
        return f"Error retrieving document {doc_id}: {e}"


@tool
def get_document_pages(doc_id: str, page_nums: List[int]) -> str:
    """Retrieve images of specific pages from a document for detailed review.

    This tool returns the actual page images for detailed examination when the
    summary is insufficient and you need to review specific clauses, signatures,
    or detailed content. The images are returned as base64-encoded data.

    Args:
        doc_id: The unique identifier for the document
        page_nums: List of page numbers to retrieve (e.g., [1, 5, 12])

    Returns:
        Base64-encoded images of the requested pages with metadata

    Example:
        To examine pages 3 and 7 of a contract for specific clauses:
        get_document_pages(doc_id="CONTRACT-2024-042", page_nums=[3, 7])

    Note: Use this sparingly as page images consume significant context.
    Only retrieve pages when you need to verify specific details that aren't
    clear from the summary.
    """
    try:
        store = get_document_store()
        return store.get_document_pages(doc_id, page_nums)
    except Exception as e:
        return f"Error retrieving pages from document {doc_id}: {e}"


@tool
def internet_search(query: str, max_results: int = 5) -> str:
    """Search the internet for legal precedents, regulations, or context.

    Use this to research legal standards, regulatory requirements, case law,
    or industry practices that inform your risk analysis.

    Args:
        query: Search query focused on legal/regulatory topics
        max_results: Maximum number of results to return (default 5)

    Returns:
        Search results with titles, snippets, and URLs
    """
    # Placeholder implementation - integrate with actual search API
    return f"Search results for: {query}\n\n[Search functionality to be implemented]"


@tool
def web_fetch(url: str) -> str:
    """Fetch and extract content from a specific web page.

    Use this to retrieve full text of legal resources, regulatory guidance,
    or reference materials identified through search.

    Args:
        url: The URL to fetch content from

    Returns:
        Extracted text content from the web page
    """
    # Placeholder implementation - integrate with actual web fetch
    return f"Content from {url}\n\n[Web fetch functionality to be implemented]"
