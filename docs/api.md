# DcoY API Reference

This document maps all backend routes, request parameters, response schemas, and authentication headers.

---

## 🔑 Authentication Schemes

1. **Bearer Token (JWT)**: Used by operators on the Streamlit dashboard dashboard.
   - Header: `Authorization: Bearer <JWT_TOKEN>`
2. **API Keys**: Used by external integration clients to ingest network telemetry or pull threat alerts.
   - Header: `X-API-Key: <YOUR_API_KEY>`

---

## 📋 Endpoint Specifications

### 1. General & System Status
* **`GET /health`**
  - Description: Probes system status.
  - Response: `{"status": "ok"}`
* **`GET /`**
  - Description: Root landing page.

### 2. Threat Analysis (Session JWT Authenticated)
* **`GET /detect`**
  - Description: Fetches aggregated metrics and current raw telemetry logs.
* **`GET /explain`**
  - Description: Fetches logs with security agent explanation summaries.
* **`GET /agents`**
  - Description: Triggers full multi-agent pipeline and returns processed categories.
* **`GET /report`**
  - Description: Generates and returns a downloadable binary PDF report.
* **`POST /ask`**
  - Description: Q&A dialog query endpoint.
  - Request: `{"question": "query string"}`
  - Response: `{"answer": "copilot reply text"}`

### 3. Operator Controls & Sign-in
* **`POST /register`**
  - Description: Creates a new user profile.
  - Request: `{"username": "user", "password": "pwd"}`
* **`POST /login`**
  - Description: Authenticates credentials and returns a Bearer access token.
* **`POST /generate-api-key`**
  - Description: Generates a persistent programmatic security token.

### 4. Integrator Telemetry API (API-Key Authenticated)
* **`POST /api/ingest`**
  - Description: Programmatically logs network event records.
  - Request: `{"data": [{"ip": "...", "failed_logins": 5, "port_attempts": 10, "request_rate": 20}]}`
* **`POST /api/detect`**
  - Description: Programmatic retrieval of detections.
* **`POST /api/explain`**
  - Description: Programmatic retrieval of explanation data.
* **`POST /api/report`**
  - Description: Compiles PDF report via automated scripts.
