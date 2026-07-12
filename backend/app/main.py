"""FastAPI application entry point for DcoY."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents import deception_agent, detection_agent, response_agent
from app.agents.reasoning_agent import answer_question, generate_explanation, answer_question_detailed
from app.config import settings
from app.models import (
    IngestPayload,
    DetectResponse,
    AgentPipelineResponse,
    ExplainPipelineResponse,
    IngestResponse,
    ApiDetectResponse,
    ApiExplainResponse,
)
from app.deception.honeypot import build_response_summary
from app.detection.anomaly import (
    build_attack_summary,
    detect_anomalies,
    load_data,
    preprocess_data,
    train_model,
)
from app.utils.user_store import create_user, authenticate_user
from app.utils.live_store import add_event, get_events, has_events
from app.utils.geo_utils import get_ip_location, batch_get_locations
from app.utils.auth_utils import create_access_token, decode_access_token
from app.utils.network_capture import capture_basic_event
from app.utils.api_key_store import generate_api_key, validate_api_key
from app.utils.report_generator import generate_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-based cybersecurity platform API (starter scaffold).",
    version="0.1.0",
)

# Add CORS middleware with explicit configuration for better debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development; restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

logger.info(f"Starting {settings.APP_NAME} API")
logger.info("CORS middleware configured to accept all origins")


def _run_agent_pipeline(user: str = "default_user") -> List[Dict[str, Any]]:
    """Shared multi-agent run: detection → deception → response."""
    records = detection_agent.run_pipeline_records()
    for rec in records:
        rec["user"] = user
    messages = detection_agent.to_detection_messages(records)
    messages = deception_agent.process(messages)
    messages = response_agent.process(messages)
    return messages


def get_current_user_from_token(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "", 1).strip()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = payload.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user


def get_current_user_from_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        logger.warning("API request missing API key header")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    
    clean_key = x_api_key.strip()
    if not clean_key:
        logger.warning("API request missing API key header")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
        
    user = validate_api_key(clean_key)
    if not user:
        logger.warning("API request with invalid API key")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    return user


@app.get("/")
def read_root() -> Dict[str, str]:
    """Simple test route to verify the API is running."""
    logger.debug("GET / - Health check (root endpoint)")
    return {
        "message": "DcoY API is running",
        "app": settings.APP_NAME,
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Explicit health check endpoint for frontend diagnostic pings.
    
    Returns:
        - status: "ok" if backend is healthy
        - timestamp: ISO timestamp for timing checks
    """
    logger.debug("GET /health - Health check endpoint")
    return {
        "status": "ok",
        "service": settings.APP_NAME
    }


@app.post("/api/ingest", response_model=IngestResponse)
def ingest_events(payload: IngestPayload, user: str = Depends(get_current_user_from_api_key)) -> IngestResponse:
    """
    Live event ingestion endpoint.
    
    Accepts a payload with event data and stores them in memory.
    Keeps only the last 100 events.
    
    Args:
        payload: IngestPayload containing a list of threat events
        
    Returns:
        IngestResponse with success message, count, and total store size
    """
    logger.info("POST /api/ingest - Ingesting live events")
    
    try:
        count = 0
        for event in payload.data:
            add_event(event.model_dump(exclude_none=True))
            count += 1
        
        logger.info(f"Ingested {count} events. Total in store: {len(get_events())}")
        
        return IngestResponse(
            message="Events ingested successfully",
            count=count,
            total_in_store=len(get_events())
        )
    
    except Exception as e:
        logger.error(f"Error ingesting events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e



@app.get("/api/capture")
def capture_event(user: str = Depends(get_current_user_from_api_key)) -> Dict[str, Any]:
    event = capture_basic_event()

    if event:
        add_event(event)
        return {"message": "Captured event", "event": event}

    return {"message": "Capture failed"}



@app.get("/detect", response_model=DetectResponse)
def run_anomaly_detection(user: str = Depends(get_current_user_from_token)) -> DetectResponse:
    """Run the Isolation Forest pipeline on live data if available, otherwise CSV."""
    logger.info("GET /detect - Running anomaly detection")
    try:
        # Use run_pipeline_records which handles live data first, then CSV fallback
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
        data=data,
    )



