"""Reusable loading skeletons for dashboard widgets and tables."""

import streamlit as st


def render_skeleton_kpi() -> None:
    with st.container(border=True):
        st.markdown(
            """
            <div class="widget-shell">
              <div class="widget-header">
                <div>
                  <div class="shimmer-skeleton title"></div>
                  <div class="shimmer-skeleton" style="height:12px; width:45%;"></div>
                </div>
                <div class="shimmer-skeleton" style="height:36px; width:36px; border-radius:10px;"></div>
              </div>
              <div class="shimmer-skeleton" style="height:32px; width:60%;"></div>
              <div class="shimmer-skeleton" style="height:14px; width:35%;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_skeleton_chart() -> None:
    with st.container(border=True):
        st.markdown(
            """
            <div class="widget-shell">
              <div class="shimmer-skeleton title"></div>
              <div class="shimmer-skeleton" style="height:12px; width:30%;"></div>
              <div class="shimmer-skeleton card"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_skeleton_table(rows: int = 5) -> None:
    with st.container(border=True):
        st.markdown(
            """
            <div class="widget-shell">
              <div class="shimmer-skeleton title"></div>
              <div class="shimmer-skeleton" style="height:12px; width:22%; margin-bottom:1rem;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for _ in range(rows):
            st.markdown(
                """
                <div class="shimmer-skeleton" style="height:16px; width:100%; margin-bottom:0.6rem;"></div>
                """,
                unsafe_allow_html=True,
            )


def render_skeleton_timeline() -> None:
    with st.container(border=True):
        st.markdown(
            """
            <div class="widget-shell">
              <div class="shimmer-skeleton title"></div>
              <div class="timeline-list">
                <div class="timeline-item"><div class="shimmer-skeleton" style="height:28px; width:28px; border-radius:999px;"></div><div style="flex:1"><div class="shimmer-skeleton" style="height:12px; width:55%; margin-bottom:0.35rem;"></div><div class="shimmer-skeleton" style="height:10px; width:80%;"></div></div></div>
                <div class="timeline-item"><div class="shimmer-skeleton" style="height:28px; width:28px; border-radius:999px;"></div><div style="flex:1"><div class="shimmer-skeleton" style="height:12px; width:60%; margin-bottom:0.35rem;"></div><div class="shimmer-skeleton" style="height:10px; width:72%;"></div></div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_skeleton_ai_panel() -> None:
    with st.container(border=True):
        st.markdown(
            """
            <div class="widget-shell">
              <div class="shimmer-skeleton title"></div>
              <div class="shimmer-skeleton" style="height:12px; width:40%;"></div>
              <div class="shimmer-skeleton" style="height:60px; width:100%; border-radius:14px; margin-top:0.8rem;"></div>
              <div class="shimmer-skeleton" style="height:16px; width:70%; margin-top:0.8rem;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
