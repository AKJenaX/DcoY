# DcoY Threat Defense Platform

<p align="center">
  <strong>Enterprise Active Defense, Machine Learning Anomaly Detection & Deception Console</strong>
</p>

<p align="center">
  <a href="https://github.com/AKJenaX/DcoY/releases"><img src="https://img.shields.io/badge/version-v1.0.0-cyan.svg?style=flat-square" alt="Version"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-18.0+-61DAFB.svg?style=flat-square&logo=react&logoColor=black" alt="React"/></a>
  <a href="https://github.com/AKJenaX/DcoY/actions"><img src="https://img.shields.io/badge/CI-Passing-00ff66.svg?style=flat-square" alt="CI Status"/></a>
  <a href="backend/tests"><img src="https://img.shields.io/badge/Tests-101%20Passed-brightgreen.svg?style=flat-square" alt="Tests"/></a>
</p>

---

## Overview

**DcoY** is an open-source active defense and cyber deception platform designed to detect, misdirect, and investigate unauthorized network ingress in real-time.

Unlike passive SIEM alert aggregators, DcoY dynamically deploys virtual honeypot listeners, scores incoming network telemetry using machine learning anomaly models, and misdirects attackers into synthetic honeynets while capturing full forensics.

The platform provides a modern **SOC Command Center** built with React, TypeScript, and FastAPI, featuring real-time WebSockets, automated incident management, rule engineering, and executive security intelligence.

---

## Console Workspace

<p align="center">
  <img src="docs/assets/command_overview.png" alt="SOC Command Center Overview" width="90%" />
  <br/>
  <em>Figure 1: DcoY Command Overview Workspace displaying real-time telemetry, threat radar, and MITRE ATT&CK coverage.</em>
</p>

---

## Key Features

* **Machine Learning Anomaly Detection**: Scores network telemetry in real-time using Isolation Forest models to detect zero-day reconnaissance and credential attacks.
* **Active Deception Engine**: Dynamically routes high-risk IP traffic into virtual honeynet traps (SSH, HTTP, Database traps) to record attacker behavior.
* **Real-time Event Ingestion & WebSockets**: Low-latency event streaming via `/ws/telemetry` channels with automatic HTTP polling fallback.
* **DB-Backed Incident Workspace**: Case ledger tracking incidents, notes, timeline event correlation, and forensic export.
* **Observability & Distributed Tracing**: Native request correlation tracking (`X-Request-ID`), structured JSON logging, classified exceptions, liveness/readiness probes (`/health/live`, `/health/ready`), and Prometheus-compatible metrics (`/metrics`).
* **Production Security & Auth Persistence**: Hashed database user storage using bcrypt, SHA-256 API key hashing, constant-time `hmac.compare_digest` verification, and JWT session handling.

---

## Architecture Overview

```text
  ┌────────────────────────────────────────────────────────────────────────┐
  │                    React + TypeScript SOC Console                      │
  │     (Command Overview, Hive Map, Deception Grid, Incident Ledger)      │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │ REST API / WebSockets
  ┌───────────────────────────────────▼────────────────────────────────────┐
  │                        FastAPI API Gateway                             │
  │   [CorrelationID] ──> [CORS] ──> [JWT & API-Key Auth] ──> [JSON Logger]  │
  └───────┬───────────────────────────┬───────────────────────────┬────────┘
          │                           │                           │
  ┌───────▼───────────┐       ┌───────▼───────────┐       ┌───────▼───────────┐
  │  Anomaly Agent    │       │  Deception Agent  │       │ Reasoning Agent   │
  │ Isolation Forest  │       │ Honeynet Listener │       │ AI Assistant /    │
  │ ML Pipeline       │       │ Strategy Engine   │       │ Incident Summaries│
  └───────┬───────────┘       └───────┬───────────┘       └───────┬───────────┘
          │                           │                           │
  ┌───────▼───────────────────────────▼───────────────────────────▼────────┐
  │                    SQLAlchemy ORM Data Store                           │
  │       (DBUser, DBApiKey, DBInvestigation, DBTimelineEvent)           │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.11+, FastAPI, Uvicorn, Starlette |
| **Machine Learning** | Scikit-learn (Isolation Forest), Pandas, NumPy |
| **Database & Persistence** | SQLAlchemy ORM, Alembic Migrations, SQLite / PostgreSQL |
| **Security & Auth** | PyJWT, bcrypt, SHA-256 Key Hashing, HMAC constant-time validation |
| **Frontend UI** | React 18, TypeScript 5, Vite, Tailwind CSS, Lucide Icons |
| **Testing & Quality** | Pytest (101 unit tests), Pyright (0 errors), ESLint, Vite Build |
| **Deployment & Ops** | Docker, Docker Compose, Multi-stage Nginx Reverse Proxy |

---

## Quick Start

### Prerequisites
* Python 3.11+
* Node.js 18+ & npm

### 1. Launch Backend API
```bash
cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1 | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### 2. Launch React SOC Console
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.  
* **Default Operator Credentials**: `operator` / `secure_password`

