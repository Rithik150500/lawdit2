"""
Tools for Legal Analysis Agents

Custom tools for document retrieval and analysis.
"""

from lawdit.tools.document_tools import (
    DocumentStore,
    get_document,
    get_document_pages,
    get_document_store,
    initialize_document_store,
    internet_search,
    web_fetch,
)

__all__ = [
    "DocumentStore",
    "get_document",
    "get_document_pages",
    "get_document_store",
    "initialize_document_store",
    "internet_search",
    "web_fetch",
]
