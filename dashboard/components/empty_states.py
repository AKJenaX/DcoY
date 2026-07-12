"""Enterprise-grade empty states for dashboard surfaces."""

from typing import Optional

import streamlit as st


def render_empty_state(
    title: str,
    message: str,
    icon: str = "◌",
    detail: Optional[str] = None,
    accent: str = "primary",
) -> None:
    """Render a reusable empty state card with consistent enterprise styling."""
    accent_class = accent if accent in {"primary", "success", "warning", "danger"} else "primary"
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="empty-state-shell accent-{accent_class}">
              <div class="empty-state-icon">{icon}</div>
              <div class="empty-state-title">{title}</div>
              <div class="empty-state-message">{message}</div>
              {f'<div class="empty-state-detail">{detail}</div>' if detail else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_no_alerts() -> None:
    render_empty_state(
        title="No Alerts",
        message="The environment is currently clear of actionable alert activity.",
        icon="✓",
        detail="Monitoring remains active and the incident queue is stable.",
        accent="success",
    )


def render_no_threats() -> None:
    render_empty_state(
        title="No Threats",
        message="No active threat objects meet the current detection thresholds.",
        icon="◌",
        detail="Recent telemetry trends remain within expected baselines.",
        accent="primary",
    )


def render_no_investigations() -> None:
    render_empty_state(
        title="No Investigations",
        message="There are no open investigations to review at the moment.",
        icon="🕵",
        detail="New triage items will appear here once workflow activity starts.",
        accent="primary",
    )


def render_no_rules() -> None:
    render_empty_state(
        title="No Rules",
        message="No detection rules are currently available for this view.",
        icon="⚙",
        detail="Rule quality and coverage insights will populate as detections are configured.",
        accent="warning",
    )


def render_no_results() -> None:
    render_empty_state(
        title="No Results",
        message="The current filter set did not return any matching records.",
        icon="🔎",
        detail="Try widening the query or clearing one of the active filters.",
        accent="warning",
    )


def render_no_telemetry() -> None:
    render_empty_state(
        title="No Telemetry",
        message="Telemetry data is currently unavailable for this surface.",
        icon="📡",
        detail="Once ingestion resumes, event streams and analytics will appear here.",
        accent="danger",
    )


def render_no_ai_response() -> None:
    render_empty_state(
        title="No AI Response",
        message="The AI layer has not returned a response for the current request.",
        icon="🤖",
        detail="Try a different prompt or re-run the analysis after the data refreshes.",
        accent="warning",
    )
