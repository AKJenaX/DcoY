# DcoY Real-Time Event System - Setup & Validation Guide

## System Architecture

```
Event Simulator → /api/ingest Endpoint → Live Event Store → Detection Pipeline → Dashboard (Auto-refresh)
     (simulator.py)     (main.py)        (live_store.py)    (detection_agent)   (Streamlit)
     Every 2 sec       Stores events      Max 100 events     Uses live data      Updates every 2 sec
```

## Component Overview

### 1. **Live Event Store** (`backend/app/utils/live_store.py`)
- In-memory buffer storing up to 100 events
- Functions:
  - `add_event(event)` - Adds new event to store
  - `get_events()` - Returns all events
  - `has_events()` - Checks if events exist
  - `clear_events()` - Clears all events
  - `get_event_count()` - Returns event count

### 2. **Ingest Endpoint** (`POST /api/ingest` in main.py)
- Receives batch of events
- Stores them in live_store
- Returns count and total_in_store
- Handles errors gracefully

### 3. **Detection Pipeline Enhancement** (detection_agent.py)
- Modified `run_pipeline_records()` to:
  - Check if live events exist
  - If yes: Process live events through ML pipeline
  - If no: Fall back to CSV pipeline
- Maintains backward compatibility

### 4. **Event Simulator** (`simulator.py`)
- Generates synthetic threat events
- Sends to `/api/ingest` every 2 seconds
- Creates batches of 3 events per batch
- Simulates various attack types and normal traffic

### 5. **Dashboard Auto-Refresh** (dashboard/app.py)
- Added cache with 2-second TTL (time-to-live)
- Sidebar shows refresh status
- Force refresh button available
- Data fetched every 2 seconds automatically

## Setup Instructions

### Prerequisites
```bash
cd backend
pip install -r requirements.txt
# Should have: fastapi, uvicorn, pandas, scikit-learn
```

### Step 1: Start Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Or with explicit localhost binding:
# uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 2: Start Dashboard (New Terminal)
```bash
cd dashboard
streamlit run app.py
```

**Expected output:**
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Step 3: Start Event Simulator (New Terminal)
```bash
python simulator.py
# Press Enter when prompted to start sending events
```

**Expected output:**
```
DcoY Event Simulator
Target: http://127.0.0.1:8000/api/ingest
Interval: 2 seconds
Events per batch: 3
Press Enter to start sending events...

[After pressing Enter]
2026-04-20 12:00:00 - INFO - ✓ Sent 3 events | Total in store: 3
2026-04-20 12:00:02 - INFO - ✓ Sent 3 events | Total in store: 6
...
```

## Validation Checklist

### ✅ Backend Health
```bash
# Check if backend is running
curl http://127.0.0.1:8000/health
# Expected: {"status":"ok","service":"DcoY"}
```

### ✅ Ingest Endpoint
```bash
# Test ingest endpoint
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"data": [{"ip":"192.168.1.1","failed_logins":5}]}'
# Expected: {"message":"Events ingested successfully","count":1,"total_in_store":1}
```

### ✅ Live Data Processing
```bash
# Get detection results (should use live data if available)
curl http://127.0.0.1:8000/detect
# Should return data from live store (not just CSV)
```

### ✅ Dashboard Display
1. Navigate to http://localhost:8501
2. Should show:
   - ✅ "System Active: Connected"
   - 📊 Overview metrics with actual counts
   - 📈 Attack Distribution chart with live data
   - 🛠️ Honeypot Response chart
   - 📋 Threat Logs table with incoming events
   - 🔄 Sidebar showing "Auto-refresh: Every 2 seconds"

### ✅ Live Updates
1. Watch dashboard - should update automatically every 2 seconds
2. Data should change as simulator sends new events
3. Anomaly count should increase with incoming attacks
4. Charts should refresh in real-time

## Testing Scenarios

### Scenario 1: Simulator → Ingest → Dashboard
**Goal:** Verify end-to-end real-time data flow

**Steps:**
1. Start backend, dashboard, simulator
2. Open dashboard in browser
3. Watch metrics update every 2 seconds
4. Verify "Total Records" increases
5. Verify "Anomalies Detected" increases
6. Check if charts show new attack types

**Expected Result:** Live updates visible in dashboard

### Scenario 2: Fallback to CSV
**Goal:** Verify system works without simulator

