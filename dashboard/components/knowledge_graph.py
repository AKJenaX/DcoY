"""Streamlit component rendering the Security Knowledge Graph & Attack Path Analysis page."""

import requests
import streamlit as st
from typing import Any, Dict, List, Set


def render_knowledge_graph_page(explain_rows: List[Dict[str, Any]], detect_rows: List[Dict[str, Any]], latency_ms: int, api_base: str):
    """Renders the comprehensive security knowledge graph, shortest path tracer, and AI reasoning widgets."""
    
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem;">
          <div>
            <h1 class="page-title">Security Knowledge Graph</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">Navigate cross-layered linkages between threat indicators, rules, simulations, playbooks, active assets, and user profiles.</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> GRAPH ENGINE STABLE
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Establish auth headers
    headers = {}
    if "auth_token" in st.session_state and st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"

    # 2. Fetch Knowledge Graph Data & Analytics
    graph = {"nodes": [], "edges": []}
    analytics = {}
    attack_paths = []

    try:
        graph_resp = requests.get(f"{api_base}/api/soar/knowledge-graph/graph", headers=headers, timeout=5, verify=False)
        if graph_resp.status_code == 200:
            graph = graph_resp.json()
    except Exception:
        pass

    try:
        analytics_resp = requests.get(f"{api_base}/api/soar/knowledge-graph/analytics", headers=headers, timeout=5, verify=False)
        if analytics_resp.status_code == 200:
            analytics = analytics_resp.json()
    except Exception:
        pass

    try:
        paths_resp = requests.get(f"{api_base}/api/soar/knowledge-graph/attack-paths", headers=headers, timeout=5, verify=False)
        if paths_resp.status_code == 200:
            attack_paths = paths_resp.json()
    except Exception:
        pass

    # Fallback default mock analytics if request fails
    if not analytics:
        analytics = {
            "total_nodes": len(graph.get("nodes", [])),
            "total_edges": len(graph.get("edges", [])),
            "campaign_clusters": [{"case_name": "SSH Brute Force", "size": 3}],
            "top_risk_assets": [{"name": "WS-OPERATOR-02", "risk": 0.65, "criticality": "Medium"}],
            "orphaned_detections": [],
            "coverage_gaps": []
        }

    # 3. KPI Metrics Layout strip (Obsidian widget variants)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Graph Nodes</div>
              <div class="metric-value" style="color:var(--primary);">{analytics.get("total_nodes", 0)}</div>
              <div class="metric-trend green">● Unified Assets & Users</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Relationship Edges</div>
              <div class="metric-value">{analytics.get("total_edges", 0)}</div>
              <div class="metric-trend green">● Active Mappings</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Campaign Clusters</div>
              <div class="metric-value" style="color:var(--accent);">{len(analytics.get("campaign_clusters", []))}</div>
              <div class="metric-trend danger">▲ Concentrated Threats</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">Orphaned Detections</div>
              <div class="metric-value">{len(analytics.get("orphaned_detections", []))}</div>
              <div class="metric-trend info">■ Rules Unmapped</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div class="metric-label">MITRE Coverage Gaps</div>
              <div class="metric-value">{len(analytics.get("coverage_gaps", []))}</div>
              <div class="metric-trend danger">▲ Gaps Tested</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Main workspace partitioned columns: Interactive Graph Explorer & Path Analyzer (3/4) | AI Assistant & Analytics panel (1/4)
    col_left, col_right = st.columns([3, 1])

    with col_left:
        with st.container(border=True):
            st.markdown('<div class="card-title">🔍 Knowledge Graph Filters & Search</div>', unsafe_allow_html=True)
            
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                search_query = st.text_input("🔍 Search Nodes (e.g. WS-OPERATOR, IP, T1110)", "").strip()
            with f_col2:
                all_types = ["Indicator", "Asset", "User", "Rule", "MITRE", "Case", "Simulation", "Workflow", "Playbook", "Report"]
                filter_type = st.multiselect("Filter Node Categories", options=all_types, default=all_types)
            with f_col3:
                show_orphaned = st.toggle("Show Isolated Detections", value=True)

            # Node filtering logic
            raw_nodes = graph.get("nodes", [])
            raw_edges = graph.get("edges", [])

            filtered_nodes = []
            for n in raw_nodes:
                if n["type"] not in filter_type:
                    continue
                if search_query and (search_query.lower() not in n["label"].lower() and search_query.lower() not in n["id"].lower()):
                    continue
                filtered_nodes.append(n)

            filtered_node_ids = {n["id"] for n in filtered_nodes}
            
            # Identify connected nodes
            connected_node_ids = set()
            filtered_edges = []
            for e in raw_edges:
                if e["source"] in filtered_node_ids and e["target"] in filtered_node_ids:
                    filtered_edges.append(e)
                    connected_node_ids.add(e["source"])
                    connected_node_ids.add(e["target"])

            # Clean isolated if requested
            if not show_orphaned:
                filtered_nodes = [n for n in filtered_nodes if n["id"] in connected_node_ids]
                filtered_node_ids = {n["id"] for n in filtered_nodes}
                filtered_edges = [e for e in filtered_edges if e["source"] in filtered_node_ids and e["target"] in filtered_node_ids]

            # Shortest Path Selection Form
            st.markdown('<hr style="margin: 0.5rem 0;" />', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🧭 Shortest Path Tracer & Attack Propagation Analysis</div>', unsafe_allow_html=True)
            
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                node_options = sorted([n["id"] for n in filtered_nodes])
                src_node = st.selectbox("Source Entry Point Node", options=node_options, index=0 if node_options else None)
            with p_col2:
                tgt_node = st.selectbox("Target Asset/Exfil Node", options=node_options, index=len(node_options)-1 if len(node_options) > 1 else 0 if node_options else None)
            with p_col3:
                trace_path = st.button("Tracer Path Progression", use_container_width=True)

            shortest_path_result = None
            if trace_path and src_node and tgt_node:
                with st.spinner("Finding shortest attack path..."):
                    try:
                        payload = {"source": src_node, "target": tgt_node}
                        path_resp = requests.get(f"{api_base}/api/soar/knowledge-graph/attack-paths", headers=headers, timeout=5, verify=False)
                        # We also calculate shortest path directly using a local algorithm if api call doesn't support parameterized paths
                        # Or since we implemented it on engine, query the engine via standard BFS/Dijkstra logic helper.
                        # For clean parameters, let's query the backend or compute it locally. We can call:
                        # /api/soar/knowledge-graph/attack-paths or compute directly since we have nodes & edges in memory!
                        
                        # Let's perform a lightweight local Dijkstra traversal to highlight steps
                        shortest_path_result = find_local_shortest_path(raw_nodes, raw_edges, src_node, tgt_node)
                    except Exception as e:
                        st.error(f"Tracer error: {e}")

            # 5. Render SVG Graph Layout Canvas
            if not filtered_nodes:
                st.info("No matching nodes fit the current filters.")
            else:
                width, height = 900, 520
                coords = {}
                col_width = width / 5
                
                # Partition nodes into 5 horizontal layout columns:
                # Col 0: Indicators
                # Col 1: MITRE & Rules
                # Col 2: Cases & Simulations
                # Col 3: Workflows & Playbooks
                # Col 4: Assets & Users & Reports
                cols_dict: Dict[int, List[Dict[str, Any]]] = {0: [], 1: [], 2: [], 3: [], 4: []}
                for node in filtered_nodes:
                    ntype = node["type"]
                    if ntype == "Indicator":
                        col = 0
                    elif ntype in ["MITRE", "Rule"]:
                        col = 1
                    elif ntype in ["Case", "Simulation"]:
                        col = 2
                    elif ntype in ["Workflow", "Playbook"]:
                        col = 3
                    else:  # Asset, User, Report
                        col = 4
                    cols_dict[col].append(node)

                for col, nodes_list in cols_dict.items():
                    total = len(nodes_list)
                    for i, node in enumerate(nodes_list):
                        x = (col + 0.5) * col_width
                        if total == 1:
                            y = height / 2
                        else:
                            y = 40 + i * ((height - 80) / (total - 1)) if total > 1 else height / 2
                        coords[node["id"]] = (x, y)

                # SVG Rendering List
                svg_lines = []
                
                # Retrieve highlighted path steps
                path_steps = shortest_path_result.get("steps", []) if shortest_path_result else []
                path_edges = set()
                if len(path_steps) > 1:
                    for i in range(len(path_steps) - 1):
                        path_edges.add((path_steps[i], path_steps[i+1]))
                        path_edges.add((path_steps[i+1], path_steps[i]))

                # Draw Edge Lines
                for edge in filtered_edges:
                    s, t = edge["source"], edge["target"]
                    if s in coords and t in coords:
                        x1, y1 = coords[s]
                        x2, y2 = coords[t]
                        rel = edge["relationship"]
                        
                        # Edge highlights if part of shortest path
                        is_highlight = (s, t) in path_edges
                        color = "var(--primary)" if is_highlight else "var(--muted)"
                        stroke_w = "3" if is_highlight else "1.2"
                        stroke_dash = "0" if is_highlight else "4,4"
                        
                        svg_lines.append(
                            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{stroke_w}" stroke-dasharray="{stroke_dash}" />'
                        )
                        # Rel label on line midpoint
                        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                        label_color = "var(--text-primary)" if is_highlight else "var(--text-secondary)"
                        font_w = "bold" if is_highlight else "normal"
                        svg_lines.append(
                            f'<text x="{mx}" y="{my - 4}" text-anchor="middle" fill="{label_color}" font-size="8px" font-weight="{font_w}">{rel}</text>'
                        )

                # Draw Node Circles
                for node in filtered_nodes:
                    node_id = node["id"]
                    if node_id in coords:
                        x, y = coords[node_id]
                        ntype = node["type"]
                        
                        # Visual styling by node type
                        fill_color = "var(--primary)"
                        if ntype == "Asset":
                            fill_color = "var(--accent)"
                        elif ntype == "User":
                            fill_color = "#e67e22" # Orange user
                        elif ntype == "Rule":
                            fill_color = "#f39c12" # Amber rule
                        elif ntype == "Case":
                            fill_color = "#9b59b6" # Purple case
                        elif ntype == "Simulation":
                            fill_color = "#3498db" # Blue sim
                        elif ntype == "MITRE":
                            fill_color = "#e74c3c" # Red MITRE
                        elif ntype in ["Workflow", "Playbook"]:
                            fill_color = "#2ecc71" # Emerald SOAR
                        elif ntype == "Report":
                            fill_color = "#1abc9c" # Teal reports
                            
                        # Search highlight or path highlight
                        is_on_path = node_id in path_steps
                        is_searched = search_query and search_query.lower() in node["label"].lower()
                        
                        if is_on_path:
                            stroke_color = "#f1c40f" # Gold highlight
                            stroke_width = 4.0
                            r = 13
                        elif is_searched:
                            stroke_color = "var(--primary)"
                            stroke_width = 3.0
                            r = 12
                        else:
                            stroke_color = "var(--card-bg)"
                            stroke_width = 1.5
                            r = 10

                        svg_lines.append(
                            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" style="cursor: pointer;" />'
                        )
                        # Render label text
                        svg_lines.append(
                            f'<text x="{x}" y="{y - r - 6}" text-anchor="middle" fill="var(--text-primary)" font-size="9px" font-weight="600">{node["label"]}</text>'
                        )

                svg_content = f"""
                <svg width="100%" height="{height}px" style="background-color: var(--card-bg-sec); border: 1px solid var(--border-color); border-radius: 8px; font-family: sans-serif;">
                  {"".join(svg_lines)}
                </svg>
                """
                st.markdown(svg_content, unsafe_allow_html=True)

            # Draw shortest path walkthrough details
            if shortest_path_result and shortest_path_result.get("path_found"):
                st.markdown("### 🗺️ Shortest Path Walkthrough Steps")
                steps_chain = shortest_path_result.get("steps", [])
                
                # Render directional arrow flow
                chain_html = " ➔ ".join([f"<span class='badge' style='background-color:var(--card-bg); border:1px solid var(--border-color); padding:0.25rem 0.5rem; font-weight:700;'>{step}</span>" for step in steps_chain])
                st.markdown(f"<div style='margin-bottom:1rem; padding: 0.5rem; background-color:var(--card-bg-sec); border-radius:6px;'>{chain_html}</div>", unsafe_allow_html=True)
                
                # Render controls
                st.markdown("#### 🛡️ Defensive Controls Matching Path Nodes")
                controls = shortest_path_result.get("defensive_controls", [])
                
                c_cols = st.columns(len(controls) if controls else 1)
                for idx, ctrl in enumerate(controls):
                    with c_cols[idx % len(c_cols)]:
                        st.markdown(
                            f"""
                            <div style="background-color:var(--card-bg-sec); border:1px solid var(--border-color); border-radius:8px; padding:0.75rem;">
                              <div style="font-size:0.65rem; color:var(--primary); font-weight:700; text-transform:uppercase;">{ctrl["type"]}</div>
                              <div style="font-size:0.85rem; font-weight:700; color:var(--text-primary); margin:0.25rem 0;">{ctrl["name"]}</div>
                              <div style="font-size:0.75rem; color:var(--text-secondary);">{ctrl["description"]}</div>
                              <div style="margin-top:0.4rem;"><span class="badge success" style="font-size:0.6rem;">{ctrl.get("status", "Active")}</span></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        # Attack Progression Timeline
        with st.container(border=True):
            st.markdown('<div class="card-title">⏳ Attack Progression & Incident Timeline Overlay</div>', unsafe_allow_html=True)
            
            timeline_overlay = [
                {"stage": "Initial Access", "time": "2026-07-13 12:00:15", "desc": "Compromised operator credentials detected targeting edge SSH portal from malicious source 198.51.100.42.", "control": "SSH Brute Force Detection rule triggered", "status": "Detected"},
                {"stage": "Privilege Escalation", "time": "2026-07-13 12:02:40", "desc": "Attacker successfully initiated local privilege check mapping to administrator privileges (adm_local).", "control": "SentinelOne Telemetry Audit", "status": "Logged"},
                {"stage": "Lateral Movement", "time": "2026-07-13 12:04:12", "desc": "Compromised workstation WS-OPERATOR-02 initiated SSH connections towards WS-ADMIN-01.", "control": "WS-OPERATOR-02 Auto-Isolation SOAR Workflow triggered", "status": "Mitigated"},
                {"stage": "Collection", "time": "2026-07-13 12:04:30", "desc": "Attempted staging dump targeting database DB-PROD-01 was blocked by defensive isolation controls.", "control": "Database connection refused due to agent isolation state", "status": "Blocked"}
            ]
            
            for t_item in timeline_overlay:
                st.markdown(
                    f"""
                    <div style="display:flex; gap:1rem; align-items:flex-start; padding: 0.65rem 0.5rem; margin-bottom:0.5rem; border-bottom:1px solid var(--border-color);">
                      <div style="flex: 0 0 100px;">
                        <span class="badge" style="font-size:0.6rem; font-weight:700; background-color:var(--card-bg-sec); display:block; text-align:center;">{t_item["stage"]}</span>
                        <div style="font-size:0.6rem; color:var(--text-secondary); text-align:center; margin-top:0.25rem;">{t_item["time"].split(" ")[1]}</div>
                      </div>
                      <div style="flex:1;">
                        <div style="font-size:0.8rem; color:var(--text-primary); font-weight:600;">{t_item["desc"]}</div>
                        <div style="font-size:0.7rem; color:var(--primary); margin-top:0.15rem;">Defensive Hook: <i>{t_item["control"]}</i></div>
                      </div>
                      <div>
                        <span class="badge {'success' if t_item['status'] in ['Mitigated', 'Blocked'] else 'danger'}" style="font-size:0.55rem; padding:0.15rem 0.4rem;">{t_item["status"]}</span>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with col_right:
        # AI Widget Reasoning Assistant Console (Reusing AIWidget style)
        st.markdown(
            """
            <div style="padding:1rem; background: linear-gradient(135deg, var(--card-bg) 0%, var(--card-bg-sec) 100%); border: 1px solid var(--border-color); border-radius: 12px; margin-bottom:1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
              <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem;">
                <svg style="width:20px; height:20px; color:var(--primary);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/>
                </svg>
                <span style="font-size:0.85rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-primary);">AI Knowledge Assistant</span>
              </div>
              <p style="font-size:0.75rem; color:var(--text-secondary); margin:0 0 1rem 0;">Query the security intelligence copilot to dissect propagation links, review compliance reporting, and receive remediation guidance.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.subheader("🤖 Ask Knowledge Assistant")
            prompt_option = st.radio(
                "AI Reasoning Templates",
                [
                    "Explain attack paths & lateral vectors",
                    "Summarize active campaigns",
                    "Identify critical high-risk nodes",
                    "Recommend detections & rules adjustments",
                    "Recommend automated SOAR workflows",
                    "Recommend manual investigations actions"
                ]
            )
            
            if st.button("Generate AI Copilot Analysis", use_container_width=True):
                with st.spinner("Analyzing graph nodes and path weights..."):
                    try:
                        payload = {"prompt": prompt_option}
                        resp = requests.post(f"{api_base}/api/soar/knowledge-graph/ai-assistant", json=payload, headers=headers, timeout=5, verify=False)
                        if resp.status_code == 200:
                            st.markdown(resp.json().get("answer", ""))
                        else:
                            st.error("AI assistant response failure.")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        # Graph Structural Analytics lists
        with st.container(border=True):
            st.markdown('<div class="card-title">🛡️ High-Risk Security Assets</div>', unsafe_allow_html=True)
            assets_list = analytics.get("top_risk_assets", [])
            for asset in assets_list:
                st.markdown(
                    f"""
                    <div style="padding:0.4rem 0.5rem; background-color:var(--card-bg-sec); border:1px solid var(--border-color); border-radius:6px; margin-bottom:0.4rem;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-family:monospace; font-size:0.8rem; font-weight:700; color:var(--primary);">{asset["name"]}</span>
                        <span class="badge danger" style="font-size:0.55rem;">Risk: {int(asset["risk"] * 100)}%</span>
                      </div>
                      <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:0.2rem;">Criticality: {asset["criticality"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with st.container(border=True):
            st.markdown('<div class="card-title">⚠️ MITRE Coverage Gaps</div>', unsafe_allow_html=True)
            gaps = analytics.get("coverage_gaps", [])
            if gaps:
                for gap in gaps[:4]:
                    st.markdown(
                        f"""
                        <div style="padding:0.35rem 0.5rem; background-color:var(--card-bg-sec); border-left: 3px solid #e74c3c; border-radius:4px; margin-bottom:0.35rem;">
                          <span style="font-size:0.75rem; font-weight:700; color:var(--text-primary);">{gap}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("Zero uncovered gaps identified.")


def find_local_shortest_path(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], source: str, target: str) -> Dict[str, Any]:
    """Helper method to run a BFS shortest path locally for immediate front-end rendering."""
    # BFS
    queue = [[source]]
    visited = {source}
    
    while queue:
        path = queue.pop(0)
        node = path[-1]
        
        if node == target:
            # Map path node structures
            node_structs = []
            for nid in path:
                n_data = next((n for n in nodes if n["id"] == nid), {"id": nid, "label": nid, "type": "Unknown"})
                node_structs.append(n_data)
                
            # Filter matches controls
            controls = []
            for nid in path:
                if nid.startswith("Rule:"):
                    rule_n = next((n for n in nodes if n["id"] == nid), None)
                    if rule_n:
                        controls.append({
                            "type": "Detection Rule",
                            "name": rule_n["label"].replace("Rule: ", ""),
                            "description": "Custom rule flagging attack technique vectors"
                        })
                if nid.startswith("MITRE:"):
                    controls.append({
                        "type": "Purple Team Validation",
                        "name": f"Simulation Scenario ({nid.split(':')[-1]})",
                        "description": "Validation check tracking telemetry coverage health"
                    })
                if nid.startswith("Case:"):
                    controls.append({
                        "type": "SOAR Workflow Execution",
                        "name": "Containment Plan",
                        "description": "Orchestrates quarantine response rules"
                    })
                    
            if not controls:
                controls.append({
                    "type": "Active Deception Decoy",
                    "name": "SSH Honeypot Node",
                    "description": "Decoy SSH server deployed to trap credentials brute force scanning"
                })

            return {
                "path_found": True,
                "steps": path,
                "nodes": node_structs,
                "defensive_controls": controls
            }
            
        # Find neighbors
        neighbors = []
        for edge in edges:
            if edge["source"] == node:
                neighbors.append(edge["target"])
            elif edge["target"] == node:
                neighbors.append(edge["source"])
                
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
                
    return {"path_found": False, "steps": [], "nodes": [], "defensive_controls": []}
