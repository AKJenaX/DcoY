"""Unified Global Search Service across all security entities."""

from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.models.intelligence import DBThreatIndicator
from app.models.knowledge_graph import DBAsset, DBUserNode, DBExecutiveReport
from app.models.detection_rule import DBDetectionRule
from app.models.database_models import DBInvestigation
from app.models.playbook import DBResponsePlaybook
from app.models.workflow import DBWorkflow
from app.models.simulation import DBSimulationRun


class SearchService:
    """Provides keyword-based search across all core database objects, formatting results with navigational routing metadata."""

    def search_all(self, db: Session, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Perform lookup across indicators, assets, users, rules, cases, and workflows."""
        if not query or not query.strip():
            return {
                "indicators": [],
                "assets": [],
                "users": [],
                "rules": [],
                "cases": [],
                "playbooks": [],
                "workflows": [],
                "simulations": [],
                "reports": []
            }

        q = f"%{query.strip()}%"

        # 1. Search Threat Indicators
        indicators_results = []
        try:
            indicators = db.query(DBThreatIndicator).filter(
                (DBThreatIndicator.ioc_value.like(q)) | 
                (DBThreatIndicator.ioc_type.like(q)) |
                (DBThreatIndicator.threat_feed.like(q))
            ).limit(8).all()
            for item in indicators:
                indicators_results.append({
                    "id": f"Indicator:{item.ioc_value}",
                    "title": f"{item.ioc_type}: {item.ioc_value}",
                    "subtitle": f"Feed: {item.threat_feed} (Confidence: {int(item.confidence_score*100)}%)",
                    "route": "intelligence_fusion",
                    "entity_id": item.ioc_value,
                    "entity_type": "Indicator"
                })
        except Exception:
            pass

        # 2. Search Assets
        assets_results = []
        try:
            assets = db.query(DBAsset).filter(
                (DBAsset.name.like(q)) |
                (DBAsset.ip_address.like(q)) |
                (DBAsset.asset_type.like(q))
            ).limit(8).all()
            for item in assets:
                assets_results.append({
                    "id": f"Asset:{item.id}",
                    "title": f"Asset: {item.name}",
                    "subtitle": f"IP: {item.ip_address} | Type: {item.asset_type} (Risk: {int(item.risk_score*100)}%)",
                    "route": "knowledge_graph",
                    "entity_id": f"Asset:{item.id}",
                    "entity_type": "Asset"
                })
        except Exception:
            pass

        # 3. Search Users
        users_results = []
        try:
            users = db.query(DBUserNode).filter(
                (DBUserNode.username.like(q)) |
                (DBUserNode.role.like(q))
            ).limit(8).all()
            for item in users:
                users_results.append({
                    "id": f"User:{item.username}",
                    "title": f"User: {item.username}",
                    "subtitle": f"Role: {item.role} (Risk: {int(item.risk_score*100)}%)",
                    "route": "knowledge_graph",
                    "entity_id": f"User:{item.username}",
                    "entity_type": "User"
                })
        except Exception:
            pass

        # 4. Search Detection Rules
        rules_results = []
        try:
            rules = db.query(DBDetectionRule).filter(
                (DBDetectionRule.name.like(q)) |
                (DBDetectionRule.description.like(q)) |
                (DBDetectionRule.category.like(q)) |
                (DBDetectionRule.mitre_technique.like(q))
            ).limit(8).all()
            for item in rules:
                rules_results.append({
                    "id": f"Rule:{item.id}",
                    "title": f"Rule: {item.name}",
                    "subtitle": f"Category: {item.category} | MITRE: {item.mitre_technique}",
                    "route": "detection_rules",
                    "entity_id": str(item.id),
                    "entity_type": "Rule"
                })
        except Exception:
            pass

        # 5. Search Investigations
        cases_results = []
        try:
            cases = db.query(DBInvestigation).filter(
                (DBInvestigation.deleted_at.is_(None)) & (
                    (DBInvestigation.id.like(q)) |
                    (DBInvestigation.title.like(q)) |
                    (DBInvestigation.severity.like(q)) |
                    (DBInvestigation.assigned_analyst.like(q))
                )
            ).limit(8).all()
            for item in cases:
                cases_results.append({
                    "id": f"Case:{item.id}",
                    "title": f"Case: {item.title}",
                    "subtitle": f"ID: {item.id} | Severity: {item.severity} | Analyst: {item.assigned_analyst}",
                    "route": "investigations",
                    "entity_id": item.id,
                    "entity_type": "Case"
                })
        except Exception:
            pass

        # 6. Search Playbooks
        playbooks_results = []
        try:
            playbooks = db.query(DBResponsePlaybook).filter(
                (DBResponsePlaybook.name.like(q)) |
                (DBResponsePlaybook.description.like(q)) |
                (DBResponsePlaybook.category.like(q))
            ).limit(8).all()
            for item in playbooks:
                playbooks_results.append({
                    "id": f"Playbook:{item.id}",
                    "title": f"Playbook: {item.name}",
                    "subtitle": f"Category: {item.category} | Steps count: {len(item.steps_json.split(','))}",
                    "route": "incident_response",
                    "entity_id": str(item.id),
                    "entity_type": "Playbook"
                })
        except Exception:
            pass

        # 7. Search Workflows
        workflows_results = []
        try:
            workflows = db.query(DBWorkflow).filter(
                (DBWorkflow.name.like(q)) |
                (DBWorkflow.description.like(q)) |
                (DBWorkflow.trigger_type.like(q))
            ).limit(8).all()
            for item in workflows:
                workflows_results.append({
                    "id": f"Workflow:{item.id}",
                    "title": f"Workflow: {item.name}",
                    "subtitle": f"Trigger: {item.trigger_type} | Trigger logic active",
                    "route": "soar",
                    "entity_id": str(item.id),
                    "entity_type": "Workflow"
                })
        except Exception:
            pass

        # 8. Search Simulations
        simulations_results = []
        try:
            sims = db.query(DBSimulationRun).filter(
                (DBSimulationRun.scenario_name.like(q)) |
                (DBSimulationRun.mitre_techniques.like(q))
            ).limit(8).all()
            for item in sims:
                simulations_results.append({
                    "id": f"Simulation:{item.id}",
                    "title": f"Simulation: {item.scenario_name}",
                    "subtitle": f"Status: {item.status} | Techniques: {item.mitre_techniques}",
                    "route": "attack_simulation",
                    "entity_id": str(item.id),
                    "entity_type": "Simulation"
                })
        except Exception:
            pass

        # 9. Search Executive Reports
        reports_results = []
        try:
            reps = db.query(DBExecutiveReport).filter(
                (DBExecutiveReport.title.like(q)) |
                (DBExecutiveReport.risk_summary.like(q))
            ).limit(8).all()
            for item in reps:
                reports_results.append({
                    "id": f"Report:{item.id}",
                    "title": f"Report: {item.title}",
                    "subtitle": f"Created: {item.created_at.strftime('%Y-%m-%d')} | Uptime report summarizations",
                    "route": "executive",
                    "entity_id": str(item.id),
                    "entity_type": "Report"
                })
        except Exception:
            pass

        return {
            "indicators": indicators_results,
            "assets": assets_results,
            "users": users_results,
            "rules": rules_results,
            "cases": cases_results,
            "playbooks": playbooks_results,
            "workflows": workflows_results,
            "simulations": simulations_results,
            "reports": reports_results
        }