**Steps:**
1. Stop simulator (Ctrl+C)
2. Wait 10+ seconds
3. Refresh dashboard (F5 or force refresh button)
4. Backend should fall back to CSV pipeline

**Expected Result:** Dashboard shows CSV data, no errors

### Scenario 3: Continuous Operation
**Goal:** Verify stability over extended period

**Steps:**
1. Let simulator run for 5+ minutes
2. Monitor dashboard for errors
3. Check backend logs for warnings
4. Verify memory doesn't spike (max 100 events in buffer)

**Expected Result:** Stable operation, consistent refresh rate

## API Reference

### POST /api/ingest
Ingest live events

**Request:**
```json
{
  "data": [
    {
      "ip": "192.168.1.1",
      "failed_logins": 5,
      "port_attempts": 10,
      "request_rate": 150.5,
      "attack_type": "brute_force",
      "honeypot_type": "ssh",
      "is_anomaly": 1,
      "severity": "high"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Events ingested successfully",
  "count": 1,
  "total_in_store": 25
}
```

### GET /detect
Get anomaly detection results (uses live data if available)

**Response:**
```json
{
  "total_records": 100,
  "anomalies_detected": 15,
  "attack_summary": {
    "brute_force": 8,
    "port_scan": 5,
    "normal": 87
  },
  "response_summary": {
    "ssh": 10,
    "http": 5
  },
  "data": [...]
}
```

### GET /agents
Multi-agent pipeline (also uses live data)

### GET /explain
Explanation pipeline (also uses live data)

## Troubleshooting

### Dashboard shows "Backend not running"
1. Check backend is actually running: `curl http://127.0.0.1:8000/health`
2. Try other URLs in BACKEND_URLS
3. Check firewall allows port 8000
4. Restart backend with explicit host: `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

### Simulator won't connect
1. Verify backend is running: `netstat -ano | findstr 8000`
2. Check URL: `http://127.0.0.1:8000/api/ingest`
3. Test endpoint: `curl -X POST http://127.0.0.1:8000/api/ingest -H "Content-Type: application/json" -d '{"data":[]}'`

### Dashboard not updating
1. Check refresh interval in code (REFRESH_INTERVAL = 2)
2. Click "Force Refresh" button in sidebar
3. Check browser console for errors
4. Verify simulator is still running (should see log messages)

### Data not showing in dashboard
1. Check if live events are being stored: `curl http://127.0.0.1:8000/detect`
2. Verify event count is > 0
3. Check if CSV fallback is working (run without simulator)

## Advanced Features

### Clear Live Events
```bash
# Currently only available programmatically
# To reset: restart backend (clears in-memory store)
```

### Monitor Event Flow
Check backend logs while simulator runs:
```
INFO:     POST /api/ingest - Ingesting live events
INFO:     Ingested 3 events. Total in store: 3
INFO:     GET /detect - Running anomaly detection
INFO:     Using live events: 3 events
```

### Adjust Refresh Rate
Edit `dashboard/app.py`:
```python
REFRESH_INTERVAL = 2  # Change to desired seconds
```

Edit `simulator.py`:
```python
INTERVAL_SECONDS = 2  # Change to desired seconds
```

## Key Implementation Details

### Why use st.cache_data with TTL?
- ✅ Native to Streamlit, no extra dependencies
- ✅ Automatic rerun after TTL expires
- ✅ Fetches fresh data from backend
- ✅ Simple and reliable

### Why keep max 100 events?
- ✅ Prevents unbounded memory growth
- ✅ Keeps pipeline fast
- ✅ Sufficient for real-time analysis
- ✅ Configurable via MAX_EVENTS in live_store.py

### Why fallback to CSV?
- ✅ System still works if simulator stops
- ✅ Maintains backward compatibility
- ✅ Useful for testing/debugging
- ✅ No disruption if live data unavailable

## Summary

The DcoY system is now fully real-time capable:

1. **Ingestion**: Events flow in via `/api/ingest`
2. **Storage**: Stored in memory (max 100 events)
3. **Processing**: Detection pipeline uses live data when available
4. **Display**: Dashboard refreshes every 2 seconds
5. **Fallback**: Reverts to CSV if no live data

All existing endpoints continue to work unchanged. The system gracefully handles both live and fallback scenarios.
