"""Structured Observability, JSON Logging, and Request Correlation utilities."""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from app.middleware.correlation import get_current_request_id


class StructuredJsonFormatter(logging.Formatter):
    """Custom logging formatter that serializes log records to JSON structure."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = getattr(record, "request_id", None) or get_current_request_id() or "N/A"
        
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": req_id,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName
        }

        # Include traceback details if exceptions occurred
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        # Include custom extra values passed dynamically
        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, dict):
            log_payload.update(extra_fields)

        return json.dumps(log_payload)


def setup_observability(log_level: str = "INFO", json_format: bool = False):
    """Configure platform-wide root logging handler setups."""
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers
    if root_logger.handlers:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    if json_format:
        handler.setFormatter(StructuredJsonFormatter())
    else:
        # Standard clean human-readable formatter for local development
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    root_logger.addHandler(handler)
    logging.getLogger("uvicorn.access").disabled = True
