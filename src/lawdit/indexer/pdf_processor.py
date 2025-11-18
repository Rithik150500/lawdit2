"""
PDF Processing Module

Handles conversion of PDF documents to images for vision-based analysis.
"""

import base64
import os
from pathlib import Path
from typing import List

import pdf2image


class PDFProcessor:
    """Processor for extracting images from PDF documents.

    This processor handles the conversion of PDF pages to images, which
    is necessary because OpenAI's vision models work with images rather
    than PDF files directly. The quality and resolution settings here
    balance file size (which affects token costs) against readability.
    """

    def __init__(self, dpi: int = 200):
        """Initialize the PDF processor.

        Args:
            dpi: Dots per inch for image conversion. Higher DPI produces
                better quality images but increases file size and token costs.
                200 DPI provides good readability for most text documents
                while keeping costs reasonable.
        """
        self.dpi = dpi

    def extract_pages_as_images(self, pdf_path: str, output_dir: str) -> List[str]:
        """Extract all pages from a PDF as individual image files.

        This method converts each page of the PDF into a separate PNG image.
        We use PNG format because it provides lossless compression, ensuring
        text remains crisp and readable for OCR and vision analysis.

        Args:
            pdf_path: Path to the PDF file to process
            output_dir: Directory where page images should be saved

        Returns:
            List of paths to the generated image files, ordered by page number
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Convert PDF pages to PIL Image objects
            # pdf2image internally uses poppler to render PDF pages
            images = pdf2image.convert_from_path(pdf_path, dpi=self.dpi, fmt="png")

            image_paths = []
            for page_num, image in enumerate(images, start=1):
                # Save each page with a numbered filename
                # Zero-padding ensures correct alphabetical sorting
                image_path = os.path.join(output_dir, f"page_{page_num:04d}.png")
                image.save(image_path, "PNG")
                image_paths.append(image_path)
                print(f"Extracted page {page_num} to {image_path}")

            return image_paths

        except Exception as e:
            print(f"Error extracting pages from {pdf_path}: {e}")
            return []

    def image_to_base64(self, image_path: str) -> str:
        """Convert an image file to base64-encoded string.

        Base64 encoding allows us to embed image data directly in API
        requests rather than hosting images on a server. This simplifies
        the architecture but increases request payload size.

        Args:
            image_path: Path to the image file

        Returns:
            Base64-encoded string representation of the image
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_string
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return ""
