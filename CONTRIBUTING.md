# Contributing to DcoY

First off, thank you for considering contributing to DcoY! It is people like you who make DcoY a powerful and resilient threat detection platform.

---

## 🛠️ Developer Setup

1. Fork the repository and clone your fork locally.
2. Initialize virtual environments in `backend/`:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Or .\.venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` in `backend/` (or root) and set credentials:
   ```bash
   cp .env.example .env
   ```

---

## 🚀 Pull Request Checklist

Before submitting a Pull Request, please ensure you satisfy the following conditions:
* **Small commits**: Group code edits by feature or module. Avoid massive, unrelated changes.
* **Keep coding styles consistent**: Follow standard PEP8 naming conventions (`snake_case` functions/files, `PascalCase` classes).
* **Test your changes**: Run the local diagnostics setup script to verify connection integrity:
  ```bash
  python scripts/verify_setup.py
  ```
* **Document your changes**: Update relevant docs under `docs/` or update details in `CHANGELOG.md`.

---

## 🐛 Bug Reports & Feature Suggestions

Please submit bug reports and feature requests using GitHub Issues:
1. Explain the **severity** and provide **reproduction steps**.
2. Explain the **root cause** and recommend any **fixes**.
3. Detail which files are affected.
