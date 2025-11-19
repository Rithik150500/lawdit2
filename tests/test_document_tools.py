"""
Tests for document retrieval tools
"""

import base64
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PIL import Image

from lawdit.tools.document_tools import (
    DocumentStore,
    get_document,
    get_document_pages,
    get_document_store,
    initialize_document_store,
    internet_search,
    web_fetch,
)


class TestDocumentStoreInitialization:
    """Tests for DocumentStore initialization."""

    def test_init_with_valid_paths(self):
        """Test initialization with valid paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)

            assert store.index_path == index_path
            assert store.working_dir == Path(tmpdir)
            assert isinstance(store.documents, dict)

    def test_init_with_nonexistent_working_dir(self):
        """Test initialization with non-existent working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            nonexistent_dir = Path(tmpdir) / "nonexistent"

            store = DocumentStore(str(index_path), working_dir=str(nonexistent_dir))

            # Should handle gracefully
            assert len(store.documents) == 0


class TestDocumentStoreLoadDocuments:
    """Tests for _load_documents method."""

    def test_load_documents_success(self):
        """Test successful loading of document records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a document directory with a record
            doc_dir = Path(tmpdir) / "test_document"
            doc_dir.mkdir()

            record = {
                "doc_id": "doc123",
                "file_name": "test.pdf",
                "mime_type": "application/pdf",
                "total_pages": 2,
                "document_summary": "Test summary",
                "pages": [
                    {"page_num": 1, "summary": "Page 1 summary"},
                    {"page_num": 2, "summary": "Page 2 summary"},
                ],
            }

            record_path = doc_dir / "document_record.json"
            with open(record_path, "w") as f:
                json.dump(record, f)

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            # Load documents
            store = DocumentStore(str(index_path), working_dir=tmpdir)

            # Verify document was loaded
            assert len(store.documents) == 1
            assert "doc123" in store.documents
            assert store.documents["doc123"]["file_name"] == "test.pdf"
            assert store.documents["doc123"]["_dir_path"] == str(doc_dir)

    def test_load_multiple_documents(self):
        """Test loading multiple document records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple document directories
            for i in range(3):
                doc_dir = Path(tmpdir) / f"doc_{i}"
                doc_dir.mkdir()

                record = {
                    "doc_id": f"doc{i}",
                    "file_name": f"test{i}.pdf",
                    "mime_type": "application/pdf",
                    "total_pages": 1,
                    "document_summary": f"Summary {i}",
                    "pages": [{"page_num": 1, "summary": f"Page summary {i}"}],
                }

                record_path = doc_dir / "document_record.json"
                with open(record_path, "w") as f:
                    json.dump(record, f)

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)

            # Verify all documents were loaded
            assert len(store.documents) == 3
            assert "doc0" in store.documents
            assert "doc1" in store.documents
            assert "doc2" in store.documents

    def test_load_documents_invalid_json(self):
        """Test handling of invalid JSON in document records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / "bad_doc"
            doc_dir.mkdir()

            # Write invalid JSON
            record_path = doc_dir / "document_record.json"
            record_path.write_text("{ invalid json }")

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)

            # Should handle error gracefully
            assert len(store.documents) == 0


class TestDocumentStoreGetDocumentSummary:
    """Tests for get_document_summary method."""

    def test_get_document_summary_success(self):
        """Test successful retrieval of document summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / "test_doc"
            doc_dir.mkdir()

            record = {
                "doc_id": "doc123",
                "file_name": "contract.pdf",
                "mime_type": "application/pdf",
                "total_pages": 2,
                "document_summary": "Employment contract with standard terms",
                "pages": [
                    {"page_num": 1, "summary": "Title page"},
                    {"page_num": 2, "summary": "Terms and conditions"},
                ],
            }

            record_path = doc_dir / "document_record.json"
            with open(record_path, "w") as f:
                json.dump(record, f)

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)
            summary = store.get_document_summary("doc123")

            # Verify summary contains all expected information
            assert "contract.pdf" in summary
            assert "application/pdf" in summary
            assert "2" in summary
            assert "Employment contract with standard terms" in summary
            assert "Page 1: Title page" in summary
            assert "Page 2: Terms and conditions" in summary

    def test_get_document_summary_not_found(self):
        """Test retrieval of non-existent document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)
            summary = store.get_document_summary("nonexistent")

            assert "Error" in summary
            assert "not found" in summary


class TestDocumentStoreGetDocumentPages:
    """Tests for get_document_pages method."""

    def test_get_document_pages_success(self):
        """Test successful retrieval of document pages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / "test_doc"
            doc_dir.mkdir()

            pages_dir = doc_dir / "pages"
            pages_dir.mkdir()

            # Create test images
            for i in range(1, 3):
                img = Image.new("RGB", (10, 10), color="red")
                img.save(pages_dir / f"page_{i:04d}.png", "PNG")

            record = {
                "doc_id": "doc123",
                "file_name": "test.pdf",
                "mime_type": "application/pdf",
                "total_pages": 2,
                "document_summary": "Test document",
                "pages": [
                    {"page_num": 1, "summary": "Page 1 content"},
                    {"page_num": 2, "summary": "Page 2 content"},
                ],
            }

            record_path = doc_dir / "document_record.json"
            with open(record_path, "w") as f:
                json.dump(record, f)

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)
            result = store.get_document_pages("doc123", [1, 2])

            # Verify result contains expected information
            assert "test.pdf" in result
            assert "Page 1" in result
            assert "Page 2" in result
            assert "Page 1 content" in result
            assert "Page 2 content" in result

    def test_get_document_pages_not_found(self):
        """Test retrieval of pages from non-existent document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)
            result = store.get_document_pages("nonexistent", [1])

            assert "Error" in result
            assert "not found" in result

    def test_get_document_pages_missing_page_file(self):
        """Test handling of missing page image files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / "test_doc"
            doc_dir.mkdir()

            pages_dir = doc_dir / "pages"
            pages_dir.mkdir()

            # Only create page 1, not page 2
            img = Image.new("RGB", (10, 10), color="blue")
            img.save(pages_dir / "page_0001.png", "PNG")

            record = {
                "doc_id": "doc123",
                "file_name": "test.pdf",
                "mime_type": "application/pdf",
                "total_pages": 2,
                "document_summary": "Test document",
                "pages": [
                    {"page_num": 1, "summary": "Page 1 content"},
                    {"page_num": 2, "summary": "Page 2 content"},
                ],
            }

            record_path = doc_dir / "document_record.json"
            with open(record_path, "w") as f:
                json.dump(record, f)

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            store = DocumentStore(str(index_path), working_dir=tmpdir)
            result = store.get_document_pages("doc123", [1, 2])

            # Should handle missing page gracefully
            assert "Page 2: Not found" in result


