import pytest
from app.agents.deception_agent import adaptive_honeypot_selection, process

def test_advanced_ssh_bruteforce_honeypot():
    """Advanced SSH brute-force should deploy high-interaction SSH honeypot."""
    result = adaptive_honeypot_selection("ssh_bruteforce", "advanced")
    assert result["honeypot"] == "high_interaction_ssh_honeypot"
    assert result["status"] == "deployed"

def test_automated_port_scan_trap():
    """Automated tools doing port scans should trigger port_scan_trap."""
    result = adaptive_honeypot_selection("port_scan", "automated_tool")
    assert result["honeypot"] == "port_scan_trap"
    assert result["status"] == "deployed"

def test_beginner_gets_basic_trap():
    """Beginner attacker should get a basic_trap regardless of event type."""
    result = adaptive_honeypot_selection("ssh_bruteforce", "beginner")
    assert result["honeypot"] == "basic_trap"

def test_unknown_profile_no_deception():
    """Unknown profile should get no deception applied."""
    result = adaptive_honeypot_selection("normal", "unknown")
    assert result["honeypot"] == "none"
    assert result["status"] == "ignored"

def test_process_pipeline_attaches_honeypot():
    """The process() pipeline should attach honeypot fields to each message."""
    messages = [
        {"ip": "1.1.1.1", "event_type": "ssh_bruteforce", "attacker_profile": "advanced"},
        {"ip": "2.2.2.2", "event_type": "normal", "attacker_profile": "unknown"},
    ]
    results = process(messages)
    assert len(results) == 2
    assert results[0]["honeypot"] == "high_interaction_ssh_honeypot"
    assert results[1]["honeypot"] == "none"
