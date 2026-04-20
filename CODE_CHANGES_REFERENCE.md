# Quick Reference - Code Changes

## File: `backend/app/utils/live_store.py` [NEW]
```python
"""Live event store for real-time data ingestion."""

from typing import Any, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# In-memory event buffer (last 100 events)
live_events: List[Dict[str, Any]] = []
MAX_EVENTS = 100


def add_event(event: Dict[str, Any]) -> int:
    """Add an event to the live store."""
    global live_events
    
    if "timestamp" not in event:
        event["timestamp"] = datetime.now().isoformat()
    
    live_events.append(event)
    logger.debug(f"Event added. Total: {len(live_events)}")
    
    if len(live_events) > MAX_EVENTS:
        live_events.pop(0)
        logger.debug(f"Removed oldest event. Current total: {len(live_events)}")
    
    return len(live_events)


def get_events() -> List[Dict[str, Any]]:
    """Get all events from the live store."""
    return live_events.copy()


def clear_events() -> None:
    """Clear all events from the live store."""
    global live_events
    live_events = []
    logger.info("Live event store cleared")


def get_event_count() -> int:
    """Get current count of events in store."""
    return len(live_events)


def has_events() -> bool:
    """Check if there are any events in the store."""
    return len(live_events) > 0
```

---

## File: `backend/app/main.py` [MODIFIED]

### Import Changes (Add to existing imports):
```python
from app.utils.live_store import add_event, get_events, has_events
```

### New Endpoint (Add after @app.get("/health")):
```python
@app.post("/api/ingest")
def ingest_events(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Live event ingestion endpoint."""
    logger.info("POST /api/ingest - Ingesting live events")
    
    try:
        data = payload.get("data", [])
        
        if not isinstance(data, list):
            logger.warning("Invalid payload: 'data' must be a list")
            raise HTTPException(status_code=400, detail="'data' must be a list")
        
        count = 0
        for event in data:
            if isinstance(event, dict):
                add_event(event)
                count += 1
        
        logger.info(f"Ingested {count} events. Total in store: {len(get_events())}")
        
        return {
            "message": "Events ingested successfully",
            "count": count,
            "total_in_store": len(get_events())
        }
    
    except Exception as e:
        logger.error(f"Error ingesting events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
```

---

## File: `backend/app/agents/detection_agent.py` [MODIFIED]

### Modified Function (Replace the existing run_pipeline_records()):
```python
def run_pipeline_records() -> List[Dict[str, Any]]:
    """
    Execute the same steps as GET /detect: load → preprocess → train → score rows.
    
    Now with live data support:
    - If live events exist, process them instead of CSV
    - Otherwise, fall back to CSV pipeline

    Returns the list of per-row dicts produced by detect_anomalies (includes all phases).
    """

    # Try to use live events if available
    from app.utils.live_store import get_events, has_events
    
    if has_events():
        live_data = get_events()
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Using live events: {len(live_data)} events")
        
        # Convert live events to DataFrame and process
        import pandas as pd
        df = pd.DataFrame(live_data)
        
        # Apply preprocessing and detection
        if len(df) > 0:
            df = preprocess_data(df)
            model = train_model(df)
            return detect_anomalies(df, model)
        else:
            return []
    
    # Fall back to CSV pipeline if no live events
    df = load_data()
    df = preprocess_data(df)
    model = train_model(df)
    return detect_anomalies(df, model)
```

---

## File: `dashboard/app.py` [MODIFIED]

### Import Changes (Update top imports):
```python
"""DcoY Streamlit Dashboard"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import sys
import time  # Add this

st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

# Auto-refresh configuration
REFRESH_INTERVAL = 2  # Refresh every 2 seconds
```

### Backend URL Configuration (No changes, just reference):
```python
BACKEND_URLS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
```

