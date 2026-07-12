"""Data visualization components, Plotly graphs, and coordinates mapping."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from typing import Any, Dict, List

def render_live_attack_map(locations: List[Dict[str, Any]]):
    """Renders the geo map and attack origin summary cards."""
    st.markdown('<h3 class="section-title">Live Threat Map</h3>', unsafe_allow_html=True)
    
    with st.container(border=True):
        if locations:
            map_df = pd.DataFrame(locations)
            
            # Map risk colors
            # In our data, map_df doesn't have risk_level directly, but we can assign based on country or ip
            # Or add a default color column
            map_df["color_hex"] = "#3B82F6"  # Accent Blue default
            
            # Let's create the base figure with Graph Objects for multi-layer glowing effects
            fig = go.Figure()
            
            # Layer 1: Glow effect (Larger, semi-transparent markers)
            fig.add_trace(go.Scattermapbox(
                lat=map_df["latitude"],
                lon=map_df["longitude"],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=22,
                    color='#3B82F6',
                    opacity=0.25
                ),
                hoverinfo='none',
                showlegend=False
            ))
            
            # Layer 2: Core Pulse (Primary threat markers)
            fig.add_trace(go.Scattermapbox(
                lat=map_df["latitude"],
                lon=map_df["longitude"],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=10,
                    color='#22D3EE',
                    opacity=0.9
                ),
                text=map_df["city"],
                hoverinfo='text',
                showlegend=False
            ))
            
            fig.update_layout(
                mapbox_style="carto-darkmatter",
                mapbox=dict(
                    zoom=1,
                    center=dict(lat=map_df["latitude"].mean(), lon=map_df["longitude"].mean())
                ),
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                paper_bgcolor="#111C2D",
                plot_bgcolor="#111C2D",
                font_color="#F8FAFC",
                height=300
            )
            
            m1, m2 = st.columns([3, 1])
            with m1:
                st.plotly_chart(fig, use_container_width=True, key="live_attack_mapbox")
            with m2:
                st.markdown("<p style='font-size:0.75rem; font-weight:600; text-transform:uppercase; color:var(--text-secondary); margin-bottom:0.5rem;'>Top Targets By Country</p>", unsafe_allow_html=True)
                country_df = map_df.groupby("country").size().reset_index(name="Count").sort_values("Count", ascending=False)
                
                # Format country summary as a clean HTML grid
                html_rows = ""
                for _, row in country_df.iterrows():
                    html_rows += f"""
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
                      <td style="padding:0.4rem 0.5rem; font-size:0.75rem; color:var(--text-primary); font-weight:500;">{row['country']}</td>
                      <td style="padding:0.4rem 0.5rem; font-size:0.75rem; color:var(--secondary); font-weight:700; text-align:right;">{row['Count']}</td>
                    </tr>
                    """
                st.markdown(
                    f"""
                    <div style="max-height: 250px; overflow-y: auto;">
                      <table style="width:100%; border-collapse:collapse;">
                        {html_rows}
                      </table>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No geolocation data available")
    st.markdown("<br>", unsafe_allow_html=True)

def render_attack_analysis_charts(attack_summary: Dict[str, int], response_summary: Dict[str, int]):
    """Renders Plotly bar charts representing attack vectors and decoy deployments."""
    st.markdown('<h3 class="section-title">Attack Analysis Metrics</h3>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        with st.container(border=True):
            st.markdown("<p style='font-size:0.8rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.25rem;'>ATTACK VECTORS DISTRIBUTION</p>", unsafe_allow_html=True)
            if attack_summary:
                attack_df = pd.DataFrame(list(attack_summary.items()), columns=["Type", "Count"])
                
                # Create a custom go.Bar trace with thin borders and soft styling
                fig_attack = go.Figure(data=[
                    go.Bar(
                        x=attack_df["Type"],
                        y=attack_df["Count"],
                        marker_color='#3B82F6',
                        marker_line_width=0,
                        opacity=0.85
                    )
                ])
                fig_attack.update_layout(
                    paper_bgcolor="#111C2D",
                    plot_bgcolor="#111C2D",
                    font_color="#F8FAFC",
                    margin={"r": 10, "t": 20, "l": 20, "b": 30},
                    height=250,
                    xaxis_title=None,
                    yaxis_title=None,
                    bargap=0.4
                )
                fig_attack.update_xaxes(showgrid=False, tickfont={"size": 10, "color": "#94A3B8"})
                fig_attack.update_yaxes(gridcolor="rgba(255,255,255,0.03)", tickfont={"size": 10, "color": "#94A3B8"})
                st.plotly_chart(fig_attack, use_container_width=True, key="chart_attack_main")
            else:
                st.info("No attack analysis data")

    with c2:
        with st.container(border=True):
            st.markdown("<p style='font-size:0.8rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.25rem;'>DECEPTION HONEYPOT COUNTERMEASURES</p>", unsafe_allow_html=True)
            if response_summary:
                response_df = pd.DataFrame(list(response_summary.items()), columns=["Honeypot", "Count"])
                
                fig_response = go.Figure(data=[
                    go.Bar(
                        x=response_df["Honeypot"],
                        y=response_df["Count"],
                        marker_color='#8B5CF6',
                        marker_line_width=0,
                        opacity=0.85
                    )
                ])
                fig_response.update_layout(
                    paper_bgcolor="#111C2D",
                    plot_bgcolor="#111C2D",
                    font_color="#F8FAFC",
                    margin={"r": 10, "t": 20, "l": 20, "b": 30},
                    height=250,
                    xaxis_title=None,
                    yaxis_title=None,
                    bargap=0.4
                )
                fig_response.update_xaxes(showgrid=False, tickfont={"size": 10, "color": "#94A3B8"})
                fig_response.update_yaxes(gridcolor="rgba(255,255,255,0.03)", tickfont={"size": 10, "color": "#94A3B8"})
                st.plotly_chart(fig_response, use_container_width=True, key="chart_response_main")
            else:
                st.info("No honeypot response data")
    st.markdown("<br>", unsafe_allow_html=True)
