"""Configuration constants for the Streamlit dashboard."""

REFRESH_INTERVAL = 10
EXPLAIN_REFRESH_INTERVAL = 15

BACKEND_URLS = [
    "http://127.0.0.1:8000",      # local run (first for local responsiveness)
    "http://backend:8000",        # docker service name
    "http://dcoy_backend:8000",   # optional fallback container name
]
