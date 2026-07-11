import pytest
from app.agents.detection_agent import run_pipeline_records, compute_risk_score, classify_attacker

def test_detection_pipeline_returns_results():
    """The pipeline should return a list of dicts from CSV fallback data."""
    results = run_pipeline_records()
    assert isinstance(results, list)
    assert len(results) > 0
    # Each result should have ML enrichment keys from detect_anomalies
    first = results[0]
    assert "is_anomaly" in first
    assert "anomaly_score" in first
    assert "attack_type" in first

def test_risk_score_high_for_brute_force():
    """A record with extreme failed_logins should yield a high risk score."""
    record = {"failed_logins": 150, "port_attempts": 200, "request_rate": 800}
    score = compute_risk_score(record)
    assert score > 0.5

def test_risk_score_low_for_normal():
    """A record with normal telemetry should yield a low risk score."""
    record = {"failed_logins": 0, "port_attempts": 1, "request_rate": 5}
    score = compute_risk_score(record)
    assert score < 0.5

def test_classify_attacker_advanced():
    """High login failures + high port attempts => advanced attacker."""
    record = {"failed_logins": 100, "port_attempts": 80, "request_rate": 500}
    profile = classify_attacker(record)
    assert profile == "advanced"

def test_classify_attacker_beginner():
    """Low metrics => beginner attacker."""
    record = {"failed_logins": 2, "port_attempts": 1, "request_rate": 5}
    profile = classify_attacker(record)
    assert profile == "beginner"
