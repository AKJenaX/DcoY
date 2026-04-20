"""DcoY Streamlit Dashboard"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import sys

st.set_page_config(page_title="DcoY AI Defense", page_icon="🛡️", layout="wide")

# Multiple backend URLs to try
BACKEND_URLS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

API_BASE = None  # Will be set dynamically

def find_working_backend():
    """Try to connect to backend using multiple URLs with detailed logging"""
    st.write("🔍 **Searching for backend...**")
    
    for url in BACKEND_URLS:
        try:
            st.write(f"  Trying: {url}")
            r = requests.get(f"{url}/health", timeout=10, verify=False)  # Increased timeout to 10s
            r.raise_for_status()
            st.success(f"  ✅ Connected to: {url}")
            return url
        except requests.exceptions.ConnectionError as e:
            st.write(f"  ❌ Connection refused")
        except requests.exceptions.Timeout:
            st.write(f"  ❌ Timeout (10s)")
        except Exception as e:
            st.write(f"  ❌ {type(e).__name__}")
    
    return None

def risk_color(level):
    if level == "high": return "🔴 HIGH"
    if level == "medium": return "🟠 MEDIUM"
    return "🟢 LOW"

def fetch_data(url):
    """Fetch detection data from backend"""
    try:
        r = requests.get(f"{url}/detect", timeout=15, verify=False)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching data: {type(e).__name__}: {str(e)}")
        return None

# ===== MAIN PAGE =====
st.title("🛡️ DcoY AI Cyber Defense System")
st.caption("Real-time Threat Detection, Intelligent Response, and Explainable AI")

# Find backend
with st.spinner("🔌 Finding backend service..."):
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

# Fetch and display data
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
        st.plotly_chart(px.bar(df, x="Type", y="Count", title="Attack Types"), use_container_width=True)
    else:
        st.info("No attack data")

with c2:
    st.subheader("🛠️ Honeypot Response")
    summary = data.get("response_summary", {})
    if summary:
        df = pd.DataFrame(list(summary.items()), columns=["Honeypot", "Count"])
        st.plotly_chart(px.bar(df, x="Honeypot", y="Count", title="Response Actions"), use_container_width=True)
    else:
        st.info("No response data")

st.divider()

# --- Threat Logs ---
st.header("Threat Logs")
rows = data.get("data", [])
if rows:
    df = pd.DataFrame(rows)
    
    # Show critical threats
    st.subheader("🚨 Critical Threats")
    high_risk = df[df["is_anomaly"] == 1]
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
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No log data available")
