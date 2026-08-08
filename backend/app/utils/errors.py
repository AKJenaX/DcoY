"""Standardized error categories and exception handling helpers."""

from datetime import datetime, timezone
from enum import Enum
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.middleware.correlation import get_current_request_id

logger = logging.getLogger(__name__)


class ErrorCategory(str, Enum):
    """Standardized error classification categories."""

    VALIDATION = "Validation"
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    EXTERNAL_SERVICE = "External Service"
    DATABASE = "Database"
    INTERNAL = "Internal"


class PlatformException(Exception):
    """Base application exception supporting classified error payloads."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        status_code: int = 500,
        details: Optional[Any] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.category = category
        self.status_code = status_code
        self.details = details


def build_error_response(
    status_code: int,
    message: str,
    category: ErrorCategory,
    details: Optional[Any] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Format consistent error response structure."""
    req_id = request_id or get_current_request_id() or "N/A"
    payload: Dict[str, Any] = {
        "error": {
            "code": status_code,
            "category": category.value,
            "message": message,
            "request_id": req_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    if details:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def setup_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers for structured error classification."""

    @app.exception_handler(PlatformException)
    async def platform_exception_handler(request: Request, exc: PlatformException):
        req_id = getattr(request.state, "request_id", get_current_request_id())
        logger.error(
            f"PlatformException [{req_id}] ({exc.category}): {exc.message}",
            extra={"extra_fields": {"category": exc.category.value, "request_id": req_id}}
        )
        return build_error_response(
            status_code=exc.status_code,
            message=exc.message,
            category=exc.category,
            details=exc.details,
            request_id=req_id
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", get_current_request_id())
        logger.warning(f"RequestValidationError [{req_id}]: {str(exc)}")
        return build_error_response(
            status_code=422,
            message="Request payload validation error",
            category=ErrorCategory.VALIDATION,
            details=exc.errors(),
            request_id=req_id
        )
