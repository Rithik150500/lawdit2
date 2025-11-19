"""Results visualization page for viewing analysis results."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components


def show() -> None:
    """Display results visualization page."""
    st.header("📊 View Results")
    st.markdown("Interactive visualization of legal risk analysis results.")

    # Check if analysis is complete
    if not st.session_state.get("analysis_complete", False):
        st.warning("⚠️ No analysis results available yet.", icon="⚠️")
        if st.button("Go to Analyzer"):
            st.session_state.page = "🔍 Analyze Documents"
            st.rerun()
        return

    # Find available results
    output_dir = Path("./outputs")
    if not output_dir.exists():
        st.error("❌ Output directory not found")
        return

    # Look for results files
    html_dashboards = list(output_dir.glob("*.html"))
    text_analyses = list(output_dir.glob("*synthesis*.txt")) or list(
        output_dir.glob("*analysis*.txt")
    )

    if not html_dashboards and not text_analyses:
        st.warning("⚠️ No results found in output directory")
        return

    # Create tabs for different views
    tabs = []
    if html_dashboards:
        tabs.append("🌐 Dashboard")
    if text_analyses:
        tabs.append("📝 Text Analysis")
    tabs.append("📊 Statistics")

    selected_tabs = st.tabs(tabs)
    tab_idx = 0

    # Dashboard tab
    if html_dashboards:
        with selected_tabs[tab_idx]:
            show_dashboard_view(html_dashboards)
        tab_idx += 1

    # Text analysis tab
    if text_analyses:
        with selected_tabs[tab_idx]:
            show_text_analysis(text_analyses)
        tab_idx += 1

    # Statistics tab
    with selected_tabs[tab_idx]:
        show_statistics(text_analyses)


def show_dashboard_view(dashboards: List[Path]) -> None:
    """Display interactive HTML dashboard."""
    st.subheader("Interactive Risk Dashboard")

    # Select dashboard if multiple exist
    if len(dashboards) > 1:
        dashboard_names = [d.name for d in dashboards]
        selected_name = st.selectbox("Select Dashboard", dashboard_names)
        selected_dashboard = next(d for d in dashboards if d.name == selected_name)
    else:
        selected_dashboard = dashboards[0]

    st.caption(f"Viewing: {selected_dashboard.name}")

    # Read and display HTML dashboard
    try:
        with open(selected_dashboard, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Display in iframe
        components.html(html_content, height=800, scrolling=True)

        # Download button
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            with open(selected_dashboard, "rb") as f:
                st.download_button(
                    "⬇️ Download Dashboard",
                    data=f,
                    file_name=selected_dashboard.name,
                    mime="text/html",
                    use_container_width=True,
                )

    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")


def show_text_analysis(analyses: List[Path]) -> None:
    """Display text-based analysis results."""
    st.subheader("Analysis Report")

    # Select analysis if multiple exist
    if len(analyses) > 1:
        analysis_names = [a.name for a in analyses]
        selected_name = st.selectbox("Select Analysis", analysis_names)
        selected_analysis = next(a for a in analyses if a.name == selected_name)
    else:
        selected_analysis = analyses[0]

    st.caption(f"Viewing: {selected_analysis.name}")

    # Read and display analysis
    try:
        with open(selected_analysis, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to parse and format the content
        formatted_content = format_analysis_text(content)
        st.markdown(formatted_content)

        # Download button
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            st.download_button(
                "⬇️ Download Analysis",
                data=content,
                file_name=selected_analysis.name,
                mime="text/plain",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"❌ Error loading analysis: {str(e)}")


def show_statistics(analyses: List[Path]) -> None:
    """Display statistical summary of analysis results."""
    st.subheader("Analysis Statistics")

    if not analyses:
        st.info("No analysis data available for statistics")
        return

    # Read analysis content
    try:
        selected_analysis = analyses[0]
        with open(selected_analysis, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract statistics from content
        stats = extract_statistics(content)

        # Display metrics
        if stats:
            st.markdown("### Risk Overview")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Critical Risks",
                    stats.get("critical", 0),
                    delta=None,
                    delta_color="inverse",
                )

            with col2:
                st.metric(
                    "High Risks", stats.get("high", 0), delta=None, delta_color="inverse"
                )

            with col3:
                st.metric(
                    "Medium Risks",
                    stats.get("medium", 0),
                    delta=None,
                    delta_color="normal",
                )

            with col4:
                st.metric(
                    "Low Risks", stats.get("low", 0), delta=None, delta_color="normal"
                )

            # Category breakdown
            st.markdown("### Risk Categories")

            categories = stats.get("categories", {})
            if categories:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("⚖️ Contracts", categories.get("contracts", 0))

                with col2:
                    st.metric("📋 Compliance", categories.get("compliance", 0))

                with col3:
                    st.metric("⚡ Litigation", categories.get("litigation", 0))

                with col4:
                    st.metric("🏛️ Governance", categories.get("governance", 0))

            # Document statistics
            st.markdown("### Document Statistics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Documents Analyzed", stats.get("total_documents", "N/A"))

            with col2:
                st.metric("Total Issues Found", stats.get("total_issues", "N/A"))

            with col3:
                st.metric(
                    "Average Risk Score",
                    f"{stats.get('avg_risk_score', 0):.1f}/10"
                    if stats.get("avg_risk_score")
                    else "N/A",
                )

        else:
            st.info("No statistical data could be extracted from the analysis")

    except Exception as e:
        st.error(f"❌ Error generating statistics: {str(e)}")


def format_analysis_text(content: str) -> str:
    """Format analysis text for better display."""
    # Convert headers
    content = re.sub(r"^# (.*?)$", r"## \1", content, flags=re.MULTILINE)
    content = re.sub(r"^## (.*?)$", r"### \1", content, flags=re.MULTILINE)

    # Highlight risk levels
    content = re.sub(
        r"\b(CRITICAL|Critical)\b", r"**🔴 \1**", content, flags=re.IGNORECASE
    )
    content = re.sub(r"\b(HIGH|High)\b", r"**🟠 \1**", content, flags=re.IGNORECASE)
    content = re.sub(r"\b(MEDIUM|Medium)\b", r"**🟡 \1**", content, flags=re.IGNORECASE)
    content = re.sub(r"\b(LOW|Low)\b", r"**🟢 \1**", content, flags=re.IGNORECASE)

    return content


def extract_statistics(content: str) -> Dict:
    """Extract statistics from analysis content."""
    stats = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "categories": {"contracts": 0, "compliance": 0, "litigation": 0, "governance": 0},
        "total_documents": 0,
        "total_issues": 0,
        "avg_risk_score": 0.0,
    }

    # Count risk levels (case insensitive)
    stats["critical"] = len(re.findall(r"\bcritical\b", content, re.IGNORECASE))
    stats["high"] = len(re.findall(r"\bhigh\b", content, re.IGNORECASE))
    stats["medium"] = len(re.findall(r"\bmedium\b", content, re.IGNORECASE))
    stats["low"] = len(re.findall(r"\blow\b", content, re.IGNORECASE))

    # Count category mentions
    stats["categories"]["contracts"] = len(
        re.findall(r"\bcontract\b", content, re.IGNORECASE)
    )
    stats["categories"]["compliance"] = len(
        re.findall(r"\bcompliance\b", content, re.IGNORECASE)
    )
    stats["categories"]["litigation"] = len(
        re.findall(r"\blitigation\b", content, re.IGNORECASE)
    )
    stats["categories"]["governance"] = len(
        re.findall(r"\bgovernance\b", content, re.IGNORECASE)
    )

    # Calculate totals
    stats["total_issues"] = sum([stats["critical"], stats["high"], stats["medium"], stats["low"]])

    # Try to extract document count
    doc_match = re.search(r"(\d+)\s+documents?", content, re.IGNORECASE)
    if doc_match:
        stats["total_documents"] = int(doc_match.group(1))

    # Calculate average risk score (weighted)
    if stats["total_issues"] > 0:
        weighted_score = (
            stats["critical"] * 10
            + stats["high"] * 7
            + stats["medium"] * 4
            + stats["low"] * 2
        ) / stats["total_issues"]
        stats["avg_risk_score"] = weighted_score

    return stats
