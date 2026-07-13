"""Purple Team & Attack Simulation Workspace component."""

import json
import time
import requests
import streamlit as st
from typing import Any, Dict, List
from dashboard.components.widget_variants import (
    KPIWidget,
    TimelineWidget,
    AIWidget,
    TableWidget,
    ThreatWidget,
    StatusWidget,
    render_kpi_widget
)


def render_attack_simulation_page(api_base: str) -> None:
    """Renders the Purple Team simulation center with execution controls, timeline, and AI analysis."""

    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
          <h1 style="margin: 0; font-size: 1.85rem; font-weight: 700; color: var(--text-primary);">🛡️ Purple Team & Attack Simulation</h1>
          <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; color: var(--text-secondary);">
            Validate defensive controls and signature coverage using synthetic adversary emulation campaigns.
          </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}

    # ─── 1. Load KPI statistics ──────────────────────────────────────────────
    kpis = {
        "scenarios_executed": 0,
        "detection_success_rate": 0.0,
        "missed_detections": 0,
        "coverage_score": 0.0,
        "average_detection_time": 0.0,
        "simulation_confidence": 0.0
    }
    
    try:
        r_kpis = requests.get(f"{api_base}/api/simulations/kpis", headers=headers, timeout=5, verify=False)
        if r_kpis.status_code == 200:
            kpis = r_kpis.json()
    except Exception:
        pass

    # ─── 2. Top KPI Cards Row ────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    with k1:
        KPIWidget(
            title="Emulations Run",
            value=str(kpis["scenarios_executed"]),
            subtitle="Scenarios Executed",
            accent="blue"
        ).render()
    with k2:
        KPIWidget(
            title="Success Rate",
            value=f"{kpis['detection_success_rate'] * 100:.1f}%",
            subtitle="Detection Success Rate",
            accent="green" if kpis['detection_success_rate'] >= 0.8 else "orange"
        ).render()
    with k3:
        KPIWidget(
            title="Missed Alerts",
            value=str(kpis["missed_detections"]),
            subtitle="Missed Detections",
            accent="red" if kpis["missed_detections"] > 0 else "blue"
        ).render()
    with k4:
        KPIWidget(
            title="MITRE Coverage",
            value=f"{kpis['coverage_score'] * 100:.1f}%",
            subtitle="Coverage Score",
            accent="blue"
        ).render()
    with k5:
        KPIWidget(
            title="Avg Latency",
            value=f"{kpis['average_detection_time']:.1f}s",
            subtitle="Average Detection Time",
            accent="blue"
        ).render()
    with k6:
        KPIWidget(
            title="Confidence",
            value=f"{kpis['simulation_confidence'] * 100:.0f}%",
            subtitle="Simulation Confidence",
            accent="green" if kpis['simulation_confidence'] >= 0.8 else "orange"
        ).render()

    st.markdown("<br/>", unsafe_allow_html=True)

    # ─── 3. Main Interface Splits ───────────────────────────────────────────
    col_left, col_right = st.columns([4, 6])

    # ─── Left Column: Control Panel and Scenarios ───────────────────────────
    with col_left:
        st.markdown("### 🗃️ Emulation Scenario Library")
        
        scenario_list = [
            "Phishing", "Password Spraying", "SSH Brute Force", 
            "Port Scan", "Privilege Escalation", "Lateral Movement", 
            "Beaconing", "Suspicious PowerShell", "Data Exfiltration", 
            "Ransomware", "Custom Scenario"
        ]
        
        selected_scenario = st.selectbox("Select Target Adversary Scenario", options=scenario_list)
        
        with st.container(border=True):
            st.markdown("⚙️ **Simulation Parameters**")
            
            # Setup custom parameters config
            c_ip = st.text_input("Source IP Address Override", value="192.168.4.99")
            c_host = st.text_input("Target Hostname Override", value="corp-dc-01")
            c_user = st.text_input("Target Username Override", value="adm_local")
            
            st.markdown(
                """
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-bottom:0.75rem;">
                  ℹ️ This simulator generates <b>synthetic telemetry only</b>. No actual attacks or scripts are run on this host.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if st.button("🚀 Execute Emulation Campaign", use_container_width=True, type="primary"):
                payload = {
                    "scenario_name": selected_scenario,
                    "custom_params": {
                        "src_ip": c_ip,
                        "host": c_host,
                        "user": c_user
                    }
                }
                
                with st.spinner("Emulating adversary activity..."):
                    try:
                        r_trig = requests.post(f"{api_base}/api/simulations", json=payload, headers=headers, timeout=10, verify=False)
                        if r_trig.status_code == 200:
                            sim_id = r_trig.json()["id"]
                            st.session_state.active_simulation_id = sim_id
                            
                            # Polling loop for async tasks
                            completed = False
                            for _ in range(10):
                                time.sleep(0.5)
                                r_check = requests.get(f"{api_base}/api/simulations/{sim_id}", headers=headers, timeout=5, verify=False)
                                if r_check.status_code == 200:
                                    run_info = r_check.json()
                                    if run_info["status"] in ["Completed", "Failed"]:
                                        completed = True
                                        break
                            
                            if completed:
                                st.toast("Emulation campaign completed!", icon="✓")
                                st.rerun()
                            else:
                                st.warning("Simulation is running asynchronously in the background. Refresh in a few seconds.")
                        else:
                            st.error(f"Failed to queue simulation: {r_trig.text}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")

        # Past Runs Table list
        st.markdown("### ⏳ Simulation History")
        try:
            r_runs = requests.get(f"{api_base}/api/simulations", headers=headers, timeout=5, verify=False)
            if r_runs.status_code == 200:
                past_runs = r_runs.json()
                if past_runs:
                    run_rows = []
                    for run in past_runs:
                        run_rows.append({
                            "ID": run["id"],
                            "Scenario": run["scenario_name"],
                            "Success Rate": f"{run['detection_success_rate'] * 100:.1f}%",
                            "Score": f"{int(run['coverage_score'] * 100)}/100",
                            "Status": run["status"]
                        })
                    
                    # Selection for viewing detail
                    selected_run_id = st.selectbox(
                        "Select Past Run to Analyze", 
                        options=[r["id"] for r in past_runs],
                        format_func=lambda x: f"Run #{x} - {next(r['scenario_name'] for r in past_runs if r['id'] == x)}"
                    )
                    if selected_run_id:
                        st.session_state.active_simulation_id = selected_run_id
                        
                    # Render simple table widget
                    TableWidget("Past Simulations List", run_rows, columns=["ID", "Scenario", "Success Rate", "Score", "Status"]).render()
                else:
                    st.info("No past emulation runs recorded. Run your first scenario above!")
        except Exception as e:
            st.error(f"Error fetching runs: {str(e)}")

    # ─── Right Column: Timeline, Validation and AI Assistant ────────────────
    with col_right:
        active_id = st.session_state.get("active_simulation_id")
        
        if not active_id:
            st.markdown("### 🔍 Simulation Analytics")
            st.info("Please execute an emulation campaign or select a past run from the history panel to view analysis details.")
            return

        # Fetch active run details
        run_data = None
        try:
            r_run = requests.get(f"{api_base}/api/simulations/{active_id}", headers=headers, timeout=5, verify=False)
            if r_run.status_code == 200:
                run_data = r_run.json()
        except Exception as e:
            st.error(f"Error loading active run details: {str(e)}")
            
        if not run_data:
            st.warning("Failed to load details for the selected run.")
            return

        results = json.loads(run_data.get("results_data") or "{}")
        exec_summary = results.get("executive_summary", {})
        timeline_events = results.get("timeline", [])
        triggered_rules = results.get("triggered_rules", [])
        missed_rules = results.get("missed_rules", [])

        st.markdown(f"### 📊 Analysis for Run #{active_id}: {run_data['scenario_name']}")

        # Render Executive Summary Row
        s1, s2 = st.columns(2)
        with s1:
            StatusWidget(
                title="Simulation Score", 
                value=f"{exec_summary.get('simulation_score', 0)} / 100",
                status="healthy" if exec_summary.get("simulation_score", 0) >= 80 else ("warning" if exec_summary.get("simulation_score", 0) >= 50 else "danger"),
                subtitle="Success Rate Indicator"
            ).render()
        with s2:
            StatusWidget(
                title="Coverage Score", 
                value=f"{exec_summary.get('coverage_score', 0)} / 100",
                status="healthy" if exec_summary.get("coverage_score", 0) >= 80 else ("warning" if exec_summary.get("coverage_score", 0) >= 50 else "danger"),
                subtitle="Rule Match Coverage"
            ).render()

        with st.container(border=True):
            st.markdown("📝 **Executive Risk Analysis**")
            st.write(exec_summary.get("risk_summary", "No risk summary generated."))
            
            st.markdown("**Major Gaps Identified:**")
            for gap in exec_summary.get("major_gaps", []):
                st.markdown(f"- 🔴 {gap}")
                
            st.markdown("**Recommended Remediation Actions:**")
            for imp in exec_summary.get("recommended_improvements", []):
                st.markdown(f"- 🛠️ {imp}")

        # Tabs for detailed widgets
        tab_timeline, tab_rules, tab_mitre, tab_ai = st.tabs([
            "📅 Attack Timeline", "🛡️ Detection Rules", "🗺️ MITRE matrix", "🧠 AI Purple Assistant"
        ])

        # ─── Timeline Tab ────────────────────────────────────────────────────
        with tab_timeline:
            st.markdown("#### Synthetic Adversary Timeline")
            timeline_items = []
            for idx, ev in enumerate(timeline_events):
                status_color = "success" if ev["detection_status"] == "Detected" else "danger"
                timeline_items.append({
                    "label": f"{ev['technique']} - {ev['detection_status'].upper()}",
                    "detail": (
                        f"**Timestamp:** {ev['timestamp']}<br/>"
                        f"**Host:** {ev['host']} | **User:** {ev['user']} | **Severity:** {ev['severity']}<br/>"
                        f"**Latency:** {ev['detection_latency_sec']}s"
                    ),
                    "status": status_color
                })
            
            if timeline_items:
                TimelineWidget("Attack Sequence Step List", timeline_items, "Chronological execution steps").render()
            else:
                st.info("No timeline events generated.")

        # ─── Rules Validation Tab ──────────────────────────────────────────
        with tab_rules:
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.markdown("🟢 **Triggered Rules**")
                if triggered_rules:
                    for rule in triggered_rules:
                        st.markdown(
                            f"""
                            <div style="background-color: var(--bg-secondary); padding: 0.5rem; border-radius: 6px; border: 1px solid var(--border-color); margin-bottom: 0.35rem;">
                              <div style="font-size:0.8rem; font-weight:700; color:var(--success);">{rule['name']}</div>
                              <div style="font-size:0.68rem; color:var(--text-secondary);">{rule['mitre_technique']} | Severity: {rule['severity']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No rules triggered.")
            with r_col2:
                st.markdown("🔴 **Missed Rules**")
                if missed_rules:
                    for rule in missed_rules:
                        st.markdown(
                            f"""
                            <div style="background-color: var(--bg-secondary); padding: 0.5rem; border-radius: 6px; border: 1px solid var(--border-color); margin-bottom: 0.35rem;">
                              <div style="font-size:0.8rem; font-weight:700; color:var(--danger);">{rule['name']}</div>
                              <div style="font-size:0.68rem; color:var(--text-secondary);">{rule['mitre_technique']} | Severity: {rule['severity']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No rules missed.")

        # ─── MITRE Tactic Matrix Tab ─────────────────────────────────────────
        with tab_mitre:
            st.markdown("#### MITRE ATT&CK Technique Coverage Matrix")
            
            # Map of simulated techniques
            scen_techs = [ev.get("technique") for ev in timeline_items]
            
            st.markdown(
                """
                <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.5rem; font-size:0.75rem; text-align:center;">
                  <div style="background-color:#1B4332; border:1px solid #2D6A4F; border-radius:6px; padding:0.5rem; color:#D8F3DC;">
                    <b>Detected</b><br/>Valid signature alert triggered
                  </div>
                  <div style="background-color:#5C1A1A; border:1px solid #800000; border-radius:6px; padding:0.5rem; color:#FFD6D6;">
                    <b>Missed</b><br/>No active signatures matched telemetry
                  </div>
                  <div style="background-color:#2C3E50; border:1px solid #34495E; border-radius:6px; padding:0.5rem; color:#ECF0F1;">
                    <b>Partially Covered</b><br/>Sub-techniques need optimization
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # List of techniques and coverage details
            for ev in timeline_events:
                status_pill = "Detected" if ev["detection_status"] == "Detected" else "Missed"
                status_color = "success" if ev["detection_status"] == "Detected" else "danger"
                
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:0.5rem 0.75rem; background-color:var(--bg-secondary); border-radius:8px; border:1px solid var(--border-color); margin-bottom:0.4rem;">
                      <div>
                        <div style="font-size:0.8rem; font-weight:700;">{ev['technique']}</div>
                        <div style="font-size:0.65rem; color:var(--text-secondary);">Host: {ev['host']} | User: {ev['user']}</div>
                      </div>
                      <span class="badge {status_color}" style="font-size:0.55rem; padding:0.15rem 0.4rem;">{status_pill.upper()}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # ─── AI Purple Assistant Tab ─────────────────────────────────────────
        with tab_ai:
            st.markdown("#### 🧠 Copilot AI Purple Assistant Suggestions")
            
            # Sub-question options for purple assistant
            ai_questions = {
                "Explain missed detections": "explain_missed",
                "Recommend new rules": "recommend_rules",
                "Suggest threshold changes": "suggest_thresholds",
                "Generate post-exercise summary": "post_exercise_summary",
                "Recommend investigation priorities": "investigation_priorities",
                "Estimate defensive maturity": "defensive_maturity"
            }
            
            selected_ai_q = st.selectbox("Select Analysis Task", options=list(ai_questions.keys()))
            query_type = ai_questions[selected_ai_q]
            
            if st.button("🧠 Ask Assistant", use_container_width=True, key="ask_purple_assistant_btn"):
                ai_payload = {
                    "run_id": active_id,
                    "query_type": query_type
                }
                
                with st.spinner("AI analyzing simulation run..."):
                    try:
                        r_ai = requests.post(f"{api_base}/api/simulations/ai-assistant", json=ai_payload, headers=headers, timeout=12, verify=False)
                        if r_ai.status_code == 200:
                            ai_res = r_ai.json()
                            st.session_state.ai_purple_response = ai_res
                        else:
                            st.error(f"AI Assistant call failed: {r_ai.text}")
                    except Exception as e:
                        st.error(f"Error calling AI Assistant: {str(e)}")
            
            # Render response using AIWidget
            ai_res_data = st.session_state.get("ai_purple_response")
            if ai_res_data:
                AIWidget(
                    title="Purple Team Assistant Insights",
                    bullets=ai_res_data.get("bullets", []),
                    subtitle=selected_ai_q,
                    confidence=ai_res_data.get("confidence", "High (90%)"),
                    actions=ai_res_data.get("actions", []),
                    mitre=run_data.get("mitre_techniques", "").split(",") if run_data.get("mitre_techniques") else [],
                    key="ai_purple"
                ).render()
            else:
                st.info("Click 'Ask Assistant' to compile the AI Purple Team analysis.")