class TestGlobalDocumentStore:
    """Tests for global document store functions."""

    def test_initialize_document_store(self):
        """Test initialization of global document store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            initialize_document_store(str(index_path), working_dir=tmpdir)

            store = get_document_store()

            assert isinstance(store, DocumentStore)
            assert store.index_path == index_path

    def test_get_document_store_not_initialized(self):
        """Test getting document store before initialization."""
        # Reset global store
        import lawdit.tools.document_tools

        lawdit.tools.document_tools._document_store = None

        with pytest.raises(RuntimeError) as exc_info:
            get_document_store()

        assert "not initialized" in str(exc_info.value)


class TestGetDocumentTool:
    """Tests for get_document tool."""

    def test_get_document_tool_success(self):
        """Test successful document retrieval via tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / "test_doc"
            doc_dir.mkdir()

            record = {
                "doc_id": "doc123",
                "file_name": "contract.pdf",
                "mime_type": "application/pdf",
                "total_pages": 1,
                "document_summary": "Test contract",
                "pages": [{"page_num": 1, "summary": "Contract terms"}],
            }

            record_path = doc_dir / "document_record.json"
            with open(record_path, "w") as f:
                json.dump(record, f)

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            initialize_document_store(str(index_path), working_dir=tmpdir)

            result = get_document.invoke({"doc_id": "doc123"})

            assert "contract.pdf" in result
            assert "Test contract" in result

    def test_get_document_tool_error_handling(self):
        """Test error handling in get_document tool."""
        # Reset global store
        import lawdit.tools.document_tools

        lawdit.tools.document_tools._document_store = None

        result = get_document.invoke({"doc_id": "doc123"})

        assert "Error" in result


