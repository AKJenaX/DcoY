"""DcoY Streamlit Dashboard."""
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
:root { --bg:#000000; --card:#2D2D2D; --green:#2CFF05; --purple:#BF00FF; --text:#FFFFFF; }
body, .stApp { background: var(--bg); color: var(--text); }
.block-container { padding-top: 1.8rem; max-width: 1400px; }
h1,h2,h3,h4,h5,h6,p,span,label,div { color: var(--text); }
.top-divider { border: none; border-top: 1px solid var(--purple); margin: 0.2rem 0 1rem 0; opacity: 0.8; }
.status-row { display: flex; gap: 0.7rem; flex-wrap: wrap; margin: 0.3rem 0 1.2rem 0; }
.status-pill { background: linear-gradient(135deg,var(--card),var(--bg)); border: 1px solid var(--purple); border-radius: 999px; padding: 0.4rem 0.9rem; font-weight: 700; font-size: 0.85rem; box-shadow: 0 0 14px rgba(191,0,255,0.22); }
.status-pill.live { color: var(--green); border-color: var(--green); box-shadow: 0 0 14px rgba(44,255,5,0.25); }
.status-pill.secure { color: var(--purple); }
.status-pill.latency { color: var(--text); }
.section-title { margin: 0.2rem 0 0.8rem 0; letter-spacing: 0.2px; }
.card { background: linear-gradient(160deg,var(--card),var(--bg)); border: 1px solid var(--purple); border-radius: 14px; padding: 1rem; margin-bottom: 0.8rem; box-shadow: 0 0 24px rgba(191,0,255,0.16); }
.metric-box { background: linear-gradient(160deg,var(--card),var(--bg)); border: 1px solid var(--purple); border-radius: 12px; padding: 1rem; text-align: center; box-shadow: 0 0 20px rgba(191,0,255,0.14); }
.metric-box h3,.metric-box h2 { margin: 0; }
.metric-box h3 { margin-bottom: 0.35rem; font-size: 0.95rem; }
.green { color: var(--green); font-weight: 800; } .purple { color: var(--purple); font-weight: 800; }
div[data-testid="stDataFrame"] { background: linear-gradient(160deg,var(--card),var(--bg)); border: 1px solid var(--purple); border-radius: 12px; padding: 0.25rem; }
div[data-testid="stDataFrame"] [role="columnheader"] { background-color: var(--bg)!important; color: var(--green)!important; font-weight: 700!important; }
div[data-testid="stDataFrame"] [role="gridcell"] { background-color: var(--card)!important; color: var(--text)!important; }
div[data-testid="stExpander"] { background: linear-gradient(160deg,var(--card),var(--bg)); border: 1px solid var(--purple); border-radius: 12px; margin-bottom: 0.6rem; }
div[data-testid="stExpander"] details summary { color: var(--green)!important; font-weight: 700; }
div[data-testid="stAlert"] { background: linear-gradient(160deg,var(--card),var(--bg)); border: 1px solid var(--purple); border-radius: 12px; color: var(--text); }
</style>
""",
    unsafe_allow_html=True,
)

# Exactly one refresh component.
st_autorefresh(interval=2000, key="refresh_main")

REFRESH_INTERVAL = 2
EXPLAIN_REFRESH_INTERVAL = 15
BACKEND_URLS = ["http://127.0.0.1:8000", "http://localhost:8000"]


def find_working_backend():
    for url in BACKEND_URLS:
        started = time.time()
        try:
            response = requests.get(f"{url}/health", timeout=10, verify=False)
            response.raise_for_status()
            return url, int((time.time() - started) * 1000)
        except Exception:
            continue
    return None, None


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    try:
        response = requests.get(f"{url}/detect", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend not reachable")
        return None


def fetch_data(url):
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))


@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    try:
        response = requests.get(f"{url}/explain", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.warning("Could not fetch explain data")
        return None


def fetch_explain_data(url):
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))


st.title("🛡️ DcoY Cyber Defense Dashboard")
st.markdown('<hr class="top-divider" />', unsafe_allow_html=True)

api_base, latency_ms = find_working_backend()
if not api_base:
    st.error("Backend not reachable")
    st.stop()

st.markdown(
    f"""
<div class="status-row">
  <span class="status-pill live">LIVE</span>
  <span class="status-pill secure">SECURE</span>
  <span class="status-pill latency">LATENCY: {latency_ms}ms</span>
</div>
""",
    unsafe_allow_html=True,
)

data = fetch_data(api_base)
if not data:
    st.stop()

if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([r for r in explain_rows if r.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

st.markdown('<h3 class="section-title">Overview Metrics</h3>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-box"><h3>Total Events</h3><h2 class="green">{total_events}</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box"><h3>High Risk</h3><h2 class="purple">{high_risk_count}</h2></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-box"><h3>Active Threats</h3><h2 class="green">{active_threats}</h2></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🌍 Live Attack Map</h3>', unsafe_allow_html=True)
locations = []
for row in explain_rows:
    loc = row.get("location", {})
    if loc.get("lat") is not None and loc.get("lon") is not None:
        locations.append(
            {
                "latitude": loc.get("lat"),
                "longitude": loc.get("lon"),
                "ip": row.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown"),
            }
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
if locations:
    map_df = pd.DataFrame(locations)
    m1, m2 = st.columns([3, 1])
    with m1:
        st.map(map_df[["latitude", "longitude"]], width='stretch')
    with m2:
        country_df = map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
        st.dataframe(country_df, width='stretch', hide_index=True)
else:
    st.info("No geolocation data available")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📊 Attack Analysis</h3>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    summary = data.get("attack_summary", {})
    if summary:
        attack_df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        fig_attack = px.bar(attack_df, x="Type", y="Count", color_discrete_sequence=["#2CFF05"])
        fig_attack.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig_attack.update_xaxes(showgrid=False)
        fig_attack.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig_attack, width='stretch', key="chart_attack_main")
    else:
        st.info("No attack analysis data")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    response_summary = data.get("response_summary", {})
    if response_summary:
        response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
        fig_response = px.bar(response_df, x="Honeypot", y="Count", color_discrete_sequence=["#BF00FF"])
        fig_response.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig_response.update_xaxes(showgrid=False)
        fig_response.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig_response, width='stretch', key="chart_response_main")
    else:
        st.info("No honeypot response data")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🚨 High Risk Threats</h3>', unsafe_allow_html=True)
high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
if high_risk:
    st.dataframe(pd.DataFrame(high_risk), width='stretch', hide_index=True)
else:
    st.success("No high-risk threats detected")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📋 Detailed Logs</h3>', unsafe_allow_html=True)
log_source = explain_rows if explain_rows else detect_rows
if log_source:
    detailed_df = pd.DataFrame(log_source)
    preferred_columns = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    existing_columns = [col for col in preferred_columns if col in detailed_df.columns]
    if existing_columns:
        detailed_df = detailed_df[existing_columns]
    st.dataframe(detailed_df, width='stretch', hide_index=True)
else:
    st.info("No log data available")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🧠 AI Explanations</h3>', unsafe_allow_html=True)
if explain_rows:
    for idx, row in enumerate(explain_rows):
        with st.expander(f"IP: {row.get('ip', 'Unknown')} | Risk: {row.get('risk_level', 'unknown')}", expanded=False):
            st.write(row.get("explanation", "No explanation available"))
else:
    st.info("No AI explanations available")

# Stop execution to prevent any accidentally appended duplicate blocks
# from rendering duplicate components in Streamlit.
st.stop()
"""DcoY Streamlit Dashboard."""
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
:root { --bg:#000000; --card:#2D2D2D; --green:#2CFF05; --purple:#BF00FF; --text:#FFFFFF; }
body, .stApp { background-color: var(--bg); color: var(--text); }
.block-container { padding-top: 1.8rem; max-width: 1400px; }
h1,h2,h3,h4,h5,h6,p,span,label,div { color: var(--text); }
.top-divider { border:none; border-top:1px solid var(--purple); margin:0.2rem 0 1rem 0; opacity:0.8; }
.status-row { display:flex; gap:0.7rem; flex-wrap:wrap; margin:0.3rem 0 1.2rem 0; }
.status-pill { background:linear-gradient(135deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:999px; padding:0.4rem 0.9rem; font-weight:700; font-size:0.85rem; box-shadow:0 0 14px rgba(191,0,255,0.22); }
.status-pill.live { color: var(--green); border-color: var(--green); box-shadow:0 0 14px rgba(44,255,5,0.25); }
.status-pill.secure { color: var(--purple); }
.status-pill.latency { color: var(--text); }
.section-title { margin:0.2rem 0 0.8rem 0; letter-spacing:0.2px; }
.card { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:14px; padding:1rem; margin-bottom:0.8rem; box-shadow:0 0 24px rgba(191,0,255,0.16); }
.metric-box { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; padding:1rem; text-align:center; box-shadow:0 0 20px rgba(191,0,255,0.14); }
.metric-box h3,.metric-box h2 { margin:0; }
.metric-box h3 { margin-bottom:0.35rem; color:var(--text); font-size:0.95rem; }
.green { color: var(--green); font-weight: 800; } .purple { color: var(--purple); font-weight: 800; }
div[data-testid="stDataFrame"] { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; padding:0.25rem; }
div[data-testid="stDataFrame"] [role="columnheader"] { background-color: var(--bg)!important; color: var(--green)!important; font-weight:700!important; }
div[data-testid="stDataFrame"] [role="gridcell"] { background-color: var(--card)!important; color: var(--text)!important; }
div[data-testid="stExpander"] { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; margin-bottom:0.6rem; }
div[data-testid="stExpander"] details summary { color: var(--green)!important; font-weight:700; }
div[data-testid="stAlert"] { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; color:var(--text); }
.stButton > button { background-color:var(--card); color:var(--text); border:1px solid var(--purple); border-radius:8px; }
.stButton > button:hover { border-color:var(--green); color:var(--green); }
</style>
""",
    unsafe_allow_html=True,
)

