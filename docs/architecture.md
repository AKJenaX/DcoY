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

---

## 💾 3. Database Schema Design (SQLAlchemy)

DcoY implements persistent storage using an SQLite backend for security cases, evidence mapping, analyst logs, and AI dialog links:

```mermaid
classDiagram
    class DBInvestigation {
        +String id
        +String title
        +String status
        +String priority
        +String severity
        +DateTime created_at
        +DateTime updated_at
        +String assigned_analyst
        +String last_modified_by
        +Float risk_score
        +Text ai_summary
        +Text notes
        +DateTime deleted_at
    }
    class DBEvidence {
        +Integer id
        +String investigation_id
        +String event
        +String timestamp
        +String severity
        +String confidence
        +String mitre
    }
    class DBAnalystNote {
        +Integer id
        +String investigation_id
        +String author
        +Text content
        +DateTime created_at
    }
    class DBCopilotLink {
        +Integer id
        +String investigation_id
        +String conversation_key
    }
    class DBTimelineEvent {
        +Integer id
        +String investigation_id
        +String timestamp
        +String event
        +Text details
        +String action_by
        +String before_value
        +String after_value
    }
    DBInvestigation "1" *-- "many" DBEvidence
    DBInvestigation "1" *-- "many" DBAnalystNote
    DBInvestigation "1" *-- "many" DBCopilotLink
    DBInvestigation "1" *-- "many" DBTimelineEvent
```

---

## 🏛️ 4. Repository & Adapter Pattern

- **InvestigationRepository**: Decouples SQLAlchemy session execution from FastAPI path operators, handling soft deletes, N+1 query mitigations (`joinedload`), and immutable audit trail generation.
- **Notification Engine**: Uses an adapter interface allowing events (such as critical case creation or assignment changes) to be broadcasted to Slack, Teams, PagerDuty, and Email alert networks.

---

## ⏳ 5. Investigation Lifecycle Management

Cases transition through three states:
1. **Open**: Case is newly initialized from telemetry outliers.
2. **Active**: Assigned to a security analyst for triage, evidence aggregation, and playbook execution.
3. **Resolved**: Mitigations applied (e.g., firewall isolation) and audit trail logged.