@app.get("/agents", response_model=AgentPipelineResponse)
def run_agent_pipeline(user: str = Depends(get_current_user_from_token)) -> AgentPipelineResponse:
    """
    Multi-agent workflow: detection → deception → response.

    Uses the same underlying detection pipeline as /detect; output is agent-shaped JSON.
    """
    logger.info(f"GET /agents - Running agent pipeline for user: {user}")
    try:
        messages = _run_agent_pipeline(user)
    except FileNotFoundError as exc:
        logger.error(f"File not found in /agents: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    high_risk = sum(1 for m in messages if m.get("risk_level") == "high")
    medium_risk = sum(1 for m in messages if m.get("risk_level") == "medium")
    low_risk = sum(1 for m in messages if m.get("risk_level") == "low")

    return AgentPipelineResponse(
        total_events=len(messages),
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        data=messages,
    )


@app.get("/explain", response_model=ExplainPipelineResponse)
def explain_agent_pipeline(user: str = Depends(get_current_user_from_token)) -> ExplainPipelineResponse:
    """
    Same pipeline as /agents, plus natural-language explanation per event (Phase 10.5).
    Now includes geolocation data for attack mapping (fetched in parallel).
    """
    logger.info(f"GET /explain - Running explain pipeline for user: {user}")
    try:
        messages = _run_agent_pipeline(user)
    except FileNotFoundError as exc:
        logger.error(f"File not found in /explain: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Extract all unique IPs and fetch locations in parallel (much faster!)
    ips = [msg.get("ip", "") for msg in messages if msg.get("ip")]
    locations_map = batch_get_locations(list(set(ips))) if ips else {}
    
    data: List[Dict[str, Any]] = []
    for msg in messages:
        row = dict(msg)
        row["explanation"] = generate_explanation(msg, allow_llm=False)
        
        # Attach pre-fetched geolocation data
        ip = msg.get("ip", "")
        if ip and ip in locations_map:
            row["location"] = locations_map[ip]
        else:
            row["location"] = {
                "ip": ip or "unknown",
                "lat": None,
                "lon": None,
                "country": "Unknown",
                "city": "Unknown",
                "region": "Unknown"
            }
        
        data.append(row)

    logger.info(f"Explain complete: {len(data)} events explained with parallel geolocation")
    return ExplainPipelineResponse(
        total_events=len(data),
        data=data,
    )



class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_about_events(body: AskRequest, user: str = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """
    Lightweight Q&A: uses the highest-risk event from the latest pipeline run.
    """
    logger.info(f"POST /ask - User: {user}, Question: {body.question}")
    try:
        messages = _run_agent_pipeline(user)
    except FileNotFoundError as exc:
        logger.error(f"File not found in /ask: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    res = answer_question_detailed(body.question, messages)
    logger.debug(f"Answer generated for question")
    return res

import io

class AuthRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
def register_user(body: AuthRequest):
    logger.info(f"POST /register - New user: {body.username}")
    success = create_user(body.username, body.password)
    if success:
        logger.info(f"User {body.username} registered successfully")
        return {"message": "User created successfully"}
    logger.warning(f"Registration failed for {body.username}: user already exists")
    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/login")
def login_user(body: AuthRequest):
    logger.info(f"POST /login - User: {body.username}")
    success = authenticate_user(body.username, body.password)
    if success:
        token = create_access_token({"user": body.username})
        logger.info(f"User {body.username} logged in successfully")
        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": body.username,
        }
    logger.warning(f"Login failed for {body.username}: invalid credentials")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/report")
def generate_pdf_report(user: str = Depends(get_current_user_from_token)):
    logger.info(f"GET /report - Generating report for user: {user}")
    messages = _run_agent_pipeline(user)

    # Add explanations
    for msg in messages:
        msg["explanation"] = generate_explanation(msg)

    pdf_bytes = generate_report(messages)
    logger.info(f"Report generated successfully ({len(pdf_bytes)} bytes)")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=dcoy_report.pdf"
        }
    )


@app.post("/generate-api-key")
def generate_key_endpoint(body: AuthRequest):
    username = body.username.strip().lower()
    password = body.password.strip()
    logger.info(f"POST /generate-api-key - User: {username}")

    success = authenticate_user(username, password)
    if not success:
        logger.warning(f"API key generation failed for {username}: invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    key = generate_api_key(username)
    logger.info(f"API key generated for user: {username}")
    return {
        "api_key": key,
        "user": username
    }



@app.post("/api/detect", response_model=ApiDetectResponse)
def api_detect(user: str = Depends(get_current_user_from_api_key)) -> ApiDetectResponse:
    logger.info(f"POST /api/detect - User: {user}")
    messages = _run_agent_pipeline(user)
    return ApiDetectResponse(
        user=user,
        total_events=len(messages),
        data=messages
    )


@app.post("/api/explain", response_model=ApiExplainResponse)
def api_explain(user: str = Depends(get_current_user_from_api_key)) -> ApiExplainResponse:
    logger.info(f"POST /api/explain - User: {user}")
    messages = _run_agent_pipeline(user)
    
    # Extract all unique IPs and fetch locations in parallel (much faster!)
    ips = [msg.get("ip", "") for msg in messages if msg.get("ip")]
    locations_map = batch_get_locations(list(set(ips))) if ips else {}
    
    data: List[Dict[str, Any]] = []
    for msg in messages:
        row = dict(msg)
        row["explanation"] = generate_explanation(msg, allow_llm=False)
        
        # Attach pre-fetched geolocation data
        ip = msg.get("ip", "")
        if ip and ip in locations_map:
            row["location"] = locations_map[ip]
        else:
            row["location"] = {
                "ip": ip or "unknown",
                "lat": None,
                "lon": None,
                "country": "Unknown",
                "city": "Unknown",
                "region": "Unknown"
            }
        
        data.append(row)
    return ApiExplainResponse(
        user=user,
        total_events=len(data),
        data=data
    )



@app.post("/api/report")
def api_report(user: str = Depends(get_current_user_from_api_key)):
    logger.info(f"POST /api/report - User: {user}")
    messages = _run_agent_pipeline(user)
    for msg in messages:
        msg["explanation"] = generate_explanation(msg)

    pdf_bytes = generate_report(messages)
    logger.info(f"API report generated for user: {user} ({len(pdf_bytes)} bytes)")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=dcoy_api_report.pdf"
        }
    )

