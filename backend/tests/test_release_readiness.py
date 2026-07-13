"""Release readiness and platform hardening validation tests."""

import pytest
from app.config import settings
from app.database import SessionLocal
from app.models.intelligence import DBThreatIndicator
from app.models.database_models import DBInvestigation
from app.utils.observability import StructuredJsonFormatter, setup_observability
from app.services.platform_registry import PlatformRegistry


def test_settings_validation():
    """Verify settings structure and checks behavior."""
    assert settings.ENV in ["development", "production", "testing"]
    assert settings.DATABASE_URL is not None
    
    # Assert validation check does not raise exceptions
    settings.validate()


def test_observability_formatting():
    """Verify logging setup does not raise exception."""
    setup_observability(log_level="DEBUG", json_format=True)
    setup_observability(log_level="INFO", json_format=False)


def test_platform_health_diagnostics():
    """Verify platform registry diagnostics collection."""
    db = SessionLocal()
    try:
        registry = PlatformRegistry()
        status = registry.get_health_status(db)
        
        assert "uptime_seconds" in status
        assert "services" in status
        assert "metrics" in status
        assert status["services"]["fastapi_backend"] == "Online"
    finally:
        db.close()
