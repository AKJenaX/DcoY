"""Unit tests for the Threat Intelligence Fusion & Correlation Engine."""

import pytest
from typing import cast, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base
from app.models.database_models import DBInvestigation
from app.models.detection_rule import DBDetectionRule
from app.models.simulation import DBSimulationRun
from app.models.workflow import DBWorkflowExecution
from app.models.intelligence import DBThreatIndicator, DBIntelligenceCorrelation
from app.services.intelligence_engine import IntelligenceEngine
from app.services.correlation_engine import CorrelationEngine


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
def intel_service() -> IntelligenceEngine:
    return IntelligenceEngine()


@pytest.fixture
def correlation_service() -> CorrelationEngine:
    return CorrelationEngine()


def test_seed_threat_indicators(db: Session, intel_service: IntelligenceEngine):
    intel_service.seed_threat_indicators(db)
    count = db.query(DBThreatIndicator).count()
    assert count == 6

    # Verify lookups
    rep = intel_service.query_ioc_reputation(db, "198.51.100.42")
    assert rep is not None
    assert rep.ioc_type == "IP"
    assert rep.confidence_score == 0.94


def test_add_and_query_indicator(db: Session, intel_service: IntelligenceEngine):
    intel_service.add_indicator(db, "attackerdomain.ru", "Domain", 0.85, "Local Intel")
    
    rep = intel_service.query_ioc_reputation(db, "attackerdomain.ru")
    assert rep is not None
    assert rep.ioc_type == "Domain"
    assert rep.confidence_score == 0.85


def test_correlation_matching(db: Session, intel_service: IntelligenceEngine, correlation_service: CorrelationEngine):
    # Seed IOCs
    intel_service.seed_threat_indicators(db)

    # 1. Seed Case containing indicator IP
    case = DBInvestigation(
        id="CASE-INTEL-001",
        title="Incident involving 198.51.100.42 attacker",
        status="Open",
        severity="High",
        risk_score=0.9
    )
    db.add(case)

    # 2. Seed Detection Rule containing hash
    rule = DBDetectionRule(
        name="Malicious Hash Check",
        description="Flags e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 in telemetry",
        author="Admin",
        version=1,
        status="Enabled",
        severity="High",
        category="Malware",
        detection_logic='{"hash": "e3b0c442"}'
    )
    db.add(rule)

    # 3. Seed Simulation matching MITRE technique
    sim = DBSimulationRun(
        id=123,
        scenario_name="Phishing simulation",
        status="Completed",
        mitre_techniques="T1110",
        detection_success_rate=0.95
    )
    db.add(sim)

    # 4. Seed SOAR Workflow Execution linked to Case
    wf = DBWorkflowExecution(
        id=456,
        workflow_id=1,
        workflow_name="Auto Isolate",
        status="Completed",
        execution_log_json="[]",
        linked_investigation_id="CASE-INTEL-001"
    )
    db.add(wf)

    db.commit()

    # Rebuild correlations
    correlation_service.rebuild_correlation_graph(db)

    # Verify correlations count
    links = db.query(DBIntelligenceCorrelation).all()
    # Should link:
    # - IP:198.51.100.42 -> Case:CASE-INTEL-001
    # - Hash:e3b0c442... -> Rule:1
    # - MITRE:T1110 -> Simulation:123
    # - Case:CASE-INTEL-001 -> Workflow:456
    assert len(links) >= 4

    # Verify node graph payload formats
    graph = correlation_service.get_correlation_graph(db, force_rebuild=True)
    assert "nodes" in graph
    assert "edges" in graph
    
    node_ids = {n["id"] for n in graph["nodes"]}
    assert "IP:198.51.100.42" in node_ids
    assert "Case:CASE-INTEL-001" in node_ids
    assert f"Rule:{rule.id}" in node_ids
    assert "Simulation:123" in node_ids
    assert "Workflow:456" in node_ids
