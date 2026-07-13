"""Streamlit component rendering the Threat Intelligence Fusion and Correlation center."""

import requests
import streamlit as st
from typing import Any, Dict, List


def render_intelligence_fusion_page(explain_rows: List[Dict[str, Any]], detect_rows: List[Dict[str, Any]], latency_ms: int, api_base: str):
    """Renders the modular correlation engine and interactive threat relation graph."""
    
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem;">
          <div>
            <h1 class="page-title">Threat Intelligence Fusion Center</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">Correlate multi-vector telemetry, active honeypot alerts, simulations, and automated playbooks.</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> ACTIVE CORRELATION
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Fetch KPIs and Graph Data
    headers = {}
    if "auth_token" in st.session_state and st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"

    kpis = {}
    graph = {"nodes": [], "edges": []}
    
    try:
        kpi_resp = requests.get(f"{api_base}/api/soar/intelligence/kpis", headers=headers, timeout=5, verify=False)
        if kpi_resp.status_code == 200:
            kpis = kpi_resp.json()
    except Exception:
        pass

    try:
        graph_resp = requests.get(f"{api_base}/api/soar/intelligence/graph", headers=headers, timeout=5, verify=False)
        if graph_resp.status_code == 200:
            graph = graph_resp.json()
    except Exception:
        pass

    # Fallback default mock data if requests fail
    if not kpis:
        kpis = {
            "correlated_incidents": 3,
            "confidence_score": 0.95,
            "campaign_coverage_pct": 84.5,
            "top_adversary_technique": "T1110 (Brute Force)",
            "total_indicators": 6
        }

    # 2. Render Top KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Correlated Incidents</div>
              <div class="metric-value" style="color:var(--accent);">{kpis.get("correlated_incidents", 0)}</div>
              <div class="metric-trend green">▲ Active Links</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Intelligence Confidence</div>
              <div class="metric-value">{int(kpis.get("confidence_score", 0.94) * 100)} %</div>
              <div class="metric-trend green">▲ Trusted Feeds</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Campaign Coverage</div>
              <div class="metric-value">{kpis.get("campaign_coverage_pct", 84.5)} %</div>
              <div class="metric-trend green">▲ MITRE Mapped</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Adversary Technique</div>
              <div class="metric-value" style="font-size: 1.1rem; line-height: 1.8rem; font-weight:700; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{kpis.get("top_adversary_technique", "T1110")}</div>
              <div class="metric-trend danger">▲ Max Activity</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Total Seeded IOCs</div>
              <div class="metric-value">{kpis.get("total_indicators", 6)}</div>
              <div class="metric-trend green">▲ Threat Indicators</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. Main Workspace Grid: Interactive Graph & Filters (3/4) | AI Insights Panel (1/4)
    col_left, col_right = st.columns([3, 1])

    with col_left:
        with st.container(border=True):
            st.markdown('<div class="card-title">🛡️ Threat Correlation Graph</div>', unsafe_allow_html=True)
            
            # Filters
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                search_query = st.text_input("🔍 Search Entities (e.g. IP, Case, T1110)", "").strip()
            with f_col2:
                filter_type = st.multiselect(
                    "Filter Node Types",
                    options=["IP", "Domain", "URL", "Hash", "Case", "Rule", "Simulation", "Workflow", "MITRE"],
                    default=["IP", "Domain", "URL", "Hash", "Case", "Rule", "Simulation", "Workflow", "MITRE"]
                )
            with f_col3:
                show_isolated = st.toggle("Show Unconnected Indicators", value=True)

            # Node Filter & Path Selection logic
            raw_nodes = graph.get("nodes", [])
            raw_edges = graph.get("edges", [])

            # Filter nodes by type & search
            filtered_nodes = []
            for n in raw_nodes:
                if n["type"] not in filter_type:
                    continue
                if search_query and (search_query.lower() not in n["label"].lower() and search_query.lower() not in n["id"].lower()):
                    continue
                filtered_nodes.append(n)

            # Keep edges only if both source and target exist in filtered nodes
            filtered_node_ids = {n["id"] for n in filtered_nodes}
            filtered_edges = []
            connected_node_ids = set()

            for e in raw_edges:
                if e["source"] in filtered_node_ids and e["target"] in filtered_node_ids:
                    filtered_edges.append(e)
                    connected_node_ids.add(e["source"])
                    connected_node_ids.add(e["target"])

            # Filter out isolated nodes if show_isolated is false
            if not show_isolated:
                filtered_nodes = [n for n in filtered_nodes if n["id"] in connected_node_ids]

            # Render Graph Layout
            if not filtered_nodes:
                st.info("No matching nodes found. Broaden your search parameters.")
            else:
                # Coordinate mapping logic
                width, height = 800, 480
                coords = {}
                col_width = width / 4
                
                # Partition nodes into columns
                cols_dict: Dict[int, List[Dict[str, Any]]] = {0: [], 1: [], 2: [], 3: []}
                for node in filtered_nodes:
                    ntype = node["type"]
                    if ntype in ["IP", "Domain", "URL", "Hash"]:
                        col = 0
                    elif ntype in ["Rule", "MITRE"]:
                        col = 1
                    elif ntype == "Case":
                        col = 2
                    else: # Simulation, Workflow
                        col = 3
                    cols_dict[col].append(node)

                for col, nodes in cols_dict.items():
                    total_in_col = len(nodes)
                    for i, node in enumerate(nodes):
                        x = (col + 0.5) * col_width
                        if total_in_col == 1:
                            y = height / 2
                        else:
                            y = 40 + i * ((height - 80) / (total_in_col - 1)) if total_in_col > 1 else height / 2
                        coords[node["id"]] = (x, y)

                # Render SVG Canvas
                svg_lines = []
                
                # Draw edges
                for edge in filtered_edges:
                    s, t = edge["source"], edge["target"]
                    if s in coords and t in coords:
                        x1, y1 = coords[s]
                        x2, y2 = coords[t]
                        rel = edge["relationship"]
                        svg_lines.append(
                            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="4,4" />'
                        )
                        # Rel label on line midpoint
                        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                        svg_lines.append(
                            f'<text x="{mx}" y="{my - 4}" text-anchor="middle" fill="var(--text-secondary)" font-size="8px">{rel}</text>'
                        )

                # Draw nodes
                for node in filtered_nodes:
                    node_id = node["id"]
                    if node_id in coords:
                        x, y = coords[node_id]
                        ntype = node["type"]
                        
                        # Determine node visual colors
                        fill_color = "var(--primary)"
                        if ntype == "Case":
                            fill_color = "var(--accent)"
                        elif ntype == "Rule":
                            fill_color = "#f39c12"  # Amber warning
                        elif ntype == "Simulation":
                            fill_color = "#9b59b6"  # Purple purple team
                        elif ntype == "Workflow":
                            fill_color = "#2ecc71"  # Emerald success
                        elif ntype == "MITRE":
                            fill_color = "#e74c3c"  # Red MITRE
                            
                        # Highlight searched node
                        stroke_color = "var(--primary)" if search_query and search_query.lower() in node["label"].lower() else "var(--card-bg)"
                        stroke_width = 3 if stroke_color != "var(--card-bg)" else 1.5

                        svg_lines.append(
                            f'<circle cx="{x}" cy="{y}" r="11" fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" />'
                        )
                        # Label text
                        svg_lines.append(
                            f'<text x="{x}" y="{y - 16}" text-anchor="middle" fill="var(--text-primary)" font-size="9px" font-weight="600">{node["label"]}</text>'
                        )

                svg_content = f"""
                <svg width="100%" height="{height}px" style="background-color: var(--card-bg-sec); border: 1px solid var(--border-color); border-radius: 8px; font-family: sans-serif;">
                  {"".join(svg_lines)}
                </svg>
                """
                st.markdown(svg_content, unsafe_allow_html=True)

        # Evolution timeline details
        with st.container(border=True):
            st.markdown('<div class="card-title">⏳ Intelligence Evolution Timeline</div>', unsafe_allow_html=True)
            
            timeline_events = [
                {"time": "12:04:12", "event": "Threat Indicator Seeding", "detail": "6 malicious IOC indicators successfully synchronised from emerging threat lists.", "status": "Info"},
                {"time": "12:04:14", "event": "Correlation Link Auto-computed", "detail": "IP address 198.51.100.42 automatically matched to Case 'CASE-2026-001'.", "status": "Success"},
                {"time": "12:04:16", "event": "SOAR Workflow Hook Triggered", "detail": "Case ID CASE-2026-001 connected to auto-isolate workflow execution run.", "status": "Success"}
            ]
            
            for te in timeline_events:
                st.markdown(
                    f"""
                    <div style="display:flex; gap:1rem; align-items:flex-start; padding: 0.5rem; margin-bottom: 0.5rem; border-bottom: 1px solid var(--border-color);">
                      <div style="font-family:monospace; color:var(--primary); font-size:0.8rem; font-weight:700;">{te["time"]}</div>
                      <div>
                        <div style="font-size:0.85rem; font-weight:700; color:var(--text-primary);">{te["event"]}</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary);">{te["detail"]}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with col_right:
        # AI assistant reasoning console (reusing AIWidget layout)
        st.markdown(
            """
            <div style="padding:1rem; background: linear-gradient(135deg, var(--card-bg) 0%, var(--card-bg-sec) 100%); border: 1px solid var(--border-color); border-radius: 12px; margin-bottom:1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
              <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem;">
                <svg style="width:20px; height:20px; color:var(--primary);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12A10 10 0 0 1 12 2z"/>
                  <path d="M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/>
                </svg>
                <span style="font-size:0.85rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-primary);">AI Intelligence Fusion</span>
              </div>
              <p style="font-size:0.75rem; color:var(--text-secondary); margin:0 0 1rem 0;">Ask Copilot to analyze campaign paths, cluster risk nodes, and suggest mitigation playbooks.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.subheader("🤖 Intelligence Query Prompt")
            prompt_option = st.radio(
                "Select Query Template",
                ["Summarize active campaign threat path", "Identify high-risk clusters", "Suggest proactive threat hunt query"]
            )
            
            if st.button("Generate AI Insights Analysis", use_container_width=True):
                with st.spinner("Analyzing graph linkages and indicators..."):
                    try:
                        payload = {"prompt": prompt_option}
                        resp = requests.post(f"{api_base}/api/soar/intelligence/ai-assistant", json=payload, headers=headers, timeout=5, verify=False)
                        if resp.status_code == 200:
                            st.markdown(resp.json().get("answer", ""))
                        else:
                            st.error("Failed to generate AI insights.")
                    except Exception as e:
                        st.error(f"Error querying AI Assistant: {e}")
            else:
                st.info("Click 'Generate AI Insights Analysis' to run campaign checks.")
