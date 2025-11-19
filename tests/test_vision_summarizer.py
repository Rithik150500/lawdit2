"""
Tests for vision-based document summarization
"""

import base64
import os
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image

from lawdit.indexer.vision_summarizer import VisionSummarizer


class TestVisionSummarizerInitialization:
    """Tests for VisionSummarizer initialization."""

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_init_with_api_key(self, mock_openai):
        """Test initialization with provided API key."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        summarizer = VisionSummarizer(api_key="test-api-key-123")

        # Verify OpenAI client was initialized with the key
        mock_openai.assert_called_once_with(api_key="test-api-key-123")

        assert summarizer.client == mock_client
        assert summarizer.model == "gpt-5-nano"

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"})
    def test_init_with_env_api_key(self, mock_openai):
        """Test initialization with API key from environment."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        summarizer = VisionSummarizer()

        # Verify OpenAI client was initialized with env key
        mock_openai.assert_called_once_with(api_key="env-api-key")

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_init_without_api_key(self, mock_openai):
        """Test initialization without API key defaults to None."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {}, clear=True):
            summarizer = VisionSummarizer()

            # Should pass None when no key is provided
            mock_openai.assert_called_once_with(api_key=None)


class TestVisionSummarizerSummarizePageImage:
    """Tests for summarize_page_image method."""

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_page_image_success(self, mock_openai):
        """Test successful page image summarization."""
        # Setup mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This page contains a contract clause regarding payment terms."

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        # Create a temporary image file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmpfile:
            img = Image.new("RGB", (100, 100), color="white")
            img.save(tmpfile.name, "PNG")
            tmpfile_path = tmpfile.name

        try:
            summary = summarizer.summarize_page_image(tmpfile_path, page_number=1)

            # Verify API was called
            assert mock_client.chat.completions.create.called

            # Verify correct model was used
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]["model"] == "gpt-5-nano"
            assert call_args[1]["max_tokens"] == 300

            # Verify summary was returned
            assert summary == "This page contains a contract clause regarding payment terms."

        finally:
            os.unlink(tmpfile_path)

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_page_image_includes_page_number(self, mock_openai):
        """Test that page number is included in the prompt."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Summary text"

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmpfile:
            img = Image.new("RGB", (100, 100), color="white")
            img.save(tmpfile.name, "PNG")
            tmpfile_path = tmpfile.name

        try:
            summarizer.summarize_page_image(tmpfile_path, page_number=42)

            # Verify prompt includes page number
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]["messages"]
            prompt_text = messages[0]["content"][0]["text"]

            assert "page 42" in prompt_text

        finally:
            os.unlink(tmpfile_path)

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_page_image_with_base64_encoding(self, mock_openai):
        """Test that image is properly base64 encoded."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Summary"

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmpfile:
            img = Image.new("RGB", (10, 10), color="red")
            img.save(tmpfile.name, "PNG")
            tmpfile_path = tmpfile.name

        try:
            summarizer.summarize_page_image(tmpfile_path, page_number=1)

            # Verify image_url was included in the message
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]["messages"]
            image_content = messages[0]["content"][1]

            assert image_content["type"] == "image_url"
            assert "data:image/png;base64," in image_content["image_url"]["url"]

            # Verify it's valid base64
            base64_part = image_content["image_url"]["url"].split(",")[1]
            decoded = base64.b64decode(base64_part)
            assert len(decoded) > 0

        finally:
            os.unlink(tmpfile_path)

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_page_image_error_handling(self, mock_openai):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        summarizer = VisionSummarizer(api_key="test-key")

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as tmpfile:
            img = Image.new("RGB", (10, 10), color="blue")
            img.save(tmpfile.name, "PNG")
            tmpfile_path = tmpfile.name

        try:
            summary = summarizer.summarize_page_image(tmpfile_path, page_number=5)

            # Should return error message
            assert "Error processing page 5" in summary

        finally:
            os.unlink(tmpfile_path)

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_page_image_nonexistent_file(self, mock_openai):
        """Test handling of non-existent image file."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        summarizer = VisionSummarizer(api_key="test-key")

        summary = summarizer.summarize_page_image("/nonexistent/image.png", page_number=1)

        # Should return error message
        assert "Error processing page 1" in summary


