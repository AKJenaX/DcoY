"""
Phase 10.5: natural-language explanations for agent decisions.

Tries a local Ollama model when available; otherwise uses a deterministic template.
No extra Python packages required for the optional LLM path (stdlib HTTP).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

# Local Ollama defaults (user can run: ollama pull llama3)
OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3"
OLLAMA_TIMEOUT_SEC = 12.0


def _template_explanation(message: Dict[str, Any]) -> str:
    """Structured fallback when no LLM is reachable (required for demos)."""
    event_label = str(message.get("event_type", "unknown")).replace("_", " ")
    risk_level = message.get("risk_level", "unknown")
    risk_score = message.get("risk_score", 0)
    action = message.get("response_action_final", "unknown")
    reason = message.get("strategy_reason", "")

    return f"""This activity is classified as a {risk_level}-risk {event_label}.
The system assigned a risk score of {risk_score}.
Based on this, the response action taken was: {action}.
Reason: {reason}.""".strip()


def _ollama_prompt(message: Dict[str, Any]) -> str:
    """Compact prompt so small local models stay on-topic."""
    return (
        "You are a cybersecurity assistant. Write exactly 2 short sentences. "
        "Explain why this automated decision makes sense for a security operator. "
        "Do not use bullet points or markdown.\n\n"
        f"Event type: {message.get('event_type')}\n"
        f"Risk level: {message.get('risk_level')}\n"
        f"Risk score: {message.get('risk_score')}\n"
        f"Action: {message.get('response_action_final')}\n"
        f"Strategy summary: {message.get('strategy_reason')}\n"
    )


def _try_ollama_explanation(message: Dict[str, Any]) -> Optional[str]:
    """
    Call Ollama's HTTP API if a model is running locally.
    Returns None on any failure (network, wrong model, timeout).
    """
    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "prompt": _ollama_prompt(message),
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SEC) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = (body.get("response") or "").strip()
        return text if text else None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return None


def generate_explanation(message: Dict[str, Any], allow_llm: bool = True) -> str:
    """
    Produce a human-readable explanation for one agent message.

    Prefer a local Llama 3 via Ollama when available; otherwise template text.
    Set allow_llm=False for latency-sensitive bulk endpoints.
    """
    if allow_llm:
        try:
            llm_text = _try_ollama_explanation(message)
            if llm_text:
                return llm_text
        except Exception:
            pass
    return _template_explanation(message)


def answer_question(question: str, messages: List[Dict[str, Any]]) -> str:
    """
    Simple POST /ask helper: focus on the highest-risk event and explain it.

    Keeps behavior predictable without another model call by default.
    """
    if not messages:
        return "No events are available yet. Run detection when log data is present."

    top = max(messages, key=lambda m: float(m.get("risk_score") or 0))
    base = generate_explanation(top)
    ip = top.get("ip", "unknown IP")
    q = (question or "").strip().lower()

    if any(word in q for word in ("why", "block", "blocked", "happen", "explain")):
        return (
            f"Regarding your question: {question.strip()!r}. "
            f"The strongest signal right now is from {ip}. {base}"
        )
    return f"Summary for the highest-risk event ({ip}): {base}"