def ensure_autorefresh_once():
    """Render auto-refresh component only once per app run."""
    if st.session_state.get("_autorefresh_rendered", False):
        return
    st.session_state["_autorefresh_rendered"] = True
    st_autorefresh(interval=2000, key="refresh_main")


# Guarded refresh registration.
ensure_autorefresh_once()

REFRESH_INTERVAL = 2
EXPLAIN_REFRESH_INTERVAL = 15
BACKEND_URLS = ["http://127.0.0.1:8000", "http://localhost:8000"]


def find_working_backend():
    for url in BACKEND_URLS:
        started = time.time()
        try:
            response = requests.get(f"{url}/health", timeout=10, verify=False)
            response.raise_for_status()
            return url, int((time.time() - started) * 1000)
        except Exception:
            continue
    return None, None


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    try:
        response = requests.get(f"{url}/detect", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend not reachable")
        return None


def fetch_data(url):
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))


@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    try:
        response = requests.get(f"{url}/explain", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.warning("Could not fetch explain data")
        return None


def fetch_explain_data(url):
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))


st.title("🛡️ DcoY Cyber Defense Dashboard")
st.markdown('<hr class="top-divider" />', unsafe_allow_html=True)

api_base, latency_ms = find_working_backend()
if not api_base:
    st.error("Backend not reachable")
    st.stop()

st.markdown(
    f"""
<div class="status-row">
  <span class="status-pill live">LIVE</span>
  <span class="status-pill secure">SECURE</span>
  <span class="status-pill latency">LATENCY: {latency_ms}ms</span>
</div>
""",
    unsafe_allow_html=True,
)

data = fetch_data(api_base)
if not data:
    st.stop()

