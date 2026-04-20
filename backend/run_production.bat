@echo off
REM Production backend startup (no auto-reload)
cd /d "%~dp0"
echo Starting DcoY backend (production mode - no auto-reload)...
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
