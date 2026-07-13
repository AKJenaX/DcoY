"""Structured Observability and JSON Logging utility."""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict


class StructuredJsonFormatter(logging.Formatter):
    """Custom logging formatter that serializes log records to JSON structure."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName
        }

        # Include traceback details if exceptions occurred
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        # Include custom extra values passed dynamically
        if hasattr(record, "extra_fields"):
            log_payload.update(record.extra_fields)

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
    logging.getLogger("uvicorn.access").disabled = True  # disable redundant access logs
