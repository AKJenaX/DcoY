"""Centralized Notifications Tray component."""

import streamlit as st
from typing import List, Dict, Any


def seed_notifications():
    """Seed initial platform notifications in session state if not present."""
    if "notifications" not in st.session_state:
        st.session_state.notifications = [
            {
                "id": "notif_01",
                "category": "Detection",
                "title": "🚨 SSH Brute Force Flood Detected",
                "desc": "High severity brute force connection attempts flagged targeting WS-OPERATOR-02.",
                "route": "detection_rules",
                "entity_id": None,
                "read": False
            },
            {
                "id": "notif_02",
                "category": "SOAR",
                "title": "⚙️ Workflow Auto-Isolation Completed",
                "desc": "Compromised operator station WS-OPERATOR-02 successfully quarantined in edge rules.",
                "route": "soar",
                "entity_id": None,
                "read": False
            },
            {
                "id": "notif_03",
                "category": "Executive",
                "title": "📊 Executive Summary Report compiled",
                "desc": "Platform metrics successfully compiled and CISO diagnostics generated.",
                "route": "executive",
                "entity_id": None,
                "read": False
            }
        ]


def render_notifications_tray():
    """Renders platform notifications list in the sidebar container."""
    seed_notifications()
    notifications = st.session_state.notifications

    unread_count = sum(1 for n in notifications if not n["read"])

    with st.sidebar:
        st.markdown("<hr style='margin: 1rem 0;' />", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
              <h4 style="margin:0; font-size:0.9rem; color:var(--text-primary);">🔔 Notification Center ({unread_count})</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not notifications:
            st.info("No active notifications.")
            return

        for idx, notif in enumerate(notifications):
            opacity = "1.0" if not notif["read"] else "0.5"
            border_style = "2px solid var(--primary)" if not notif["read"] else "1px solid var(--border-color)"
            
            st.markdown(
                f"""
                <div style="opacity:{opacity}; background-color:var(--card-bg-sec); border:{border_style}; border-radius:6px; padding:0.5rem; margin-bottom:0.4rem; position:relative;">
                  <span class="badge" style="font-size:0.55rem; background-color:var(--card-bg); float:right;">{notif['category']}</span>
                  <div style="font-size:0.75rem; font-weight:700; color:var(--text-primary);">{notif['title']}</div>
                  <div style="font-size:0.65rem; color:var(--text-secondary); margin-top:0.2rem;">{notif['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col_actions_1, col_actions_2 = st.columns(2)
            with col_actions_1:
                # Nav link
                if st.button(f"Go ➔", key=f"notif_nav_{notif['id']}", use_container_width=True):
                    notif["read"] = True
                    st.query_params["page"] = notif["route"]
                    st.rerun()
            with col_actions_2:
                # Mark as read
                if not notif["read"]:
                    if st.button(f"Dismiss", key=f"notif_read_{notif['id']}", use_container_width=True):
                        notif["read"] = True
                        st.rerun()
                else:
                    if st.button(f"Remove", key=f"notif_del_{notif['id']}", use_container_width=True):
                        notifications.pop(idx)
                        st.session_state.notifications = notifications
                        st.rerun()
