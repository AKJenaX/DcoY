"""FastAPI application entry point for DcoY."""

import logging
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents import deception_agent, detection_agent, response_agent
from app.agents.reasoning_agent import answer_question, generate_explanation
from app.config import settings
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
        # Backward-compatible fallback for legacy dashboard/testing flows.
        return "default_user"

    token = authorization.replace("Bearer ", "", 1).strip()
    if not token:
        return "default_user"
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = payload.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token payload")
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


@app.post("/api/ingest")
def ingest_events(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Live event ingestion endpoint.
    
    Accepts a payload with event data and stores them in memory.
    Keeps only the last 100 events.
    
    Args:
        payload: Dictionary with "data" key containing list of events
        
    Returns:
        Success message with event count
        
    Example:
        POST /api/ingest
        {
            "data": [
                {"ip": "192.168.1.1", "failed_logins": 5, ...},
                {"ip": "192.168.1.2", "failed_logins": 10, ...}
            ]
        }
    """
    logger.info("POST /api/ingest - Ingesting live events")
    
    try:
        data = payload.get("data", [])
        
        if not isinstance(data, list):
            logger.warning("Invalid payload: 'data' must be a list")
            raise HTTPException(status_code=400, detail="'data' must be a list")
        
        count = 0
        for event in data:
            if isinstance(event, dict):
                add_event(event)
                count += 1
        
        logger.info(f"Ingested {count} events. Total in store: {len(get_events())}")
        
        return {
            "message": "Events ingested successfully",
            "count": count,
            "total_in_store": len(get_events())
        }
    
    except Exception as e:
        logger.error(f"Error ingesting events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/capture")
def capture_event() -> Dict[str, Any]:
    event = capture_basic_event()

    if event:
        add_event(event)
        return {"message": "Captured event", "event": event}

    return {"message": "Capture failed"}


@app.get("/detect")
def run_anomaly_detection() -> Dict[str, Any]:
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

    return {
        "total_records": len(data),
        "anomalies_detected": anomalies_detected,
        "attack_summary": attack_summary,
        "response_summary": response_summary,
        "data": data,
    }


@app.get("/agents")
def run_agent_pipeline(user: str = Depends(get_current_user_from_token)) -> Dict[str, Any]:
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

    return {
        "total_events": len(messages),
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "data": messages,
    }


@app.get("/explain")
def explain_agent_pipeline(user: str = Depends(get_current_user_from_token)) -> Dict[str, Any]:
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
    return {
        "total_events": len(data),
        "data": data,
    }


class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_about_events(body: AskRequest) -> Dict[str, str]:
    """
    Lightweight Q&A: uses the highest-risk event from the latest pipeline run.
    """
    logger.info(f"POST /ask - Question: {body.question}")
    try:
        messages = _run_agent_pipeline()
    except FileNotFoundError as exc:
        logger.error(f"File not found in /ask: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    answer = answer_question(body.question, messages)
    logger.debug(f"Answer generated for question")
    return {"answer": answer}

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


def get_current_user_from_api_key(x_api_key: str = Header(None)):
    x_api_key = x_api_key.strip() if x_api_key else None
    if not x_api_key:
        logger.warning("API request missing API key header")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    user = validate_api_key(x_api_key)
    if not user:
        logger.warning("API request with invalid API key")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    return user


@app.post("/api/detect")
def api_detect(user: str = Depends(get_current_user_from_api_key)):
    logger.info(f"POST /api/detect - User: {user}")
    messages = _run_agent_pipeline(user)
    return {
        "user": user,
        "total_events": len(messages),
        "data": messages
    }


@app.post("/api/explain")
def api_explain(user: str = Depends(get_current_user_from_api_key)):
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
    return {
        "user": user,
        "total_events": len(data),
        "data": data
    }


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
