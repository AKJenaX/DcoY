# DcoY Developer Guide

This guide describes development workflows, diagnostic tools, and simulation setups for the DcoY Threat Defense Platform.

---

## 🛠️ Local Sandbox Setup

1. **Backend Environment**:
   ```bash
   cd backend
   python -m venv .venv
   # Activate: source .venv/bin/activate (Linux/macOS) or .\.venv\Scripts\Activate.ps1 (Windows)
   pip install -r requirements.txt
   ```

2. **Frontend React Workspace**:
   ```bash
   cd frontend
   npm install
   ```

---

## 🔍 Diagnostics & Connection Checks

Confirm system availability using the verification diagnostic script:
```bash
python scripts/verify_setup.py
```
This script validates:
* Pydantic schemas & SQLAlchemy ORM model availability.
* FastAPI backend server connectivity on port `8001`.
* Health endpoints (`/health/live`, `/health/ready`, `/metrics`).
* React frontend workspace file structure and `API_BASE` endpoints.

---

## 📈 Simulating Traffic & Purple Team Attacks

Simulate active attack scenarios (SSH brute force, credential stuffing, TCP port sweeps, lateral movement) directly through the React dashboard **Attack Simulation** workspace, or trigger via the simulation API endpoint:

```bash
curl -X POST http://127.0.0.1:8001/api/simulation/run \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"scenario_name": "SSH Brute Force Attack", "target_ip": "10.0.0.5"}'
```

* **Mechanism**: The backend simulation engine (`app/services/simulation_engine.py`) generates synthetic event telemetry, evaluates Isolation Forest anomaly detection models, triggers Honeypot honeynet traps, and broadcasts events over WebSockets to the SOC Command Center in real-time.
