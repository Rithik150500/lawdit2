"""Configuration page for API keys and settings."""

import os
from pathlib import Path
from typing import Dict, Optional

import streamlit as st
from dotenv import load_dotenv, set_key

from lawdit.config import get_settings


def show() -> None:
    """Display configuration page."""
    st.header("⚙️ Configuration")
    st.markdown("Configure your API keys, credentials, and processing settings.")

    # Load existing .env if available
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)

    # Create tabs for different configuration sections
    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "📁 Google Drive", "⚡ Processing Settings"])

    with tab1:
        show_api_configuration(env_path)

    with tab2:
        show_google_configuration(env_path)

    with tab3:
        show_processing_configuration(env_path)

    # Validation status
    st.markdown("---")
    st.subheader("Configuration Status")

    config_status = validate_configuration()
    if config_status["valid"]:
        st.success("✅ Configuration is valid and ready to use!")
        st.session_state.config_valid = True
    else:
        st.error("❌ Configuration incomplete. Please fill in the required fields above.")
        st.session_state.config_valid = False
        for issue in config_status["issues"]:
            st.warning(f"⚠️ {issue}")


def show_api_configuration(env_path: Path) -> None:
    """Show API keys configuration section."""
    st.subheader("API Keys")
    st.markdown("Enter your API keys for OpenAI and Tavily services.")

    # OpenAI API Key
    openai_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Your OpenAI API key (starts with sk-)",
        placeholder="sk-proj-...",
    )

    # Tavily API Key
    tavily_key = st.text_input(
        "Tavily API Key",
        value=os.getenv("TAVILY_API_KEY", ""),
        type="password",
        help="Your Tavily API key for web search functionality",
        placeholder="tvly-...",
    )

    # Model configuration
    st.markdown("### Model Selection")

    col1, col2 = st.columns(2)

    with col1:
        vision_model = st.selectbox(
            "Vision Model (for page analysis)",
            options=["gpt-5-nano", "gpt-4-vision-preview", "gpt-4o"],
            index=0,
            help="Model used for analyzing document pages. gpt-5-nano is most cost-effective.",
        )

    with col2:
        analysis_model = st.selectbox(
            "Analysis Model (for legal analysis)",
            options=[
                "claude-sonnet-4-5-20250929",
                "claude-opus-4-5-20250514",
                "gpt-4o",
                "gpt-4-turbo",
            ],
            index=0,
            help="Model used for legal risk analysis. Claude Sonnet recommended.",
        )

    # Save button
    if st.button("💾 Save API Configuration", type="primary"):
        updates = {
            "OPENAI_API_KEY": openai_key,
            "TAVILY_API_KEY": tavily_key,
            "VISION_MODEL": vision_model,
            "ANALYSIS_MODEL": analysis_model,
        }
        save_to_env(env_path, updates)
        st.success("✅ API configuration saved!")
        st.rerun()


