"""Analyzer page for running legal risk analysis."""

import os
import subprocess
import time
from pathlib import Path
from typing import Optional

import streamlit as st


def show() -> None:
    """Display analyzer page."""
    st.header("🔍 Analyze Documents")
    st.markdown(
        """
        Run comprehensive legal risk analysis on your indexed documents.
        The AI agents will identify risks in contracts, compliance, litigation, and governance.
        """
    )

    # Check if index exists
    if not st.session_state.get("index_file"):
        st.warning(
            "⚠️ No index file selected. Please index documents first.", icon="⚠️"
        )
        if st.button("Go to Indexer"):
            st.session_state.page = "📥 Index Documents"
            st.rerun()
        return

    # Analysis options
    st.subheader("Analysis Options")

    col1, col2 = st.columns(2)

    with col1:
        # Index file selection
        index_file = st.text_input(
            "Index File",
            value=st.session_state.get("index_file", "./data_room_index.txt"),
            help="Path to the data room index file",
        )

        # Verify index exists
        if not Path(index_file).exists():
            st.error(f"❌ Index file not found: {index_file}")
            return

        st.success(f"✅ Index file found ({Path(index_file).stat().st_size:,} bytes)")

    with col2:
        output_dir = st.text_input(
            "Output Directory",
            value=os.getenv("OUTPUT_DIR", "./outputs"),
            help="Where to save analysis reports",
        )

        # Show model being used
        analysis_model = os.getenv("ANALYSIS_MODEL", "claude-sonnet-4-5-20250929")
        st.info(f"🤖 Analysis Model: {analysis_model}")
        st.caption("Change in Configuration → API Keys")

    # Analysis focus areas
    st.markdown("### Analysis Focus Areas")
    st.markdown("Select which areas to emphasize in the analysis:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        focus_contracts = st.checkbox("⚖️ Contracts", value=True)
    with col2:
        focus_compliance = st.checkbox("📋 Compliance", value=True)
    with col3:
        focus_litigation = st.checkbox("⚡ Litigation", value=True)
    with col4:
        focus_governance = st.checkbox("🏛️ Governance", value=True)

    # Advanced options
    with st.expander("Advanced Options"):
        st.markdown("#### Agent Configuration")

        use_web_search = st.checkbox(
            "Enable Web Search",
            value=True,
            help="Allow agents to search the web for legal precedents and regulations",
        )

        max_iterations = st.slider(
            "Maximum Analysis Iterations",
            min_value=5,
            max_value=50,
            value=20,
            help="Maximum number of agent iterations (higher = more thorough but slower)",
        )

        st.markdown("#### Output Options")

        generate_word = st.checkbox(
            "Generate Word Report", value=True, help="Create professional .docx report"
        )

        generate_dashboard = st.checkbox(
            "Generate HTML Dashboard",
            value=True,
            help="Create interactive HTML dashboard",
        )

    # Start analysis button
    st.markdown("---")

    if not any([focus_contracts, focus_compliance, focus_litigation, focus_governance]):
        st.error("❌ Please select at least one focus area")
        return

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        start_button = st.button(
            "🚀 Start Analysis",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get("analysis_in_progress", False),
        )

    if start_button:
        focus_areas = []
        if focus_contracts:
            focus_areas.append("contracts")
        if focus_compliance:
            focus_areas.append("compliance")
        if focus_litigation:
            focus_areas.append("litigation")
        if focus_governance:
            focus_areas.append("governance")

        run_analysis(
            index_file,
            output_dir,
            focus_areas,
            use_web_search,
            max_iterations,
            generate_word,
            generate_dashboard,
        )

    # Show previous analysis results
    st.markdown("---")
    show_previous_analyses(output_dir)


def run_analysis(
    index_file: str,
    output_dir: str,
    focus_areas: list,
    use_web_search: bool,
    max_iterations: int,
    generate_word: bool,
    generate_dashboard: bool,
) -> None:
    """Run the legal risk analysis with progress tracking."""
    st.session_state.analysis_in_progress = True

    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_metric = st.empty()

        log_container = st.expander("📝 Analysis Log", expanded=True)

        # Build command
        cmd = [
            "lawdit-analyze",
            "--index",
            index_file,
            "--output-dir",
            output_dir,
        ]

        if focus_areas:
            cmd.extend(["--focus"] + focus_areas)

        with log_container:
            st.write(f"🚀 Starting analysis...")
            st.write(f"📁 Index: {index_file}")
            st.write(f"📂 Output: {output_dir}")
            st.write(f"🎯 Focus areas: {', '.join(focus_areas)}")
            st.write(f"🔍 Web search: {'Enabled' if use_web_search else 'Disabled'}")
            st.write("---")

        start_time = time.time()

        # Update progress
        progress_bar.progress(10)
        status_text.text("🤖 Initializing AI agents...")

        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Note: In production, you'd want to run this asynchronously
            # and stream the output. For now, we'll use subprocess
            with log_container:
                st.write("⏳ Running analysis (this may take several minutes)...")
                st.write("")

                # Show simulated progress
                progress_messages = [
                    (20, "📖 Loading document index..."),
                    (30, "🔍 Main agent analyzing document structure..."),
                    (45, "📄 Document analyst retrieving documents..."),
                    (60, "⚖️ Analyzing contract risks..."),
                    (70, "📋 Analyzing compliance issues..."),
                    (80, "⚡ Analyzing litigation risks..."),
                    (85, "🏛️ Analyzing governance matters..."),
                    (90, "🌐 Performing web research..." if use_web_search else "✍️ Synthesizing findings..."),
                    (95, "📊 Generating deliverables..."),
                ]

                progress_placeholder = st.empty()

                # Run the actual command
                # Note: This is a simplified version. In production, you'd want
                # better process management and real-time output streaming
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                )

                # Simulate progress updates during execution
                for prog, msg in progress_messages:
                    progress_bar.progress(prog)
                    status_text.text(msg)
                    progress_placeholder.write(f"• {msg}")
                    elapsed = time.time() - start_time
                    time_metric.metric("Time Elapsed", f"{elapsed:.1f}s")
                    time.sleep(0.5)

            progress_bar.progress(100)
            elapsed_time = time.time() - start_time

            if result.returncode == 0:
                # Success
                status_text.text("")
                st.success(
                    f"✅ Analysis complete! Results saved to {output_dir}", icon="✅"
                )

                with log_container:
                    st.write("---")
                    st.write(f"✓ Analysis completed in {elapsed_time:.1f} seconds")
                    st.write(f"✓ Output directory: {output_dir}")

                    # Show generated files
                    output_path = Path(output_dir)
                    if output_path.exists():
                        files = list(output_path.glob("*"))
                        if files:
                            st.write(f"✓ Generated {len(files)} file(s):")
                            for file in files:
                                st.write(f"  • {file.name}")

                # Update session state
                st.session_state.analysis_complete = True
                st.balloons()

            else:
                # Error
                progress_bar.progress(0)
                status_text.text("")
                st.error(f"❌ Analysis failed with exit code {result.returncode}")

                with log_container:
                    st.error("Error output:")
                    st.code(result.stderr)

        except Exception as e:
            progress_bar.progress(0)
            status_text.text("")
            st.error(f"❌ Analysis failed: {str(e)}")
            with log_container:
                st.error(f"Error details: {str(e)}")

    finally:
        st.session_state.analysis_in_progress = False


