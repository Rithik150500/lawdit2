"""
Tests for configuration management
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from lawdit.config import Settings, get_settings, reload_settings


class TestSettings:
    """Tests for the Settings class."""

    def test_settings_initialization_with_required_fields(self):
        """Test that Settings can be initialized with required fields."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
            settings = Settings()
            assert settings.openai_api_key == "test-key-123"

    def test_settings_missing_required_field(self):
        """Test that Settings raises error when required field is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):  # pydantic ValidationError
                Settings()

    def test_settings_default_values(self):
        """Test that Settings uses correct default values."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            settings = Settings()

            # Check default paths
            assert settings.working_dir == Path("./data_room_processing")
            assert settings.output_dir == Path("./outputs")

            # Check default processing values
            assert settings.pdf_dpi == 200
            assert settings.max_parallel_processes == 4

            # Check default model configuration
            assert settings.vision_model == "gpt-5-nano"
            assert settings.analysis_model == "claude-sonnet-4-5-20250929"

            # Check default rate limiting
            assert settings.openai_max_requests_per_minute == 60
            assert settings.openai_max_tokens_per_minute == 90000

    def test_settings_custom_values(self):
        """Test that Settings accepts custom values."""
        env_vars = {
            "OPENAI_API_KEY": "custom-key",
            "GOOGLE_CREDENTIALS_PATH": "/path/to/creds.json",
            "GOOGLE_DRIVE_FOLDER_ID": "folder-123",
            "WORKING_DIR": "/tmp/custom_work",
            "OUTPUT_DIR": "/tmp/custom_output",
            "PDF_DPI": "300",
            "MAX_PARALLEL_PROCESSES": "8",
            "VISION_MODEL": "gpt-4-vision",
            "ANALYSIS_MODEL": "gpt-4",
            "OPENAI_MAX_REQUESTS_PER_MINUTE": "100",
            "OPENAI_MAX_TOKENS_PER_MINUTE": "150000",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert settings.openai_api_key == "custom-key"
            assert settings.google_credentials_path == "/path/to/creds.json"
            assert settings.google_drive_folder_id == "folder-123"
            assert settings.working_dir == Path("/tmp/custom_work")
            assert settings.output_dir == Path("/tmp/custom_output")
            assert settings.pdf_dpi == 300
            assert settings.max_parallel_processes == 8
            assert settings.vision_model == "gpt-4-vision"
            assert settings.analysis_model == "gpt-4"
            assert settings.openai_max_requests_per_minute == 100
            assert settings.openai_max_tokens_per_minute == 150000

    def test_settings_pdf_dpi_validation(self):
        """Test that PDF DPI is validated within range (72-600)."""
        # Test valid DPI
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "PDF_DPI": "300"}):
            settings = Settings()
            assert settings.pdf_dpi == 300

        # Test DPI below minimum
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "PDF_DPI": "50"}):
            with pytest.raises(Exception):  # pydantic ValidationError
                Settings()

        # Test DPI above maximum
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "PDF_DPI": "700"}):
            with pytest.raises(Exception):  # pydantic ValidationError
                Settings()

    def test_settings_max_parallel_processes_validation(self):
        """Test that max_parallel_processes is validated within range (1-20)."""
        # Test valid value
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "MAX_PARALLEL_PROCESSES": "10"}):
            settings = Settings()
            assert settings.max_parallel_processes == 10

        # Test value below minimum
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "MAX_PARALLEL_PROCESSES": "0"}):
            with pytest.raises(Exception):  # pydantic ValidationError
                Settings()

        # Test value above maximum
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "MAX_PARALLEL_PROCESSES": "25"}):
            with pytest.raises(Exception):  # pydantic ValidationError
                Settings()

    def test_settings_creates_directories(self):
        """Test that Settings automatically creates working and output directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = os.path.join(tmpdir, "work")
            output_dir = os.path.join(tmpdir, "output")

            # Verify directories don't exist yet
            assert not os.path.exists(work_dir)
            assert not os.path.exists(output_dir)

            env_vars = {
                "OPENAI_API_KEY": "test-key",
                "WORKING_DIR": work_dir,
                "OUTPUT_DIR": output_dir,
            }

            with patch.dict(os.environ, env_vars):
                settings = Settings()

                # Verify directories were created
                assert os.path.exists(work_dir)
                assert os.path.exists(output_dir)
                assert os.path.isdir(work_dir)
                assert os.path.isdir(output_dir)

    def test_settings_case_insensitive(self):
        """Test that Settings accepts case-insensitive environment variables."""
        with patch.dict(os.environ, {"openai_api_key": "test-key-lower"}):
            settings = Settings()
            assert settings.openai_api_key == "test-key-lower"

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-upper"}):
            settings = Settings()
            assert settings.openai_api_key == "test-key-upper"

    def test_settings_ignores_extra_fields(self):
        """Test that Settings ignores extra environment variables."""
        env_vars = {
            "OPENAI_API_KEY": "test-key",
            "RANDOM_EXTRA_FIELD": "should-be-ignored",
            "ANOTHER_FIELD": "also-ignored",
        }

        with patch.dict(os.environ, env_vars):
            # Should not raise an error
            settings = Settings()
            assert settings.openai_api_key == "test-key"


class TestGetSettings:
    """Tests for the get_settings() function."""

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # Reset global settings
            import lawdit.config
            lawdit.config.settings = None

            settings = get_settings()
            assert isinstance(settings, Settings)
            assert settings.openai_api_key == "test-key"

    def test_get_settings_returns_cached_instance(self):
        """Test that get_settings returns the same instance on multiple calls."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # Reset global settings
            import lawdit.config
            lawdit.config.settings = None

            settings1 = get_settings()
            settings2 = get_settings()

            # Should be the same object
            assert settings1 is settings2


class TestReloadSettings:
    """Tests for the reload_settings() function."""

    def test_reload_settings_creates_new_instance(self):
        """Test that reload_settings creates a new Settings instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-1"}):
            # Reset global settings
            import lawdit.config
            lawdit.config.settings = None

            settings1 = get_settings()
            assert settings1.openai_api_key == "test-key-1"

        # Change environment and reload
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-2"}):
            settings2 = reload_settings()

            # Should be different object with new value
            assert settings2 is not settings1
            assert settings2.openai_api_key == "test-key-2"

    def test_reload_settings_updates_global_settings(self):
        """Test that reload_settings updates the global settings instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-1"}):
            # Reset global settings
            import lawdit.config
            lawdit.config.settings = None

            get_settings()

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-2"}):
            reload_settings()

            # get_settings should now return the reloaded instance
            settings = get_settings()
            assert settings.openai_api_key == "test-key-2"
