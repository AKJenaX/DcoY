#!/usr/bin/env python3
"""Quick test to verify live data is flowing through the backend."""

import requests
import time
import sys

API_URL = "http://127.0.0.1:8000"

print("🧪 DcoY Live Data Test\n")

# Test 1: Check health
print("1️⃣  Checking backend health...")
try:
    r = requests.get(f"{API_URL}/health", timeout=5)
    print(f"   ✓ Backend running: {r.json()}")
except Exception as e:
    print(f"   ✗ Backend not reachable: {e}")
    sys.exit(1)

# Test 2: Check for live events
print("\n2️⃣  Checking for live events...")
try:
    r = requests.get(f"{API_URL}/detect", timeout=10)
    data = r.json()
    total_records = data.get("total_records", 0)
    anomalies = data.get("anomalies_detected", 0)
    print(f"   ✓ Total Records: {total_records}")
    print(f"   ✓ Anomalies: {anomalies}")
    
    if total_records > 5:
        print("   ✅ LIVE DATA DETECTED! (>5 records indicates live ingestion)")
    else:
        print("   ⚠️  Low record count - may be using CSV fallback")
        
except Exception as e:
    print(f"   ✗ Error fetching detect: {e}")
    sys.exit(1)

# Test 3: Ingest test event
print("\n3️⃣  Testing event ingestion...")
try:
    r = requests.post(
        f"{API_URL}/api/ingest",
        json={"data": [{"ip": "10.0.0.99", "failed_logins": 25, "port_attempts": 50, "request_rate": 200}]},
        timeout=5
    )
    result = r.json()
    print(f"   ✓ Event ingested: {result}")
    
    time.sleep(2)
    
    # Check if detection increased
    r2 = requests.get(f"{API_URL}/detect", timeout=10)
    data2 = r2.json()
    new_total = data2.get("total_records", 0)
    
    if new_total > total_records:
        print(f"   ✅ DATA FLOWING! Records increased: {total_records} → {new_total}")
    else:
        print(f"   ⚠️  Records didn't increase: {total_records} → {new_total}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Check agents endpoint
print("\n4️⃣  Testing agent pipeline...")
try:
    r = requests.get(f"{API_URL}/agents", timeout=15)
    data = r.json()
    print(f"   ✓ Events processed: {data.get('total_events', 0)}")
    print(f"   ✓ Risk breakdown: High={data.get('high_risk', 0)}, Med={data.get('medium_risk', 0)}, Low={data.get('low_risk', 0)}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n✅ Test complete!")
print("\nIf you see high record counts (>5), live data is flowing correctly.")
print("If you see low counts (≤5), backend may still be using CSV fallback.")
