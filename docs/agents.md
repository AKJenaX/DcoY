# DcoY Multi-Agent Architecture

DcoY splits threat detection and active defense tasks across four specialized, cooperative agents.

---

## 🤖 1. Detection Agent
* **File**: `backend/app/agents/detection_agent.py`
* **Role**: Primary intake classifier.
* **Logic**: Receives ingested events, maps them against historical repeat offenders in the `feedback_store`, and runs the Isolation Forest model to assign an anomaly classification and risk score.

---

## 🕸️ 2. Deception Agent
* **File**: `backend/app/agents/deception_agent.py`
* **Role**: Policy planner.
* **Logic**: Evaluates risk scores and threat profiles (e.g. login failures vs port mapping scan activity) and selects the appropriate active countermeasure (e.g. redirect traffic to virtual environments).

---

## 🛠️ 3. Response Agent
* **File**: `backend/app/agents/response_agent.py`
* **Role**: Mitigation driver.
* **Logic**: Formulates honeypot containment parameters, binds them to target ports, and reports success responses to the main dashboard.

---

## 🧠 4. Reasoning Agent
* **File**: `backend/app/agents/reasoning_agent.py`
* **Role**: Operator helper and Copilot.
* **Logic**: Connects to the local Ollama service (Llama 3) using a resilient connection probe (150ms timeout) and circuit breaker framework. Translates raw telemetry data and agent decisions into clean, readable text explanations for security team review.
