"""
Legal Analysis Agents

Multi-agent system for legal risk analysis using the Deep Agents framework.
"""

from lawdit.agents.legal_risk_agent import (
    create_deliverable_creator_subagent,
    create_document_analyst_subagent,
    create_legal_risk_agent,
    run_analysis,
)
from lawdit.agents.prompts import (
    DELIVERABLE_CREATOR_PROMPT,
    DOCUMENT_ANALYST_PROMPT,
    MAIN_AGENT_PROMPT,
)

__all__ = [
    "create_legal_risk_agent",
    "create_document_analyst_subagent",
    "create_deliverable_creator_subagent",
    "run_analysis",
    "MAIN_AGENT_PROMPT",
    "DOCUMENT_ANALYST_PROMPT",
    "DELIVERABLE_CREATOR_PROMPT",
]
