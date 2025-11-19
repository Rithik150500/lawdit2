"""
Tests for legal risk analysis agent system
"""

from unittest.mock import Mock, patch

import pytest

from lawdit.agents.legal_risk_agent import (
    create_deep_agents_system,
    create_deliverable_creator_subagent,
    create_document_analyst_subagent,
    create_legal_risk_agent,
    create_simple_agent_system,
    run_analysis,
)


class TestCreateDocumentAnalystSubagent:
    """Tests for create_document_analyst_subagent function."""

    def test_create_document_analyst_returns_dict(self):
        """Test that function returns a dictionary configuration."""
        subagent = create_document_analyst_subagent()

        assert isinstance(subagent, dict)

    def test_document_analyst_has_required_fields(self):
        """Test that subagent config has all required fields."""
        subagent = create_document_analyst_subagent()

        assert "name" in subagent
        assert "description" in subagent
        assert "system_prompt" in subagent
        assert "tools" in subagent
        assert "model" in subagent

    def test_document_analyst_name(self):
        """Test that subagent has correct name."""
        subagent = create_document_analyst_subagent()

        assert subagent["name"] == "document-analyst"

    def test_document_analyst_has_tools(self):
        """Test that subagent has access to document tools."""
        subagent = create_document_analyst_subagent()

        tools = subagent["tools"]
        assert len(tools) == 4  # get_document, get_document_pages, internet_search, web_fetch

    def test_document_analyst_model(self):
        """Test that subagent uses correct model."""
        subagent = create_document_analyst_subagent()

        assert subagent["model"] == "claude-sonnet-4-5-20250929"

    def test_document_analyst_description_content(self):
        """Test that description explains subagent purpose."""
        subagent = create_document_analyst_subagent()

        description = subagent["description"]
        assert "document retrieval" in description.lower()
        assert "legal risk" in description.lower()


class TestCreateDeliverableCreatorSubagent:
    """Tests for create_deliverable_creator_subagent function."""

    def test_create_deliverable_creator_returns_dict(self):
        """Test that function returns a dictionary configuration."""
        subagent = create_deliverable_creator_subagent()

        assert isinstance(subagent, dict)

    def test_deliverable_creator_has_required_fields(self):
        """Test that subagent config has all required fields."""
        subagent = create_deliverable_creator_subagent()

        assert "name" in subagent
        assert "description" in subagent
        assert "system_prompt" in subagent
        assert "tools" in subagent
        assert "model" in subagent

    def test_deliverable_creator_name(self):
        """Test that subagent has correct name."""
        subagent = create_deliverable_creator_subagent()

        assert subagent["name"] == "deliverable-creator"

    def test_deliverable_creator_empty_tools(self):
        """Test that deliverable creator has no explicit tools (uses filesystem)."""
        subagent = create_deliverable_creator_subagent()

        tools = subagent["tools"]
        assert tools == []  # Uses filesystem tools provided by default

    def test_deliverable_creator_model(self):
        """Test that subagent uses correct model."""
        subagent = create_deliverable_creator_subagent()

        assert subagent["model"] == "claude-sonnet-4-5-20250929"

    def test_deliverable_creator_description_content(self):
        """Test that description explains subagent purpose."""
        subagent = create_deliverable_creator_subagent()

        description = subagent["description"]
        assert "deliverable" in description.lower()
        assert "word" in description.lower() or "document" in description.lower()


class TestCreateLegalRiskAgent:
    """Tests for create_legal_risk_agent function."""

    @patch("lawdit.agents.legal_risk_agent.create_deep_agents_system")
    def test_create_legal_risk_agent_with_deep_agents(self, mock_create_deep):
        """Test creating agent with Deep Agents framework."""
        mock_agent = Mock()
        mock_create_deep.return_value = mock_agent

        agent = create_legal_risk_agent(use_deep_agents=True)

        # Verify deep agents system was created
        mock_create_deep.assert_called_once()
        assert agent == mock_agent

    @patch("lawdit.agents.legal_risk_agent.create_simple_agent_system")
    def test_create_legal_risk_agent_without_deep_agents(self, mock_create_simple):
        """Test creating agent without Deep Agents framework."""
        mock_agent = Mock()
        mock_create_simple.return_value = mock_agent

        agent = create_legal_risk_agent(use_deep_agents=False)

        # Verify simple system was created
        mock_create_simple.assert_called_once()
        assert agent == mock_agent

    @patch("lawdit.agents.legal_risk_agent.create_deep_agents_system")
    def test_create_legal_risk_agent_default_uses_deep_agents(self, mock_create_deep):
        """Test that default behavior uses Deep Agents."""
        mock_create_deep.return_value = Mock()

        create_legal_risk_agent()

        # Verify deep agents was called (default behavior)
        mock_create_deep.assert_called_once()

    @patch("lawdit.agents.legal_risk_agent.create_deep_agents_system")
    def test_create_legal_risk_agent_passes_kwargs(self, mock_create_deep):
        """Test that kwargs are passed to agent creation."""
        mock_create_deep.return_value = Mock()

        create_legal_risk_agent(use_deep_agents=True, custom_param="value")

        # Verify kwargs were passed
        mock_create_deep.assert_called_once_with(custom_param="value")


