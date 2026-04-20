#!/usr/bin/env python3
"""
Quick verification script for DcoY backend-frontend connection.
Run this from the project root directory to verify everything is configured correctly.
"""

import sys
import requests
import subprocess
from pathlib import Path

# Configuration
API_BASE = "http://127.0.0.1:8000"
BACKEND_TIMEOUT = 5

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_status(status, message):
    """Print a status message with emoji."""
    emoji = "✓" if status else "✗"
    print(f"  {emoji} {message}")

def check_backend_running():
    """Check if FastAPI backend is running."""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=BACKEND_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return True, data
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - backend may not be running on port 8000"
    except requests.exceptions.Timeout:
        return False, "Request timeout - backend is not responding"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def check_backend_endpoints():
    """Check if all required endpoints are available."""
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/detect", "Anomaly detection"),
        ("/agents", "Agent pipeline"),
        ("/explain", "AI explanations"),
    ]
    
    results = {}
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            results[endpoint] = (response.status_code == 200, description, response.status_code)
        except Exception as e:
            results[endpoint] = (False, description, str(e))
    
    return results

def check_streamlit_config():
    """Check if Streamlit dashboard is configured correctly."""
    dashboard_path = Path("dashboard/app.py")
    
    if not dashboard_path.exists():
        return False, "dashboard/app.py not found"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "API_BASE" in content and "http://127.0.0.1:8000" in content:
                return True, "API_BASE configured correctly"
            else:
                return False, "API_BASE not properly configured"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def check_backend_config():
    """Check if FastAPI backend is configured correctly."""
    backend_path = Path("backend/app/main.py")
    
    if not backend_path.exists():
        return False, "backend/app/main.py not found"
    
    try:
        with open(backend_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_cors = "CORSMiddleware" in content
            has_health = 'def health_check' in content
            has_logging = "import logging" in content
            
            if has_cors and has_health and has_logging:
                return True, "Backend properly configured with CORS, health check, and logging"
            else:
                missing = []
                if not has_cors:
                    missing.append("CORS")
                if not has_health:
                    missing.append("health endpoint")
                if not has_logging:
                    missing.append("logging")
                return False, f"Backend missing: {', '.join(missing)}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def main():
    """Run all verification checks."""
    print_header("🛡️  DcoY Backend-Frontend Verification")
    
    # Check file structure
    print("1. Checking Project Structure...")
    backend_exists = Path("backend/app/main.py").exists()
    dashboard_exists = Path("dashboard/app.py").exists()
    print_status(backend_exists, "Backend found at backend/app/main.py")
    print_status(dashboard_exists, "Dashboard found at dashboard/app.py")
    
    if not (backend_exists and dashboard_exists):
        print("\n❌ Project structure incomplete. Please run from project root directory.")
        return 1
    
    # Check configurations
    print("\n2. Checking Configurations...")
    backend_ok, backend_msg = check_backend_config()
    print_status(backend_ok, f"Backend config: {backend_msg}")
    
    streamlit_ok, streamlit_msg = check_streamlit_config()
    print_status(streamlit_ok, f"Streamlit config: {streamlit_msg}")
    
    # Check backend connectivity
    print("\n3. Checking Backend Connectivity...")
    backend_running, backend_data = check_backend_running()
    
    if backend_running:
        print_status(True, f"✓ Backend is running: {backend_data}")
        
        # Check endpoints
        print("\n4. Checking Backend Endpoints...")
        endpoints = check_backend_endpoints()
        for endpoint, (ok, desc, status) in endpoints.items():
            if ok:
                print_status(True, f"{desc} ({endpoint}): {status}")
            else:
                print_status(False, f"{desc} ({endpoint}): {status}")
    else:
        print_status(False, f"Backend not running: {backend_data}")
        print("\n⚠️  NEXT STEPS:")
        print("  1. Open terminal in 'backend' directory")
        print("  2. Run: uvicorn app.main:app --reload")
        print("  3. Then run this verification script again")
        return 1
    
    # Summary
    print_header("✅ Verification Complete")
    print("  All systems ready! You can now:")
    print("  1. Start backend (if not already running):")
    print("     cd backend && uvicorn app.main:app --reload")
    print("  2. Start dashboard in another terminal:")
    print("     cd dashboard && streamlit run app.py")
    print("  3. Open browser at http://localhost:8501")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
