"""
Detection agent (Phase 7–8).

Runs the existing anomaly pipeline and emits normalized JSON events for other agents.
Does not duplicate ML or classification rules — those live in app.detection.anomaly.

Phase 8 adds a numeric risk score so downstream agents can reason about threat level
without replacing the original severity or event metadata.
"""

from typing import Any, Dict, List

from app.detection.anomaly import (
    detect_anomalies,
    load_data,
    preprocess_data,
    train_model,
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_risk_score(record: dict) -> float:
    """
    Combine unsupervised ML signal with scaled log features into one score in [0, 1].

    Why normalize (divide by 50 / 50 / 200)?
    Raw failed_logins, port_attempts, and request_rate live on different scales.
    Dividing by chosen caps maps each into a rough 0–1 band so they can be averaged
    fairly before blending with the ML term. Caps are demo constants, not from anomaly.py.

    Why weight ML 0.6 and the rule average 0.4?
    The Isolation Forest outlier flag (ml_score) is treated as the strongest signal
    for “this row is unusual” in this demo. The log features add context (brute force,
    scan-like port fan-out, high rate) without overriding the model entirely.

    Formula:
        ml_score = 1 if is_anomaly else 0
        rule_avg = mean(failed/50, ports/50, rate/200)
        risk = 0.6 * ml_score + 0.4 * rule_avg
    """
    failed = _safe_float(record.get("failed_logins"))
    ports = _safe_float(record.get("port_attempts"))
    rate = _safe_float(record.get("request_rate"))

    normalized_failed_logins = failed / 50.0
    normalized_port_attempts = ports / 50.0
    normalized_request_rate = rate / 200.0

    ml_score = 1.0 if record.get("is_anomaly") == 1 else 0.0

    rule_blend = (
        normalized_failed_logins + normalized_port_attempts + normalized_request_rate
    ) / 3.0

    risk_score = 0.6 * ml_score + 0.4 * rule_blend

    return max(0.0, min(1.0, risk_score))


def _risk_level_from_score(risk_score: float) -> str:
    """Bucket continuous risk into labels for policy rules."""
    if risk_score > 0.75:
        return "high"
    if risk_score > 0.4:
        return "medium"
    return "low"


def run_pipeline_records() -> List[Dict[str, Any]]:
    """
    Execute the same steps as GET /detect: load → preprocess → train → score rows.

    Returns the list of per-row dicts produced by detect_anomalies (includes all phases).
    """
    df = load_data()
    df = preprocess_data(df)
    model = train_model(df)
    return detect_anomalies(df, model)


def classify_attacker(record: dict) -> str:
    """
    Classify attacker based on behavior patterns.
    Priority order is important:
    advanced → automated_tool → beginner → unknown
    """
    failed_logins = record.get("failed_logins", 0)
    port_attempts = record.get("port_attempts", 0)
    request_rate = record.get("request_rate", 0)

    # Advanced attacker: high-speed and aggressive scanning behavior
    if request_rate > 100 and port_attempts > 20:
        return "advanced"

    # Automated tool: repeated structured login + port attempts
    elif failed_logins >= 10 and port_attempts >= 5:
        return "automated_tool"

    # Beginner attacker: low activity, likely manual attempts
    elif failed_logins < 10 and port_attempts < 5:
        return "beginner"

    # Fallback for unmatched patterns
    else:
        return "unknown"


def get_profile_reason(profile: str) -> str:
    """
    Return human-readable explanation for attacker profile.
    This provides clear context and interpretability for analysts so they
    understand why a certain profile was assigned. It improves transparency.
    """
    if profile == "beginner":
        return "Low-frequency activity suggesting manual or inexperienced attacker."

    elif profile == "automated_tool":
        return "Repeated login attempts and port scans indicating automated scripts."

    elif profile == "advanced":
        return "High-speed and high-volume activity suggesting advanced attacker behavior."

    else:
        return "Unrecognized behavior pattern."


def to_detection_messages(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Map pipeline rows to agent messages.

    - event_type: mirrors rule-based attack_type (what happened).
    - severity: ML outlier → high; inlier → low (Isolation Forest signal, unchanged).
    - risk_score / risk_level: Phase 8 decision layer (additive; does not replace severity).
    - details: full original record for audit / backward compatibility.
    """
    messages: List[Dict[str, Any]] = []
    for rec in records:
        is_outlier = rec.get("is_anomaly") == 1
        risk_score = compute_risk_score(rec)
        
        from app.utils.feedback_store import update_feedback, get_feedback
        ip = str(rec.get("ip", ""))
        user = str(rec.get("user", "default_user")).strip().lower()
        initial_risk_level = _risk_level_from_score(risk_score)
        
        update_feedback(user, ip, initial_risk_level)
        feedback = get_feedback(user, ip)
        
        history_factor = min(feedback["high_risk_count"] / 10.0, 0.3)
        risk_score = min(1.0, risk_score + history_factor)
        
        profile = classify_attacker(rec)
        reason = get_profile_reason(profile)
        
        out = {
            "event_type": rec.get("attack_type", "normal"),
            "severity": "high" if is_outlier else "low",
            "ip": ip,
            "risk_score": round(risk_score, 4),
            "risk_level": _risk_level_from_score(risk_score),
            "attacker_profile": profile,
            "profile_reason": reason,
            "history_events": feedback["total_events"],
            "repeat_offender_score": feedback["high_risk_count"],
            "details": dict(rec),
        }
        out["user"] = user
        messages.append(out)
    return messages


def run() -> List[Dict[str, Any]]:
    """Run detection end-to-end and return messages for the deception agent."""
    records = run_pipeline_records()
    return to_detection_messages(records)

