"""Deception, playbooks, and SOAR response orchestration router."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies.auth import check_permission
from app.database import get_db
from app.models.playbook import DBPlaybookExecution
from app.models.workflow import DBWorkflowExecution
from app.services.container import container

logger = logging.getLogger(__name__)

router = APIRouter()


class CustomPlaybookPayload(BaseModel):
    name: str
    description: str
    steps: List[str]
    estimated_duration_minutes: int = 30
    category: str = "Incident Response"


class TriggerPlaybookPayload(BaseModel):
    investigation_id: str
    playbook_id: int


class UpdateExecutionStepPayload(BaseModel):
    step_index: Optional[int] = None
    status: Optional[str] = None
    note: Optional[str] = ""
    notes: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None


class CreateWorkflowPayload(BaseModel):
    name: str
    description: str
    trigger_type: str
    steps: List[Dict[str, Any]]


class ApproveWorkflowStepPayload(BaseModel):
    note: str


@router.get("/api/playbooks", summary="List Response Playbooks", description="Returns configured response playbook templates.")
def get_playbooks(
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/playbooks - User: {user}")
    return container.playbook_engine.get_all_playbooks(db)


@router.post("/api/playbooks", summary="Create Response Playbook", description="Creates new custom response playbook template.")
def create_playbook(
    body: CustomPlaybookPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/playbooks - User: {user}")
    return container.playbook_engine.create_playbook_template(
        db, body.name, body.description, body.steps, body.estimated_duration_minutes, body.category
    )


@router.get("/api/playbooks/executions", summary="List Playbook Executions", description="Returns playbook execution history for case or all cases.")
def get_playbook_executions(
    case_id: Optional[str] = None,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/playbooks/executions - User: {user}, CaseID: {case_id}")
    if case_id:
        return container.playbook_engine.get_executions_for_case(db, case_id)
    return db.query(DBPlaybookExecution).all()


@router.post("/api/playbooks/executions", summary="Trigger Playbook Execution", description="Executes response playbook against target investigation case.")
def trigger_playbook_execution(
    body: TriggerPlaybookPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/playbooks/executions - User: {user}, CaseID: {body.investigation_id}")
    return container.playbook_engine.trigger_playbook(db, body.investigation_id, body.playbook_id)


@router.put("/api/playbooks/executions/{eid}", summary="Update Playbook Step Status", description="Updates status and evidence notes for playbook execution step.")
def update_playbook_execution(
    eid: int,
    body: UpdateExecutionStepPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"PUT /api/playbooks/executions/{eid} - User: {user}")
    execution = container.playbook_engine.get_playbook_execution(db, eid)
    if not execution:
        raise HTTPException(status_code=404, detail="Playbook execution not found")
        
    if body.step_index is not None and body.status is not None:
        execution = container.playbook_engine.update_execution_step(
            db, eid, body.step_index, body.status, body.note or ""
        )
    if body.notes is not None or body.evidence is not None:
        execution = container.playbook_engine.update_execution_notes_and_evidence(
            db, eid, body.notes, body.evidence
        )
    return execution


@router.get("/api/incident-response/kpis", summary="Incident Response KPIs", description="Calculates Incident Response MTTR and automation containment stats.")
def get_incident_kpis_endpoint(
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/incident-response/kpis - User: {user}")
    return container.incident_service.get_incident_kpis(db)


@router.get("/api/soar/workflows", summary="List SOAR Workflows", description="Returns active SOAR orchestration workflows.")
def get_soar_workflows(
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/soar/workflows - User: {user}")
    return container.workflow_engine.get_workflows(db)


@router.post("/api/soar/workflows", summary="Create SOAR Workflow", description="Registers new automated SOAR workflow definition.")
def create_soar_workflow(
    body: CreateWorkflowPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/soar/workflows - User: {user}")
    return container.workflow_engine.create_workflow(db, body.name, body.description, body.trigger_type, body.steps)


@router.get("/api/soar/executions", summary="List SOAR Executions", description="Returns history of executed SOAR workflows.")
def get_soar_executions(
    case_id: Optional[str] = None,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /api/soar/executions - User: {user}, CaseID: {case_id}")
    if case_id:
        return db.query(DBWorkflowExecution).filter(DBWorkflowExecution.linked_investigation_id == case_id).all()
    return db.query(DBWorkflowExecution).all()


@router.post("/api/soar/executions/{eid}/approve", summary="Approve SOAR Workflow Step", description="Approve manual operator step checkpoint to resume suspended SOAR workflow.")
def approve_soar_workflow_step(
    eid: int,
    body: ApproveWorkflowStepPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/soar/executions/{eid}/approve - User: {user}")
    execution = container.workflow_engine.approve_workflow_step(db, eid, body.note)
    if not execution:
        raise HTTPException(status_code=404, detail="Workflow execution not found or not suspended.")
    return execution
