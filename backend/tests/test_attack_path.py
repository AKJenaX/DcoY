"""Unit tests for Attack Path Engine."""

import pytest
from app.database import SessionLocal
from app.services.knowledge_graph_engine import KnowledgeGraphEngine
from app.services.attack_path_engine import AttackPathEngine


def test_attack_path_engine():
    db = SessionLocal()
    try:
        # Instantiate engines
        kg_engine = KnowledgeGraphEngine()
        ap_engine = AttackPathEngine(kg_engine)

        # 1. Force rebuild to load all initial nodes & edges
        kg_engine.rebuild_graph(db)

        # 2. Run shortest path tracer
        source = "Indicator:198.51.100.42"
        target = "Indicator:badmalwaredomain.com"
        
        path_info = ap_engine.find_shortest_path(db, source, target)
        assert "path_found" in path_info
        assert "steps" in path_info
        assert "nodes" in path_info
        assert "defensive_controls" in path_info

        # If a path was successfully computed, trace details
        if path_info["path_found"]:
            assert path_info["steps"][0] == source
            assert path_info["steps"][-1] == target
            assert len(path_info["nodes"]) == len(path_info["steps"])
            assert len(path_info["defensive_controls"]) > 0

        # 3. Test attack path staging detection
        paths = ap_engine.detect_attack_paths(db)
        assert len(paths) > 0
        for path in paths:
            assert "path_id" in path
            assert "stages" in path
            assert "defensive_controls" in path
            
            # Verify stage ordering
            stages_list = [s["stage"] for s in path["stages"]]
            assert "Initial Access" in stages_list
            assert "Exfiltration" in stages_list

    finally:
        db.close()
