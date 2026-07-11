"""API requests service client connecting to the FastAPI backend with security token authentication."""

import requests
import streamlit as st
import time
from typing import Any, Dict, Optional, Tuple
from dashboard.utils.constants import BACKEND_URLS, REFRESH_INTERVAL, EXPLAIN_REFRESH_INTERVAL

@st.cache_data(ttl=60)
def find_working_backend() -> Tuple[Optional[str], Optional[int]]:
    """Probe BACKEND_URLS list for an active health check response."""
    for url in BACKEND_URLS:
        started = time.time()
        try:
            response = requests.get(f"{url}/health", timeout=5, verify=False)
            response.raise_for_status()
            latency_ms = int((time.time() - started) * 1000)
            return url, latency_ms
        except Exception:
            continue
    return None, None

@st.cache_data(ttl=REFRESH_INTERVAL)
def _fetch_data_cached(url: str, cache_key: int, headers: dict) -> Optional[Dict[str, Any]]:
    """Perform an authenticated cached GET request to the /detect endpoint."""
    try:
        response = requests.get(f"{url}/detect", headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def fetch_data(url: str) -> Optional[Dict[str, Any]]:
    """Retrieve detection dataset from backend with authentication headers."""
    cache_key = int(time.time() // REFRESH_INTERVAL)
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}
    return _fetch_data_cached(url, cache_key, headers)

@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def _fetch_explain_cached(url: str, cache_key: int, headers: dict) -> Optional[Dict[str, Any]]:
    """Perform an authenticated cached GET request to the /explain endpoint."""
    try:
        response = requests.get(f"{url}/explain", headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def fetch_explain_data(url: str) -> Optional[Dict[str, Any]]:
    """Retrieve explainable alerts from backend with authentication headers."""
    cache_key = int(time.time() // EXPLAIN_REFRESH_INTERVAL)
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}
    return _fetch_explain_cached(url, cache_key, headers)
