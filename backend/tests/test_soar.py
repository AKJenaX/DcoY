"""Unit tests for the SOAR Workflow & Orchestration Engine."""

import json
import pytest
from typing import cast, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base
from app.models.database_models import DBInvestigation, DBTimelineEvent
from app.models.workflow import DBWorkflow, DBWorkflowExecution
from app.services.workflow_engine import WorkflowEngine
from app.services.incident_response import IncidentResponseService


# In-memory test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def case(db: Session) -> DBInvestigation:
    c = DBInvestigation(
        id="CASE-SOAR-001",
        title="Threat Simulation Attack Hook",
        status="Open",
        severity="High",
        risk_score=0.92
    )
    db.add(c)
    db.commit()
    return c


@pytest.fixture
def engine_service() -> WorkflowEngine:
    return WorkflowEngine()


def test_workflow_seeding(db: Session, engine_service: WorkflowEngine):
    engine_service.seed_default_workflows(db)
    count = db.query(DBWorkflow).count()
    assert count == 4
    
    wf = db.query(DBWorkflow).filter(DBWorkflow.name == "Auto Isolate High Severity Host").first()
    assert wf is not None
    assert wf.trigger_type == "Severity High"
    
    steps = json.loads(cast(str, wf.steps_json))
    assert len(steps) == 4
    assert steps[2]["name"] == "Isolate Host"


def test_create_custom_workflow(db: Session, engine_service: WorkflowEngine):
    steps = [
        {"type": "Action", "name": "Block IP", "parameter": "192.168.1.100"},
        {"type": "Action", "name": "Notify Teams", "parameter": "#incident-channel"}
    ]
    wf = engine_service.create_workflow(
        db, "Port Scan Block", "Auto firewall block on scanning", "Port Scan", steps
    )
    assert wf.id is not None
    assert wf.name == "Port Scan Block"
    
    db_wf = db.query(DBWorkflow).filter(DBWorkflow.id == cast(int, wf.id)).first()
    assert db_wf is not None
    assert json.loads(cast(str, db_wf.steps_json))[0]["name"] == "Block IP"


def test_trigger_workflow_execution_high_severity(db: Session, engine_service: WorkflowEngine, case: DBInvestigation):
    engine_service.seed_default_workflows(db)

    run = engine_service.trigger_workflow_for_case(
        db, cast(str, case.id), cast(str, case.severity), cast(str, case.title)
    )
    assert run is not None
    assert run.status == "Suspended"
    assert run.current_step_index == 1
    
    log = json.loads(cast(str, run.execution_log_json))
    assert log[0]["status"] == "Completed"
    assert log[0]["name"] == "Notify Slack"
    assert log[1]["status"] == "Suspended"
    assert log[1]["name"] == "Require Manual SOC Approval to Isolate Host"


def test_approve_workflow_step_resumes(db: Session, engine_service: WorkflowEngine, case: DBInvestigation):
    engine_service.seed_default_workflows(db)
    
    run = engine_service.trigger_workflow_for_case(
        db, cast(str, case.id), cast(str, case.severity), cast(str, case.title)
    )
    assert run is not None
    assert run.status == "Suspended"

    resumed_run = engine_service.approve_workflow_step(db, cast(int, run.id), "Workstation isolation approved by admin")
    assert resumed_run is not None
    assert resumed_run.status == "Completed"
    assert resumed_run.current_step_index == 4
    
    log = json.loads(cast(str, resumed_run.execution_log_json))
    assert log[1]["status"] == "Completed"
    assert "Approved by SOC Analyst" in log[1]["detail"]
    assert log[2]["status"] == "Completed"
    assert log[3]["status"] == "Completed"

    events = db.query(DBTimelineEvent).filter(DBTimelineEvent.investigation_id == cast(str, case.id)).all()
    assert len(events) == 3
    assert events[0].event == "SOAR Workflow Triggered"
    assert events[1].event == "SOAR Action Approved"
    assert events[2].event == "SOAR Workflow Completed"


def test_soar_kpis_aggregation(db: Session, engine_service: WorkflowEngine, case: DBInvestigation):
    engine_service.seed_default_workflows(db)
    
    kpis = IncidentResponseService.get_incident_kpis(db)
    assert kpis["automated_actions"] == 0
    assert kpis["pending_approvals"] == 0
    assert kpis["workflow_success_rate"] == 100.0

    run = engine_service.trigger_workflow_for_case(
        db, cast(str, case.id), cast(str, case.severity), cast(str, case.title)
    )
    assert run is not None
    
    kpis = IncidentResponseService.get_incident_kpis(db)
    assert kpis["automated_actions"] == 1
    assert kpis["pending_approvals"] == 1
    assert kpis["workflow_success_rate"] == 0.0

    engine_service.approve_workflow_step(db, cast(int, run.id), "Clear")
    
    kpis = IncidentResponseService.get_incident_kpis(db)
    assert kpis["automated_actions"] == 3
    assert kpis["pending_approvals"] == 0
    assert kpis["workflow_success_rate"] == 100.0
