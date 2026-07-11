# Quick Test Commands

## System Health Check

### 1. Backend Health
```bash
curl http://127.0.0.1:8000/health
```

**Expected Response:**
```json
{"status":"ok","service":"DcoY"}
```

---

## Real-Time Pipeline Tests

### 2. Clear Events (Restart Backend)
```bash
# Kill and restart backend to clear in-memory store
taskkill /F /IM python.exe
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 3. Ingest Single Event
```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "ip": "192.168.1.100",
        "failed_logins": 5,
        "port_attempts": 15,
        "request_rate": 100.5,
        "attack_type": "brute_force",
        "honeypot_type": "ssh",
        "is_anomaly": 1,
        "severity": "high"
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "message": "Events ingested successfully",
  "count": 1,
  "total_in_store": 1
}
```

---

### 4. Ingest Batch of Events
```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "ip": "192.168.1.101",
        "failed_logins": 3,
        "port_attempts": 20,
        "request_rate": 150.0,
        "attack_type": "port_scan",
        "honeypot_type": "http",
        "is_anomaly": 1
      },
      {
        "ip": "192.168.1.102",
        "failed_logins": 0,
        "port_attempts": 1,
        "request_rate": 10.5,
        "attack_type": "normal",
        "honeypot_type": "dns",
        "is_anomaly": 0
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "message": "Events ingested successfully",
  "count": 2,
  "total_in_store": 3
}
```

---

### 5. Get Detection Results (Uses Live Data)
```bash
curl http://127.0.0.1:8000/detect
```

**Expected Response:**
```json
{
  "total_records": 3,
  "anomalies_detected": 2,
  "attack_summary": {
    "brute_force": 1,
    "port_scan": 1,
    "normal": 1
  },
  "response_summary": {
    "ssh": 1,
    "http": 1,
    "dns": 1
  },
  "data": [
    {
      "ip": "192.168.1.100",
      "failed_logins": 5,
      "is_anomaly": 1,
      "risk_level": "high",
      ...
    },
    ...
  ]
}
```

---

### 6. Get Agent Pipeline Results (Uses Live Data)
```bash
curl http://127.0.0.1:8000/agents
```

**Expected Response:**
```json
{
  "total_events": 3,
  "high_risk": 2,
  "medium_risk": 0,
  "low_risk": 1,
  "data": [...]
}
```

---

### 7. Get Explanation (Uses Live Data)
```bash
curl http://127.0.0.1:8000/explain
```

**Expected Response:**
```json
{
  "total_events": 3,
  "data": [
    {
      "ip": "192.168.1.100",
      "risk_level": "high",
      "explanation": "This IP attempted multiple failed logins (5) with high request rate (100.5). Detected as anomaly by ML model.",
      ...
    },
    ...
  ]
}
```

---

## Fallback Testing

### 8. Test CSV Fallback (No Live Data)
```bash
# Stop simulator if running
# In backend, clear live events (restart backend)
# Now GET /detect should return CSV data

curl http://127.0.0.1:8000/detect
```

**Expected Response:**
```json
{
  "total_records": 100,
  "anomalies_detected": 5,
  "attack_summary": {...},
  "response_summary": {...},
  "data": [...]
}
```

*Note: Total records will be from CSV (usually 100), not 3 from our ingested events*

---

## Dashboard Testing

### 9. Dashboard Auto-Refresh Test
1. Open http://localhost:8501
2. Look for sidebar: "Auto-refresh: Every 2 seconds"
3. Watch "Total Records" metric
4. Ingest new events in another terminal (using curl commands above)
5. Verify metric increases every 2 seconds
6. Click "Force Refresh" button
7. Verify data updates immediately

---

### 10. Simulator Testing
```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start dashboard
cd dashboard
streamlit run app.py

# Terminal 3: Start simulator
python simulator.py
# Press Enter when prompted

# Wait 10 seconds, then:
curl http://127.0.0.1:8000/detect
```

**Expected:**
- Dashboard shows increasing metrics
- Total Records increases every 2 seconds
- Anomalies increase as simulator sends attack events
- Charts update with new data
- No errors in any terminal

---

## Event Ingestion Test Script

Save as `test_ingest.py`:
```python
#!/usr/bin/env python3
import requests
import json
import time
import random

API_URL = "http://127.0.0.1:8000/api/ingest"

