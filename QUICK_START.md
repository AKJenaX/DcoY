# Quick Start Guide - DcoY System

## Prerequisites

- Python 3.8+
- FastAPI and Streamlit installed

## Running the System

### Option 1: Quick Start (Recommended)

**Terminal 1 - Start Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 [Press CTRL+C to quit]
INFO:app.main:Starting DcoY API
INFO:app.main:CORS middleware configured to accept all origins
```

**Terminal 2 - Start Dashboard:**
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.
  URL: http://localhost:8501
```

### Option 2: Docker Compose

```bash
docker-compose up --build
```

---

## Verifying Connection

### Method 1: Automatic Verification
```bash
# From project root
python verify_setup.py
```

### Method 2: Manual Testing

1. **Test Backend Health:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   Expected: `{"status": "ok", "service": "DcoY AI Defense"}`

2. **Test Detection:**
   ```bash
   curl http://127.0.0.1:8000/detect
   ```
   Expected: JSON with detection results

3. **View Dashboard:**
   Open http://localhost:8501 in browser

---

## ✅ Success Indicators

- [ ] Backend starts without errors
- [ ] Dashboard loads without "Backend not running"
- [ ] Detection data displays in Overview section
- [ ] Attack Distribution chart shows data
- [ ] Can ask DcoY questions
- [ ] AI Explanations load properly

---

## ❌ Common Issues & Fixes

### "Connection refused on port 8000"
- Backend not running → Start it with `uvicorn` command above
- Port in use → Kill process or use different port: `--port 8001`

### "Timeout waiting for backend"
- Backend too slow → Check logs for errors
- Network issue → Verify firewall allows port 8000

### "Backend not running" in dashboard
- CORS issue → Check backend has CORS middleware
- URL mismatch → Verify API_BASE in dashboard/app.py matches backend URL

---

## Key Files Modified

- `dashboard/app.py` - Enhanced error handling and logging
- `backend/app/main.py` - Added logging and improved health check

See `BACKEND_FRONTEND_FIX.md` for detailed changes.

---

## Troubleshooting

1. **Check backend logs** - Look for errors in Terminal 1
2. **Run verify_setup.py** - Comprehensive system check
3. **Check port conflicts** - Ensure 8000 and 8501 are free
4. **Test endpoints directly** - Use curl commands above

Need help? Check `BACKEND_FRONTEND_FIX.md` for detailed documentation.
