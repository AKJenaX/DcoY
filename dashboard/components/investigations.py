"""Dedicated Investigations & Case Management page view component connected to SQLAlchemy DB backend."""

import json
import time
import requests
import streamlit as st
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dashboard.utils.constants import LOW_RISK_THRESHOLD, HIGH_RISK_THRESHOLD


def render_investigations_page(
    explain_rows: List[Dict[str, Any]],
    detect_rows: List[Dict[str, Any]],
    latency_ms: int,
    api_base: str
):
    """Renders the SOC Case Investigations Workspace linked to database backend."""

    # Resolve token headers
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}

    # Initialize select state variables
    if "selected_case_id" not in st.session_state:
        st.session_state.selected_case_id = "CASE-2026-001"
    if "case_search_query" not in st.session_state:
        st.session_state.case_search_query = ""
    if "case_filter_status" not in st.session_state:
        st.session_state.case_filter_status = "All"
    if "case_filter_severity" not in st.session_state:
        st.session_state.case_filter_severity = "All"
    if "case_sort_by" not in st.session_state:
        st.session_state.case_sort_by = "Last Updated"

    # ─── 1. Header Section ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">Investigations</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">DB-Backed Case Management & Incident Auditing</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> DATABASE CORE SYNCHRONIZED
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ─── Fetch Cases List from Backend ──────────────────────────────────────
    params = {
        "status": st.session_state.case_filter_status,
        "severity": st.session_state.case_filter_severity,
        "search": st.session_state.case_search_query,
        "sort_by": st.session_state.case_sort_by
    }
    
    try:
        r_list = requests.get(f"{api_base}/api/investigations", params=params, headers=headers, timeout=10, verify=False)
        if r_list.status_code == 200:
            cases_list = r_list.json()
        else:
            cases_list = []
            st.error(f"Failed to fetch cases: {r_list.status_code} - {r_list.text}")
    except Exception as e:
        cases_list = []
        st.error(f"Backend offline: Connection to database API failed. ({type(e).__name__})")

    # ─── 2. Top KPI Cards ───────────────────────────────────────────────────
    open_cases = len([c for c in cases_list if c["status"] == "Open"])
    active_cases = len([c for c in cases_list if c["status"] == "Active"])
    resolved_cases = len([c for c in cases_list if c["status"] == "Resolved"])
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Open Cases</div>
                <div class="metric-value">{open_cases}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Awaiting triage analysis</div>
              </div>
              <div class="soc-kpi-icon warning">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                </svg>
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
                <div class="card-title">Active Investigations</div>
                <div class="metric-value">{active_cases}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Currently triaged by analysts</div>
              </div>
              <div class="soc-kpi-icon blue">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
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
                <div class="card-title">Resolved Cases</div>
                <div class="metric-value">{resolved_cases}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Remediated threat metrics</div>
              </div>
              <div class="soc-kpi-icon success">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            """
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Avg Resolution Time</div>
                <div class="metric-value">1.4 hrs</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Incident start to remediation</div>
              </div>
              <div class="soc-kpi-icon purple">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                  <polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("<br/>", unsafe_allow_html=True)

    # Resolve active selected case key
    sel_id = st.session_state.selected_case_id
    if cases_list and sel_id not in [c["id"] for c in cases_list]:
        sel_id = cases_list[0]["id"]
        st.session_state.selected_case_id = sel_id

    # ─── 3. Left Panel (35%): Case List Ledger ──────────────────────────────
    col_list, col_details = st.columns([3.5, 6.5])

    with col_list:
        st.markdown('<h3 class="section-title">Case Triage Ledger</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            st.session_state.case_search_query = st.text_input(
                "Search Ledger",
                value=st.session_state.case_search_query,
                placeholder="ID, Title, Analyst...",
                key="case_search_input"
            )
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.session_state.case_filter_status = st.selectbox(
                    "Status Filter",
                    options=["All", "Open", "Active", "Resolved"],
                    index=["All", "Open", "Active", "Resolved"].index(st.session_state.case_filter_status),
                    key="case_filter_status_select"
                )
            with f_col2:
                st.session_state.case_filter_severity = st.selectbox(
                    "Severity Filter",
                    options=["All", "High", "Medium", "Low"],
                    index=["All", "High", "Medium", "Low"].index(st.session_state.case_filter_severity),
                    key="case_filter_severity_select"
                )
                
            st.session_state.case_sort_by = st.selectbox(
                "Sort Ledger By",
                options=["Last Updated", "Severity", "Priority", "Created Time"],
                index=["Last Updated", "Severity", "Priority", "Created Time"].index(st.session_state.case_sort_by),
                key="case_sort_select"
            )
            
            st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)
            
            # Action: Create Case POST API Call
            if st.button("➕ Create New Investigation", use_container_width=True, key="create_new_case_btn"):
                new_id = f"CASE-{datetime.now().year}-{int(time.time()) % 1000:03d}"
                payload = {
                    "id": new_id,
                    "title": f"Incident Investigation Case {new_id}",
                    "status": "Open",
                    "priority": "Medium",
                    "severity": "Medium",
                    "assigned_analyst": "Unassigned",
                    "risk_score": 0.50,
                    "ai_summary": "No case summary compiled yet. Attach telemetry context to compile executive summary.",
                    "notes": ""
                }
                try:
                    r_create = requests.post(f"{api_base}/api/investigations", json=payload, headers=headers, timeout=10, verify=False)
                    if r_create.status_code == 200:
                        st.session_state.selected_case_id = new_id
                        st.toast(f"Case {new_id} created successfully!", icon="✓")
                        st.rerun()
                    else:
                        st.error(f"Failed to create case: {r_create.text}")
                except Exception as e:
                    st.error(f"Network error creating case: {str(e)}")

            st.markdown("<br/>", unsafe_allow_html=True)

            # Render scrollable list of cases
            for c in cases_list:
                cid = c["id"]
                is_active = (cid == sel_id)
                border_glow = "border: 1px solid var(--primary); box-shadow: 0 0 10px rgba(59,130,246,0.15);" if is_active else "border: 1px solid var(--border-color);"
                
                s_level = c["severity"].upper()
                s_color = "var(--danger)" if s_level == "HIGH" else ("var(--warning)" if s_level == "MEDIUM" else "var(--success)")
                
                status_style = "color:var(--text-secondary);"
                if c["status"] == "Open":
                    status_style = "color:var(--warning);"
                elif c["status"] == "Active":
                    status_style = "color:var(--primary);"
                elif c["status"] == "Resolved":
                    status_style = "color:var(--success);"
                    
                st.markdown(
                    f"""
                    <div style="{border_glow} background-color: var(--card-bg); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.7rem; font-weight:700; color:var(--text-secondary);">{cid}</span>
                        <span style="font-size:0.62rem; font-weight:700; color:{s_color}; border:1px solid {s_color}; border-radius:3px; padding:0.1rem 0.35rem;">
                          {s_level}
                        </span>
                      </div>
                      <div style="font-size:0.84rem; font-weight:700; color:var(--text-primary); margin: 0.35rem 0;">{c["title"]}</div>
                      <div style="display:flex; justify-content:space-between; font-size:0.72rem; margin-top:0.5rem;">
                        <span style="{status_style}">Status: <b>{c["status"]}</b></span>
                        <span style="color:var(--muted);">Analyst: <b>{c["assigned_analyst"]}</b></span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button(f"Analyze {cid}", key=f"select_case_btn_{cid}", use_container_width=True):
                    st.session_state.selected_case_id = cid
                    st.rerun()

    # ─── 4. Right Panel (65%): Case Details ──────────────────────────────────
    with col_details:
        st.markdown('<h3 class="section-title">Case Details & Chronology</h3>', unsafe_allow_html=True)
        
        # Load Case Details from Backend
        case = None
        if sel_id:
            try:
                r_details = requests.get(f"{api_base}/api/investigations/{sel_id}", headers=headers, timeout=10, verify=False)
                if r_details.status_code == 200:
                    case = r_details.json()
                else:
                    st.warning(f"Failed to fetch details for {sel_id}: {r_details.status_code}")
            except Exception as e:
                st.error(f"Error loading case: {str(e)}")

        if case:
            with st.container(border=True):
                # Toolbar Case Actions
                a_col1, a_col2, a_col3, a_col4 = st.columns([1.5, 1.5, 1.5, 2])
                with a_col1:
                    # Rename Case Title
                    r_title = st.text_input("Rename Case Title", value=case["title"], key=f"case_rename_input_{sel_id}")
                    if r_title and r_title != case["title"]:
                        try:
                            r_up = requests.put(f"{api_base}/api/investigations/{sel_id}", json={"title": r_title}, headers=headers, timeout=10, verify=False)
                            if r_up.status_code == 200:
                                st.toast("Case renamed successfully!", icon="✓")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with a_col2:
                    # Reassign Analyst
                    r_analyst = st.selectbox(
                        "Assign Analyst",
                        options=["Unassigned", "Analyst Alpha", "Analyst Beta", "Lead SOC Officer"],
                        index=["Unassigned", "Analyst Alpha", "Analyst Beta", "Lead SOC Officer"].index(case["assigned_analyst"]),
                        key=f"case_assign_select_{sel_id}"
                    )
                    if r_analyst != case["assigned_analyst"]:
                        try:
                            r_up = requests.put(f"{api_base}/api/investigations/{sel_id}", json={"assigned_analyst": r_analyst}, headers=headers, timeout=10, verify=False)
                            if r_up.status_code == 200:
                                st.toast(f"Case assigned to {r_analyst}", icon="✓")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with a_col3:
                    # Case Status Toggle
                    status_opts = ["Open", "Active", "Resolved"]
                    r_status = st.selectbox(
                        "Case Status",
                        options=status_opts,
                        index=status_opts.index(case["status"]),
                        key=f"case_status_select_{sel_id}"
                    )
                    if r_status != case["status"]:
                        try:
                            r_up = requests.put(f"{api_base}/api/investigations/{sel_id}", json={"status": r_status}, headers=headers, timeout=10, verify=False)
                            if r_up.status_code == 200:
                                st.toast(f"Status changed to {r_status}", icon="✓")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with a_col4:
                    ctrl_d1, ctrl_d2 = st.columns(2)
                    with ctrl_d1:
                        # Duplicate case
                        if st.button("👥 Duplicate", use_container_width=True, key=f"dup_case_btn_{sel_id}"):
                            new_id = f"CASE-{datetime.now().year}-{int(time.time()) % 1000:03d}"
                            payload = {
                                "id": new_id,
                                "title": f"Copy of {case['title']}",
                                "status": "Open",
                                "priority": case["priority"],
                                "severity": case["severity"],
                                "assigned_analyst": case["assigned_analyst"],
                                "risk_score": case["risk_score"],
                                "ai_summary": case["ai_summary"],
                                "notes": case["notes"]
                            }
                            try:
                                r_create = requests.post(f"{api_base}/api/investigations", json=payload, headers=headers, timeout=10, verify=False)
                                if r_create.status_code == 200:
                                    st.session_state.selected_case_id = new_id
                                    st.toast(f"Case duplicated as {new_id}!", icon="✓")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error duplicating: {str(e)}")
                    with ctrl_d2:
                        # Soft delete case
                        if st.button("🗑️ Delete", use_container_width=True, key=f"del_case_btn_{sel_id}"):
                            try:
                                r_del = requests.delete(f"{api_base}/api/investigations/{sel_id}", headers=headers, timeout=10, verify=False)
                                if r_del.status_code == 200:
                                    st.toast(f"Case {sel_id} deleted.", icon="✓")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting: {str(e)}")

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Primary metadata details
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.markdown(f"**Case ID:** `{case['id']}`")
                    st.markdown(f"**Severity:** `{case['severity']}`")
                    st.markdown(f"**Priority:** `{case['priority']}`")
                with m_col2:
                    st.markdown(f"**Risk Score:** `{case['risk_score']:.2f}`")
                    st.markdown(f"**Affected IPs:** `{', '.join(case.get('affected_ips', [])) if case.get('affected_ips') else 'None'}`")
                with m_col3:
                    created_dt = case["created_time"].replace("T", " ").replace("Z", "")
                    updated_dt = case["updated_time"].replace("T", " ").replace("Z", "")
                    st.markdown(f"**Created:** `{created_dt}`")
                    st.markdown(f"**Updated:** `{updated_dt}`")

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # AI Summary & Remediation Runbook
                st.markdown("#### 🧠 AI Copilot Summary & Strategy")
                st.markdown(f"_{case['ai_summary']}_")
                
                ar_col1, ar_col2 = st.columns(2)
                with ar_col1:
                    # Regenerate AI Summary
                    if st.button("🔄 Regenerate AI Summary", use_container_width=True, key=f"regen_ai_summary_{sel_id}"):
                        ips_str = ", ".join(case.get("affected_ips", [])) if case.get("affected_ips") else "Unknown IPs"
                        mitre_str = ", ".join(case.get("mitre_techniques", [])) if case.get("mitre_techniques") else "Unknown MITRE ATT&CK vectors"
                        new_summary = (
                            f"Investigation case {case['id']} focuses on anomalous activity linked to source node host {ips_str}. "
                            f"The activity matches techniques including {mitre_str}. Recommended threat action incorporates "
                            f"network isolation rules and deploying deception honey decoy servers."
                        )
                        try:
                            r_up = requests.put(f"{api_base}/api/investigations/{sel_id}", json={"ai_summary": new_summary}, headers=headers, timeout=10, verify=False)
                            if r_up.status_code == 200:
                                st.toast("AI summary regenerated!", icon="✓")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with ar_col2:
                    if st.button("📋 Suggested Remediation Playbook", use_container_width=True, key=f"suggest_remediation_{sel_id}"):
                        st.session_state.remediation_dialogue = (
                            "**[REMEDIATION RUNBOOK: SSH & SCAN CONTROLS]**\n\n"
                            "1. **Isolate Attacking Interface:** Apply firewall ACLs blocking inbound TCP on port 22/80 for source subnets.\n"
                            "2. **Deception Trap Allocation:** Direct deception honeypot trap routers to advertise dynamic SYN decoy responses.\n"
                            "3. **Trigger Case Report:** Export incident JSON log telemetry and deploy case notes to SOC archive."
                        )
                        st.toast("Playbook runbook loaded!", icon="✓")

                if "remediation_dialogue" in st.session_state:
                    st.info(st.session_state.remediation_dialogue)
                    p_col1, p_col2 = st.columns(2)
                    with p_col1:
                        if st.button("🎯 Execute Playbook in Workspace", key="go_to_playbook_workspace_btn", use_container_width=True):
                            st.session_state.selected_incident_id = case["id"]
                            st.query_params["page"] = "incident_response"
                            st.rerun()
                    with p_col2:
                        if st.button("Dismiss Playbook", key="dismiss_remediation_btn", use_container_width=True):
                            del st.session_state.remediation_dialogue
                            st.rerun()

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Evidence Panel
                st.markdown("#### 📂 Attached Evidence Telemetry")
                if case.get("evidence"):
                    st.markdown(
                        """
                        <style>
                        .evidence-table {
                            width: 100%;
                            border-collapse: collapse;
                            font-size: 0.78rem;
                            background-color: var(--bg-secondary);
                            border: 1px solid var(--border-color);
                            border-radius: 4px;
                            margin-bottom: 0.75rem;
                        }
                        .evidence-table th, .evidence-table td {
                            padding: 0.45rem 0.65rem;
                            border-bottom: 1px solid var(--border-color);
                            text-align: left;
                        }
                        .evidence-table th {
                            font-weight: 700;
                            color: var(--secondary);
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    rows_html = ""
                    for ev in case["evidence"]:
                        rows_html += f"""
                        <tr>
                          <td>{ev.get('event')}</td>
                          <td>{ev.get('timestamp')}</td>
                          <td>{ev.get('severity')}</td>
                          <td>{ev.get('confidence')}</td>
                          <td><code>{ev.get('mitre')}</code></td>
                        </tr>
                        """
                    st.markdown(
                        f"""
                        <table class="evidence-table">
                          <thead>
                            <tr>
                              <th>Event</th>
                              <th>Timestamp</th>
                              <th>Severity</th>
                              <th>Confidence</th>
                              <th>MITRE</th>
                            </tr>
                          </thead>
                          <tbody>
                            {rows_html}
                          </tbody>
                        </table>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.info("No network telemetry attached as evidence yet. Select anomalies below to link evidence.")

                # Interactive panel to link telemetry as evidence
                st.markdown("##### Link Telemetry Anomaly as Case Evidence")
                live_anomalies_options = []
                for idx, r in enumerate(explain_rows):
                    ip_val = r.get("ip", "unknown")
                    et_val = r.get("event_type", "normal")
                    score_val = r.get("risk_score", 0.5)
                    live_anomalies_options.append(f"{idx}: {ip_val} | {et_val} | Score: {score_val:.2f}")
                
                if live_anomalies_options:
                    selected_anomaly = st.selectbox(
                        "Select Live Telemetry Anomaly",
                        options=live_anomalies_options,
                        key=f"link_anomaly_select_{sel_id}"
                    )
                    if st.button("🔗 Link Telemetry to Case", use_container_width=True, key=f"link_telemetry_btn_{sel_id}"):
                        a_idx = int(selected_anomaly.split(":")[0])
                        anomaly_data = explain_rows[a_idx]
                        
                        timestamp_clean = extract_event_timestamp(anomaly_data)
                        ev_payload = {
                            "event": f"Telemetry spike from {anomaly_data.get('ip')}",
                            "timestamp": timestamp_clean,
                            "severity": "High" if float(anomaly_data.get("risk_score") or 0) >= HIGH_RISK_THRESHOLD else "Medium",
                            "confidence": "High",
                            "mitre": "T1110" if "brute" in str(anomaly_data.get("event_type")).lower() else "T1046"
                        }
                        try:
                            r_ev = requests.post(f"{api_base}/api/investigations/{sel_id}/evidence", json=ev_payload, headers=headers, timeout=10, verify=False)
                            if r_ev.status_code == 200:
                                st.toast("Evidence linked to database case!", icon="✓")
                                st.rerun()
                            else:
                                st.error(f"Failed: {r_ev.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Linked Copilot Conversations
                st.markdown("#### 💬 Linked AI Investigation Conversations")
                if "copilot_conversations" in st.session_state:
                    avail_conv_ids = list(st.session_state.copilot_conversations.keys())
                    avail_conv_names = [st.session_state.copilot_conversations[k]["name"] for k in avail_conv_ids]
                    
                    if avail_conv_names:
                        link_target_name = st.selectbox(
                            "Link Investigation Case Chat",
                            options=avail_conv_names,
                            key=f"link_chat_select_{sel_id}"
                        )
                        target_conv_key = avail_conv_ids[avail_conv_names.index(link_target_name)]
                        
                        if st.button("🔗 Link Conversation to Case", use_container_width=True, key=f"link_chat_btn_{sel_id}"):
                            try:
                                r_chat = requests.post(f"{api_base}/api/investigations/{sel_id}/conversations", json={"conversation_key": target_conv_key}, headers=headers, timeout=10, verify=False)
                                if r_chat.status_code == 200:
                                    st.toast("Copilot conversation linked!", icon="✓")
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {r_chat.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                
                if case.get("linked_conversations"):
                    for c_key in case["linked_conversations"]:
                        if c_key in st.session_state.copilot_conversations:
                            conv = st.session_state.copilot_conversations[c_key]
                            with st.expander(f"Linked Chat: {conv['name']}"):
                                for msg in conv["history"]:
                                    st.markdown(f"**{msg['role'].upper()}**: {msg['content']}")
                else:
                    st.info("No Copilot conversations linked to this case yet.")

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Timeline Events (Audit Trail & Activity Logs)
                st.markdown("#### ⏳ Case Audit Trail & History")
                timeline_html = ""
                for log in sorted(case.get("timeline", []), key=lambda x: x["timestamp"]):
                    log_dt = log["timestamp"].replace("T", " ").replace("Z", "")
                    diff_vals = ""
                    if log.get("before_value") or log.get("after_value"):
                        diff_vals = f"""<br/><span style="color:var(--text-secondary); font-size:0.7rem;">Changed: <code>{log.get('before_value')}</code> &rarr; <code>{log.get('after_value')}</code></span>"""
                    
                    timeline_html += f"""
                    <div style="border-left: 2px solid var(--primary); padding-left: 0.75rem; margin-bottom: 0.75rem; font-size: 0.78rem;">
                      <div style="color:var(--secondary); font-weight:700; display:flex; justify-content:space-between;">
                        <span>{log_dt}</span>
                        <span style="color:var(--muted); font-size:0.68rem;">Action By: {log.get('action_by', 'System')}</span>
                      </div>
                      <div style="color:var(--text-primary); margin-top:0.15rem;">{log['event']} {diff_vals}</div>
                    </div>
                    """
                st.markdown(timeline_html, unsafe_allow_html=True)

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Analyst Notes History
                st.markdown("#### 📝 Case Analyst Notes Ledger")
                if case.get("notes_list"):
                    for n in case["notes_list"]:
                        n_dt = n["created_at"].replace("T", " ").replace("Z", "")[:19]
                        st.markdown(
                            f"""
                            <div style="background-color: var(--bg-secondary); padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--border-color); margin-bottom: 0.5rem;">
                              <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:var(--secondary); margin-bottom:0.25rem;">
                                <b>{n['author']}</b>
                                <span>{n_dt}</span>
                              </div>
                              <div style="font-size:0.8rem; color:var(--text-primary);">{n['content']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                # Add Analyst Note
                new_note = st.text_area("Add Case Note", value="", key=f"case_notes_input_{sel_id}")
                if st.button("💾 Save Case Note", key=f"save_notes_btn_{sel_id}"):
                    if new_note.strip():
                        try:
                            r_note = requests.post(f"{api_base}/api/investigations/{sel_id}/notes", json={"content": new_note}, headers=headers, timeout=10, verify=False)
                            if r_note.status_code == 200:
                                st.toast("Note added to database case!", icon="✓")
                                st.rerun()
                            else:
                                st.error(f"Failed: {r_note.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Export Controls (Markdown, HTML/PDF, JSON)
                st.markdown("#### 📥 Export Case Records")
                e_col1, e_col2, e_col3 = st.columns(3)
                
                # Format Markdown Export
                case_md = f"""# DcoY Security Case Record: {case['id']}
## Title: {case['title']}
- **Status:** {case['status']}
- **Severity:** {case['severity']}
- **Priority:** {case['priority']}
- **Assigned Analyst:** {case['assigned_analyst']}
- **Risk Score:** {case['risk_score']}
- **Created Time:** {case['created_time']}
- **Updated Time:** {case['updated_time']}

### Executive AI Summary
{case['ai_summary']}

### Telemetry Evidence Records
"""
                for ev in case.get("evidence", []):
                    case_md += f"- **{ev.get('event')}** [{ev.get('timestamp')}] | Severity: {ev.get('severity')} | MITRE: {ev.get('mitre')}\n"
                
                case_md += "\n### Analyst Notes Ledger\n"
                for n in case.get("notes_list", []):
                    case_md += f"- **{n['author']}** [{n['created_at']}]: {n['content']}\n"

                case_md += "\n### Investigation Chronological Timeline\n"
                for t in case.get("timeline", []):
                    case_md += f"- **{t['timestamp']}** [By: {t.get('action_by')}]: {t['event']}\n"
                
                with e_col1:
                    st.download_button(
                        label="📥 Export Markdown",
                        data=case_md,
                        file_name=f"dcoy_case_{sel_id}.md",
                        mime="text/markdown",
                        use_container_width=True,
                        key=f"export_md_btn_{sel_id}"
                    )
                with e_col2:
                    # PDF HTML-printable layout format
                    case_html = f"""
                    <html>
                    <head>
                      <style>
                        body {{ font-family: sans-serif; color: #111827; padding: 20px; }}
                        h1 {{ color: #1f2937; border-bottom: 2px solid #3B82F6; padding-bottom: 5px; }}
                        h2 {{ color: #4b5563; margin-top: 20px; }}
                        .meta-info {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                        .section {{ background-color: #f9fafb; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 15px; }}
                        .timeline-item {{ border-left: 2px solid #3B82F6; padding-left: 10px; margin-bottom: 10px; }}
                      </style>
                    </head>
                    <body>
                      <h1>DcoY SOC Incident Report - {case['id']}</h1>
                      <div class="meta-info">
                        <div><b>Case Title:</b> {case['title']}</div>
                        <div><b>Status:</b> {case['status']}</div>
                        <div><b>Severity:</b> {case['severity']}</div>
                        <div><b>Priority:</b> {case['priority']}</div>
                        <div><b>Assigned Analyst:</b> {case['assigned_analyst']}</div>
                        <div><b>Risk Score:</b> {case['risk_score']:.2f}</div>
                      </div>
                      <div class="section">
                        <h2>AI Summary</h2>
                        <p>{case['ai_summary']}</p>
                      </div>
                      <h2>Analyst Notes</h2>
                    """
                    for n in case.get("notes_list", []):
                        case_html += f"<div><b>{n['author']} ({n['created_at']}):</b> {n['content']}</div><br/>"
                        
                    case_html += "<h2>Timeline</h2>"
                    for t in case.get("timeline", []):
                        case_html += f"""
                        <div class="timeline-item">
                          <div><b>{t['timestamp']} (Action By: {t.get('action_by')})</b></div>
                          <div>{t['event']}</div>
                        </div>
                        """
                    case_html += "</body></html>"
                    
                    st.download_button(
                        label="📥 Export PDF (HTML)",
                        data=case_html,
                        file_name=f"dcoy_case_{sel_id}.html",
                        mime="text/html",
                        use_container_width=True,
                        key=f"export_pdf_btn_{sel_id}"
                    )
                with e_col3:
                    case_json = json.dumps(case, indent=2)
                    st.download_button(
                        label="📥 Export JSON",
                        data=case_json,
                        file_name=f"dcoy_case_{sel_id}.json",
                        mime="application/json",
                        use_container_width=True,
                        key=f"export_json_btn_{sel_id}"
                    )
        else:
            st.warning("No investigations selected or available. Click 'Create New Investigation' to begin a case.")
