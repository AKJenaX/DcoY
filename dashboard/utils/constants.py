"""Configuration constants for the Streamlit dashboard."""

from pathlib import Path

# ─── Refresh Intervals ───────────────────────────────────────────────────────
REFRESH_INTERVAL = 10
EXPLAIN_REFRESH_INTERVAL = 15

# ─── Backend URLs ─────────────────────────────────────────────────────────────
BACKEND_URLS = [
    "http://127.0.0.1:8000",      # local run (first for local responsiveness)
    "http://backend:8000",        # docker service name
    "http://dcoy_backend:8000",   # optional fallback container name
]

# ─── Risk Score Thresholds ────────────────────────────────────────────────────
# Single source of truth for all severity classification across the dashboard.
LOW_RISK_THRESHOLD = 0.35
MEDIUM_RISK_THRESHOLD = 0.70
HIGH_RISK_THRESHOLD = 0.85

# ─── Session Token Persistence ────────────────────────────────────────────────
# Resolved relative to this file → always <project>/dashboard/.session_token
# regardless of the working directory at launch time.
SESSION_TOKEN_PATH = Path(__file__).resolve().parent.parent / ".session_token"

# ─── Fallback Timestamp ──────────────────────────────────────────────────────
DEFAULT_FALLBACK_TIMESTAMP = "2026-07-11T12:00:00Z"
