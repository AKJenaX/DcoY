"""Executive metrics and platform search router."""

import logging
import time
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import check_permission
from app.database import get_db
from app.services.pipeline import run_agent_pipeline
from app.utils.geo_utils import batch_get_locations
from app.services.executive_metrics import build_executive_metrics
from app.services.container import container

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/api/executive/metrics",
    summary="Executive SOC Metrics",
    description="Returns operational SOC metrics, top attack vectors, and detection rule performance stats."
)
def get_executive_metrics(
    user: str = Depends(check_permission("executive:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/executive/metrics - User: {user}")
    messages = run_agent_pipeline(user)

    ips = [msg.get("ip", "") for msg in messages if msg.get("ip")]
    locations_map = batch_get_locations(list(set(ips))) if ips else {}
    enriched_messages: List[Dict[str, Any]] = []
    for msg in messages:
        row = dict(msg)
        ip = row.get("ip", "")
        row["location"] = locations_map.get(
            ip,
            {
                "ip": ip or "unknown",
                "lat": None,
                "lon": None,
                "country": "Unknown",
                "city": "Unknown",
                "region": "Unknown",
            },
        )
        enriched_messages.append(row)

    return build_executive_metrics(
        db=db,
        telemetry=enriched_messages,
        rule_metrics=container.rule_engine.metrics.get_all_metrics(),
    )


@router.get(
    "/api/soar/platform/search",
    summary="Platform Global Search",
    description="Searches across Cases, Detection Rules, Threat Indicators, and Assets."
)
def run_platform_global_search(
    query: str,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/soar/platform/search - User: {user}, query={query}")
    t_start = time.perf_counter()
    results = container.search_service.search_all(db, query)
    container.platform_registry.log_latency((time.perf_counter() - t_start) * 1000.0)
    return results
