"""SOAR Automation & Response Orchestration Streamlit View Component."""

import json
import time
import requests
import streamlit as st
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dashboard.components.empty_states import render_empty_state
from dashboard.components.loading_states import render_loading_state


def render_soar_page(
    explain_rows: List[Dict[str, Any]],
    detect_rows: List[Dict[str, Any]],
    latency_ms: int,
    api_base: str
):
    """Renders the SOAR Automation & Response Orchestration Workspace."""

    # Authentication headers
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}

    # Initialize local session states
    if "soar_selected_workflow_id" not in st.session_state:
        st.session_state.soar_selected_workflow_id = None
    if "soar_ai_query_type" not in st.session_state:
        st.session_state.soar_ai_query_type = "recommend_automation"
    if "soar_ai_results" not in st.session_state:
        st.session_state.soar_ai_results = {}
    if "soar_new_workflow_steps" not in st.session_state:
        st.session_state.soar_new_workflow_steps = []

    # ─── 1. Header Section ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">SOAR Orchestration</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">Security Orchestration, Automation, and Automated Threat Containment Actions</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> AUTOMATION LOGIC ENGAGED
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ─── 2. Fetch KPIs from API ─────────────────────────────────────────────
    kpis = {
        "automation_coverage_pct": 82.5,
        "automated_actions": 12,
        "pending_approvals": 0,
        "workflow_success_rate": 96.8,
        "avg_automation_time_seconds": 1.88,
        "playbook_automation_score": 88.4
    }
    
    try:
        r_kpis = requests.get(f"{api_base}/api/incident-response/kpis", headers=headers, timeout=5, verify=False)
        if r_kpis.status_code == 200:
            res_kpis = r_kpis.json()
            # Update matching SOAR keys
            for key in kpis.keys():
                if key in res_kpis:
                    kpis[key] = res_kpis[key]
    except Exception:
        pass

    # Render KPI Cards Row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Automation Coverage</div>
                <div class="metric-value">{kpis["automation_coverage_pct"]}%</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Orchestrated incidents</div>
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
                <div class="card-title">Automated Actions</div>
                <div class="metric-value">{kpis["automated_actions"]}</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Simulated blocks executed</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k3:
        pill_color = "var(--danger)" if kpis["pending_approvals"] > 0 else "var(--text-secondary)"
        font_weight = "700" if kpis["pending_approvals"] > 0 else "normal"
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Pending Approvals</div>
                <div class="metric-value" style="color:{pill_color};">{kpis["pending_approvals"]}</div>
                <div style="font-size:0.7rem; color:{pill_color}; font-weight:{font_weight};">Suspended gates</div>
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
                <div class="card-title">Workflow Success</div>
                <div class="metric-value">{kpis["workflow_success_rate"]}%</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Action success rate</div>
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
                <div class="card-title">Avg Automation Time</div>
                <div class="metric-value">{kpis["avg_automation_time_seconds"]}s</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Trigger to finish time</div>
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
                <div class="card-title">Playbook Auto Score</div>
                <div class="metric-value">{kpis["playbook_automation_score"]}</div>
                <div style="font-size:0.7rem; color:var(--text-secondary);">Overall orchestrator rating</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── 3. Main Workspace Layout (Two Columns) ─────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        # ─── Workflow Builder ───
        st.markdown(
            """
            <div class="soc-card-header" style="margin-top:0;">
                <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:0.5rem;">
                    🛠️ Workflow Orchestrator
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Fetch workflows from API
        workflows = []
        try:
            r_wf = requests.get(f"{api_base}/api/soar/workflows", headers=headers, timeout=5, verify=False)
            if r_wf.status_code == 200:
                workflows = r_wf.json()
        except Exception:
            pass

        # Select workflow
        wf_names = ["-- Create Custom Workflow --"] + [w["name"] for w in workflows]
        selected_wf_name = st.selectbox("Select Active Workflow Template:", wf_names, index=1 if len(workflows) > 0 else 0)

        selected_wf = None
        if selected_wf_name != "-- Create Custom Workflow --":
            selected_wf = next((w for w in workflows if w["name"] == selected_wf_name), None)

        if selected_wf:
            # Display Selected Workflow Details
            st.markdown(
                f"""
                <div style="padding:1rem; background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:4px; margin-bottom:1rem;">
                    <strong>Trigger Condition:</strong> <code style="color:var(--primary);">{selected_wf['trigger_type']}</code><br>
                    <strong>Description:</strong> {selected_wf['description']}<br>
                    <strong>Status:</strong> <span style="color:green; font-weight:700;">{selected_wf['status']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.session_state.soar_selected_workflow_id = selected_wf["id"]

            # Visual list of steps
            steps = json.loads(selected_wf["steps_json"])
            st.markdown("<strong>Workflow Processing Steps:</strong>", unsafe_allow_html=True)
            for idx, step in enumerate(steps):
                step_type = step["type"]
                badge_color = "var(--primary)" if step_type == "Action" else "var(--warning)"
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; justify-content:space-between; padding:0.5rem 0.75rem; background:rgba(255,255,255,0.02); border-left:4px solid {badge_color}; margin-bottom:0.5rem; border-radius:0 4px 4px 0;">
                        <div>
                            <strong>Step {idx+1}:</strong> {step['name']}
                            <div style="font-size:0.75rem; color:var(--text-secondary);">Parameter: <code>{step['parameter']}</code></div>
                        </div>
                        <span style="font-size:0.75rem; background:rgba(255,255,255,0.05); padding:0.2rem 0.5rem; border-radius:3px;">
                            {step_type}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            # Create Custom Workflow Form
            st.markdown("<p style='font-size:0.85rem; color:var(--text-secondary);'>Define a trigger, condition criteria, and response actions checklist.</p>", unsafe_allow_html=True)
            with st.form("create_workflow_form"):
                wf_name = st.text_input("Workflow Name:", placeholder="e.g. Host Isolation on Ransomware")
                wf_desc = st.text_area("Description:", placeholder="Brief explanation of safety controls and actions...")
                wf_trigger = st.selectbox("Trigger Classification Criteria:", [
                    "Severity High", "Port Scan", "Credential Spray", "Phishing Alert", "Ransomware Detected", "SQL Injection Alert"
                ])

                st.markdown("<strong>Configure Steps Checklist:</strong>", unsafe_allow_html=True)
                
                # Dynamic Steps list input using session state
                cols = st.columns([2, 2, 3])
                with cols[0]:
                    new_step_type = st.selectbox("Step Type:", ["Action", "Approval"])
                with cols[1]:
                    new_step_name = st.selectbox("Action Integration:", [
                        "Isolate Host", "Block IP", "Disable User", "Create Ticket", "Notify Slack", "Notify Teams", "Send Email"
                    ] if new_step_type == "Action" else ["Require Manual SOC Approval", "Require Multi-Step Approval"])
                with cols[2]:
                    new_step_param = st.text_input("Parameter / Target:", placeholder="e.g. workstation-01, 10.0.0.1")

                add_step = st.form_submit_button("➕ Append Step to Logic Array")
                if add_step:
                    st.session_state.soar_new_workflow_steps.append({
                        "type": new_step_type,
                        "name": new_step_name,
                        "parameter": new_step_param
                    })

                # Display currently built steps
                if st.session_state.soar_new_workflow_steps:
                    st.markdown("<div style='margin-top:0.5rem; font-size:0.8rem; font-weight:700;'>Added Steps Queue:</div>", unsafe_allow_html=True)
                    for step_idx, step in enumerate(st.session_state.soar_new_workflow_steps):
                        st.text(f"  [{step_idx+1}] {step['type']}: {step['name']} -> {step['parameter']}")

                # Clear steps helper
                clear_steps = st.form_submit_button("🧹 Clear Added Steps")
                if clear_steps:
                    st.session_state.soar_new_workflow_steps = []
                    st.rerun()

                submit_workflow = st.form_submit_button("💾 Save & Enable Automated Playbook")
                if submit_workflow:
                    if not wf_name or not st.session_state.soar_new_workflow_steps:
                        st.error("Please fill name and add at least one response step.")
                    else:
                        payload = {
                            "name": wf_name,
                            "description": wf_desc,
                            "trigger_type": wf_trigger,
                            "steps": st.session_state.soar_new_workflow_steps
                        }
                        try:
                            res = requests.post(f"{api_base}/api/soar/workflows", json=payload, headers=headers, timeout=5)
                            if res.status_code == 200:
                                st.success(f"Successfully configured workflow '{wf_name}'!")
                                st.session_state.soar_new_workflow_steps = []
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Error creating workflow: {res.text}")
                        except Exception as e:
                            st.error(f"Network error: {str(e)}")

    with col2:
        # ─── Approval Queue ───
        st.markdown(
            """
            <div class="soc-card-header" style="margin-top:0;">
                <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:0.5rem;">
                    🛡️ Pending Approval Queue
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        executions = []
        try:
            r_ex = requests.get(f"{api_base}/api/soar/executions", headers=headers, timeout=5, verify=False)
            if r_ex.status_code == 200:
                executions = r_ex.json()
        except Exception:
            pass

        suspended_executions = [e for e in executions if e["status"] == "Suspended"]

        if not suspended_executions:
            render_empty_state("No actions are currently suspended awaiting validation approval. Systems running fully automated or clear.", "SOAR Gates Clear")
        else:
            for ex in suspended_executions:
                log = json.loads(ex["execution_log_json"])
                current_idx = ex["current_step_index"]
                current_step = log[current_idx] if current_idx < len(log) else {}

                st.markdown(
                    f"""
                    <div style="border: 1px solid var(--warning); padding:1rem; border-radius:4px; margin-bottom:1rem; background:rgba(239,127,26,0.03);">
                        <div style="font-size:0.75rem; color:var(--warning); font-weight:700; text-transform:uppercase;">APPROVAL GATED CHECKPOINT</div>
                        <h4 style="margin:0.25rem 0 0.5rem 0; font-size:1rem;">{ex['workflow_name']}</h4>
                        <strong>Gated Action:</strong> <code style="color:var(--warning); font-size:0.9rem;">{current_step.get('name', 'N/A')}</code><br>
                        <strong>Target Parameter:</strong> <code>{current_step.get('parameter', 'N/A')}</code><br>
                        <strong>Linked Incident:</strong> <code style="color:var(--primary); font-weight:700;">{ex.get('linked_investigation_id', 'N/A')}</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Approval comment input
                note = st.text_input("Approver Action Audit Note:", key=f"note_{ex['id']}", placeholder="e.g. Confirmed malicious indicator, proceed with containment.")
                
                app_cols = st.columns(2)
                with app_cols[0]:
                    if st.button("✅ Approve Action", key=f"app_{ex['id']}"):
                        try:
                            payload = {"note": note if note else "Approved by analyst."}
                            res_app = requests.post(f"{api_base}/api/soar/executions/{ex['id']}/approve", json=payload, headers=headers)
                            if res_app.status_code == 200:
                                st.success("Step approved and execution resumed.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Approval failed: {res_app.text}")
                        except Exception as e:
                            st.error(f"Error approving: {str(e)}")

    st.markdown("<br><hr style='border:0; border-top:1px solid var(--border-color);'><br>", unsafe_allow_html=True)

    # ─── 4. Automation History ──────────────────────────────────────────────
    st.markdown(
        """
        <div class="soc-card-header">
            <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:0.5rem;">
                🕰️ Automation Execution Logs
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not executions:
        render_empty_state("No automated workflow runs have been logged in the audit history.", "Orchestrator Idle")
    else:
        # History table
        hist_data = []
        for ex in executions:
            started = ex.get("started_at", "N/A")
            if started != "N/A":
                started = started.split("T")[0] + " " + started.split("T")[1][:8]
            
            status_style = "color:green; font-weight:700;" if ex["status"] == "Completed" else (
                "color:var(--warning); font-weight:700;" if ex["status"] == "Suspended" else "color:red;"
            )
            
            hist_data.append(
                f"""
                <tr>
                    <td style="font-weight:700;">{ex["workflow_name"]}</td>
                    <td><code>{ex["linked_investigation_id"] or "N/A"}</code></td>
                    <td><span style="{status_style}">{ex["status"]}</span></td>
                    <td>Step {ex["current_step_index"] + 1}</td>
                    <td>{started}</td>
                    <td>{ex["duration_seconds"]:.1f}s</td>
                    <td><small>{ex["result"] or "Processing..."}</small></td>
                </tr>
                """
            )

        st.markdown(
            f"""
            <table class="soc-table" style="width:100%;">
                <thead>
                    <tr>
                        <th>Workflow Template</th>
                        <th>Investigation ID</th>
                        <th>Execution Status</th>
                        <th>Progress</th>
                        <th>Started At</th>
                        <th>Duration</th>
                        <th>Audit Conclusion</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(hist_data)}
                </tbody>
            </table>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><hr style='border:0; border-top:1px solid var(--border-color);'><br>", unsafe_allow_html=True)

    # ─── 5. AI Automation Assistant ─────────────────────────────────────────
    st.markdown(
        """
        <div class="soc-card-header">
            <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:0.5rem; color:var(--primary);">
                🤖 Copilot AI Orchestration Assistant
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    ai_col1, ai_col2 = st.columns([1, 2])

    with ai_col1:
        st.session_state.soar_ai_query_type = st.radio(
            "Select AI Analysis Perspective:",
            [
                ("recommend_automation", "Recommend Automation"),
                ("explain_workflow", "Explain Workflow Diagram"),
                ("detect_redundancy", "Detect Redundant Steps"),
                ("suggest_optimizations", "Suggest Tuning & Optimizations"),
                ("estimate_impact", "Estimate Automation Impact (ROI)"),
                ("draft_documentation", "Draft Workflow Wiki Documentation")
            ],
            format_func=lambda x: x[1]
        )[0]

        # Use first workflow as target for analysis
        target_wf_id = st.session_state.soar_selected_workflow_id if st.session_state.soar_selected_workflow_id else (
            workflows[0]["id"] if len(workflows) > 0 else None
        )

        if st.button("🔮 Query Copilot Insights", disabled=(target_wf_id is None)):
            with st.spinner("Analyzing playbook graph structure and compliance SLAs..."):
                try:
                    payload = {"query_type": st.session_state.soar_ai_query_type, "workflow_id": target_wf_id}
                    r_ai = requests.post(f"{api_base}/api/soar/ai-assistant", json=payload, headers=headers, timeout=5)
                    if r_ai.status_code == 200:
                        st.session_state.soar_ai_results = r_ai.json()
                    else:
                        st.session_state.soar_ai_results = {"bullets": ["Error fetching AI suggestions."], "confidence": "0%"}
                except Exception as e:
                    st.session_state.soar_ai_results = {"bullets": [f"Error: {str(e)}"], "confidence": "0%"}

    with ai_col2:
        if st.session_state.soar_ai_results:
            res = st.session_state.soar_ai_results
            st.markdown(
                f"""
                <div class="ai-widget-output" style="padding:1.25rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:0.5rem; margin-bottom:0.75rem;">
                        <span style="font-weight:700; color:var(--primary);">COPILOT ORCHESTRATION FEEDBACK</span>
                        <span style="font-size:0.75rem; background:var(--primary-bg); color:var(--primary); padding:0.2rem 0.5rem; border-radius:3px;">
                            CONFIDENCE: {res.get('confidence', 'N/A')}
                        </span>
                    </div>
                    {"".join(f"<p style='margin:0.4rem 0; font-size:0.9rem;'>{b}</p>" for b in res.get('bullets', []))}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Interactive action items proposed by AI
            if res.get("actions"):
                st.markdown("<p style='font-size:0.8rem; margin: 0.5rem 0 0.25rem 0; color:var(--text-secondary);'>Quick-Apply Actions Suggested by Copilot:</p>", unsafe_allow_html=True)
                for act in res["actions"]:
                    if st.button(f"⚡ Apply: {act}", key=f"quick_{act}"):
                        st.info(f"Applying AI optimization: '{act}'. (Mock Action Executed Successfully)")
                        time.sleep(1)
        else:
            render_empty_state("Select a perspective and click 'Query Copilot Insights' to generate visual playbook reviews.", "AI Copilot Standby")
