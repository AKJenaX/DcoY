# DcoY

<p align="center">
  <img src="assets/logo/logo.png" alt="DcoY Logo" width="128"/>
</p>

<p align="center">
  <strong>Enterprise AI Security Operations, Threat Detection, and Active Deception</strong>
</p>

<p align="center">
  <a href="https://github.com/AKJenaX/DcoY/releases"><img src="https://img.shields.io/badge/version-v0.1.0--alpha-orange.svg" alt="Release Version"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python compatibility"/></a>
  <a href="https://github.com/AKJenaX/DcoY/actions/workflows/ci.yml"><img src="https://github.com/AKJenaX/DcoY/actions/workflows/ci.yml/badge.svg" alt="CI status"/></a>
  <a href="https://github.com/AKJenaX/DcoY"><img src="https://img.shields.io/github/stars/AKJenaX/DcoY.svg?style=social" alt="Stars Badge"/></a>
</p>

---

## Overview

**DcoY** is an AI-assisted cyber defense platform for real-time threat detection, deception response, SOC investigation workflows, and executive security intelligence.

The platform combines:

- Machine-learning anomaly detection with Isolation Forest.
- Active deception and honeypot response orchestration.
- Local Copilot-style reasoning through Ollama/Llama 3 with circuit-breaker fallbacks.
- Streamlit-based SOC workspaces for analysts and security operators.
- DB-backed investigation and detection-rule management.
- Executive Intelligence dashboards for SOC managers and CISOs.
- A standalone React/TypeScript enterprise design system for future frontend work.

DcoY is built to feel like practical enterprise security software: calm, technical, auditable, and fast.

---

## Core Capabilities

- **ML Anomaly Detection**: Scores network telemetry and identifies suspicious outliers.
- **Active Deception Engine**: Selects honeypot responses and isolation strategies based on attacker behavior.
- **AI Copilot Intel**: Answers questions, explains detections, maps activity to security context, and supports investigation summaries.
- **Threat Intelligence Center**: Tracks indicators, risk scores, MITRE mappings, response actions, and intelligence feeds.
- **Live Geolocation**: Visualizes source locations for observed suspicious activity.
- **Investigations Workspace**: Provides DB-backed case management, evidence linking, notes, timeline history, and exports.
- **Threat Hunting Workbench**: Supports proactive query building and telemetry filtering.
- **Detection Engineering**: Manages detection rules, validation, revisions, testing, benchmarking, and rule health.
- **Executive Intelligence**: Provides SOC operational KPIs, MITRE coverage, threat trends, SOC performance, AI insights, and executive report exports.
- **PDF, Markdown, and JSON Reporting**: Exports operational and executive security reports.
- **Telemetry Simulator**: Generates synthetic traffic for testing ingestion and detection flows.

---

## Executive Intelligence

The Executive Intelligence workspace is available at:

```text
http://localhost:8501/?page=executive
```

It includes:

- Open investigations.
- Critical alerts over the current 24-hour operating window.
- Detection coverage.
- Mean time to investigate and resolve.
- AI confidence averages.
- Security posture overview.
- Interactive MITRE ATT&CK coverage.
- Daily and weekly threat trends.
- Top attack vectors, affected countries, affected assets, and severity distribution.
- SOC performance metrics.
- Copilot-backed executive summaries with deterministic fallback.
- Executive report downloads as PDF, Markdown, and JSON.

Backend aggregate endpoint:

```text
GET /api/executive/metrics
```

---

## Enterprise Design System

DcoY now includes a standalone design-system foundation for future React-based frontend work:

```text
design-system/
```

The design system uses:

- React
- TypeScript
- Tailwind CSS
- shadcn/ui-compatible configuration
- Framer Motion
- Lucide React
- Tabler icon compatibility

It provides reusable foundations for:

- Semantic design tokens.
- Enterprise dark theme architecture.
- Typography, spacing, radius, shadow, glow, and elevation systems.
- Layout primitives.
- Background layers.
- Motion presets.
- Accessible component primitives.
- SOC-specific cards, widgets, timelines, command palette, and chart wrappers.
- Data visualization styles for line, area, bar, donut, radar, heatmap, timeline, network graph, MITRE matrix, and threat map.

Design-system entry points:

```ts
import "@dcoy/design-system/theme";
import { Button, Card, DashboardLayout } from "@dcoy/design-system";
```

Migration guidance:

- [Design System Migration Strategy](design-system/docs/migration-strategy.md)
- [Component Contracts](design-system/docs/component-contracts.md)

---

## Architecture

