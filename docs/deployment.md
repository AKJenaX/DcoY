# DcoY Deployment Guide

This document describes how to deploy the DcoY platform inside production or local testing environments using Docker or native scripts.

---

## 🐳 1. Docker Compose Deploy (Recommended)

DcoY provides a default `docker-compose.yml` config in the project root to spin up the FastAPI service and modular dashboard jointly.

### Launch Containers
Run the following command from the root directory:
```bash
docker-compose up --build -d
```

This starts:
1. **`backend`**: FastAPI listener mapped to port `8000`.
2. **`dashboard`**: Streamlit interface mapped to port `8501`.

---

## 💻 2. Native Windows/Linux Deployment

### Windows Deployment Script
A helper script `run_production.bat` is located in `backend/` to start the backend with environment defaults:
```cmd
cd backend
run_production.bat
```

### Linux Deployment Script
A script `run_production.sh` is provided in `backend/` to bind uvicorn workers cleanly:
```bash
cd backend
chmod +x run_production.sh
./run_production.sh
```

---

## 📋 3. Environment Config Checks

Ensure your `.env` contains the required settings:
* `LLM_ENABLED`: Toggle local AI copilot (`True`/`False`).
* `SECRET_KEY`: Set to a strong random hash to secure signed JWT tokens.
* `DEBUG`: Toggle verbose error logging for FastAPI operations.
