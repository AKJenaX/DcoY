"""Dedicated Detection Engineering & Rule Management workspace component."""

import json
import requests
import streamlit as st
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dashboard.components.rule_quality import render_rule_quality_panel, render_validation_errors, render_ai_validation_assistant


def render_detection_rules_page(
    explain_rows: List[Dict[str, Any]],
    detect_rows: List[Dict[str, Any]],
    latency_ms: int,
    api_base: str
):
    """Renders the SOC Detection Engineering Rules Management Workspace."""

    # Set headers
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}

    # Initialize editor selections
    if "selected_rule_id" not in st.session_state:
        st.session_state.selected_rule_id = 1
    if "rule_search_query" not in st.session_state:
        st.session_state.rule_search_query = ""
    if "rule_filter_category" not in st.session_state:
        st.session_state.rule_filter_category = "All"
    if "rule_filter_severity" not in st.session_state:
        st.session_state.rule_filter_severity = "All"
    if "rule_filter_status" not in st.session_state:
        st.session_state.rule_filter_status = "All"

    # AI rule generator helpers
    if "ai_rule_helper_response" not in st.session_state:
        st.session_state.ai_rule_helper_response = None
    if "rule_test_metrics" not in st.session_state:
        st.session_state.rule_test_metrics = None
    if "rule_simulation_metrics" not in st.session_state:
        st.session_state.rule_simulation_metrics = None

    # ─── 1. Header Section ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">Detection Engineering</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">Analytical Threat Rules, Custom Signature Testing & Version control</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> SIG ENGINE ACTIVE
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ─── Fetch Rules List from Backend ──────────────────────────────────────
    params = {
        "category": st.session_state.rule_filter_category,
        "severity": st.session_state.rule_filter_severity,
        "status": st.session_state.rule_filter_status,
        "search": st.session_state.rule_search_query
    }
    
    try:
        r_rules = requests.get(f"{api_base}/api/rules", params=params, headers=headers, timeout=10, verify=False)
        if r_rules.status_code == 200:
            rules_list = r_rules.json()
        else:
            rules_list = []
            st.error(f"Failed to fetch rules: {r_rules.status_code}")
    except Exception as e:
        rules_list = []
        st.error(f"Rule database backend unreachable: {str(e)}")

    # ─── 2. Top KPI Cards ───────────────────────────────────────────────────
    active_count = len([r for r in rules_list if r["status"] == "Enabled"])
    disabled_count = len([r for r in rules_list if r["status"] == "Disabled"])
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Active Rules</div>
                <div class="metric-value">{active_count}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Currently evaluating log traffic</div>
              </div>
              <div class="soc-kpi-icon success">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
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
                <div class="card-title">Disabled Rules</div>
                <div class="metric-value">{disabled_count}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Parked rule signatures</div>
              </div>
              <div class="soc-kpi-icon warning">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            """
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Triggered Today</div>
                <div class="metric-value">4</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Matched ingress indicators</div>
              </div>
              <div class="soc-kpi-icon blue">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <line x1="18" y1="2" x2="22" y2="6"/><path d="M7.5 11.5L2 17l2 2 5.5-5.5"/><path d="M11.5 7.5L17 2l2 2-5.5 5.5"/>
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
                <div class="card-title">Avg Latency</div>
                <div class="metric-value">23ms</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Signature parsing execution</div>
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

    # ─── Rule Quality & Coverage Dashboard ──────────────────────────────────
    render_rule_quality_panel(api_base)

    # ─── 3. Main Split Layout ───────────────────────────────────────────────
    col_left, col_center = st.columns([3, 7])

    # Left Column (30%): Rule Explorer
    with col_left:
        st.markdown('<h3 class="section-title">Rule Explorer</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            st.session_state.rule_search_query = st.text_input(
                "Search Rules",
                value=st.session_state.rule_search_query,
                placeholder="Rule Name, details...",
                key="rule_search_input"
            )
            
            st.session_state.rule_filter_category = st.selectbox(
                "Category",
                options=["All", "Brute Force", "Port Scan", "Credential Stuffing", "Lateral Movement", "Privilege Escalation", "Suspicious PowerShell", "Public Exploit", "Beaconing", "Impossible Travel", "Custom Rules"],
                index=["All", "Brute Force", "Port Scan", "Credential Stuffing", "Lateral Movement", "Privilege Escalation", "Suspicious PowerShell", "Public Exploit", "Beaconing", "Impossible Travel", "Custom Rules"].index(st.session_state.rule_filter_category),
                key="rule_cat_select"
            )
            
            st.session_state.rule_filter_severity = st.selectbox(
                "Severity Filter",
                options=["All", "High", "Medium", "Low"],
                index=["All", "High", "Medium", "Low"].index(st.session_state.rule_filter_severity),
                key="rule_sev_select"
            )
            
            st.session_state.rule_filter_status = st.selectbox(
                "Status",
                options=["All", "Enabled", "Disabled"],
                index=["All", "Enabled", "Disabled"].index(st.session_state.rule_filter_status),
                key="rule_stat_select"
            )

            st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

            # Create Rule Trigger
            if st.button("➕ Create New Rule Signature", use_container_width=True, key="create_rule_trigger_btn"):
                # Clear active selection to flag new editor body
                st.session_state.selected_rule_id = -1
                st.session_state.ai_rule_helper_response = None
                st.session_state.rule_test_metrics = None
                st.session_state.rule_simulation_metrics = None
                st.rerun()

            st.markdown("<br/>", unsafe_allow_html=True)

            # Render rules list
            for r in rules_list:
                rid = r["id"]
                is_active = (rid == st.session_state.selected_rule_id)
                border_glow = "border: 1px solid var(--primary); box-shadow: 0 0 10px rgba(59,130,246,0.15);" if is_active else "border: 1px solid var(--border-color);"
                
                s_level = r["severity"].upper()
                s_color = "var(--danger)" if s_level == "HIGH" else ("var(--warning)" if s_level == "MEDIUM" else "var(--success)")
                
                status_style = "color:var(--success);" if r["status"] == "Enabled" else "color:var(--muted);"
                
                st.markdown(
                    f"""
                    <div style="{border_glow} background-color: var(--card-bg); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.62rem; font-weight:700; color:var(--text-secondary);">v{r['version']} | {r['category']}</span>
                        <span style="font-size:0.6rem; font-weight:700; color:{s_color}; border:1px solid {s_color}; border-radius:3px; padding:0.05rem 0.25rem;">
                          {s_level}
                        </span>
                      </div>
                      <div style="font-size:0.84rem; font-weight:700; color:var(--text-primary); margin: 0.35rem 0;">{r["name"]}</div>
                      <div style="display:flex; justify-content:space-between; font-size:0.72rem; margin-top:0.5rem;">
                        <span style="{status_style}">Status: <b>{r["status"]}</b></span>
                        <span style="color:var(--muted);">By: <b>{r["author"]}</b></span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button(f"Configure {r['name']}", key=f"select_rule_btn_{rid}", use_container_width=True):
                    st.session_state.selected_rule_id = rid
                    st.session_state.ai_rule_helper_response = None
                    st.session_state.rule_test_metrics = None
                    st.session_state.rule_simulation_metrics = None
                    st.rerun()

    # Center Column (70%): Rule Editor
    with col_center:
        st.markdown('<h3 class="section-title">Rule Configuration Editor</h3>', unsafe_allow_html=True)
        
        # Load rule details
        sel_rid = st.session_state.selected_rule_id
        rule_details = None
        
        if sel_rid != -1:
            try:
                r_det = requests.get(f"{api_base}/api/rules/{sel_rid}", headers=headers, timeout=10, verify=False)
                if r_det.status_code == 200:
                    rule_details = r_det.json()
                else:
                    st.error(f"Failed to fetch rule details: {r_det.status_code}")
            except Exception as e:
                st.error(f"Error loading rule details: {str(e)}")

        with st.container(border=True):
            if sel_rid == -1:
                # Mode: Create New Rule
                st.markdown("#### 🆕 Create New Custom Rule")
                
                e_name = st.text_input("Rule Name", placeholder="e.g. Ingress SSH Attack Tracker")
                e_desc = st.text_area("Rule Description", placeholder="Flags repeated SSH connections from anomalous external nodes...")
                
                ed_col1, ed_col2, ed_col3 = st.columns(3)
                with ed_col1:
                    e_cat = st.selectbox(
                        "Category",
                        options=["Brute Force", "Port Scan", "Credential Stuffing", "Lateral Movement", "Privilege Escalation", "Suspicious PowerShell", "Public Exploit", "Beaconing", "Impossible Travel", "Custom Rules"]
                    )
                with ed_col2:
                    e_sev = st.selectbox("Severity", options=["High", "Medium", "Low"])
                with ed_col3:
                    e_mitre = st.selectbox(
                        "MITRE Tactic",
                        options=["T1110 - Brute Force", "T1046 - Network Scanning", "T1190 - Exploit Public-Facing Application", "T1210 - Exploitation of Remote Services", "T1059 - Command and Scripting Interpreter"]
                    )

                e_logic = st.text_area("Detection Query Logic (JSON Criteria)", value='{"event_type": "ssh_bruteforce"}')
                
                ed_k1, ed_k2 = st.columns(2)
                with ed_k1:
                    e_threshold = st.number_input("Threshold", min_value=1, max_value=1000, value=5)
                with ed_k2:
                    e_time_window = st.number_input("Time Window (sec)", min_value=5, max_value=86400, value=60)
                    
                e_response = st.text_area("Recommended Response Actions", placeholder="Block source subnet interfaces via edge firewalls...")
                e_tags = st.text_input("Rule Tags (comma separated)", placeholder="SSH, Bruteforce, Custom")

                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    if st.button("✅ Validate Rule", use_container_width=True, key="validate_new_rule_btn"):
                        v_payload = {
                            "name": e_name, "description": e_desc, "severity": e_sev,
                            "category": e_cat, "mitre_technique": e_mitre,
                            "detection_logic": e_logic, "threshold": e_threshold, "time_window": e_time_window
                        }
                        try:
                            r_val = requests.post(f"{api_base}/api/rules/validate", json=v_payload, headers=headers, timeout=10, verify=False)
                            if r_val.status_code == 200:
                                val_result = r_val.json()
                                if val_result["valid"]:
                                    st.success("Rule validation passed — no errors detected.")
                                else:
                                    render_validation_errors(val_result["errors"])
                                    render_ai_validation_assistant(v_payload, val_result["errors"])
                        except Exception as e:
                            st.error(f"Validation error: {str(e)}")
                with v_col2:
                    if st.button("💾 Save Rule to Signature Core", use_container_width=True, key="save_new_rule_btn"):
                        payload = {
                            "name": e_name,
                            "description": e_desc,
                            "severity": e_sev,
                            "category": e_cat,
                            "mitre_technique": e_mitre,
                            "detection_logic": e_logic,
                            "threshold": e_threshold,
                            "time_window": e_time_window,
                            "recommended_response": e_response,
                            "tags": e_tags
                        }
                        try:
                            r_save = requests.post(f"{api_base}/api/rules", json=payload, headers=headers, timeout=10, verify=False)
                            if r_save.status_code == 200:
                                st.session_state.selected_rule_id = r_save.json()["id"]
                                st.toast("Detection rule saved successfully!", icon="✓")
                                st.rerun()
                            else:
                                st.error(f"Failed to save rule: {r_save.text}")
                        except Exception as e:
                            st.error(f"Error saving: {str(e)}")

            elif rule_details:
                # Mode: Edit Existing Rule
                st.markdown(f"#### ⚙️ Edit Rule: {rule_details['name']} (v{rule_details['version']})")
                
                e_name = st.text_input("Rule Name", value=rule_details["name"])
                e_desc = st.text_area("Rule Description", value=rule_details["description"])
                
                ed_col1, ed_col2, ed_col3 = st.columns(3)
                with ed_col1:
                    e_cat = st.selectbox(
                        "Category",
                        options=["Brute Force", "Port Scan", "Credential Stuffing", "Lateral Movement", "Privilege Escalation", "Suspicious PowerShell", "Public Exploit", "Beaconing", "Impossible Travel", "Custom Rules"],
                        index=["Brute Force", "Port Scan", "Credential Stuffing", "Lateral Movement", "Privilege Escalation", "Suspicious PowerShell", "Public Exploit", "Beaconing", "Impossible Travel", "Custom Rules"].index(rule_details["category"])
                    )
                with ed_col2:
                    e_sev = st.selectbox(
                        "Severity",
                        options=["High", "Medium", "Low"],
                        index=["High", "Medium", "Low"].index(rule_details["severity"])
                    )
                with ed_col3:
                    mitre_opts = ["T1110 - Brute Force", "T1046 - Network Scanning", "T1190 - Exploit Public-Facing Application", "T1210 - Exploitation of Remote Services", "T1059 - Command and Scripting Interpreter"]
                    e_mitre = st.selectbox(
                        "MITRE Tactic",
                        options=mitre_opts,
                        index=mitre_opts.index(rule_details["mitre_technique"]) if rule_details["mitre_technique"] in mitre_opts else 0
                    )

                e_logic = st.text_area("Detection Query Logic (JSON Criteria)", value=rule_details["detection_logic"])
                
                ed_k1, ed_k2 = st.columns(2)
                with ed_k1:
                    e_threshold = st.number_input("Threshold", min_value=1, max_value=1000, value=int(rule_details["threshold"]))
                with ed_k2:
                    e_time_window = st.number_input("Time Window (sec)", min_value=5, max_value=86400, value=int(rule_details["time_window"]))
                    
                e_response = st.text_area("Recommended Response Actions", value=rule_details["recommended_response"] or "")
                e_tags = st.text_input("Rule Tags (comma separated)", value=rule_details["tags"] or "")
                
                # Rule status and changelog
                ed_c1, ed_c2 = st.columns(2)
                with ed_c1:
                    e_status = st.selectbox(
                        "Rule Status",
                        options=["Enabled", "Disabled"],
                        index=["Enabled", "Disabled"].index(rule_details["status"])
                    )
                with ed_c2:
                    e_changelog = st.text_input("Revision Changelog", value="Update configuration attributes", placeholder="What changed in this version...")

                # Action Buttons
                st.markdown("<br/>", unsafe_allow_html=True)
                act_col1, act_col2, act_col3 = st.columns(3)
                
                with act_col1:
                    if st.button("💾 Save Updates (New Version)", use_container_width=True, key="update_rule_btn"):
                        payload = {
                            "name": e_name,
                            "description": e_desc,
                            "status": e_status,
                            "severity": e_sev,
                            "category": e_cat,
                            "mitre_technique": e_mitre,
                            "detection_logic": e_logic,
                            "threshold": e_threshold,
                            "time_window": e_time_window,
                            "recommended_response": e_response,
                            "tags": e_tags,
                            "changelog": e_changelog
                        }
                        try:
                            r_up = requests.put(f"{api_base}/api/rules/{sel_rid}", json=payload, headers=headers, timeout=10, verify=False)
                            if r_up.status_code == 200:
                                st.toast("Detection rule updated successfully!", icon="✓")
                                st.rerun()
                            else:
                                st.error(f"Failed to update: {r_up.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with act_col2:
                    if st.button("🗑️ Delete Rule", use_container_width=True, key="delete_rule_btn"):
                        try:
                            r_del = requests.delete(f"{api_base}/api/rules/{sel_rid}", headers=headers, timeout=10, verify=False)
                            if r_del.status_code == 200:
                                st.session_state.selected_rule_id = 1
                                st.toast("Detection rule deleted.", icon="✓")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                with act_col3:
                    # Export options
                    export_fmt = st.selectbox(
                        "Export Rule Format",
                        options=["JSON", "YAML", "Markdown"],
                        key="export_fmt_select"
                    )
                    
                    if export_fmt == "JSON":
                        e_data = json.dumps(rule_details, indent=2)
                        mime_t = "application/json"
                        file_ext = "json"
                    elif export_fmt == "YAML":
                        # Standard mock yaml converter
                        e_data = (
                            f"id: {rule_details['id']}\n"
                            f"name: {rule_details['name']}\n"
                            f"description: {rule_details['description']}\n"
                            f"severity: {rule_details['severity']}\n"
                            f"logic: {rule_details['detection_logic']}\n"
                        )
                        mime_t = "text/yaml"
                        file_ext = "yaml"
                    else:
                        e_data = (
                            f"# Detection Rule: {rule_details['name']}\n"
                            f"- **Category:** {rule_details['category']}\n"
                            f"- **Severity:** {rule_details['severity']}\n"
                            f"- **Logic:** `{rule_details['detection_logic']}`\n"
                        )
                        mime_t = "text/markdown"
                        file_ext = "md"
                        
                    st.download_button(
                        label=f"📥 Download {export_fmt}",
                        data=e_data,
                        file_name=f"dcoy_rule_{sel_rid}.{file_ext}",
                        mime=mime_t,
                        use_container_width=True
                    )

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Rule Testing & dry-run simulation
                st.markdown("#### 🧪 Rule Testing & dry-run Simulation")
                
                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    # Test Rule
                    if st.button("🏃 Run Rule test (Active Telemetry)", use_container_width=True, key="test_rule_btn"):
                        try:
                            r_test = requests.post(f"{api_base}/api/rules/{sel_rid}/test", headers=headers, timeout=10, verify=False)
                            if r_test.status_code == 200:
                                st.session_state.rule_test_metrics = r_test.json()
                                st.toast("Rule test finished!", icon="✓")
                            else:
                                st.error(f"Failed: {r_test.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            
                with t_col2:
                    # Simulation
                    if st.button("📋 Run dry-run Simulation", use_container_width=True, key="simulate_rule_btn"):
                        try:
                            r_sim = requests.post(f"{api_base}/api/rules/test-custom", json={"detection_logic": e_logic}, headers=headers, timeout=10, verify=False)
                            if r_sim.status_code == 200:
                                st.session_state.rule_simulation_metrics = r_sim.json()
                                st.toast("Simulation finished!", icon="✓")
                            else:
                                st.error(f"Failed: {r_sim.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("✅ Validate Rule Config", use_container_width=True, key="validate_edit_rule_btn"):
                        v_payload = {
                            "name": e_name, "description": e_desc, "severity": e_sev,
                            "category": e_cat, "mitre_technique": e_mitre,
                            "detection_logic": e_logic, "threshold": e_threshold, "time_window": e_time_window
                        }
                        try:
                            r_val = requests.post(f"{api_base}/api/rules/validate", json=v_payload, headers=headers, timeout=10, verify=False)
                            if r_val.status_code == 200:
                                val_result = r_val.json()
                                if val_result["valid"]:
                                    st.success("Rule validation passed — no errors detected.")
                                else:
                                    render_validation_errors(val_result["errors"])
                                    render_ai_validation_assistant(v_payload, val_result["errors"])
                        except Exception as e:
                            st.error(f"Validation error: {str(e)}")
                with b_col2:
                    if st.button("⚡ Benchmark Rule Performance", use_container_width=True, key="benchmark_rule_btn"):
                        try:
                            r_bench = requests.post(f"{api_base}/api/rules/{sel_rid}/benchmark", headers=headers, timeout=15, verify=False)
                            if r_bench.status_code == 200:
                                bench = r_bench.json()
                                st.info(
                                    f"**[BENCHMARK RESULTS]**\n\n"
                                    f"- **Events Scanned:** `{bench['total_events_scanned']}`\n"
                                    f"- **Matching Events:** `{bench['matching_events']}`\n"
                                    f"- **Execution Time:** `{bench['execution_time_ms']:.2f}ms`\n"
                                    f"- **Detection Coverage:** `{bench['detection_coverage'] * 100:.1f}%`\n"
                                    f"- **Production Impact:** `{bench['estimated_production_impact']}`\n"
                                    f"- **Cache State:** `{bench['cache_state']}`"
                                )
                            else:
                                st.error(f"Benchmark failed: {r_bench.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                # Render Rule test Results
                if st.session_state.rule_test_metrics:
                    m = st.session_state.rule_test_metrics
                    st.info(
                        f"**[RULE TEST METRICS]**\n\n"
                        f"- **Matched Events:** `{m['matched_count']}`\n"
                        f"- **False Positive Estimate:** `{m['false_positive_estimate'] * 100:.1f}%`\n"
                        f"- **Detection Coverage:** `{m['detection_coverage'] * 100:.1f}%`\n"
                        f"- **Execution Time:** `{m['execution_time_ms']:.2f}ms`"
                    )
                    
                    if m.get("matched_events"):
                        with st.expander("Show Matched Events Detail"):
                            for ev in m["matched_events"]:
                                st.markdown(f"- **IP:** {ev['ip']} | Timestamp: {ev['timestamp']} | Risk Score: {ev['risk_score']}")
                                
                # Render Simulation Results
                if st.session_state.rule_simulation_metrics:
                    m = st.session_state.rule_simulation_metrics
                    st.success(
                        f"**[DRY-RUN SIMULATION RESULTS]**\n\n"
                        f"- **Would Trigger:** `{m['would_trigger']}`\n"
                        f"- **Would Ignore:** `{not m['would_trigger']}`\n"
                        f"- **Affected Events:** `{m['affected_events_count']}`\n"
                        f"- **Confidence:** `{m['confidence']}`"
                    )

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # AI Rule Assistant
                st.markdown("#### 🧠 Copilot AI Rule Assistant")
                
                ai_col1, ai_col2, ai_col3 = st.columns(3)
                with ai_col1:
                    if st.button("🧠 Explain Rule", use_container_width=True, key="ai_explain_rule_btn"):
                        st.session_state.ai_rule_helper_response = (
                            f"**[AI RULE ANALYSIS: {rule_details['name']}]**\n\n"
                            f"This rule evaluates log records for key matching criteria: `{rule_details['detection_logic']}`. "
                            f"It acts as a pattern signature mapping specifically to technique {rule_details['mitre_technique']}."
                        )
                with ai_col2:
                    if st.button("📈 Optimize Thresholds", use_container_width=True, key="ai_optimize_threshold_btn"):
                        st.session_state.ai_rule_helper_response = (
                            f"**[AI THRESHOLD OPTIMIZATION]**\n\n"
                            f"Based on telemetry volume, we suggest adjusting "
                            f"the threshold from `{rule_details['threshold']}` to `8` and the time window to `120` seconds "
                            f"to reduce false positive alert triggers by an estimated 12%."
                        )
                with ai_col3:
                    if st.button("🗺️ Suggest MITRE mapping", use_container_width=True, key="ai_suggest_mitre_btn"):
                        st.session_state.ai_rule_helper_response = (
                            f"**[AI MITRE SUGGESTION]**\n\n"
                            f"The logic matches initial access infiltration behaviors. We recommend mapping this signature to: "
                            f"**T1190 (Exploit Public-Facing Application)** or **T1110 (Brute Force)**."
                        )

                if st.session_state.ai_rule_helper_response:
                    from dashboard.components.widget_variants import render_ai_markdown_widget
                    render_ai_markdown_widget(
                        title="Copilot AI Rule Assistant",
                        markdown_text=st.session_state.ai_rule_helper_response,
                        default_subtitle="Detection Logic Optimization",
                        key="ai_rule_helper_widget"
                    )
                    if st.button("Dismiss AI Suggestion", key="dismiss_ai_helper_btn"):
                        st.session_state.ai_rule_helper_response = None
                        st.rerun()

                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

                # Version History Revisions
                st.markdown("#### ⏳ Rule Configuration Version history")
                if rule_details.get("revisions"):
                    for rev in rule_details["revisions"]:
                        rev_dt = rev["created_at"].replace("T", " ").replace("Z", "")[:19]
                        st.markdown(
                            f"""
                            <div style="background-color: var(--bg-secondary); padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--border-color); margin-bottom: 0.5rem;">
                              <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:var(--secondary); margin-bottom:0.25rem;">
                                <b>Version: {rev['version']}</b>
                                <span>{rev_dt} | Author: {rev['author']}</span>
                              </div>
                              <div style="font-size:0.8rem; color:var(--text-primary);">Changelog: <i>{rev['changelog']}</i></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        if st.button(f"Revert to Version {rev['version']}", key=f"revert_version_btn_{rev['version']}", use_container_width=True):
                            try:
                                r_revert = requests.post(f"{api_base}/api/rules/{sel_rid}/revert/{rev['version']}", headers=headers, timeout=10, verify=False)
                                if r_revert.status_code == 200:
                                    st.toast(f"Reverted to version {rev['version']}!", icon="✓")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to revert: {r_revert.text}")
                            except Exception as e:
                                st.error(f"Error reverting: {str(e)}")
                else:
                    st.info("No past configuration revisions logged for this rule.")
            else:
                st.warning("Select a detection rule from the Rule Explorer or click 'Create New Rule Signature' to begin.")