```text
DcoY/
  backend/
    app/
      agents/              Multi-agent detection, deception, response, and reasoning
      detection/           ML anomaly detection pipeline
      deception/           Honeypot and deception response logic
      models/              Pydantic and SQLAlchemy models
      services/            Rule quality, executive metrics, and rule services
      utils/               Auth, repository, reporting, geolocation, stores
      main.py              FastAPI application entry point
    tests/                 Backend test suite
  dashboard/
    app.py                 Streamlit dashboard entry point
    components/            SOC workspace components
    services/              Backend API clients
    utils/                 Theme, constants, formatting helpers
  design-system/
    src/
      tokens/              Semantic design tokens
      theme/               CSS variable theme and Tailwind layers
      components/          React UI primitives and SOC components
      layouts/             Dashboard and content layout primitives
      animations/          Framer Motion presets
      backgrounds/         Subtle enterprise background layers
      data-viz/            Shared chart and security visualization wrappers
      hooks/               Interaction and accessibility hooks
      providers/           Design system provider
  docs/                    Architecture, development, security, and setup docs
  scripts/                 Diagnostics and verification utilities
  simulator.py             Synthetic telemetry simulator
```

---

## Tech Stack

### Backend

- FastAPI
- Pydantic V2
- SQLAlchemy
- Scikit-learn
- Pandas
- NumPy
- Python-Jose
- Passlib
- ReportLab
- Ollama/Llama 3 integration

### Dashboard

- Streamlit
- Plotly
- Streamlit Autorefresh
- Requests

### Design System

- React
- TypeScript
- Tailwind CSS
- shadcn/ui-compatible config
- Radix UI primitives
- Framer Motion
- Lucide React
- Tabler icon compatibility

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/AKJenaX/DcoY.git
cd DcoY
cp .env.example .env
```

For local development, set:

```env
DEBUG=True
SECRET_KEY=replace_with_a_32_character_minimum_secret
```

### 2. Start the FastAPI backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Windows PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

Backend API:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

### 3. Start the Streamlit dashboard

In a new terminal:

```bash
cd dashboard
pip install -r requirements.txt
python -m streamlit run app.py
```

Dashboard:

```text
http://localhost:8501
```

### 4. Run the telemetry simulator

From the repository root:

```bash
python simulator.py
```

---

## Docker

Run the backend and dashboard together:

```bash
docker-compose up --build
```

Services:

- Backend API: `http://localhost:8000`
- Streamlit Dashboard: `http://localhost:8501`

---

## Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_NAME` | Platform display name | `DcoY` |
| `DEBUG` | Enables development mode | `True` in local development |
| `SECRET_KEY` | JWT signing key, minimum 32 characters in production | Required in production |
| `LLM_ENABLED` | Enables Ollama-backed reasoning | `True` |
| `LLM_HOST` | Ollama host URL | `http://127.0.0.1:11434` |
| `LLM_MODEL` | Ollama model name | `llama3` |
| `LLM_TIMEOUT` | LLM request timeout in seconds | `2.0` |
| `LLM_HEALTH_CHECK_INTERVAL` | Cached health-check window | `60.0` |
| `LLM_RETRY_INTERVAL` | Circuit-breaker retry interval | `30.0` |
| `LLM_FAILURE_THRESHOLD` | Failures before opening circuit | `3` |

---

## Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run backend tests:

```bash
set DEBUG=True
set SECRET_KEY=0123456789abcdef0123456789abcdef
python -m pytest backend/tests -q
```

PowerShell:

```powershell
$env:DEBUG='True'
$env:SECRET_KEY='0123456789abcdef0123456789abcdef'
python -m pytest backend\tests -q
```

Run focused rule-quality tests:

```bash
python -m pytest backend/tests/test_rule_quality.py -q
```

---

## Documentation

- [Quick Start](docs/quick-start.md)
- [API](docs/api.md)
- [Architecture](docs/architecture.md)
- [System Design](docs/system-design.md)
- [Security](docs/security.md)
- [Development](docs/development.md)
- [Deployment](docs/deployment.md)
- [Agents](docs/agents.md)
- [Real-Time Setup](docs/real-time-setup.md)
- [Test Commands](docs/test-commands.md)

---

## Release Milestones & Roadmap

- **v0.1.0-alpha**: Real-time telemetry, ML anomaly detection, active deception, Streamlit SOC workspaces, detection engineering, and executive dashboards.
- **v1.0.0-rc1 (Current)**:
  - **Security Knowledge Graph**: Directional entity relationships with caching and degree centrality analytics.
  - **Attack Path Engine**: Dijkstra-based shortest-path traversal mapping threat movements alongside matching defensive controls.
  - **Platform Diagnostics & Health**: Dynamic FastAPI route inventories, latency profiling, and health statuses.
  - **Structured Observability**: Structured JSON logging, OpenAPI schema metadata, and request latency logging middleware.
  - **Alembic Database Migrations**: Relational schema versioning for SQLite.
  - **Hardened Deployment**: Docker multi-stage builds running as non-privileged users.
  - **Interactive Demo Orchestration**: One-click synthetic attack scenario generation and observer consoles.

---

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

For security issues, follow [SECURITY.md](SECURITY.md).

---

## License

DcoY is licensed under the terms of the [MIT License](LICENSE).
