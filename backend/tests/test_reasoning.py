import pytest
import time
from unittest.mock import patch, MagicMock
from app.agents.reasoning_agent import (
    generate_explanation,
    _try_ollama_explanation,
    _handle_llm_failure,
    _handle_llm_success,
    CB_STATE,
    RESPONSE_CACHE,
    _get_cache_key
)
from app.config import settings

@pytest.fixture(autouse=True)
def reset_cb_and_cache():
    """Reset circuit breaker and response cache states before each test case."""
    CB_STATE["state"] = "CLOSED"
    CB_STATE["consecutive_failures"] = 0
    CB_STATE["last_state_change"] = 0.0
    CB_STATE["is_healthy"] = None
    CB_STATE["last_health_check"] = 0.0
    RESPONSE_CACHE.clear()
    yield

def test_template_fallback_structure():
    msg = {
        "ip": "5.5.5.5",
        "risk_level": "high",
        "event_type": "web_attack",
        "risk_score": 0.85,
        "response_action_final": "web_honeypot",
        "strategy_reason": "Suspicious path scanning detected.",
        "details": {"is_anomaly": 1}
    }

    # Force LLM off to hit fallback template
    res = generate_explanation(msg, allow_llm=False)
    assert "**Threat Summary:**" in res
    assert "WEB ATTACK" in res
    assert "WEB_HONEYPOT" in res
    assert "HIGH (ML Outlier)" in res

def test_circuit_breaker_opens_after_threshold():
    """Calling _handle_llm_failure threshold times should open the circuit."""
    assert CB_STATE["state"] == "CLOSED"

    for i in range(settings.LLM_FAILURE_THRESHOLD):
        _handle_llm_failure()

    assert CB_STATE["state"] == "OPEN"
    assert CB_STATE["consecutive_failures"] >= settings.LLM_FAILURE_THRESHOLD

def test_circuit_breaker_resets_on_success():
    """A successful LLM call should reset the circuit breaker."""
    # Accumulate failures just below threshold
    for _ in range(settings.LLM_FAILURE_THRESHOLD - 1):
        _handle_llm_failure()
    assert CB_STATE["state"] == "CLOSED"

    _handle_llm_success()
    assert CB_STATE["consecutive_failures"] == 0
    assert CB_STATE["state"] == "CLOSED"

@patch("app.agents.reasoning_agent._check_socket_reachable")
def test_llm_unavailable_returns_none(mock_socket):
    """When socket is unreachable, _try_ollama_explanation returns None."""
    mock_socket.return_value = False

    msg = {
        "ip": "1.2.3.4",
        "risk_level": "high",
        "event_type": "ssh_bruteforce",
        "risk_score": 0.95
    }

    result = _try_ollama_explanation(msg)
    assert result is None

@patch("app.agents.reasoning_agent._check_socket_reachable")
@patch("urllib.request.urlopen")
def test_response_cache(mock_urlopen, mock_socket):
    # Mock Ollama online
    mock_socket.return_value = True

    # Mock urllib response
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"response": "Cached explanation response"}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    msg = {
        "ip": "9.9.9.9",
        "risk_level": "high",
        "event_type": "port_scan",
        "risk_score": 0.8
    }

    # First call: hits URL, populates cache
    res1 = _try_ollama_explanation(msg)
    assert res1 == "Cached explanation response"
    assert mock_urlopen.call_count == 1

    # Second call: returns cached, urlopen is not called again
    res2 = _try_ollama_explanation(msg)
    assert res2 == "Cached explanation response"
    assert mock_urlopen.call_count == 1
