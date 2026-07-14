"""SQLAlchemy Database Models for Investigations, Collaboration, Timeline, and Evidence with SQLAlchemy 2.0 mapped_column."""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base


class DBInvestigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="Open", index=True)
    priority: Mapped[str] = mapped_column(String, default="Medium", index=True)
    severity: Mapped[str] = mapped_column(String, default="Medium", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    assigned_analyst: Mapped[str] = mapped_column(String, default="Unassigned", index=True)
    last_modified_by: Mapped[str] = mapped_column(String, default="System")
    risk_score: Mapped[float] = mapped_column(Float, default=0.5)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Soft delete support

    # Relationships
    evidence: Mapped[List["DBEvidence"]] = relationship("DBEvidence", back_populates="investigation", cascade="all, delete-orphan")
    analyst_notes: Mapped[List["DBAnalystNote"]] = relationship("DBAnalystNote", back_populates="investigation", cascade="all, delete-orphan")
    conversations: Mapped[List["DBCopilotLink"]] = relationship("DBCopilotLink", back_populates="investigation", cascade="all, delete-orphan")
    timeline: Mapped[List["DBTimelineEvent"]] = relationship("DBTimelineEvent", back_populates="investigation", cascade="all, delete-orphan")


class DBEvidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String, ForeignKey("investigations.id"), nullable=False, index=True)
    event: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, default="Medium")
    confidence: Mapped[str] = mapped_column(String, default="High")
    mitre: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    investigation: Mapped["DBInvestigation"] = relationship("DBInvestigation", back_populates="evidence")


class DBAnalystNote(Base):
    __tablename__ = "analyst_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String, ForeignKey("investigations.id"), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    investigation: Mapped["DBInvestigation"] = relationship("DBInvestigation", back_populates="analyst_notes")


class DBCopilotLink(Base):
    __tablename__ = "copilot_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String, ForeignKey("investigations.id"), nullable=False, index=True)
    conversation_key: Mapped[str] = mapped_column(String, nullable=False)

    investigation: Mapped["DBInvestigation"] = relationship("DBInvestigation", back_populates="conversations")


class DBTimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String, ForeignKey("investigations.id"), nullable=False, index=True)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)
    event: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_by: Mapped[str] = mapped_column(String, default="System")
    before_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    after_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    investigation: Mapped["DBInvestigation"] = relationship("DBInvestigation", back_populates="timeline")