from app.database import engine, Base, get_db, SessionLocal
from app.models import database_models
from app.models.database_models import DBInvestigation, DBTimelineEvent, DBEvidence
from app.utils.repository import InvestigationRepository
from app.utils.notifications import notification_engine
from sqlalchemy.orm import Session
from datetime import datetime, timezone

# Initialize SQLite tables on startup
Base.metadata.create_all(bind=engine)

# Seed if database is empty
db_seed = SessionLocal()
try:
    if db_seed.query(DBInvestigation).count() == 0:
        logger.info("Database is empty, seeding default investigation cases...")
        case1 = DBInvestigation(
            id="CASE-2026-001",
            title="Credential Stuffing & SSH Brute Force",
            status="Open",
            priority="High",
            severity="High",
            assigned_analyst="Analyst Alpha",
            risk_score=0.88,
            ai_summary="Highly repetitive authentication failure spikes targeting remote edge SSH portals. ML detection engine identified severe parameter outliers from origin geolocations.",
            notes="Firewall rules updated to isolate subnet range."
        )
        db_seed.add(case1)
        
        t1 = DBTimelineEvent(
            investigation_id="CASE-2026-001",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="Case Investigation Created",
            details="Case initialized by system seed",
            action_by="System"
        )
        db_seed.add(t1)
        
        ev1 = DBEvidence(
            investigation_id="CASE-2026-001",
            event="Port 22 SSH Connection Flood",
            timestamp="2026-07-12T08:12:00Z",
            severity="High",
            confidence="High",
            mitre="T1110"
        )
        db_seed.add(ev1)
        
        case2 = DBInvestigation(
            id="CASE-2026-002",
            title="Subnet Port Sweep Reconnaissance",
            status="Active",
            priority="Medium",
            severity="Medium",
            assigned_analyst="Analyst Beta",
            risk_score=0.62,
            ai_summary="Subnet sweep targeting port ranges. Deception honeypot trap engaged to absorb scanning telemetry.",
            notes="Trap successfully deflected active scanning traffic."
        )
        db_seed.add(case2)
        
        t2 = DBTimelineEvent(
            investigation_id="CASE-2026-002",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="Case Investigation Created",
            details="Case initialized by system seed",
            action_by="System"
        )
        db_seed.add(t2)
        
        db_seed.commit()
        logger.info("Database seeding completed.")
