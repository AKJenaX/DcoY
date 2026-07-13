"""Threat Intelligence Fusion Engine."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.intelligence import DBThreatIndicator


class IntelligenceEngine:
    """Manages threat intelligence indicators, feeds lookup, and automated seeding."""

    DEFAULT_IOCS = [
        {"value": "198.51.100.42", "type": "IP", "confidence": 0.94, "feed": "Abuse.ch Feodo Tracker"},
        {"value": "198.51.100.200", "type": "IP", "confidence": 0.98, "feed": "Ransomware Tracker C2"},
        {"value": "203.0.113.88", "type": "IP", "confidence": 0.88, "feed": "Emerging Threats WAF Blocklist"},
        {"value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "type": "Hash", "confidence": 0.99, "feed": "VirusTotal Malicious Hashes"},
        {"value": "badmalwaredomain.com", "type": "Domain", "confidence": 0.92, "feed": "Spamhaus Command & Control list"},
        {"value": "http://badmalwaredomain.com/payload.exe", "type": "URL", "confidence": 0.97, "feed": "AlienVault OTX Malicious Links"}
    ]

    def seed_threat_indicators(self, db: Session):
        """Seeds default threat intelligence indicators if table is empty."""
        if db.query(DBThreatIndicator).count() == 0:
            for ioc in self.DEFAULT_IOCS:
                db_ioc = DBThreatIndicator(
                    ioc_value=ioc["value"],
                    ioc_type=ioc["type"],
                    confidence_score=ioc["confidence"],
                    threat_feed=ioc["feed"],
                    status="Active",
                    created_at=datetime.now(timezone.utc)
                )
                db.add(db_ioc)
            db.commit()

    def get_indicators(self, db: Session) -> List[DBThreatIndicator]:
        """Fetch all threat intelligence indicators."""
        self.seed_threat_indicators(db)
        return db.query(DBThreatIndicator).all()

    def add_indicator(
        self,
        db: Session,
        value: str,
        type: str,
        confidence: float = 1.0,
        feed: str = "Local Intelligence"
    ) -> DBThreatIndicator:
        """Register a new threat indicator."""
        # Check if already exists
        existing = db.query(DBThreatIndicator).filter(DBThreatIndicator.ioc_value == value.strip()).first()
        if existing:
            existing.confidence_score = confidence
            existing.threat_feed = feed
            existing.status = "Active"
            db.commit()
            return existing

        db_ioc = DBThreatIndicator(
            ioc_value=value.strip(),
            ioc_type=type.strip(),
            confidence_score=confidence,
            threat_feed=feed,
            status="Active",
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_ioc)
        db.commit()
        db.refresh(db_ioc)
        return db_ioc

    def query_ioc_reputation(self, db: Session, value: str) -> Optional[DBThreatIndicator]:
        """Lookup threat intelligence reputation for a given IOC value."""
        self.seed_threat_indicators(db)
        return db.query(DBThreatIndicator).filter(
            DBThreatIndicator.ioc_value == value.strip(),
            DBThreatIndicator.status == "Active"
        ).first()
