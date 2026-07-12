"""SQLAlchemy Database Models for Detection Rules and Revisions with mapped_column."""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base


class DBDetectionRule(Base):
    __tablename__ = "detection_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String, default="System")
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String, default="Enabled", index=True)  # Enabled, Disabled
    severity: Mapped[str] = mapped_column(String, default="Medium", index=True)  # High, Medium, Low
    category: Mapped[str] = mapped_column(String, default="Custom Rules", index=True)
    mitre_technique: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    detection_logic: Mapped[str] = mapped_column(Text, nullable=False)  # JSON or simple filter logic
    threshold: Mapped[int] = mapped_column(Integer, default=5)
    time_window: Mapped[int] = mapped_column(Integer, default=60)  # in seconds
    recommended_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Comma separated
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    revisions = relationship("DBRuleRevision", back_populates="rule", cascade="all, delete-orphan")


class DBRuleRevision(Base):
    __tablename__ = "rule_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("detection_rules.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    detection_logic: Mapped[str] = mapped_column(Text, nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    time_window: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changelog: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    author: Mapped[str] = mapped_column(String, default="System")

    rule = relationship("DBDetectionRule", back_populates="revisions")
