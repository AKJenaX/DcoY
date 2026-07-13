"""Global Search Component for rendering search matches and handling navigation redirects."""

import requests
import streamlit as st
from typing import Any, Dict


def render_global_search_results(api_base: str):
    """Renders the global search interface and processes selection redirects."""
    
    # 1. Fetch query parameters
    query = st.query_params.get("search", "").strip()
    
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
          <h1 class="page-title">Global Search Results</h1>
          <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">Search results for: <b>"{query}"</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not query:
        st.warning("Please enter a search query in the search bar above.")
        return

    # 2. Query search endpoint
    headers = {}
    if "auth_token" in st.session_state and st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"

    results = {}
    with st.spinner("Searching platform registry..."):
        try:
            r = requests.get(f"{api_base}/api/soar/platform/search", params={"query": query}, headers=headers, timeout=5, verify=False)
            if r.status_code == 200:
                results = r.json()
        except Exception as e:
            st.error(f"Search query error: {e}")

    if not results or not any(results.values()):
        st.info("No matching indicators, assets, users, cases, playbooks, or simulations found.")
        return

    # 3. Render categorized search results
    categories_labels = {
        "indicators": "🔍 Threat Indicators (IPs, Hashes, Domains)",
        "assets": "🖥️ Enterprise Assets",
        "users": "👤 User Accounts",
        "rules": "🛡️ Detection Rules",
        "cases": "📁 Cases & Investigations",
        "playbooks": "📖 Incident Response Playbooks",
        "workflows": "⚙️ SOAR Workflows",
        "simulations": "🎯 Attack Simulations",
        "reports": "📊 Executive Reports"
    }

    found_any = False
    for key, label in categories_labels.items():
        items = results.get(key, [])
        if not items:
            continue
            
        found_any = True
        st.markdown(f"### {label}")
        
        # Grid of results
        for idx, item in enumerate(items):
            with st.container(border=True):
                col_left, col_right = st.columns([4, 1])
                with col_left:
                    st.markdown(f"**{item['title']}**")
                    st.markdown(f"<span style='font-size:0.8rem; color:var(--text-secondary);'>{item['subtitle']}</span>", unsafe_allow_html=True)
                with col_right:
                    # Renders a navigate button
                    btn_label = f"Inspect"
                    if st.button(f"{btn_label} ##{key}_{idx}", key=f"nav_{key}_{idx}", use_container_width=True):
                        # Configure redirects
                        st.query_params["page"] = item["route"]
                        if item["entity_type"] == "Case":
                            st.session_state.active_case_id = item["entity_id"]
                        elif item["entity_type"] in ["Asset", "User", "Indicator"]:
                            st.session_state.active_entity = {
                                "id": item["entity_id"],
                                "type": item["entity_type"]
                            }
                        st.rerun()

    if not found_any:
        st.info("No matching results found. Broaden your search term.")