---

## Project Structure

```text
DcoY/
├── backend/
│   ├── alembic/                # Database migration scripts
│   ├── app/
│   │   ├── agents/             # Detection, deception, and response agents
│   │   ├── dependencies/       # FastAPI authentication & RBAC dependencies
│   │   ├── middleware/         # Correlation ID, CORS, and logging middleware
│   │   ├── models/             # Pydantic V2 schemas & SQLAlchemy ORM models
│   │   ├── repositories/       # ORM repository data access layer
│   │   ├── routers/            # 10 domain REST API router modules
│   │   ├── services/           # Simulation & rule engines
│   │   └── main.py             # FastAPI entry point & lifespan manager
│   └── tests/                  # Pytest test suite (101 tests)
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable React UI widgets
│   │   ├── hooks/              # useRealtimeChannel & state hooks
│   │   ├── services/           # REST API client
│   │   └── views/              # 10 SOC Command Center views
│   ├── Dockerfile              # Multi-stage production Nginx container
│   └── nginx.conf              # Nginx reverse proxy configuration
├── docs/                       # Technical architecture documentation
├── scripts/                    # Verification & setup diagnostic tools
└── docker-compose.yml          # Production multi-container orchestrator
```

---

## Documentation & API References

Detailed architecture specs, API endpoints, and guides are available in [`docs/`](docs/):

* 🚀 **[Quick Start Guide](docs/quick-start.md)** — Step-by-step setup and verification.
* 🏗️ **[System Architecture](docs/architecture.md)** — Monorepo design, multi-agent pipeline, and data flow.
* 📡 **[API Reference](docs/api.md)** — Complete OpenAPI specification and endpoints.
* 🛡️ **[Security Architecture](docs/security.md)** — Authentication, API keys, and RBAC control flows.
* 🚢 **[Deployment Manual](deployment.md)** — Production readiness, Docker, Nginx, and rollback procedures.

---

## Testing & Quality Assurance

Run the automated test suite and type diagnostics:

```bash
# Execute 101 backend unit & integration tests
cd backend
python -m pytest

# Run Pyright static type checker (0 errors)
npx pyright app

# Verify frontend production build
cd ../frontend
npm run build
```

---

## Deployment

To deploy DcoY in a production environment using Docker Compose:

```bash
cp production.env.example .env
docker-compose up -d --build
```
This builds the multi-stage Nginx frontend container and FastAPI backend service with health probes enabled.

---

## Roadmap

* [ ] **Redis Pub/Sub Layer**: Scaling WebSocket streaming horizontally across multi-pod backend deployments.
* [ ] **PostgreSQL Production Target**: Official Helm chart for Kubernetes deployment with connection pooling.
* [ ] **eBPF Kernel Agent**: Low-overhead Linux kernel probe for network socket interception.
* [ ] **SIEM Export Pipeline**: Automated Syslog / CEF exporter for Splunk and Microsoft Sentinel integration.

---

## Contributing

Contributions are welcome! Please review our **[Contributing Guide](CONTRIBUTING.md)** and **[Code of Conduct](CODE_OF_CONDUCT.md)** before submitting a pull request.

---

## License

This project is licensed under the **[MIT License](LICENSE)**.
