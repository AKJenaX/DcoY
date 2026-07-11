# DcoY System Design

This document details the internal design of the machine learning anomaly pipeline, memory data stores, and geographical tracking systems.

---

## 🤖 1. Machine Learning Telemetry Pipeline

DcoY utilizes the **Isolation Forest** algorithm (from `scikit-learn`) to detect network traffic anomalies. 

### telemetric Features Checked
1. `failed_logins`: High counts signal brute-force SSH/Web authentication attacks.
2. `port_attempts`: High counts indicate port scan mapping behaviors.
3. `request_rate`: High frequency implies DDoS or scraper payloads.

### Classifier Execution
- **Outlier Threshold**: Anomaly contamination rate defaults to `0.15` ($15\%$).
- **Scoring**: Standard scikit-learn anomaly scores. Scores $< 0.0$ are labeled as anomalies (assigned outlier score `1`).
- **Fallbacks**: If less than $5$ events are present in the memory store, the backend cleanly defaults to fitting and predicting on the static `sample_logs.csv` dataset.

---

## 💾 2. In-Memory Data Store (LiveStore)

To ensure high performance without external dependencies, DcoY implements an in-memory threat cache store `LiveStore`:
* **Buffering**: Stores a rolling window of the last $1000$ incoming events.
* **Aggregations**: Computes summary statistics (DDoS, brute-force counters, honeypot hits) on the fly, feeding the Streamlit visual charts.
* **Thread-Safety**: Governed by threading locks during ingestion writes.

---

## 🌍 3. IP Geolocation Resolution

Geographical coordinate mapping runs on a lightweight lookup mechanism:
* **Mock database**: Resolves country, city, latitude, and longitude based on standard IP subnets.
* **Visual mapping**: Structures coordinate outputs for Plotly Maps inside the Streamlit frontend.
