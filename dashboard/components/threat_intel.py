"""Dedicated Threat Intelligence page view and data visualization components."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from typing import Any, Dict, List

from dashboard.utils.formatting import extract_event_timestamp
from dashboard.utils.constants import LOW_RISK_THRESHOLD, HIGH_RISK_THRESHOLD

def render_threat_intelligence_page(explain_rows: List[Dict[str, Any]], detect_rows: List[Dict[str, Any]], latency_ms: int):
    """Renders the comprehensive Threat Intelligence analysis layout."""
    
    # 1. Page Header Block
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">Threat Intelligence Center</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">MITRE ATT&CK technique tracking, active IP blocks, and chronological attack timelines.</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> INTEL LINK ACTIVE
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 9. Empty State Illustration Checks
    if not explain_rows:
        st.markdown(
            """
            <div style="text-align:center; padding:6rem 2rem; background-color: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
              <svg class="soc-icon" style="width:80px; height:80px; color:var(--success); margin-bottom:1.25rem;" viewBox="0 0 24 24">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <polyline points="9 11 11 13 15 9"/>
              </svg>
              <h2 style="color:var(--text-primary); font-size:1.5rem; font-weight:700; margin:0 0 0.5rem 0;">All Deception Subnets Secure</h2>
              <p style="color:var(--text-secondary); max-width:420px; margin:0 auto; font-size:0.9rem; line-height:1.5;">No malicious payloads or scans detected across internal honey subnets. Cyber defenses remain fully enforced.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Extract statistics
    total_alerts = len(explain_rows)
    high_risk_alerts = [r for r in explain_rows if r.get("risk_level") == "high"]
    high_risk_count = len(high_risk_alerts)
    risk_percentage = min(100, int((high_risk_count / max(1, total_alerts)) * 100 + 40)) if high_risk_count > 0 else 12

    # 10. Responsive layout grid splits
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # 6. Attack Timeline Graph using Plotly
        st.markdown('<h3 class="section-title">Attack Activity Timeline</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            df = pd.DataFrame(explain_rows)
            df["risk_score"] = pd.to_numeric(df.get("risk_score", pd.Series(dtype=float)), errors="coerce").fillna(0.5)
            df["ip"] = df.get("ip", pd.Series(dtype=str)).fillna("unknown")
            df["timestamp_clean"] = df.apply(extract_event_timestamp, axis=1)
            df["datetime"] = pd.to_datetime(df["timestamp_clean"], errors="coerce")
            df = df.sort_values("datetime")
            
            fig = go.Figure()
            
            # Draw linear progression trace
            fig.add_trace(go.Scatter(
                x=df["datetime"],
                y=df["risk_score"],
                mode='lines+markers',
                line=dict(width=2, color='rgba(59, 130, 246, 0.4)'),
                marker=dict(
                    size=10,
                    color=df["risk_score"],
                    colorscale=[[0.0, '#10B981'], [0.5, '#F59E0B'], [1.0, '#EF4444']],
                    line=dict(width=1, color='rgba(255,255,255,0.2)'),
                    showscale=False
                ),
                text=df["ip"],
                hovertemplate="<b>Attacker:</b> %{text}<br><b>Time:</b> %{x}<br><b>Risk Weight:</b> %{y:.2f}<extra></extra>"
            ))
            
            fig.update_layout(
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                font_color="#F9FAFB",
                margin={"r": 15, "t": 20, "l": 25, "b": 30},
                height=250,
                xaxis=dict(showgrid=False, tickfont={"size": 10, "color": "#9CA3AF"}),
                yaxis=dict(gridcolor="rgba(255,255,255,0.03)", range=[0, 1.1], tickfont={"size": 10, "color": "#9CA3AF"})
            )
            st.plotly_chart(fig, use_container_width=True, key="threat_intel_timeline_chart")

        # 4. Top Indicators of Compromise table
        st.markdown('<h3 class="section-title">Indicators of Compromise (IOC)</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            html = """
            <div class="soc-table-container">
              <table class="soc-table">
                <thead>
                  <tr>
                    <th>Threat IP Node</th>
                    <th>Risk Score</th>
                    <th>MITRE Mapping</th>
                    <th>Decoy Isolated</th>
                    <th>Enforcement Action</th>
                  </tr>
                </thead>
                <tbody>
            """
            for row in explain_rows:
                score = row.get("risk_score", 0.0)
                score_color = "var(--danger)" if score >= HIGH_RISK_THRESHOLD else ("var(--warning)" if score >= LOW_RISK_THRESHOLD else "var(--success)")
                ip = row.get("ip", "unknown")
                avatar_char = ip.split(".")[-1][:2] if "." in ip else "IP"
                
                # Mitre mapping display label
                mitre_tag = "T1110 (Brute Force)" if row.get("event_type") == "ssh_bruteforce" else "T1046 (Scan)"
                
                html += f"""
                <tr>
                  <td><div class="avatar">{avatar_char}</div><b>{ip}</b></td>
                  <td style="color:{score_color}; font-weight:700;">{score:.2f}</td>
                  <td><span class="badge cyan">{mitre_tag}</span></td>
                  <td><span class="badge purple">{row.get('honeypot', 'none')}</span></td>
                  <td><span class="badge success">{row.get('response_status_final', 'enforced')}</span></td>
                </tr>
                """
            html += "</tbody></table></div>"
            st.markdown(html, unsafe_allow_html=True)

    with col_right:
        # 2. Risk Score card
        st.markdown(
            f"""
            <div class="gauge-container" style="background-color: var(--card-bg); margin-top: 1rem;">
              <div class="card-title">Overall Risk Score</div>
              <div class="gauge-value">{risk_percentage} %</div>
              <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:0.4rem;">Deception network state: <b>HIGH THREAT</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 3. AI Threat Summary
        st.markdown('<h3 class="section-title">AI Threat Summary</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            if high_risk_alerts:
                summary_text = f"Anomalous ingress attempts detected from {len(high_risk_alerts)} critical actors. AI Defense Copilot has automatically mapped the credentials probes, isolated sessions inside localized honeypot instances, and deployed socket blocks to prevent lateral propagation."
            else:
                summary_text = "System telemetry reports nominal traffic rates. Active defenses are stable across all decoy nodes."
            st.markdown(f"<p style='font-size:0.85rem; line-height:1.6; color:var(--text-secondary);'>{summary_text}</p>", unsafe_allow_html=True)

        # 5. MITRE ATT&CK mapping cards
        st.markdown('<h3 class="section-title">MITRE ATT&CK Matrix</h3>', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-bottom:1rem;">
              <div style="padding:0.75rem; background-color:var(--card-bg); border-radius:12px; border:1px solid var(--border-color);">
                <span class="badge info" style="font-size:0.6rem; padding:0.1rem 0.35rem; margin-bottom:0.25rem;">CREDENTIAL ACCESS</span>
                <p style="font-size:0.8rem; font-weight:700; margin:0 0 0.15rem 0;">T1110 - Brute Force</p>
                <span style="font-size:0.65rem; color:var(--text-secondary);">SSH password guessing isolated on proxy decoy.</span>
              </div>
              <div style="padding:0.75rem; background-color:var(--card-bg); border-radius:12px; border:1px solid var(--border-color);">
                <span class="badge warning" style="font-size:0.6rem; padding:0.1rem 0.35rem; margin-bottom:0.25rem;">DISCOVERY</span>
                <p style="font-size:0.8rem; font-weight:700; margin:0 0 0.15rem 0;">T1046 - Port Scan</p>
                <span style="font-size:0.65rem; color:var(--text-secondary);">Automated network scanning identified and logged.</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 7. Intelligence Feed panel
    st.markdown('<h3 class="section-title">Intelligence Feed Logs</h3>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div style="max-height: 280px; overflow-y: auto;">', unsafe_allow_html=True)
        for idx, row in enumerate(explain_rows):
            ip = row.get("ip", "unknown")
            timestamp = extract_event_timestamp(row)
            if "T" in timestamp:
                timestamp = timestamp.split("T")[-1][:8]
            risk = row.get("risk_level", "low").upper()
            color = "var(--danger)" if risk == "HIGH" else "var(--warning)"
            
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:0.65rem 0.75rem; background-color:var(--bg-secondary); border-radius:8px; margin-bottom:0.5rem; border:1px solid var(--border-color);">
                  <div>
                    <span style="font-size:0.75rem; color:var(--text-secondary); margin-right:0.75rem;">[{timestamp}]</span>
                    <span style="font-size:0.85rem; font-weight:700; color:var(--text-primary); font-family:monospace;">IP: {ip}</span>
                  </div>
                  <span class="badge" style="background-color:rgba(255,255,255,0.02); color:{color}; border:1px solid {color}; font-size:0.6rem; padding:0.15rem 0.4rem;">{risk}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
