"""Unit and integration tests for Observability, Request Correlation, and Health Probes."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


def test_request_correlation_id_middleware(client):
    """Verify X-Request-ID header is generated and returned in response."""
    response = client.get("/")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 10

    # Custom request correlation ID propagation
    custom_id = "custom-trace-id-12345"
    resp_custom = client.get("/", headers={"X-Request-ID": custom_id})
    assert resp_custom.status_code == 200
    assert resp_custom.headers["X-Request-ID"] == custom_id


def test_liveness_probe_endpoint(client):
    """Verify /health/live returns fast liveness status."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "live"
    assert "timestamp" in data


def test_readiness_probe_endpoint(client):
    """Verify /health/ready evaluates DB and service container status."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["service_container"] == "ok"


def test_operational_metrics_endpoint(client):
    """Verify /metrics returns telemetry snapshot."""
    # Execute a request to populate metrics
    client.get("/health")
    
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "requests" in data
    assert data["requests"]["total_count"] >= 1
    assert "detection" in data
    assert "security_auth" in data
