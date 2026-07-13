"""SQLAlchemy Database Models for SOAR Workflows and Executions."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class DBWorkflow(Base):
    __tablename__ = "soar_workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String, default="Severity High", index=True)
    status: Mapped[str] = mapped_column(String, default="Enabled", index=True)  # Enabled, Disabled
    steps_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list of dicts describing workflow steps


class DBWorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    workflow_name: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, default="Running", index=True)  # Running, Completed, Failed, Suspended
    current_step_index: Mapped[int] = mapped_column(Integer, default=0)
    execution_log_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON audit trail of action results
    linked_investigation_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
