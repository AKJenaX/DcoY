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
from datetime import datetime, timezone
from app.config import settings

logger = logging.getLogger(__name__)

# Circuit breaker state
CB_STATE: Dict[str, Any] = {
    "state": "CLOSED",  # CLOSED, OPEN, HALF-OPEN
    "consecutive_failures": 0,
    "last_state_change": 0.0,
    "is_healthy": None,
    "last_health_check": 0.0
}

from app.utils.cache import SimpleCache

# Prompt/response cache for successful LLM generation
RESPONSE_CACHE = SimpleCache(max_size=500, default_ttl_sec=1800.0)

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
    cached_response = RESPONSE_CACHE.get(cache_key)
    if cached_response is not None:
        logger.info(f"Response cache hit for key: {cache_key}")
        return cached_response

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
            RESPONSE_CACHE.set(cache_key, text)
            _handle_llm_success()
            return text
        else:
            logger.warning("Empty response returned from Ollama service.")
            return None
    except Exception as e:
        logger.warning(f"Ollama request failed: {type(e).__name__} (Details: {str(e)})")
        _handle_llm_failure()
        return None

def answer_question_with_llm(question: str, messages: List[Dict[str, Any]]) -> Optional[str]:
    """Helper using local Ollama model to answer operator questions using messages as context."""
    if not is_llm_available():
        return None

    # Construct context summary of top messages (limit to 10 for context window efficiency)
    summary_lines = []
    for m in messages[:10]:
        summary_lines.append(
            f"- IP: {m.get('ip')}, Event: {m.get('event_type')}, Risk Score: {m.get('risk_score')}, Honeypot: {m.get('honeypot')}, Action: {m.get('response_action_final')}"
        )
    context_str = "\n".join(summary_lines)

    prompt = (
        "You are DcoY Security Copilot, an advanced AI security assistant. "
        "Analyze the following real-time threat detection telemetry and answer the operator's query. "
        "Keep your response concise, highly professional, and structured in clean Markdown. "
        "Use bullet points, bold text, or code blocks where appropriate to present security insights.\n\n"
        "[Active Threats Telemetry]\n"
        f"{context_str}\n\n"
        f"Operator Query: {question}\n\n"
        "AI Copilot Response:"
    )

    payload = json.dumps(
        {
            "model": settings.LLM_MODEL,
            "prompt": prompt,
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
        logger.info(f"Sending Q&A prompt to Ollama model '{settings.LLM_MODEL}' at {url}...")
        with urllib.request.urlopen(req, timeout=settings.LLM_TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            
        text = (body.get("response") or "").strip()
        if text:
            _handle_llm_success()
            return text
    except Exception as e:
        logger.warning(f"Failed to query Ollama for Q&A: {str(e)}")
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

def answer_question_payload(question: str, messages: List[Dict[str, Any]]) -> Dict[str, str]:
    """Q&A payload with an explicit source contract for live vs fallback content."""
    if not messages:
        return {
            "source": "fallback",
            "content": "No events are available yet. Run detection when log data is present.",
        }

    # Try LLM Q&A first if enabled and available
    if settings.LLM_ENABLED:
        llm_response = answer_question_with_llm(question, messages)
        if llm_response:
            return {"source": "live", "content": llm_response}

    # Fallback to deterministic template
    top = max(messages, key=lambda m: float(m.get("risk_score") or 0))
    base = generate_explanation(top, allow_llm=False)
    ip = top.get("ip", "unknown IP")
    q = (question or "").strip().lower()

    if any(word in q for word in ("why", "block", "blocked", "happen", "explain")):
        content = (
            f"Regarding your question: {question.strip()!r}. "
            f"The strongest signal right now is from {ip}.\n\n{base}"
        )
    else:
        content = f"Summary for the highest-risk event ({ip}):\n\n{base}"

    return {"source": "fallback", "content": content}


def answer_question(question: str, messages: List[Dict[str, Any]]) -> str:
    """
    Q&A: uses Ollama when available, falls back to deterministic template when offline.
    """
    return answer_question_payload(question, messages)["content"]

def answer_question_detailed(question: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Q&A with rich reliability and explainability metadata return.
    """
    start_time = time.time()
    payload = answer_question_payload(question, messages)
    answer = payload["content"]
    duration = time.time() - start_time
    
    # 1. Evidence calculations
    events_analyzed = len(messages)
    unique_ips = list(set(m.get("ip") for m in messages if m.get("ip")))
    anomalies_analyzed = len([m for m in messages if float(m.get("risk_score") or 0) >= 0.35])
    highest_risk_score = max([float(m.get("risk_score") or 0) for m in messages]) if messages else 0.0
    
    mitre_techs = []
    for m in messages:
        et = m.get("event_type", "")
        if et == "ssh_bruteforce" and "T1110 - Brute Force" not in mitre_techs:
            mitre_techs.append("T1110 - Brute Force")
        elif "scan" in et.lower() and "T1046 - Network Scanning" not in mitre_techs:
            mitre_techs.append("T1046 - Network Scanning")
        elif "exploit" in et.lower() and "T1190 - Public Exploit" not in mitre_techs:
            mitre_techs.append("T1190 - Public Exploit")
            
    # 2. Confidence calculations
    gis_coverage = len([m for m in messages if m.get("latitude") is not None])
    gis_ratio = gis_coverage / max(1, events_analyzed)
    
    risk_coverage = len([m for m in messages if m.get("risk_score") is not None])
    risk_ratio = risk_coverage / max(1, events_analyzed)
    
    anomaly_coverage = len([
        m for m in messages
        if isinstance(m.get("details"), dict) and getattr(m.get("details"), "get", lambda k: None)("is_anomaly") is not None
    ])
    anomaly_ratio = anomaly_coverage / max(1, events_analyzed)
    
    conf_score = int((gis_ratio * 30) + (risk_ratio * 40) + (anomaly_ratio * 30))
    conf_score = max(15, min(98, conf_score))
    
    if conf_score >= 80:
        conf_level = "High"
    elif conf_score >= 50:
        conf_level = "Medium"
    else:
        conf_level = "Low"
        
    # 3. Context telemetry reconstruction (what was sent to LLM)
    summary_lines = []
    for m in messages[:10]:
        summary_lines.append(
            f"- IP: {m.get('ip')}, Event: {m.get('event_type')}, Risk Score: {m.get('risk_score')}, Honeypot: {m.get('honeypot')}, Action: {m.get('response_action_final')}"
        )
    context_telemetry = "\n".join(summary_lines)
    
    # Explicit response source replaces client-side guessing.
    source = payload["source"]
    fallback = source == "fallback"
    
    return {
        "source": source,
        "content": answer,
        "answer": answer,
        "metadata": {
            "model": settings.LLM_MODEL,
            "fallback": fallback,
            "response_time": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_telemetry": context_telemetry,
            "evidence": {
                "anomalies_analyzed": anomalies_analyzed,
                "events_analyzed": events_analyzed,
                "source_ips": len(unique_ips),
                "mitre_techniques": mitre_techs if mitre_techs else ["T1046 - Network Scanning"],
                "highest_risk_score": highest_risk_score
            },
            "confidence": {
                "score": conf_score,
                "level": conf_level
            }
        }
    }
