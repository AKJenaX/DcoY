"""SQLAlchemy Database Models for Threat Intelligence and Correlations."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class DBThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ioc_value: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    ioc_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # IP, Domain, URL, Hash, Hostname, User
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    threat_feed: Mapped[str] = mapped_column(String, default="Local Intelligence")
    status: Mapped[str] = mapped_column(String, default="Active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class DBIntelligenceCorrelation(Base):
    __tablename__ = "intelligence_correlations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    relationship_class: Mapped[str] = mapped_column(String, nullable=False)  # resolves_to, triggered_by, etc.
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
