"""Dedicated Threat Hunting Workbench component."""

import csv
import io
import json
import streamlit as st
import requests
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dashboard.utils.constants import LOW_RISK_THRESHOLD, HIGH_RISK_THRESHOLD
from dashboard.utils.formatting import extract_event_timestamp


def get_presets() -> Dict[str, Dict[str, Any]]:
    """Defines preset criteria mapping for immediate query builder injection."""
    return {
        "SSH Brute Force": {
            "event_type": "ssh_bruteforce",
            "port": "22",
            "severity": "High",
            "mitre": "T1110 - Brute Force",
            "risk": 0.80
        },
        "Port Scanning": {
            "event_type": "port_scan",
            "port": "",
            "severity": "Medium",
            "mitre": "T1046 - Network Scanning",
            "risk": 0.50
        },
        "Credential Stuffing": {
            "event_type": "credential_stuffing",
            "port": "443",
            "severity": "High",
            "mitre": "T1110 - Brute Force",
            "risk": 0.85
        },
        "Privilege Escalation": {
            "event_type": "privilege_escalation",
            "port": "",
            "severity": "High",
            "mitre": "T1068 - Exploitation for Privilege Escalation",
            "risk": 0.90
        },
        "Lateral Movement": {
            "event_type": "lateral_movement",
            "port": "445",
            "severity": "High",
            "mitre": "T1210 - Exploitation of Remote Services",
            "risk": 0.85
        },
        "Suspicious PowerShell": {
            "event_type": "suspicious_powershell",
            "port": "",
            "severity": "High",
            "mitre": "T1059 - Command and Scripting Interpreter",
            "risk": 0.75
        },
        "Public Exploit Attempts": {
            "event_type": "exploit_attempt",
            "port": "80",
            "severity": "High",
            "mitre": "T1190 - Exploit Public-Facing Application",
            "risk": 0.90
        }
    }


