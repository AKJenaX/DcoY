"""DcoY Cyber Defense Dashboard entry point."""

import sys
from pathlib import Path

# Add project root to path to allow importing dashboard package
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

from dashboard.services.api_client import find_working_backend, fetch_data, fetch_explain_data
from dashboard.utils.constants import REFRESH_INTERVAL
from dashboard.utils.theme import inject_custom_theme
from dashboard.utils.formatting import format_attack_locations
from dashboard.components.sidebar import render_sidebar
from dashboard.components.metrics import render_overview_metrics
from dashboard.components.charts import render_live_attack_map, render_attack_analysis_charts
from dashboard.components.tables import render_high_risk_threats, render_detailed_logs, render_ai_explanations
from dashboard.components.chat import render_qa_chat

# Disable insecure warning for development environment calls
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set Streamlit Page Configuration
st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

# Inject Custom styling
inject_custom_theme()

# Set Auto-Refresh component (dynamically set in constants.py)
st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="refresh_main")

# 1. Establish API Connection and Latency
api_base, latency_ms = find_working_backend()

if not api_base:
    st.error("FastAPI Backend not reachable. Ensure the server is running on port 8000.")
    st.stop()

# 1.5 Handle Security Portal Authentication
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "current_user" not in st.session_state:
    st.session_state.current_user = "operator"

if not st.session_state.auth_token:
    import requests
    import time
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("🔑 Operator Security Portal")
            st.info("Since database states are volatile, please click 'Register Operator' on your first visit, then click 'Log In'.")
            username = st.text_input("Username", value="operator")
            password = st.text_input("Password", type="password", value="secure_password")
            
            login_col, register_col = st.columns(2)
            with login_col:
                if st.button("Log In", use_container_width=True):
                    try:
                        r = requests.post(f"{api_base}/login", json={"username": username, "password": password}, verify=False)
                        if r.status_code == 200:
                            st.session_state.auth_token = r.json()["access_token"]
                            st.session_state.current_user = username
                            st.success("Access Granted! Loading system portal...")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please register first.")
                    except Exception as e:
                        st.error(f"Authentication failed: {str(e)}")
            with register_col:
                if st.button("Register Operator", use_container_width=True):
                    try:
                        r = requests.post(f"{api_base}/register", json={"username": username, "password": password}, verify=False)
                        if r.status_code == 200:
                            st.success("Registration successful! You may now Log In.")
                        else:
                            st.error(f"Registration failed: {r.json().get('detail', 'User already exists')}")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")
    st.stop()

# 2. Render Sticky Top Navigation Bar
from datetime import datetime
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
user_display = st.session_state.get("current_user", "operator")

st.markdown(
    f"""
    <div class="top-navbar">
      <div class="navbar-left">
        <svg class="soc-icon" style="width:24px; height:24px; color:var(--primary);" viewBox="0 0 24 24">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <span class="navbar-logo-text">DcoY</span>
        <span class="navbar-subtitle">AI-Powered Cyber Defense Platform</span>
      </div>
      <div class="navbar-center">
        <input type="text" class="navbar-search-box" placeholder="Search threats, IPs, reports, agents..." />
      </div>
      <div class="navbar-right">
        <button class="navbar-icon-btn">
          <svg class="soc-icon" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        </button>
        <button class="navbar-icon-btn">
          <svg class="soc-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        </button>
        <button class="navbar-icon-btn">
          <svg class="soc-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
        <div class="navbar-avatar">{user_display[:2].upper()}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. Fetch Data
data = fetch_data(api_base)
if not data:
    st.warning("No data returned from backend.")
    st.stop()

# 4. Fetch Explanations (with session caching fallback)
if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

# 5. Extract rows
detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([r for r in explain_rows if r.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

# 5.5 Cache chart data states to prevent redraw blinking on static page queries
if "last_total_events" not in st.session_state:
    st.session_state.last_total_events = 0
if "cached_attack_locations" not in st.session_state:
    st.session_state.cached_attack_locations = []
if "cached_attack_summary" not in st.session_state:
    st.session_state.cached_attack_summary = {}
if "cached_response_summary" not in st.session_state:
    st.session_state.cached_response_summary = {}

# Update cache only if data size has changed or cache is empty
if total_events != st.session_state.last_total_events or not st.session_state.cached_attack_locations:
    st.session_state.last_total_events = total_events
    st.session_state.cached_attack_locations = format_attack_locations(explain_rows)
    st.session_state.cached_attack_summary = data.get("attack_summary", {})
    st.session_state.cached_response_summary = data.get("response_summary", {})

# 6. Render Collapsible Sidebar
render_sidebar(api_base)

# 7. Render Hero Landing Section
st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem;">
      <div>
        <h1 class="page-title">Threat Intelligence Overview</h1>
        <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">Real-time AI-powered cyber defense monitoring and active honeypot metrics.</p>
      </div>
      <div style="display:flex; gap:0.5rem;">
        <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
          <span class="status-indicator green" style="width:6px; height:6px;"></span> LIVE FEEDS
        </span>
        <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
        <span class="status-pill secure" style="font-size:0.7rem;">AGENTS: 4/4 ACTIVE</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 8. Render Overview KPI metrics cards
render_overview_metrics(total_events, high_risk_count, active_threats, explain_rows)

# 9. Main Grid Layout Redesign

# Row 1: Threat Map (2/3 width) | Threat Timeline/AI Explanations (1/3 width)
row1_left, row1_right = st.columns([2, 1])
with row1_left:
    render_live_attack_map(st.session_state.cached_attack_locations)
with row1_right:
    render_ai_explanations(explain_rows)

# Row 2: Attack Analysis Charts (2/3 width) | AI Copilot (1/3 width)
row2_left, row2_right = st.columns([2, 1])
with row2_left:
    render_attack_analysis_charts(st.session_state.cached_attack_summary, st.session_state.cached_response_summary)
with row2_right:
    render_qa_chat(api_base)

# Row 3: Threat Feed / Alerts (2/3 width) | Recent Events / Logs (1/3 width)
row3_left, row3_right = st.columns([2, 1])
with row3_left:
    render_high_risk_threats(explain_rows)
with row3_right:
    render_detailed_logs(detect_rows, explain_rows)
