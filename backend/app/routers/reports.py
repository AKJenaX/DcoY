"""PDF and operational report generation router."""

import io
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies.auth import get_current_user_from_token, get_current_user_from_api_key
from app.services.pipeline import run_agent_pipeline
from app.agents.reasoning_agent import generate_explanation
from app.utils.report_generator import generate_report

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report")
def generate_pdf_report(user: str = Depends(get_current_user_from_token)):
    logger.info(f"GET /report - Generating report for user: {user}")
    messages = run_agent_pipeline(user)

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


@router.post("/api/report")
def api_report(user: str = Depends(get_current_user_from_api_key)):
    logger.info(f"POST /api/report - User: {user}")
    messages = run_agent_pipeline(user)
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
