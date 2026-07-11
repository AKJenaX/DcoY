"""End-to-end automated QA validation script for DcoY system."""

import requests
import time
import sys
if sys.platform == "win32":
    try:
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

API_BASE = "http://127.0.0.1:8000"
LATENCIES = {}

def log_test(name, success, info=""):
    status = "✓" if success else "✗"
    print(f"  {status} {name:<45} | {info}")

def test_endpoint(url, method="GET", json_data=None, headers=None, expected_status=200):
    start = time.time()
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=10, verify=False)
        elif method == "POST":
            r = requests.post(url, json=json_data, headers=headers, timeout=10, verify=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        latency = int((time.time() - start) * 1000)
        success = r.status_code == expected_status
        return success, f"HTTP {r.status_code} ({latency}ms)", r.json() if "application/json" in r.headers.get("content-type", "") else r.content, latency
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        return False, f"Exception: {type(e).__name__} ({latency}ms)", str(e), latency

def run_all_tests():
    print("=" * 70)
    print(" DcoY END-TO-END QA TESTING & DIAGNOSTICS")
    print("=" * 70)

    # 1. Health
    success, info, data, lat = test_endpoint(f"{API_BASE}/health")
    log_test("GET /health (Health Check)", success, info)
    LATENCIES["/health"] = lat

    # 2. Detect
    success, info, data, lat = test_endpoint(f"{API_BASE}/detect")
    log_test("GET /detect (Anomaly Detection)", success, info)
    LATENCIES["/detect"] = lat

    # 3. Agents
    success, info, data, lat = test_endpoint(f"{API_BASE}/agents")
    log_test("GET /agents (Agent Pipeline)", success, info)
    LATENCIES["/agents"] = lat

    # 4. Explain
    success, info, data, lat = test_endpoint(f"{API_BASE}/explain")
    log_test("GET /explain (AI Explanation)", success, info)
    LATENCIES["/explain"] = lat

    # 5. Ask Q&A
    ask_payload = {"question": "Why did we block the IP?"}
    success, info, data, lat = test_endpoint(f"{API_BASE}/ask", "POST", ask_payload)
    log_test("POST /ask (Copilot Chat Q&A)", success, info)
    LATENCIES["/ask"] = lat

    # 6. Auth Registration
    # Generating unique username to prevent duplicate registration conflict
    username = f"tester_{int(time.time())}"
    auth_payload = {"username": username, "password": "secure_password_123"}
    success, info, data, lat = test_endpoint(f"{API_BASE}/register", "POST", auth_payload)
    log_test("POST /register (User Signup)", success, info)
    LATENCIES["/register"] = lat

    # 7. Auth Login
    success, info, login_data, lat = test_endpoint(f"{API_BASE}/login", "POST", auth_payload)
    token = login_data.get("access_token") if success and isinstance(login_data, dict) else None
    log_test("POST /login (User Signin & JWT Token)", success, f"{info} | Token: {'Obtained' if token else 'None'}")
    LATENCIES["/login"] = lat

    # 8. Download PDF Report (JWT Authenticated)
    pdf_headers = {"Authorization": f"Bearer {token}"} if token else {}
    success, info, pdf_bytes, lat = test_endpoint(f"{API_BASE}/report", "GET", headers=pdf_headers)
    has_pdf_header = pdf_bytes[:4] == b"%PDF" if success and isinstance(pdf_bytes, bytes) else False
    log_test("GET /report (Download PDF Document)", success and has_pdf_header, f"{info} | PDF Format Verified: {has_pdf_header}")
    LATENCIES["/report"] = lat

    # 9. Generate API Key
    success, info, key_data, lat = test_endpoint(f"{API_BASE}/generate-api-key", "POST", auth_payload)
    api_key = key_data.get("api_key") if success and isinstance(key_data, dict) else None
    log_test("POST /generate-api-key (API Key Registry)", success, f"{info} | Key: {'Obtained' if api_key else 'None'}")
    LATENCIES["/generate-api-key"] = lat

    # 10. Authenticated API Detect (API Key Header)
    api_headers = {"X-API-Key": api_key} if api_key else {}
    success, info, data, lat = test_endpoint(f"{API_BASE}/api/detect", "POST", headers=api_headers)
    log_test("POST /api/detect (API-Key Authenticated)", success, info)
    LATENCIES["/api/detect"] = lat

    # 11. Authenticated API Explain (API Key Header)
    success, info, data, lat = test_endpoint(f"{API_BASE}/api/explain", "POST", headers=api_headers)
    log_test("POST /api/explain (API-Key Authenticated)", success, info)
    LATENCIES["/api/explain"] = lat

    # 12. Invalid Payload Error Validation (Ingest)
    invalid_payload = {"data": "should_be_a_list"}
    success, info, data, lat = test_endpoint(f"{API_BASE}/api/ingest", "POST", invalid_payload, expected_status=422)
    log_test("POST /api/ingest (Error Input Type Validation)", success, f"{info} | Checked 422: {success}")
    LATENCIES["/api/ingest_error"] = lat

    print("=" * 70)
    print(" LATENCY PERFORMANCE PROFILE")
    print("=" * 70)
    for route, delay in LATENCIES.items():
        print(f"  - {route:<30}: {delay} ms")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
