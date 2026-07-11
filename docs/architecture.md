# DcoY Subsystem Architecture

This document describes the high-level subsystem interactions and data flow pipelines within the DcoY platform.

---

## 🏛️ System Block Diagram

```mermaid
graph LR
    Sim[Traffic Simulator] -- POST /api/ingest --> API[FastAPI Backend]
    API -- Read/Write --> Store[(Memory Store)]
    Dashboard[Streamlit UI] -- GET /detect --> API
    Dashboard -- GET /explain --> API
    Dashboard -- POST /ask --> API
    API -- HTTP Prompt --> Ollama[(Local Ollama)]
```

---

## 🔄 Sequence Pipeline Flow

The diagram below details the end-to-end telemetry ingestion, detection classification, agent mitigation, and UI rendering pipeline:

```mermaid
sequenceDiagram
    autonumber
    actor Sim as Traffic Simulator
    participant API as FastAPI Backend
    participant Det as Detection Agent
    participant Dec as Deception Agent
    participant Reasoning as Reasoning Agent
    participant Dashboard as Streamlit UI

    Sim->>API: Ingest network traffic logs (POST /api/ingest)
    API->>Det: Run Isolation Forest classifier
    Det-->>API: Return threat anomalies and risk scores
    API->>Dec: Select active response action
    Dec-->>API: Allocate honeypot trap type
    Dashboard->>API: Fetch current detections (GET /detect)
    API-->>Dashboard: Display live KPI statistics and charts
    Dashboard->>API: Fetch explanations (GET /explain or POST /ask)
    API->>Reasoning: Query natural language explanation
    Reasoning->>Reasoning: Check Circuit Breaker & Health Cache
    alt Ollama Available
        Reasoning->>Reasoning: Perform Llama 3 Inference
    else Ollama Offline
        Reasoning->>Reasoning: Fallback to Markdown Template
    end
    Reasoning-->>API: Return explanation content
    API-->>Dashboard: Render expanders / chat dialogue bubble
```
