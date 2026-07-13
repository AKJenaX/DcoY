"""SOAR Threat Intelligence Correlation Engine."""

import json
import time
from typing import Any, Dict, List, Set, Optional, cast
from sqlalchemy.orm import Session

from app.models.intelligence import DBThreatIndicator, DBIntelligenceCorrelation
from app.models.database_models import DBInvestigation
from app.models.detection_rule import DBDetectionRule
from app.models.simulation import DBSimulationRun
from app.models.workflow import DBWorkflowExecution
from app.models.knowledge_graph import DBKnowledgeGraphEdge


class CorrelationEngine:
    """Computes directed relationship links between all core database entities and threat intelligence objects."""

    _cached_graph: Optional[Dict[str, List[Any]]] = None
    _last_build_time: float = 0.0
    CACHE_DURATION_SEC = 10.0  # 10s caching to optimize web requests

    def rebuild_correlation_graph(self, db: Session):
        """Analyze database tables and compute correlation links, purging the old edges and inserting new ones."""
        # 1. Clear previous correlation table and auto-computed graph edges
        db.query(DBIntelligenceCorrelation).delete()
        db.query(DBKnowledgeGraphEdge).filter(DBKnowledgeGraphEdge.description == "Auto-computed correlation").delete()
        db.commit()

        correlations: List[DBIntelligenceCorrelation] = []

        # Fetch entities
        indicators = db.query(DBThreatIndicator).all()
        cases = db.query(DBInvestigation).all()
        rules = db.query(DBDetectionRule).all()
        simulations = db.query(DBSimulationRun).all()
        workflow_executions = db.query(DBWorkflowExecution).all()

        # ─── Correlation Rule 1: IP/Domain -> Investigation Case ────────────────
        for indicator in indicators:
            ioc_val = cast(str, indicator.ioc_value)
            ioc_type = cast(str, indicator.ioc_type)
            
            for case in cases:
                case_title = cast(str, case.title) or ""
                case_summary = cast(str, case.ai_summary) or ""
                case_notes = cast(str, case.notes) or ""
                
                # Check for substring match in case metadata fields
                if (ioc_val in case_title) or (ioc_val in case_summary) or (ioc_val in case_notes):
                    correlations.append(DBIntelligenceCorrelation(
                        source_id=f"{ioc_type}:{ioc_val}",
                        source_type=ioc_type,
                        target_id=f"Case:{case.id}",
                        target_type="Case",
                        relationship_class="implicated_in",
                        weight=indicator.confidence_score
                    ))

        # ─── Correlation Rule 2: Hash/MITRE -> Detection Rule ──────────────────
        for rule in rules:
            rule_logic = cast(str, rule.detection_logic) or ""
            rule_desc = cast(str, rule.description) or ""
            rule_mitre = cast(str, rule.mitre_technique) or ""
            
            # Match MITRE techniques
            if rule_mitre:
                correlations.append(DBIntelligenceCorrelation(
                    source_id=f"MITRE:{rule_mitre}",
                    source_type="MITRE",
                    target_id=f"Rule:{rule.id}",
                    target_type="Rule",
                    relationship_class="covered_by",
                    weight=0.90
                ))

            # Match hashes
            for indicator in indicators:
                ioc_val = cast(str, indicator.ioc_value)
                if indicator.ioc_type == "Hash" and ((ioc_val in rule_logic) or (ioc_val in rule_desc)):
                    correlations.append(DBIntelligenceCorrelation(
                        source_id=f"Hash:{ioc_val}",
                        source_type="Hash",
                        target_id=f"Rule:{rule.id}",
                        target_type="Rule",
                        relationship_class="targets_hash",
                        weight=indicator.confidence_score
                    ))

        # ─── Correlation Rule 3: MITRE -> Purple Team Simulation ─────────────────
        for sim in simulations:
            sim_techniques = sim.mitre_techniques or ""
            # Split comma separated techniques
            techniques = [t.strip() for t in sim_techniques.split(",") if t.strip()]
            for tech in techniques:
                correlations.append(DBIntelligenceCorrelation(
                    source_id=f"MITRE:{tech}",
                    source_type="MITRE",
                    target_id=f"Simulation:{sim.id}",
                    target_type="Simulation",
                    relationship_class="tested_in",
                    weight=sim.detection_success_rate
                ))

        # ─── Correlation Rule 4: Investigation Case -> SOAR Workflow Execution ─────
        for wf_exec in workflow_executions:
            case_id = wf_exec.linked_investigation_id
            if case_id:
                correlations.append(DBIntelligenceCorrelation(
                    source_id=f"Case:{case_id}",
                    source_type="Case",
                    target_id=f"Workflow:{wf_exec.id}",
                    target_type="Workflow",
                    relationship_class="orchestrated_by",
                    weight=0.95 if wf_exec.status == "Completed" else 0.70
                ))

        # 2. Add all to DB
        if correlations:
            db.add_all(correlations)
            db.commit()

            # Mirror to DBKnowledgeGraphEdge for true security knowledge graph implementation
            kg_edges = []
            for corr in correlations:
                rel_map = {
                    "implicated_in": "investigated_by",
                    "covered_by": "detected_by",
                    "targets_hash": "detected_by",
                    "tested_in": "simulated_by",
                    "orchestrated_by": "orchestrated_by"
                }
                rel_class = cast(str, corr.relationship_class)
                rel_type = rel_map.get(rel_class, "related_to")
                
                src_id = cast(str, corr.source_id)
                src_type = cast(str, corr.source_type)
                if ":" not in src_id:
                    src_id = f"{src_type}:{src_id}"
                tgt_id = cast(str, corr.target_id)
                tgt_type = cast(str, corr.target_type)
                if ":" not in tgt_id:
                    tgt_id = f"{tgt_type}:{tgt_id}"
                    
                kg_edges.append(DBKnowledgeGraphEdge(
                    source_id=src_id,
                    source_type=src_type,
                    target_id=tgt_id,
                    target_type=tgt_type,
                    relationship_type=rel_type,
                    weight=corr.weight,
                    description="Auto-computed correlation"
                ))
            if kg_edges:
                db.add_all(kg_edges)
                db.commit()

        self._last_build_time = time.time()

    def get_correlation_graph(self, db: Session, force_rebuild: bool = False) -> Dict[str, List[Any]]:
        """Return the nodes and edges representation of the calculated intelligence graph."""
        now = time.time()
        # Cache traversal logic
        if force_rebuild or (now - self._last_build_time > self.CACHE_DURATION_SEC) or (self._cached_graph is None):
            self.rebuild_correlation_graph(db)
            
            # Fetch relationships
            edges_db = db.query(DBIntelligenceCorrelation).all()
            
            nodes_set: Set[str] = set()
            nodes_payload = []
            edges_payload = []
            
            # Retrieve node definitions
            indicators = {cast(str, i.ioc_value): i for i in db.query(DBThreatIndicator).all()}
            cases = {cast(str, c.id): c for c in db.query(DBInvestigation).all()}
            rules = {cast(int, r.id): r for r in db.query(DBDetectionRule).all()}
            sims = {cast(int, s.id): s for s in db.query(DBSimulationRun).all()}
            wfs = {cast(int, w.id): w for w in db.query(DBWorkflowExecution).all()}

            def add_node(node_id: str, node_type: str):
                if node_id in nodes_set:
                    return
                nodes_set.add(node_id)
                
                # Fetch detailed labels
                val = node_id.split(":", 1)[1] if ":" in node_id else node_id
                label = val
                confidence = 1.0
                
                if node_type in indicators:
                    label = f"{node_type}: {val}"
                    confidence = indicators[val].confidence_score
                elif node_type == "Case" and val in cases:
                    label = f"Case: {cases[val].title}"
                    confidence = cases[val].risk_score
                elif node_type == "Rule" and int(val) in rules:
                    label = f"Rule: {rules[int(val)].name}"
                elif node_type == "Simulation" and int(val) in sims:
                    label = f"Sim: {sims[int(val)].scenario_name}"
                    confidence = sims[int(val)].detection_success_rate
                elif node_type == "Workflow" and int(val) in wfs:
                    label = f"Workflow: {wfs[int(val)].workflow_name}"
                
                nodes_payload.append({
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "confidence": confidence
                })

            for edge in edges_db:
                add_node(cast(str, edge.source_id), cast(str, edge.source_type))
                add_node(cast(str, edge.target_id), cast(str, edge.target_type))
                
                edges_payload.append({
                    "source": cast(str, edge.source_id),
                    "target": cast(str, edge.target_id),
                    "relationship": cast(str, edge.relationship_class),
                    "weight": edge.weight
                })

            # Handle isolated indicators to guarantee full visibility
            for ind in indicators.values():
                ioc_val = cast(str, ind.ioc_value)
                ioc_type = cast(str, ind.ioc_type)
                node_id = f"{ioc_type}:{ioc_val}"
                add_node(node_id, ioc_type)

            self._cached_graph = {
                "nodes": nodes_payload,
                "edges": edges_payload
            }

        return self._cached_graph
