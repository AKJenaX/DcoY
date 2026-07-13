"""SQLAlchemy Database Models for Security Knowledge Graph entities and edges."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class DBAsset(Base):
    __tablename__ = "security_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # Workstation, Server, Database, Honeypot, Active Directory
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    criticality: Mapped[str] = mapped_column(String, default="Medium", index=True)  # High, Medium, Low
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class DBUserNode(Base):
    __tablename__ = "security_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, default="User", index=True)  # Admin, Operator, Executive, ServiceAccount, EndUser
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class DBExecutiveReport(Base):
    __tablename__ = "executive_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    risk_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class DBKnowledgeGraphEdge(Base):
    __tablename__ = "knowledge_graph_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # relationship_type matches: detected_by, investigated_by, orchestrated_by, mitigated_by,
    # simulated_by, related_to, originated_from, targets, uses, affects
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
