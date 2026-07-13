"""SOAR Workflow Orchestration Engine."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast
from sqlalchemy.orm import Session

from app.models.workflow import DBWorkflow, DBWorkflowExecution
from app.models.database_models import DBTimelineEvent
from app.services.automation_engine import AutomationEngine


class WorkflowEngine:
    """Manages workflow configuration templates, automatic seeding, and active execution step-throughs."""

    DEFAULT_WORKFLOWS = [
        {
            "name": "Auto Isolate High Severity Host",
            "description": "Triggered on high severity incidents to alert the SOC, request approval, and isolate infected nodes.",
            "trigger_type": "Severity High",
            "steps": [
                {"type": "Action", "name": "Notify Slack", "parameter": "#security-ops"},
                {"type": "Approval", "name": "Require Manual SOC Approval to Isolate Host", "parameter": "workstation-01"},
                {"type": "Action", "name": "Isolate Host", "parameter": "workstation-01"},
                {"type": "Action", "name": "Block IP", "parameter": "198.51.100.42"}
            ]
        },
        {
            "name": "Credential Compromise Response",
            "description": "Automated playbook to disable compromised active directory users and email the CISO office.",
            "trigger_type": "Credential Spray",
            "steps": [
                {"type": "Action", "name": "Disable User", "parameter": "compromised_operator"},
                {"type": "Action", "name": "Notify Slack", "parameter": "#identity-alerts"},
                {"type": "Action", "name": "Send Email", "parameter": "CISO Incident Briefing"}
            ]
        },
        {
            "name": "Ransomware Subnet Containment",
            "description": "Critical response block to isolate file servers immediately upon detecting encrypted file systems.",
            "trigger_type": "Ransomware Detected",
            "steps": [
                {"type": "Action", "name": "Block IP", "parameter": "198.51.100.200"},
                {"type": "Approval", "name": "Require Multi-Step Approval to Isolate Storage Node", "parameter": "file-server-primary"},
                {"type": "Action", "name": "Isolate Host", "parameter": "file-server-primary"},
                {"type": "Action", "name": "Create Ticket", "parameter": "Jira Service Desk Escalation"}
            ]
        },
        {
            "name": "Web App Attack Block",
            "description": "Fast block mechanism to shield REST web portals when WAF logs flag SQL injections.",
            "trigger_type": "SQL Injection Alert",
            "steps": [
                {"type": "Action", "name": "Block IP", "parameter": "203.0.113.88"},
                {"type": "Action", "name": "Notify Teams", "parameter": "#web-ops-alerts"}
            ]
        }
    ]

    def seed_default_workflows(self, db: Session):
        """Seeds built-in default workflow templates if table is empty."""
        if db.query(DBWorkflow).count() == 0:
            for w in self.DEFAULT_WORKFLOWS:
                wf = DBWorkflow(
                    name=w["name"],
                    description=w["description"],
                    trigger_type=w["trigger_type"],
                    status="Enabled",
                    steps_json=json.dumps(w["steps"])
                )
                db.add(wf)
            db.commit()

    def get_workflows(self, db: Session) -> List[DBWorkflow]:
        """Fetch all workflow configurations."""
        self.seed_default_workflows(db)
        return db.query(DBWorkflow).all()

    def create_workflow(
        self,
        db: Session,
        name: str,
        description: str,
        trigger_type: str,
        steps: List[Dict[str, Any]]
    ) -> DBWorkflow:
        """Create a new custom workflow definition."""
        wf = DBWorkflow(
            name=name.strip(),
            description=description.strip(),
            trigger_type=trigger_type.strip(),
            status="Enabled",
            steps_json=json.dumps(steps)
        )
        db.add(wf)
        db.commit()
        db.refresh(wf)
        return wf

    def trigger_workflow_for_case(
        self,
        db: Session,
        case_id: str,
        severity: str,
        incident_type: str
    ) -> Optional[DBWorkflowExecution]:
        """Check if any enabled workflow triggers match the case severity/type and initiate execution."""
        self.seed_default_workflows(db)
        workflows = db.query(DBWorkflow).filter(DBWorkflow.status == "Enabled").all()
        
        matched_workflow = None
        
        # Match high severity trigger
        if severity.lower() == "high":
            matched_workflow = next((w for w in workflows if w.trigger_type == "Severity High"), None)
            
        # Match specific incident types if no severity matches
        if not matched_workflow:
            matched_workflow = next((w for w in workflows if w.trigger_type.lower() in incident_type.lower()), None)
            
        if not matched_workflow:
            return None

        steps = json.loads(cast(str, matched_workflow.steps_json))
        
        # Prepare execution log checklist structure
        execution_log = []
        for idx, step in enumerate(steps):
            execution_log.append({
                "index": idx,
                "type": step["type"],
                "name": step["name"],
                "parameter": step["parameter"],
                "status": "Pending",
                "completed_at": None,
                "detail": ""
            })

        execution = DBWorkflowExecution(
            workflow_id=matched_workflow.id,
            workflow_name=matched_workflow.name,
            started_at=datetime.now(timezone.utc),
            status="Running",
            current_step_index=0,
            execution_log_json=json.dumps(execution_log),
            linked_investigation_id=case_id,
            duration_seconds=0.0,
            result="Workflow triggered"
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        # Log timeline event to case details
        timeline = DBTimelineEvent(
            investigation_id=case_id,
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            event="SOAR Workflow Triggered",
            details=f"Triggered automated orchestration plan: '{matched_workflow.name}'",
            action_by="System"
        )
        db.add(timeline)
        db.commit()

        # Run starting steps
        return self._evaluate_execution(db, execution)

    def approve_workflow_step(self, db: Session, execution_id: int, approver_note: str) -> Optional[DBWorkflowExecution]:
        """Approve a suspended workflow execution and resume remaining actions."""
        execution = db.query(DBWorkflowExecution).filter(DBWorkflowExecution.id == execution_id).first()
        if not execution or execution.status != "Suspended":
            return execution

        exec_any = cast(Any, execution)
        log = json.loads(cast(str, exec_any.execution_log_json))
        idx = exec_any.current_step_index
        
        if idx >= len(log) or log[idx]["type"] != "Approval":
            return execution

        # Record manual approval complete
        log[idx]["status"] = "Completed"
        log[idx]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
        log[idx]["detail"] = f"Approved by SOC Analyst (Note: {approver_note})"
        
        exec_any.current_step_index = idx + 1
        exec_any.execution_log_json = json.dumps(log)
        exec_any.status = "Running"
        db.commit()

        # Log timeline event to case details
        if exec_any.linked_investigation_id:
            timeline = DBTimelineEvent(
                investigation_id=exec_any.linked_investigation_id,
                timestamp=datetime.now(timezone.utc).isoformat() + "Z",
                event="SOAR Action Approved",
                details=f"Manual approval granted for step '{log[idx]['name']}' ({approver_note})",
                action_by="System"
            )
            db.add(timeline)
            db.commit()

        # Resume evaluating remaining workflow steps
        return self._evaluate_execution(db, execution)

    def _evaluate_execution(self, db: Session, execution: DBWorkflowExecution) -> DBWorkflowExecution:
        """Run workflow steps sequentially until completed or suspended at an approval checkpoint."""
        exec_any = cast(Any, execution)
        log = json.loads(cast(str, exec_any.execution_log_json))
        start_time = exec_any.started_at
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        while exec_any.current_step_index < len(log):
            idx = exec_any.current_step_index
            step = log[idx]

            if step["type"] == "Approval":
                # Workflow suspends at approvals awaiting manual handler trigger
                exec_any.status = "Suspended"
                step["status"] = "Suspended"
                step["detail"] = "Suspended awaiting operator validation approval."
                exec_any.execution_log_json = json.dumps(log)
                db.commit()
                return execution

            # Execute action step
            res = AutomationEngine.execute_action(step["name"], step["parameter"])
            step["status"] = "Completed"
            step["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            step["detail"] = res["detail"]

            exec_any.current_step_index = idx + 1
            exec_any.execution_log_json = json.dumps(log)
            db.commit()

        # If loop completed all steps successfully
        exec_any.status = "Completed"
        exec_any.completed_at = datetime.now(timezone.utc)
        exec_any.result = f"Successfully completed all {len(log)} automated steps."
        
        now = datetime.now(timezone.utc)
        exec_any.duration_seconds = float((now - start_time).total_seconds())
        
        db.commit()

        # Log timeline event to case details
        if exec_any.linked_investigation_id:
            timeline = DBTimelineEvent(
                investigation_id=exec_any.linked_investigation_id,
                timestamp=datetime.now(timezone.utc).isoformat() + "Z",
                event="SOAR Workflow Completed",
                details=f"Orchestration workflow completed successfully.",
                action_by="System"
            )
            db.add(timeline)
            db.commit()

        return execution
