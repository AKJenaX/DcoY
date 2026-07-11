import pytest

def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "service" in data

def test_detect_endpoint_requires_auth(client):
    """GET /detect without token must return 401."""
    r = client.get("/detect")
    assert r.status_code == 401

def test_agents_endpoint_requires_auth(client):
    """GET /agents without token must return 401."""
    r = client.get("/agents")
    assert r.status_code == 401

def test_explain_endpoint_requires_auth(client):
    """GET /explain without token must return 401."""
    r = client.get("/explain")
    assert r.status_code == 401

def test_ask_endpoint_requires_auth(client):
    """POST /ask without token must return 401."""
    r = client.post("/ask", json={"question": "What is the highest risk event?"})
    assert r.status_code == 401

def test_report_endpoint_requires_auth(client):
    """GET /report without token must return 401."""
    r = client.get("/report")
    assert r.status_code == 401

def test_user_registration_and_login_flow(client):
    # Register user
    payload = {"username": "test_operator", "password": "secure_password"}
    r_reg = client.post("/register", json=payload)
    assert r_reg.status_code == 200
    assert r_reg.json()["message"] == "User created successfully"

    # Try duplicate registration - should fail with 400
    r_dup = client.post("/register", json=payload)
    assert r_dup.status_code == 400

    # Login with valid credentials
    r_login = client.post("/login", json=payload)
    assert r_login.status_code == 200
    login_data = r_login.json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    # Test accessing protected endpoints with JWT token
    headers = {"Authorization": f"Bearer {token}"}
    
    r_detect = client.get("/detect", headers=headers)
    assert r_detect.status_code == 200
    
    r_agents = client.get("/agents", headers=headers)
    assert r_agents.status_code == 200
    
    r_explain = client.get("/explain", headers=headers)
    assert r_explain.status_code == 200

    r_ask = client.post("/ask", json={"question": "What is the highest risk event?"}, headers=headers)
    assert r_ask.status_code == 200
    assert "answer" in r_ask.json()

    r_report = client.get("/report", headers=headers)
    assert r_report.status_code == 200
    assert r_report.content[:4] == b"%PDF"

def test_login_invalid_credentials(client):
    r = client.post("/login", json={"username": "nobody", "password": "wrong_password"})
    assert r.status_code == 401

def test_report_invalid_token(client):
    r = client.get("/report", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert r.status_code == 401

def test_api_endpoints_require_api_key(client):
    """Endpoints with /api prefix must reject calls with missing or invalid API Keys."""
    # Register and login operator
    payload = {"username": "api_user", "password": "api_password"}
    client.post("/register", json=payload)
    
    r_key = client.post("/generate-api-key", json=payload)
    assert r_key.status_code == 200
    api_key = r_key.json()["api_key"]

    # 1. Access Ingest without key
    r_ingest_no_key = client.post("/api/ingest", json={"data": []})
    assert r_ingest_no_key.status_code == 401

    # 2. Access Ingest with invalid key
    r_ingest_bad_key = client.post("/api/ingest", json={"data": []}, headers={"X-API-Key": "invalid_api_key"})
    assert r_ingest_bad_key.status_code == 401

    # 3. Access Ingest with valid key
    data = {"data": [{"ip": "1.2.3.4", "failed_logins": 5, "port_attempts": 10, "request_rate": 12.5}]}
    r_ingest_valid = client.post("/api/ingest", json=data, headers={"X-API-Key": api_key})
    assert r_ingest_valid.status_code == 200
    assert r_ingest_valid.json()["message"] == "Events ingested successfully"

    # 4. Access Capture without key
    r_capture_no_key = client.get("/api/capture")
    assert r_capture_no_key.status_code == 401

    # 5. Access Capture with valid key
    r_capture_valid = client.get("/api/capture", headers={"X-API-Key": api_key})
    assert r_capture_valid.status_code == 200
