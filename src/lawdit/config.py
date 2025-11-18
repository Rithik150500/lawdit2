"""
Configuration Management

Centralized configuration using pydantic-settings.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Google Cloud Configuration
    google_credentials_path: Optional[str] = Field(
        None, description="Path to Google Cloud credentials JSON file"
    )
    google_drive_folder_id: Optional[str] = Field(
        None, description="Google Drive folder ID for data room"
    )

    # Directories
    working_dir: Path = Field(
        Path("./data_room_processing"),
        description="Working directory for temporary files",
    )
    output_dir: Path = Field(Path("./outputs"), description="Output directory for deliverables")

    # Processing Configuration
    pdf_dpi: int = Field(200, description="DPI for PDF to image conversion", ge=72, le=600)
    max_parallel_processes: int = Field(
        4, description="Maximum parallel processes for document analysis", ge=1, le=20
    )

    # Model Configuration
    vision_model: str = Field(
        "gpt-4-vision-preview", description="Model to use for vision tasks"
    )
    analysis_model: str = Field(
        "claude-sonnet-4-5-20250929", description="Model to use for analysis tasks"
    )

    # Rate Limiting (optional)
    openai_max_requests_per_minute: int = Field(60, description="Max OpenAI requests per minute")
    openai_max_tokens_per_minute: int = Field(90000, description="Max OpenAI tokens per minute")

    def __init__(self, **kwargs):
        """Initialize settings and create directories if they don't exist."""
        super().__init__(**kwargs)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance.

    Returns:
        Settings instance loaded from environment variables
    """
    global settings
    if settings is None:
        settings = Settings()
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment variables.

    Returns:
        Fresh Settings instance
    """
    global settings
    settings = Settings()
    return settings
