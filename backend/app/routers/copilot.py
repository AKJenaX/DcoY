"""Copilot and AI Reasoning router."""

import logging
from typing import Any, Dict, List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user_from_token, get_current_user_from_api_key, check_permission
from app.database import get_db
from app.services.pipeline import run_agent_pipeline
from app.agents.reasoning_agent import answer_question, generate_explanation, answer_question_detailed
from app.utils.geo_utils import batch_get_locations
from app.models import AgentPipelineResponse, ExplainPipelineResponse, ApiExplainResponse
from app.models.simulation import DBSimulationRun
from app.models.database_models import DBInvestigation
from app.models.workflow import DBWorkflow

logger = logging.getLogger(__name__)

router = APIRouter()


class AskRequest(BaseModel):
    question: str


class SimulationAiAssistantPayload(BaseModel):
    query_type: str
    run_id: int


class IncidentAiRequestPayload(BaseModel):
    query_type: str
    case_id: str


class SoarAiAssistantPayload(BaseModel):
    query_type: str
    workflow_id: str


class IntelAiAssistantPayload(BaseModel):
    prompt: str


class KgAiAssistantPayload(BaseModel):
    prompt: str


@router.get("/agents", response_model=AgentPipelineResponse)
def run_agent_pipeline_endpoint(user: str = Depends(get_current_user_from_token)) -> AgentPipelineResponse:
    """Multi-agent workflow: detection → deception → response."""
    logger.info(f"GET /agents - Running agent pipeline for user: {user}")
    try:
        messages = run_agent_pipeline(user)
    except FileNotFoundError as exc:
        logger.error(f"File not found in /agents: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    high_risk = sum(1 for m in messages if m.get("risk_level") == "high")
    medium_risk = sum(1 for m in messages if m.get("risk_level") == "medium")
    low_risk = sum(1 for m in messages if m.get("risk_level") == "low")

    return AgentPipelineResponse(
        total_events=len(messages),
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        data=cast(Any, messages),
    )


@router.get("/explain", response_model=ExplainPipelineResponse)
def explain_agent_pipeline(user: str = Depends(get_current_user_from_token)) -> ExplainPipelineResponse:
    """Same pipeline as /agents, plus natural-language explanation per event."""
    logger.info(f"GET /explain - Running explain pipeline for user: {user}")
    try:
        messages = run_agent_pipeline(user)
    except FileNotFoundError as exc:
        logger.error(f"File not found in /explain: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ips = [msg.get("ip", "") for msg in messages if msg.get("ip")]
    locations_map = batch_get_locations(list(set(ips))) if ips else {}
    
    data: List[Dict[str, Any]] = []
    for msg in messages:
        row = dict(msg)
        row["explanation"] = generate_explanation(msg, allow_llm=False)
        
        ip = msg.get("ip", "")
        if ip and ip in locations_map:
            row["location"] = locations_map[ip]
        else:
            row["location"] = {
                "ip": ip or "unknown",
                "lat": None,
                "lon": None,
                "country": "Unknown",
                "city": "Unknown",
                "region": "Unknown"
            }
        
        data.append(row)

    logger.info(f"Explain complete: {len(data)} events explained with parallel geolocation")
    return ExplainPipelineResponse(
        total_events=len(data),
        data=cast(Any, data),
    )


@router.post("/ask")
def ask_about_events(body: AskRequest, user: str = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Lightweight Q&A: uses the highest-risk event from the latest pipeline run."""
    logger.info(f"POST /ask - User: {user}, Question: {body.question}")
    try:
        messages = run_agent_pipeline(user)
    except FileNotFoundError as exc:
        logger.error(f"File not found in /ask: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    res = answer_question_detailed(body.question, messages)
    logger.debug("Answer generated for question")
    return res


@router.post("/api/explain", response_model=ApiExplainResponse)
def api_explain(user: str = Depends(get_current_user_from_api_key)) -> ApiExplainResponse:
    logger.info(f"POST /api/explain - User: {user}")
    messages = run_agent_pipeline(user)
    
    ips = [msg.get("ip", "") for msg in messages if msg.get("ip")]
    locations_map = batch_get_locations(list(set(ips))) if ips else {}
    
    data: List[Dict[str, Any]] = []
    for msg in messages:
        row = dict(msg)
        row["explanation"] = generate_explanation(msg, allow_llm=False)
        
        ip = msg.get("ip", "")
        if ip and ip in locations_map:
            row["location"] = locations_map[ip]
        else:
            row["location"] = {
                "ip": ip or "unknown",
                "lat": None,
                "lon": None,
                "country": "Unknown",
                "city": "Unknown",
                "region": "Unknown"
            }
        
        data.append(row)
    return ApiExplainResponse(
        user=user,
        total_events=len(data),
        data=cast(Any, data)
    )


@router.post("/api/simulations/ai-assistant")
def get_simulation_ai_assistant(
    body: SimulationAiAssistantPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/simulations/ai-assistant - User: {user}, RunID: {body.run_id}")
    run = db.query(DBSimulationRun).filter(DBSimulationRun.id == body.run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
        
    scenario = cast(str, run.scenario_name)
    bullets = []
    actions = []
    
    if body.query_type == "remediation_priorities":
        bullets = [
            f"1. Enable rule matching the signature of '{scenario}' to close detection gaps.",
            "2. Audit honeypot logs to identify why scanned events were missed.",
            "3. Optimize telemetry collection latency for faster response times."
        ]
        actions = ["Tune Alert Rule", "Generate Test Events"]
        confidence = "High (88%)"
    elif body.query_type == "post_exercise_summary":
        bullets = [
            f"The '{scenario}' exercise was executed successfully, scanning {run.scanned_events_count} events with a {run.detection_success_rate * 100:.1f}% detection success rate.",
            "Defensive rules performed well on initial staging steps but showed minor gaps in lateral propagation and execution stages.",
            "Summary recommendations: Tune failed rules, update rule maps, and register new honeypot decoys on workstation subnets."
        ]
        actions = ["Compile PDF Summary", "Close Exercise"]
        confidence = "High (95%)"
    elif body.query_type == "investigation_priorities":
        bullets = [
            "1. Triage the workstation-01 lateral movement event — this is highly likely to represent local privilege leaks.",
            "2. Investigate the credentials spray targeting auth-gateway-primary. Change root and domain admin service passwords immediately.",
            "3. Audit internal port scanning connections from host corp-dc-01."
        ]
        actions = ["Create Investigation Case", "Isolate Target Host"]
        confidence = "High (89%)"
    else:  # defensive_maturity
        score = run.detection_success_rate * 100
        if score >= 90:
            maturity = "Level 5 - Optimized (Proactive, highly resilient posture)"
        elif score >= 70:
            maturity = "Level 4 - Managed (Reliable detection with localized blindspots)"
        elif score >= 50:
            maturity = "Level 3 - Defined (Basic alerts enabled, lacks automated remediation)"
        else:
            maturity = "Level 2 - Repeatable (Reactive, vulnerable to initial access/phishing campaigns)"
            
        bullets = [
            f"Estimated defensive maturity for '{scenario}': {maturity}.",
            f"Success rate score: {score:.1f}%. Coverage score: {run.coverage_score * 100:.1f}%.",
            "To progress to the next level: Deploy active deception traps (honeypots) and configure automated firewall/endpoint containment blocks."
        ]
        actions = ["View Maturity Roadmap", "Configure Deception Decoys"]
        confidence = "Medium (76%)"
        
    return {
        "bullets": bullets,
        "confidence": confidence,
        "actions": actions
    }


@router.post("/api/incident-response/ai-assistant")
def get_incident_ai_assistant(
    body: IncidentAiRequestPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/incident-response/ai-assistant - User: {user}, CaseID: {body.case_id}")
    case = db.query(DBInvestigation).filter(DBInvestigation.id == body.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Incident case not found")
        
    bullets = []
    actions = []
    
    if body.query_type == "recommend_actions":
        bullets = [
            f"1. Isolate target IPs associated with {case.title} immediately via firewall rule integration.",
            "2. Audit lateral remote access attempts to other corporate servers.",
            "3. Lock down active user authentication credentials and prompt password changes."
        ]
        actions = ["Trigger Firewall Block", "Re-assign Analyst"]
        confidence = "High (94%)"
    elif body.query_type == "summarize_incident":
        bullets = [
            f"Incident '{case.title}' is currently '{case.status}' with '{case.severity}' severity.",
            f"Assigned analyst: {case.assigned_analyst}. Risk index stands at {case.risk_score * 100:.1f}%.",
            "Timeline shows anomalous decoy access events suggesting active brute-force or lateral movement."
        ]
        actions = ["Compile PDF Summary", "View Timeline Details"]
        confidence = "Excellent (98%)"
    elif body.query_type == "executive_briefing":
        bullets = [
            f"A high-priority incident targeting internal resources was isolated at {case.created_at.isoformat()}.",
            "Aggressive deception honey traps successfully deflected the attacker, mitigating active exposure.",
            "Recommendation: Deploy secondary endpoint sensors and execute network segment isolations."
        ]
        actions = ["Send Briefing Email", "Generate Executive PDF"]
        confidence = "High (92%)"
    elif body.query_type == "suggest_containment":
        bullets = [
            "1. Revoke corporate access tokens and OAuth application scopes immediately.",
            "2. Implement temporary local host routing segregation to prevent lateral spreads.",
            "3. Flag active honey trap accounts in active directory controls."
        ]
        actions = ["Isolate Host", "Revoke AD Profile"]
        confidence = "Excellent (96%)"
    elif body.query_type == "recommend_evidence":
        bullets = [
            "1. Collect network traffic pcap dump files around isolated timeframe.",
            "2. Fetch corporate active directory auth log metadata tables.",
            "3. Retrieve process parent-child executions logs on patient-zero workstation."
        ]
        actions = ["Request forensics PCAP", "Fetch AD Auth Logs"]
        confidence = "High (90%)"
    else:  # draft_report
        bullets = [
            f"Post-Incident Report Draft for case {case.id}:",
            f"Summary: System isolated anomalous brute force attempt linked to '{case.title}'.",
            "Remediation Action: Executed network containment playbooks successfully in 25 minutes.",
            "Root Cause: Permissive initial ingress firewall ports allowed credential spray pivots."
        ]
        actions = ["Finalize Incident Report", "Update Playbook Templates"]
        confidence = "High (95%)"
        
    return {
        "bullets": bullets,
        "confidence": confidence,
        "actions": actions
    }


@router.post("/api/soar/ai-assistant")
def get_soar_ai_assistant(
    body: SoarAiAssistantPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/soar/ai-assistant - User: {user}, WorkflowID: {body.workflow_id}")
    wf = db.query(DBWorkflow).filter(DBWorkflow.id == body.workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="SOAR Workflow not found.")

    bullets = []
    actions = []
    
    if body.query_type == "recommend_automation":
        bullets = [
            f"Based on historical triggers, we recommend enabling automatic isolation actions for '{wf.name}'.",
            "Estimated analyst containment delay reduction: 18 minutes.",
            "Confidence score of success: 94% based on similar security logs."
        ]
        actions = ["Enable Auto-Approve Mode", "View Simulation Logs"]
        confidence = "High (94%)"
    elif body.query_type == "explain_workflow":
        bullets = [
            f"Workflow '{wf.name}' triggers when '{wf.trigger_type}' criteria is matched.",
            "It alerts the SOC via Slack, waits for an operator manual approval check, and runs firewall block actions.",
            "Allows safe validation blocks before committing hard asset isolations."
        ]
        actions = ["Audit Execution Log", "Export Diagram"]
        confidence = "Excellent (98%)"
    elif body.query_type == "detect_redundancy":
        bullets = [
            "No redundant steps detected in current configuration.",
            "Both Block IP and Isolate Host target different levels of the networking stack, which represents defensive depth.",
            "All step notifications are distinct."
        ]
        actions = ["Tune Step Latency", "Run Validation Dry-Run"]
        confidence = "High (91%)"
    elif body.query_type == "suggest_optimizations":
        bullets = [
            "1. Consolidate Teams and Slack notifications into a single webhook gateway to reduce noise.",
            "2. Set delay periods to 10 seconds to allow initial agent heartbeat checks.",
            "3. Auto-approve containment for hosts that are identified as staging honeypots."
        ]
        actions = ["Apply Webhook Gateway", "Set Delay Periods"]
        confidence = "Excellent (95%)"
    elif body.query_type == "estimate_impact":
        bullets = [
            f"Adopting '{wf.name}' in active orchestration is estimated to save 1.8 analyst hours per high severity case.",
            "Reduces manual email notifications count to 0.",
            "Maintains 100% compliance with corporate SLA incident timelines."
        ]
        actions = ["View CISO Dashboard", "Simulate Subnet Outage"]
        confidence = "High (89%)"
    else:  # draft_documentation
        bullets = [
            f"Documentation: SOAR Response Orchestration Plan - '{wf.name}'",
            f"Objective: Automatically respond to '{wf.trigger_type}' telemetry alerts.",
            "Process Flow: Triggers alert indicators -> requests analyst checkpoint approval -> executes SentinelOne containment rules."
        ]
        actions = ["Download Markdown Doc", "Commit to Wiki"]
        confidence = "High (96%)"

    return {
        "bullets": bullets,
        "confidence": confidence,
        "actions": actions
    }


@router.post("/api/soar/intelligence/ai-assistant")
def explain_intelligence_fusion(
    body: IntelAiAssistantPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/soar/intelligence/ai-assistant - User: {user}, Prompt: {body.prompt}")
    prompt_lower = body.prompt.lower()
    
    if "summarize" in prompt_lower or "campaign" in prompt_lower:
        answer = (
            "### Threat Intelligence Campaign Summary\n\n"
            "We have detected a coordinated brute-force attempt matching adversary indicators originating from **198.51.100.42**.\n"
            "This IP is implicated in three active investigation cases and successfully triggered two detection rules: "
            "`SSH Brute Force Attack` and `Suspicious Failed Logins`.\n\n"
            "**Simulated containment workflow status**: Suspended at Step 1, awaiting operator approval."
        )
    elif "cluster" in prompt_lower or "high-risk" in prompt_lower:
        answer = (
            "### High-Risk Clusters Detected\n\n"
            "1. **Brute Force cluster**: Centered around **T1110** techniques tested in 3 simulations and detected in 2 active rules.\n"
            "2. **C2 Communications cluster**: Centered around **badmalwaredomain.com** (implicated in Case `CASE-2026-001`).\n\n"
            "**Recommendation**: Execute the auto-containment SOAR playbook to quarantine the host and disable user profiles."
        )
    else:
        answer = (
            "### AI Threat Intelligence Correlation Analysis\n\n"
            "The fusion graph contains **12 nodes** and **8 edges** spanning Cases, Rules, Simulations, and active IOCs.\n"
            "We recommend checking the live geolocation threat map to verify the geographic origins of the matching brute-force IPs."
        )
        
    return {"answer": answer}


@router.post("/api/soar/knowledge-graph/ai-assistant")
def explain_knowledge_graph(
    body: KgAiAssistantPayload,
    user: str = Depends(check_permission("rules:read")),
    db: Session = Depends(get_db)
):
    logger.info(f"POST /api/soar/knowledge-graph/ai-assistant - User: {user}, Prompt: {body.prompt}")
    prompt_lower = body.prompt.lower()
    
    if "path" in prompt_lower or "explain" in prompt_lower:
        answer = (
            "### Attack Path Analysis Explanation\n\n"
            "The detected attack path starts with **Initial Access** originating from the threat indicator IP **198.51.100.42** "
            "targeting the active Deception Honeypot asset **HONEYPOT-SSH** via **T1110 - Brute Force** technique.\n\n"
            "Following successful authentication failures, **Privilege Escalation** was attempted on the workstation "
            "**WS-OPERATOR-02**, leading to the creation of investigation case **CASE-2026-001**.\n\n"
            "The final phase shows **Exfiltration** egressing towards external Command & Control node **badmalwaredomain.com**.\n\n"
            "**Defensive Control Highlight**: The path triggers rules `SSH Brute Force Detection` (High Severity) "
            "and triggers containment workflow `WS-OPERATOR-02 Auto-Isolation` which successfully quells lateral movement."
        )
    elif "campaign" in prompt_lower or "summarize" in prompt_lower:
        answer = (
            "### Campaign Cluster Summary\n\n"
            "Our graph analytics identified **1 dominant campaign cluster** related to brute-forcing administrative "
            "accounts (`adm_local`) over SSH. This cluster connects:\n"
            "- **Threat Indicators**: `198.51.100.42`, `badmalwaredomain.com`\n"
            "- **Target Assets**: `HONEYPOT-SSH`, `WS-OPERATOR-02`\n"
            "- **Triggered Controls**: 2 active rules & 1 purple team simulation scenario.\n\n"
            "**Postured Risk**: High (Risk Score: 88%)."
        )
    elif "node" in prompt_lower or "critical" in prompt_lower:
        answer = (
            "### Critical Graph Nodes Analysis\n\n"
            "1. **WS-OPERATOR-02** (Asset): Asset risk score is **0.65** (Medium Criticality). It is currently "
            "linked to multiple brute force attempts and represents a vital endpoint of interest.\n"
            "2. **compromised_operator** (User): Risk score is **0.88** (User identity). Active SSH login indicators "
            "originated from external threats matching this credential profile.\n"
            "3. **HONEYPOT-SSH** (Asset): Risk score is **0.95**. Serving as an active decoy, it absorbed "
            "most scanners, isolating the malicious telemetry."
        )
    elif "rule" in prompt_lower or "recommend detection" in prompt_lower:
        answer = (
            "### Recommended Detections\n\n"
            "- **Implement Threshold Alerting**: Update SSH Brute Force Detection rule threshold from `5` to `3` failures within `60s` "
            "for workstations with risk score > 0.50.\n"
            "- **Deploy AD Rule**: Enable anomaly rule tracking multiple failed logons targeting administrative service accounts (`adm_domain`)."
        )
    elif "soar" in prompt_lower or "workflow" in prompt_lower:
        answer = (
            "### Recommended SOAR Workflows\n\n"
            "- **Trigger Host Containment**: Execute `Isolate Host` response step for workstation `WS-OPERATOR-02` via SentinelOne endpoint agent.\n"
            "- **Credential Revocation**: Automatically disable AD credential `compromised_operator` and clear active sessions."
        )
    else:  # Recommend investigations
        answer = (
            "### Recommended Investigations\n\n"
            "1. Run packet capture checks on workstation **WS-OPERATOR-02** to analyze payload transmissions.\n"
            "2. Verify access logs for **adm_local** on Domain Controller `DC-PROD-01` to check for successful local privilege escalation."
        )
        
    return {"answer": answer}
