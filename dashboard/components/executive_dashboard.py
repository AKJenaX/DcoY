"""Executive Intelligence command center dashboard component."""

import base64
import json
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _go_page(page: str) -> None:
    st.query_params["page"] = page
    st.rerun()


def _plotly_layout(fig: go.Figure, height: int = 260) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="#F9FAFB",
        margin={"r": 12, "t": 24, "l": 24, "b": 34},
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, tickfont={"size": 10, "color": "#9CA3AF"})
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", tickfont={"size": 10, "color": "#9CA3AF"})
    return fig


def _metric_card(title: str, value: Any, helper: str, tone: str = "blue") -> None:
    st.markdown(
        f"""
        <div class="soc-kpi-card" aria-label="{title}: {value}">
          <div>
            <div class="card-title">{title}</div>
            <div class="metric-value" style="font-size:2.1rem;">{value}</div>
            <div style="font-size:0.72rem; color:var(--text-secondary);">{helper}</div>
          </div>
          <div class="soc-kpi-icon {tone}">
            <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _drilldown_bar(key_prefix: str) -> None:
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        if st.button("Threat Intelligence", key=f"{key_prefix}_to_intel", use_container_width=True):
            _go_page("threat_intel")
    with d2:
        if st.button("Threat Hunting", key=f"{key_prefix}_to_hunt", use_container_width=True):
            _go_page("threat_hunting")
    with d3:
        if st.button("Detection Engineering", key=f"{key_prefix}_to_rules", use_container_width=True):
            _go_page("detection_rules")
    with d4:
        if st.button("Investigations", key=f"{key_prefix}_to_cases", use_container_width=True):
            _go_page("investigations")


def _bar_chart(items: List[Dict[str, Any]], label_key: str, value_key: str, color: str, title: str, key: str) -> None:
    df = pd.DataFrame(items or [{label_key: "No data", value_key: 0}])
    fig = go.Figure(
        data=[
            go.Bar(
                x=df[label_key],
                y=df[value_key],
                marker_color=color,
                opacity=0.86,
                hovertemplate=f"<b>{title}</b><br>%{{x}}: %{{y}}<extra></extra>",
            )
        ]
    )
    _plotly_layout(fig)
    st.plotly_chart(fig, use_container_width=True, key=key)


def _render_header(metrics: Dict[str, Any], latency_ms: int) -> None:
    generated = str(metrics.get("generated_at", ""))[:19].replace("T", " ")
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">Executive Intelligence</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">SOC Operational Overview</p>
          </div>
          <div style="display:flex; gap:0.5rem; align-items:center;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> EXECUTIVE FEED ACTIVE
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
            <span class="status-pill secure" style="font-size:0.7rem;">UPDATED: {generated}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_kpis(metrics: Dict[str, Any]) -> None:
    kpis = metrics.get("kpis", {})
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        _metric_card("Open Investigations", kpis.get("open_investigations", 0), "Active case load", "warning")
    with c2:
        _metric_card("Critical Alerts (24h)", kpis.get("critical_alerts_24h", 0), "Current operating window", "danger")
    with c3:
        _metric_card("Detection Coverage", f"{kpis.get('detection_coverage', 0)}%", "MITRE mapped controls", "success")
    with c4:
        _metric_card("MTTI", f"{kpis.get('mtti_hours', 0)}h", "Mean investigate time", "blue")
    with c5:
        _metric_card("MTTR", f"{kpis.get('mttr_hours', 0)}h", "Mean resolve time", "purple")
    with c6:
        _metric_card("AI Confidence Avg", f"{kpis.get('ai_confidence_average', 0)}%", "Evidence quality score", "cyan")
    st.markdown("<br/>", unsafe_allow_html=True)


def _render_posture(metrics: Dict[str, Any]) -> None:
    posture = metrics.get("posture", {})
    st.markdown('<h3 class="section-title">Security Posture Overview</h3>', unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns([1.2, 1, 1, 1])
    with p1:
        with st.container(border=True):
            risk = posture.get("overall_risk_score", 0)
            color = "var(--danger)" if risk >= 70 else ("var(--warning)" if risk >= 40 else "var(--success)")
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=risk,
                    number={"suffix": "%", "font": {"color": "#F9FAFB"}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#9CA3AF"},
                        "bar": {"color": color},
                        "bgcolor": "#1F2937",
                        "borderwidth": 0,
                        "steps": [
                            {"range": [0, 40], "color": "rgba(16,185,129,0.18)"},
                            {"range": [40, 70], "color": "rgba(245,158,11,0.18)"},
                            {"range": [70, 100], "color": "rgba(239,68,68,0.18)"},
                        ],
                    },
                )
            )
            _plotly_layout(fig, height=230)
            st.plotly_chart(fig, use_container_width=True, key="exec_risk_gauge")
            st.caption(f"Posture: {posture.get('posture_label', 'Unknown')}")
    with p2:
        with st.container(border=True):
            _metric_card("Threat Trend", posture.get("threat_trend", "Stable"), "Alert movement", "warning")
    with p3:
        with st.container(border=True):
            _metric_card("Analyst Workload", posture.get("analyst_workload", 0), "Cases per analyst", "blue")
    with p4:
        with st.container(border=True):
            _metric_card("Rule Health Average", f"{posture.get('rule_health_average', 0)}%", "Control readiness", "success")


def _render_mitre_matrix(metrics: Dict[str, Any]) -> None:
    matrix = metrics.get("mitre_coverage", [])
    st.markdown('<h3 class="section-title">MITRE ATT&CK Coverage</h3>', unsafe_allow_html=True)
    with st.container(border=True):
        status_color = {
            "Covered": "var(--success)",
            "Partially Covered": "var(--warning)",
            "Not Covered": "var(--muted)",
        }
        tiles = ""
        for item in matrix:
            color = status_color.get(item.get("status"), "var(--muted)")
            rules_count = len(item.get("rules", []))
            tiles += f"""
            <div style="border:1px solid {color}; background-color:rgba(255,255,255,0.025); border-radius:8px; padding:0.65rem; min-height:116px;">
              <div style="font-size:0.62rem; color:var(--text-secondary); text-transform:uppercase; font-weight:700; margin-bottom:0.35rem;">{item.get('tactic')}</div>
              <div style="font-size:0.78rem; color:var(--text-primary); font-weight:700; line-height:1.25;">{item.get('technique')}</div>
              <div style="margin-top:0.5rem; display:flex; justify-content:space-between; align-items:center;">
                <span class="badge" style="color:{color}; border:1px solid {color}; background-color:rgba(255,255,255,0.02); font-size:0.56rem;">{item.get('status')}</span>
                <span style="font-size:0.65rem; color:var(--text-secondary);">{rules_count} rules</span>
              </div>
            </div>
            """
        st.markdown(
            f"""<div style="display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:0.65rem;">{tiles}</div>""",
            unsafe_allow_html=True,
        )

        options = [f"{item.get('technique')} - {item.get('status')}" for item in matrix]
        selected = st.selectbox("ATT&CK technique drill-down", options=options, key="exec_mitre_drilldown")
        selected_item = matrix[options.index(selected)] if options else {}
        rules = selected_item.get("rules", [])
        if rules:
            rows = ""
            for rule in rules:
                rows += f"""
                <tr>
                  <td>{rule.get('id')}</td>
                  <td>{rule.get('name')}</td>
                  <td><span class="badge info">{rule.get('status')}</span></td>
                  <td>{rule.get('severity')}</td>
                </tr>
                """
            st.markdown(
                f"""
                <div class="soc-table-container" style="margin-top:0.75rem;">
                  <table class="soc-table">
                    <thead><tr><th>ID</th><th>Detection Rule</th><th>Status</th><th>Severity</th></tr></thead>
                    <tbody>{rows}</tbody>
                  </table>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No mapped rules for this ATT&CK technique.")
        if st.button("Open Related Detection Rules", key="exec_open_related_rules", use_container_width=True):
            _go_page("detection_rules")


def _render_trends(metrics: Dict[str, Any]) -> None:
    trends = metrics.get("trends", {})
    st.markdown('<h3 class="section-title">Executive Threat Trends</h3>', unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        with st.container(border=True):
            _bar_chart(trends.get("daily_alerts", []), "date", "alerts", "#3B82F6", "Daily alerts", "exec_daily_alerts")
            _drilldown_bar("exec_daily_alerts")
    with r1c2:
        with st.container(border=True):
            weekly = trends.get("weekly_trends", []) or [{"week": "No data", "alerts": 0}]
            df = pd.DataFrame(weekly)
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=df["week"],
                        y=df["alerts"],
                        mode="lines+markers",
                        line={"color": "#22D3EE", "width": 3},
                        marker={"size": 8},
                        hovertemplate="<b>Weekly trend</b><br>%{x}: %{y}<extra></extra>",
                    )
                ]
            )
            _plotly_layout(fig)
            st.plotly_chart(fig, use_container_width=True, key="exec_weekly_trends")
            _drilldown_bar("exec_weekly_trends")

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        with st.container(border=True):
            _bar_chart(trends.get("top_attack_vectors", []), "label", "value", "#8B5CF6", "Top attack vectors", "exec_vectors")
            _drilldown_bar("exec_vectors")
    with r2c2:
        with st.container(border=True):
            severity = trends.get("severity_distribution", []) or [{"label": "No data", "value": 0}]
            df = pd.DataFrame(severity)
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=df["label"],
                        values=df["value"],
                        hole=0.58,
                        marker={"colors": ["#EF4444", "#F59E0B", "#10B981"]},
                        hovertemplate="<b>%{label}</b>: %{value}<extra></extra>",
                    )
                ]
            )
            _plotly_layout(fig)
            st.plotly_chart(fig, use_container_width=True, key="exec_severity")
            _drilldown_bar("exec_severity")
    with r2c3:
        with st.container(border=True):
            _bar_chart(trends.get("top_affected_countries", []), "label", "value", "#22D3EE", "Affected countries", "exec_countries")
            _drilldown_bar("exec_countries")
    with r2c4:
        with st.container(border=True):
            _bar_chart(trends.get("top_affected_assets", []), "label", "value", "#10B981", "Affected assets", "exec_assets")
            _drilldown_bar("exec_assets")


