"""Reusable chart shell for consistent enterprise chart surfaces."""

from typing import Any, Optional

import streamlit as st


def render_chart_shell(
    title: str,
    description: Optional[str] = None,
    figure: Any = None,
    key: Optional[str] = None,
    height: int = 280,
    toolbar: bool = True,
    filters: Optional[str] = None,
    footer: Optional[str] = None,
    show_export: bool = True,
    show_legend: bool = True,
) -> None:
    """Render a consistent chart card with title, description, controls, legend, and footer."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="widget-shell">
              <div class="widget-header">
                <div>
                  <div class="widget-title">{title}</div>
                  {f'<div class="widget-subtitle">{description}</div>' if description else ''}
                </div>
                <div class="chart-toolbar" role="toolbar" aria-label="Chart actions">
                  {f'<span class="chart-toolbar-chip">{filters}</span>' if filters else ''}
                  {f'<button class="chart-toolbar-btn" type="button">Export</button>' if show_export else ''}
                  {f'<button class="chart-toolbar-btn" type="button">{("Filters" if not filters else "View")}</button>' if toolbar else ''}
                </div>
              </div>
              {f'<div class="chart-legend">{("Legend" if show_legend else "")}</div>' if show_legend else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if figure is not None:
            st.plotly_chart(figure, use_container_width=True, key=key, height=height)
        if footer:
            st.markdown(
                f"<div class='chart-footer'>{footer}</div>",
                unsafe_allow_html=True
            )
