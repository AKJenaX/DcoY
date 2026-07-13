"""DcoY Cyber Defense Dashboard entry point."""

import time
from datetime import datetime

import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

from dashboard.services.api_client import find_working_backend, fetch_data, fetch_explain_data, fetch_executive_metrics
from dashboard.utils.constants import REFRESH_INTERVAL, SESSION_TOKEN_PATH
from dashboard.utils.theme import inject_custom_theme
from dashboard.utils.formatting import format_attack_locations
from dashboard.components.sidebar import render_sidebar
from dashboard.components.metrics import render_overview_metrics
from dashboard.components.charts import render_live_attack_map, render_attack_analysis_charts
from dashboard.components.tables import render_high_risk_threats, render_detailed_logs, render_ai_explanations
from dashboard.components.chat import render_qa_chat
from dashboard.components.threat_intel import render_threat_intelligence_page
from dashboard.components.live_geolocation import render_live_geolocation_page
from dashboard.components.copilot_intel import render_copilot_page
from dashboard.components.investigations import render_investigations_page
from dashboard.components.threat_hunting import render_threat_hunting_page
from dashboard.components.detection_engineering import render_detection_rules_page
from dashboard.components.executive_dashboard import render_executive_dashboard_page
from dashboard.components.attack_simulation import render_attack_simulation_page
from dashboard.components.incident_response import render_incident_response_page
from dashboard.components.knowledge_graph import render_knowledge_graph_page
from marketing.pages.landing import render_marketing_page

# Disable insecure warning for development environment calls
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set Streamlit Page Configuration
st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

# Inject Custom styling
inject_custom_theme()

page = st.query_params.get("page", "marketing")
search_val = st.query_params.get("search", "")

if search_val and page != "marketing":
    page = "search"

if page == "marketing":
    render_marketing_page()
    st.stop()

# Set Auto-Refresh component
st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="refresh_main")

