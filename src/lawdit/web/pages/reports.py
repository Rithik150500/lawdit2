"""Reports page for managing and downloading analysis deliverables."""

import os
import time
from pathlib import Path
from typing import List

import streamlit as st


def show() -> None:
    """Display reports page."""
    st.header("📄 Reports")
    st.markdown(
        """
        Download and manage your legal risk analysis reports and deliverables.
        """
    )

    # Get output directory
    output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))

    if not output_dir.exists():
        st.warning("⚠️ Output directory not found. Run an analysis first.")
        if st.button("Go to Analyzer"):
            st.session_state.page = "🔍 Analyze Documents"
            st.rerun()
        return

    # Create tabs for different report types
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📄 Word Reports", "🌐 HTML Dashboards", "📝 Text Files", "📦 All Files"]
    )

    with tab1:
        show_word_reports(output_dir)

    with tab2:
        show_html_dashboards(output_dir)

    with tab3:
        show_text_files(output_dir)

    with tab4:
        show_all_files(output_dir)


def show_word_reports(output_dir: Path) -> None:
    """Display Word report files."""
    st.subheader("Word Reports")

    reports = list(output_dir.glob("*.docx"))

    if not reports:
        st.info("📭 No Word reports found. Generate one in the Analyzer.")
        return

    st.markdown(f"Found {len(reports)} Word report(s):")

    for report in sorted(reports, key=lambda x: x.stat().st_mtime, reverse=True):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.markdown(f"### 📄 {report.name}")
                size = report.stat().st_size
                st.caption(f"Size: {format_file_size(size)}")

            with col2:
                mtime = report.stat().st_mtime
                st.metric(
                    "Last Modified",
                    time.strftime("%Y-%m-%d", time.localtime(mtime)),
                )
                st.caption(time.strftime("%H:%M:%S", time.localtime(mtime)))

            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                with open(report, "rb") as f:
                    st.download_button(
                        "⬇️ Download",
                        data=f,
                        file_name=report.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_word_{report.name}",
                        use_container_width=True,
                    )

            st.markdown("---")


def show_html_dashboards(output_dir: Path) -> None:
    """Display HTML dashboard files."""
    st.subheader("HTML Dashboards")

    dashboards = list(output_dir.glob("*.html"))

    if not dashboards:
        st.info("📭 No HTML dashboards found. Generate one in the Analyzer.")
        return

    st.markdown(f"Found {len(dashboards)} dashboard(s):")

    for dashboard in sorted(dashboards, key=lambda x: x.stat().st_mtime, reverse=True):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.markdown(f"### 🌐 {dashboard.name}")
                size = dashboard.stat().st_size
                st.caption(f"Size: {format_file_size(size)}")

            with col2:
                mtime = dashboard.stat().st_mtime
                st.metric(
                    "Last Modified",
                    time.strftime("%Y-%m-%d", time.localtime(mtime)),
                )
                st.caption(time.strftime("%H:%M:%S", time.localtime(mtime)))

            with col3:
                st.markdown("<br>", unsafe_allow_html=True)

                # View button
                if st.button(
                    "👁️ View",
                    key=f"view_{dashboard.name}",
                    use_container_width=True,
                ):
                    st.session_state.selected_dashboard = str(dashboard)
                    st.session_state.page = "📊 View Results"
                    st.rerun()

                # Download button
                with open(dashboard, "rb") as f:
                    st.download_button(
                        "⬇️ Download",
                        data=f,
                        file_name=dashboard.name,
                        mime="text/html",
                        key=f"download_html_{dashboard.name}",
                        use_container_width=True,
                    )

            st.markdown("---")


def show_text_files(output_dir: Path) -> None:
    """Display text analysis files."""
    st.subheader("Text Analysis Files")

    text_files = list(output_dir.glob("*.txt"))

    if not text_files:
        st.info("📭 No text files found.")
        return

    st.markdown(f"Found {len(text_files)} text file(s):")

    for text_file in sorted(text_files, key=lambda x: x.stat().st_mtime, reverse=True):
        with st.expander(f"📝 {text_file.name}"):
            col1, col2 = st.columns([3, 2])

            with col1:
                size = text_file.stat().st_size
                mtime = text_file.stat().st_mtime
                st.caption(f"Size: {format_file_size(size)}")
                st.caption(
                    f"Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))}"
                )

            with col2:
                with open(text_file, "r", encoding="utf-8") as f:
                    content = f.read()
                st.download_button(
                    "⬇️ Download",
                    data=content,
                    file_name=text_file.name,
                    mime="text/plain",
                    key=f"download_text_{text_file.name}",
                    use_container_width=True,
                )

            # Show preview
            try:
                with open(text_file, "r", encoding="utf-8") as f:
                    content = f.read()
                preview = content[:1000] + ("..." if len(content) > 1000 else "")
                st.text_area("Preview", preview, height=200, disabled=True)
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")


def show_all_files(output_dir: Path) -> None:
    """Display all files in output directory."""
    st.subheader("All Files")

    all_files = [
        f for f in output_dir.iterdir() if f.is_file() and not f.name.startswith(".")
    ]

    if not all_files:
        st.info("📭 No files found in output directory.")
        return

    st.markdown(f"Found {len(all_files)} file(s) in `{output_dir}`:")

    # Create a table view
    file_data = []
    for file in sorted(all_files, key=lambda x: x.stat().st_mtime, reverse=True):
        file_data.append(
            {
                "Name": file.name,
                "Type": file.suffix.upper()[1:] or "FILE",
                "Size": format_file_size(file.stat().st_size),
                "Modified": time.strftime(
                    "%Y-%m-%d %H:%M", time.localtime(file.stat().st_mtime)
                ),
                "Path": str(file),
            }
        )

    # Display as dataframe
    if file_data:
        st.dataframe(
            file_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn("File Name", width="large"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Size": st.column_config.TextColumn("Size", width="small"),
                "Modified": st.column_config.TextColumn("Modified", width="medium"),
                "Path": None,  # Hide path column
            },
        )

        # Bulk download option
        st.markdown("---")
        st.markdown("### Bulk Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📦 Download All as ZIP", use_container_width=True):
                st.info("ZIP download feature coming soon!")

        with col2:
            if st.button("🗑️ Clear Old Reports", use_container_width=True):
                st.warning("This feature requires confirmation dialog (coming soon)")

        with col3:
            total_size = sum(f["Size"] for f in file_data if "KB" in f["Size"] or "MB" in f["Size"])
            st.metric("Total Files", len(file_data))


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
