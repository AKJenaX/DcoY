"""Structured request logging and metrics middleware."""

import logging
import time
from fastapi import FastAPI, Request
from app.services.container import container
from app.utils.metrics import metrics_collector
from app.middleware.correlation import get_current_request_id

logger = logging.getLogger(__name__)


def setup_logging_middleware(app: FastAPI) -> None:
    """Configure request logging middleware for observability metrics."""
    
    @app.middleware("http")
    async def log_requests_observability(request: Request, call_next):
        t_start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - t_start) * 1000.0
        req_id = getattr(request.state, "request_id", get_current_request_id())
        
        extra_data = {
            "extra_fields": {
                "request_id": req_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2)
            }
        }
        logger.info(
            f"API Request [{req_id}]: {request.method} {request.url.path} finished with status {response.status_code} in {round(duration_ms, 2)}ms",
            extra=extra_data
        )
        
        try:
            container.platform_registry.log_latency(duration_ms)
            metrics_collector.record_request(request.url.path, duration_ms)
        except Exception:
            pass
            
        return response
