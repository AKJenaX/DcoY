"""Tests for Sprint 5.1: Purple Team & Attack Simulation services and endpoints."""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.simulation import DBSimulationRun
from app.models.detection_rule import DBDetectionRule
from app.services.simulation_engine import SimulationEngine
from app.services.attack_simulator import AttackSimulator


class TestSimulationEngine:
    """Test suite for synthetic telemetry generation."""

    def test_phishing_scenario(self):
        events = SimulationEngine.generate_scenario_telemetry("Phishing")
        assert len(events) == 2
        assert any(e["mitre_technique"] == "T1566 - Phishing" for e in events)
        assert any("outlook.exe" in e.get("details", {}).get("parent_process", "") for e in events)

    def test_ssh_brute_force_scenario(self):
        events = SimulationEngine.generate_scenario_telemetry("SSH Brute Force")
        assert len(events) == 15
        assert all(e["event_type"] == "ssh_bruteforce" for e in events)

    def test_port_scan_scenario(self):
        events = SimulationEngine.generate_scenario_telemetry("Port Scan")
        assert len(events) == 13
        assert all(e["event_type"] == "port_scan" for e in events)


class TestAttackSimulator:
    """Test suite for the AttackSimulator service."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = TestingSessionLocal()
        
        # Seed test rules
        rule1 = DBDetectionRule(
            id=1,
            name="SSH Brute Force Trigger",
            description="Matches ssh_bruteforce",
            status="Enabled",
            mitre_technique="T1110.001 - Brute Force: Password Guessing",
            detection_logic='{"event_type": "ssh_bruteforce"}',
            threshold=5,
            time_window=60
        )
        rule2 = DBDetectionRule(
            id=2,
            name="Port Scan Trigger",
            description="Matches port_scan",
            status="Enabled",
            mitre_technique="T1046 - Network Scanning",
            detection_logic='{"event_type": "port_scan"}',
            threshold=5,
            time_window=60
        )
        self.db.add(rule1)
        self.db.add(rule2)
        self.db.commit()
        
        self.simulator = AttackSimulator()
        
        yield
        
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_execute_simulation_ssh_brute_force(self):
        run = self.simulator.execute_simulation(self.db, "SSH Brute Force")
        assert run.status == "Completed"
        assert run.scanned_events_count == 15
        assert run.detection_success_rate == 1.0  # SSH Brute Force matches rule1
        assert run.missed_detections_count == 0
        
        results = json.loads(run.results_data)
        assert len(results["triggered_rules"]) == 1
        assert results["triggered_rules"][0]["name"] == "SSH Brute Force Trigger"

    def test_execute_simulation_port_scan(self):
        run = self.simulator.execute_simulation(self.db, "Port Scan")
        assert run.status == "Completed"
        assert run.scanned_events_count == 13
        assert run.detection_success_rate == 1.0
        
        results = json.loads(run.results_data)
        assert len(results["triggered_rules"]) == 1
        assert results["triggered_rules"][0]["name"] == "Port Scan Trigger"

    def test_execute_simulation_phishing_uncovered(self):
        # We don't have a rule matching event_type="phishing", so success rate should be 0%
        run = self.simulator.execute_simulation(self.db, "Phishing")
        assert run.status == "Completed"
        assert run.detection_success_rate == 0.0
        assert run.missed_detections_count == 2
