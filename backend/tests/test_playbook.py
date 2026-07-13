"""Tests for Sprint 5.2: Incident Response & Response Playbooks services and endpoints."""

import json
import pytest
from typing import cast
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.database_models import DBInvestigation
from app.models.playbook import DBResponsePlaybook, DBPlaybookExecution
from app.services.playbook_engine import PlaybookEngine
from app.services.incident_response import IncidentResponseService


class TestPlaybookEngine:
    """Test suite for playbook templates seeding, trigger operations, and checklists updates."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        # Setup an in-memory SQLite database
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = TestingSessionLocal()
        
        # Instantiate engine
        self.engine_service = PlaybookEngine()
        
        # Seed default test investigation case
        self.case = DBInvestigation(
            id="CASE-2026-999",
            title="Test Unauthorized API Ingress",
            status="Open",
            priority="High",
            severity="High",
            risk_score=0.85,
            assigned_analyst="Unassigned"
        )
        self.db.add(self.case)
        self.db.commit()
        
        yield
        
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_playbook_seeding(self):
        templates = self.engine_service.get_all_playbooks(self.db)
        assert len(templates) == 8
        assert any(t.name == "Malware Containment" for t in templates)
        assert any(t.name == "Web Application Attack" for t in templates)

    def test_create_custom_playbook_template(self):
        tpl = self.engine_service.create_playbook_template(
            self.db,
            name="Custom Isolation Plan",
            description="Isolate target hosts and lock AD credentials",
            steps=["Isolate target IP", "Disable user accounts", "Notify CISO office"],
            duration=15,
            category="Custom"
        )
        assert tpl.name == "Custom Isolation Plan"
        assert tpl.estimated_duration_minutes == 15
        
        steps = json.loads(cast(str, tpl.steps_json))
        assert len(steps) == 3
        assert steps[1] == "Disable user accounts"

    def test_trigger_playbook_execution(self):
        templates = self.engine_service.get_all_playbooks(self.db)
        malware_tpl = next(t for t in templates if t.name == "Malware Containment")
        
        run = self.engine_service.trigger_playbook(self.db, cast(str, self.case.id), cast(int, malware_tpl.id))
        assert run.investigation_id == cast(str, self.case.id)
        assert run.playbook_name == "Malware Containment"
        assert run.status == "Running"
        assert run.current_step_index == 0
        
        steps_log = json.loads(cast(str, run.execution_log_json))
        assert len(steps_log) == 5
        assert steps_log[0]["step"] == "Verify malware file hash on threat intelligence databases (e.g. VirusTotal)"
        assert steps_log[0]["status"] == "Pending"

    def test_update_execution_step(self):
        templates = self.engine_service.get_all_playbooks(self.db)
        malware_tpl = next(t for t in templates if t.name == "Malware Containment")
        run = self.engine_service.trigger_playbook(self.db, cast(str, self.case.id), cast(int, malware_tpl.id))
        
        # Mark first step as Completed
        updated_run = self.engine_service.update_execution_step(
            self.db, cast(int, run.id), step_index=0, status="Completed", step_note="Hash verified: MD5=abcd"
        )
        assert updated_run is not None
        assert updated_run.current_step_index == 1
        
        log = json.loads(updated_run.execution_log_json)
        assert log[0]["status"] == "Completed"
        assert log[0]["note"] == "Hash verified: MD5=abcd"
        assert log[0]["completed_at"] is not None

    def test_auto_complete_playbook(self):
        templates = self.engine_service.get_all_playbooks(self.db)
        custom_tpl = next(t for t in templates if t.name == "Custom Playbook")
        run = self.engine_service.trigger_playbook(self.db, cast(str, self.case.id), cast(int, custom_tpl.id))
        
        steps_count = len(json.loads(cast(str, run.execution_log_json))) # should be 4
        
        # Complete all steps
        for i in range(steps_count):
            run = self.engine_service.update_execution_step(
                self.db, cast(int, run.id), step_index=i, status="Completed", step_note="Completed step"
            )
            assert run is not None
            
        assert run is not None
        assert run.status == "Completed"
        assert run.completed_at is not None

    def test_update_notes_and_evidence(self):
        templates = self.engine_service.get_all_playbooks(self.db)
        custom_tpl = next(t for t in templates if t.name == "Custom Playbook")
        run = self.engine_service.trigger_playbook(self.db, cast(str, self.case.id), cast(int, custom_tpl.id))
        
        evidence = [{"evidence": "198.51.100.42", "type": "Blocked IP", "timestamp": "2026-07-13T08:00:00Z"}]
        run = self.engine_service.update_execution_notes_and_evidence(
            self.db, cast(int, run.id), notes="Workstation fully isolated.", evidence=evidence
        )
        assert run is not None
        assert run.notes == "Workstation fully isolated."
        
        assert run.evidence_json is not None
        ev_attached = json.loads(cast(str, run.evidence_json))
        assert len(ev_attached) == 1
        assert ev_attached[0]["evidence"] == "198.51.100.42"


class TestIncidentResponseService:
    """Test suite for Incident Response operational KPIs calculation."""

    def test_empty_kpis(self):
        # We need a clean engine setup
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        
        kpis = IncidentResponseService.get_incident_kpis(db)
        assert kpis["active_incidents"] == 0
        assert kpis["high_severity_cases"] == 0
        assert kpis["playbooks_executed"] == 0
        assert kpis["automation_coverage_pct"] == 0.0
        
        db.close()
        Base.metadata.drop_all(bind=engine)

    def test_populated_kpis(self):
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        
        # Add cases
        c1 = DBInvestigation(id="CASE-1", title="Low Risk Event", status="Open", severity="Low", risk_score=0.2)
        c2 = DBInvestigation(id="CASE-2", title="High Risk Scan", status="Active", severity="High", risk_score=0.9)
        c3 = DBInvestigation(id="CASE-3", title="Resolved Leak", status="Resolved", severity="Medium", risk_score=0.5)
        db.add_all([c1, c2, c3])
        db.commit()
        
        # Execute playbooks
        p_engine = PlaybookEngine()
        templates = p_engine.get_all_playbooks(db)
        
        p_engine.trigger_playbook(db, "CASE-2", cast(int, templates[0].id))
        
        kpis = IncidentResponseService.get_incident_kpis(db)
        assert kpis["active_incidents"] == 2
        assert kpis["high_severity_cases"] == 1
        assert kpis["playbooks_executed"] == 1
        assert kpis["automation_coverage_pct"] == 33.3  # 1/3 cases have playbooks
        
        db.close()
        Base.metadata.drop_all(bind=engine)