def test_single_event():
    """Test single event ingestion"""
    print("\n1️⃣  Testing single event...")
    response = requests.post(API_URL, json={
        "data": [{
            "ip": "10.1.1.1",
            "failed_logins": 5,
            "port_attempts": 20,
            "request_rate": 100.0,
            "is_anomaly": 1
        }]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    print(f"   ✓ Single event ingested: {data}")

def test_batch():
    """Test batch ingestion"""
    print("\n2️⃣  Testing batch of 5 events...")
    events = []
    for i in range(5):
        events.append({
            "ip": f"10.1.1.{i}",
            "failed_logins": random.randint(0, 50),
            "port_attempts": random.randint(0, 100),
            "request_rate": random.uniform(0, 200),
            "is_anomaly": random.choice([0, 1])
        })
    
    response = requests.post(API_URL, json={"data": events})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
    print(f"   ✓ Batch ingested: {data}")

def test_detection():
    """Test detection uses live data"""
    print("\n3️⃣  Testing detection with live data...")
    response = requests.get("http://127.0.0.1:8000/detect")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] > 0
    print(f"   ✓ Detection result: {data['total_records']} records, {data['anomalies_detected']} anomalies")

def test_agents():
    """Test agent pipeline uses live data"""
    print("\n4️⃣  Testing agent pipeline...")
    response = requests.get("http://127.0.0.1:8000/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] > 0
    print(f"   ✓ Agent pipeline: {data['total_events']} events processed")

def test_explain():
    """Test explanation pipeline"""
    print("\n5️⃣  Testing explanation pipeline...")
    response = requests.get("http://127.0.0.1:8000/explain")
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] > 0
    assert "explanation" in data["data"][0]
    print(f"   ✓ Explanations generated for {data['total_events']} events")

if __name__ == "__main__":
    print("🧪 DcoY Real-Time System Tests")
    print("=" * 50)
    
    try:
        test_single_event()
        test_batch()
        test_detection()
        test_agents()
        test_explain()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to backend at {API_URL}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
```

**Run the test:**
```bash
python test_ingest.py
```

---

## Continuous Load Test

Save as `load_test.py`:
```python
#!/usr/bin/env python3
import requests
import threading
import time
import random

API_URL = "http://127.0.0.1:8000/api/ingest"

def send_events(thread_id, count):
    """Send events continuously"""
    for i in range(count):
        try:
            response = requests.post(API_URL, json={
                "data": [{
                    "ip": f"10.{thread_id}.{i}.1",
                    "failed_logins": random.randint(0, 50),
                    "port_attempts": random.randint(0, 100),
                    "request_rate": random.uniform(0, 200),
                    "is_anomaly": random.choice([0, 1])
                }]
            })
            if response.status_code == 200:
                print(f"✓ Thread {thread_id}: Event {i}")
            else:
                print(f"✗ Thread {thread_id}: Error {response.status_code}")
        except Exception as e:
            print(f"✗ Thread {thread_id}: {str(e)}")
        
        time.sleep(0.5)  # 0.5 second delay between sends

if __name__ == "__main__":
    print("📊 Load Test - Send events from multiple threads")
    threads = []
    
    # Start 3 threads, each sending 100 events
    for i in range(3):
        t = threading.Thread(target=send_events, args=(i+1, 100))
        threads.append(t)
        t.start()
    
    # Wait for all to complete
    for t in threads:
        t.join()
    
    print("✅ Load test complete!")
```

---

## Monitoring Commands

### Watch Live Events Count
```bash
# Linux/Mac
watch -n 1 'curl -s http://127.0.0.1:8000/detect | jq .total_records'

# Windows (PowerShell)
for($i=1; $i -le 100; $i++) { 
  Write-Host "$(Get-Date): $(curl -s http://127.0.0.1:8000/detect | ConvertFrom-Json | Select -ExpandProperty total_records) records"
  Start-Sleep -Seconds 1
}
```

### Monitor Simulator Output
```bash
# Check simulator is sending events
tail -f simulator_output.log
# Or just watch terminal where simulator runs
```

---

## Troubleshooting

### Test 1: Backend Running?
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"ok","service":"DcoY"}
```

### Test 2: Ingest Endpoint Accessible?
```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"data":[]}'
# Should return: {"message":"Events ingested successfully","count":0,"total_in_store":0}
```

### Test 3: Dashboard Connected?
```bash
# Open http://localhost:8501
# Should show "System Active: Connected"
```

### Test 4: Data Flowing?
```bash
# Run once
curl http://127.0.0.1:8000/detect | jq .total_records
# Should be > 0 if events ingested
```

---

## Summary

✅ Use curl commands above to test each endpoint
✅ Use test scripts for comprehensive testing
✅ Monitor output for errors
✅ Verify data flows end-to-end
✅ Check dashboard updates in real-time

All commands assume backend is running on http://127.0.0.1:8000
