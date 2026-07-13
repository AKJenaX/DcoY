"""Service for managing response playbooks and execution runs."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.playbook import DBResponsePlaybook, DBPlaybookExecution
from app.models.database_models import DBTimelineEvent


class PlaybookEngine:
    """Manages response playbook templates, seeding, execution checklist progress, and case linking."""

    BUILT_IN_PLAYBOOKS = [
        {
            "name": "Malware Containment",
            "description": "Structured steps to isolate infected host nodes, verify file hashes, and eradicate malicious process chains.",
            "category": "Malware",
            "estimated_duration_minutes": 25,
            "steps": [
                "Verify malware file hash on threat intelligence databases (e.g. VirusTotal)",
                "Isolate endpoint from local corporate network",
                "Terminate malicious parent-child process chains",
                "Run local anti-malware full system scan",
                "Collect memory dump for forensics analysis"
            ]
        },
        {
            "name": "Credential Compromise",
            "description": "Incident workflow targeting compromised user profiles, rogue API keys, and unauthorized MFA additions.",
            "category": "Access Control",
            "estimated_duration_minutes": 30,
            "steps": [
                "Identify source IP and audit anomalous sign-in logs",
                "Force password reset and expire all active user sessions",
                "Audit recent API key generation and OAuth application scopes",
                "Check for recent MFA device additions or changes",
                "Verify security logs for secondary privilege escalation attempts"
            ]
        },
        {
            "name": "Ransomware Response",
            "description": "Priority containment flow to sever SMB connections, stop shadow copies deletion, and secure restore backups.",
            "category": "Ransomware",
            "estimated_duration_minutes": 60,
            "steps": [
                "Identify patient-zero network interface card (NIC)",
                "Enforce temporary SMB/CIFS port blocks on workstation subnets",
                "Kill shadow copy deletion processes and lock down file structures",
                "Verify integrity of offline and cloud backup data paths",
                "Register firewall block rules targeting command-and-control beacon IPs"
            ]
        },
        {
            "name": "Data Exfiltration",
            "description": "Containment protocol to block egress connections, audit access logs, and examine cloud storage.",
            "category": "Exfiltration",
            "estimated_duration_minutes": 45,
            "steps": [
                "Identify high-volume outbound network flows and target destination IPs",
                "Enforce egress firewall filters blocking connection ports",
                "Audit read/access logs to affected databases and cloud buckets",
                "Revoke compromise credentials for involved service accounts",
                "Engage ISP data stream capture diagnostics"
            ]
        },
        {
            "name": "Insider Threat",
            "description": "Investigation playbook to preserve local machine data, revoke tokens, and initiate administrative escalation.",
            "category": "Insider Threat",
            "estimated_duration_minutes": 120,
            "steps": [
                "Audit target employee administrative and data access logs",
                "Clone and isolate local workstation disk drive",
                "Revoke active authentication cookies and SSO profiles",
                "Escalate incident ticket to HR, legal, and department leadership",
                "Deploy security monitoring agents on adjacent database nodes"
            ]
        },
        {
            "name": "Web Application Attack",
            "description": "Triage steps to analyze WAF logs, apply virtual patches, and restore target services.",
            "category": "Web App Security",
            "estimated_duration_minutes": 20,
            "steps": [
                "Inspect Web Application Firewall (WAF) logs for injection payloads",
                "Blacklist attacking source IP on cloud load balancer/firewall",
                "Apply virtual patch rules on vulnerable REST endpoints",
                "Verify and restore target web server files to clean pristine state",
                "Audit database activity for secondary lateral pivots"
            ]
        },
        {
            "name": "Cloud Misconfiguration",
            "description": "Remediation workflow for public S3 buckets, permissive security groups, and IAM rollbacks.",
            "category": "Cloud Security",
            "estimated_duration_minutes": 15,
            "steps": [
                "Identify public-facing storage buckets and S3 repositories",
                "Enforce private Access Control List (ACL) configuration policies",
                "Audit recent IAM policy changes and role assumptions",
                "Scan active security group ingress rules for wildcard (0.0.0.0/0) access",
                "Re-validate IaC template deployment configuration states"
            ]
        },
        {
            "name": "Custom Playbook",
            "description": "Standard baseline investigation checklist for general SOC alert triaging.",
            "category": "Custom Playbook",
            "estimated_duration_minutes": 30,
            "steps": [
                "Triage initial alerts telemetry and anomalies data",
                "Identify affected user profiles, host assets, and networks",
                "Implement localized host containment and monitoring measures",
                "Document action steps taken and compile post-incident report"
            ]
        }
    ]

    def seed_built_in_playbooks(self, db: Session):
        """Seeds standard response playbooks if none exist in the database."""
        if db.query(DBResponsePlaybook).count() == 0:
            for p in self.BUILT_IN_PLAYBOOKS:
                playbook = DBResponsePlaybook(
                    name=p["name"],
                    description=p["description"],
                    steps_json=json.dumps(p["steps"]),
                    estimated_duration_minutes=p["estimated_duration_minutes"],
                    category=p["category"]
                )
                db.add(playbook)
            db.commit()

    def get_all_playbooks(self, db: Session) -> List[DBResponsePlaybook]:
        """Fetch all response playbook templates."""
        self.seed_built_in_playbooks(db)
        return db.query(DBResponsePlaybook).all()

    def create_playbook_template(
        self,
        db: Session,
        name: str,
        description: str,
        steps: List[str],
        duration: int = 30,
        category: str = "Incident Response"
    ) -> DBResponsePlaybook:
        """Create a new custom response playbook template."""
        playbook = DBResponsePlaybook(
            name=name.strip(),
            description=description.strip(),
            steps_json=json.dumps(steps),
            estimated_duration_minutes=duration,
            category=category
        )
        db.add(playbook)
        db.commit()
        db.refresh(playbook)
        return playbook

    def get_playbook_execution(self, db: Session, execution_id: int) -> Optional[DBPlaybookExecution]:
        """Retrieve a specific playbook execution."""
        return db.query(DBPlaybookExecution).filter(DBPlaybookExecution.id == execution_id).first()

    def get_executions_for_case(self, db: Session, case_id: str) -> List[DBPlaybookExecution]:
        """Retrieve all playbook execution runs associated with a specific case."""
        return db.query(DBPlaybookExecution).filter(DBPlaybookExecution.investigation_id == case_id).all()

    def trigger_playbook(self, db: Session, case_id: str, playbook_id: int) -> DBPlaybookExecution:
        """Assign and initiate a response playbook execution run for a case."""
        playbook = db.query(DBResponsePlaybook).filter(DBResponsePlaybook.id == playbook_id).first()
        if not playbook:
            raise ValueError(f"Playbook template ID {playbook_id} not found.")

        steps = json.loads(playbook.steps_json)
        
        # Prepare standard step status structures
        execution_log = []
        for step in steps:
            execution_log.append({
                "step": step,
                "status": "Pending",
                "completed_at": None,
                "note": ""
            })

        execution = DBPlaybookExecution(
            investigation_id=case_id,
            playbook_id=playbook.id,
            playbook_name=playbook.name,
            status="Running",
            started_at=datetime.now(timezone.utc),
            current_step_index=0,
            execution_log_json=json.dumps(execution_log),
            notes="",
            evidence_json=json.dumps([])
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        # Log timeline event to case details
        timeline = DBTimelineEvent(
            investigation_id=case_id,
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            event="Playbook Triggered",
            details=f"Assigned and initiated the response playbook: '{playbook.name}'",
            action_by="System"
        )
        db.add(timeline)
        db.commit()

        return execution

    def update_execution_step(
        self,
        db: Session,
        execution_id: int,
        step_index: int,
        status: str,
        step_note: str
    ) -> Optional[DBPlaybookExecution]:
        """Update checklist step state (e.g. check off, add comment)."""
        execution = db.query(DBPlaybookExecution).filter(DBPlaybookExecution.id == execution_id).first()
        if not execution:
            return None

        log = json.loads(execution.execution_log_json)
        if step_index < 0 or step_index >= len(log):
            return execution

        # Record changes
        log[step_index]["status"] = status
        log[step_index]["note"] = step_note
        if status == "Completed":
            log[step_index]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        else:
            log[step_index]["completed_at"] = None

        # Advance current step index automatically to next Pending step if current is checked
        if status == "Completed" and execution.current_step_index == step_index:
            next_idx = step_index + 1
            while next_idx < len(log) and log[next_idx]["status"] == "Completed":
                next_idx += 1
            execution.current_step_index = min(next_idx, len(log))

        # Check if all steps are completed
        all_done = all(item["status"] == "Completed" for item in log)
        if all_done:
            execution.status = "Completed"
            execution.completed_at = datetime.now(timezone.utc)
            
            # Log timeline event to case details
            timeline = DBTimelineEvent(
                investigation_id=execution.investigation_id,
                timestamp=datetime.now(timezone.utc).isoformat() + "Z",
                event="Playbook Completed",
                details=f"All steps completed on response playbook: '{execution.playbook_name}'",
                action_by="System"
            )
            db.add(timeline)
        else:
            execution.status = "Running"
            execution.completed_at = None

        execution.execution_log_json = json.dumps(log)
        db.commit()
        db.refresh(execution)
        return execution

    def update_execution_notes_and_evidence(
        self,
        db: Session,
        execution_id: int,
        notes: Optional[str] = None,
        evidence: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[DBPlaybookExecution]:
        """Update overall notes and append evidence indicators to the playbook execution run."""
        execution = db.query(DBPlaybookExecution).filter(DBPlaybookExecution.id == execution_id).first()
        if not execution:
            return None

        if notes is not None:
            execution.notes = notes
        if evidence is not None:
            execution.evidence_json = json.dumps(evidence)

        db.commit()
        db.refresh(execution)
        return execution
