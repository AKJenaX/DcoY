"""FastAPI application entry point for DcoY."""

import logging
from typing import Any, Dict, List
from fastapi import FastAPI

from app.config import settings
from app.lifecycle import lifespan
from app.middleware.cors import setup_cors_middleware
from app.middleware.logging import setup_logging_middleware
from app.middleware.correlation import setup_correlation_middleware
from app.utils.observability import setup_observability
from app.utils.errors import setup_exception_handlers
from app.dependencies.auth import (
    get_current_user_from_token,
    get_current_user_from_api_key,
    check_permission,
)
from app.services.pipeline import run_agent_pipeline

# Initialize structured observability logging
setup_observability(log_level=settings.LOG_LEVEL, json_format=settings.LOG_FORMAT_JSON)
logger = logging.getLogger(__name__)

# Instantiate FastAPI application
app = FastAPI(
    title="DcoY Enterprise Security Platform",
    description="""
    ## DcoY REST API v1.0
    
    Welcome to the DcoY Enterprise Threat Defense and Deception Platform API.
    
    This API provides endpoints for:
    * **Threat Intelligence & Fusion**
    * **Anomaly Detection & Rules Engine**
    * **Deception Decoy System & Honeypots**
    * **Incident Response & Playbooks Orchestration**
    * **SOAR Workflow Automation**
    * **Security Knowledge Graph & Attack Path Analysis**
    * **Platform Health Monitoring & Diagnostics**
    """,
    version="1.0.0-rc1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure middleware & exception handlers
setup_correlation_middleware(app)
setup_cors_middleware(app)
setup_logging_middleware(app)
setup_exception_handlers(app)

logger.info("Starting DcoY API with Structured Observability & Correlation Tracking")
logger.info("CORS, Request Correlation, and Exception Middleware configured successfully")

# Include Router Modules with Domain OpenAPI Tags
from app.routers import (
    health,
    auth,
    reports,
    copilot,
    detection,
    deception,
    executive,
    investigation,
    simulation,
    websocket,
)

app.include_router(health.router, tags=["Health & Diagnostics"])
app.include_router(auth.router, tags=["Authentication & API Keys"])
app.include_router(reports.router, tags=["Report Generation"])
app.include_router(copilot.router, tags=["AI Copilot & Reasoning"])
app.include_router(detection.router, tags=["Anomaly Detection & Rules Engine"])
app.include_router(deception.router, tags=["Deception & SOAR Orchestration"])
app.include_router(executive.router, tags=["Executive Intelligence"])
app.include_router(investigation.router, tags=["Investigations & Knowledge Graph"])
app.include_router(simulation.router, tags=["Telemetry & Simulations"])
app.include_router(websocket.router, tags=["WebSockets"])


# Alias helper re-export for backward compatibility
def _run_agent_pipeline(user: str = "default_user") -> List[Dict[str, Any]]:
    return run_agent_pipeline(user)
