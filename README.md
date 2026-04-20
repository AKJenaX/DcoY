# DcoY

Starter layout for **DcoY**, an AI-based cybersecurity project. The backend uses **FastAPI**; ML dependencies are installed for later use. No detection or ML logic is included yet.

## Repository layout

- `backend/` — FastAPI app, data samples, configuration
- `frontend/` — reserved for a future Next.js app (not implemented)
- `docs/` — project documentation (add as needed)

## Prerequisites

- Python 3.10+ recommended
- Windows PowerShell (for the activation steps below)

## Backend setup

All commands below assume your current directory is the project root (`dcoy`), then you enter `backend`.

### 1. Create a virtual environment

```powershell
cd backend
python -m venv .venv
```

This creates a `.venv` folder inside `backend` with an isolated Python environment.

### 2. Activate the virtual environment (Windows PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

If execution policy blocks this, run PowerShell as Administrator once and use:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the FastAPI server

From the `backend` directory (with the virtual environment activated):

```powershell
uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000` by default. Open `http://127.0.0.1:8000/` in a browser or use curl; you should see a JSON welcome payload. Interactive docs: `http://127.0.0.1:8000/docs`.

### Environment variables

Configuration is loaded from `backend/.env` (see `APP_NAME` and `DEBUG`). Adjust values there for local development.

## Next steps

- Add routers under `backend/app/` and register them in `main.py`
- Implement modules under `agents/`, `detection/`, `deception/`, and `response/` as you build features
- Use `backend/data/sample_logs.csv` as a starting point for pipelines and tests
