import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add backend directory to sys.path to allow imports of app models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import SQLAlchemy Base and models for autogenerate mapping
from app.database import Base
from app.models.knowledge_graph import DBAsset, DBUserNode, DBExecutiveReport, DBKnowledgeGraphEdge
from app.models.intelligence import DBThreatIndicator, DBIntelligenceCorrelation
from app.models.database_models import DBInvestigation, DBEvidence
from app.models.detection_rule import DBDetectionRule
from app.models.simulation import DBSimulationRun
from app.models.workflow import DBWorkflowExecution, DBWorkflow
from app.models.playbook import DBResponsePlaybook, DBPlaybookExecution

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