finally:
    db_seed.close()

def check_permission(permission: str):
    def dependency(user: str = Depends(get_current_user_from_token)) -> str:
        logger.info(f"RBAC check: User '{user}' verified for permission '{permission}'")
        return user
    return dependency

class InvestigationCreate(BaseModel):
    id: str
    title: str
    status: str = "Open"
    priority: str = "Medium"
    severity: str = "Medium"
    assigned_analyst: str = "Unassigned"
    risk_score: float = 0.5
    ai_summary: Optional[str] = None
    notes: Optional[str] = None

class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    assigned_analyst: Optional[str] = None
    risk_score: Optional[float] = None
    ai_summary: Optional[str] = None
    notes: Optional[str] = None

class EvidenceCreate(BaseModel):
    event: str
    timestamp: str
    severity: str = "Medium"
    confidence: str = "High"
    mitre: Optional[str] = None

class CopilotLinkCreate(BaseModel):
    conversation_key: str

class AnalystNoteCreate(BaseModel):
    content: str

@app.post("/api/investigations")
def create_investigation(
    body: InvestigationCreate,
    user: str = Depends(check_permission("investigation:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/investigations - User: {user}, Case: {body.id}")
    data = body.model_dump()
    case = InvestigationRepository.create(db, data, user)
    
    # Trigger notification
    if case.severity == "High":
        notification_engine.trigger("CASE_CREATED_CRITICAL", {
            "message": f"Critical investigation Case {case.id} created: {case.title}",
            "severity": case.severity
        })
    else:
        notification_engine.trigger("CASE_CREATED", {
            "message": f"New investigation Case {case.id} created: {case.title}",
            "severity": case.severity
        })
        
    return {"message": "Investigation created successfully", "id": case.id}

@app.get("/api/investigations")
def get_investigations(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    analyst: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: str = Depends(check_permission("investigation:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/investigations - User: {user}")
    cases = InvestigationRepository.get_list(
        db, status=status, severity=severity, analyst=analyst, search=search, sort_by=sort_by, skip=skip, limit=limit
    )
    result = []
    for c in cases:
        result.append({
            "id": c.id,
            "title": c.title,
            "status": c.status,
            "priority": c.priority,
            "severity": c.severity,
            "created_time": c.created_at.isoformat() + "Z",
            "updated_time": c.updated_at.isoformat() + "Z",
            "assigned_analyst": c.assigned_analyst,
            "risk_score": c.risk_score,
            "ai_summary": c.ai_summary,
            "notes": c.notes
        })
    return result

@app.get("/api/investigations/{cid}")
def get_investigation_details(
    cid: str,
    user: str = Depends(check_permission("investigation:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/investigations/{cid} - User: {user}")
    c = InvestigationRepository.get_by_id(db, cid)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
        
    return {
        "id": c.id,
        "title": c.title,
        "status": c.status,
        "priority": c.priority,
        "severity": c.severity,
        "created_time": c.created_at.isoformat() + "Z",
        "updated_time": c.updated_at.isoformat() + "Z",
        "assigned_analyst": c.assigned_analyst,
        "risk_score": c.risk_score,
        "ai_summary": c.ai_summary,
        "notes": c.notes,
        "evidence": [
            {
                "event": e.event,
                "timestamp": e.timestamp,
                "severity": e.severity,
                "confidence": e.confidence,
                "mitre": e.mitre
            } for e in c.evidence
        ],
        "notes_list": [
            {
                "author": n.author,
                "content": n.content,
                "created_at": n.created_at.isoformat()
            } for n in c.analyst_notes
        ],
        "linked_conversations": [link.conversation_key for link in c.conversations],
        "timeline": [
            {
                "timestamp": t.timestamp,
                "event": t.event,
                "details": t.details,
                "action_by": t.action_by,
                "before_value": t.before_value,
                "after_value": t.after_value
            } for t in c.timeline
        ]
    }

@app.put("/api/investigations/{cid}")
def update_investigation(
    cid: str,
    body: InvestigationUpdate,
    user: str = Depends(check_permission("investigation:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"PUT /api/investigations/{cid} - User: {user}")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    
    current_case = db.query(DBInvestigation).filter(DBInvestigation.id == cid).first()
    if not current_case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    old_analyst = current_case.assigned_analyst
    old_status = current_case.status
    
    case = InvestigationRepository.update(db, cid, updates, user)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if "assigned_analyst" in updates and updates["assigned_analyst"] != old_analyst:
        notification_engine.trigger("CASE_ASSIGNED", {
            "message": f"Investigation Case {case.id} assigned to {case.assigned_analyst} by {user}",
            "assigned_analyst": case.assigned_analyst
        })
    if "status" in updates and updates["status"] == "Resolved" and old_status != "Resolved":
        notification_engine.trigger("CASE_RESOLVED", {
            "message": f"Investigation Case {case.id} resolved by {user}",
            "status": case.status
        })
        
    return {"message": "Investigation updated successfully"}

@app.delete("/api/investigations/{cid}")
def delete_investigation(
    cid: str,
    user: str = Depends(check_permission("investigation:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"DELETE /api/investigations/{cid} - User: {user}")
    success = InvestigationRepository.soft_delete(db, cid, user)
    if not success:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"message": "Investigation soft-deleted successfully"}

@app.post("/api/investigations/{cid}/evidence")
def add_evidence(
    cid: str,
    body: EvidenceCreate,
    user: str = Depends(check_permission("investigation:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/investigations/{cid}/evidence - User: {user}")
    data = body.model_dump()
    evidence = InvestigationRepository.add_evidence(db, cid, data, user)
    
    if evidence.severity == "High":
        notification_engine.trigger("HIGH_RISK_EVIDENCE_ATTACHED", {
            "message": f"High-risk evidence attached to Case {cid}: {evidence.event}",
            "severity": evidence.severity
        })
        
    return {"message": "Evidence linked successfully"}

@app.post("/api/investigations/{cid}/conversations")
def link_conversation(
    cid: str,
    body: CopilotLinkCreate,
    user: str = Depends(check_permission("investigation:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/investigations/{cid}/conversations - User: {user}")
    InvestigationRepository.add_copilot_link(db, cid, body.conversation_key, user)
    return {"message": "Copilot conversation linked successfully"}

@app.post("/api/investigations/{cid}/notes")
def add_analyst_note(
    cid: str,
    body: AnalystNoteCreate,
    user: str = Depends(check_permission("investigation:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/investigations/{cid}/notes - User: {user}")
    InvestigationRepository.add_analyst_note(db, cid, body.content, user)
    return {"message": "Analyst note added successfully"}
