"""Indexer page for processing documents from Google Drive."""

import os
import time
from pathlib import Path
from typing import Optional

import streamlit as st

from lawdit.config import get_settings
from lawdit.indexer.data_room_indexer import DataRoomIndexer


def show() -> None:
    """Display indexer page."""
    st.header("📥 Index Documents")
    st.markdown(
        """
        Process legal documents from Google Drive to create a searchable index.
        This step analyzes all documents and prepares them for legal risk analysis.
        """
    )

    # Check configuration
    if not st.session_state.get("config_valid", False):
        st.warning(
            "⚠️ Configuration incomplete. Please configure your settings first.",
            icon="⚠️",
        )
        if st.button("Go to Configuration"):
            st.session_state.page = "⚙️ Configuration"
            st.rerun()
        return

    # Get settings
    settings = get_settings()

    # Indexing options
    st.subheader("Indexing Options")

    col1, col2 = st.columns(2)

    with col1:
        # Override folder ID if needed
        folder_id = st.text_input(
            "Google Drive Folder ID",
            value=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
            help="The folder containing your legal documents",
        )

        output_path = st.text_input(
            "Index Output File",
            value="./data_room_index.txt",
            help="Where to save the generated index",
        )

    with col2:
        working_dir = st.text_input(
            "Working Directory",
            value=os.getenv("WORKING_DIR", "./data_room_processing"),
            help="Directory for intermediate files",
        )

        # Show DPI setting
        st.info(f"📷 Image Quality: {os.getenv('PDF_DPI', '200')} DPI")
        st.caption("Change in Configuration → Processing Settings")

    # Advanced options (collapsible)
    with st.expander("Advanced Options"):
        force_reprocess = st.checkbox(
            "Force Reprocess All Documents",
            value=False,
            help="Reprocess even if already indexed (slower but ensures fresh analysis)",
        )

        skip_exports = st.checkbox(
            "Skip Google Docs/Sheets/Slides Export",
            value=False,
            help="Only process PDFs, skip exporting Google Workspace files",
        )

    # Start indexing button
    st.markdown("---")

    if not folder_id:
        st.error("❌ Please enter a Google Drive Folder ID")
        return

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        start_button = st.button(
            "🚀 Start Indexing",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get("indexing_in_progress", False),
        )

    if start_button:
        run_indexing(folder_id, output_path, working_dir, force_reprocess)

    # Show existing index files
    st.markdown("---")
    show_existing_indexes()


def run_indexing(
    folder_id: str, output_path: str, working_dir: str, force_reprocess: bool
) -> None:
    """Run the indexing process with progress tracking."""
    st.session_state.indexing_in_progress = True

    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_container = st.container()

        with metrics_container:
            col1, col2, col3 = st.columns(3)
            metric1 = col1.empty()
            metric2 = col2.empty()
            metric3 = col3.empty()

        log_container = st.expander("📝 Processing Log", expanded=True)

        # Initialize indexer
        status_text.text("🔧 Initializing indexer...")
        progress_bar.progress(5)

        with log_container:
            st.write(f"✓ Folder ID: {folder_id}")
            st.write(f"✓ Output: {output_path}")
            st.write(f"✓ Working directory: {working_dir}")

        try:
            indexer = DataRoomIndexer(
                google_credentials_path=os.getenv(
                    "GOOGLE_CREDENTIALS_PATH", "./google-credentials.json"
                ),
                openai_api_key=os.getenv("OPENAI_API_KEY", ""),
                working_dir=working_dir,
            )
            with log_container:
                st.write("✓ Indexer initialized successfully")
        except Exception as e:
            st.error(f"❌ Failed to initialize indexer: {str(e)}")
            st.session_state.indexing_in_progress = False
            return

        # Start processing
        status_text.text("📥 Downloading documents from Google Drive...")
        progress_bar.progress(15)

        with log_container:
            st.write("🔍 Scanning Google Drive folder...")

        start_time = time.time()

        try:
            # Run the indexer
            # Note: This is a simplified version - in production you'd want to
            # add callbacks to the indexer for real-time progress updates
            with log_container:
                st.write("⏳ Processing documents (this may take several minutes)...")
                st.write("🔄 Extracting pages, analyzing with AI vision...")

            progress_bar.progress(50)
            status_text.text("🤖 Analyzing documents with AI...")

            # Build the index
            index_text = indexer.build_data_room_index(
                folder_id=folder_id, output_path=output_path
            )

            progress_bar.progress(90)

            # Save the index
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(index_text)

            progress_bar.progress(100)
            elapsed_time = time.time() - start_time

            # Update metrics
            metric1.metric("Status", "✅ Complete")
            metric2.metric("Time Elapsed", f"{elapsed_time:.1f}s")
            metric3.metric("Output Size", f"{len(index_text):,} chars")

            # Success message
            status_text.text("")
            st.success(
                f"✅ Indexing complete! Index saved to {output_path}", icon="✅"
            )

            with log_container:
                st.write(f"✓ Processed successfully in {elapsed_time:.1f} seconds")
                st.write(f"✓ Index file: {output_path}")
                st.write(f"✓ Index size: {len(index_text):,} characters")

            # Update session state
            st.session_state.index_file = output_path
            st.balloons()

        except Exception as e:
            progress_bar.progress(0)
            status_text.text("")
            st.error(f"❌ Indexing failed: {str(e)}")
            with log_container:
                st.error(f"Error details: {str(e)}")

    finally:
        st.session_state.indexing_in_progress = False


def show_existing_indexes() -> None:
    """Display list of existing index files."""
    st.subheader("📚 Existing Index Files")

    # Look for index files
    index_files = []
    search_paths = [Path("."), Path("./outputs"), Path("./data_room_processing")]

    for search_path in search_paths:
        if search_path.exists():
            index_files.extend(search_path.glob("*index*.txt"))
            index_files.extend(search_path.glob("data_room*.txt"))

    if not index_files:
        st.info("No index files found. Create one using the form above.")
        return

    # Display as table
    for idx, file_path in enumerate(sorted(set(index_files), key=lambda x: x.stat().st_mtime, reverse=True)):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            st.text(f"📄 {file_path.name}")

        with col2:
            size = file_path.stat().st_size
            st.caption(f"Size: {size:,} bytes")

        with col3:
            mtime = file_path.stat().st_mtime
            st.caption(f"Modified: {time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))}")

        with col4:
            if st.button(f"Use This Index", key=f"use_index_{idx}"):
                st.session_state.index_file = str(file_path)
                st.success(f"✅ Selected: {file_path.name}")
                st.rerun()
