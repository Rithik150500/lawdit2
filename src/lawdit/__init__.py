"""
Lawdit - Legal Due Diligence Intelligence Tool

A comprehensive AI-powered legal risk analysis system for due diligence.
"""

__version__ = "0.1.0"
__author__ = "Lawdit Team"

from lawdit.indexer.data_room_indexer import DataRoomIndexer
from lawdit.indexer.google_drive_client import GoogleDriveClient
from lawdit.indexer.pdf_processor import PDFProcessor
from lawdit.indexer.vision_summarizer import VisionSummarizer

__all__ = [
    "DataRoomIndexer",
    "GoogleDriveClient",
    "PDFProcessor",
    "VisionSummarizer",
]
