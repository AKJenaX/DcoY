"""Metrics layout grid displaying threat intelligence overview statistics."""

import streamlit as st
from typing import Any, Dict, List

def render_overview_metrics(total_events: int, high_risk_count: int, active_threats: int, explain_rows: List[Dict[str, Any]]):
    """Renders the top card row featuring key performance metrics."""
    # Count mitigated threats (enforced responses)
    blocked_count = len([r for r in explain_rows if r.get("response_status_final") == "enforced"])
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Total Ingested</div>
                <div class="metric-value">{total_events}</div>
                <div style="display:flex; align-items:center; gap:0.4rem;">
                  <span class="trend-badge up">▲ +12%</span>
                  <span class="muted-helper">vs last hr</span>
                </div>
                <svg viewBox="0 0 100 30" width="80" height="24" style="margin-top: 0.5rem; display:block;">
                  <path d="M0 25 L15 20 L30 24 L45 10 L60 15 L75 5 L90 18 L100 12" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round"></path>
                </svg>
              </div>
              <div class="soc-kpi-icon blue">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">High Risk</div>
                <div class="metric-value">{high_risk_count}</div>
                <div style="display:flex; align-items:center; gap:0.4rem;">
                  <span class="trend-badge down">▼ -3%</span>
                  <span class="muted-helper">mitigated</span>
                </div>
                <svg viewBox="0 0 100 30" width="80" height="24" style="margin-top: 0.5rem; display:block;">
                  <path d="M0 10 L15 15 L30 8 L45 22 L60 18 L75 25 L90 12 L100 5" fill="none" stroke="var(--danger)" stroke-width="2" stroke-linecap="round"></path>
                </svg>
              </div>
              <div class="soc-kpi-icon danger">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Anomalies</div>
                <div class="metric-value">{active_threats}</div>
                <div style="display:flex; align-items:center; gap:0.4rem;">
                  <span class="trend-badge stable">● ML Mode</span>
                  <span class="muted-helper">outliers</span>
                </div>
                <svg viewBox="0 0 100 30" width="80" height="24" style="margin-top: 0.5rem; display:block;">
                  <path d="M0 20 L20 20 L35 15 L50 25 L65 10 L80 18 L100 12" fill="none" stroke="var(--warning)" stroke-width="2" stroke-linecap="round"></path>
                </svg>
              </div>
              <div class="soc-kpi-icon warning">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                  <line x1="12" y1="22.08" x2="12" y2="12"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col4:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Decoys Blocked</div>
                <div class="metric-value">{blocked_count}</div>
                <div style="display:flex; align-items:center; gap:0.4rem;">
                  <span class="trend-badge up">▲ 100%</span>
                  <span class="muted-helper">enforced</span>
                </div>
                <svg viewBox="0 0 100 30" width="80" height="24" style="margin-top: 0.5rem; display:block;">
                  <path d="M0 28 L20 25 L40 22 L60 18 L80 12 L100 5" fill="none" stroke="var(--success)" stroke-width="2" stroke-linecap="round"></path>
                </svg>
              </div>
              <div class="soc-kpi-icon success">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col5:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Active Agents</div>
                <div class="metric-value">4</div>
                <div style="display:flex; align-items:center; gap:0.4rem;">
                  <span class="trend-badge up">▲ 4 / 4</span>
                  <span class="muted-helper">healthy</span>
                </div>
                <svg viewBox="0 0 100 30" width="80" height="24" style="margin-top: 0.5rem; display:block;">
                  <path d="M0 15 L25 15 L50 15 L75 15 L100 15" fill="none" stroke="var(--secondary)" stroke-width="2" stroke-linecap="round"></path>
                </svg>
              </div>
              <div class="soc-kpi-icon cyan">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="9" y1="9" x2="15" y2="9"/>
                  <line x1="9" y1="13" x2="15" y2="13"/>
                  <line x1="9" y1="17" x2="13" y2="17"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col6:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Assets Guarded</div>
                <div class="metric-value">12</div>
                <div style="display:flex; align-items:center; gap:0.4rem;">
                  <span class="trend-badge stable">● Normal</span>
                  <span class="muted-helper">subnets</span>
                </div>
                <svg viewBox="0 0 100 30" width="80" height="24" style="margin-top: 0.5rem; display:block;">
                  <path d="M0 15 L10 12 L20 18 L30 10 L40 22 L50 8 L60 25 L70 12 L80 18 L90 5 L100 15" fill="none" stroke="var(--purple)" stroke-width="1.5" stroke-linecap="round"></path>
                </svg>
              </div>
              <div class="soc-kpi-icon purple">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
                  <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
                  <line x1="6" y1="6" x2="6.01" y2="6"/>
                  <line x1="6" y1="18" x2="6.01" y2="18"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)
