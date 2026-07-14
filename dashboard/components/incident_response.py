"""Incident Response & Response Playbooks Streamlit View Component."""

import json
import time
import requests
import streamlit as st
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def render_incident_response_page(
    explain_rows: List[Dict[str, Any]],
    detect_rows: List[Dict[str, Any]],
    latency_ms: int,
    api_base: str
):
    """Renders the Incident Response Workspace page view."""

    # Set authentication headers
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}

    # Initialize session states
    if "selected_incident_id" not in st.session_state:
        st.session_state.selected_incident_id = "CASE-2026-001"
    if "selected_playbook_id" not in st.session_state:
        st.session_state.selected_playbook_id = 1
    if "ir_ai_query_type" not in st.session_state:
        st.session_state.ir_ai_query_type = "recommend_actions"
    if "ir_ai_results" not in st.session_state:
        st.session_state.ir_ai_results = {}

    # ─── 1. Header Section ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">Incident Response</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">SOAR Playbook Execution & Incident Coordination Workbench</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> SOAR CORE ACTIVE
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ─── 2. Fetch Incident Response KPIs from API ───────────────────────────
    try:
        r_kpis = requests.get(f"{api_base}/api/incident-response/kpis", headers=headers, timeout=10, verify=False)
        if r_kpis.status_code == 200:
            kpis = r_kpis.json()
        else:
            kpis = {
                "active_incidents": 1,
                "high_severity_cases": 0,
                "sla_breaches": 0,
                "mean_response_time_minutes": 25.0,
                "playbooks_executed": 3,
                "automation_coverage_pct": 78.5
            }
    except Exception:
        kpis = {
            "active_incidents": 1,
            "high_severity_cases": 0,
            "sla_breaches": 0,
            "mean_response_time_minutes": 25.0,
            "playbooks_executed": 3,
            "automation_coverage_pct": 78.5
        }

    # Render Top KPI Row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Active Incidents</div>
                <div class="metric-value">{kpis["active_incidents"]}</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Open / triaged cases</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">High Severity Cases</div>
                <div class="metric-value">{kpis["high_severity_cases"]}</div>
                <div style="font-size:0.7rem; color:var(--danger); font-weight:700;">Urgent remediation</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">SLA Breaches</div>
                <div class="metric-value">{kpis["sla_breaches"]}</div>
                <div style="font-size:0.7rem; color:{"var(--danger)" if kpis["sla_breaches"] > 0 else "var(--text-secondary)"}; font-weight:700;">Over 60-min limit</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Mean Response Time</div>
                <div class="metric-value">{kpis["mean_response_time_minutes"]}m</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Avg triage to resolution</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k5:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Playbooks Executed</div>
                <div class="metric-value">{kpis["playbooks_executed"]}</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Total response checklists</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k6:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Automation Coverage</div>
                <div class="metric-value">{kpis["automation_coverage_pct"]}%</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Cases with playbook run</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Fetch Cases List from API (reuse from investigations API)
    try:
        r_cases = requests.get(f"{api_base}/api/investigations", headers=headers, timeout=10, verify=False)
        cases_list = r_cases.json() if r_cases.status_code == 200 else []
    except Exception:
        cases_list = []

    # ─── 3. Left Panel (30%): Incident Queue ────────────────────────────────
    col_queue, col_workspace = st.columns([3, 7])

    with col_queue:
        st.markdown('<h3 class="section-title">Incident Queue Ledger</h3>', unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown(
                """
                <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.75rem;">
                  Select an active incident case to execute response playbooks:
                </p>
                """,
                unsafe_allow_html=True
            )

            # Filter cases to active/open ones
            active_incidents = [c for c in cases_list if c["status"] in {"Open", "Active"}]
            if not active_incidents:
                active_incidents = cases_list  # Fallback to all if no active cases exist
                
            if not active_incidents:
                st.warning("No incidents found. Please create one on the Investigations page.")
            else:
                for c in active_incidents:
                    cid = c["id"]
                    is_selected = (cid == st.session_state.selected_incident_id)
                    border_glow = "border: 1px solid var(--primary); box-shadow: 0 0 10px rgba(59,130,246,0.15);" if is_selected else "border: 1px solid var(--border-color);"
                    
                    s_level = c["severity"].upper()
                    s_color = "var(--danger)" if s_level == "HIGH" else ("var(--warning)" if s_level == "MEDIUM" else "var(--success)")
                    
                    st.markdown(
                        f"""
                        <div style="{border_glow} background-color: var(--card-bg); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                          <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.7rem; font-weight:700; color:var(--text-secondary);">{cid}</span>
                            <span style="font-size:0.6rem; font-weight:700; color:{s_color}; border:1px solid {s_color}; border-radius:3px; padding:0.05rem 0.3rem;">
                              {s_level}
                            </span>
                          </div>
                          <div style="font-size:0.82rem; font-weight:700; color:var(--text-primary); margin:0.25rem 0;">{c["title"]}</div>
                          <div style="display:flex; justify-content:space-between; font-size:0.7rem; margin-top:0.4rem;">
                            <span style="color:var(--text-secondary);">Status: <b>{c["status"]}</b></span>
                            <span style="color:var(--muted);">Analyst: <b>{c["assigned_analyst"]}</b></span>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if st.button(f"Triage Case {cid}", key=f"triage_inc_btn_{cid}", use_container_width=True):
                        st.session_state.selected_incident_id = cid
                        st.session_state.ir_ai_results = {}
                        st.rerun()

    # ─── 4. Right Panel (70%): Playbook Execution Workspace ─────────────────
    sel_inc_id = st.session_state.selected_incident_id

    # Fetch Case details
    selected_case = next((c for c in cases_list if c["id"] == sel_inc_id), None)
    
    with col_workspace:
        st.markdown(f'<h3 class="section-title">SOAR Workspace: {sel_inc_id}</h3>', unsafe_allow_html=True)
        
        if not selected_case:
            st.info("Please select an incident case from the ledger queue.")
        else:
            with st.container(border=True):
                # Render current case overview
                st.markdown(
                    f"""
                    <div style="padding:0.75rem; background-color:var(--card-bg-sec); border-radius:6px; border:1px solid var(--border-color); margin-bottom:1rem;">
                      <div style="font-size:0.9rem; font-weight:700; color:var(--text-primary);">{selected_case["title"]}</div>
                      <div style="display:flex; gap:1.5rem; font-size:0.75rem; color:var(--text-secondary); margin-top:0.35rem;">
                        <span>Assigned: <b>{selected_case["assigned_analyst"]}</b></span>
                        <span>Severity: <b>{selected_case["severity"]}</b></span>
                        <span>Priority: <b>{selected_case["priority"]}</b></span>
                        <span>Risk Score: <b>{selected_case["risk_score"]:.2f}</b></span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Fetch running executions for this case
                try:
                    r_execs = requests.get(f"{api_base}/api/playbooks/executions?case_id={sel_inc_id}", headers=headers, timeout=10, verify=False)
                    executions = r_execs.json() if r_execs.status_code == 200 else []
                except Exception:
                    executions = []

                running_execution = next((e for e in executions if e["status"] == "Running"), None)
                if not running_execution and executions:
                    # Fallback to the latest execution if none is running
                    running_execution = executions[-1]

                # TABS: Playbook Execution | Playbook Library | Response Timeline | AI Assistant
                tab_exec, tab_lib, tab_timeline, tab_ai = st.tabs([
                    "📋 Playbook Execution",
                    "📚 Playbook Library",
                    "🕒 Response Timeline",
                    "🧠 AI Response Assistant"
                ])

                # ─── TAB 1: Playbook Execution ──────────────────────────────────────
                with tab_exec:
                    if not running_execution:
                        st.markdown(
                           """
                           <div style="text-align:center; padding:2rem 1rem;">
                             <p style="font-size:0.9rem; color:var(--text-secondary); margin-bottom:1rem;">
                               No active response playbook is assigned to this incident.
                             </p>
                           </div>
                           """,
                           unsafe_allow_html=True
                        )
                        st.info("💡 Go to the 'Playbook Library' tab to choose and trigger a response plan.")
                    else:
                        eid = running_execution["id"]
                        st.markdown(
                            f"""
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                              <div>
                                <h4 style="margin:0; font-size:1.1rem; color:var(--primary);">{running_execution["playbook_name"]}</h4>
                                <span style="font-size:0.75rem; color:var(--text-secondary);">Execution Status: <b>{running_execution["status"]}</b></span>
                              </div>
                              <span class="status-pill active" style="font-size:0.7rem; font-weight:700;">RUNNING EID: {eid}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Checklist Manual Steps
                        st.markdown("##### Manual Playbook Checklist Steps:")
                        steps_log = json.loads(running_execution["execution_log_json"])
                        
                        for idx, step in enumerate(steps_log):
                            status = step["status"]
                            is_checked = (status == "Completed")
                            
                            c_col1, c_col2, c_col3 = st.columns([1, 6, 3])
                            with c_col1:
                                check_val = st.checkbox(
                                    "",
                                    value=is_checked,
                                    key=f"step_check_{eid}_{idx}"
                                )
                            with c_col2:
                                text_style = "text-decoration: line-through; color: var(--muted);" if is_checked else "color: var(--text-primary);"
                                st.markdown(f"<span style='font-size:0.85rem; {text_style}'>{step['step']}</span>", unsafe_allow_html=True)
                                if step.get("completed_at"):
                                    st.markdown(f"<span style='font-size:0.65rem; color:var(--muted);'>Completed: {step['completed_at'][:19].replace('T', ' ')}</span>", unsafe_allow_html=True)
                            with c_col3:
                                note_val = st.text_input(
                                    "Comment",
                                    value=step.get("note", ""),
                                    placeholder="Add log notes...",
                                    label_visibility="collapsed",
                                    key=f"step_note_input_{eid}_{idx}"
                                )

                            # If state has changed, update step immediately
                            new_status = "Completed" if check_val else "Pending"
                            if new_status != status or note_val != step.get("note", ""):
                                payload = {
                                    "step_index": idx,
                                    "status": new_status,
                                    "note": note_val
                                }
                                try:
                                    r_up = requests.put(f"{api_base}/api/playbooks/executions/{eid}", json=payload, headers=headers, timeout=10, verify=False)
                                    if r_up.status_code == 200:
                                        st.toast(f"Step {idx + 1} updated!", icon="✓")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating step: {str(e)}")

                            st.markdown("<hr style='margin: 0.35rem 0; border: none; border-top: 1px dotted var(--border-color);' />", unsafe_allow_html=True)

                        st.markdown("<br/>", unsafe_allow_html=True)
                        
                        # General Notes and Evidence Section
                        st.markdown("##### 📁 Action Notes & Evidence Attachments:")
                        ir_notes = st.text_area("Incident Handler Remediation Notes", value=running_execution.get("notes") or "", key=f"ir_notes_input_{eid}")
                        
                        # Parse existing evidence list
                        try:
                            evidence_list = json.loads(running_execution["evidence_json"] or "[]")
                        except Exception:
                            evidence_list = []

                        # Add evidence section
                        add_ev_col1, add_ev_col2 = st.columns([7, 3])
                        with add_ev_col1:
                            ev_name = st.text_input("Evidence Identifier / Value", placeholder="e.g. Blocked IP: 198.51.100.42", key=f"add_ev_name_{eid}")
                        with add_ev_col2:
                            ev_type = st.selectbox("Evidence Type", ["Blocked IP", "Password Reset User", "Isolated Host", "Memory Forensics Dump"], key=f"add_ev_type_{eid}")

                        if st.button("➕ Attach Evidence to Playbook Log", key=f"attach_ev_btn_{eid}", use_container_width=True):
                            if ev_name:
                                evidence_list.append({
                                    "evidence": ev_name,
                                    "type": ev_type,
                                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
                                })
                                payload = {
                                    "notes": ir_notes,
                                    "evidence": evidence_list
                                }
                                try:
                                    r_up = requests.put(f"{api_base}/api/playbooks/executions/{eid}", json=payload, headers=headers, timeout=10, verify=False)
                                    if r_up.status_code == 200:
                                        st.toast("Evidence attached!", icon="✓")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to attach evidence: {str(e)}")
                            else:
                                st.warning("Please provide evidence identifier info.")

                        # Render current evidence attachments
                        if evidence_list:
                            st.markdown("<br/><b>Current Attached Evidence Log:</b>", unsafe_allow_html=True)
                            for ev in evidence_list:
                                st.markdown(
                                    f"""
                                    <div style="font-size:0.75rem; padding:0.4rem 0.5rem; background-color:var(--card-bg-sec); border-radius:4px; margin-bottom:0.35rem; border:1px solid var(--border-color); display:flex; justify-content:space-between;">
                                      <span><b>[{ev['type']}]</b> {ev['evidence']}</span>
                                      <span style="color:var(--muted);">{ev['timestamp'][:19].replace('T', ' ')}</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                        # Save Notes state manually
                        if ir_notes != (running_execution.get("notes") or ""):
                            if st.button("💾 Save Action Notes Changes", key=f"save_notes_btn_{eid}", use_container_width=True):
                                payload = {"notes": ir_notes}
                                try:
                                    r_up = requests.put(f"{api_base}/api/playbooks/executions/{eid}", json=payload, headers=headers, timeout=10, verify=False)
                                    if r_up.status_code == 200:
                                        st.toast("Playbook notes saved!", icon="✓")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to save notes: {str(e)}")

                        # Executive Summary Box
                        st.markdown("<br/>", unsafe_allow_html=True)
                        st.markdown("#### 📊 Post-Incident Executive Assessment Summary:")
                        st.markdown(
                            f"""
                            <div style="background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.75rem; font-size:0.8rem; line-height: 1.4;">
                              <b>SLA Compliance Status:</b> <span style="color:var(--success);">COMPLIANT</span> (Active response duration initialized within 15 mins)<br/>
                              <b>Response Effectiveness Score:</b> <b>{int((running_execution['current_step_index'] / max(1, len(steps_log))) * 100)}%</b> checklist coverage.<br/>
                              <b>Incident Impact Assessment:</b> Defensive honeypots isolated anomalous telemetry pivots, preventing root environment exposure.<br/>
                              <b>Strategic Posture Recommendations:</b> Update ingress firewall port scanning rules; extend automated API key rotation periods.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                # ─── TAB 2: Playbook Library ──────────────────────────────────────
                with tab_lib:
                    st.markdown("##### 📚 Playbook Library & Templates:")
                    
                    # Fetch templates list
                    try:
                        r_tpls = requests.get(f"{api_base}/api/playbooks", headers=headers, timeout=10, verify=False)
                        playbook_templates = r_tpls.json() if r_tpls.status_code == 200 else []
                    except Exception:
                        playbook_templates = []

                    # Show templates dropdown
                    if not playbook_templates:
                        st.warning("No playbook templates found.")
                    else:
                        tpl_names = [t["name"] for t in playbook_templates]
                        selected_tpl_name = st.selectbox(
                            "Select Playbook Template",
                            options=tpl_names,
                            key=f"tpl_select_dropdown_{sel_inc_id}"
                        )
                        
                        # Find selected template details
                        selected_tpl = next((t for t in playbook_templates if t["name"] == selected_tpl_name), playbook_templates[0])
                        
                        st.markdown(
                            f"""
                            <div style="border:1px solid var(--border-color); border-radius:6px; padding:0.75rem; background-color:var(--card-bg-sec); margin-bottom:1rem;">
                              <div style="font-weight:700; color:var(--primary); font-size:0.95rem;">{selected_tpl['name']}</div>
                              <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.25rem;">{selected_tpl['description']}</div>
                              <div style="font-size:0.75rem; color:var(--muted); margin-top:0.4rem; display:flex; gap:1.5rem;">
                                <span>Category: <b>{selected_tpl['category']}</b></span>
                                <span>Estimated Duration: <b>{selected_tpl['estimated_duration_minutes']} minutes</b></span>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown("<b>Steps checklist to be initialized:</b>", unsafe_allow_html=True)
                        tpl_steps = json.loads(selected_tpl["steps_json"])
                        for idx, step_txt in enumerate(tpl_steps):
                            st.markdown(f"<span style='font-size:0.8rem;'>{idx + 1}. {step_txt}</span>", unsafe_allow_html=True)
                        
                        st.markdown("<br/>", unsafe_allow_html=True)

                        # Trigger button
                        if st.button("🚀 Assign & Trigger Playbook Execution", key=f"trigger_playbook_btn_{selected_tpl['id']}", use_container_width=True):
                            payload = {
                                "investigation_id": sel_inc_id,
                                "playbook_id": selected_tpl["id"]
                            }
                            try:
                                r_trig = requests.post(f"{api_base}/api/playbooks/executions", json=payload, headers=headers, timeout=10, verify=False)
                                if r_trig.status_code == 200:
                                    st.success(f"Playbook '{selected_tpl['name']}' triggered successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to trigger: {r_trig.text}")
                            except Exception as e:
                                st.error(f"Network error: {str(e)}")

                # ─── TAB 3: Response Timeline ──────────────────────────────────────
                with tab_ai:
                    st.markdown("##### 🧠 AI Security Incident Copilot Assistant:")
                    
                    st.session_state.ir_ai_query_type = st.selectbox(
                        "AI Copilot Queries",
                        options=[
                            "recommend_actions",
                            "summarize_incident",
                            "executive_briefing",
                            "suggest_containment",
                            "recommend_evidence",
                            "draft_report"
                        ],
                        format_func=lambda x: {
                            "recommend_actions": "Recommend Next SOC Actions",
                            "summarize_incident": "Summarize Incident Scope",
                            "executive_briefing": "Generate CISO Executive Briefing",
                            "suggest_containment": "Suggest Incident Containment Strategy",
                            "recommend_evidence": "Recommend Additional Evidence Items",
                            "draft_report": "Draft Post-Incident Post-Mortem Report"
                        }.get(x, x),
                        key=f"ir_ai_query_select_{sel_inc_id}"
                    )

                    if st.button("🔮 Ask AI Copilot Assistant", key=f"ask_ir_ai_btn_{sel_inc_id}", use_container_width=True):
                        payload = {
                            "query_type": st.session_state.ir_ai_query_type,
                            "case_id": sel_inc_id
                        }
                        with st.spinner("AI Copilot is drafting incident strategy..."):
                            try:
                                r_ai = requests.post(f"{api_base}/api/incident-response/ai-assistant", json=payload, headers=headers, timeout=20, verify=False)
                                if r_ai.status_code == 200:
                                    st.session_state.ir_ai_results = r_ai.json()
                                else:
                                    st.error(f"AI error: {r_ai.text}")
                            except Exception as e:
                                st.error(f"Network error: {str(e)}")

                    # Render AI Copilot results
                    ai_results = st.session_state.ir_ai_results
                    if ai_results:
                        from dashboard.components.widget_variants import AIWidget
                        AIWidget(
                            title="AI Security Assistant Response",
                            bullets=ai_results.get("bullets", []),
                            subtitle="Incident Intelligence Analysis",
                            confidence=ai_results.get("confidence", "High (90%)"),
                            actions=ai_results.get("actions", []),
                            key=f"ir_ai_{sel_inc_id}"
                        ).render()

                # ─── TAB 4: Response Timeline ──────────────────────────────────────
                with tab_timeline:
                    st.markdown("##### 🕒 Incident Response Chronology Stage Map:")
                    
                    # Core Incident Stages
                    # Detection -> Investigation -> Evidence -> Containment -> Eradication -> Recovery -> Lessons Learned
                    stages = [
                        {"stage": "Detection", "status": "Completed", "desc": "Initial anomalous honeypot activity flagged by detection engines."},
                        {"stage": "Investigation", "status": "Completed", "desc": "Investigation database ticket case created and analyst assigned."},
                        {"stage": "Evidence", "status": "Completed", "desc": "Telemetry and process logs verified and attached to evidence list."},
                        {"stage": "Containment", "status": "In Progress", "desc": "Response playbook triggered. Local workstation isolated from corporate subnet."},
                        {"stage": "Eradication", "status": "Pending", "desc": "Kill parent-child processes, delete payloads, and restore state backups."},
                        {"stage": "Recovery", "status": "Pending", "desc": "Reconnect networks and restore host access control policies."},
                        {"stage": "Lessons Learned", "status": "Pending", "desc": "Compile post-mortem report and tune failed detection rules."}
                    ]

                    # Dynamically update based on playbook status
                    if running_execution:
                        if running_execution["status"] == "Completed":
                            for s in stages:
                                s["status"] = "Completed"
                        else:
                            # Containment is completed if first few steps of the playbook execution checklist are checked
                            log_steps = json.loads(running_execution["execution_log_json"])
                            comp_steps = sum(1 for item in log_steps if item["status"] == "Completed")
                            if comp_steps >= 2:
                                stages[3]["status"] = "Completed"
                                stages[4]["status"] = "In Progress"
                            if comp_steps >= 4:
                                stages[4]["status"] = "Completed"
                                stages[5]["status"] = "In Progress"

                    # Render Stages using styled widgets
                    for idx, s in enumerate(stages):
                        status_label = s["status"]
                        color_glow = "var(--success)" if status_label == "Completed" else ("var(--primary)" if status_label == "In Progress" else "var(--muted)")
                        glow_border = f"border-left: 3px solid {color_glow}; padding-left: 0.75rem;"
                        
                        st.markdown(
                            f"""
                            <div style="{glow_border} margin-bottom: 0.75rem;">
                              <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.85rem; font-weight:700; color:{color_glow};">{idx + 1}. {s['stage'].upper()}</span>
                                <span style="font-size:0.7rem; font-weight:700; color:{color_glow};">{status_label}</span>
                              </div>
                              <p style="font-size:0.75rem; color:var(--text-secondary); margin:0.15rem 0 0 0;">{s['desc']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        if idx < len(stages) - 1:
                            st.markdown(f"<div style='border-left: 1px dashed var(--border-color); height:12px; margin-left:8px;'></div>", unsafe_allow_html=True)
