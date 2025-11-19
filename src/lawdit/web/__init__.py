"""Streamlit web interface for Lawdit."""

from pathlib import Path

__all__ = ["app"]

WEB_DIR = Path(__file__).parent
PAGES_DIR = WEB_DIR / "pages"
