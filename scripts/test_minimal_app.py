"""
Minimal test app - no complex code, just test connectivity
"""
import streamlit as st

st.set_page_config(page_title="Connection Test", layout="wide")
st.title("Connection Test")

# Import here to catch errors
try:
    import requests
    import socket
    st.success("✓ Libraries imported successfully")
except Exception as e:
    st.error(f"✗ Import failed: {str(e)}")
    st.stop()

# Test 1: Socket
st.write("### Test 1: Socket Connection")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("127.0.0.1", 8000))
    sock.close()
    if result == 0:
        st.success("✓ Port 8000 is open")
    else:
        st.error(f"✗ Cannot connect to port 8000 (errno {result})")
except Exception as e:
    st.error(f"✗ Socket test failed: {str(e)}")

# Test 2: Direct HTTP request
st.write("### Test 2: HTTP Request to http://127.0.0.1:8000/health")
try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    st.success(f"✓ HTTP {response.status_code}")
    st.json(response.json())
except Exception as e:
    st.error(f"✗ Failed: {type(e).__name__}: {str(e)}")

# Test 3: Try with localhost
st.write("### Test 3: HTTP Request to http://localhost:8000/health")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    st.success(f"✓ HTTP {response.status_code}")
    st.json(response.json())
except Exception as e:
    st.error(f"✗ Failed: {type(e).__name__}: {str(e)}")

st.divider()
st.write("**If you see ✓ in any test above, the backend is reachable!**")
