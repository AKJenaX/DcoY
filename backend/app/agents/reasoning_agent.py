"""
Phase 10.5: natural-language explanations for agent decisions.

Tries a local Ollama model when available; otherwise uses a deterministic template.
No extra Python packages required for the optional LLM path (stdlib HTTP).
"""

from __future__ import annotations

import json
import logging
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Circuit breaker state
CB_STATE = {
    "state": "CLOSED",  # CLOSED, OPEN, HALF-OPEN
    "consecutive_failures": 0,
    "last_state_change": 0.0,
    "is_healthy": None,
    "last_health_check": 0.0
}

# Prompt/response cache for successful LLM generation
RESPONSE_CACHE: Dict[str, str] = {}

def _check_socket_reachable(host_url: str, timeout_ms: int = 150) -> bool:
    """Helper checking TCP socket reachability on target LLM model port."""
    try:
        parsed = urlparse(host_url)
        hostname = parsed.hostname or "127.0.0.1"
        port = parsed.port or 11434
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_ms / 1000.0)
        result = sock.connect_ex((hostname, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def _handle_llm_failure():
    """Register failure and evaluate circuit open state."""
    CB_STATE["consecutive_failures"] += 1
    CB_STATE["is_healthy"] = False
    CB_STATE["last_health_check"] = time.time()
    
    logger.warning(
        f"LLM failure registered. Failures: {CB_STATE['consecutive_failures']}/{settings.LLM_FAILURE_THRESHOLD}"
    )
    
    if CB_STATE["consecutive_failures"] >= settings.LLM_FAILURE_THRESHOLD:
        if CB_STATE["state"] != "OPEN":
            logger.error(
                f"LLM failure threshold reached. Opening circuit breaker. Cooldown retry active for {settings.LLM_RETRY_INTERVAL} seconds."
            )
            CB_STATE["state"] = "OPEN"
            CB_STATE["last_state_change"] = time.time()

def _handle_llm_success():
    """Register success and close the circuit if it was open/half-open."""
    CB_STATE["consecutive_failures"] = 0
    CB_STATE["is_healthy"] = True
    CB_STATE["last_health_check"] = time.time()
    
    if CB_STATE["state"] != "CLOSED":
        logger.info("LLM connection succeeded. Closing circuit breaker.")
        CB_STATE["state"] = "CLOSED"
        CB_STATE["last_state_change"] = time.time()

def is_llm_available() -> bool:
    """Evaluates availability state of local Ollama using cached health status and circuit breaker."""
    if not settings.LLM_ENABLED:
        return False
        
    now = time.time()
    
    # 1. Circuit Breaker state validation
    if CB_STATE["state"] == "OPEN":
        if now - CB_STATE["last_state_change"] > settings.LLM_RETRY_INTERVAL:
            logger.info("Circuit breaker cooldown retry interval elapsed. Transitioning to HALF-OPEN.")
            CB_STATE["state"] = "HALF-OPEN"
            CB_STATE["last_state_change"] = now
        else:
            return False
            
    # 2. Cached Health state check
    if CB_STATE["is_healthy"] is not None:
        if now - CB_STATE["last_health_check"] < settings.LLM_HEALTH_CHECK_INTERVAL:
            return CB_STATE["is_healthy"]
            
    # 3. Perform Fast Health Probe
    logger.info("Performing quick Ollama health check...")
    healthy = _check_socket_reachable(settings.LLM_HOST, timeout_ms=150)
    
    CB_STATE["is_healthy"] = healthy
    CB_STATE["last_health_check"] = now
    
    if healthy:
        logger.info("Ollama service verified as AVAILABLE.")
        if CB_STATE["state"] == "HALF-OPEN":
            logger.info("Ollama is available under HALF-OPEN. Resetting circuit breaker to CLOSED.")
            CB_STATE["state"] = "CLOSED"
            CB_STATE["consecutive_failures"] = 0
            CB_STATE["last_state_change"] = now
    else:
        logger.warning("Ollama health check FAILED (Ollama service unavailable).")
        _handle_llm_failure()
        
    return healthy

def _get_cache_key(message: Dict[str, Any]) -> str:
    """Build signature hash based on log details for response caching."""
    ip = message.get("ip", "unknown")
    event_type = message.get("event_type", "normal")
    risk_score = message.get("risk_score", 0.0)
    user = message.get("user", "default")
    return f"{ip}:{event_type}:{risk_score}:{user}"

def _template_explanation(message: Dict[str, Any]) -> str:
    """Deterministic structured fallback explanation when LLM is offline."""
    event_label = str(message.get("event_type", "unknown")).replace("_", " ").upper()
    risk_level = message.get("risk_level", "unknown").upper()
    risk_score = message.get("risk_score", 0.0)
    action = message.get("response_action_final", "unknown").upper()
    reason = message.get("strategy_reason", "No additional context provided.")

    # Confidence evaluation
    is_anomaly = message.get("details", {}).get("is_anomaly") == 1
    confidence = "HIGH (ML Outlier)" if is_anomaly else "MEDIUM (Heuristic Match)"

    return (
        f"**Threat Summary:** Classified as a {risk_level}-risk {event_label} activity.\n"
        f"**Risk Explanation:** The risk score of {risk_score} was calculated based on log telemetry. {reason}\n"
        f"**Recommended Action:** Execute mitigation action '{action}'.\n"
        f"**Detection Confidence:** {confidence}."
    )

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
    cache_key = _get_cache_key(message)
    if cache_key in RESPONSE_CACHE:
        logger.info(f"Response cache hit for key: {cache_key}")
        return RESPONSE_CACHE[cache_key]

    if not is_llm_available():
        logger.info("LLM is unavailable or circuit is open. Falling back to template immediately.")
        return None

    payload = json.dumps(
        {
            "model": settings.LLM_MODEL,
            "prompt": _ollama_prompt(message),
            "stream": False,
        }
    ).encode("utf-8")
    
    url = f"{settings.LLM_HOST}/api/generate"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    try:
        logger.info(f"Sending prompt to Ollama model '{settings.LLM_MODEL}' at {url}...")
        with urllib.request.urlopen(req, timeout=settings.LLM_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            
        text = (body.get("response") or "").strip()
        if text:
            RESPONSE_CACHE[cache_key] = text
            _handle_llm_success()
            return text
        else:
            logger.warning("Empty response returned from Ollama service.")
            return None
    except Exception as e:
        logger.warning(f"Ollama request failed: {type(e).__name__} (Details: {str(e)})")
        _handle_llm_failure()
        return None

def generate_explanation(message: Dict[str, Any], allow_llm: bool = True) -> str:
    """
    Produce a human-readable explanation for one agent message.

    Prefer a local Llama 3 via Ollama when available; otherwise template text.
    Set allow_llm=False for latency-sensitive bulk endpoints.
    """
    if allow_llm and settings.LLM_ENABLED:
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
            f"The strongest signal right now is from {ip}.\n\n{base}"
        )
    return f"Summary for the highest-risk event ({ip}):\n\n{base}"