class TestCreateDeepAgentsSystem:
    """Tests for create_deep_agents_system function."""

    def test_create_deep_agents_system_missing_dependency(self):
        """Test that ImportError is raised when deepagents not available."""
        with patch.dict("sys.modules", {"deepagents": None}):
            with pytest.raises(ImportError) as exc_info:
                create_deep_agents_system()

            assert "Deep Agents framework not available" in str(exc_info.value)

    @patch("lawdit.agents.legal_risk_agent.create_deep_agent")
    def test_create_deep_agents_system_success(self, mock_create_deep_agent):
        """Test successful creation of deep agents system."""
        # Mock the deepagents imports
        mock_agent = Mock()
        mock_create_deep_agent.return_value = mock_agent

        with patch.dict("sys.modules", {"deepagents": Mock(), "deepagents.backends": Mock()}):
            # Mock the imports
            with patch("lawdit.agents.legal_risk_agent.create_deep_agent", mock_create_deep_agent):
                agent = create_deep_agents_system()

                # Verify create_deep_agent was called
                mock_create_deep_agent.assert_called_once()
                assert agent == mock_agent

    @patch("lawdit.agents.legal_risk_agent.create_deep_agent")
    def test_create_deep_agents_system_default_model(self, mock_create_deep_agent):
        """Test that default model is used."""
        mock_create_deep_agent.return_value = Mock()

        with patch.dict("sys.modules", {"deepagents": Mock(), "deepagents.backends": Mock()}):
            with patch("lawdit.agents.legal_risk_agent.create_deep_agent", mock_create_deep_agent):
                create_deep_agents_system()

                # Verify default model
                call_kwargs = mock_create_deep_agent.call_args[1]
                assert call_kwargs["model"] == "claude-sonnet-4-5-20250929"

    @patch("lawdit.agents.legal_risk_agent.create_deep_agent")
    def test_create_deep_agents_system_custom_model(self, mock_create_deep_agent):
        """Test that custom model can be specified."""
        mock_create_deep_agent.return_value = Mock()

        with patch.dict("sys.modules", {"deepagents": Mock(), "deepagents.backends": Mock()}):
            with patch("lawdit.agents.legal_risk_agent.create_deep_agent", mock_create_deep_agent):
                create_deep_agents_system(model="custom-model")

                # Verify custom model
                call_kwargs = mock_create_deep_agent.call_args[1]
                assert call_kwargs["model"] == "custom-model"

    @patch("lawdit.agents.legal_risk_agent.create_deep_agent")
    def test_create_deep_agents_system_has_subagents(self, mock_create_deep_agent):
        """Test that system is configured with subagents."""
        mock_create_deep_agent.return_value = Mock()

        with patch.dict("sys.modules", {"deepagents": Mock(), "deepagents.backends": Mock()}):
            with patch("lawdit.agents.legal_risk_agent.create_deep_agent", mock_create_deep_agent):
                create_deep_agents_system()

                # Verify subagents were configured
                call_kwargs = mock_create_deep_agent.call_args[1]
                subagents = call_kwargs["subagents"]

                assert len(subagents) == 2
                assert any(sa["name"] == "document-analyst" for sa in subagents)
                assert any(sa["name"] == "deliverable-creator" for sa in subagents)

    @patch("lawdit.agents.legal_risk_agent.create_deep_agent")
    def test_create_deep_agents_system_has_tools(self, mock_create_deep_agent):
        """Test that main agent has access to tools."""
        mock_create_deep_agent.return_value = Mock()

        with patch.dict("sys.modules", {"deepagents": Mock(), "deepagents.backends": Mock()}):
            with patch("lawdit.agents.legal_risk_agent.create_deep_agent", mock_create_deep_agent):
                create_deep_agents_system()

                # Verify tools were provided
                call_kwargs = mock_create_deep_agent.call_args[1]
                tools = call_kwargs["tools"]

                assert len(tools) == 2  # internet_search, web_fetch


