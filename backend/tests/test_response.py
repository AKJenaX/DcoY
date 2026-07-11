import pytest
from app.agents.response_agent import decide_response, process

def test_high_risk_ssh_response():
    """High-risk SSH brute-force should block IP and deploy SSH honeypot."""
    msg = {"ip": "8.8.8.8", "risk_level": "high", "event_type": "ssh_bruteforce"}
    result = decide_response(msg)
    assert result["response_action_final"] == "block_ip_and_deploy_ssh_honeypot"
    assert result["response_status_final"] == "enforced"

def test_medium_risk_web_attack_response():
    """Medium-risk web attack should delay response and deploy web honeypot."""
    msg = {"ip": "9.9.9.9", "risk_level": "medium", "event_type": "web_attack"}
    result = decide_response(msg)
    assert result["response_action_final"] == "delay_response_and_deploy_web_honeypot"
    assert result["response_status_final"] == "active_monitoring"

def test_low_risk_silent_monitoring():
    """Low-risk activity should just monitor silently."""
    msg = {"ip": "1.2.3.4", "risk_level": "low", "event_type": "normal"}
    result = decide_response(msg)
    assert result["response_action_final"] == "silent_monitoring"
    assert result["response_status_final"] == "passive"

def test_process_pipeline():
    """Process should apply decide_response to each message."""
    messages = [
        {"ip": "1.1.1.1", "risk_level": "high", "event_type": "port_scan"},
        {"ip": "2.2.2.2", "risk_level": "low", "event_type": "normal"},
    ]
    results = process(messages)
    assert len(results) == 2
    assert results[0]["response_action_final"] == "block_ip_and_deploy_generic_trap"
    assert results[1]["response_action_final"] == "silent_monitoring"
