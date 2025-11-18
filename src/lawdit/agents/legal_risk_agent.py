"""
Legal Risk Analysis Agent System

Multi-agent system for comprehensive legal due diligence using Deep Agents framework.
"""

from typing import Any, Dict, List

from lawdit.agents.prompts import (
    DELIVERABLE_CREATOR_PROMPT,
    DOCUMENT_ANALYST_PROMPT,
    MAIN_AGENT_PROMPT,
)
from lawdit.tools.document_tools import get_document, get_document_pages, internet_search, web_fetch


# ==============================================================================
# SUBAGENT CONFIGURATIONS
# ==============================================================================


def create_document_analyst_subagent() -> Dict[str, Any]:
    """Create the document analyst subagent configuration.

    This subagent specializes in detailed document retrieval and legal risk analysis.
    It has access to tools for retrieving documents and pages, and can research
    legal standards and precedents.

    Returns:
        Subagent configuration dictionary
    """
    return {
        "name": "document-analyst",
        "description": """Specialized subagent for detailed document retrieval and legal risk analysis.

Use this subagent when you need to:
- Retrieve and analyze specific documents from the data room
- Examine detailed page content and images
- Identify legal risks, compliance issues, or concerning clauses
- Research relevant legal standards or regulations
- Provide detailed findings on specific documents or document categories

This subagent has access to data room retrieval tools and can conduct
thorough document-by-document analysis without cluttering your context.""",
        "system_prompt": DOCUMENT_ANALYST_PROMPT,
        "tools": [get_document, get_document_pages, internet_search, web_fetch],
        "model": "claude-sonnet-4-5-20250929",
    }


def create_deliverable_creator_subagent() -> Dict[str, Any]:
    """Create the deliverable creator subagent configuration.

    This subagent specializes in creating polished legal deliverables from
    analysis findings. It creates Word documents and interactive web dashboards.

    Returns:
        Subagent configuration dictionary
    """
    return {
        "name": "deliverable-creator",
        "description": """Specialized subagent for creating polished legal deliverables from analysis findings.

Use this subagent when you need to transform synthesized legal risk analysis into professional deliverables including Word documents and interactive web dashboards.

This subagent specializes in document formatting, visual presentation, and creating user-friendly interfaces for complex legal information. It has access to the filesystem to read synthesis files and detailed findings, and it knows how to create properly structured Word documents and interactive React dashboards.

Delegate to this subagent after you have completed your synthesis of all findings and saved your comprehensive risk assessment to the filesystem. The subagent will handle all the technical work of creating professional deliverables.""",
        "system_prompt": DELIVERABLE_CREATOR_PROMPT,
        "tools": [],  # Uses filesystem tools which are provided by default
        "model": "claude-sonnet-4-5-20250929",
    }


# ==============================================================================
# MAIN AGENT FACTORY
# ==============================================================================


def create_legal_risk_agent(
    use_deep_agents: bool = True, **kwargs
) -> Any:
    """Create the legal risk analysis agent system.

    This function creates either a full Deep Agents-based multi-agent system
    or a simplified single-agent version depending on availability and configuration.

    Args:
        use_deep_agents: Whether to use the Deep Agents framework (default: True)
        **kwargs: Additional configuration options

    Returns:
        Configured agent system

    Raises:
        ImportError: If Deep Agents framework is not available when use_deep_agents=True
    """
    if use_deep_agents:
        return create_deep_agents_system(**kwargs)
    else:
        return create_simple_agent_system(**kwargs)


def create_deep_agents_system(**kwargs) -> Any:
    """Create the full Deep Agents-based multi-agent system.

    This creates a three-tier architecture:
    - Main agent: Coordinates analysis and synthesizes findings
    - Document analyst: Retrieves and analyzes documents
    - Deliverable creator: Generates professional reports and dashboards

    Args:
        **kwargs: Configuration options (model, backend settings, etc.)

    Returns:
        Configured Deep Agents system

    Raises:
        ImportError: If Deep Agents framework is not available
    """
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import CompositeBackend, StateBackend
    except ImportError:
        raise ImportError(
            "Deep Agents framework not available. Install it or use use_deep_agents=False"
        )

    # Configure the backend for organized storage
    def make_backend(runtime):
        return CompositeBackend(
            default=StateBackend(runtime),
            routes={
                "/analysis/": StateBackend(runtime),  # All analysis work stays in state
            },
        )

    # Create subagent configurations
    document_analyst = create_document_analyst_subagent()
    deliverable_creator = create_deliverable_creator_subagent()

    # Create the complete legal risk analysis agent
    agent = create_deep_agent(
        model=kwargs.get("model", "claude-sonnet-4-5-20250929"),
        system_prompt=MAIN_AGENT_PROMPT,
        backend=make_backend,
        subagents=[document_analyst, deliverable_creator],
        tools=[internet_search, web_fetch],  # Main agent also has these for its own research
    )

    return agent


def create_simple_agent_system(**kwargs) -> Any:
    """Create a simplified single-agent system without Deep Agents framework.

    This is a fallback implementation that provides basic functionality
    without the full multi-agent architecture.

    Args:
        **kwargs: Configuration options

    Returns:
        Configured simple agent

    Note:
        This is a placeholder. Full implementation would use LangChain or similar.
    """
    # Placeholder for simple agent implementation
    # In a real implementation, you would use LangChain or similar
    raise NotImplementedError(
        "Simple agent system not yet implemented. Please install Deep Agents framework."
    )


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def run_analysis(
    agent: Any,
    data_room_index: str,
    focus_areas: List[str] = None,
    output_dir: str = "./outputs",
) -> Dict[str, Any]:
    """Run a complete legal risk analysis using the agent system.

    Args:
        agent: The configured agent system
        data_room_index: The data room index text or path
        focus_areas: Optional list of areas to focus on (contracts, regulatory, etc.)
        output_dir: Directory for output files

    Returns:
        Dictionary with analysis results and deliverable paths
    """
    # Construct the analysis request
    focus_text = ""
    if focus_areas:
        focus_text = f"\n\nFocus particularly on: {', '.join(focus_areas)}"

    request = f"""Please conduct a comprehensive legal risk analysis of this data room.

{data_room_index}

Provide:
1. A detailed Legal Risk Analysis Report (Word document)
2. An interactive Legal Risk Analysis Dashboard (web artifact)
{focus_text}

Focus on identifying critical risks in contracts, regulatory compliance, litigation exposure, and corporate governance."""

    # Run the agent
    result = agent.invoke({"messages": [{"role": "user", "content": request}]})

    return result
