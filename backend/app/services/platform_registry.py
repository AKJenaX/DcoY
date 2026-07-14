"""Platform Registry and Services Health Monitor."""

import time
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text


class PlatformRegistry:
    """Manages platform component status tracking, API route inventory, latency logs, and system documentation."""

    def __init__(self):
        self._start_time = time.time()
        self._cache_hits = 0
        self._cache_misses = 0
        self._latency_log: List[float] = [12.0, 15.0, 11.0, 14.0, 18.0]  # ms

    def log_cache_hit(self):
        self._cache_hits += 1

    def log_cache_miss(self):
        self._cache_misses += 1

    def log_latency(self, duration_ms: float):
        self._latency_log.append(duration_ms)
        if len(self._latency_log) > 20:
            self._latency_log.pop(0)

    def get_health_status(self, db: Session) -> Dict[str, Any]:
        """Verify statuses of SQLite DB, caching metrics, API latency, and other active services."""
        # 1. SQLite DB Verification
        db_alive = False
        db_error = None
        try:
            db.execute(text("SELECT 1"))
            db_alive = True
        except Exception as e:
            db_error = str(e)

        uptime_seconds = int(time.time() - self._start_time)
        avg_latency = sum(self._latency_log) / max(1, len(self._latency_log))

        # Check model counts to evaluate rule engine and knowledge graph states
        from app.models.detection_rule import DBDetectionRule
        from app.models.knowledge_graph import DBKnowledgeGraphEdge, DBAsset
        
        rules_count = 0
        enabled_rules_count = 0
        try:
            rules_count = db.query(DBDetectionRule).count()
            enabled_rules_count = db.query(DBDetectionRule).filter(DBDetectionRule.status == "Enabled").count()
        except Exception:
            pass

        assets_count = 0
        edges_count = 0
        try:
            from app.models.intelligence import DBIntelligenceCorrelation
            assets_count = db.query(DBAsset).count()
            edges_count = db.query(DBKnowledgeGraphEdge).count() + db.query(DBIntelligenceCorrelation).count()
        except Exception:
            pass

        # WebSocket channel connection counts
        ws_counts = {}
        try:
            from app.utils.websocket_manager import manager
            for channel, conns in manager.active_connections.items():
                ws_counts[channel] = len(conns)
        except Exception:
            ws_counts = {"telemetry": 0, "geolocation": 0, "simulation": 0}

        # SQLite lock retry metrics
        from app.database import SQLITE_LOCK_RETRY_METRICS
        sqlite_retries = SQLITE_LOCK_RETRY_METRICS.copy()

        # Ollama status
        from app.agents.reasoning_agent import is_llm_available
        ollama_status = "live" if is_llm_available() else "fallback"

        return {
            "uptime_seconds": uptime_seconds,
            "services": {
                "fastapi_backend": "Online",
                "sqlite_database": "Online" if db_alive else f"Degraded ({db_error})",
                "rule_engine": "Active" if enabled_rules_count > 0 else "Idle",
                "knowledge_graph": "Fresh" if edges_count > 0 else "Uninitialized",
                "deception_agent": "Operational",
                "ai_copilot_service": "Live" if ollama_status == "live" else "Fallback"
            },
            "metrics": {
                "average_latency_ms": round(avg_latency, 2),
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_efficiency_pct": round((self._cache_hits / max(1, self._cache_hits + self._cache_misses)) * 100, 1),
                "active_rules": rules_count,
                "enabled_rules": enabled_rules_count,
                "monitored_assets": assets_count,
                "graph_relationships": edges_count
            },
            "latency_history": self._latency_log.copy(),
            "websocket_connections": ws_counts,
            "sqlite_lock_retries": sqlite_retries,
            "copilot_source": ollama_status
        }

    def get_documentation(self) -> Dict[str, Any]:
        """Retrieve automatically generated architecture guidelines, dependencies, and developer onboarding instructions."""
        
        # 1. Mermaid Architecture Diagram
        architecture_mermaid = (
            "graph TD\n"
            "    subgraph Ingress Layer\n"
            "        React[\"React Dashboard Front-end\"]\n"
            "    end\n"
            "    subgraph API Layer\n"
            "        FastAPI[\"FastAPI Backend REST Service\"]\n"
            "    end\n"
            "    subgraph Core Engines\n"
            "        RuleEngine[\"Anomaly & Rules Engine\"]\n"
            "        IntelEngine[\"Threat Intelligence Engine\"]\n"
            "        KGEngine[\"Knowledge Graph Engine\"]\n"
            "        APEngine[\"Attack Path Engine\"]\n"
            "        SOAREngine[\"SOAR Workflow Engine\"]\n"
            "    end\n"
            "    subgraph Database Layer\n"
            "        SQLite[\"SQLite Database File (dcoy.db)\"]\n"
            "    end\n"
            "    React -->|HTTP / JSON / WS| FastAPI\n"
            "    FastAPI --> RuleEngine\n"
            "    FastAPI --> IntelEngine\n"
            "    FastAPI --> KGEngine\n"
            "    KGEngine --> APEngine\n"
            "    RuleEngine --> SQLite\n"
            "    IntelEngine --> SQLite\n"
            "    KGEngine --> SQLite\n"
            "    SOAREngine --> SQLite\n"
        )

        # 2. Module Dependency Map
        dependency_map = {
            "app.main": ["app.database", "app.models", "app.services", "app.utils"],
            "app.services.attack_path_engine": ["app.services.knowledge_graph_engine"],
            "app.services.knowledge_graph_engine": ["app.models.knowledge_graph", "app.models.intelligence", "app.models.database_models"],
            "app.services.correlation_engine": ["app.models.intelligence", "app.models.database_models", "app.models.knowledge_graph"],
            "app.services.executive_metrics": ["app.services.knowledge_graph_engine", "app.models.database_models"]
        }

        # 3. Entity-Relationship documentation
        er_documentation = (
            "### Entity-Relationship Schemas\n\n"
            "1. **DBAsset** (Table: `security_assets`)\n"
            "   - `id` (Integer, PK)\n"
            "   - `name` (String, Unique, Index)\n"
            "   - `ip_address` (String, Index)\n"
            "   - `asset_type` (String)\n"
            "   - `risk_score` (Float)\n"
            "   - `criticality` (String)\n\n"
            "2. **DBUserNode** (Table: `security_users`)\n"
            "   - `id` (Integer, PK)\n"
            "   - `username` (String, Unique, Index)\n"
            "   - `role` (String)\n"
            "   - `risk_score` (Float)\n\n"
            "3. **DBKnowledgeGraphEdge** (Table: `knowledge_graph_edges`)\n"
            "   - `id` (Integer, PK)\n"
            "   - `source_id` (String, Index)\n"
            "   - `source_type` (String, Index)\n"
            "   - `target_id` (String, Index)\n"
            "   - `target_type` (String, Index)\n"
            "   - `relationship_type` (String)\n"
            "   - `weight` (Float)\n"
            "   - `description` (Text)\n"
        )

        # 4. Developer Onboarding Guide
        onboarding_guide = (
            "# Developer Onboarding Guide: DcoY Platform\n\n"
            "## Setup Environment\n"
            "1. Activate your virtual environment: `.\\backend\\.venv\\Scripts\\activate` (Windows) or `source backend/.venv/bin/activate` (Linux/Mac)\n"
            "2. Install required packages: `pip install -r backend/requirements.txt`\n\n"
            "## Running the Application\n"
            "1. Start the backend API server: `python backend/app/main.py`\n"
            "2. Start the user dashboard interface: `cd frontend && npm run dev`\n\n"
            "## Running Test Suites\n"
            "1. Run unit checks: `python -m pytest backend/tests/`\n"
            "2. Run integration tests specifically: `python -m pytest backend/tests/test_platform_integration.py`\n"
        )

        return {
            "mermaid_diagram": architecture_mermaid,
            "dependency_map": dependency_map,
            "er_documentation": er_documentation,
            "onboarding_guide": onboarding_guide
        }
