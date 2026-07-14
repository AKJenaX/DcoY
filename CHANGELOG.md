# Changelog

All notable changes to the DcoY project will be documented in this file.

---

## [0.1.0-alpha] - 2026-07-10

This is the initial alpha release scaffold preparing DcoY for open-source availability.

### Added
* **Standardized Backend Schemas**: Unified Pydantic V2 data models inside `backend/app/models/` to govern API payload structures.
* **Modular React Dashboard**: Refactored the frontend dashboard into React + Vite inside the `frontend/` directory to improve readability and code reuse.
* **Fail-Fast LLM Reasoning**: Redesigned local Ollama calls in `reasoning_agent.py` to use fast TCP port socket probes (150ms timeout limit) and a circuit breaker (`CLOSED`/`OPEN`/`HALF-OPEN` states) to bypass LLM timeouts when offline.
* **Inference and Health Caching**: Cached successful LLM responses and socket health checks to improve performance.
* **Interactive Chat Copilot**: Integrated a Q&A security assistant widget in the dashboard UI connecting to the backend `/ask` endpoint.
* **PDF Report Builder**: Built a report compiler and downloader on the sidebar connecting to `/report`.
* **Mock Threat Simulator**: Refactored the synthetic traffic generator script `simulator.py` to test anomaly scoring pipelines in real-time.
