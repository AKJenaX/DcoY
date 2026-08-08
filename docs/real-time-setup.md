# DcoY Real-Time Event System - Architecture & Setup Guide

## System Architecture

```
Attack Engine / Ingest API → In-Memory Event Store → WebSocket Broadcast → React SOC Console
  (/api/simulation/run)        (live_store.py)        (/ws/telemetry)       (useRealtimeChannel)
   Generates Telemetry        Buffers 100 Events     Push Stream (0-latency)   Renders Live Feed
```

---

## Component Overview

### 1. **Live Event Store** (`backend/app/utils/live_store.py`)
- Thread-safe ring buffer storing up to 200 live threat events.
- Functions:
  - `add_event(event)` - Adds new telemetry event and triggers WebSocket push.
  - `get_events()` - Returns buffered events.
  - `has_events()` - Checks if active events exist.
  - `clear_events()` - Resets buffer.

### 2. **Ingest Endpoint** (`POST /api/ingest`)
- API key or JWT authenticated endpoint receiving ingress event batches.
- Stores events in `live_store` and broadcasts to `/ws/telemetry` clients.

### 3. **WebSocket Router** (`backend/app/routers/websocket.py`)
- Real-time channels (`telemetry`, `geolocation`, `simulation`).
- Broadcasts event payloads directly to connected React clients with zero polling latency.

### 4. **React Realtime Hook** (`frontend/src/hooks/useRealtimeChannel.ts`)
- Manages dual-mode WebSocket connection with HTTP polling fallback.
- Pre-fetches initial event buffers on mount and handles automatic reconnection.

---

## Setup Instructions

### Step 1: Start Backend Server
```bash
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Step 2: Start React Frontend
```bash
cd frontend
npm run dev
```

### Step 3: Trigger Attack Simulation
In the React Command Center, navigate to **Attack Simulation** (`http://localhost:5173/`), select a scenario (e.g., *SSH Brute Force Attack*), and click **Launch Simulation**. Real-time threat cards will immediately stream into **`SYS.FEED // LIVE TELEMETRY`**.
