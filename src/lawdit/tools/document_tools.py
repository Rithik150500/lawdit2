"""
Document Retrieval Tools

Tools for accessing indexed documents and their content.
"""

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Literal

import requests
from langchain_core.tools import tool
from tavily import TavilyClient


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
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
) -> str:
    """Search the internet for legal precedents, regulations, or context.

    Use this to research legal standards, regulatory requirements, case law,
    or industry practices that inform your risk analysis.

    Args:
        query: Search query focused on legal/regulatory topics
        max_results: Maximum number of results to return (default 5)
        topic: Topic filter for search results (general, news, or finance)

    Returns:
        Search results with titles, snippets, and URLs
    """
    try:
        tavily_api_key = os.environ.get("TAVILY_API_KEY")
        if not tavily_api_key:
            return "Error: TAVILY_API_KEY environment variable not set. Please configure your Tavily API key."

        tavily_client = TavilyClient(api_key=tavily_api_key)

        # Perform the search
        search_results = tavily_client.search(
            query=query,
            max_results=max_results,
            topic=topic,
            include_raw_content=False,
        )

        # Format the results
        formatted_results = [f"Search results for: {query}\n"]

        if "results" in search_results:
            for idx, result in enumerate(search_results["results"], start=1):
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                content = result.get("content", "No content available")

                formatted_results.append(
                    f"\n{idx}. {title}\n   URL: {url}\n   Summary: {content}\n"
                )
        else:
            formatted_results.append("\nNo results found.")

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Error performing search: {str(e)}"


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
    try:
        # Set a reasonable timeout and user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Fetch the web page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Try to use Tavily's extract endpoint for better content extraction
        tavily_api_key = os.environ.get("TAVILY_API_KEY")
        if tavily_api_key:
            try:
                tavily_client = TavilyClient(api_key=tavily_api_key)
                extract_result = tavily_client.extract(urls=[url])

                if extract_result and "results" in extract_result and extract_result["results"]:
                    content = extract_result["results"][0].get("raw_content", "")
                    if content:
                        return f"Content from {url}:\n\n{content}"
            except Exception:
                # Fall back to basic extraction if Tavily extract fails
                pass

        # Basic fallback: return raw HTML with a note
        from html import unescape
        import re

        # Remove script and style elements
        text = re.sub(r"<script[^>]*>.*?</script>", "", response.text, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = unescape(text).strip()

        # Limit length to avoid overwhelming context
        max_length = 10000
        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated due to length...]"

        return f"Content from {url}:\n\n{text}"

    except requests.exceptions.Timeout:
        return f"Error: Request to {url} timed out after 10 seconds."
    except requests.exceptions.RequestException as e:
        return f"Error fetching {url}: {str(e)}"
    except Exception as e:
        return f"Error processing content from {url}: {str(e)}"