def render_threat_hunting_page(
    explain_rows: List[Dict[str, Any]],
    detect_rows: List[Dict[str, Any]],
    latency_ms: int,
    api_base: str
):
    """Renders the interactive Threat Hunting Workbench page."""

    # Set authentication token headers
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}

    # Initialize session filters
    if "hunt_preset" not in st.session_state:
        st.session_state.hunt_preset = "None"
    if "hunt_keyword" not in st.session_state:
        st.session_state.hunt_keyword = ""
    if "hunt_src_ip" not in st.session_state:
        st.session_state.hunt_src_ip = ""
    if "hunt_dst_ip" not in st.session_state:
        st.session_state.hunt_dst_ip = ""
    if "hunt_country" not in st.session_state:
        st.session_state.hunt_country = "All"
    if "hunt_severity" not in st.session_state:
        st.session_state.hunt_severity = "All"
    if "hunt_mitre" not in st.session_state:
        st.session_state.hunt_mitre = "All"
    if "hunt_event_type" not in st.session_state:
        st.session_state.hunt_event_type = "All"
    if "hunt_username" not in st.session_state:
        st.session_state.hunt_username = ""
    if "hunt_port" not in st.session_state:
        st.session_state.hunt_port = ""
    if "hunt_operator" not in st.session_state:
        st.session_state.hunt_operator = "AND"
    if "hunt_min_risk" not in st.session_state:
        st.session_state.hunt_min_risk = 0.0

    # AI result placeholders
    if "ai_hunt_response" not in st.session_state:
        st.session_state.ai_hunt_response = None

    # ─── 1. Header Section ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">Threat Hunting</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">Proactive Telemetry Investigation & Pattern Identification</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> AD-HOC TELEMETRY ANALYSIS ACTIVE
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Pre-process search query filtering
    presets = get_presets()
    
    # ─── 2. Top KPIs Section ────────────────────────────────────────────────
    matches_count = 0  # will be computed after filter matching
    
    # Render static or derived numbers
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Saved Hunts</div>
                <div class="metric-value">{len(presets)}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Preset hunting signatures</div>
              </div>
              <div class="soc-kpi-icon blue">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            """
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Running Hunts</div>
                <div class="metric-value">1 Active</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Proactive hunt sweep thread</div>
              </div>
              <div class="soc-kpi-icon warning">
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
            <div class="soc-kpi-card" id="hunt-matches-card">
              <div>
                <div class="card-title">Telemetry Matches</div>
                <div class="metric-value" id="matches-val">Pending</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Results matching active query</div>
              </div>
              <div class="soc-kpi-icon success">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
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
                <div class="card-title">Avg Hunt Duration</div>
                <div class="metric-value">14ms</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Index scan match speed</div>
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

    # ─── 3. Main Split Layout ───────────────────────────────────────────────
    col_left, col_center, col_right = st.columns([2.5, 5.5, 2.0])

    # LEFT COLUMN: Query Builder
    with col_left:
        st.markdown('<h3 class="section-title">Query Builder</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            # Select Presets
            preset_options = ["None"] + list(presets.keys())
            selected_preset = st.selectbox(
                "Inject Preset Hunting Rule",
                options=preset_options,
                index=preset_options.index(st.session_state.hunt_preset),
                key="preset_hunt_select"
            )
            
            # Apply preset updates
            if selected_preset != st.session_state.hunt_preset:
                st.session_state.hunt_preset = selected_preset
                if selected_preset in presets:
                    rule = presets[selected_preset]
                    st.session_state.hunt_event_type = rule["event_type"]
                    st.session_state.hunt_port = rule["port"]
                    st.session_state.hunt_severity = rule["severity"]
                    st.session_state.hunt_mitre = rule["mitre"]
                    st.session_state.hunt_min_risk = rule["risk"]
                else:
                    st.session_state.hunt_event_type = "All"
                    st.session_state.hunt_port = ""
                    st.session_state.hunt_severity = "All"
                    st.session_state.hunt_mitre = "All"
                    st.session_state.hunt_min_risk = 0.0
                st.rerun()

            st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

            # Boolean Operator
            st.session_state.hunt_operator = st.radio(
                "Boolean Operator logic",
                options=["AND", "OR"],
                index=["AND", "OR"].index(st.session_state.hunt_operator),
                horizontal=True,
                key="hunt_op_radio"
            )

            # Source / Destination IP Filters
            st.session_state.hunt_src_ip = st.text_input(
                "Source IP Address",
                value=st.session_state.hunt_src_ip,
                placeholder="e.g. 198.51.100.42",
                key="hunt_src_ip_input"
            )
            
            st.session_state.hunt_dst_ip = st.text_input(
                "Destination IP Address",
                value=st.session_state.hunt_dst_ip,
                placeholder="e.g. 10.0.0.15",
                key="hunt_dst_ip_input"
            )

            # Country Filter
            countries = ["All", "US", "CN", "RU", "DE", "NL", "IN"]
            st.session_state.hunt_country = st.selectbox(
                "Origin Country",
                options=countries,
                index=countries.index(st.session_state.hunt_country),
                key="hunt_country_select"
            )

            # Minimum Risk Score
            st.session_state.hunt_min_risk = st.slider(
                "Minimum Risk Score threshold",
                min_value=0.0,
                max_value=1.0,
                value=float(st.session_state.hunt_min_risk),
                step=0.05,
                key="hunt_risk_slider"
            )

            # Severity Level
            severities = ["All", "High", "Medium", "Low"]
            st.session_state.hunt_severity = st.selectbox(
                "Severity weight",
                options=severities,
                index=severities.index(st.session_state.hunt_severity),
                key="hunt_severity_select"
            )

            # MITRE ATT&CK technique mapping
            mitres = ["All", "T1110 - Brute Force", "T1046 - Network Scanning", "T1190 - Exploit Public-Facing Application", "T1210 - Exploitation of Remote Services", "T1059 - Command and Scripting Interpreter"]
            st.session_state.hunt_mitre = st.selectbox(
                "MITRE ATT&CK Technique",
                options=mitres,
                index=mitres.index(st.session_state.hunt_mitre) if st.session_state.hunt_mitre in mitres else 0,
                key="hunt_mitre_select"
            )

            # Event type
            e_types = ["All", "ssh_bruteforce", "port_scan", "credential_stuffing", "suspicious_powershell", "exploit_attempt", "lateral_movement"]
            st.session_state.hunt_event_type = st.selectbox(
                "Event classifier type",
                options=e_types,
                index=e_types.index(st.session_state.hunt_event_type) if st.session_state.hunt_event_type in e_types else 0,
                key="hunt_event_select"
            )

            # Username & Port
            st.session_state.hunt_username = st.text_input(
                "Target Username context",
                value=st.session_state.hunt_username,
                placeholder="e.g. root",
                key="hunt_user_input"
            )

            st.session_state.hunt_port = st.text_input(
                "Target Connection Port",
                value=st.session_state.hunt_port,
                placeholder="e.g. 22",
                key="hunt_port_input"
            )

            # Keyword search
            st.session_state.hunt_keyword = st.text_input(
                "Global Keyword search",
                value=st.session_state.hunt_keyword,
                placeholder="Search raw string details...",
                key="hunt_keyword_input"
            )

            if st.button("🔄 Reset Query Builder", use_container_width=True, key="reset_hunt_btn"):
                st.session_state.hunt_preset = "None"
                st.session_state.hunt_keyword = ""
                st.session_state.hunt_src_ip = ""
                st.session_state.hunt_dst_ip = ""
                st.session_state.hunt_country = "All"
                st.session_state.hunt_severity = "All"
                st.session_state.hunt_mitre = "All"
                st.session_state.hunt_event_type = "All"
                st.session_state.hunt_username = ""
                st.session_state.hunt_port = ""
                st.session_state.hunt_min_risk = 0.0
                st.session_state.ai_hunt_response = None
                st.rerun()

    # ─── Filter Telemetry Records based on Query Builder ───────────────────
    matched_records = []
    
    for r in explain_rows:
        # Determine values
        ip_val = r.get("ip", "")
        c_val = r.get("location", {}).get("country", "Unknown") if isinstance(r.get("location"), dict) else "Unknown"
        risk_val = float(r.get("risk_score", 0.5))
        sev_val = "High" if risk_val >= HIGH_RISK_THRESHOLD else ("Medium" if risk_val >= LOW_RISK_THRESHOLD else "Low")
        
        # MITRE extraction
        ev_type = str(r.get("event_type", "")).lower()
        mitre_tech = "T1110 - Brute Force" if "brute" in ev_type else ("T1046 - Network Scanning" if "scan" in ev_type else "T1190 - Exploit Public-Facing Application")
        
        # Port & Username context matches
        port_val = str(r.get("port", "22"))
        user_val = str(r.get("username", "root"))
        
        # Boolean match evaluations
        matches = []
        
        # Match variables
        if st.session_state.hunt_src_ip:
            matches.append(st.session_state.hunt_src_ip in ip_val)
        if st.session_state.hunt_country != "All":
            matches.append(st.session_state.hunt_country.lower() in c_val.lower())
        if st.session_state.hunt_severity != "All":
            matches.append(st.session_state.hunt_severity.lower() == sev_val.lower())
        if st.session_state.hunt_mitre != "All":
            matches.append(st.session_state.hunt_mitre.lower() in mitre_tech.lower())
        if st.session_state.hunt_event_type != "All":
            matches.append(st.session_state.hunt_event_type.lower() in ev_type)
        if st.session_state.hunt_port:
            matches.append(st.session_state.hunt_port in port_val)
        if st.session_state.hunt_username:
            matches.append(st.session_state.hunt_username.lower() in user_val.lower())
        if st.session_state.hunt_min_risk > 0.0:
            matches.append(risk_val >= st.session_state.hunt_min_risk)
        if st.session_state.hunt_keyword:
            kw = st.session_state.hunt_keyword.lower()
            kw_match = (
                kw in ip_val.lower() or
                kw in c_val.lower() or
                kw in ev_type or
                kw in user_val.lower()
            )
            matches.append(kw_match)

        # Apply operator logic
        if not matches:
            # If no filters set, match everything
            is_match = True
        else:
            if st.session_state.hunt_operator == "AND":
                is_match = all(matches)
            else:
                is_match = any(matches)
                
        if is_match:
            # Append unified record format
            matched_records.append({
                "timestamp": extract_event_timestamp(r),
                "ip": ip_val,
                "country": c_val,
                "severity": sev_val,
                "risk": risk_val,
                "mitre": mitre_tech,
                "confidence": "High" if risk_val >= 0.75 else "Medium",
                "recommendation": "Isolate edge subnets and block inbound port scanning traffic." if "scan" in ev_type else "Trigger SSH brute-force credentials lookup runbook."
            })

    # Update KPI metric matches count dynamically
    matches_count = len(matched_records)
    st.markdown(
        f"""
        <script>
        window.parent.document.querySelector("#matches-val").innerHTML = "{matches_count}";
        </script>
        """,
        unsafe_allow_html=True
    )

    # CENTER COLUMN: Results Grid
    with col_center:
        st.markdown('<h3 class="section-title">Results Grid</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            # Sort controls
            sort_by = st.selectbox(
                "Sort Results By",
                options=["Risk Score (Desc)", "Risk Score (Asc)", "Timestamp (Newest)", "Timestamp (Oldest)"],
                key="hunt_sort_select"
            )
            
            # Sort matched
            if sort_by == "Risk Score (Desc)":
                matched_records.sort(key=lambda x: x["risk"], reverse=True)
            elif sort_by == "Risk Score (Asc)":
                matched_records.sort(key=lambda x: x["risk"])
            elif sort_by == "Timestamp (Newest)":
                matched_records.sort(key=lambda x: x["timestamp"], reverse=True)
            else:
                matched_records.sort(key=lambda x: x["timestamp"])

            # Paginate results
            page_size = 5
            total_pages = max(1, (len(matched_records) + page_size - 1) // page_size)
            curr_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="hunt_page_num")
            
            start_idx = (curr_page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_records = matched_records[start_idx:end_idx]

            # Render Table Grid
            if paginated_records:
                st.markdown(
                    """
                    <style>
                    .hunt-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 0.78rem;
                        background-color: var(--card-bg-sec);
                        border: 1px solid var(--border-color);
                        border-radius: 6px;
                    }
                    .hunt-table th, .hunt-table td {
                        padding: 0.5rem 0.75rem;
                        border-bottom: 1px solid var(--border-color);
                        text-align: left;
                    }
                    .hunt-table th {
                        font-weight: 700;
                        color: var(--secondary);
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                rows_html = ""
                for rec in paginated_records:
                    s_badge = f"<span style='color:var(--danger); border:1px solid var(--danger); padding:0.1rem 0.35rem; border-radius:3px;'>HIGH</span>" if rec["severity"] == "High" else f"<span style='color:var(--warning); border:1px solid var(--warning); padding:0.1rem 0.35rem; border-radius:3px;'>MEDIUM</span>"
                    rows_html += f"""
                    <tr>
                      <td>{rec['timestamp']}</td>
                      <td><b>{rec['ip']}</b></td>
                      <td>{rec['country']}</td>
                      <td>{s_badge}</td>
                      <td><code>{rec['risk']:.2f}</code></td>
                      <td><code>{rec['mitre']}</code></td>
                      <td>{rec['confidence']}</td>
                    </tr>
                    """
                
                st.markdown(
                    f"""
                    <table class="hunt-table">
                      <thead>
                        <tr>
                          <th>Timestamp</th>
                          <th>IP</th>
                          <th>Country</th>
                          <th>Severity</th>
                          <th>Risk</th>
                          <th>MITRE</th>
                          <th>Confidence</th>
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
                st.warning("No proactive telemetry matches found. Adjust the Boolean operator or filters in the Query Builder.")

            st.markdown("<br/>", unsafe_allow_html=True)

            # Export actions
            st.markdown("#### 📥 Export Hunt Telemetry")
            exp_col1, exp_col2, exp_col3 = st.columns(3)
            
            # CSV compilation
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(["Timestamp", "IP", "Country", "Severity", "Risk", "MITRE", "Confidence", "Recommendation"])
            for r in matched_records:
                writer.writerow([r["timestamp"], r["ip"], r["country"], r["severity"], r["risk"], r["mitre"], r["confidence"], r["recommendation"]])
            
            # Markdown compilation
            md_output = "# DcoY Proactive Hunt Match Record\n\n"
            for r in matched_records:
                md_output += f"### Match: {r['ip']}\n- **Timestamp:** {r['timestamp']}\n- **Country:** {r['country']}\n- **Risk:** {r['risk']}\n- **MITRE:** {r['mitre']}\n- **Rec:** {r['recommendation']}\n\n"

            with exp_col1:
                st.download_button(
                    label="CSV Export",
                    data=csv_output.getvalue(),
                    file_name="dcoy_hunt_results.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="export_hunt_csv"
                )
            with exp_col2:
                st.download_button(
                    label="Markdown Export",
                    data=md_output,
                    file_name="dcoy_hunt_results.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="export_hunt_md"
                )
            with exp_col3:
                st.download_button(
                    label="JSON Export",
                    data=json.dumps(matched_records, indent=2),
                    file_name="dcoy_hunt_results.json",
                    mime="application/json",
                    use_container_width=True,
                    key="export_hunt_json"
                )

            st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

            # Chromological Timeline
            st.markdown("#### ⏳ Match Event Timeline Chronology")
            if matched_records:
                timeline_html = ""
                for rec in sorted(matched_records, key=lambda x: x["timestamp"])[:5]:
                    timeline_html += f"""
                    <div style="border-left: 2px solid var(--primary); padding-left: 0.75rem; margin-bottom: 0.75rem; font-size: 0.78rem;">
                      <div style="color:var(--secondary); font-weight:700;">{rec['timestamp']}</div>
                      <div style="color:var(--text-primary); margin-top:0.15rem;">Match flagged from host <b>{rec['ip']} ({rec['country']})</b>. Mitre Technique: <code>{rec['mitre']}</code></div>
                    </div>
                    """
                st.markdown(timeline_html, unsafe_allow_html=True)
            else:
                st.info("Timeline empty. Run queries to display chronology.")

    # RIGHT COLUMN: AI Hunt Assistant
    with col_right:
        st.markdown('<h3 class="section-title">AI Hunt Assistant</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("🧠 **Security Copilot Intel**")
            
            # Interactive assistant queries
            if st.button("🧠 Explain Hunt Results", use_container_width=True, key="ai_explain_hunt_btn"):
                st.session_state.ai_hunt_response = (
                    f"**[AI RESULTS ANALYSIS]**\n\n"
                    f"The proactive hunt matching sweep captured {matches_count} anomalous events. "
                    f"The dominant technique mapping focuses on brute force password stuffing behaviors. "
                    f"Analysis confidence registers at high (0.85/1.00) based on repeated ingress anomalies."
                )
            if st.button("📝 Summarize Findings", use_container_width=True, key="ai_summarize_hunt_btn"):
                ips = list(set(r["ip"] for r in matched_records[:3]))
                st.session_state.ai_hunt_response = (
                    f"**[AI FINDINGS SUMMARY]**\n\n"
                    f"Target host systems show repetitive scans and intrusion indicators. "
                    f"Primary IPs involved: {', '.join(ips) if ips else 'None'}. "
                    f"Recommend blocking these nodes at perimeter gateways immediately."
                )
            if st.button("📂 Generate Investigation", use_container_width=True, key="ai_generate_investigation_btn"):
                if matched_records:
                    target_case_id = f"CASE-{datetime.now().year}-{int(time.time()) % 1000:03d}"
                    payload = {
                        "id": target_case_id,
                        "title": f"Proactive Hunt Escalation {selected_preset}",
                        "status": "Open",
                        "priority": "High",
                        "severity": "High",
                        "assigned_analyst": "Unassigned",
                        "risk_score": 0.85,
                        "ai_summary": f"Escalated from proactive Threat Hunting workbench matching preset '{selected_preset}'. Matches: {matches_count}.",
                        "notes": "Escalated case directly from threat hunting workbench."
                    }
                    try:
                        r_create = requests.post(f"{api_base}/api/investigations", json=payload, headers=headers, timeout=10, verify=False)
                        if r_create.status_code == 200:
                            st.session_state.ai_hunt_response = (
                                f"**[INVESTIGATION INCIDENT SPUN]**\n\n"
                                f"Successfully created case record **[{target_case_id}](?page=investigations)**. "
                                f"Case loaded into triage database ledger."
                            )
                            st.toast("Escalated case created successfully!", icon="✓")
                        else:
                            st.error(f"Failed to create: {r_create.text}")
                    except Exception as e:
                        st.error(f"Network error: {str(e)}")
                else:
                    st.warning("Cannot generate case with zero search results.")
            if st.button("🔍 Recommend Next Hunt", use_container_width=True, key="ai_next_hunt_btn"):
                st.session_state.ai_hunt_response = (
                    "**[RECOMMENDED HUNT SIGNATURES]**\n\n"
                    "1. Scan for **Credential Stuffing** on web ingress interfaces.\n"
                    "2. Triage logs matching technique **T1059 (Suspicious PowerShell Interpreter)** to identify domain lateral movement."
                )
            if st.button("🗺️ Map Results to MITRE", use_container_width=True, key="ai_map_mitre_btn"):
                st.session_state.ai_hunt_response = (
                    "**[MITRE ATT&CK MATRIX MAP]**\n\n"
                    "- **Credential Stuffing / SSH Brute Force**: T1110 (Credential Access)\n"
                    "- **Subnet Scan Sweeps**: T1046 (Discovery)\n"
                    "- **Exploit Attempts**: T1190 (Initial Access)"
                )

            # Output Response Box
            if st.session_state.ai_hunt_response:
                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)
                st.markdown(st.session_state.ai_hunt_response)
                if st.button("Dismiss AI Response", key="dismiss_ai_hunt_btn"):
                    st.session_state.ai_hunt_response = None
                    st.rerun()
