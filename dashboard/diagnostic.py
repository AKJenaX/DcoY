"""
Simplified diagnostic app to test backend connectivity.
Run this to see what's actually happening.
"""

import streamlit as st
import requests
import socket

st.set_page_config(page_title="DcoY Diagnostic", layout="wide")
st.title("🔧 DcoY Backend Diagnostic")

st.write("### Network Information")
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    st.write(f"**Hostname:** `{hostname}`")
    st.write(f"**Local IP:** `{local_ip}`")
except:
    st.write("Could not get network info")

# Try multiple URL formats
urls_to_test = [
    "http://127.0.0.1:8000/health",
    "http://localhost:8000/health",
    "http://0.0.0.0:8000/health",
]

st.divider()
st.write("### Testing Different URL Formats")

for url in urls_to_test:
    st.write(f"\n**Testing:** `{url}`")
    try:
        response = requests.get(url, timeout=5)
        st.success(f"✓ Connected! Status: {response.status_code}")
        st.write(f"Response: {response.json()}")
        break  # Found working URL
    except requests.exceptions.ConnectionError as e:
        st.error(f"✗ Connection refused")
    except requests.exceptions.Timeout as e:
        st.error(f"✗ Timeout")
    except Exception as e:
        st.error(f"✗ {type(e).__name__}: {str(e)}")