def _render_soc_performance(metrics: Dict[str, Any]) -> None:
    perf = metrics.get("soc_performance", {})
    st.markdown('<h3 class="section-title">SOC Performance</h3>', unsafe_allow_html=True)
    labels = [
        "Avg Response Time",
        "Avg Investigation Duration",
        "Case Backlog",
        "Detection Latency",
        "False Positive Rate",
        "Analyst Productivity",
    ]
    values = [
        f"{perf.get('average_response_time_minutes', 0)}m",
        f"{perf.get('average_investigation_duration_hours', 0)}h",
        perf.get("case_backlog", 0),
        f"{perf.get('detection_latency_seconds', 0)}s",
        f"{perf.get('false_positive_rate', 0)}%",
        perf.get("analyst_productivity", 0),
    ]
    helpers = [
        "Alert to first action",
        "Created to latest update",
        "Open and active cases",
        "Ingest to detection",
        "Estimated review waste",
        "Resolved/critical items",
    ]
    tones = ["blue", "purple", "warning", "cyan", "danger", "success"]
    cols = st.columns(6)
    for idx, col in enumerate(cols):
        with col:
            with st.container(border=True):
                _metric_card(labels[idx], values[idx], helpers[idx], tones[idx])


def _render_ai_insights(metrics: Dict[str, Any]) -> None:
    ai = metrics.get("ai_insights", {})
    st.markdown('<h3 class="section-title">AI Insights</h3>', unsafe_allow_html=True)
    left, right = st.columns([2, 1])
    with left:
        with st.container(border=True):
            st.markdown('<div class="card-title">Executive Copilot Summary</div>', unsafe_allow_html=True)
            st.markdown(ai.get("summary", "No executive summary available."))
            sections = [
                ("Major Incidents", ai.get("major_incidents", [])),
                ("Emerging Patterns", ai.get("emerging_patterns", [])),
                ("Coverage Gaps", ai.get("coverage_gaps", [])),
                ("Recommended Priorities", ai.get("recommended_priorities", [])),
                ("Strategic Observations", ai.get("strategic_observations", [])),
            ]
            for title, items in sections:
                with st.expander(title, expanded=title in {"Major Incidents", "Recommended Priorities"}):
                    for item in items:
                        st.markdown(f"- {item}")
    with right:
        with st.container(border=True):
            st.markdown('<div class="card-title">Executive Report Export</div>', unsafe_allow_html=True)
            reports = metrics.get("reports", {})
            st.download_button(
                "Download Markdown",
                data=reports.get("markdown", ""),
                file_name="dcoy_executive_report.md",
                mime="text/markdown",
                use_container_width=True,
                key="exec_export_markdown",
            )
            st.download_button(
                "Download JSON",
                data=reports.get("json", json.dumps(metrics, indent=2)),
                file_name="dcoy_executive_report.json",
                mime="application/json",
                use_container_width=True,
                key="exec_export_json",
            )
            pdf_payload = reports.get("pdf_base64", "")
            pdf_bytes = base64.b64decode(pdf_payload.encode("ascii")) if pdf_payload else b""
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name="dcoy_executive_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="exec_export_pdf",
            )
            st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)
            _drilldown_bar("exec_ai")


def render_executive_dashboard_page(metrics: Dict[str, Any], latency_ms: int, api_base: str) -> None:
    """Render the Executive Intelligence command center."""
    _render_header(metrics, latency_ms)
    _render_kpis(metrics)
    _render_posture(metrics)
    _render_mitre_matrix(metrics)
    _render_trends(metrics)
    _render_soc_performance(metrics)
    _render_ai_insights(metrics)
