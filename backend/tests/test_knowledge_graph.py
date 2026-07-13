"""Unit tests for Security Knowledge Graph Engine."""

import pytest
from app.database import SessionLocal
from app.models.knowledge_graph import DBAsset, DBUserNode, DBKnowledgeGraphEdge
from app.services.knowledge_graph_engine import KnowledgeGraphEngine


def test_knowledge_graph_engine():
    db = SessionLocal()
    try:
        # Seed test database if empty
        if db.query(DBAsset).count() == 0:
            db.add_all([
                DBAsset(name="WS-ADMIN-01", ip_address="198.51.100.10", asset_type="Workstation", risk_score=0.15, criticality="High"),
                DBAsset(name="WS-OPERATOR-02", ip_address="198.51.100.20", asset_type="Workstation", risk_score=0.65, criticality="Medium"),
                DBAsset(name="DB-PROD-01", ip_address="198.51.100.50", asset_type="Database", risk_score=0.08, criticality="High"),
                DBAsset(name="HONEYPOT-SSH", ip_address="198.51.100.42", asset_type="Honeypot", risk_score=0.95, criticality="Low"),
                DBAsset(name="DC-PROD-01", ip_address="198.51.100.100", asset_type="Active Directory", risk_score=0.04, criticality="High"),
            ])
            db.commit()

        if db.query(DBUserNode).count() == 0:
            db.add_all([
                DBUserNode(username="adm_local", role="Admin", risk_score=0.25),
                DBUserNode(username="adm_domain", role="Admin", risk_score=0.05),
                DBUserNode(username="operator", role="Operator", risk_score=0.12),
                DBUserNode(username="compromised_operator", role="User", risk_score=0.88),
            ])
            db.commit()

        # Instantiate engine
        kg_engine = KnowledgeGraphEngine()
        
        # 1. Fetch graph, verify base nodes exist
        graph = kg_engine.get_graph(db, force_rebuild=True)
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) >= 0
        
        # 2. Assert assets and user nodes exist
        assets = db.query(DBAsset).all()
        assert len(assets) > 0
        
        users = db.query(DBUserNode).all()
        assert len(users) > 0

        # 3. Add custom relationship edge
        initial_edge_count = db.query(DBKnowledgeGraphEdge).count()
        edge = kg_engine.add_custom_edge(
            db=db,
            source_id="Asset:1",
            source_type="Asset",
            target_id="User:operator",
            target_type="User",
            rel_type="uses",
            weight=1.0,
            desc="Test edge"
        )
        assert edge.id is not None
        assert db.query(DBKnowledgeGraphEdge).count() == initial_edge_count + 1

        # 4. Verify custom edge exists in recompiled graph
        new_graph = kg_engine.get_graph(db, force_rebuild=True)
        edge_found = False
        for e in new_graph["edges"]:
            if e["source"] == "Asset:1" and e["target"] == "User:operator" and e["relationship"] == "uses":
                edge_found = True
                break
        assert edge_found

        # 5. Verify analytics calculations
        analytics = kg_engine.get_analytics(db)
        assert "top_connected" in analytics
        assert "top_risk_assets" in analytics
        assert "orphaned_detections" in analytics
        assert "campaign_clusters" in analytics
        assert "coverage_gaps" in analytics
        assert analytics["total_nodes"] == len(new_graph["nodes"])
        assert analytics["total_edges"] == len(new_graph["edges"])

        # Cleanup
        db.delete(edge)
        db.commit()

    finally:
        db.close()
