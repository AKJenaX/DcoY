"""Sidebar status monitors, grouped navigation lists, and report compiler controls."""

import requests
import streamlit as st
from dashboard.utils.constants import REFRESH_INTERVAL, SESSION_TOKEN_PATH

def render_sidebar(api_base: str):
    """Renders the dashboard sidebar navigation, refresh actions, and PDF reports."""
    current_page = st.query_params.get("page", "overview")
    
    with st.sidebar:
        # Title Logo Header Block
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
              <svg class="soc-icon" style="width:36px; height:36px; color:var(--primary); margin-bottom:0.25rem;" viewBox="0 0 24 24">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
              <h2 style="margin: 0.25rem 0 0 0; font-size: 1.25rem; color: var(--text-primary); font-weight: 700; letter-spacing: -0.5px;">DcoY Console</h2>
              <span style="font-size: 0.6rem; color: var(--text-secondary); letter-spacing: 0.5px; text-transform: uppercase;">Enterprise SOC Portal</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Navigation Group 1: MONITORING
        st.markdown(
            f"""
            <p style="font-size: 0.65rem; color: var(--muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 0.5rem; padding-left: 0.5rem;">MONITORING</p>
            <a href="?page=overview" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "overview" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
                Dashboard Overview
              </div>
            </a>
            <a href="?page=threat_intel" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "threat_intel" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                Threat Intelligence
              </div>
            </a>
            <a href="?page=live_geo" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "live_geo" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                Live Geolocation
              </div>
            </a>
            <a href="?page=copilot" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "copilot" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                Copilot Intel
              </div>
            </a>
            <a href="?page=threat_hunting" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "threat_hunting" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                Threat Hunting
              </div>
            </a>
            <br/>
            """,
            unsafe_allow_html=True
        )
        
        # Navigation Group 2: MANAGEMENT
        st.markdown(
            f"""
            <p style="font-size: 0.65rem; color: var(--muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 0.5rem; padding-left: 0.5rem;">MANAGEMENT</p>
            <a href="?page=executive" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "executive" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                Executive Intelligence
              </div>
            </a>
            <a href="?page=investigations" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "investigations" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                Investigations
              </div>
            </a>
            <a href="?page=detection_rules" target="_self" style="text-decoration:none; color:inherit;">
              <div class="sidebar-menu-item {"active" if current_page == "detection_rules" else ""}">
                <svg class="soc-icon" viewBox="0 0 24 24"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>
                Detection Rules
              </div>
            </a>
            <div class="sidebar-menu-item">
              <svg class="soc-icon" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Reports Archive
            </div>
            <div class="sidebar-menu-item">
              <svg class="soc-icon" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
              System Health Status
            </div>
            <br/>
            """,
            unsafe_allow_html=True
        )
        
        # Navigation Group 3: SUPPORT
        st.markdown(
            """
            <p style="font-size: 0.65rem; color: var(--muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 0.5rem; padding-left: 0.5rem;">SUPPORT</p>
            <div class="sidebar-menu-item">
              <svg class="soc-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              Settings Panel
            </div>
            <div class="sidebar-menu-item">
              <svg class="soc-icon" viewBox="0 0 24 24"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
              Documentation Guide
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # System Health Card
        st.markdown(
            f"""
            <div style="background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem; margin-bottom: 1.25rem;">
              <p style="margin: 0 0 0.4rem 0; font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">SYSTEM HEALTH</p>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                <span style="font-size: 0.75rem; color: var(--text-primary);">Deception Decoy:</span>
                <span class="badge success" style="font-size: 0.55rem; padding: 0.1rem 0.4rem;">ONLINE</span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                <span style="font-size: 0.75rem; color: var(--text-primary);">Anomaly Detect:</span>
                <span class="badge success" style="font-size: 0.55rem; padding: 0.1rem 0.4rem;">STABLE</span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; color: var(--text-primary);">Polling Loop:</span>
                <span style="font-size: 0.75rem; color: var(--secondary); font-weight: 700;">Every {REFRESH_INTERVAL}s</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Controls panel
        st.markdown("<p style='font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 0.5rem; padding-left: 0.5rem;'>OPERATOR PANEL</p>", unsafe_allow_html=True)
        
        # Force refresh button
        if st.button("Force Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
        st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
        
        # Download PDF Report button
        if api_base:
            try:
                report_url = f"{api_base}/report"
                
                if st.button("Compile PDF Report", use_container_width=True):
                    with st.spinner("Compiling PDF report..."):
                        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}
                        response = requests.get(report_url, headers=headers, timeout=30, verify=False)
                        response.raise_for_status()
                        pdf_bytes = response.content
                        
                        st.download_button(
                            label="Download Report",
                            data=pdf_bytes,
                            file_name="dcoy_defense_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("Report ready!")
            except Exception as e:
                st.error("Report downloader unreachable")

        st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
        
        # Log Out button
        if st.button("Log Out", use_container_width=True):
            st.session_state.auth_token = None
            st.session_state.current_user = "operator"
            if SESSION_TOKEN_PATH.exists():
                try:
                    SESSION_TOKEN_PATH.unlink()
                except Exception:
                    pass
            st.session_state.logout_success = True
            st.rerun()
                 
        # Footer version details
        st.markdown(
            """
            <div style="margin-top: 2rem; text-align: center; border-top: 1px solid var(--border-color); padding-top: 0.75rem;">
              <span style="font-size: 0.65rem; color: var(--muted);">DcoY v0.1.0-alpha</span><br/>
              <span style="font-size: 0.6rem; color: var(--muted);">MIT Open Source License</span>
            </div>
            """,
            unsafe_allow_html=True
        )
