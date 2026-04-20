"""Anomaly detection module (Phase 3) with Phase 4 rule-based attack labels."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from app.deception.honeypot import select_honeypot

# Resolved from backend/app/detection/anomaly.py -> backend/data/sample_logs.csv
_DEFAULT_CSV = Path(__file__).resolve().parent.parent.parent / "data" / "sample_logs.csv"

FEATURE_COLUMNS = ["failed_logins", "port_attempts", "request_rate"]

# Canonical labels for API summaries (order not significant).
ATTACK_LABELS = ("ssh_bruteforce", "port_scan", "web_attack", "normal")


def load_data(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load log rows from a CSV file."""
    path = csv_path if csv_path is not None else _DEFAULT_CSV
    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path)


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values and coerce feature columns to numeric."""
    out = df.copy()
    for col in FEATURE_COLUMNS:
        if col not in out.columns:
            out[col] = 0
    out[FEATURE_COLUMNS] = out[FEATURE_COLUMNS].fillna(0)
    out[FEATURE_COLUMNS] = (
        out[FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0)
    )
    return out


def train_model(df: pd.DataFrame) -> IsolationForest:
    """Fit an Isolation Forest on the feature columns."""
    features = df[FEATURE_COLUMNS]
    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(features)
    return model


def _jsonable(value: Any) -> Any:
    """Convert numpy/pandas scalars to plain Python types for JSON."""
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return float(value)
    return value


def classify_attack(row: pd.Series) -> str:
    """
    Rule-based attack type for one log row (Phase 4 classification layer).

    This runs *after* Isolation Forest scoring. ML flags statistical outliers;
    these thresholds map common feature patterns to human-readable scenarios
    for demos and reporting.

    Rules (first match wins — same idea as if / elif):
    - ssh_bruteforce: very high failed logins → repeated bad password / SSH guess attempts.
    - port_scan: many ports touched → reconnaissance across services.
    - web_attack: very high request rate → possible HTTP flood or abusive client.
    - normal: none of the above.
    """
    failed_logins = row["failed_logins"]
    port_attempts = row["port_attempts"]
    request_rate = row["request_rate"]

    if failed_logins > 20:
        return "ssh_bruteforce"
    if port_attempts > 15:
        return "port_scan"
    if request_rate > 100:
        return "web_attack"
    return "normal"


def build_attack_summary(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count how many rows fell into each attack_type bucket."""
    summary = {label: 0 for label in ATTACK_LABELS}
    for row in records:
        label = row.get("attack_type")
        if label in summary:
            summary[label] += 1
    return summary


def detect_anomalies(df: pd.DataFrame, model: IsolationForest) -> List[Dict[str, Any]]:
    """
    Score each row and label anomalies, then apply rule-based attack types.

    Phase 3 (unchanged): Isolation Forest → anomaly_score, is_anomaly.
    Phase 4: classify_attack() → attack_type (separate heuristic layer).
    Phase 5: select_honeypot() → honeypot, response_action, response_status (deception layer).
    """
    features = df[FEATURE_COLUMNS]
    enriched = df.copy()

    # Phase 3 — ML: unsupervised anomaly scores (Isolation Forest only).
    enriched["anomaly_score"] = model.decision_function(features)
    predictions = model.predict(features)
    enriched["is_anomaly"] = (predictions == -1).astype(int)

    # Phase 4 — rules: interpret features as attack scenarios (no ML here).
    enriched["attack_type"] = enriched.apply(classify_attack, axis=1)

    # Phase 5 — deception: honeypot plan per row (rules live in deception/honeypot.py).
    _plans = enriched["attack_type"].map(lambda t: select_honeypot(str(t)))
    enriched["honeypot"] = _plans.map(lambda p: p["honeypot"])
    enriched["response_action"] = _plans.map(lambda p: p["action"])
    enriched["response_status"] = _plans.map(lambda p: p["status"])

    raw_rows = enriched.to_dict(orient="records")
    return [
        {key: _jsonable(val) for key, val in row.items()} for row in raw_rows
    ]
