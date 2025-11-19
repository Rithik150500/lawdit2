"""
Streamlit Web Interface for Lawdit
AI-Powered Legal Due Diligence Intelligence Tool
"""

import os
import sys
from pathlib import Path
from typing import Optional

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Lawdit - Legal Due Diligence Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .status-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .status-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .status-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    """Main application entry point."""
    # Header
    st.markdown('<div class="main-header">⚖️ Lawdit</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered Legal Due Diligence Intelligence Tool</div>',
        unsafe_allow_html=True,
    )

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "⚙️ Configuration",
            "📥 Index Documents",
            "🔍 Analyze Documents",
            "📊 View Results",
            "📄 Reports",
        ],
    )

    # Initialize session state
    if "config_valid" not in st.session_state:
        st.session_state.config_valid = False
    if "index_file" not in st.session_state:
        st.session_state.index_file = None
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False

    # Route to appropriate page
    if page == "🏠 Home":
        show_home()
    elif page == "⚙️ Configuration":
        show_configuration()
    elif page == "📥 Index Documents":
        show_indexer()
    elif page == "🔍 Analyze Documents":
        show_analyzer()
    elif page == "📊 View Results":
        show_results()
    elif page == "📄 Reports":
        show_reports()


def show_home() -> None:
    """Display home page with overview and instructions."""
    st.header("Welcome to Lawdit")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 🎯 What is Lawdit?

            Lawdit is an AI-powered legal intelligence tool that automates the processing
            and analysis of legal documents for comprehensive due diligence.

            ### ✨ Key Features

            - **Automated Document Indexing**: Process entire Google Drive folders
            - **Vision-Based Analysis**: Extract information from PDFs using AI
            - **Multi-Agent Analysis**: Specialized AI agents for legal domains
            - **Professional Deliverables**: Word reports and interactive dashboards
            - **Cost-Optimized**: Smart model selection to minimize API costs
            """
        )

    with col2:
        st.markdown(
            """
            ### 🚀 Getting Started

            1. **Configure** your API keys and credentials
            2. **Index** your Google Drive folder of legal documents
            3. **Analyze** the documents for legal risks
            4. **Review** results and download professional reports

            ### 📋 Risk Categories

            - **Contracts**: Terms, obligations, liabilities
            - **Compliance**: Regulatory adherence, violations
            - **Litigation**: Lawsuits, disputes, proceedings
            - **Corporate Governance**: Structure, policies, decisions
            """
        )

    # System status
    st.markdown("---")
    st.subheader("System Status")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status = "✅ Ready" if st.session_state.config_valid else "⚠️ Not Configured"
        st.metric("Configuration", status)

    with col2:
        status = "✅ Ready" if st.session_state.index_file else "⏳ Pending"
        st.metric("Index Status", status)

    with col3:
        status = "✅ Complete" if st.session_state.analysis_complete else "⏳ Pending"
        st.metric("Analysis Status", status)

    with col4:
        output_dir = Path("./outputs")
        report_count = (
            len(list(output_dir.glob("*.docx"))) + len(list(output_dir.glob("*.html")))
            if output_dir.exists()
            else 0
        )
        st.metric("Reports Available", report_count)

    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⚙️ Configure Settings", use_container_width=True):
            st.session_state.page = "⚙️ Configuration"
            st.rerun()

    with col2:
        if st.button("📥 Index Documents", use_container_width=True):
            st.session_state.page = "📥 Index Documents"
            st.rerun()

    with col3:
        if st.button("🔍 Start Analysis", use_container_width=True):
            st.session_state.page = "🔍 Analyze Documents"
            st.rerun()


def show_configuration() -> None:
    """Display configuration page for API keys and settings."""
    from lawdit.web.pages import configuration

    configuration.show()


def show_indexer() -> None:
    """Display indexer page for processing documents."""
    from lawdit.web.pages import indexer

    indexer.show()


def show_analyzer() -> None:
    """Display analyzer page for legal risk analysis."""
    from lawdit.web.pages import analyzer

    analyzer.show()


def show_results() -> None:
    """Display results page with visualizations."""
    from lawdit.web.pages import results

    results.show()


def show_reports() -> None:
    """Display reports page for downloading deliverables."""
    from lawdit.web.pages import reports

    reports.show()


if __name__ == "__main__":
    main()
