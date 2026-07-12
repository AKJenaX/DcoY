"""Reusable enterprise widget shells for dashboard polish and consistency."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st


class EnterpriseWidget:
    """Base helper for consistent enterprise widget rendering."""

    def __init__(self, title: str, subtitle: Optional[str] = None, key: Optional[str] = None):
        self.title = title
        self.subtitle = subtitle
        self.key = key

    def render(self) -> None:
        raise NotImplementedError


def render_kpi_widget(
    title: str,
    value: str,
    subtitle: str,
    accent: str = "blue",
    trend: Optional[str] = None,
    icon_svg: Optional[str] = None,
    key: Optional[str] = None,
):
    """Render a polished KPI card with consistent spacing and hierarchy."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="widget-shell widget-kpi {accent}" role="status" aria-label="{title}">
              <div class="widget-header">
                <div>
                  <div class="widget-title">{title}</div>
                  <div class="widget-subtitle">{subtitle}</div>
                </div>
                {f'<div class="widget-icon">{icon_svg}</div>' if icon_svg else ''}
              </div>
              <div class="widget-metric">{value}</div>
              {f'<div class="widget-trend">{trend}</div>' if trend else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )


class KPIWidget(EnterpriseWidget):
    def __init__(self, title: str, value: str, subtitle: str, accent: str = "blue", trend: Optional[str] = None, icon_svg: Optional[str] = None, key: Optional[str] = None):
        super().__init__(title, subtitle, key)
        self.value = value
        self.accent = accent
        self.trend = trend
        self.icon_svg = icon_svg

    def render(self) -> None:
        render_kpi_widget(self.title, self.value, self.subtitle or "", self.accent, self.trend, self.icon_svg, self.key)


class ChartWidget(EnterpriseWidget):
    def __init__(self, title: str, figure: Any, description: Optional[str] = None, key: Optional[str] = None, height: int = 280, toolbar: bool = True, filters: Optional[str] = None, footer: Optional[str] = None):
        super().__init__(title, description, key)
        self.figure = figure
        self.height = height
        self.toolbar = toolbar
        self.filters = filters
        self.footer = footer

    def render(self) -> None:
        from dashboard.components.chart_shell import render_chart_shell

        render_chart_shell(self.title, self.subtitle, self.figure, self.key, self.height, self.toolbar, self.filters, self.footer)


class TableWidget(EnterpriseWidget):
    def __init__(self, title: str, rows: List[Dict[str, Any]], columns: Optional[List[str]] = None, description: Optional[str] = None, key: Optional[str] = None):
        super().__init__(title, description, key)
        self.rows = rows
        self.columns = columns or []

    def render(self) -> None:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="widget-shell">
                  <div class="widget-header">
                    <div>
                      <div class="widget-title">{self.title}</div>
                      {f'<div class="widget-subtitle">{self.subtitle}</div>' if self.subtitle else ''}
                    </div>
                    <div class="table-toolbar" aria-label="Table actions"><span class="chart-toolbar-chip">Sorted</span><span class="chart-toolbar-chip">Export</span></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if self.rows:
                st.dataframe(self.rows, use_container_width=True, hide_index=True)
            else:
                from dashboard.components.empty_states import render_no_results

                render_no_results()


class TimelineWidget(EnterpriseWidget):
    def __init__(self, title: str, items: List[Dict[str, Any]], subtitle: Optional[str] = None, key: Optional[str] = None):
        super().__init__(title, subtitle, key)
        self.items = items

    def render(self) -> None:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="widget-shell">
                  <div class="widget-header">
                    <div>
                      <div class="widget-title">{self.title}</div>
                      {f'<div class="widget-subtitle">{self.subtitle}</div>' if self.subtitle else ''}
                    </div>
                  </div>
                  <div class="timeline-list">
                """,
                unsafe_allow_html=True,
            )
            for idx, item in enumerate(self.items):
                label = item.get("label", "Event")
                detail = item.get("detail", "")
                status = item.get("status", "open")
                st.markdown(
                    f"""
                    <div class="timeline-item {status}">
                      <div class="timeline-badge">{idx + 1}</div>
                      <div>
                        <div class="timeline-label">{label}</div>
                        <div class="timeline-detail">{detail}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div></div>", unsafe_allow_html=True)


