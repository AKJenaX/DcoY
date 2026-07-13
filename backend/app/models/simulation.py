"""SQLAlchemy Database Models for Purple Team & Attack Simulation."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class DBSimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, default="Pending", index=True)  # Pending, Running, Completed, Failed
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    scanned_events_count: Mapped[int] = mapped_column(Integer, default=0)
    detection_success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    missed_detections_count: Mapped[int] = mapped_column(Integer, default=0)
    coverage_score: Mapped[float] = mapped_column(Float, default=0.0)
    average_detection_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    simulation_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    mitre_techniques: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Comma separated
    telemetry_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of synthetic telemetry events
    results_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON results of evaluations
