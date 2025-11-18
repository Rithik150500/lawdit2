"""
Vision-Based Document Summarization

Uses OpenAI's vision capabilities to analyze and summarize document pages.
"""

import base64
import os
from typing import Any, Dict, List

from openai import OpenAI


class VisionSummarizer:
    """Summarizer using OpenAI's vision capabilities.

    This class handles all interactions with OpenAI's vision API for
    analyzing document page images and generating summaries. It uses
    GPT-4 Vision because we're processing potentially hundreds of pages
    and need cost-efficient analysis.
    """

    def __init__(self, api_key: str = None):
        """Initialize the vision summarizer.

        Args:
            api_key: OpenAI API key. If not provided, will look for
                    OPENAI_API_KEY environment variable.
        """
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-4-vision-preview"  # Cost-optimized model for vision tasks

    def summarize_page_image(self, image_path: str, page_number: int) -> str:
        """Analyze a page image and generate a summary description.

        This method sends a page image to GPT-4 Vision with instructions to
        extract and summarize the key information. The prompt is carefully
        crafted to focus on information relevant for legal analysis while
        remaining concise.

        Args:
            image_path: Path to the page image file
            page_number: The page number (for context in the prompt)

        Returns:
            A text summary of the page contents
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            # Construct the prompt for page analysis
            # This prompt guides the model to extract structured information
            # relevant for legal due diligence
            prompt = f"""You are analyzing page {page_number} of a legal document.
Please provide a concise summary that captures:

1. The type of content on this page (e.g., contract clause, financial table, signature block, exhibit)
2. Key information present (parties, dates, amounts, obligations, terms)
3. Any notable or concerning provisions
4. References to other documents or sections

Be specific and factual. Focus on information that would be relevant for legal risk assessment.
Keep your summary to 2-3 sentences unless the page contains complex information requiring more detail."""

            # Call OpenAI's vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            # Extract the text summary from the response
            summary = response.choices[0].message.content

            print(f"Summarized page {page_number}: {summary[:100]}...")
            return summary

        except Exception as e:
            print(f"Error summarizing page {page_number} from {image_path}: {e}")
            return f"Error processing page {page_number}"

    def summarize_document_from_pages(
        self, page_summaries: List[Dict[str, Any]], document_name: str
    ) -> str:
        """Create a document-level summary from individual page summaries.

        This method takes all the page summaries for a document and asks
        the model to synthesize them into a coherent document-level summary.
        This aggregation step helps identify themes and patterns that span
        multiple pages.

        Args:
            page_summaries: List of dictionaries containing page_num and summary
            document_name: Name of the document being summarized

        Returns:
            A comprehensive summary of the entire document
        """
        try:
            # Compile all page summaries into a single text for analysis
            combined_pages = "\n\n".join(
                [f"Page {ps['page_num']}: {ps['summary']}" for ps in page_summaries]
            )

            # Construct the prompt for document-level summarization
            # This prompt asks the model to synthesize across pages
            prompt = f"""You are creating a comprehensive summary of the document "{document_name}"
based on individual page summaries.

Here are the summaries of each page:

{combined_pages}

Please provide a document-level summary that:

1. Identifies the document type and purpose
2. Lists the main parties involved
3. Summarizes key terms, provisions, or information
4. Notes any concerning clauses or unusual provisions
5. Highlights important dates, amounts, or obligations
6. Indicates the document's relevance for legal due diligence

Your summary should be comprehensive but concise (approximately 150-200 words).
Focus on information that would help a legal analyst understand this document's
significance without reading every page."""

            # Call OpenAI API for document-level summarization
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )

            summary = response.choices[0].message.content

            print(f"Created document summary for {document_name}")
            return summary

        except Exception as e:
            print(f"Error creating document summary for {document_name}: {e}")
            return f"Error summarizing document {document_name}"