def show_google_configuration(env_path: Path) -> None:
    """Show Google Drive configuration section."""
    st.subheader("Google Drive Settings")
    st.markdown("Configure access to your Google Drive data room.")

    # Google credentials file upload
    st.markdown("### Google Cloud Credentials")
    st.markdown(
        """
        Upload your Google Cloud service account credentials JSON file.
        This file should have Google Drive API access enabled.
        """
    )

    uploaded_file = st.file_uploader(
        "Upload credentials.json",
        type=["json"],
        help="Service account JSON key file from Google Cloud Console",
    )

    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./google-credentials.json")

    if uploaded_file is not None:
        # Save uploaded file
        save_path = Path(credentials_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Credentials saved to {credentials_path}")

    # Show current credentials path
    if Path(credentials_path).exists():
        st.info(f"📄 Current credentials: {credentials_path}")
    else:
        st.warning("⚠️ No credentials file found. Please upload your credentials JSON.")

    # Credentials path input (for manual entry)
    new_creds_path = st.text_input(
        "Credentials File Path",
        value=credentials_path,
        help="Path to Google Cloud credentials JSON file",
        placeholder="./google-credentials.json",
    )

    # Google Drive Folder ID
    folder_id = st.text_input(
        "Google Drive Folder ID",
        value=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
        help="The ID of the Google Drive folder containing your legal documents",
        placeholder="1abc...xyz",
    )

    st.markdown(
        """
        💡 **How to find your Folder ID:**
        1. Open the folder in Google Drive
        2. Copy the ID from the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
        """
    )

    # Save button
    if st.button("💾 Save Google Drive Configuration", type="primary"):
        updates = {
            "GOOGLE_CREDENTIALS_PATH": new_creds_path,
            "GOOGLE_DRIVE_FOLDER_ID": folder_id,
        }
        save_to_env(env_path, updates)
        st.success("✅ Google Drive configuration saved!")
        st.rerun()


def show_processing_configuration(env_path: Path) -> None:
    """Show processing settings configuration section."""
    st.subheader("Processing Settings")
    st.markdown("Configure document processing and performance settings.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Quality Settings")

        pdf_dpi = st.slider(
            "PDF Image Quality (DPI)",
            min_value=72,
            max_value=600,
            value=int(os.getenv("PDF_DPI", "200")),
            step=50,
            help="Higher DPI = better quality but higher cost. 150-200 recommended.",
        )

        st.markdown(
            f"""
            **Estimated cost impact:**
            - 72 DPI: Lowest cost, basic quality
            - 150 DPI: Low cost, good quality ⭐
            - 200 DPI: Moderate cost, high quality ⭐ (recommended)
            - 300 DPI: High cost, very high quality
            - 600 DPI: Very high cost, maximum quality
            """
        )

    with col2:
        st.markdown("### Performance Settings")

        max_parallel = st.slider(
            "Maximum Parallel Processes",
            min_value=1,
            max_value=16,
            value=int(os.getenv("MAX_PARALLEL_PROCESSES", "4")),
            step=1,
            help="Number of documents to process simultaneously. Higher = faster but more memory.",
        )

        max_requests = st.number_input(
            "Max API Requests per Minute",
            min_value=10,
            max_value=500,
            value=int(os.getenv("OPENAI_MAX_REQUESTS_PER_MINUTE", "60")),
            step=10,
            help="Rate limit for API calls. Adjust based on your API tier.",
        )

        max_tokens = st.number_input(
            "Max Tokens per Minute",
            min_value=10000,
            max_value=500000,
            value=int(os.getenv("OPENAI_MAX_TOKENS_PER_MINUTE", "90000")),
            step=10000,
            help="Token rate limit. Adjust based on your API tier.",
        )

    # Directory settings
    st.markdown("### Directory Configuration")

    col1, col2 = st.columns(2)

    with col1:
        working_dir = st.text_input(
            "Working Directory",
            value=os.getenv("WORKING_DIR", "./data_room_processing"),
            help="Directory for intermediate processing files",
        )

    with col2:
        output_dir = st.text_input(
            "Output Directory",
            value=os.getenv("OUTPUT_DIR", "./outputs"),
            help="Directory for final reports and deliverables",
        )

    # Save button
    if st.button("💾 Save Processing Configuration", type="primary"):
        updates = {
            "PDF_DPI": str(pdf_dpi),
            "MAX_PARALLEL_PROCESSES": str(max_parallel),
            "OPENAI_MAX_REQUESTS_PER_MINUTE": str(max_requests),
            "OPENAI_MAX_TOKENS_PER_MINUTE": str(max_tokens),
            "WORKING_DIR": working_dir,
            "OUTPUT_DIR": output_dir,
        }
        save_to_env(env_path, updates)
        st.success("✅ Processing configuration saved!")
        st.rerun()


def save_to_env(env_path: Path, updates: Dict[str, str]) -> None:
    """Save configuration to .env file."""
    # Create .env if it doesn't exist
    if not env_path.exists():
        env_path.touch()

    # Update each key
    for key, value in updates.items():
        set_key(env_path, key, value)

    # Reload environment
    load_dotenv(env_path, override=True)


def validate_configuration() -> Dict[str, any]:
    """Validate current configuration."""
    issues = []

    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OpenAI API key is not configured")

    # Check Tavily API key
    if not os.getenv("TAVILY_API_KEY"):
        issues.append("Tavily API key is not configured")

    # Check Google credentials
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./google-credentials.json")
    if not Path(creds_path).exists():
        issues.append(f"Google credentials file not found at {creds_path}")

    # Check Google Drive folder ID
    if not os.getenv("GOOGLE_DRIVE_FOLDER_ID"):
        issues.append("Google Drive folder ID is not configured")

    return {"valid": len(issues) == 0, "issues": issues}
