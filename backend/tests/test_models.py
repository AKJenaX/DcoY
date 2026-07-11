import pytest
from pydantic import ValidationError
from app.models.event import EventModel, IngestPayload, GeolocationInfo, AgentMessageModel

def test_event_model_valid():
    """Valid EventModel instantiation."""
    event = EventModel(ip="192.168.1.1", failed_logins=5, port_attempts=12, request_rate=50.5)
    assert event.ip == "192.168.1.1"
    assert event.failed_logins == 5
    assert event.port_attempts == 12
    assert event.request_rate == 50.5

def test_event_model_defaults():
    """EventModel should default numeric fields to 0.0."""
    event = EventModel(ip="10.0.0.1")
    assert event.failed_logins == 0.0
    assert event.port_attempts == 0.0
    assert event.request_rate == 0.0

def test_event_model_missing_ip():
    """EventModel requires ip field."""
    with pytest.raises(ValidationError):
        EventModel()

def test_ingest_payload_valid():
    """IngestPayload should accept a list of EventModels."""
    payload = IngestPayload(data=[
        EventModel(ip="1.2.3.4", failed_logins=1, port_attempts=2, request_rate=3)
    ])
    assert len(payload.data) == 1
    assert payload.data[0].ip == "1.2.3.4"

def test_ingest_payload_empty_list():
    """IngestPayload should accept an empty list."""
    payload = IngestPayload(data=[])
    assert len(payload.data) == 0

def test_geolocation_defaults():
    """GeolocationInfo should default to Unknown for country/city/region."""
    geo = GeolocationInfo(ip="8.8.8.8")
    assert geo.country == "Unknown"
    assert geo.city == "Unknown"
    assert geo.lat is None

def test_agent_message_model_valid():
    """AgentMessageModel should accept all required fields."""
    msg = AgentMessageModel(
        event_type="ssh_bruteforce",
        severity="high",
        ip="10.0.0.1",
        risk_score=0.95,
        risk_level="high",
        attacker_profile="advanced",
        profile_reason="High failed logins",
        details={"failed_logins": 150}
    )
    assert msg.risk_score == 0.95
    assert msg.honeypot is None  # Optional, should default to None
