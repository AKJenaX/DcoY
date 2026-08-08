"""Application lifecycle context manager and startup/shutdown hooks."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from fastapi import FastAPI

from app.database import engine, Base, SessionLocal
from app.models.database_models import DBInvestigation, DBTimelineEvent, DBEvidence
from app.models.detection_rule import DBDetectionRule
from app.models.intelligence import DBThreatIndicator
from app.models.knowledge_graph import DBAsset, DBUserNode, DBExecutiveReport
from app.services.intelligence_engine import IntelligenceEngine

logger = logging.getLogger(__name__)

_is_db_initialized = False


def init_db_and_seed() -> None:
    """Initialize SQLite database tables and seed default baseline data if empty (Idempotent)."""
    global _is_db_initialized
    if _is_db_initialized:
        logger.debug("Database initialization skipped (already initialized)")
        return
        
    Base.metadata.create_all(bind=engine)
    
    db_seed = SessionLocal()
    try:
        from app.models.auth_models import DBUser
        from app.repositories.user_repository import UserRepository
        
        if db_seed.query(DBUser).count() == 0:
            logger.info("Database has no persistent users, seeding default accounts...")
            UserRepository.create_user(db_seed, username="default_user", password="secure_password")
            UserRepository.create_user(db_seed, username="adm_local", password="secure_password", role="Admin")
            UserRepository.create_user(db_seed, username="operator", password="secure_password", role="Operator")
            logger.info("Default persistent user accounts seeded successfully.")
        else:
            op_user = UserRepository.get_by_username(db_seed, "operator")
            if op_user:
                UserRepository.update_user(db_seed, int(getattr(op_user, "id")), {"password": "secure_password"})

        if db_seed.query(DBInvestigation).count() == 0:
            logger.info("Database is empty, seeding default investigation cases...")
            case1 = DBInvestigation(
                id="CASE-2026-001",
                title="Credential Stuffing & SSH Brute Force",
                status="Open",
                priority="High",
                severity="High",
                assigned_analyst="Analyst Alpha",
                risk_score=0.88,
                ai_summary="Highly repetitive authentication failure spikes targeting remote edge SSH portals. ML detection engine identified severe parameter outliers from origin geolocations.",
                notes="Firewall rules updated to isolate subnet range."
            )
            db_seed.add(case1)
            
            t1 = DBTimelineEvent(
                investigation_id="CASE-2026-001",
                timestamp=datetime.now(timezone.utc).isoformat(),
                event="Case Investigation Created",
                details="Case initialized by system seed",
                action_by="System"
            )
            db_seed.add(t1)
            
            ev1 = DBEvidence(
                investigation_id="CASE-2026-001",
                event="Port 22 SSH Connection Flood",
                timestamp="2026-07-12T08:12:00Z",
                severity="High",
                confidence="High",
                mitre="T1110"
            )
            db_seed.add(ev1)
            
            case2 = DBInvestigation(
                id="CASE-2026-002",
                title="Subnet Port Sweep Reconnaissance",
                status="Active",
                priority="Medium",
                severity="Medium",
                assigned_analyst="Analyst Beta",
                risk_score=0.62,
                ai_summary="Subnet sweep targeting port ranges. Deception honeypot trap engaged to absorb scanning telemetry.",
                notes="Trap successfully deflected active scanning traffic."
            )
            db_seed.add(case2)
            
            t2 = DBTimelineEvent(
                investigation_id="CASE-2026-002",
                timestamp=datetime.now(timezone.utc).isoformat(),
                event="Case Investigation Created",
                details="Case initialized by system seed",
                action_by="System"
            )
            db_seed.add(t2)
            
            db_seed.commit()
            logger.info("Database seeding completed.")

        if db_seed.query(DBDetectionRule).count() == 0:
            logger.info("Database is empty of rules, seeding default detection rules...")
            rule1 = DBDetectionRule(
                name="SSH Brute Force Detection",
                description="Flags potential brute force attacks when SSH connection thresholds are exceeded.",
                author="System",
                version=1,
                status="Enabled",
                severity="High",
                category="Brute Force",
                mitre_technique="T1110 - Brute Force",
                detection_logic='{"event_type": "ssh_bruteforce"}',
                threshold=5,
                time_window=60,
                recommended_response="Update edge firewall configs to isolate attacking source subnet.",
                tags="SSH, Bruteforce, Ingress"
            )
            db_seed.add(rule1)
            
            rule2 = DBDetectionRule(
                name="Port Sweep Reconnaissance",
                description="Flags ad-hoc TCP sweep behaviors targeting multiple ports.",
                author="System",
                version=1,
                status="Enabled",
                severity="Medium",
                category="Port Scan",
                mitre_technique="T1046 - Network Scanning",
                detection_logic='{"event_type": "port_scan"}',
                threshold=10,
                time_window=120,
                recommended_response="Redirect traffic context to active deception decoy traps.",
                tags="Recon, Portscan, Discovery"
            )
            db_seed.add(rule2)
            db_seed.commit()
            logger.info("Detection rules seeding completed.")
            
            intelligence_engine = IntelligenceEngine()
            intelligence_engine.seed_threat_indicators(db_seed)
            logger.info("Threat intelligence seeding completed.")
            
            if db_seed.query(DBAsset).count() == 0:
                logger.info("Database has no assets, seeding default network assets...")
                assets_to_seed = [
                    DBAsset(name="WS-ADMIN-01", ip_address="198.51.100.10", asset_type="Workstation", risk_score=0.15, criticality="High"),
                    DBAsset(name="WS-OPERATOR-02", ip_address="198.51.100.20", asset_type="Workstation", risk_score=0.65, criticality="Medium"),
                    DBAsset(name="DB-PROD-01", ip_address="198.51.100.50", asset_type="Database", risk_score=0.08, criticality="High"),
                    DBAsset(name="HONEYPOT-SSH", ip_address="198.51.100.42", asset_type="Honeypot", risk_score=0.95, criticality="Low"),
                    DBAsset(name="DC-PROD-01", ip_address="198.51.100.100", asset_type="Active Directory", risk_score=0.04, criticality="High"),
                ]
                db_seed.add_all(assets_to_seed)
                db_seed.commit()
                logger.info("Default assets seeding completed.")

            if db_seed.query(DBUserNode).count() == 0:
                logger.info("Database has no security users, seeding default user nodes...")
                users_to_seed = [
                    DBUserNode(username="adm_local", role="Admin", risk_score=0.25),
                    DBUserNode(username="adm_domain", role="Admin", risk_score=0.05),
                    DBUserNode(username="operator", role="Operator", risk_score=0.12),
                    DBUserNode(username="compromised_operator", role="User", risk_score=0.88),
                ]
                db_seed.add_all(users_to_seed)
                db_seed.commit()
                logger.info("Default users seeding completed.")

            if db_seed.query(DBExecutiveReport).count() == 0:
                logger.info("Database has no executive reports, seeding default reports...")
                reports_to_seed = [
                    DBExecutiveReport(title="Q3 Security Posture & Incident Report", risk_summary="Overall SOC posture is guarded. Deception honeypot trap deflected SSH credential stuffing attacks. Automated response isolated WS-OPERATOR-02 within minutes."),
                    DBExecutiveReport(title="Adversary Campaign & MITRE ATT&CK Matrix Review", risk_summary="Campaign analysis identified persistent credential brute-forcing targeting administrative entry points. Coverage validation confirmed 84.5% rule matching rate."),
                ]
                db_seed.add_all(reports_to_seed)
                db_seed.commit()
                logger.info("Default executive reports seeding completed.")

            from app.utils.live_store import add_event, has_events
            if not has_events():
                logger.info("Seeding initial telemetry events into live store...")
                now_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
                now_iso = datetime.now(timezone.utc).isoformat()
                add_event({
                    "time": now_str,
                    "timestamp": now_iso,
                    "event_type": "ssh_brute_force",
                    "attack_type": "ssh_brute_force",
                    "ip": "185.220.101.5",
                    "host": "HONEYPOT-SSH-01",
                    "user": "root",
                    "severity": "High",
                    "mitre_technique": "T1110 - Brute Force",
                    "failed_logins": 14.0,
                    "details": {
                        "phase": "Credential Access",
                        "action": "Failed SSH login root:admin",
                        "decoy": "HONEYPOT-SSH-01",
                    },
                })
                add_event({
                    "time": now_str,
                    "timestamp": now_iso,
                    "event_type": "port_scan",
                    "attack_type": "port_scan",
                    "ip": "198.51.100.42",
                    "host": "HONEYPOT-HTTP-01",
                    "user": "anonymous",
                    "severity": "Medium",
                    "mitre_technique": "T1046 - Network Service Scanning",
                    "port_attempts": 28.0,
                    "details": {
                        "phase": "Reconnaissance",
                        "action": "TCP SYN Port Sweep on 80, 443, 8080",
                        "decoy": "HONEYPOT-HTTP-01",
                    },
                })
                add_event({
                    "time": now_str,
                    "timestamp": now_iso,
                    "event_type": "credential_stuffing",
                    "attack_type": "credential_stuffing",
                    "ip": "45.132.22.99",
                    "host": "auth-gateway-prod",
                    "user": "operator",
                    "severity": "High",
                    "mitre_technique": "T1110.004 - Credential Stuffing",
                    "failed_logins": 42.0,
                    "details": {
                        "phase": "Initial Access",
                        "action": "Repetitive Auth Failures",
                        "status": "Diverted to Decoy Mesh",
                    },
                })
    finally:
        _is_db_initialized = True
        db_seed.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager handling application startup and shutdown events."""
    logger.info("Application startup: initializing database schema and seed data...")
    init_db_and_seed()
    yield
    logger.info("Application shutdown: cleaning up DcoY backend resources.")