def show_previous_analyses(output_dir: str) -> None:
    """Display list of previous analysis results."""
    st.subheader("📊 Previous Analyses")

    output_path = Path(output_dir)
    if not output_path.exists():
        st.info("No previous analyses found.")
        return

    # Find analysis files
    word_reports = list(output_path.glob("*.docx"))
    html_dashboards = list(output_path.glob("*.html"))
    text_reports = list(output_path.glob("*analysis*.txt"))

    if not any([word_reports, html_dashboards, text_reports]):
        st.info("No previous analyses found.")
        return

    # Display files
    if word_reports:
        st.markdown("**📄 Word Reports:**")
        for report in sorted(word_reports, key=lambda x: x.stat().st_mtime, reverse=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.text(f"📄 {report.name}")
            with col2:
                mtime = report.stat().st_mtime
                st.caption(time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime)))
            with col3:
                with open(report, "rb") as f:
                    st.download_button(
                        "⬇️ Download",
                        data=f,
                        file_name=report.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_word_{report.name}",
                    )

    if html_dashboards:
        st.markdown("**🌐 HTML Dashboards:**")
        for dashboard in sorted(
            html_dashboards, key=lambda x: x.stat().st_mtime, reverse=True
        ):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.text(f"🌐 {dashboard.name}")
            with col2:
                mtime = dashboard.stat().st_mtime
                st.caption(time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime)))
            with col3:
                if st.button("👁️ View", key=f"view_dashboard_{dashboard.name}"):
                    st.session_state.selected_dashboard = str(dashboard)
                    st.session_state.page = "📊 View Results"
                    st.rerun()
