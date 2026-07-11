# DcoY Developer Guide

This guide describes development workflows, diagnostic tools, and simulation setups.

---

## 🛠️ Local Sandbox Setup

1. **Virtual Environment**: Initialize virtual environments under `backend/`:
   ```bash
   cd backend
   python -m venv .venv
   # Activate: source .venv/bin/activate (Linux) or .\.venv\Scripts\Activate.ps1 (Windows)
   pip install -r requirements.txt
   ```
2. **Dashboard packages**: Install Streamlit and charting packages:
   ```bash
   cd dashboard
   pip install -r requirements.txt
   ```

---

## 🔍 Diagnostics & Connections Checks

We provide a diagnostic validation script `scripts/verify_setup.py` to confirm backend and ML availability:
```bash
python scripts/verify_setup.py
```
This script checks:
* Model schema instantiation and Pydantic models.
* Backend server connectivity on port `8000`.
* Outlier predictions using Mock datasets.

---

## 📈 Simulating Traffic Alerts

To feed active logs to the dashboard in real-time, run the mock traffic simulator script `simulator.py` from the root folder:
```bash
python simulator.py
```
* **Mechanism**: Generates unique threat records (normal, brute-force, web attacks) and POSTs them to the backend `/api/ingest` route every 2 seconds.
* **Result**: Dashboard gauge panels, Plotly express bar plots, and attack origin scatter maps will refresh dynamically.
