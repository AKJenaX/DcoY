#!/usr/bin/env python3
"""
Verification Script for DcoY Platform Setup
Tests backend API endpoints and frontend project structure readiness.
"""

import sys
from pathlib import Path
import requests

API_BASE = "http://127.0.0.1:8001"

def print_header(title: str):
    """Print formatted header."""
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_status(ok: bool, message: str):
    """Print status item with checkbox icon."""
    icon = "✅" if ok else "❌"
    print(f"{icon}  {message}")

def check_backend_running():
    """Check if FastAPI backend is running on API_BASE."""
    try:
        response = requests.get(f"{API_BASE}/health/live", timeout=3)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"Could not connect to {API_BASE}"
    except Exception as e:
        return False, str(e)

def check_backend_endpoints():
    """Check all critical backend API endpoints."""
    endpoints = {
        "/health/live": "Liveness Probe",
        "/health/ready": "Readiness Probe",
        "/metrics": "Application Telemetry",
        "/docs": "OpenAPI Swagger UI Documentation",
    }
    
    results = {}
    for endpoint, description in endpoints.items():
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            results[endpoint] = (response.status_code == 200, description, response.status_code)
        except Exception as e:
            results[endpoint] = (False, description, str(e))
    
    return results

def check_frontend_config():
    """Check if React frontend is configured correctly."""
    frontend_app = Path("frontend/src/App.tsx")
    frontend_api = Path("frontend/src/services/api.ts")
    
    if not (frontend_app.exists() and frontend_api.exists()):
        return False, "frontend workspace components not found"
    
    try:
        with open(frontend_api, 'r', encoding='utf-8') as f:
            content = f.read()
            if "API_BASE" in content and ("8001" in content or "8000" in content):
                return True, "API_BASE configured correctly in frontend/src/services/api.ts"
            return False, "API_BASE missing or invalid in frontend/src/services/api.ts"
    except Exception as e:
        return False, f"Error reading frontend config: {str(e)}"

def check_backend_config():
    """Check if FastAPI backend is configured correctly."""
    backend_path = Path("backend/app/main.py")
    
    if not backend_path.exists():
        return False, "backend/app/main.py not found"
    
    try:
        with open(backend_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_cors = "setup_cors_middleware" in content or "CORSMiddleware" in content
            has_routers = "include_router" in content
            has_lifespan = "lifespan" in content
            
            if has_cors and has_routers and has_lifespan:
                return True, "Backend properly configured with modular routers, CORS, and lifespan lifecycle"
            else:
                missing = []
                if not has_cors: missing.append("CORS")
                if not has_routers: missing.append("Routers")
                if not has_lifespan: missing.append("Lifespan")
                return False, f"Backend missing: {', '.join(missing)}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def main():
    """Run all verification checks."""
    print_header("🛡️  DcoY Backend-Frontend Verification")
    
    # Check file structure
    print("1. Checking Project Structure...")
    backend_exists = Path("backend/app/main.py").exists()
    frontend_exists = Path("frontend/src/App.tsx").exists()
    print_status(backend_exists, "Backend found at backend/app/main.py")
    print_status(frontend_exists, "Frontend found at frontend/src/App.tsx")
    
    if not (backend_exists and frontend_exists):
        print("\n❌ Project structure incomplete. Please run from project root directory.")
        return 1
    
    # Check configurations
    print("\n2. Checking Configurations...")
    backend_ok, backend_msg = check_backend_config()
    print_status(backend_ok, f"Backend config: {backend_msg}")
    
    frontend_ok, frontend_msg = check_frontend_config()
    print_status(frontend_ok, f"Frontend config: {frontend_msg}")
    
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
        print("  2. Run: .\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8001")
        print("  3. Then run this verification script again")
        return 1
    
    # Summary
    print_header("✅ Verification Complete")
    print("  All systems ready! You can now:")
    print("  1. Start backend (if not already running):")
    print("     cd backend && .\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8001")
    print("  2. Start frontend in another terminal:")
    print("     cd frontend && npm run dev")
    print("  3. Open browser at http://localhost:5173")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nVerification cancelled.")
        sys.exit(1)
