"""Health, liveness, readiness probes, and telemetry metrics router."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies.auth import get_current_user_from_token
from app.services.container import container

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", summary="Root API status check", description="Returns simple status payload indicating API is running.")
def read_root() -> Dict[str, str]:
    """Simple test route to verify the API is running."""
    logger.debug("GET / - Health check (root endpoint)")
    return {
        "message": "DcoY API is running",
        "app": settings.APP_NAME,
    }


@router.get("/health", summary="Health check endpoint", description="Diagnostic endpoint for health pings.")
def health_check() -> Dict[str, str]:
    """Explicit health check endpoint for frontend diagnostic pings."""
    logger.debug("GET /health - Health check endpoint")
    return {
        "status": "ok",
        "service": settings.APP_NAME
    }


@router.get("/health/live", summary="Liveness probe", description="Fast probe returning 200 if server process is running.")
def liveness_probe() -> Dict[str, Any]:
    """Kubernetes/Container liveness probe endpoint."""
    return {
        "status": "live",
        "service": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ready", summary="Readiness probe", description="Deep readiness probe verifying DB connectivity and security engine status.")
def readiness_probe(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Kubernetes/Container readiness probe checking critical infrastructure dependencies."""
    checks = {}
    is_ready = True

    # 1. Verify Database Connectivity
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        logger.error(f"Readiness check failed - Database error: {str(e)}")
        checks["database"] = f"error: {str(e)}"
        is_ready = False

    # 2. Verify Service Container Singletons
    try:
        if (
            container.rule_engine is not None
            and container.workflow_engine is not None
            and container.knowledge_graph_engine is not None
        ):
            checks["service_container"] = "ok"
        else:
            checks["service_container"] = "error: uninitialized container engines"
            is_ready = False
    except Exception as e:
        logger.error(f"Readiness check failed - Container error: {str(e)}")
        checks["service_container"] = f"error: {str(e)}"
        is_ready = False

    # 3. Verify Metrics Telemetry Collector
    checks["metrics_collector"] = "ok" if container.metrics_collector is not None else "degraded"

    if not is_ready:
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "checks": checks}
        )

    return {
        "status": "ready",
        "service": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks
    }


@router.get("/metrics", summary="Application metrics", description="Returns telemetry metrics (requests, latencies, cache, websockets, auth).")
def get_operational_metrics() -> Dict[str, Any]:
    """Expose application metrics snapshot for operational monitoring."""
    return container.metrics_collector.get_metrics_snapshot()


@router.get("/api/soar/platform/health", summary="Platform metrics", description="Returns component health statuses and latency metrics.")
def get_platform_health(user: str = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get system health metrics, component statuses, and telemetry latency."""
    return container.platform_registry.get_health_metrics()


@router.get("/api/soar/platform/api-inventory", summary="API inventory", description="Returns operational inventory of platform endpoints.")
def get_api_inventory(user: str = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get inventory of registered API endpoints and their operational status."""
    return container.platform_registry.get_api_inventory()


@router.get("/api/soar/platform/docs", summary="Platform documentation", description="Returns documentation guides and architectural overview.")
def get_platform_docs(
    category: str = Query("all", description="Category filter"),
    user: str = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Get platform documentation topics and architectural guides."""
    return container.platform_registry.get_documentation(category)
