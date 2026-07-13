"""SQLAlchemy Database Models for Response Playbooks and Playbook Executions."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class DBResponsePlaybook(Base):
    __tablename__ = "response_playbooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    steps_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list of strings (step instructions)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    category: Mapped[str] = mapped_column(String, default="Incident Response")


class DBPlaybookExecution(Base):
    __tablename__ = "playbook_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    playbook_id: Mapped[int] = mapped_column(Integer, nullable=False)
    playbook_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="Running", index=True)  # Running, Completed, Failed
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_step_index: Mapped[int] = mapped_column(Integer, default=0)
    execution_log_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON tracking each step's status, notes, timestamp
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of attached evidence dicts
