"""Telemetry ingestion, network capture, and purple team simulation router."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, cast
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user_from_api_key, check_permission
from app.database import get_db, SessionLocal
from app.models import IngestPayload, IngestResponse
from app.models.simulation import DBSimulationRun
from app.models.intelligence import DBThreatIndicator
from app.models.knowledge_graph import DBAsset, DBKnowledgeGraphEdge
from app.models.database_models import DBInvestigation, DBEvidence
from app.models.workflow import DBWorkflowExecution
from app.utils.live_store import add_event, get_events
from app.utils.network_capture import capture_basic_event
from app.utils.websocket_manager import broadcast_sync
from app.services.attack_simulator import AttackSimulator
from app.services.container import container

logger = logging.getLogger(__name__)

router = APIRouter()


class TriggerSimulationPayload(BaseModel):
    scenario_name: str


def run_simulation_task(db_session_factory, run_id: int, scenario_name: str):
    db = db_session_factory()
    try:
        simulator = AttackSimulator()
        sim_run = simulator.execute_simulation(db, scenario_name)
        
        existing_run = db.query(DBSimulationRun).filter(DBSimulationRun.id == run_id).first()
        if existing_run:
            existing_run.status = "Completed"
            existing_run.completed_at = sim_run.completed_at
            existing_run.scanned_events_count = sim_run.scanned_events_count
            existing_run.detection_success_rate = sim_run.detection_success_rate
            existing_run.missed_detections_count = sim_run.missed_detections_count
            existing_run.coverage_score = sim_run.coverage_score
            existing_run.average_detection_time_seconds = sim_run.average_detection_time_seconds
            existing_run.simulation_confidence = sim_run.simulation_confidence
            existing_run.mitre_techniques = sim_run.mitre_techniques
            existing_run.telemetry_data = sim_run.telemetry_data
            existing_run.results_data = sim_run.results_data
            
            db.delete(sim_run)
            db.commit()
    except Exception as e:
        logger.error(f"Error executing simulation in background: {str(e)}")
        existing_run = db.query(DBSimulationRun).filter(DBSimulationRun.id == run_id).first()
        if existing_run:
            existing_run.status = "Failed"
            db.commit()
    finally:
        db.close()


@router.post(
    "/api/ingest",
    response_model=IngestResponse,
    summary="Ingest Live Telemetry Events",
    description="Ingests live network threat events into memory buffer and broadcasts to WebSocket subscribers."
)
def ingest_events(payload: IngestPayload, user: str = Depends(get_current_user_from_api_key)) -> IngestResponse:
    """Live event ingestion endpoint."""
    logger.info("POST /api/ingest - Ingesting live events")
    
    try:
        count = 0
        for event in payload.data:
            event_dict = event.model_dump(exclude_none=True)
            add_event(event_dict)
            broadcast_sync("telemetry", event_dict)
            count += 1
        
        logger.info(f"Ingested {count} events. Total in store: {len(get_events())}")
        
        return IngestResponse(
            message="Events ingested successfully",
            count=count,
            total_in_store=len(get_events())
        )
    
    except Exception as e:
        logger.error(f"Error ingesting events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/api/capture",
    summary="Capture Real-Time Event",
    description="Captures live network frame or synthetic event and streams to subscribers."
)
def capture_event(user: str = Depends(get_current_user_from_api_key)) -> Dict[str, Any]:
    event = capture_basic_event()

    if event:
        add_event(event)
        broadcast_sync("telemetry", event)
        return {"message": "Captured event", "event": event}

    return {"message": "Capture failed"}


@router.post(
    "/api/simulations",
    summary="Trigger Purple Team Simulation",
    description="Launches background attack simulation exercise for specified adversary scenario."
)
def trigger_simulation(
    body: TriggerSimulationPayload,
    background_tasks: BackgroundTasks,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/simulations - User: {user}, Scenario: {body.scenario_name}")
    
    sim_run = DBSimulationRun(
        scenario_name=body.scenario_name,
        status="Running",
        started_at=datetime.now(timezone.utc),
        scanned_events_count=0,
        detection_success_rate=0.0,
        missed_detections_count=0,
        coverage_score=0.0,
        average_detection_time_seconds=0.0,
        simulation_confidence=0.0,
        results_data="{}"
    )
    db.add(sim_run)
    db.commit()
    db.refresh(sim_run)
    
    background_tasks.add_task(run_simulation_task, SessionLocal, cast(int, sim_run.id), cast(str, sim_run.scenario_name))
    return sim_run


@router.get(
    "/api/simulations",
    summary="List Simulation Runs",
    description="Returns list of past purple team simulation runs ordered by date."
)
def list_simulations(
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/simulations - User: {user}")
    return db.query(DBSimulationRun).order_by(DBSimulationRun.started_at.desc()).all()


@router.get(
    "/api/simulations/kpis",
    summary="Simulation KPIs",
    description="Calculates detection success rates, coverage scores, and average detection latency from simulations."
)
def get_simulations_kpis(
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/simulations/kpis - User: {user}")
    runs = db.query(DBSimulationRun).filter(DBSimulationRun.status == "Completed").all()
    total_runs = len(runs)
    
    if total_runs == 0:
        return {
            "scenarios_executed": 0,
            "detection_success_rate": 0.0,
            "missed_detections": 0,
            "coverage_score": 0.0,
            "average_detection_time": 0.0,
            "simulation_confidence": 0.0
        }
        
    avg_success = sum(cast(float, r.detection_success_rate) for r in runs) / total_runs
    total_missed = sum(cast(int, r.missed_detections_count) for r in runs)
    avg_coverage = sum(cast(float, r.coverage_score) for r in runs) / total_runs
    avg_time = sum(cast(float, r.average_detection_time_seconds) for r in runs) / total_runs
    avg_conf = sum(cast(float, r.simulation_confidence) for r in runs) / total_runs
    
    return {
        "scenarios_executed": total_runs,
        "detection_success_rate": round(avg_success, 4),
        "missed_detections": total_missed,
        "coverage_score": round(avg_coverage, 4),
        "average_detection_time": round(avg_time, 2),
        "simulation_confidence": round(avg_conf, 4)
    }


@router.post(
    "/api/soar/platform/demo/trigger",
    summary="Trigger Interactive Demo Scenario",
    description="Seeds synthetic attack scenario elements into graph, cases, indicators, and evidence."
)
def trigger_interactive_demo_scenario(
    user: str = Depends(check_permission("cases:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/soar/platform/demo/trigger - Triggering synthetic scenario - User: {user}")
    
    test_ip = "198.51.100.222"
    indicator = db.query(DBThreatIndicator).filter(DBThreatIndicator.ioc_value == test_ip).first()
    if not indicator:
        indicator = DBThreatIndicator(
            ioc_value=test_ip,
            ioc_type="IP",
            confidence_score=0.98,
            threat_feed="Synthetic Demo Attack Feed",
            status="Active"
        )
        db.add(indicator)
        db.commit()
        db.refresh(indicator)

    asset = db.query(DBAsset).filter(DBAsset.name == "WS-OPERATOR-02").first()
    if not asset:
        asset = DBAsset(
            name="WS-OPERATOR-02",
            ip_address="198.51.100.20",
            asset_type="Workstation",
            risk_score=0.88,
            criticality="High"
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)

    case_id = "CASE-DEMO-2026"
    case = db.query(DBInvestigation).filter(DBInvestigation.id == case_id).first()
    if not case:
        case = DBInvestigation(
            id=case_id,
            title="SSH Intrusion & Lateral Sweep [DEMO]",
            status="Open",
            priority="Critical",
            severity="Critical",
            assigned_analyst="SOC Team Lead",
            risk_score=0.92,
            ai_summary="Synthetic attack simulation replicating external brute force, user compromise, and lateral sweep."
        )
        db.add(case)
        db.commit()
        db.refresh(case)

    evidence = db.query(DBEvidence).filter(DBEvidence.investigation_id == case_id).first()
    if not evidence:
        evidence = DBEvidence(
            investigation_id=case_id,
            event=f"Failed SSH brute-forcing logs detected from {test_ip}",
            timestamp="2026-07-13T12:00:00Z",
            severity="High",
            confidence="High",
            mitre="T1110"
        )
        db.add(evidence)
        db.commit()

    edges_to_create = [
        ("Indicator:198.51.100.222", "Asset:HONEYPOT-SSH", "targets", 0.95, "Brute force target decoy"),
        ("Asset:HONEYPOT-SSH", "Case:CASE-DEMO-2026", "investigated_by", 0.90, "Telemetry escalated to case"),
        ("User:compromised_operator", "Case:CASE-DEMO-2026", "implicated_in", 0.85, "Operator credentials compromised")
    ]
    for src, tgt, rel, weight, desc in edges_to_create:
        edge = db.query(DBKnowledgeGraphEdge).filter(
            DBKnowledgeGraphEdge.source_id == src,
            DBKnowledgeGraphEdge.target_id == tgt,
            DBKnowledgeGraphEdge.relationship_type == rel
        ).first()
        if not edge:
            edge = DBKnowledgeGraphEdge(
                source_id=src,
                source_type=src.split(":")[0],
                target_id=tgt,
                target_type=tgt.split(":")[0],
                relationship_type=rel,
                weight=weight,
                description=desc
            )
            db.add(edge)
    db.commit()

    wf_exec = db.query(DBWorkflowExecution).filter(DBWorkflowExecution.workflow_name == "DEMO: Host Isolation").first()
    if not wf_exec:
        wf_exec = DBWorkflowExecution(
            workflow_id=99,
            workflow_name="DEMO: Host Isolation",
            status="Completed",
            execution_log_json='[{"type":"Containment","name":"Isolate WS-OPERATOR-02","status":"Completed"}]',
            linked_investigation_id=case_id
        )
        db.add(wf_exec)
        db.commit()

    container.knowledge_graph_engine.rebuild_graph(db)
    
    return {"status": "success", "message": "Synthetic attack demo scenario triggered successfully."}


@router.post(
    "/api/soar/platform/demo/clear",
    summary="Clear Interactive Demo Scenario",
    description="Purges synthetic demo records from graph and cases database tables."
)
def clear_interactive_demo_scenario(
    user: str = Depends(check_permission("cases:write")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/soar/platform/demo/clear - Cleaning synthetic demo records - User: {user}")
    
    test_ip = "198.51.100.222"
    case_id = "CASE-DEMO-2026"

    db.query(DBEvidence).filter(DBEvidence.investigation_id == case_id).delete()
    db.query(DBInvestigation).filter(DBInvestigation.id == case_id).delete()
    db.query(DBThreatIndicator).filter(DBThreatIndicator.ioc_value == test_ip).delete()
    db.query(DBWorkflowExecution).filter(DBWorkflowExecution.workflow_name == "DEMO: Host Isolation").delete()
    
    db.query(DBKnowledgeGraphEdge).filter(
        (DBKnowledgeGraphEdge.source_id == f"Indicator:{test_ip}") |
        (DBKnowledgeGraphEdge.target_id == f"Case:{case_id}")
    ).delete()
    db.commit()

    container.knowledge_graph_engine.rebuild_graph(db)
    return {"status": "success", "message": "Synthetic attack demo scenario cleared successfully."}