# Show skeleton loader animation on initial page boot
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        st.markdown('<div class="shimmer-skeleton title" style="width: 40%;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="shimmer-skeleton card" style="height: 80px; margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="shimmer-skeleton card" style="height: 300px; margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown('<div class="shimmer-skeleton card" style="height: 400px;"></div>', unsafe_allow_html=True)
    time.sleep(0.6)
    st.session_state.loaded = True
    st.rerun()

# 1. Establish API Connection and Latency
api_base, latency_ms = find_working_backend()

if not api_base:
    st.error("FastAPI Backend not reachable. Ensure the server is running on port 8000.")
    st.stop()

latency_ms = int(latency_ms or 0)

# 1.5 Handle Security Portal Authentication and persistence

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None

# Attempt to restore token from temp session file
if not st.session_state.auth_token and SESSION_TOKEN_PATH.exists():
    try:
        st.session_state.auth_token = SESSION_TOKEN_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        st.session_state.auth_token = None

if "current_user" not in st.session_state:
    st.session_state.current_user = "operator"

if not st.session_state.auth_token:
    if st.session_state.get("logout_success"):
        st.toast("Successfully logged out!", icon="🔑")
        st.session_state.logout_success = False
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
                            token = r.json()["access_token"]
                            st.session_state.auth_token = token
                            st.session_state.current_user = username
                            
                            # Write token to file for persistence
                            try:
                                SESSION_TOKEN_PATH.write_text(token, encoding="utf-8")
                            except Exception:
                                pass
                                
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
        <span style="font-size:0.75rem; color:var(--text-secondary); border-right:1px solid var(--border-color); padding-right:0.75rem; font-weight:600;">UTC: {current_time.split(" ")[-1]}</span>
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

# 3. Render Collapsible Sidebar and parse active page view routing
render_sidebar(api_base)
page = st.query_params.get("page", "overview")

if page == "executive":
    executive_metrics = fetch_executive_metrics(api_base)
    if not executive_metrics:
        st.warning("Executive metrics could not be loaded from backend.")
        st.stop()
    render_executive_dashboard_page(executive_metrics, latency_ms, api_base)
    st.stop()

# 4. Fetch Data
data = fetch_data(api_base)
if not data:
    # Check if this is an auth failure — probe the backend directly
    try:
        _headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if st.session_state.auth_token else {}
        _probe = requests.get(f"{api_base}/detect", headers=_headers, timeout=5, verify=False)
        if _probe.status_code == 401:
            # Token is expired or invalid — clear it and force re-login
            st.session_state.auth_token = None
            if SESSION_TOKEN_PATH.exists():
                try:
                    SESSION_TOKEN_PATH.unlink()
                except Exception:
                    pass
            st.cache_data.clear()
            st.rerun()
    except Exception:
        pass
    st.warning("No data returned from backend.")
    st.stop()

# 5. Fetch Explanations (with session caching fallback)
if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

# 6. Extract rows
detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([r for r in explain_rows if r.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

# Trigger elegant toast alert on threat alerts updates
if active_threats > 0:
    st.toast(f"🚨 CRITICAL WARNING: {active_threats} anomalous connections isolated in decoy honeypots!", icon="🚨")

# 6.5 Cache chart data states to prevent redraw blinking on static page queries
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

if page == "overview":
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
              <span class="status-indicator green" style="width:6px; height:6px;"></span> LIVE SYSTEM LINK
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
            <span class="status-pill secure" style="font-size:0.7rem;">AGENTS: 4/4 ONLINE</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 8. Partition Layout Columns: Main grid (3/4 width) | Right Threat Intelligence panel (1/4 width)
    col_main, col_right = st.columns([3, 1])

    with col_main:
        # 8.1 Render Overview KPI metrics cards
        render_overview_metrics(total_events, high_risk_count, active_threats, explain_rows)

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

    with col_right:
        st.markdown('<h3 class="section-title">Threat Intel Panel</h3>', unsafe_allow_html=True)
        
        # 1. Threat Score Gauge (Obsidian format)
        risk_percentage = min(100, int((high_risk_count / max(1, total_events)) * 100 + 40)) if high_risk_count > 0 else 12
        st.markdown(
            f"""
            <div class="gauge-container">
              <div class="card-title">Threat Risk Index</div>
              <div class="gauge-value">{risk_percentage} %</div>
              <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:0.4rem;">Status: <b>HIGH ALERT</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 2. Top IOCs List
        st.markdown('<div class="card-title" style="margin-top: 1rem;">Top IOCs (Threat IPs)</div>', unsafe_allow_html=True)
        ioc_html = ""
        unique_ips = list(set([r.get("ip") for r in explain_rows if r.get("ip")]))[:4]
        for ip in unique_ips:
            ioc_html += f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:0.4rem 0.5rem; background-color:var(--card-bg-sec); border-radius:6px; margin-bottom:0.4rem; border:1px solid var(--border-color);">
              <span style="font-size:0.8rem; font-family:monospace; color:var(--primary); font-weight:700;">{ip}</span>
              <span class="badge danger" style="font-size:0.55rem; padding:0.15rem 0.35rem;">MALICIOUS</span>
            </div>
            """
        if not ioc_html:
            ioc_html = "<p style='font-size:0.8rem; color:var(--text-secondary);'>No IOC indicators listed.</p>"
        st.markdown(ioc_html, unsafe_allow_html=True)
        
        # 3. MITRE ATT&CK Mapping
        st.markdown('<div class="card-title" style="margin-top: 1.25rem;">MITRE ATT&CK Techniques</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="padding: 0.65rem 0.75rem; background-color:var(--card-bg-sec); border-radius:8px; border:1px solid var(--border-color); font-size:0.75rem;">
              <div style="margin-bottom:0.4rem;"><b>T1110 - Brute Force</b><br/><span style="color:var(--text-secondary);">Credential Access</span></div>
              <div style="margin-bottom:0.4rem;"><b>T1046 - Network Scanning</b><br/><span style="color:var(--text-secondary);">Discovery</span></div>
              <div><b>T1190 - Public Exploit</b><br/><span style="color:var(--text-secondary);">Initial Access</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

elif page == "threat_intel":
    # Render dedicated Threat Intelligence page view
    render_threat_intelligence_page(explain_rows, detect_rows, latency_ms)
elif page == "live_geo":
    # Render dedicated Live Geolocation page view
    render_live_geolocation_page(explain_rows, detect_rows, latency_ms)
elif page == "copilot":
    # Render dedicated AI Security Copilot Center view
    render_copilot_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "investigations":
    # Render dedicated investigations and case management page view
    render_investigations_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "threat_hunting":
    # Render dedicated threat hunting proactive investigation view
    render_threat_hunting_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "detection_rules":
    # Render dedicated detection rules configuration workbench view
    render_detection_rules_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "incident_response":
    render_incident_response_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "soar":
    from dashboard.components.soar import render_soar_page
    render_soar_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "intelligence_fusion":
    from dashboard.components.intelligence_fusion import render_intelligence_fusion_page
    render_intelligence_fusion_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "attack_simulation":
    # Render dedicated attack simulation validation view
    render_attack_simulation_page(api_base)
elif page == "knowledge_graph":
    render_knowledge_graph_page(explain_rows, detect_rows, latency_ms, api_base)
elif page == "platform_health":
    from dashboard.components.platform_health import render_platform_health_page
    render_platform_health_page(api_base)
elif page == "search":
    from dashboard.components.global_search import render_global_search_results
    render_global_search_results(api_base)
else:
    # Unknown page route — redirect to overview
    st.query_params["page"] = "overview"
    st.rerun()
