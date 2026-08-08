"""Anomaly detection and rule engine router."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user_from_token, get_current_user_from_api_key, check_permission
from app.database import get_db
from app.services.pipeline import run_agent_pipeline
from app.agents import detection_agent
from app.deception.honeypot import build_response_summary
from app.detection.anomaly import build_attack_summary
from app.models import DetectResponse, ApiDetectResponse
from app.models.detection_rule import DBDetectionRule, DBRuleRevision
from app.services.container import container
from app.utils.notifications import notification_engine

logger = logging.getLogger(__name__)

router = APIRouter()


class DetectionRuleCreate(BaseModel):
    name: str
    description: str
    severity: str = "Medium"
    category: str = "Custom Rules"
    mitre_technique: Optional[str] = None
    detection_logic: str = "{}"
    threshold: int = 5
    time_window: int = 60
    recommended_response: Optional[str] = None
    tags: Optional[List[str]] = None


class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    mitre_technique: Optional[str] = None
    detection_logic: Optional[str] = None
    threshold: Optional[int] = None
    time_window: Optional[int] = None
    recommended_response: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    changelog: Optional[str] = None


class TestCustomRulePayload(BaseModel):
    detection_logic: str


class RuleValidatePayload(BaseModel):
    name: str
    description: str
    severity: str = "Medium"
    category: str = "Custom Rules"
    mitre_technique: Optional[str] = None
    detection_logic: str = "{}"
    threshold: int = 5
    time_window: int = 60


@router.get(
    "/detect",
    response_model=DetectResponse,
    summary="Run Anomaly Detection Pipeline",
    description="Evaluates Isolation Forest anomaly detection model over network telemetry."
)
def run_anomaly_detection(user: str = Depends(get_current_user_from_token)) -> DetectResponse:
    """Run the Isolation Forest pipeline on live data if available, otherwise CSV."""
    logger.info("GET /detect - Running anomaly detection")
    try:
        data = detection_agent.run_pipeline_records()
        logger.debug(f"Anomaly detection complete: {len(data)} records")
    except FileNotFoundError as exc:
        logger.error(f"File not found in /detect: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    anomalies_detected = sum(1 for row in data if row.get("is_anomaly") == 1)
    attack_summary = build_attack_summary(data)
    response_summary = build_response_summary(data)

    logger.info(f"Detection result: {anomalies_detected} anomalies in {len(data)} records")

    return DetectResponse(
        total_records=len(data),
        anomalies_detected=anomalies_detected,
        attack_summary=attack_summary,
        response_summary=response_summary,
        data=cast(Any, data),
    )


@router.post(
    "/api/detect",
    response_model=ApiDetectResponse,
    summary="API Anomaly Detection",
    description="API-key authenticated endpoint to run anomaly detection pipeline."
)
def api_detect(user: str = Depends(get_current_user_from_api_key)) -> ApiDetectResponse:
    logger.info(f"POST /api/detect - User: {user}")
    messages = run_agent_pipeline(user)
    return ApiDetectResponse(
        user=user,
        total_events=len(messages),
        data=cast(Any, messages)
    )


@router.post("/api/rules", summary="Create Detection Rule", description="Registers new detection rule in rule catalog.")
def create_detection_rule(
    body: DetectionRuleCreate,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/rules - User: {user}, Rule: {body.name}")
    rule = DBDetectionRule(
        name=body.name,
        description=body.description,
        author=user,
        version=1,
        status="Enabled",
        severity=body.severity,
        category=body.category,
        mitre_technique=body.mitre_technique,
        detection_logic=body.detection_logic,
        threshold=body.threshold,
        time_window=body.time_window,
        recommended_response=body.recommended_response,
        tags=body.tags
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    rev = DBRuleRevision(
        rule_id=rule.id,
        version=1,
        name=rule.name,
        description=rule.description,
        severity=rule.severity,
        detection_logic=rule.detection_logic,
        threshold=rule.threshold,
        time_window=rule.time_window,
        recommended_response=rule.recommended_response,
        changelog="Initial creation",
        author=user
    )
    db.add(rev)
    db.commit()
    
    notification_engine.trigger("RULE_CREATED", {
        "message": f"New detection rule '{rule.name}' created by {user}.",
        "severity": rule.severity
    })
    
    return {"message": "Detection rule created successfully", "id": rule.id}


@router.get("/api/rules", summary="List Detection Rules", description="Returns list of rules filtered by category/severity/status/search.")
def get_detection_rules(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/rules - User: {user}")
    query = db.query(DBDetectionRule)
    
    if category and category != "All":
        query = query.filter(DBDetectionRule.category == category)
    if severity and severity != "All":
        query = query.filter(DBDetectionRule.severity == severity)
    if status and status != "All":
        query = query.filter(DBDetectionRule.status == status)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            DBDetectionRule.name.like(search_pattern) |
            DBDetectionRule.description.like(search_pattern)
        )
        
    rules = query.order_by(DBDetectionRule.updated_at.desc()).all()
    
    result = []
    for r in rules:
        result.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "author": r.author,
            "version": r.version,
            "status": r.status,
            "severity": r.severity,
            "category": r.category,
            "mitre_technique": r.mitre_technique,
            "detection_logic": r.detection_logic,
            "threshold": r.threshold,
            "time_window": r.time_window,
            "recommended_response": r.recommended_response,
            "tags": r.tags,
            "created_at": r.created_at.isoformat() + "Z",
            "updated_at": r.updated_at.isoformat() + "Z"
        })
    return result


@router.get("/api/rules/{rid}", summary="Get Detection Rule Details", description="Retrieves rule details and full revision history.")
def get_detection_rule_details(
    rid: int,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/rules/{rid} - User: {user}")
    r = db.query(DBDetectionRule).filter(DBDetectionRule.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    r_any: Any = r
    return {
        "id": r_any.id,
        "name": r_any.name,
        "description": r_any.description,
        "author": r_any.author,
        "version": r_any.version,
        "status": r_any.status,
        "severity": r_any.severity,
        "category": r_any.category,
        "mitre_technique": r_any.mitre_technique,
        "detection_logic": r_any.detection_logic,
        "threshold": r_any.threshold,
        "time_window": r_any.time_window,
        "recommended_response": r_any.recommended_response,
        "tags": r_any.tags,
        "revisions": [
            {
                "version": getattr(rev, "version"),
                "name": getattr(rev, "name"),
                "description": getattr(rev, "description"),
                "severity": getattr(rev, "severity"),
                "detection_logic": getattr(rev, "detection_logic"),
                "threshold": getattr(rev, "threshold"),
                "time_window": getattr(rev, "time_window"),
                "recommended_response": getattr(rev, "recommended_response"),
                "changelog": getattr(rev, "changelog"),
                "created_at": getattr(rev, "created_at").isoformat(),
                "author": getattr(rev, "author")
            } for rev in sorted(r_any.revisions or [], key=lambda x: getattr(x, "version"), reverse=True)
        ]
    }


@router.put("/api/rules/{rid}", summary="Update Detection Rule", description="Updates detection rule parameters and saves a version revision.")
def update_detection_rule(
    rid: int,
    body: DetectionRuleUpdate,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"PUT /api/rules/{rid} - User: {user}")
    rule = db.query(DBDetectionRule).filter(DBDetectionRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    rule_any: Any = rule
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    changelog_str = updates.pop("changelog", "Configuration update")
    
    rev = DBRuleRevision(
        rule_id=rule_any.id,
        version=rule_any.version,
        name=rule_any.name,
        description=rule_any.description,
        severity=rule_any.severity,
        detection_logic=rule_any.detection_logic,
        threshold=rule_any.threshold,
        time_window=rule_any.time_window,
        recommended_response=rule_any.recommended_response,
        changelog=changelog_str,
        author=rule_any.author
    )
    db.add(rev)
    
    for k, v in updates.items():
        setattr(rule_any, k, v)
        
    rule_any.version += 1
    rule_any.author = user
    rule_any.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    container.rule_engine.clear_cache(rule_any.id)
    
    return {"message": "Rule updated successfully", "version": rule_any.version}


@router.delete("/api/rules/{rid}", summary="Delete Detection Rule", description="Removes rule record from database.")
def delete_detection_rule(
    rid: int,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"DELETE /api/rules/{rid} - User: {user}")
    rule = db.query(DBDetectionRule).filter(DBDetectionRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}


@router.post("/api/rules/{rid}/test", summary="Test Detection Rule", description="Evaluates detection rule against active telemetry stream.")
def test_detection_rule(
    rid: int,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/rules/{rid}/test - User: {user}")
    rule = db.query(DBDetectionRule).filter(DBDetectionRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    telemetry = run_agent_pipeline(user)
    matched, duration_ms, coverage = container.rule_engine.test_rule(rule, telemetry)
    
    return {
        "matched_count": len(matched),
        "execution_time_ms": duration_ms,
        "detection_coverage": coverage,
        "false_positive_estimate": 0.05 if len(matched) > 2 else 0.01,
        "matched_events": [
            {
                "ip": e.get("ip"),
                "timestamp": e.get("timestamp") or e.get("time") or datetime.now(timezone.utc).isoformat(),
                "event_type": e.get("event_type"),
                "risk_score": e.get("risk_score")
            } for e in matched
        ]
    }


@router.post("/api/rules/test-custom", summary="Test Custom Rule Logic", description="Tests transient rule criteria against active telemetry.")
def test_custom_rule(
    body: TestCustomRulePayload,
    user: str = Depends(check_permission("rules:read"))
):
    logger.info(f"POST /api/rules/test-custom - User: {user}")
    temp_rule = DBDetectionRule(id=999999, detection_logic=body.detection_logic)
    telemetry = run_agent_pipeline(user)
    
    matched, duration_ms, coverage = container.rule_engine.test_rule(temp_rule, telemetry)
    return {
        "would_trigger": len(matched) > 0,
        "affected_events_count": len(matched),
        "execution_time_ms": duration_ms,
        "confidence": "High" if len(matched) < 5 else "Medium"
    }


@router.post("/api/rules/{rid}/revert/{version}", summary="Revert Detection Rule Revision", description="Rolls back rule definition to target historical revision version.")
def revert_detection_rule_revision(
    rid: int,
    version: int,
    user: str = Depends(check_permission("rules:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/rules/{rid}/revert/{version} - User: {user}")
    rule = db.query(DBDetectionRule).filter(DBDetectionRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    rev = db.query(DBRuleRevision).filter(
        DBRuleRevision.rule_id == rid,
        DBRuleRevision.version == version
    ).first()
    if not rev:
        raise HTTPException(status_code=404, detail="Revision version not found")
        
    rule_any: Any = rule
    rule_any.name = rev.name
    rule_any.description = rev.description
    rule_any.severity = rev.severity
    rule_any.detection_logic = rev.detection_logic
    rule_any.threshold = rev.threshold
    rule_any.time_window = rev.time_window
    rule_any.recommended_response = rev.recommended_response
    rule_any.author = user
    rule_any.version += 1
    rule_any.updated_at = datetime.now(timezone.utc)

    db.commit()
    container.rule_engine.clear_cache(rule_any.id)

    return {"message": "Rule reverted successfully", "version": rule_any.version}


@router.post("/api/rules/validate", summary="Validate Rule Schema", description="Validates JSON syntax and checks rule name uniqueness.")
def validate_rule(
    body: RuleValidatePayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/rules/validate - User: {user}")
    existing_names = [str(getattr(r, "name")) for r in db.query(DBDetectionRule).all()]
    is_valid, errors = container.rule_validator.validate(body.model_dump(), existing_names)
    return {"valid": is_valid, "errors": errors}


@router.get("/api/rules/{rid}/metrics", summary="Get Rule Execution Metrics", description="Returns trigger count and latency statistics for a rule.")
def get_rule_metrics(
    rid: int,
    user: str = Depends(check_permission("rules:read"))
):
    logger.info(f"GET /api/rules/{rid}/metrics - User: {user}")
    return container.rule_engine.metrics.get_metrics(rid)


@router.get("/api/rules/metrics/all", summary="Get All Rule Metrics", description="Returns aggregate performance metrics across all active rules.")
def get_all_rule_metrics(
    user: str = Depends(check_permission("rules:read"))
):
    logger.info(f"GET /api/rules/metrics/all - User: {user}")
    return container.rule_engine.metrics.get_all_metrics()


@router.post("/api/rules/{rid}/benchmark", summary="Benchmark Rule Execution", description="Benchmarks rule execution time against active telemetry.")
def benchmark_rule(
    rid: int,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/rules/{rid}/benchmark - User: {user}")
    rule = db.query(DBDetectionRule).filter(DBDetectionRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    telemetry = run_agent_pipeline(user)
    return container.rule_engine.benchmark_rule(rule, telemetry)


@router.get("/api/rules/coverage", summary="Get Detection Rule MITRE Coverage", description="Returns MITRE ATT&CK technique coverage statistics.")
def get_rule_coverage(
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/rules/coverage - User: {user}")
    rules = db.query(DBDetectionRule).all()
    rule_dicts = [
        {
            "mitre_technique": getattr(r, "mitre_technique", None),
            "category": getattr(r, "category", "Custom Rules"),
            "severity": getattr(r, "severity", "Medium"),
        }
        for r in rules
    ]
    return container.rule_engine.metrics.get_coverage_stats(rule_dicts)


@router.get("/api/rules/{rid}/health", summary="Get Rule Health Score", description="Calculates health score and false positive estimate for rule.")
def get_rule_health(
    rid: int,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/rules/{rid}/health - User: {user}")
    rule = db.query(DBDetectionRule).filter(DBDetectionRule.id == rid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    metrics = container.rule_engine.metrics.get_metrics(rid)
    r: Any = rule
    return {
        "rule_id": rid,
        "name": r.name,
        "status": r.status,
        "trigger_count": metrics["trigger_count"],
        "last_triggered": metrics["last_triggered"],
        "avg_execution_time_ms": metrics["avg_latency_ms"],
        "false_positive_estimate": 0.05 if metrics["matches"] > 2 else 0.01,
        "detection_coverage": metrics["trigger_rate"],
        "health_score": metrics["health_score"],
    }
