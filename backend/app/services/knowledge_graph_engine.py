"""Security Knowledge Graph Engine. Builds and caches the unified security topology."""

import json
import time
from typing import Any, Dict, List, Set, Optional, cast
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.intelligence import DBThreatIndicator, DBIntelligenceCorrelation
from app.models.database_models import DBInvestigation, DBEvidence
from app.models.detection_rule import DBDetectionRule
from app.models.simulation import DBSimulationRun
from app.models.workflow import DBWorkflowExecution, DBWorkflow
from app.models.playbook import DBResponsePlaybook, DBPlaybookExecution
from app.models.knowledge_graph import DBAsset, DBUserNode, DBExecutiveReport, DBKnowledgeGraphEdge


class KnowledgeGraphEngine:
    """Manages the lifecycle, caching, and metrics aggregation of the Security Knowledge Graph."""

    _cached_graph: Optional[Dict[str, Any]] = None
    _last_build_time: float = 0.0
    _last_rebuild_timestamp: Optional[datetime] = None
    _last_profile_duration_ms: float = 0.0
    CACHE_DURATION_SEC = 15.0  # 15s cache duration

    def rebuild_graph(self, db: Session) -> Dict[str, Any]:
        """Compute the unified graph structure and cache it."""
        t_start = time.perf_counter()
        # 1. Fetch all raw entities
        indicators = db.query(DBThreatIndicator).all()
        assets = db.query(DBAsset).all()
        users = db.query(DBUserNode).all()
        rules = db.query(DBDetectionRule).all()
        cases = db.query(DBInvestigation).filter(DBInvestigation.deleted_at.is_(None)).all()
        simulations = db.query(DBSimulationRun).all()
        workflows = db.query(DBWorkflow).all()
        workflow_execs = db.query(DBWorkflowExecution).all()
        playbooks = db.query(DBResponsePlaybook).all()
        playbook_execs = db.query(DBPlaybookExecution).all()
        reports = db.query(DBExecutiveReport).all()
        
        # 2. Get static correlations to bootstrap standard intelligence relationships
        correlations = db.query(DBIntelligenceCorrelation).all()
        
        # 3. Fetch existing edges from DB
        db_edges = db.query(DBKnowledgeGraphEdge).all()

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        nodes_seen: Set[str] = set()
        edges_seen: Set[str] = set()

        def add_node(node_id: str, node_type: str, label: str, risk: float = 0.0, confidence: float = 1.0, details: Optional[Dict[str, Any]] = None):
            if node_id in nodes_seen:
                return
            nodes_seen.add(node_id)
            nodes.append({
                "id": node_id,
                "type": node_type,
                "label": label,
                "risk": risk,
                "confidence": confidence,
                "details": details or {}
            })

        def add_edge(source: str, target: str, rel_type: str, weight: float = 1.0, description: str = ""):
            # Avoid duplicate edges or self loops
            if source == target:
                return
            edge_key = f"{source}->{rel_type}->{target}"
            if edge_key in edges_seen:
                return
            edges_seen.add(edge_key)
            edges.append({
                "source": source,
                "target": target,
                "relationship": rel_type,
                "weight": weight,
                "description": description
            })

        # Add Core Nodes
        # ─── Indicators ───
        for ind in indicators:
            val = cast(str, ind.ioc_value)
            t = cast(str, ind.ioc_type)
            node_id = f"Indicator:{val}"
            label = f"{t}: {val}"
            add_node(node_id, "Indicator", label, risk=cast(float, ind.confidence_score), confidence=cast(float, ind.confidence_score), details={
                "feed": ind.threat_feed,
                "status": ind.status
            })

        # ─── Assets ───
        for asset in assets:
            node_id = f"Asset:{asset.id}"
            add_node(node_id, "Asset", f"Asset: {asset.name}", risk=cast(float, asset.risk_score), confidence=1.0, details={
                "ip": asset.ip_address,
                "type": asset.asset_type,
                "criticality": asset.criticality
            })

        # ─── Users ───
        for user in users:
            node_id = f"User:{user.username}"
            add_node(node_id, "User", f"User: {user.username}", risk=cast(float, user.risk_score), confidence=1.0, details={
                "role": user.role
            })

        # ─── Detection Rules ───
        for rule in rules:
            node_id = f"Rule:{rule.id}"
            add_node(node_id, "Rule", f"Rule: {rule.name}", risk=0.2 if rule.severity == "Low" else (0.5 if rule.severity == "Medium" else 0.8), confidence=1.0, details={
                "category": rule.category,
                "technique": rule.mitre_technique,
                "status": rule.status
            })
            # Mitre technique as an independent node if present
            if rule.mitre_technique:
                tech_id = rule.mitre_technique.split(" - ")[0].strip()
                tech_node_id = f"MITRE:{tech_id}"
                add_node(tech_node_id, "MITRE", cast(str, rule.mitre_technique), risk=0.5, confidence=1.0)
                add_edge(node_id, tech_node_id, "related_to", weight=0.9, description="Rule implements detection for technique")

        # ─── Investigations (Cases) ───
        for case in cases:
            node_id = f"Case:{case.id}"
            add_node(node_id, "Case", f"Case: {case.title}", risk=cast(float, case.risk_score), confidence=1.0, details={
                "status": case.status,
                "priority": case.priority,
                "severity": case.severity,
                "analyst": case.assigned_analyst
            })

        # ─── Simulations ───
        for sim in simulations:
            node_id = f"Simulation:{sim.id}"
            add_node(node_id, "Simulation", f"Sim: {sim.scenario_name}", risk=1.0 - cast(float, sim.detection_success_rate), confidence=cast(float, sim.simulation_confidence), details={
                "status": sim.status,
                "success_rate": sim.detection_success_rate,
                "mitre_techniques": sim.mitre_techniques
            })
            if sim.mitre_techniques:
                for tech in sim.mitre_techniques.split(","):
                    tech_id = tech.strip()
                    if tech_id:
                        tech_node_id = f"MITRE:{tech_id}"
                        add_node(tech_node_id, "MITRE", f"MITRE: {tech_id}", risk=0.5, confidence=1.0)
                        add_edge(node_id, tech_node_id, "simulated_by", weight=0.9, description="Simulation validates technique")

        # ─── Workflows ───
        for wf in workflows:
            node_id = f"Workflow:{wf.id}"
            add_node(node_id, "Workflow", f"Workflow: {wf.name}", risk=0.1, confidence=1.0, details={
                "trigger": wf.trigger_type,
                "status": wf.status
            })

        # ─── Playbooks ───
        for pb in playbooks:
            node_id = f"Playbook:{pb.id}"
            add_node(node_id, "Playbook", f"Playbook: {pb.name}", risk=0.1, confidence=1.0, details={
                "category": pb.category,
                "duration": pb.estimated_duration_minutes
            })

        # ─── Executive Reports ───
        for rep in reports:
            node_id = f"Report:{rep.id}"
            add_node(node_id, "Report", f"Report: {rep.title}", risk=0.1, confidence=1.0, details={
                "summary": rep.risk_summary
            })

        # Process correlations -> Add edges
        for corr in correlations:
            # Translate corr.source_id / target_id into nodes
            src = cast(str, corr.source_id)
            tgt = cast(str, corr.target_id)
            src_type = cast(str, corr.source_type)
            tgt_type = cast(str, corr.target_type)
            
            # Map standard prefixes to match node IDs
            if ":" not in src:
                src = f"{src_type}:{src}"
            if ":" not in tgt:
                tgt = f"{tgt_type}:{tgt}"
                
            # Map correlation relationship class to standardized types
            rel_map = {
                "implicated_in": "investigated_by",
                "covered_by": "detected_by",
                "targets_hash": "detected_by",
                "tested_in": "simulated_by",
                "orchestrated_by": "orchestrated_by"
            }
            rel_class = cast(str, corr.relationship_class)
            rel_type = rel_map.get(rel_class, "related_to")
            add_edge(src, tgt, rel_type, weight=cast(float, corr.weight))

        # Process DB Edges -> Add persistent custom edges
        for edge in db_edges:
            add_edge(edge.source_id, edge.target_id, edge.relationship_type, weight=edge.weight, description=edge.description or "")

        # Dynamic heuristic mappings to build a "true security knowledge graph"
        # 1. Map indicators of type "IP" targeting "Asset" nodes or "User" nodes
        for ind in indicators:
            ioc_val = cast(str, ind.ioc_value)
            # Link indicator to assets if there's an IP match
            for asset in assets:
                if ioc_val == asset.ip_address:
                    add_edge(f"Indicator:{ioc_val}", f"Asset:{asset.id}", "targets", weight=ind.confidence_score, description="Indicator matches asset IP")
            
            # If the indicator is a User (e.g. compromised AD credentials)
            if ind.ioc_type == "User":
                for user in users:
                    if ioc_val == user.username:
                        add_edge(f"Indicator:{ioc_val}", f"User:{user.username}", "uses", weight=ind.confidence_score, description="Indicator target matches user identity")

        # 2. Map Active Cases to Rules and Playbooks
        # Link Cases -> `investigated_by` -> Analyst/User
        # Link Workflows -> `mitigated_by` -> Playbook (workflows trigger response steps or playbooks)
        for wf_exec in workflow_execs:
            if wf_exec.linked_investigation_id:
                case_node = f"Case:{wf_exec.linked_investigation_id}"
                wf_node = f"Workflow:{wf_exec.workflow_id}"
                # Add link: Case orchestrated_by Workflow
                add_edge(case_node, wf_node, "orchestrated_by", weight=0.95 if wf_exec.status == "Completed" else 0.70)
                
                # Check steps_json in workflow or playbook names in executions
                for pb in playbooks:
                    if pb.name.lower() in wf_exec.workflow_name.lower():
                        add_edge(wf_node, f"Playbook:{pb.id}", "mitigated_by", weight=0.90)

        # 3. Associate cases with executive reports
        for rep in reports:
            # Heuristic title match or relate to open cases
            for case in cases:
                if "credential" in case.title.lower() and "credential" in rep.title.lower():
                    add_edge(f"Case:{case.id}", f"Report:{rep.id}", "related_to", weight=1.0)
                elif "recon" in case.title.lower() and "recon" in rep.title.lower():
                    add_edge(f"Case:{case.id}", f"Report:{rep.id}", "related_to", weight=1.0)
                else:
                    add_edge(f"Case:{case.id}", f"Report:{rep.id}", "related_to", weight=0.5)

        # 4. Connect simulated attack targets (e.g. simulation scenario names mentioning workstations or database)
        for sim in simulations:
            for asset in assets:
                if asset.name.lower() in sim.scenario_name.lower() or "host" in sim.scenario_name.lower() and asset.asset_type == "Workstation":
                    add_edge(f"Simulation:{sim.id}", f"Asset:{asset.id}", "affects", weight=0.8)

        # Make sure that every node referenced in edges exists in nodes list.
        # If any node was omitted, add a basic entry.
        nodes_in_edges = {e["source"] for e in edges} | {e["target"] for e in edges}
        for nid in nodes_in_edges:
            if nid not in nodes_seen:
                parts = nid.split(":", 1)
                ntype = parts[0]
                label = parts[1] if len(parts) > 1 else nid
                add_node(nid, ntype, label, risk=0.5, confidence=1.0)

        self._cached_graph = {
            "nodes": nodes,
            "edges": edges
        }
        self._last_build_time = time.time()
        self._last_rebuild_timestamp = datetime.now(timezone.utc)
        self._last_profile_duration_ms = (time.perf_counter() - t_start) * 1000.0
        return self._cached_graph

    def get_graph(self, db: Session, force_rebuild: bool = False) -> Dict[str, Any]:
        """Fetch cached graph or trigger rebuild."""
        now = time.time()
        if force_rebuild or (self._cached_graph is None) or (now - self._last_build_time > self.CACHE_DURATION_SEC):
            return self.rebuild_graph(db)
        return self._cached_graph

    def add_custom_edge(self, db: Session, source_id: str, source_type: str, target_id: str, target_type: str, rel_type: str, weight: float, desc: str = "") -> DBKnowledgeGraphEdge:
        """Incrementally add a relationship link to the database and clear cache."""
        edge = DBKnowledgeGraphEdge(
            source_id=source_id,
            source_type=source_type,
            target_id=target_id,
            target_type=target_type,
            relationship_type=rel_type,
            weight=weight,
            description=desc,
            created_at=datetime.now(timezone.utc)
        )
        db.add(edge)
        db.commit()
        db.refresh(edge)
        self._cached_graph = None  # invalidate cache
        return edge

    def get_analytics(self, db: Session) -> Dict[str, Any]:
        """Compute structural graph analytics."""
        graph = self.get_graph(db)
        nodes = graph["nodes"]
        edges = graph["edges"]

        # 1. Degree Centrality (Most connected indicators / nodes)
        degrees: Dict[str, int] = {}
        for edge in edges:
            degrees[edge["source"]] = degrees.get(edge["source"], 0) + 1
            degrees[edge["target"]] = degrees.get(edge["target"], 0) + 1

        sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        top_connected = []
        for nid, deg in sorted_degrees[:5]:
            node_label = next((n["label"] for n in nodes if n["id"] == nid), nid)
            node_type = next((n["type"] for n in nodes if n["id"] == nid), "Unknown")
            top_connected.append({"id": nid, "label": node_label, "type": node_type, "connections": deg})

        # 2. Highest Risk Assets
        risk_assets = [n for n in nodes if n["type"] == "Asset"]
        risk_assets_sorted = sorted(risk_assets, key=lambda x: x["risk"], reverse=True)
        top_risk_assets = []
        for ra in risk_assets_sorted[:5]:
            top_risk_assets.append({
                "id": ra["id"],
                "name": ra["label"].replace("Asset: ", ""),
                "risk": ra["risk"],
                "criticality": ra["details"].get("criticality", "Medium")
            })

        # 3. Orphaned Detections (rules without any connections to cases, workflows, or threat indicators)
        connected_rules = set()
        for edge in edges:
            if edge["source"].startswith("Rule:"):
                connected_rules.add(edge["source"])
            if edge["target"].startswith("Rule:"):
                connected_rules.add(edge["target"])

        all_rules = [n["id"] for n in nodes if n["type"] == "Rule"]
        orphaned_rules = [r for r in all_rules if r not in connected_rules]
        orphaned_rules_data = []
        for orid in orphaned_rules:
            rule_node = next(n for n in nodes if n["id"] == orid)
            orphaned_rules_data.append({
                "id": orid,
                "name": rule_node["label"].replace("Rule: ", ""),
                "category": rule_node["details"].get("category", "Uncategorized")
            })

        # 4. Campaign Clusters (connected components or dense areas of indicators and cases)
        # Simple clustering: group by Case and its connected indicators
        case_clusters: Dict[str, List[str]] = {}
        for edge in edges:
            if edge["relationship"] == "investigated_by":
                # Typically Indicator -> investigated_by -> Case, check types
                case_id = edge["target"] if edge["target"].startswith("Case:") else (edge["source"] if edge["source"].startswith("Case:") else None)
                indicator_id = edge["source"] if edge["source"].startswith("Indicator:") else (edge["target"] if edge["target"].startswith("Indicator:") else None)
                if case_id and indicator_id:
                    case_clusters.setdefault(case_id, []).append(indicator_id)

        campaign_clusters = []
        for cid, iocs in case_clusters.items():
            case_label = next((n["label"] for n in nodes if n["id"] == cid), cid).replace("Case: ", "")
            campaign_clusters.append({
                "case_id": cid,
                "case_name": case_label,
                "size": len(iocs),
                "indicators": iocs
            })
        campaign_clusters = sorted(campaign_clusters, key=lambda x: x["size"], reverse=True)

        # 5. MITRE Coverage Gaps
        # Check MITRE techniques simulated vs. covered by active rules
        covered_techs = set()
        simulated_techs = set()
        for n in nodes:
            if n["type"] == "Rule" and n["details"].get("status") == "Enabled" and n["details"].get("technique"):
                tech_id = n["details"].get("technique").split(" - ")[0].strip()
                covered_techs.add(tech_id)
            if n["type"] == "Simulation" and n["details"].get("status") == "Completed" and n["details"].get("mitre_techniques"):
                for tech in n["details"].get("mitre_techniques").split(","):
                    tech_id = tech.strip()
                    if tech_id:
                        simulated_techs.add(tech_id)

        coverage_gaps = list(simulated_techs - covered_techs)

        return {
            "top_connected": top_connected,
            "top_risk_assets": top_risk_assets,
            "orphaned_detections": orphaned_rules_data,
            "campaign_clusters": campaign_clusters,
            "coverage_gaps": coverage_gaps,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }

    def get_freshness_age_seconds(self) -> float:
        """Return the number of seconds since the graph was last recompiled."""
        if not self._last_rebuild_timestamp:
            return 9999.0
        delta = datetime.now(timezone.utc) - self._last_rebuild_timestamp
        return delta.total_seconds()

    def get_last_profile_duration_ms(self) -> float:
        """Return the duration in milliseconds of the last graph compilation."""
        return self._last_profile_duration_ms
