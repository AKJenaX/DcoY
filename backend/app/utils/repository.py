"""Repository pattern implementation for DB CRUD and Advanced Search."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.database_models import (
    DBInvestigation,
    DBEvidence,
    DBAnalystNote,
    DBCopilotLink,
    DBTimelineEvent
)


class InvestigationRepository:
    """Encapsulates all database query and persistence logic for cases."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any], user: str) -> DBInvestigation:
        """Create a new case, triggering audit trail logs."""
        cid = data.get("id")
        investigation = DBInvestigation(
            id=cid,
            title=data.get("title"),
            status=data.get("status", "Open"),
            priority=data.get("priority", "Medium"),
            severity=data.get("severity", "Medium"),
            assigned_analyst=data.get("assigned_analyst", "Unassigned"),
            last_modified_by=user,
            risk_score=data.get("risk_score", 0.5),
            ai_summary=data.get("ai_summary"),
            notes=data.get("notes")
        )
        db.add(investigation)
        
        # Add initial timeline log
        t_event = DBTimelineEvent(
            investigation_id=cid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="Case Investigation Created",
            details=f"Case initialized by user: {user}",
            action_by=user
        )
        db.add(t_event)
        db.commit()
        db.refresh(investigation)
        return investigation

    @staticmethod
    def get_by_id(db: Session, cid: str) -> Optional[DBInvestigation]:
        """Fetch investigation detail resolving dependencies with joinedload to avoid N+1 queries."""
        return db.query(DBInvestigation).options(
            joinedload(DBInvestigation.evidence),
            joinedload(DBInvestigation.analyst_notes),
            joinedload(DBInvestigation.conversations),
            joinedload(DBInvestigation.timeline)
        ).filter(
            DBInvestigation.id == cid,
            DBInvestigation.deleted_at.is_(None)
        ).first()

    @staticmethod
    def get_list(
        db: Session,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        analyst: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[DBInvestigation]:
        """Lazy-loaded list of active cases with search filtering and sorting."""
        query = db.query(DBInvestigation).filter(DBInvestigation.deleted_at.is_(None))
        
        # Apply filters
        if status and status != "All":
            query = query.filter(DBInvestigation.status == status)
        if severity and severity != "All":
            query = query.filter(DBInvestigation.severity == severity)
        if analyst and analyst != "All":
            query = query.filter(DBInvestigation.assigned_analyst == analyst)
            
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                DBInvestigation.id.like(search_pattern) |
                DBInvestigation.title.like(search_pattern) |
                DBInvestigation.assigned_analyst.like(search_pattern)
            )

        # Sorting
        if sort_by == "Severity":
            # Simple ordering on raw value
            query = query.order_by(DBInvestigation.severity.desc())
        elif sort_by == "Priority":
            query = query.order_by(DBInvestigation.priority.desc())
        elif sort_by == "Created Time":
            query = query.order_by(DBInvestigation.created_at.asc())
        else:
            query = query.order_by(DBInvestigation.updated_at.desc())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        cid: str,
        updates: Dict[str, Any],
        user: str
    ) -> Optional[DBInvestigation]:
        """Updates case details and logs immutable audit trail events of state transitions."""
        case = db.query(DBInvestigation).filter(
            DBInvestigation.id == cid,
            DBInvestigation.deleted_at.is_(None)
        ).first()
        if not case:
            return None

        # Track audit timeline modifications
        timeline_logs = []
        now_str = datetime.now(timezone.utc).isoformat()
        
        for k, val in updates.items():
            if hasattr(case, k):
                old_val = getattr(case, k)
                if old_val != val:
                    setattr(case, k, val)
                    timeline_logs.append(DBTimelineEvent(
                        investigation_id=cid,
                        timestamp=now_str,
                        event=f"Attribute Modified: {k}",
                        before_value=str(old_val),
                        after_value=str(val),
                        action_by=user
                    ))
                    
        case.last_modified_by = user
        case.updated_at = datetime.now(timezone.utc)
        
        for log in timeline_logs:
            db.add(log)
            
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def soft_delete(db: Session, cid: str, user: str) -> bool:
        """Mark case as deleted without purging row data, capturing log trace."""
        case = db.query(DBInvestigation).filter(
            DBInvestigation.id == cid,
            DBInvestigation.deleted_at.is_(None)
        ).first()
        if not case:
            return False

        case.deleted_at = datetime.now(timezone.utc)
        case.last_modified_by = user
        
        log = DBTimelineEvent(
            investigation_id=cid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="Case Soft Deleted",
            details=f"Case soft-deleted by user: {user}",
            action_by=user
        )
        db.add(log)
        db.commit()
        return True

    @staticmethod
    def add_evidence(db: Session, cid: str, data: Dict[str, Any], user: str) -> DBEvidence:
        """Link evidence to case and append event log."""
        evidence = DBEvidence(
            investigation_id=cid,
            event=data.get("event"),
            timestamp=data.get("timestamp"),
            severity=data.get("severity", "Medium"),
            confidence=data.get("confidence", "High"),
            mitre=data.get("mitre")
        )
        db.add(evidence)
        
        log = DBTimelineEvent(
            investigation_id=cid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="Evidence Attached",
            details=f"Evidence event '{data.get('event')}' linked to case.",
            action_by=user
        )
        db.add(log)
        db.commit()
        return evidence

    @staticmethod
    def add_copilot_link(db: Session, cid: str, key: str, user: str) -> DBCopilotLink:
        """Link copilot conversation token session to investigation case."""
        link = DBCopilotLink(
            investigation_id=cid,
            conversation_key=key
        )
        db.add(link)
        
        log = DBTimelineEvent(
            investigation_id=cid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="Copilot Chat Linked",
            details=f"Copilot dialogue session key '{key}' linked.",
            action_by=user
        )
        db.add(log)
        db.commit()
        return link

    @staticmethod
    def add_analyst_note(db: Session, cid: str, note_text: str, user: str) -> DBAnalystNote:
        """Appends analyst notes ledger log."""
        note = DBAnalystNote(
            investigation_id=cid,
            author=user,
            content=note_text
        )
        db.add(note)
        
        log = DBTimelineEvent(
            investigation_id=cid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="Analyst Note Added",
            details="New analyst note saved to ledger.",
            action_by=user
        )
        db.add(log)
        db.commit()
        return note