class TestGetDocumentPagesTool:
    """Tests for get_document_pages tool."""

    def test_get_document_pages_tool_success(self):
        """Test successful page retrieval via tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / "test_doc"
            doc_dir.mkdir()

            pages_dir = doc_dir / "pages"
            pages_dir.mkdir()

            img = Image.new("RGB", (10, 10), color="green")
            img.save(pages_dir / "page_0001.png", "PNG")

            record = {
                "doc_id": "doc123",
                "file_name": "test.pdf",
                "mime_type": "application/pdf",
                "total_pages": 1,
                "document_summary": "Test document",
                "pages": [{"page_num": 1, "summary": "Page content"}],
            }

            record_path = doc_dir / "document_record.json"
            with open(record_path, "w") as f:
                json.dump(record, f)

            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index")

            initialize_document_store(str(index_path), working_dir=tmpdir)

            result = get_document_pages.invoke({"doc_id": "doc123", "page_nums": [1]})

            assert "test.pdf" in result
            assert "Page 1" in result


class TestInternetSearchTool:
    """Tests for internet_search tool."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-api-key"})
    @patch("lawdit.tools.document_tools.TavilyClient")
    def test_internet_search_success(self, mock_tavily):
        """Test successful internet search."""
        mock_client = Mock()
        mock_tavily.return_value = mock_client

        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Legal Precedent Case",
                    "url": "https://example.com/case",
                    "content": "Summary of the case",
                }
            ]
        }

        result = internet_search.invoke({"query": "contract law precedents", "max_results": 5})

        # Verify search was called
        mock_client.search.assert_called_once()

        # Verify result format
        assert "contract law precedents" in result
        assert "Legal Precedent Case" in result
        assert "https://example.com/case" in result
        assert "Summary of the case" in result

    @patch.dict(os.environ, {}, clear=True)
    def test_internet_search_no_api_key(self):
        """Test internet search without API key."""
        result = internet_search.invoke({"query": "test query"})

        assert "Error" in result
        assert "TAVILY_API_KEY" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-api-key"})
    @patch("lawdit.tools.document_tools.TavilyClient")
    def test_internet_search_api_error(self, mock_tavily):
        """Test handling of API errors."""
        mock_client = Mock()
        mock_tavily.return_value = mock_client
        mock_client.search.side_effect = Exception("API Error")

        result = internet_search.invoke({"query": "test query"})

        assert "Error" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-api-key"})
    @patch("lawdit.tools.document_tools.TavilyClient")
    def test_internet_search_with_topic(self, mock_tavily):
        """Test internet search with topic filter."""
        mock_client = Mock()
        mock_tavily.return_value = mock_client
        mock_client.search.return_value = {"results": []}

        internet_search.invoke({"query": "financial news", "max_results": 3, "topic": "finance"})

        # Verify topic was passed
        call_args = mock_client.search.call_args
        assert call_args[1]["topic"] == "finance"
        assert call_args[1]["max_results"] == 3


class TestWebFetchTool:
    """Tests for web_fetch tool."""

    @patch("lawdit.tools.document_tools.requests.get")
    def test_web_fetch_success(self, mock_get):
        """Test successful web page fetch."""
        mock_response = Mock()
        mock_response.text = "<html><body><p>Test content here</p></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = web_fetch.invoke({"url": "https://example.com/article"})

        # Verify request was made
        mock_get.assert_called_once()

        # Verify content was extracted
        assert "Test content here" in result
        assert "https://example.com/article" in result

    @patch("lawdit.tools.document_tools.requests.get")
    def test_web_fetch_timeout(self, mock_get):
        """Test handling of request timeout."""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        result = web_fetch.invoke({"url": "https://example.com/slow"})

        assert "Error" in result
        assert "timed out" in result

    @patch("lawdit.tools.document_tools.requests.get")
    def test_web_fetch_request_error(self, mock_get):
        """Test handling of request errors."""
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

        result = web_fetch.invoke({"url": "https://example.com/error"})

        assert "Error" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-api-key"})
    @patch("lawdit.tools.document_tools.TavilyClient")
    @patch("lawdit.tools.document_tools.requests.get")
    def test_web_fetch_with_tavily_extract(self, mock_get, mock_tavily):
        """Test web fetch using Tavily extract."""
        mock_response = Mock()
        mock_response.text = "<html><body>Content</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_client = Mock()
        mock_tavily.return_value = mock_client
        mock_client.extract.return_value = {
            "results": [{"raw_content": "Extracted content from Tavily"}]
        }

        result = web_fetch.invoke({"url": "https://example.com/page"})

        # Verify Tavily extract was attempted
        mock_client.extract.assert_called_once()

        # Verify Tavily content was used
        assert "Extracted content from Tavily" in result