if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([r for r in explain_rows if r.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

st.markdown('<h3 class="section-title">Overview Metrics</h3>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-box"><h3>Total Events</h3><h2 class="green">{total_events}</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box"><h3>High Risk</h3><h2 class="purple">{high_risk_count}</h2></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-box"><h3>Active Threats</h3><h2 class="green">{active_threats}</h2></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🌍 Live Attack Map</h3>', unsafe_allow_html=True)
locations = []
for row in explain_rows:
    loc = row.get("location", {})
    if loc.get("lat") is not None and loc.get("lon") is not None:
        locations.append(
            {
                "latitude": loc.get("lat"),
                "longitude": loc.get("lon"),
                "ip": row.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown"),
            }
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
if locations:
    map_df = pd.DataFrame(locations)
    m1, m2 = st.columns([3, 1])
    with m1:
        st.map(map_df[["latitude", "longitude"]], width='stretch')
    with m2:
        country_df = map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
        st.dataframe(country_df, width='stretch', hide_index=True)
else:
    st.info("No geolocation data available")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📊 Attack Analysis</h3>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    summary = data.get("attack_summary", {})
    if summary:
        attack_df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        fig = px.bar(attack_df, x="Type", y="Count", color_discrete_sequence=["#2CFF05"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No attack analysis data")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    response_summary = data.get("response_summary", {})
    if response_summary:
        response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
        fig = px.bar(response_df, x="Honeypot", y="Count", color_discrete_sequence=["#BF00FF"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No honeypot response data")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🚨 High Risk Threats</h3>', unsafe_allow_html=True)
high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
if high_risk:
    st.dataframe(pd.DataFrame(high_risk), width='stretch', hide_index=True)
else:
    st.success("No high-risk threats detected")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📋 Detailed Logs</h3>', unsafe_allow_html=True)
log_source = explain_rows if explain_rows else detect_rows
if log_source:
    detailed_df = pd.DataFrame(log_source)
    preferred_columns = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    existing_columns = [col for col in preferred_columns if col in detailed_df.columns]
    if existing_columns:
        detailed_df = detailed_df[existing_columns]
    st.dataframe(detailed_df, width='stretch', hide_index=True)
else:
    st.info("No log data available")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🧠 AI Explanations</h3>', unsafe_allow_html=True)
if explain_rows:
    for row in explain_rows:
        with st.expander(f"IP: {row.get('ip', 'Unknown')} | Risk: {row.get('risk_level', 'unknown')}"):
            st.write(row.get("explanation", "No explanation available"))
else:
    st.info("No AI explanations available")
"""DcoY Streamlit Dashboard."""
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
:root { --bg:#000000; --card:#2D2D2D; --green:#2CFF05; --purple:#BF00FF; --text:#FFFFFF; }
body, .stApp { background-color: var(--bg); color: var(--text); }
.block-container { padding-top: 1.8rem; max-width: 1400px; }
h1,h2,h3,h4,h5,h6,p,span,label,div { color: var(--text); }
.top-divider { border:none; border-top:1px solid var(--purple); margin:0.2rem 0 1rem 0; opacity:0.8; }
.status-row { display:flex; gap:0.7rem; flex-wrap:wrap; margin:0.3rem 0 1.2rem 0; }
.status-pill { background:linear-gradient(135deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:999px; padding:0.4rem 0.9rem; font-weight:700; font-size:0.85rem; box-shadow:0 0 14px rgba(191,0,255,0.22); }
.status-pill.live { color: var(--green); border-color: var(--green); box-shadow:0 0 14px rgba(44,255,5,0.25); }
.status-pill.secure { color: var(--purple); }
.status-pill.latency { color: var(--text); }
.section-title { margin:0.2rem 0 0.8rem 0; letter-spacing:0.2px; }
.card { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:14px; padding:1rem; margin-bottom:0.8rem; box-shadow:0 0 24px rgba(191,0,255,0.16); }
.metric-box { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; padding:1rem; text-align:center; box-shadow:0 0 20px rgba(191,0,255,0.14); }
.metric-box h3,.metric-box h2 { margin:0; }
.metric-box h3 { margin-bottom:0.35rem; color:var(--text); font-size:0.95rem; }
.green { color: var(--green); font-weight: 800; } .purple { color: var(--purple); font-weight: 800; }
div[data-testid="stDataFrame"] { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; padding:0.25rem; }
div[data-testid="stDataFrame"] [role="columnheader"] { background-color: var(--bg)!important; color: var(--green)!important; font-weight:700!important; }
div[data-testid="stDataFrame"] [role="gridcell"] { background-color: var(--card)!important; color: var(--text)!important; }
div[data-testid="stExpander"] { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; margin-bottom:0.6rem; }
div[data-testid="stExpander"] details summary { color: var(--green)!important; font-weight:700; }
div[data-testid="stAlert"] { background:linear-gradient(160deg,var(--card),var(--bg)); border:1px solid var(--purple); border-radius:12px; color:var(--text); }
.stButton > button { background-color:var(--card); color:var(--text); border:1px solid var(--purple); border-radius:8px; }
.stButton > button:hover { border-color:var(--green); color:var(--green); }
</style>
""",
    unsafe_allow_html=True,
)

# One auto-refresh component only.
ensure_autorefresh_once()

REFRESH_INTERVAL = 2
EXPLAIN_REFRESH_INTERVAL = 15
BACKEND_URLS = ["http://127.0.0.1:8000", "http://localhost:8000"]


def find_working_backend():
    for url in BACKEND_URLS:
        started = time.time()
        try:
            response = requests.get(f"{url}/health", timeout=10, verify=False)
            response.raise_for_status()
            return url, int((time.time() - started) * 1000)
        except Exception:
            continue
    return None, None


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    try:
        response = requests.get(f"{url}/detect", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend not reachable")
        return None


def fetch_data(url):
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))


@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    try:
        response = requests.get(f"{url}/explain", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.warning("Could not fetch explain data")
        return None


def fetch_explain_data(url):
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))


st.title("🛡️ DcoY Cyber Defense Dashboard")
st.markdown('<hr class="top-divider" />', unsafe_allow_html=True)

api_base, latency_ms = find_working_backend()
if not api_base:
    st.error("Backend not reachable")
    st.stop()

st.markdown(
    f"""
<div class="status-row">
  <span class="status-pill live">LIVE</span>
  <span class="status-pill secure">SECURE</span>
  <span class="status-pill latency">LATENCY: {latency_ms}ms</span>
</div>
""",
    unsafe_allow_html=True,
)

data = fetch_data(api_base)
if not data:
    st.stop()

if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([r for r in explain_rows if r.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

st.markdown('<h3 class="section-title">Overview Metrics</h3>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-box"><h3>Total Events</h3><h2 class="green">{total_events}</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box"><h3>High Risk</h3><h2 class="purple">{high_risk_count}</h2></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-box"><h3>Active Threats</h3><h2 class="green">{active_threats}</h2></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🌍 Live Attack Map</h3>', unsafe_allow_html=True)
locations = []
for row in explain_rows:
    loc = row.get("location", {})
    if loc.get("lat") is not None and loc.get("lon") is not None:
        locations.append(
            {
                "latitude": loc.get("lat"),
                "longitude": loc.get("lon"),
                "ip": row.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown"),
            }
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
if locations:
    map_df = pd.DataFrame(locations)
    m1, m2 = st.columns([3, 1])
    with m1:
        st.map(map_df[["latitude", "longitude"]], width='stretch')
    with m2:
        country_df = map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
        st.dataframe(country_df, width='stretch', hide_index=True)
else:
    st.info("No geolocation data available")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📊 Attack Analysis</h3>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    summary = data.get("attack_summary", {})
    if summary:
        attack_df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        fig = px.bar(attack_df, x="Type", y="Count", color_discrete_sequence=["#2CFF05"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No attack analysis data")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    response_summary = data.get("response_summary", {})
    if response_summary:
        response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
        fig = px.bar(response_df, x="Honeypot", y="Count", color_discrete_sequence=["#BF00FF"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No honeypot response data")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🚨 High Risk Threats</h3>', unsafe_allow_html=True)
high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
if high_risk:
    st.dataframe(pd.DataFrame(high_risk), width='stretch', hide_index=True)
else:
    st.success("No high-risk threats detected")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📋 Detailed Logs</h3>', unsafe_allow_html=True)
log_source = explain_rows if explain_rows else detect_rows
if log_source:
    detailed_df = pd.DataFrame(log_source)
    preferred_columns = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    existing_columns = [col for col in preferred_columns if col in detailed_df.columns]
    if existing_columns:
        detailed_df = detailed_df[existing_columns]
    st.dataframe(detailed_df, width='stretch', hide_index=True)
else:
    st.info("No log data available")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🧠 AI Explanations</h3>', unsafe_allow_html=True)
if explain_rows:
    for row in explain_rows:
        with st.expander(f"IP: {row.get('ip', 'Unknown')} | Risk: {row.get('risk_level', 'unknown')}"):
            st.write(row.get("explanation", "No explanation available"))
else:
    st.info("No AI explanations available")
"""DcoY Streamlit Dashboard."""
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
:root {
    --bg: #000000;
    --card: #2D2D2D;
    --green: #2CFF05;
    --purple: #BF00FF;
    --text: #FFFFFF;
}

body, .stApp {
    background-color: var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 1.8rem;
    max-width: 1400px;
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: var(--text);
}

.top-divider {
    border: none;
    border-top: 1px solid var(--purple);
    margin: 0.2rem 0 1rem 0;
    opacity: 0.8;
}

.status-row {
    display: flex;
    gap: 0.7rem;
    flex-wrap: wrap;
    margin: 0.3rem 0 1.2rem 0;
}

.status-pill {
    background: linear-gradient(135deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 0 14px rgba(191, 0, 255, 0.22);
}

.status-pill.live {
    color: var(--green);
    border-color: var(--green);
    box-shadow: 0 0 14px rgba(44, 255, 5, 0.25);
}

.status-pill.secure {
    color: var(--purple);
}

.status-pill.latency {
    color: var(--text);
}

.section-title {
    margin: 0.2rem 0 0.8rem 0;
    letter-spacing: 0.2px;
}

.card {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 24px rgba(191, 0, 255, 0.16);
}

.metric-box {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(191, 0, 255, 0.14);
}

.metric-box h3, .metric-box h2 {
    margin: 0;
}

.metric-box h3 {
    margin-bottom: 0.35rem;
    color: var(--text);
    font-size: 0.95rem;
}

.green { color: var(--green); font-weight: 800; }
.purple { color: var(--purple); font-weight: 800; }

div[data-testid="stDataFrame"] {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    padding: 0.25rem;
}
div[data-testid="stDataFrame"] [role="columnheader"] {
    background-color: var(--bg) !important;
    color: var(--green) !important;
    font-weight: 700 !important;
}
div[data-testid="stDataFrame"] [role="gridcell"] {
    background-color: var(--card) !important;
    color: var(--text) !important;
}

div[data-testid="stExpander"] {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    margin-bottom: 0.6rem;
}
div[data-testid="stExpander"] details summary {
    color: var(--green) !important;
    font-weight: 700;
}

div[data-testid="stAlert"] {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    color: var(--text);
}

.stButton > button {
    background-color: var(--card);
    color: var(--text);
    border: 1px solid var(--purple);
    border-radius: 8px;
}
.stButton > button:hover {
    border-color: var(--green);
    color: var(--green);
}
</style>
""",
    unsafe_allow_html=True,
)

# Single autorefresh call with unique key.
ensure_autorefresh_once()

REFRESH_INTERVAL = 2
EXPLAIN_REFRESH_INTERVAL = 15
BACKEND_URLS = ["http://127.0.0.1:8000", "http://localhost:8000"]


def find_working_backend():
    """Try to connect to backend using multiple URLs and return latency."""
    for url in BACKEND_URLS:
        start = time.time()
        try:
            response = requests.get(f"{url}/health", timeout=10, verify=False)
            response.raise_for_status()
            latency_ms = int((time.time() - start) * 1000)
            return url, latency_ms
        except Exception:
            continue
    return None, None


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    """Fetch detection data from backend."""
    try:
        response = requests.get(f"{url}/detect", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend not reachable")
        return None


def fetch_data(url):
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))


@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    """Fetch explanation data from backend."""
    try:
        response = requests.get(f"{url}/explain", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.warning("Could not fetch explain data")
        return None


def fetch_explain_data(url):
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))


st.title("🛡️ DcoY Cyber Defense Dashboard")
st.markdown('<hr class="top-divider" />', unsafe_allow_html=True)

api_base, latency_ms = find_working_backend()
if not api_base:
    st.error("Backend not reachable")
    st.stop()

st.markdown(
    f"""
<div class="status-row">
  <span class="status-pill live">LIVE</span>
  <span class="status-pill secure">SECURE</span>
  <span class="status-pill latency">LATENCY: {latency_ms}ms</span>
</div>
""",
    unsafe_allow_html=True,
)

data = fetch_data(api_base)
if not data:
    st.stop()

if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([row for row in explain_rows if row.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

st.markdown('<h3 class="section-title">Overview Metrics</h3>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="metric-box"><h3>Total Events</h3><h2 class="green">{total_events}</h2></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-box"><h3>High Risk</h3><h2 class="purple">{high_risk_count}</h2></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-box"><h3>Active Threats</h3><h2 class="green">{active_threats}</h2></div>',
        unsafe_allow_html=True,
    )
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🌍 Live Attack Map</h3>', unsafe_allow_html=True)
locations = []
for row in explain_rows:
    loc = row.get("location", {})
    lat = loc.get("lat")
    lon = loc.get("lon")
    if lat is not None and lon is not None:
        locations.append(
            {
                "latitude": lat,
                "longitude": lon,
                "ip": row.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown"),
            }
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
if locations:
    map_df = pd.DataFrame(locations)
    map_col1, map_col2 = st.columns([3, 1])
    with map_col1:
        st.map(map_df[["latitude", "longitude"]], width='stretch')
    with map_col2:
        country_df = (
            map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )
        st.dataframe(country_df, width='stretch', hide_index=True)
else:
    st.info("No geolocation data available")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📊 Attack Analysis</h3>', unsafe_allow_html=True)
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    summary = data.get("attack_summary", {})
    if summary:
        attack_df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        fig = px.bar(attack_df, x="Type", y="Count", color_discrete_sequence=["#2CFF05"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No attack analysis data")
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    response_summary = data.get("response_summary", {})
    if response_summary:
        response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
        fig = px.bar(response_df, x="Honeypot", y="Count", color_discrete_sequence=["#BF00FF"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No honeypot response data")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🚨 High Risk Threats</h3>', unsafe_allow_html=True)
high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
if high_risk:
    st.dataframe(pd.DataFrame(high_risk), width='stretch', hide_index=True)
else:
    st.success("No high-risk threats detected")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📋 Detailed Logs</h3>', unsafe_allow_html=True)
log_source = explain_rows if explain_rows else detect_rows
if log_source:
    detailed_df = pd.DataFrame(log_source)
    preferred_columns = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    existing_columns = [col for col in preferred_columns if col in detailed_df.columns]
    if existing_columns:
        detailed_df = detailed_df[existing_columns]
    st.dataframe(detailed_df, width='stretch', hide_index=True)
else:
    st.info("No log data available")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<h3 class="section-title">🧠 AI Explanations</h3>', unsafe_allow_html=True)
if explain_rows:
    for row in explain_rows:
        with st.expander(f"IP: {row.get('ip', 'Unknown')} | Risk: {row.get('risk_level', 'unknown')}"):
            st.write(row.get("explanation", "No explanation available"))
else:
    st.info("No AI explanations available")
"""DcoY Streamlit Dashboard."""
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
:root {
    --bg: #000000;
    --card: #2D2D2D;
    --green: #2CFF05;
    --purple: #BF00FF;
    --text: #FFFFFF;
}

body, .stApp {
    background-color: var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 1.8rem;
    max-width: 1400px;
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: var(--text);
}

.top-divider {
    border: none;
    border-top: 1px solid var(--purple);
    margin: 0.2rem 0 1rem 0;
    opacity: 0.8;
}

.status-row {
    display: flex;
    gap: 0.7rem;
    flex-wrap: wrap;
    margin: 0.3rem 0 1.2rem 0;
}

.status-pill {
    background: linear-gradient(135deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 0 14px rgba(191, 0, 255, 0.22);
}

.status-pill.live {
    color: var(--green);
    border-color: var(--green);
    box-shadow: 0 0 14px rgba(44, 255, 5, 0.25);
}

.status-pill.secure {
    color: var(--purple);
}

.status-pill.latency {
    color: var(--text);
}

.section-title {
    margin: 0.2rem 0 0.8rem 0;
    letter-spacing: 0.2px;
}

.card {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 24px rgba(191, 0, 255, 0.16);
}

.metric-box {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(191, 0, 255, 0.14);
}

.metric-box h3, .metric-box h2 {
    margin: 0;
}

.metric-box h3 {
    margin-bottom: 0.35rem;
    color: var(--text);
    font-size: 0.95rem;
}

.green { color: var(--green); font-weight: 800; }
.purple { color: var(--purple); font-weight: 800; }

/* DataFrame style */
div[data-testid="stDataFrame"] {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    padding: 0.25rem;
}
div[data-testid="stDataFrame"] [role="columnheader"] {
    background-color: var(--bg) !important;
    color: var(--green) !important;
    font-weight: 700 !important;
}
div[data-testid="stDataFrame"] [role="gridcell"] {
    background-color: var(--card) !important;
    color: var(--text) !important;
}

/* Expander style */
div[data-testid="stExpander"] {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    margin-bottom: 0.6rem;
}
div[data-testid="stExpander"] details summary {
    color: var(--green) !important;
    font-weight: 700;
}

/* Alert style */
div[data-testid="stAlert"] {
    background: linear-gradient(160deg, var(--card), var(--bg));
    border: 1px solid var(--purple);
    border-radius: 12px;
    color: var(--text);
}

.stButton > button {
    background-color: var(--card);
    color: var(--text);
    border: 1px solid var(--purple);
    border-radius: 8px;
}
.stButton > button:hover {
    border-color: var(--green);
    color: var(--green);
}
</style>
""",
    unsafe_allow_html=True,
)

ensure_autorefresh_once()

REFRESH_INTERVAL = 2
EXPLAIN_REFRESH_INTERVAL = 15
BACKEND_URLS = ["http://127.0.0.1:8000", "http://localhost:8000"]


def find_working_backend():
    """Try to connect to backend using multiple URLs and return latency."""
    for url in BACKEND_URLS:
        start = time.time()
        try:
            response = requests.get(f"{url}/health", timeout=10, verify=False)
            response.raise_for_status()
            latency_ms = int((time.time() - start) * 1000)
            return url, latency_ms
        except Exception:
            continue
    return None, None


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    """Fetch detection data from backend."""
    try:
        response = requests.get(f"{url}/detect", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend not reachable")
        return None


def fetch_data(url):
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))


@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    """Fetch explanation data from backend."""
    try:
        response = requests.get(f"{url}/explain", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.warning("Could not fetch explain data")
        return None


def fetch_explain_data(url):
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))


st.title("🛡️ DcoY Cyber Defense Dashboard")
st.markdown('<hr class="top-divider" />', unsafe_allow_html=True)

api_base, latency_ms = find_working_backend()
if not api_base:
    st.error("Backend not reachable")
    st.stop()

st.markdown(
    f"""
<div class="status-row">
  <span class="status-pill live">LIVE</span>
  <span class="status-pill secure">SECURE</span>
  <span class="status-pill latency">LATENCY: {latency_ms}ms</span>
</div>
""",
    unsafe_allow_html=True,
)

data = fetch_data(api_base)
if not data:
    st.stop()

if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([row for row in explain_rows if row.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

# 1) Overview Metrics
st.markdown('<h3 class="section-title">Overview Metrics</h3>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="metric-box"><h3>Total Events</h3><h2 class="green">{total_events}</h2></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-box"><h3>High Risk</h3><h2 class="purple">{high_risk_count}</h2></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-box"><h3>Active Threats</h3><h2 class="green">{active_threats}</h2></div>',
        unsafe_allow_html=True,
    )
st.markdown("<br>", unsafe_allow_html=True)

# 2) Attack Map
st.markdown('<h3 class="section-title">🌍 Live Attack Map</h3>', unsafe_allow_html=True)
locations = []
for row in explain_rows:
    loc = row.get("location", {})
    lat = loc.get("lat")
    lon = loc.get("lon")
    if lat is not None and lon is not None:
        locations.append(
            {
                "latitude": lat,
                "longitude": lon,
                "ip": row.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown"),
            }
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
if locations:
    map_df = pd.DataFrame(locations)
    map_col1, map_col2 = st.columns([3, 1])
    with map_col1:
        st.map(map_df[["latitude", "longitude"]], width='stretch')
    with map_col2:
        country_df = (
            map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )
        st.dataframe(country_df, width='stretch', hide_index=True)
else:
    st.info("No geolocation data available")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 3) Attack Analysis
st.markdown('<h3 class="section-title">📊 Attack Analysis</h3>', unsafe_allow_html=True)
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    summary = data.get("attack_summary", {})
    if summary:
        attack_df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        fig = px.bar(attack_df, x="Type", y="Count", color_discrete_sequence=["#2CFF05"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No attack analysis data")
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    response_summary = data.get("response_summary", {})
    if response_summary:
        response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
        fig = px.bar(response_df, x="Honeypot", y="Count", color_discrete_sequence=["#BF00FF"])
        fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="#FFFFFF")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#BF00FF")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No honeypot response data")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 4) High Risk Threats
st.markdown('<h3 class="section-title">🚨 High Risk Threats</h3>', unsafe_allow_html=True)
high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
if high_risk:
    st.dataframe(pd.DataFrame(high_risk), width='stretch', hide_index=True)
else:
    st.success("No high-risk threats detected")
st.markdown("<br>", unsafe_allow_html=True)

# 5) Detailed Logs
st.markdown('<h3 class="section-title">📋 Detailed Logs</h3>', unsafe_allow_html=True)
log_source = explain_rows if explain_rows else detect_rows
if log_source:
    detailed_df = pd.DataFrame(log_source)
    preferred_columns = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    existing_columns = [col for col in preferred_columns if col in detailed_df.columns]
    if existing_columns:
        detailed_df = detailed_df[existing_columns]
    st.dataframe(detailed_df, width='stretch', hide_index=True)
else:
    st.info("No log data available")
st.markdown("<br>", unsafe_allow_html=True)

# 6) AI Explanations
st.markdown('<h3 class="section-title">🧠 AI Explanations</h3>', unsafe_allow_html=True)
if explain_rows:
    for row in explain_rows:
        with st.expander(f"IP: {row.get('ip', 'Unknown')} | Risk: {row.get('risk_level', 'unknown')}"):
            st.write(row.get("explanation", "No explanation available"))
else:
    st.info("No AI explanations available")
"""DcoY Streamlit Dashboard."""
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
body {
    background-color: #000000;
    color: #FFFFFF;
}

.stApp {
    background-color: #000000;
    color: #FFFFFF;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background-color: #2D2D2D;
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border: 1px solid #BF00FF;
}

.green {
    color: #2CFF05;
    font-weight: bold;
}

.purple {
    color: #BF00FF;
    font-weight: bold;
}

.metric-box {
    background-color: #2D2D2D;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    border: 1px solid #BF00FF;
}

.metric-box h2,
.metric-box h3 {
    margin: 0;
}

.metric-box h3 {
    margin-bottom: 0.5rem;
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #FFFFFF;
}

/* Native dataframe styling */
div[data-testid="stDataFrame"] {
    background-color: #2D2D2D;
    border: 1px solid #BF00FF;
    border-radius: 10px;
    padding: 0.25rem;
}

div[data-testid="stDataFrame"] [role="columnheader"] {
    background-color: #000000 !important;
    color: #2CFF05 !important;
    font-weight: 700 !important;
}

div[data-testid="stDataFrame"] [role="gridcell"] {
    background-color: #2D2D2D !important;
    color: #FFFFFF !important;
}

/* Expander styling */
div[data-testid="stExpander"] {
    background-color: #2D2D2D;
    border: 1px solid #BF00FF;
    border-radius: 10px;
    margin-bottom: 0.5rem;
}

div[data-testid="stExpander"] details summary {
    color: #2CFF05 !important;
    font-weight: 700;
}

/* Alert/callout styling */
div[data-testid="stAlert"] {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #BF00FF;
}

/* Keep interactive widgets consistent */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
input,
textarea {
    background-color: #2D2D2D !important;
    color: #FFFFFF !important;
    border-color: #BF00FF !important;
}

.stButton > button {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: 1px solid #BF00FF;
    border-radius: 8px;
}

.stButton > button:hover {
    border-color: #2CFF05;
    color: #2CFF05;
}

hr {
    border: 1px solid #BF00FF;
}
</style>
""",
    unsafe_allow_html=True,
)

# Auto-refresh every 2 seconds
ensure_autorefresh_once()

REFRESH_INTERVAL = 2
EXPLAIN_REFRESH_INTERVAL = 15

BACKEND_URLS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]


def find_working_backend():
    """Try to connect to backend using multiple URLs."""
    for url in BACKEND_URLS:
        try:
            r = requests.get(f"{url}/health", timeout=10, verify=False)
            r.raise_for_status()
            return url
        except Exception:
            continue
    return None


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    """Fetch detection data from backend."""
    try:
        response = requests.get(f"{url}/detect", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend not reachable")
        return None


def fetch_data(url):
    """Fetch detection data with cache key rotation."""
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))


@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    """Fetch explain data with geolocation from backend."""
    try:
        response = requests.get(f"{url}/explain", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.warning("Could not fetch explain data")
        return None


def fetch_explain_data(url):
    """Fetch explain data with cache key rotation."""
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))


st.title("🛡️ DcoY Cyber Defense Dashboard")
st.markdown("<hr>", unsafe_allow_html=True)

api_base = find_working_backend()
if not api_base:
    st.error("Backend not reachable")
    st.stop()

data = fetch_data(api_base)
if not data:
    st.stop()

if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([row for row in explain_rows if row.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

# 1) Overview Metrics
st.markdown("### Overview Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="metric-box"><h3>Total Events</h3><h2 class="green">{total_events}</h2></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-box"><h3>High Risk</h3><h2 class="purple">{high_risk_count}</h2></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-box"><h3>Active Threats</h3><h2 class="green">{active_threats}</h2></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 2) Attack Map
st.markdown("### 🌍 Live Attack Map")
locations = []
for row in explain_rows:
    loc = row.get("location", {})
    lat = loc.get("lat")
    lon = loc.get("lon")
    if lat is not None and lon is not None:
        locations.append(
            {
                "latitude": lat,
                "longitude": lon,
                "ip": row.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown"),
            }
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
if locations:
    map_df = pd.DataFrame(locations)
    map_col1, map_col2 = st.columns([3, 1])
    with map_col1:
        st.map(map_df[["latitude", "longitude"]], width='stretch')
    with map_col2:
        country_df = (
            map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )
        st.dataframe(country_df, width='stretch', hide_index=True)
else:
    st.info("No geolocation data available")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3) Attack Analysis (charts)
st.markdown("### 📊 Attack Analysis")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    summary = data.get("attack_summary", {})
    if summary:
        attack_df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        fig = px.bar(attack_df, x="Type", y="Count", color_discrete_sequence=["#2CFF05"])
        fig.update_layout(
            paper_bgcolor="#2D2D2D",
            plot_bgcolor="#2D2D2D",
            font_color="#FFFFFF",
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No attack analysis data")
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    response_summary = data.get("response_summary", {})
    if response_summary:
        response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
        fig = px.bar(response_df, x="Honeypot", y="Count", color_discrete_sequence=["#BF00FF"])
        fig.update_layout(
            paper_bgcolor="#2D2D2D",
            plot_bgcolor="#2D2D2D",
            font_color="#FFFFFF",
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No honeypot response data")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4) High Risk Threats
st.markdown("### 🚨 High Risk Threats")
high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
if high_risk:
    st.dataframe(pd.DataFrame(high_risk), width='stretch', hide_index=True)
else:
    st.success("No high-risk threats detected")

st.markdown("<br>", unsafe_allow_html=True)

# 5) Detailed Logs
st.markdown("### 📋 Detailed Logs")
log_source = explain_rows if explain_rows else detect_rows
if log_source:
    detailed_df = pd.DataFrame(log_source)
    preferred_columns = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    existing_columns = [col for col in preferred_columns if col in detailed_df.columns]
    if existing_columns:
        detailed_df = detailed_df[existing_columns]
    st.dataframe(detailed_df, width='stretch', hide_index=True)
else:
    st.info("No log data available")

st.markdown("<br>", unsafe_allow_html=True)

# 6) AI Explanations
st.markdown("### 🧠 AI Explanations")
if explain_rows:
    for row in explain_rows:
        with st.expander(f"IP: {row.get('ip', 'Unknown')} | Risk: {row.get('risk_level', 'unknown')}"):
            st.write(row.get("explanation", "No explanation available"))
else:
    st.info("No AI explanations available")
"""DcoY Streamlit Dashboard"""
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib3
from streamlit_autorefresh import st_autorefresh

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
body {
    background-color: #000000;
    color: #FFFFFF;
}

.stApp {
    background-color: #000000;
    color: #FFFFFF;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background-color: #2D2D2D;
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.green {
    color: #2CFF05;
    font-weight: bold;
}

.purple {
    color: #BF00FF;
    font-weight: bold;
}

.metric-box {
    background-color: #2D2D2D;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    border: 1px solid #BF00FF;
}

.metric-box h2,
.metric-box h3 {
    margin: 0;
}

.metric-box h3 {
    margin-bottom: 0.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# Auto-refresh every 2 seconds
ensure_autorefresh_once()

REFRESH_INTERVAL = 2
EXPLAIN_REFRESH_INTERVAL = 15

BACKEND_URLS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]


def find_working_backend():
    """Try to connect to backend using multiple URLs."""
    for url in BACKEND_URLS:
        try:
            r = requests.get(f"{url}/health", timeout=10, verify=False)
            r.raise_for_status()
            return url
        except Exception:
            continue
    return None


@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    """Fetch detection data from backend."""
    try:
        response = requests.get(f"{url}/detect", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend not reachable")
        return None


def fetch_data(url):
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))


@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    """Fetch explain data with geolocation from backend."""
    try:
        response = requests.get(f"{url}/explain", timeout=60, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.warning("Could not fetch explain data")
        return None


def fetch_explain_data(url):
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))


st.title("🛡️ DcoY Cyber Defense Dashboard")
st.markdown("<hr>", unsafe_allow_html=True)

api_base = find_working_backend()
if not api_base:
    st.error("Backend not reachable")
    st.stop()

data = fetch_data(api_base)
if not data:
    st.stop()

if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(api_base)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data or {}

detect_rows = data.get("data", [])
explain_rows = explain_data.get("data", [])

total_events = data.get("total_records", len(detect_rows))
high_risk_count = len([row for row in explain_rows if row.get("risk_level") == "high"])
active_threats = data.get("anomalies_detected", 0)

# 1) Overview Metrics
st.markdown("### Overview Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="metric-box"><h3>Total Events</h3><h2 class="green">{total_events}</h2></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-box"><h3>High Risk</h3><h2 class="purple">{high_risk_count}</h2></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-box"><h3>Active Threats</h3><h2 class="green">{active_threats}</h2></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 2) Attack Map
st.markdown("### 🌍 Live Attack Map")

locations = []
for row in explain_rows:
    loc = row.get("location", {})
    lat = loc.get("lat")
    lon = loc.get("lon")
    if lat is not None and lon is not None:
        locations.append(
            {
                "latitude": lat,
                "longitude": lon,
                "ip": row.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown"),
            }
        )

st.markdown('<div class="card">', unsafe_allow_html=True)
if locations:
    map_df = pd.DataFrame(locations)
    map_col1, map_col2 = st.columns([3, 1])
    with map_col1:
        st.map(map_df[["latitude", "longitude"]], width='stretch')
    with map_col2:
        country_df = (
            map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
        )
        st.dataframe(country_df, width='stretch', hide_index=True)
else:
    st.info("No geolocation data available")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3) Attack Analysis (charts)
st.markdown("### 📊 Attack Analysis")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    summary = data.get("attack_summary", {})
    if summary:
        attack_df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        fig = px.bar(attack_df, x="Type", y="Count", color_discrete_sequence=["#2CFF05"])
        fig.update_layout(
            paper_bgcolor="#2D2D2D",
            plot_bgcolor="#2D2D2D",
            font_color="#FFFFFF",
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No attack analysis data")
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    response_summary = data.get("response_summary", {})
    if response_summary:
        response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
        fig = px.bar(response_df, x="Honeypot", y="Count", color_discrete_sequence=["#BF00FF"])
        fig.update_layout(
            paper_bgcolor="#2D2D2D",
            plot_bgcolor="#2D2D2D",
            font_color="#FFFFFF",
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No honeypot response data")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4) High Risk Threats
st.markdown("### 🚨 High Risk Threats")
high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
if high_risk:
    high_risk_df = pd.DataFrame(high_risk)
    st.dataframe(high_risk_df, width='stretch', hide_index=True)
else:
    st.success("No high-risk threats detected")

st.markdown("<br>", unsafe_allow_html=True)

# 5) Detailed Logs
st.markdown("### 📋 Detailed Logs")
log_source = explain_rows if explain_rows else detect_rows
if log_source:
    detailed_df = pd.DataFrame(log_source)
    preferred_columns = ["ip", "risk_level", "attacker_profile", "response_action_final", "honeypot"]
    existing_columns = [col for col in preferred_columns if col in detailed_df.columns]
    if existing_columns:
        detailed_df = detailed_df[existing_columns]
    st.dataframe(detailed_df, width='stretch', hide_index=True)
else:
    st.info("No log data available")

st.markdown("<br>", unsafe_allow_html=True)

# 6) AI Explanations
st.markdown("### 🧠 AI Explanations")
if explain_rows:
    for row in explain_rows:
        with st.expander(f"IP: {row.get('ip', 'Unknown')} | Risk: {row.get('risk_level', 'unknown')}"):
            st.write(row.get("explanation", "No explanation available"))
else:
    st.info("No AI explanations available")
"""DcoY Streamlit Dashboard"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import sys
import time
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

# Auto-refresh configuration
REFRESH_INTERVAL = 2  # seconds
EXPLAIN_REFRESH_INTERVAL = 15  # seconds

# Multiple backend URLs to try
BACKEND_URLS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

API_BASE = None  # Will be set dynamically

# Initialize session state for timing
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

def find_working_backend():
    """Try to connect to backend using multiple URLs with detailed logging"""
    st.write("🔍 **Searching for backend...**")
    
    for url in BACKEND_URLS:
        try:
            st.write(f"  Trying: {url}")
            r = requests.get(f"{url}/health", timeout=30, verify=False)
            r.raise_for_status()
            st.success(f"  ✅ Connected to: {url}")
            return url
        except requests.exceptions.ConnectionError as e:
            st.write(f"  ❌ Connection refused")
        except requests.exceptions.Timeout:
            st.write(f"  ❌ Timeout (30s)")
        except Exception as e:
            st.write(f"  ❌ {type(e).__name__}")
    
    return None

def risk_color(level):
    if level == "high": return "🔴 HIGH"
    if level == "medium": return "🟠 MEDIUM"
    return "🟢 LOW"

@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data_cached(url, cache_key):
    """Fetch detection data from backend - fresh on cache key change"""
    try:
        r = requests.get(f"{url}/detect", timeout=60, verify=False)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Backend /detect timeout (60s) - server overloaded or unreachable")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to backend - ensure backend is running on port 8000")
        return None
    except Exception as e:
        st.error(f"Error fetching data: {type(e).__name__}: {str(e)}")
        return None

def fetch_data(url):
    """Fetch detection data - wrapper for non-cached version"""
    return fetch_data_cached(url, int(time.time() // REFRESH_INTERVAL))

@st.cache_data(ttl=EXPLAIN_REFRESH_INTERVAL)
def fetch_explain_cached(url, cache_key):
    """Fetch explanation data with geolocation from backend"""
    try:
        r = requests.get(f"{url}/explain", timeout=60, verify=False)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        st.warning("⏱️ Backend request timeout - server may be slow or unreachable")
        return None
    except requests.exceptions.ConnectionError:
        st.warning("🔌 Cannot connect to backend - ensure backend is running on port 8000")
        return None
    except Exception as e:
        st.warning(f"Could not fetch explain data: {type(e).__name__}")
        return None

def fetch_explain_data(url):
    """Fetch explain data - wrapper with cache busting"""
    return fetch_explain_cached(url, int(time.time() // EXPLAIN_REFRESH_INTERVAL))

# ===== MAIN PAGE =====
st.title("🛡️ DcoY AI Cyber Defense System")
st.caption("Real-time Threat Detection, Intelligent Response, and Explainable AI")

# Sidebar refresh indicator
with st.sidebar:
    st.markdown("### 🔄 Live Dashboard")
    st.markdown(f"Auto-refresh: **Every {REFRESH_INTERVAL} seconds**")
    
    # Force refresh button
    if st.button("🔁 Force Refresh Now"):
        st.rerun()

# Auto-refresh every N seconds using time-based check
current_time = time.time()
time_since_refresh = current_time - st.session_state.last_refresh

if time_since_refresh >= REFRESH_INTERVAL:
    st.session_state.last_refresh = current_time

# Find backend
found_url = find_working_backend()

if not found_url:
    st.error("❌ **Backend not found!**")
    st.error("**Error:** Cannot connect to backend on any of these URLs:")
    for url in BACKEND_URLS:
        st.code(url)
    
    st.info("**Fix:**\n"
            "1. **Start backend with correct host:**\n"
            "   ```bash\n"
            "   cd backend\n"
            "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload\n"
            "   ```\n"
            "2. Wait for message: `Uvicorn running on http://0.0.0.0:8000`\n"
            "3. Then refresh this page (F5)")
    st.stop()

API_BASE = found_url
st.success(f"🟢 System Active: Connected to {API_BASE}")
st.divider()

# Fetch and display data - cache key changes every 2 seconds for auto-refresh
data = fetch_data(API_BASE)
if not data:
    st.stop()

# --- Overview ---
st.header("Overview")
col1, col2 = st.columns(2)
col1.metric("Total Records", data.get("total_records", 0))
col2.metric("Anomalies Detected", data.get("anomalies_detected", 0))
st.divider()

# --- Attack Analysis ---
st.header("Attack Analysis & Honeypot Response")
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Attack Distribution")
    summary = data.get("attack_summary", {})
    if summary:
        df = pd.DataFrame(list(summary.items()), columns=["Type", "Count"])
        st.plotly_chart(px.bar(df, x="Type", y="Count", title="Attack Types"), width="stretch")
    else:
        st.info("No attack data")

with c2:
    st.subheader("🛠️ Honeypot Response")
    summary = data.get("response_summary", {})
    if summary:
        df = pd.DataFrame(list(summary.items()), columns=["Honeypot", "Count"])
        st.plotly_chart(px.bar(df, x="Honeypot", y="Count", title="Response Actions"), width="stretch")
    else:
        st.info("No response data")

st.divider()

# --- Live Attack Map ---
st.header("🌍 Live Attack Map")

# Fetch explain data for geolocation
if "last_explain_data" not in st.session_state:
    st.session_state.last_explain_data = None

fresh_explain_data = fetch_explain_data(API_BASE)
if fresh_explain_data:
    st.session_state.last_explain_data = fresh_explain_data
explain_data = st.session_state.last_explain_data

if explain_data:
    explain_rows = explain_data.get("data", [])
    
    # Extract location data for mapping
    locations = []
    for row in explain_rows:
        loc = row.get("location", {})
        if loc.get("lat") and loc.get("lon"):
            locations.append({
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "ip": loc.get("ip", "Unknown"),
                "country": loc.get("country", "Unknown"),
                "city": loc.get("city", "Unknown")
            })
    
    if locations:
        # Convert to DataFrame for Streamlit map
        map_df = pd.DataFrame(locations)
        
        # Show map with attack locations
        col1, col2 = st.columns([3, 1])
        with col1:
            st.map(map_df[["latitude", "longitude"]], zoom=2)
        
        with col2:
            st.markdown("**Attack Origins**")
            origin_summary = map_df.groupby("country").size().reset_index(name="Count")
            st.dataframe(origin_summary.sort_values("Count", ascending=False), width="stretch", hide_index=True)
    else:
        st.info("📍 No geolocation data available yet. Wait for more threats to be detected.")
else:
    st.info("📍 Geolocation data loading...")

st.divider()

# --- High-Risk Threats ---
st.header("🚨 High-Risk Threats Detected")

if explain_data:
    explain_rows = explain_data.get("data", [])
    high_risk_threats = [row for row in explain_rows if row.get("risk_level") == "high"]
    
    if high_risk_threats:
        st.markdown(f"### 🔴 **{len(high_risk_threats)} High-Risk Event(s)**")
        
        for idx, threat in enumerate(high_risk_threats, 1):
            with st.expander(f"🚨 Alert #{idx}: {threat.get('ip', 'Unknown')} - {threat.get('attack_type', 'Unknown')}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Risk Level", "🔴 HIGH", delta="Critical")
                with col2:
                    location = threat.get("location", {})
                    st.metric("Location", f"{location.get('country', 'Unknown')}", location.get("city", "N/A"))
                with col3:
                    st.metric("Risk Score", f"{threat.get('risk_score', 0):.2f}", "out of 1.0")
                
                st.markdown("---")
                
                # Threat details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Threat Details:**")
                    st.write(f"- IP: `{threat.get('ip', 'Unknown')}`")
                    st.write(f"- Attack Type: {threat.get('attack_type', 'Unknown')}")
                    st.write(f"- Failed Logins: {threat.get('failed_logins', 0)}")
                    st.write(f"- Port Attempts: {threat.get('port_attempts', 0)}")
                
                with col2:
                    st.markdown(f"**AI Analysis:**")
                    st.write(threat.get("explanation", "No explanation available"))
                
                # Response action
                st.markdown("---")
                st.info(f"**Response Action:** {threat.get('response_action', 'No action taken')}")
    else:
        st.success("✅ **No high-risk threats detected!** System is secure.")
else:
    st.info("Loading threat analysis...")

st.divider()
rows = data.get("data", [])
if rows:
    try:
        df = pd.DataFrame(rows)
        
        # Ensure required columns exist
        if "is_anomaly" not in df.columns:
            df["is_anomaly"] = 0  # Default to 0 (not anomaly)
        
        # Show critical threats
        st.subheader("🚨 Critical Threats")
        high_risk = df[df["is_anomaly"] == 1] if "is_anomaly" in df.columns else pd.DataFrame()
        
        if high_risk.empty:
            st.success("✅ No critical threats detected")
        else:
            for _, row in high_risk.iterrows():
                st.error(
                    f"🚨 {row.get('ip', 'Unknown')} - {row.get('attack_type', 'Unknown')} | "
                    f"Failed Logins: {row.get('failed_logins', 0)} | Ports: {row.get('port_attempts', 0)}"
                )
        
        # All logs table
        st.subheader("📋 All Logs")
        st.dataframe(df, width="stretch", hide_index=True)
    
    except Exception as e:
        st.error(f"❌ Error processing logs: {str(e)}")
        st.write("Raw data:", rows[:3] if len(rows) > 3 else rows)
else:
    st.warning("No log data available")

# Auto-rerun mechanism for live updates
st.markdown("---")
st.caption(f"⏱️ Last update: {time.strftime('%H:%M:%S')}")

# Use a placeholder to trigger reruns
import threading

def auto_refresh_trigger():
    """Background thread to trigger page reruns every REFRESH_INTERVAL seconds"""
    while True:
        time.sleep(REFRESH_INTERVAL)
        # Note: This won't directly work in Streamlit, so we'll use the cache-busting approach above instead
        pass

# The cache busting happens via the cache_key variable above
# which changes every REFRESH_INTERVAL seconds due to: int(current_time // REFRESH_INTERVAL)
