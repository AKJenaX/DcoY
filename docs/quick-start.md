# Quick Start Guide - DcoY Enterprise Threat Defense Platform

## Prerequisites

- Python 3.11+
- Node.js 18+ & npm

---

## Running the System

### Option 1: Development Environment (Recommended)

**Terminal 1 — Start Backend:**
```bash
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:app.main:Starting DcoY API with Structured Observability & Correlation Tracking
INFO:app.main:CORS, Request Correlation, and Exception Middleware configured successfully
```

**Terminal 2 — Start React Frontend Dashboard:**
```bash
cd frontend
npm install
npm run dev
```

You should see:
```
  VITE v5.4.21 ready in 240 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

### Option 2: Production Containerization (Docker Compose)

```bash
cp production.env.example .env
docker-compose build --no-cache
docker-compose up -d
```

---

## Verifying Connection & Health

### Method 1: Automatic Verification Script
```bash
# From project root directory
python scripts/verify_setup.py
```

### Method 2: Manual Testing

1. **Test Backend Liveness Probe:**
   ```bash
   curl http://127.0.0.1:8001/health/live
   ```
   Expected: `{"status":"live","timestamp":"..."}`

2. **Test Backend Readiness Probe:**
   ```bash
   curl http://127.0.0.1:8001/health/ready
   ```
   Expected: `{"status":"ready","database":"connected","services":{"rule_engine":"active",...}}`

3. **Open Operator Console:**
   Open [http://localhost:5173](http://localhost:5173) in your web browser.
   - **Operator Login:** `operator` / `secure_password`
   - **Admin Login:** `adm_local` / `secure_password`

---

## Success Indicators Checklist

- [x] Backend starts cleanly on port 8001 without errors.
- [x] React frontend loads SOC Command Center without connection errors.
- [x] Live telemetry events stream in real-time.
- [x] MITRE ATT&CK Matrix updates dynamically.
- [x] Interactive Attack Path Topology Graph (`Hive Map`) renders Dijkstra nodes.
- [x] Incident cases and evidence logs register in SQLite database.

---

## Key Project Locations

- **Backend API Entrypoint:** [`backend/app/main.py`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/backend/app/main.py)
- **Frontend App Entrypoint:** [`frontend/src/App.tsx`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/frontend/src/App.tsx)
- **API Client Service:** [`frontend/src/services/api.ts`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/frontend/src/services/api.ts)
- **Production Environment Config:** [`production.env.example`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/production.env.example)
- **Master Release Manual:** [`deployment.md`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/deployment.md)