class TestCreateSimpleAgentSystem:
    """Tests for create_simple_agent_system function."""

    def test_create_simple_agent_system_not_implemented(self):
        """Test that simple agent system raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            create_simple_agent_system()

        assert "not yet implemented" in str(exc_info.value).lower()
        assert "Deep Agents" in str(exc_info.value)


class TestRunAnalysis:
    """Tests for run_analysis function."""

    def test_run_analysis_basic(self):
        """Test basic analysis execution."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {"result": "analysis complete"}

        result = run_analysis(
            agent=mock_agent, data_room_index="# Data Room\n- Document 1", output_dir="./outputs"
        )

        # Verify agent was invoked
        mock_agent.invoke.assert_called_once()
        assert result == {"result": "analysis complete"}

    def test_run_analysis_request_structure(self):
        """Test that analysis request is properly structured."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        run_analysis(agent=mock_agent, data_room_index="# Index", output_dir="./outputs")

        # Verify request structure
        call_args = mock_agent.invoke.call_args[0][0]
        assert "messages" in call_args
        assert len(call_args["messages"]) == 1
        assert call_args["messages"][0]["role"] == "user"

    def test_run_analysis_includes_index_content(self):
        """Test that data room index is included in request."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        index_content = "# Data Room Index\n- Document 1: Contract\n- Document 2: Agreement"

        run_analysis(agent=mock_agent, data_room_index=index_content, output_dir="./outputs")

        # Verify index content is in request
        call_args = mock_agent.invoke.call_args[0][0]
        request_content = call_args["messages"][0]["content"]
        assert index_content in request_content

    def test_run_analysis_without_focus_areas(self):
        """Test analysis without specific focus areas."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        run_analysis(agent=mock_agent, data_room_index="# Index", focus_areas=None)

        # Verify request was made without focus areas
        call_args = mock_agent.invoke.call_args[0][0]
        request_content = call_args["messages"][0]["content"]

        # Should not have "Focus particularly on" section
        assert "Focus particularly on:" not in request_content

    def test_run_analysis_with_focus_areas(self):
        """Test analysis with specific focus areas."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        focus_areas = ["contracts", "regulatory"]

        run_analysis(
            agent=mock_agent, data_room_index="# Index", focus_areas=focus_areas, output_dir="./outputs"
        )

        # Verify focus areas are in request
        call_args = mock_agent.invoke.call_args[0][0]
        request_content = call_args["messages"][0]["content"]

        assert "Focus particularly on:" in request_content
        assert "contracts" in request_content
        assert "regulatory" in request_content

    def test_run_analysis_requests_word_document(self):
        """Test that analysis requests Word document deliverable."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        run_analysis(agent=mock_agent, data_room_index="# Index")

        # Verify Word document is requested
        call_args = mock_agent.invoke.call_args[0][0]
        request_content = call_args["messages"][0]["content"]

        assert "Word document" in request_content or "Word" in request_content

    def test_run_analysis_requests_dashboard(self):
        """Test that analysis requests dashboard deliverable."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        run_analysis(agent=mock_agent, data_room_index="# Index")

        # Verify dashboard is requested
        call_args = mock_agent.invoke.call_args[0][0]
        request_content = call_args["messages"][0]["content"]

        assert "dashboard" in request_content.lower() or "artifact" in request_content.lower()

    def test_run_analysis_mentions_risk_categories(self):
        """Test that analysis request mentions key risk categories."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        run_analysis(agent=mock_agent, data_room_index="# Index")

        # Verify key categories are mentioned
        call_args = mock_agent.invoke.call_args[0][0]
        request_content = call_args["messages"][0]["content"]

        assert "contracts" in request_content.lower()
        assert "regulatory" in request_content.lower()
        assert "litigation" in request_content.lower()
        assert "governance" in request_content.lower()

    def test_run_analysis_returns_agent_result(self):
        """Test that run_analysis returns the agent's result."""
        mock_agent = Mock()
        expected_result = {"analysis": "complete", "risks": [1, 2, 3]}
        mock_agent.invoke.return_value = expected_result

        result = run_analysis(agent=mock_agent, data_room_index="# Index")

        assert result == expected_result

    def test_run_analysis_with_all_parameters(self):
        """Test analysis with all parameters specified."""
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}

        run_analysis(
            agent=mock_agent,
            data_room_index="# Complete Index",
            focus_areas=["contracts", "regulatory", "litigation"],
            output_dir="./custom_outputs",
        )

        # Verify agent was called
        mock_agent.invoke.assert_called_once()

        # Verify all parameters are reflected in request
        call_args = mock_agent.invoke.call_args[0][0]
        request_content = call_args["messages"][0]["content"]

        assert "# Complete Index" in request_content
        assert "contracts" in request_content
        assert "regulatory" in request_content
        assert "litigation" in request_content
