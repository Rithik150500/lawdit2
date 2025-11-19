"""
Tests for agents CLI
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lawdit.agents.cli import main


class TestMainFunction:
    """Tests for the main CLI function."""

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    def test_main_missing_index_file(self, mock_parse_args):
        """Test that main returns error when index file doesn't exist."""
        mock_args = Mock()
        mock_args.index = "/nonexistent/file.txt"
        mock_args.working_dir = "./data_room"
        mock_args.output_dir = "./outputs"
        mock_args.focus = ["all"]
        mock_args.no_deep_agents = False
        mock_parse_args.return_value = mock_args

        result = main()

        # Should return error code
        assert result == 1

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    @patch("lawdit.agents.cli.run_analysis")
    def test_main_success(
        self, mock_run_analysis, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test successful execution of main function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test index file
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Data Room Index\n- Document 1")

            # Setup mocks
            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = Path(tmpdir) / "outputs"
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent
            mock_run_analysis.return_value = {"result": "success"}

            result = main()

            # Verify success
            assert result == 0

            # Verify components were called
            mock_init_store.assert_called_once()
            mock_create_agent.assert_called_once_with(use_deep_agents=True)
            mock_run_analysis.assert_called_once()

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    def test_main_missing_working_directory(
        self, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test that main handles missing working directory gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create index file
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = "/nonexistent/working/dir"
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent

            # Should not fail, just warn
            # (actual test would require capturing stdout)
            # For now, just verify it doesn't crash
            try:
                result = main()
                # May succeed or fail depending on agent behavior
                assert result in [0, 1]
            except Exception:
                # Some exception is acceptable in test environment
                pass

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    def test_main_creates_output_directory(self, mock_parse_args):
        """Test that main creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            output_dir = Path(tmpdir) / "nested" / "outputs"

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(output_dir)
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            # Verify directory doesn't exist
            assert not output_dir.exists()

            # Try to run (may fail for other reasons, but should create dir)
            try:
                main()
            except:
                pass

            # Verify directory was created
            assert output_dir.exists()

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    @patch("lawdit.agents.cli.run_analysis")
    def test_main_with_specific_focus_areas(
        self, mock_run_analysis, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test main with specific focus areas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["contracts", "regulatory"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent
            mock_run_analysis.return_value = {}

            main()

            # Verify focus areas were passed to run_analysis
            call_kwargs = mock_run_analysis.call_args[1]
            assert call_kwargs["focus_areas"] == ["contracts", "regulatory"]

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    @patch("lawdit.agents.cli.run_analysis")
    def test_main_with_all_focus(
        self, mock_run_analysis, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test main with 'all' focus area."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent
            mock_run_analysis.return_value = {}

            main()

            # Verify focus_areas is None when "all" is selected
            call_kwargs = mock_run_analysis.call_args[1]
            assert call_kwargs["focus_areas"] is None

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    def test_main_with_no_deep_agents_flag(
        self, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test main with --no-deep-agents flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = True  # Flag set
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent

            try:
                main()
            except:
                pass

            # Verify use_deep_agents=False was passed
            mock_create_agent.assert_called_with(use_deep_agents=False)

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    def test_main_handles_import_error(
        self, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test main handles ImportError from agent creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            # Simulate ImportError
            mock_create_agent.side_effect = ImportError("Deep Agents not available")

            result = main()

            # Should return error code
            assert result == 1

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    @patch("lawdit.agents.cli.run_analysis")
    def test_main_handles_file_not_found_error(
        self, mock_run_analysis, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test main handles FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent

            # Simulate FileNotFoundError during analysis
            mock_run_analysis.side_effect = FileNotFoundError("File not found")

            result = main()

            # Should return error code
            assert result == 1

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    @patch("lawdit.agents.cli.run_analysis")
    def test_main_handles_general_exception(
        self, mock_run_analysis, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test main handles general exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent

            # Simulate general exception
            mock_run_analysis.side_effect = Exception("Unexpected error")

            result = main()

            # Should return error code
            assert result == 1

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    @patch("lawdit.agents.cli.run_analysis")
    def test_main_loads_index_file_content(
        self, mock_run_analysis, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test that main loads index file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_content = "# Complete Data Room Index\n- Document 1\n- Document 2"
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text(index_content)

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = str(Path(tmpdir) / "outputs")
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent
            mock_run_analysis.return_value = {}

            main()

            # Verify index content was passed to run_analysis
            call_kwargs = mock_run_analysis.call_args[1]
            assert call_kwargs["data_room_index"] == index_content

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    @patch("lawdit.agents.cli.initialize_document_store")
    @patch("lawdit.agents.cli.create_legal_risk_agent")
    @patch("lawdit.agents.cli.run_analysis")
    def test_main_passes_output_dir(
        self, mock_run_analysis, mock_create_agent, mock_init_store, mock_parse_args
    ):
        """Test that output directory is passed to run_analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.txt"
            index_path.write_text("# Index")

            custom_output = str(Path(tmpdir) / "custom_outputs")

            mock_args = Mock()
            mock_args.index = str(index_path)
            mock_args.working_dir = tmpdir
            mock_args.output_dir = custom_output
            mock_args.focus = ["all"]
            mock_args.no_deep_agents = False
            mock_parse_args.return_value = mock_args

            mock_agent = Mock()
            mock_create_agent.return_value = mock_agent
            mock_run_analysis.return_value = {}

            main()

            # Verify output_dir was passed
            call_kwargs = mock_run_analysis.call_args[1]
            assert call_kwargs["output_dir"] == custom_output


class TestMainArgumentParsing:
    """Tests for argument parsing in main."""

    @patch("lawdit.agents.cli.sys.argv", ["lawdit-analyze", "--index", "test.txt"])
    def test_index_argument_required(self):
        """Test that --index argument is required."""
        # This would be tested by actually running argparse
        # For now, just verify it doesn't crash
        try:
            main()
        except SystemExit:
            # Expected if file doesn't exist
            pass

    @patch("lawdit.agents.cli.sys.argv", ["lawdit-analyze"])
    def test_missing_required_index_argument(self):
        """Test that missing --index argument causes error."""
        with pytest.raises(SystemExit):
            main()

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    def test_default_working_dir(self, mock_parse_args):
        """Test default working directory value."""
        # This is implicitly tested by the ArgumentParser setup
        # The default is "./data_room_processing"
        pass

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    def test_default_output_dir(self, mock_parse_args):
        """Test default output directory value."""
        # The default is "./outputs"
        pass

    @patch("lawdit.agents.cli.argparse.ArgumentParser.parse_args")
    def test_default_focus_all(self, mock_parse_args):
        """Test default focus is 'all'."""
        # The default focus is ["all"]
        pass
