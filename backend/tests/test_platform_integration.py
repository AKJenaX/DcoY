"""Integration test simulating the platform-wide workflow: Detect -> Hunt -> Investigate -> Respond -> SOAR -> Knowledge Graph -> Executive Dashboard."""

import pytest
from app.database import SessionLocal
from app.models.intelligence import DBThreatIndicator
from app.models.database_models import DBInvestigation, DBEvidence
from app.models.detection_rule import DBDetectionRule
from app.models.workflow import DBWorkflow, DBWorkflowExecution
from app.models.playbook import DBResponsePlaybook, DBPlaybookExecution
from app.models.knowledge_graph import DBAsset, DBUserNode, DBKnowledgeGraphEdge

from app.services.intelligence_engine import IntelligenceEngine
from app.services.correlation_engine import CorrelationEngine
from app.services.knowledge_graph_engine import KnowledgeGraphEngine
from app.services.attack_path_engine import AttackPathEngine
from app.services.executive_metrics import build_executive_metrics
from app.services.platform_registry import PlatformRegistry


def test_platform_end_to_end_integration():
    db = SessionLocal()
    try:
        # Initialize engines
        intel_engine = IntelligenceEngine()
        corr_engine = CorrelationEngine()
        kg_engine = KnowledgeGraphEngine()
        ap_engine = AttackPathEngine(kg_engine)
        registry = PlatformRegistry()

        # Step 0: Ensure base seeding has run
        if db.query(DBAsset).count() == 0:
            db.add_all([
                DBAsset(name="WS-ADMIN-01", ip_address="198.51.100.10", asset_type="Workstation", risk_score=0.15, criticality="High"),
                DBAsset(name="WS-OPERATOR-02", ip_address="198.51.100.20", asset_type="Workstation", risk_score=0.65, criticality="Medium"),
                DBAsset(name="HONEYPOT-SSH", ip_address="198.51.100.42", asset_type="Honeypot", risk_score=0.95, criticality="Low"),
            ])
            db.commit()

        # ─── 1. DETECT (Register Threat Indicator & Trigger Rule Check) ───
        test_ip = "198.51.100.250"
        indicator = intel_engine.add_indicator(
            db=db,
            value=test_ip,
            type="IP",
            confidence=0.99,
            feed="Integration Test Sandbox Feed"
        )
        assert indicator.id is not None
        assert indicator.ioc_value == test_ip

        # Setup standard rule
        rule = db.query(DBDetectionRule).filter(DBDetectionRule.name == "Integration Test Rule").first()
        if not rule:
            rule = DBDetectionRule(
                name="Integration Test Rule",
                description="Simulates detecting malicious test IP sweeps",
                author="QA Team",
                version=1,
                status="Enabled",
                severity="High",
                category="Integration Tests",
                mitre_technique="T1046 - Network Scanning",
                detection_logic='{"event_type": "port_scan"}',
                threshold=1,
                time_window=60
            )
            db.add(rule)
            db.commit()

        # ─── 2. HUNT (Proactive search for threat context) ───
        # Simulate checking reputation of indicator
        rep = intel_engine.query_ioc_reputation(db, test_ip)
        assert rep is not None
        assert rep.confidence_score == 0.99

        # ─── 3. INVESTIGATE (Create Case & Attach Evidence) ───
        case_id = "CASE-INTEGRATION-TEST"
        case = db.query(DBInvestigation).filter(DBInvestigation.id == case_id).first()
        if case:
            db.query(DBEvidence).filter(DBEvidence.investigation_id == case_id).delete()
            db.delete(case)
            db.commit()

        case = DBInvestigation(
            id=case_id,
            title="Suspicious Egress Port Scan",
            status="Open",
            priority="High",
            severity="High",
            assigned_analyst="QA Lead",
            risk_score=0.85,
            ai_summary="Integration test case tracking port sweep anomalies from external sandbox feed."
        )
        db.add(case)
        db.commit()

        evidence = DBEvidence(
            investigation_id=case_id,
            event=f"Port scanning from IP: {test_ip}",
            timestamp="2026-07-13T12:00:00Z",
            severity="High",
            confidence="High",
            mitre="T1046"
        )
        db.add(evidence)
        db.commit()

        # ─── 4. RESPOND & SOAR (Start Workflow & Playbook Executions) ───
        workflow = db.query(DBWorkflow).filter(DBWorkflow.name == "Integration Containment Workflow").first()
        if not rule:
            workflow = DBWorkflow(
                name="Integration Containment Workflow",
                description="Auto-quarantine test workflow",
                trigger_type="Severity High",
                status="Enabled",
                steps_json='[{"type": "Action", "name": "Block IP", "parameter": "198.51.100.250"}]'
            )
            db.add(workflow)
            db.commit()

        wf_exec = DBWorkflowExecution(
            workflow_id=10,
            workflow_name="Integration Containment Workflow",
            status="Completed",
            execution_log_json='[{"type": "Action", "name": "Block IP", "status": "Completed", "timestamp": "2026-07-13T12:05:00Z"}]',
            linked_investigation_id=case_id
        )
        db.add(wf_exec)
        db.commit()

        # ─── 5. KNOWLEDGE GRAPH (Rebuild and check links) ───
        # Rebuild correlations & verify graph compiles the newly generated workflow edge
        corr_engine.rebuild_correlation_graph(db)
        
        graph = kg_engine.get_graph(db, force_rebuild=True)
        assert len(graph["nodes"]) > 0
        assert len(graph["edges"]) > 0

        # Check if the case node is linked to the workflow node
        case_wf_edge_found = False
        for edge in graph["edges"]:
            if edge["source"] == f"Case:{case_id}" and edge["relationship"] == "orchestrated_by":
                case_wf_edge_found = True
                break
        assert case_wf_edge_found

        # Verify shortest path tracing
        path_info = ap_engine.find_shortest_path(db, f"Case:{case_id}", "Asset:1")
        assert "path_found" in path_info

        # ─── 6. EXECUTIVE DASHBOARD (Verify aggregate counts) ───
        telemetry = [
            {"ip": test_ip, "event_type": "port_scan", "risk_score": 0.85, "risk_level": "high"}
        ]
        metrics = build_executive_metrics(db, telemetry)
        assert metrics["kpis"]["open_investigations"] >= 1
        assert metrics["platform_health_diagnostics"]["metrics"]["graph_relationships"] > 0

        # Cleanup test entities
        db.query(DBEvidence).filter(DBEvidence.investigation_id == case_id).delete()
        db.delete(case)
        db.delete(wf_exec)
        db.delete(indicator)
        if rule:
            db.delete(rule)
        db.commit()

    finally:
        db.close()