class AIWidget(EnterpriseWidget):
    def __init__(self, title: str, bullets: List[str], subtitle: Optional[str] = None, confidence: Optional[str] = None, actions: Optional[List[str]] = None, mitre: Optional[List[str]] = None, key: Optional[str] = None):
        super().__init__(title, subtitle, key)
        self.bullets = bullets
        self.confidence = confidence
        self.actions = actions or []
        self.mitre = mitre or []

    def render(self) -> None:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="widget-shell">
                  <div class="widget-header">
                    <div>
                      <div class="widget-title">{self.title}</div>
                      {f'<div class="widget-subtitle">{self.subtitle}</div>' if self.subtitle else ''}
                    </div>
                    {f'<div class="confidence-badge">{self.confidence}</div>' if self.confidence else ''}
                  </div>
                  <div class="ai-list">
                """,
                unsafe_allow_html=True,
            )
            for bullet in self.bullets:
                st.markdown(f"<div class='ai-item'>{bullet}</div>", unsafe_allow_html=True)
            if self.mitre:
                st.markdown("<div class='ai-footer-group'><div class='widget-title'>MITRE</div>" + "".join(f"<span class='chip'>{item}</span>" for item in self.mitre) + "</div>", unsafe_allow_html=True)
            if self.actions:
                cols = st.columns(len(self.actions))
                for col, action in zip(cols, self.actions):
                    with col:
                        st.button(action, key=f"{self.key or 'ai_action'}_{action}", use_container_width=True)
            st.markdown("</div></div>", unsafe_allow_html=True)


class ThreatWidget(EnterpriseWidget):
    def __init__(self, title: str, summary: str, severity: str = "medium", subtitle: Optional[str] = None, key: Optional[str] = None):
        super().__init__(title, subtitle, key)
        self.summary = summary
        self.severity = severity

    def render(self) -> None:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="widget-shell threat-widget">
                  <div class="widget-header">
                    <div>
                      <div class="widget-title">{self.title}</div>
                      {f'<div class="widget-subtitle">{self.subtitle}</div>' if self.subtitle else ''}
                    </div>
                    <div class="severity-badge {self.severity}">{self.severity.upper()}</div>
                  </div>
                  <div class="widget-body">{self.summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


class InvestigationWidget(EnterpriseWidget):
    def __init__(self, title: str, summary: str, subtitle: Optional[str] = None, key: Optional[str] = None):
        super().__init__(title, subtitle, key)
        self.summary = summary

    def render(self) -> None:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="widget-shell">
                  <div class="widget-header">
                    <div>
                      <div class="widget-title">{self.title}</div>
                      {f'<div class="widget-subtitle">{self.subtitle}</div>' if self.subtitle else ''}
                    </div>
                  </div>
                  <div class="widget-body">{self.summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


class ExecutiveWidget(EnterpriseWidget):
    def __init__(self, title: str, value: str, subtitle: Optional[str] = None, key: Optional[str] = None):
        super().__init__(title, subtitle, key)
        self.value = value

    def render(self) -> None:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="widget-shell executive-widget">
                  <div class="widget-header">
                    <div>
                      <div class="widget-title">{self.title}</div>
                      {f'<div class="widget-subtitle">{self.subtitle}</div>' if self.subtitle else ''}
                    </div>
                  </div>
                  <div class="widget-metric">{self.value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


class StatusWidget(EnterpriseWidget):
    def __init__(self, title: str, value: str, status: str = "healthy", subtitle: Optional[str] = None, key: Optional[str] = None):
        super().__init__(title, subtitle, key)
        self.value = value
        self.status = status

    def render(self) -> None:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="widget-shell status-widget">
                  <div class="widget-header">
                    <div>
                      <div class="widget-title">{self.title}</div>
                      {f'<div class="widget-subtitle">{self.subtitle}</div>' if self.subtitle else ''}
                    </div>
                    <div class="status-pill {self.status}">{self.status.upper()}</div>
                  </div>
                  <div class="widget-metric">{self.value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


class EmptyStateWidget(EnterpriseWidget):
    def __init__(self, title: str, message: str, icon: str = "◌", detail: Optional[str] = None, accent: str = "primary", key: Optional[str] = None):
        super().__init__(title, subtitle=message, key=key)
        self.message = message
        self.icon = icon
        self.detail = detail
        self.accent = accent

    def render(self) -> None:
        from dashboard.components.empty_states import render_empty_state

        render_empty_state(self.title, self.message, self.icon, self.detail, self.accent)


def render_chart_widget(title: str, subtitle: str, figure: Any, key: str, height: int = 280):
    """Wrap a Plotly chart in a consistent enterprise card."""
    return ChartWidget(title, figure, description=subtitle, key=key, height=height).render()


def render_timeline_widget(title: str, items: List[Dict[str, Any]], subtitle: Optional[str] = None):
    """Render a vertical timeline for recent activity or investigation steps."""
    return TimelineWidget(title, items, subtitle).render()


def render_ai_widget(title: str, bullets: List[str], subtitle: Optional[str] = None):
    """Render an AI reasoning panel with structured evidence bullets."""
    return AIWidget(title, bullets, subtitle).render()


def render_investigation_widget(title: str, summary: str, subtitle: Optional[str] = None):
    """Render an investigation summary panel with polished body copy."""
    return InvestigationWidget(title, summary, subtitle).render()


def render_rule_widget(title: str, summary: str, subtitle: Optional[str] = None):
    """Render a rule or detection-quality summary panel."""
    return InvestigationWidget(title, summary, subtitle).render()


def render_executive_widget(title: str, value: str, subtitle: Optional[str] = None):
    """Render a leadership summary widget with executive emphasis."""
    return ExecutiveWidget(title, value, subtitle).render()


def render_empty_state(title: str, message: str, icon: str = "◌"):
    """Render a polished empty state for sparse or empty data views."""
    return EmptyStateWidget(title, message, icon).render()
