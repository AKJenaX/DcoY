"""Request correlation middleware injecting unique request IDs."""

import uuid
from contextvars import ContextVar
from fastapi import FastAPI, Request

REQUEST_ID_CTX_VAR: ContextVar[str] = ContextVar("request_id", default="")


def get_current_request_id() -> str:
    """Retrieve current request ID from context variable."""
    return REQUEST_ID_CTX_VAR.get()


def setup_correlation_middleware(app: FastAPI) -> None:
    """Configure request correlation ID middleware."""

    @app.middleware("http")
    async def correlate_requests(request: Request, call_next):
        incoming_id = request.headers.get("X-Request-ID")
        request_id = incoming_id.strip() if incoming_id else uuid.uuid4().hex
        
        request.state.request_id = request_id
        token = REQUEST_ID_CTX_VAR.set(request_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            REQUEST_ID_CTX_VAR.reset(token)
