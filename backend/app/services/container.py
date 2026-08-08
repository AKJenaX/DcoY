"""Shared Service Container providing singleton security engine instances and metrics."""

import logging
from app.services.attack_path_engine import AttackPathEngine
from app.services.correlation_engine import CorrelationEngine
from app.services.incident_response import IncidentResponseService
from app.services.intelligence_engine import IntelligenceEngine
from app.services.knowledge_graph_engine import KnowledgeGraphEngine
from app.services.platform_registry import PlatformRegistry
from app.services.playbook_engine import PlaybookEngine
from app.services.rule_engine import RuleEngine
from app.services.rule_validator import RuleValidator
from app.services.search_service import SearchService
from app.services.workflow_engine import WorkflowEngine
from app.utils.metrics import metrics_collector

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Central singleton container managing stateful platform service engines."""

    def __init__(self) -> None:
        logger.info("Initializing DcoY Shared Service Container singletons")
        self.rule_engine = RuleEngine()
        self.rule_validator = RuleValidator()
        self.workflow_engine = WorkflowEngine()
        self.knowledge_graph_engine = KnowledgeGraphEngine()
        self.attack_path_engine = AttackPathEngine(self.knowledge_graph_engine)
        self.playbook_engine = PlaybookEngine()
        self.intelligence_engine = IntelligenceEngine()
        self.correlation_engine = CorrelationEngine()
        self.platform_registry = PlatformRegistry()
        self.search_service = SearchService()
        self.incident_service = IncidentResponseService()
        self.metrics_collector = metrics_collector


# Export central container singleton
container = ServiceContainer()
