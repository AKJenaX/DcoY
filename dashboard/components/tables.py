import streamlit as st
from typing import Any, Dict, List
from dashboard.utils.constants import LOW_RISK_THRESHOLD, HIGH_RISK_THRESHOLD
from dashboard.utils.formatting import extract_event_timestamp

def render_high_risk_threats(explain_rows: List[Dict[str, Any]]):
    """Renders the alert logs highlighting top-risk events."""
    st.markdown('<h3 class="section-title">Critical Threat Alerts</h3>', unsafe_allow_html=True)
    high_risk = [row for row in explain_rows if row.get("risk_level") == "high"]
    
    if high_risk:
        html = """
        <div class="soc-table-container" style="border:1px solid var(--border-color); border-radius: 14px; overflow:hidden;">
          <table class="soc-table">
            <thead>
              <tr>
                <th>Attacker IP</th>
                <th>Risk Score</th>
                <th>Attack Vector</th>
                <th>Deception Decoy</th>
                <th>Mitigation Action</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
        """
        for row in high_risk:
            score = row.get("risk_score", 0.0)
            score_color = "var(--danger)" if score >= HIGH_RISK_THRESHOLD else ("var(--warning)" if score >= LOW_RISK_THRESHOLD else "var(--success)")
            ip = row.get("ip", "unknown")
            avatar_char = ip.split(".")[-1][:2] if "." in ip else "IP"
            
            html += f"""
            <tr>
              <td><div class="avatar">{avatar_char}</div><b>{ip}</b></td>
              <td style="color:{score_color}; font-weight:700;">{score:.2f}</td>
              <td><span class="badge danger">{str(row.get('event_type', 'unknown')).replace('_', ' ')}</span></td>
              <td><span class="badge purple">{row.get('honeypot', 'none')}</span></td>
              <td style="font-size:0.75rem; color:var(--text-secondary);">{str(row.get('response_action_final', 'monitor')).replace('_', ' ')}</td>
              <td><span class="badge success">{row.get('response_status_final', 'active')}</span></td>
            </tr>
            """
        html += "</tbody></table></div>"
        
        with st.container(border=True):
            st.markdown(html, unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown(
                '<div class="empty-state" style="min-height: 120px;"><div class="empty-icon">◌</div><div class="widget-title">No high-risk threats</div><div class="widget-subtitle">The environment is currently clear of critical alerts.</div></div>',
                unsafe_allow_html=True
            )
    st.markdown("<br>", unsafe_allow_html=True)

def render_detailed_logs(detect_rows: List[Dict[str, Any]], explain_rows: List[Dict[str, Any]]):
    """Renders tabular log grids of all threats formatted with selected columns."""
    st.markdown('<h3 class="section-title">Live Terminal Logs Feed</h3>', unsafe_allow_html=True)
    log_source = explain_rows if explain_rows else detect_rows
    
    if log_source:
        # Search filter
        search_ip = st.text_input("Search logs by target IP:", key="logs_search_ip_input", placeholder="Type IP to filter...")
        filtered_source = log_source
        if search_ip.strip():
            filtered_source = [r for r in log_source if search_ip.strip() in r.get("ip", "")]
            
        if filtered_source:
            # Create a premium Terminal log window
            terminal_html = '<div class="terminal-window">'
            for idx, row in enumerate(filtered_source):
                level = row.get("risk_level", "low").upper()
                ip = row.get("ip", "unknown")
                details = row.get("details", {}) if isinstance(row.get("details"), dict) else {}
                timestamp = extract_event_timestamp(row)
                if "T" in timestamp:
                    timestamp = timestamp.split("T")[-1][:8]

                failed_logins = details.get("failed_logins", row.get("failed_logins", 0))
                port_attempts = details.get("port_attempts", row.get("port_attempts", 0))
                
                # Terminal description details
                if level == "HIGH":
                    text_detail = f"Brute force breach alert! Failed logins count: {failed_logins}. Port scans: {port_attempts}."
                elif level == "MEDIUM":
                    text_detail = f"Anomalous port traffic rate. Injected deception decoy: {row.get('honeypot', 'smtp')}."
                else:
                    text_detail = "Normal stream connection. Status allowed."
                    
                terminal_html += f"""
                <div class="terminal-line">
                  <span class="terminal-num">{idx + 1}</span>
                  <span class="terminal-time">[{timestamp}]</span>
                  <span class="terminal-ip">{ip}</span>
                  <span class="terminal-level {level.lower()}">{level}</span>
                  <span class="terminal-text">{text_detail}</span>
                </div>
                """
            terminal_html += '</div>'
            
            with st.container(border=True):
                st.markdown(terminal_html, unsafe_allow_html=True)
        else:
            with st.container(border=True):
                st.markdown('<p style="color:var(--text-secondary); text-align:center; margin:0;">No matching log rows found.</p>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state" style="min-height: 140px;"><div class="empty-icon">◌</div><div class="widget-title">No log data available</div><div class="widget-subtitle">Telemetry is currently unavailable or has not been ingested.</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def render_ai_explanations(explain_rows: List[Dict[str, Any]]):
    """Renders detail expander panels presenting natural language AI logic summaries."""
    st.markdown('<h3 class="section-title">Copilot Decision Feed</h3>', unsafe_allow_html=True)
    
    with st.container(border=True):
        if explain_rows:
            st.markdown('<div style="max-height: 380px; overflow-y: auto; padding-right: 0.5rem;">', unsafe_allow_html=True)
            for idx, row in enumerate(explain_rows):
                ip = row.get("ip", "Unknown")
                level = row.get("risk_level", "unknown").upper()
                with st.expander(f"DECISION FEED | IP: {ip} | RISK: {level}", expanded=False):
                    st.markdown(row.get("explanation", "No explanation available"))
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state" style="min-height: 140px;"><div class="empty-icon">◌</div><div class="widget-title">No AI explanations available</div><div class="widget-subtitle">The analysis layer does not currently have narrative evidence to display.</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
