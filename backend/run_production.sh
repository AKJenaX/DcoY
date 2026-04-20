#!/bin/bash
# Production backend startup (no auto-reload)
cd "$(dirname "$0")"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
