"""Metrics layout grid displaying threat intelligence overview statistics."""

import streamlit as st
from typing import Any, Dict, List
from dashboard.components.widget_variants import KPIWidget, render_kpi_widget

def render_overview_metrics(total_events: int, high_risk_count: int, active_threats: int, explain_rows: List[Dict[str, Any]]):
    """Renders the top card row featuring key performance metrics."""
    # Count mitigated threats (enforced responses)
    blocked_count = len([r for r in explain_rows if r.get("response_status_final") == "enforced"])
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        KPIWidget(
            title="Total Ingested",
            value=f"{total_events}",
            subtitle="vs last hr",
            accent="blue",
            trend="▲ +12%",
            icon_svg='<svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
        ).render()
        
    with col2:
        KPIWidget(
            title="High Risk",
            value=f"{high_risk_count}",
            subtitle="mitigated",
            accent="danger",
            trend="▼ -3%",
            icon_svg='<svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
        ).render()
        
    with col3:
        KPIWidget(
            title="Anomalies",
            value=f"{active_threats}",
            subtitle="outliers",
            accent="warning",
            trend="● ML Mode",
            icon_svg='<svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0-2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>'
        ).render()
        
    with col4:
        KPIWidget(
            title="Decoys Blocked",
            value=f"{blocked_count}",
            subtitle="enforced",
            accent="success",
            trend="▲ 100%",
            icon_svg='<svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
        ).render()
        
    with col5:
        KPIWidget(
            title="Active Agents",
            value="4",
            subtitle="healthy",
            accent="cyan",
            trend="▲ 4 / 4",
            icon_svg='<svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/></svg>'
        ).render()
        
    with col6:
        KPIWidget(
            title="Assets Guarded",
            value="12",
            subtitle="subnets",
            accent="purple",
            trend="● Normal",
            icon_svg='<svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>'
        ).render()
    st.markdown("<br>", unsafe_allow_html=True)