class TestVisionSummarizerSummarizeDocumentFromPages:
    """Tests for summarize_document_from_pages method."""

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_document_from_pages_success(self, mock_openai):
        """Test successful document summarization from page summaries."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a comprehensive employment contract with standard terms and conditions."

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        page_summaries = [
            {"page_num": 1, "summary": "Cover page with title and date"},
            {"page_num": 2, "summary": "Employment terms and salary details"},
            {"page_num": 3, "summary": "Benefits and vacation policy"},
        ]

        summary = summarizer.summarize_document_from_pages(page_summaries, "Employment_Contract.pdf")

        # Verify API was called
        assert mock_client.chat.completions.create.called

        # Verify correct model was used
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-5-nano"
        assert call_args[1]["max_tokens"] == 500

        # Verify summary was returned
        assert summary == "This is a comprehensive employment contract with standard terms and conditions."

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_document_includes_all_pages(self, mock_openai):
        """Test that all page summaries are included in the prompt."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Document summary"

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        page_summaries = [
            {"page_num": 1, "summary": "First page content"},
            {"page_num": 2, "summary": "Second page content"},
            {"page_num": 3, "summary": "Third page content"},
        ]

        summarizer.summarize_document_from_pages(page_summaries, "Test_Document.pdf")

        # Verify all page summaries are in the prompt
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        prompt_text = messages[0]["content"]

        assert "Page 1: First page content" in prompt_text
        assert "Page 2: Second page content" in prompt_text
        assert "Page 3: Third page content" in prompt_text

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_document_includes_document_name(self, mock_openai):
        """Test that document name is included in the prompt."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Summary"

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        page_summaries = [{"page_num": 1, "summary": "Content"}]

        summarizer.summarize_document_from_pages(page_summaries, "Important_Contract.pdf")

        # Verify document name is in the prompt
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        prompt_text = messages[0]["content"]

        assert "Important_Contract.pdf" in prompt_text

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_document_empty_pages(self, mock_openai):
        """Test handling of empty page summaries list."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "No content available"

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        summary = summarizer.summarize_document_from_pages([], "Empty_Document.pdf")

        # Should still call API and return a summary
        assert mock_client.chat.completions.create.called
        assert isinstance(summary, str)

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_document_error_handling(self, mock_openai):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        summarizer = VisionSummarizer(api_key="test-key")

        page_summaries = [{"page_num": 1, "summary": "Content"}]

        summary = summarizer.summarize_document_from_pages(page_summaries, "Test.pdf")

        # Should return error message
        assert "Error summarizing document Test.pdf" in summary

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_document_single_page(self, mock_openai):
        """Test document summarization with a single page."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Single page document summary"

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        page_summaries = [{"page_num": 1, "summary": "Single page with all content"}]

        summary = summarizer.summarize_document_from_pages(page_summaries, "Single_Page.pdf")

        assert summary == "Single page document summary"
        assert mock_client.chat.completions.create.called

    @patch("lawdit.indexer.vision_summarizer.OpenAI")
    def test_summarize_document_many_pages(self, mock_openai):
        """Test document summarization with many pages."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Multi-page document summary"

        mock_client.chat.completions.create.return_value = mock_response

        summarizer = VisionSummarizer(api_key="test-key")

        # Create 50 page summaries
        page_summaries = [
            {"page_num": i, "summary": f"Content of page {i}"} for i in range(1, 51)
        ]

        summary = summarizer.summarize_document_from_pages(page_summaries, "Long_Document.pdf")

        # Verify API was called
        assert mock_client.chat.completions.create.called

        # Verify summary was returned
        assert summary == "Multi-page document summary"

        # Verify all pages were included in prompt
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        prompt_text = messages[0]["content"]

        assert "Page 1: Content of page 1" in prompt_text
        assert "Page 50: Content of page 50" in prompt_text
