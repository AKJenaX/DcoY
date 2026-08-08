"""Shared agent pipeline execution service."""

from typing import Any, Dict, List
from app.agents import deception_agent, detection_agent, response_agent


def run_agent_pipeline(user: str = "default_user") -> List[Dict[str, Any]]:
    """Shared multi-agent run: detection → deception → response."""
    records = detection_agent.run_pipeline_records()
    for rec in records:
        rec["user"] = user
    messages = detection_agent.to_detection_messages(records)
    messages = deception_agent.process(messages)
    messages = response_agent.process(messages)
    return messages