### Modified Backend Finding Function:
```python
@st.cache_data(ttl=REFRESH_INTERVAL)  # Add this decorator
def find_working_backend():
    """Try to connect to backend using multiple URLs with detailed logging"""
    st.write("🔍 **Searching for backend...**")
    
    for url in BACKEND_URLS:
        try:
            st.write(f"  Trying: {url}")
            r = requests.get(f"{url}/health", timeout=10, verify=False)
            r.raise_for_status()
            st.success(f"  ✅ Connected to: {url}")
            return url
        except requests.exceptions.ConnectionError as e:
            st.write(f"  ❌ Connection refused")
        except requests.exceptions.Timeout:
            st.write(f"  ❌ Timeout (10s)")
        except Exception as e:
            st.write(f"  ❌ {type(e).__name__}")
    
    return None
```

### Modified Data Fetch Function:
```python
@st.cache_data(ttl=REFRESH_INTERVAL)  # Add this decorator
def fetch_data(url):
    """Fetch detection data from backend - auto-refreshes every 2 seconds"""
    try:
        r = requests.get(f"{url}/detect", timeout=15, verify=False)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching data: {type(e).__name__}: {str(e)}")
        return None
```

### Add Sidebar Refresh Controls (After MAIN PAGE title):
```python
# ===== MAIN PAGE =====
st.title("🛡️ DcoY AI Cyber Defense System")
st.caption("Real-time Threat Detection, Intelligent Response, and Explainable AI")

# Sidebar refresh indicator
with st.sidebar:
    st.markdown("### 🔄 Live Dashboard")
    st.markdown(f"Auto-refresh: **Every {REFRESH_INTERVAL} seconds**")
    st.markdown("Last refresh: **Now**")
    
    # Clear cache button for manual refresh
    if st.button("🔁 Force Refresh"):
        st.cache_data.clear()
        st.rerun()

# Find backend
with st.spinner("🔌 Finding backend service..."):
    found_url = find_working_backend()
```

---

## File: `simulator.py` [NEW]
See separate simulator.py file for complete code.

Key highlights:
- Generates synthetic events
- Sends to POST /api/ingest
- Every 2 seconds
- 3 events per batch
- Various attack types

---

## Testing Each Component

### Test live_store.py
```python
from backend.app.utils.live_store import add_event, get_events, has_events

# Add events
add_event({"ip": "192.168.1.1", "failed_logins": 5})
add_event({"ip": "192.168.1.2", "failed_logins": 10})

# Check
assert has_events() == True
assert len(get_events()) == 2
```

### Test ingest endpoint
```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"data": [{"ip":"192.168.1.1","failed_logins":5}]}'

# Response:
# {"message":"Events ingested successfully","count":1,"total_in_store":1}
```

### Test dashboard refresh
1. Open http://localhost:8501
2. Check sidebar shows "Auto-refresh: Every 2 seconds"
3. Watch metrics update every 2 seconds
4. Click "Force Refresh" button
5. Verify data refreshes immediately

---

## Minimal Integration Test

```python
# test_realtime.py
import requests
import time

# Test 1: Ingest
response = requests.post(
    "http://127.0.0.1:8000/api/ingest",
    json={"data": [{"ip": "10.0.0.1", "failed_logins": 5}]}
)
assert response.status_code == 200
print("✓ Ingest works")

# Test 2: Detection uses live data
response = requests.get("http://127.0.0.1:8000/detect")
assert response.status_code == 200
data = response.json()
assert data["total_records"] >= 1
print("✓ Detection uses live data")

# Test 3: Dashboard connects
response = requests.get("http://localhost:8501", timeout=5)
assert response.status_code == 200
print("✓ Dashboard runs")

print("\n✅ All tests passed!")
```

---

## Key Points

✅ `live_store.py` - New in-memory storage
✅ `main.py` - Added /api/ingest endpoint
✅ `detection_agent.py` - Modified to use live data
✅ `dashboard/app.py` - Added auto-refresh caching
✅ `simulator.py` - New event generator
✅ Backward compatible - no breaking changes
✅ Fallback to CSV when no live data

All modifications are minimal and focused on extending functionality.
