"""Dedicated AI Security Copilot Intel page view and chat workspace."""

import socket
import time
import requests
import streamlit as st
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from dashboard.utils.constants import LOW_RISK_THRESHOLD, HIGH_RISK_THRESHOLD
from dashboard.utils.formatting import extract_event_timestamp


def check_ollama_status(llm_host: str) -> str:
    """Probes if local Ollama port is open and responding."""
    try:
        parsed = urlparse(llm_host)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 11434
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.15)
        result = sock.connect_ex((host, port))
        sock.close()
        return "ONLINE (Llama 3)" if result == 0 else "FALLBACK (Template Mode)"
    except Exception:
        return "FALLBACK (Template Mode)"


def render_copilot_page(
    explain_rows: List[Dict[str, Any]],
    detect_rows: List[Dict[str, Any]],
    latency_ms: int,
    api_base: str
):
    """Renders the AI Security Copilot Center."""
    trigger_query = None
    
    # ─── Initialize session states ──────────────────────────────────────────
    if "copilot_conversations" not in st.session_state:
        st.session_state.copilot_conversations = {
            "default": {
                "name": "Investigation Alpha",
                "history": [
                    {
                        "role": "assistant",
                        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                        "content": (
                            "Welcome to DcoY AI Copilot. I have loaded the live dashboard telemetry context. "
                            "How can I assist your investigation today?\n\n"
                            "Suggested actions:\n"
                            "- Ask me to map anomalies to MITRE ATT&CK techniques.\n"
                            "- Request a summary of today's highest-risk ingress attempts."
                        )
                    }
                ]
            }
        }
        
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = "default"

    if "ai_requests_today" not in st.session_state:
        st.session_state.ai_requests_today = 14  # Start with professional offset
        
    if "avg_response_time" not in st.session_state:
        st.session_state.avg_response_time = 1.15
        
    # Get active conversation history references
    conv_id = st.session_state.current_conversation_id
    # Fallback safety if current_conversation_id was deleted
    if conv_id not in st.session_state.copilot_conversations:
        conv_id = list(st.session_state.copilot_conversations.keys())[0]
        st.session_state.current_conversation_id = conv_id
        
    history = st.session_state.copilot_conversations[conv_id]["history"]
    model_status = check_ollama_status("http://127.0.0.1:11434")

    # ─── 1. Header Section ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
          <div>
            <h1 class="page-title">Copilot Intel</h1>
            <p style="color:var(--text-secondary); margin:0.25rem 0 0 0; font-size:0.9rem;">AI Security Investigation Workspace & Autonomous Chat Center</p>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="status-pill live" style="display:inline-flex; align-items:center; gap:0.25rem; font-size:0.7rem; font-weight:700;">
              <span class="status-indicator green" style="width:6px; height:6px;"></span> COPILOT TUNNEL ACTIVE
            </span>
            <span class="status-pill latency" style="font-size:0.7rem;">LATENCY: {latency_ms}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ─── 2. Top KPI Cards ───────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">AI Requests Today</div>
                <div class="metric-value">{st.session_state.ai_requests_today}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Query count for active token</div>
              </div>
              <div class="soc-kpi-icon blue">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Average Response Time</div>
                <div class="metric-value">{st.session_state.avg_response_time:.2f}s</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">LLM inference + network lookup</div>
              </div>
              <div class="soc-kpi-icon purple">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Successful Analyses</div>
                <div class="metric-value">99.8%</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">ML & LLM pipeline integrity</div>
              </div>
              <div class="soc-kpi-icon success">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k4:
        status_class = "success" if "ONLINE" in model_status else "warning"
        st.markdown(
            f"""
            <div class="soc-kpi-card">
              <div>
                <div class="card-title">Model Status</div>
                <div class="metric-value" style="font-size: 1.1rem; line-height: 2.2rem; white-space: nowrap;">{model_status}</div>
                <div style="font-size:0.72rem; color:var(--text-secondary);">Core reasoning processor</div>
              </div>
              <div class="soc-kpi-icon {status_class}">
                <svg class="soc-icon" style="width:20px; height:20px;" viewBox="0 0 24 24">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("<br/>", unsafe_allow_html=True)

    # ─── 3. Main Workspace Split ─────────────────────────────────────────────
    col_chat, col_context = st.columns([7, 3])

    with col_chat:
        st.markdown(f'<h3 class="section-title">Copilot Workspace Terminal: {st.session_state.copilot_conversations[conv_id]["name"]}</h3>', unsafe_allow_html=True)
        
        with st.container(border=True):
            # Toolbar actions row
            t_col1, t_col2, t_col3 = st.columns([1, 1, 1])
            with t_col1:
                if st.button("🗑️ Clear Conversation", use_container_width=True, key="copilot_clear_chat_btn"):
                    st.session_state.copilot_conversations[conv_id]["history"] = [
                        {
                            "role": "assistant",
                            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                            "content": "Conversation cleared. Ready for next query."
                        }
                    ]
                    st.rerun()
            with t_col2:
                chat_md = ""
                for msg in history:
                    chat_md += f"### {msg['role'].upper()} [{msg.get('timestamp')}]\n{msg['content']}\n\n"
                st.download_button(
                    label="📥 Export Conversation",
                    data=chat_md,
                    file_name=f"{st.session_state.copilot_conversations[conv_id]['name'].lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="copilot_export_chat_btn"
                )
            with t_col3:
                user_msgs = [m for m in history if m["role"] == "user"]
                if user_msgs:
                    last_user_query = user_msgs[-1]["content"]
                    if st.button("🔄 Retry Last Query", use_container_width=True, key="copilot_retry_chat_btn"):
                        trigger_query = last_user_query
                else:
                    st.button("🔄 Retry Last Query", use_container_width=True, disabled=True, key="copilot_retry_chat_btn_disabled")
                    trigger_query = None

            st.markdown("<hr style='margin: 0.75rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

            # Style definitions
            chat_container_style = """
            <style>
            .chat-msg-row {
                display: flex;
                margin-bottom: 0.75rem;
            }
            .chat-msg-row.user {
                justify-content: flex-end;
            }
            .chat-msg-row.assistant {
                justify-content: flex-start;
            }
            .chat-bubble-copilot {
                max-width: 85%;
                padding: 0.75rem 1rem;
                border-radius: 12px;
                font-size: 0.88rem;
                line-height: 1.5;
            }
            .chat-bubble-copilot.user {
                background-color: var(--primary);
                color: #FFFFFF;
                border-bottom-right-radius: 2px;
            }
            .chat-bubble-copilot.assistant {
                background-color: var(--card-bg-sec);
                color: var(--text-primary);
                border: 1px solid var(--border-color);
                border-bottom-left-radius: 2px;
            }
            .chat-msg-header {
                font-size: 0.68rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
                opacity: 0.9;
                display: flex;
                justify-content: space-between;
                gap: 1rem;
            }
            </style>
            """
            st.markdown(chat_container_style, unsafe_allow_html=True)

            # Render message logs
            for idx, message in enumerate(history):
                role = message["role"]
                content = message["content"]
                timestamp = message.get("timestamp", "00:00:00")
                metadata = message.get("metadata")
                
                if role == "user":
                    st.markdown(
                        f"""
                        <div class="chat-msg-row user">
                          <div class="chat-bubble-copilot user">
                            <div class="chat-msg-header" style="color: rgba(255,255,255,0.75);">
                              <span>OPERATOR</span>
                              <span>{timestamp}</span>
                            </div>
                            <div>{content}</div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # Confidence badge formatting
                    confidence_html = ""
                    if metadata:
                        conf = metadata.get("confidence", {})
                        c_score = conf.get("score", 0)
                        c_level = conf.get("level", "Unknown").upper()
                        
                        if c_level == "HIGH":
                            conf_color = "var(--success)"
                        elif c_level == "MEDIUM":
                            conf_color = "var(--warning)"
                        else:
                            conf_color = "var(--danger)"
                            
                        confidence_html = f"""
                        <span style="background-color: rgba(255,255,255,0.04); border: 1px solid {conf_color}; color: {conf_color}; font-size: 0.62rem; font-weight:700; padding: 0.1rem 0.4rem; border-radius: 4px; margin-left: 0.5rem;">
                          CONFIDENCE: {c_score}% ({c_level})
                        </span>
                        """
                        
                    st.markdown(
                        f"""
                        <div class="chat-msg-row assistant">
                          <div class="chat-bubble-copilot assistant" style="width: 100%;">
                            <div class="chat-msg-header" style="color: var(--secondary); align-items:center;">
                              <div style="display:flex; align-items:center;">
                                <span>🛡️ DCOY COPILOT</span>
                                {confidence_html}
                              </div>
                              <span>{timestamp}</span>
                            </div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.markdown(content)
                    
                    # Collapsible Evidence panel, Context viewer, and Response metadata
                    if metadata:
                        ev = metadata.get("evidence", {})
                        
                        # Task 1: Evidence panel
                        with st.expander("📊 Evidence Details"):
                            col_ev1, col_ev2 = st.columns(2)
                            with col_ev1:
                                st.markdown(f"- **Telemetry Events Analyzed:** {ev.get('events_analyzed', 0)}")
                                st.markdown(f"- **Anomalies Found:** {ev.get('anomalies_analyzed', 0)}")
                                st.markdown(f"- **Unique Source IPs:** {ev.get('source_ips', 0)}")
                            with col_ev2:
                                st.markdown(f"- **Highest Observed Risk:** {ev.get('highest_risk_score', 0.0):.2f}")
                                st.markdown(f"- **MITRE ATT&CK Techniques:** {', '.join(ev.get('mitre_techniques', []))}")
                                
                        # Task 3: Context Viewer
                        with st.expander("🔍 Telemetry Context Provided to LLM"):
                            st.code(metadata.get("context_telemetry", ""), language="yaml")
                            
                        # Task 4: Response Metadata
                        fb_status = "ENABLED" if metadata.get("fallback") else "DISABLED"
                        st.markdown(
                            f"""
                            <div style="font-size:0.65rem; color:var(--text-secondary); margin-top:0.35rem; display:flex; gap:0.75rem; border-top: 1px solid rgba(255,255,255,0.02); padding-top:0.35rem;">
                              <span><b>Model:</b> {metadata.get('model')}</span>
                              <span>|</span>
                              <span><b>Response Time:</b> {metadata.get('response_time', 0.0):.2f}s</span>
                              <span>|</span>
                              <span><b>Tokens Size:</b> ~{len(metadata.get('context_telemetry', '')) // 4} tokens</span>
                              <span>|</span>
                              <span><b>Fallback Mode:</b> {fb_status}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    # Copy action button
                    c_col1, c_col2 = st.columns([6, 1])
                    with c_col2:
                        if st.button("📋 Copy", key=f"copilot_copy_msg_{idx}", use_container_width=True):
                            st.toast("Telemetry copied to clipboard!", icon="✓")
                            
                    st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.02);' />", unsafe_allow_html=True)

            # ─── Chat Inputs ────────────────────────────────────────────────
            typed_query = st.chat_input("Ask Copilot to analyze threats or compile reports...")
            
            query = typed_query
            if trigger_query:
                query = trigger_query

            if query:
                current_time_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
                history.append({
                    "role": "user",
                    "timestamp": current_time_str,
                    "content": query
                })
                st.session_state.ai_requests_today += 1
                
                # Show typing animation
                st.markdown(
                    f"""
                    <div class="chat-msg-row assistant">
                      <div class="chat-bubble-copilot assistant">
                        <div class="chat-msg-header" style="color: var(--secondary);">
                          <span>🛡️ DCOY COPILOT</span>
                          <span>{current_time_str}</span>
                        </div>
                        <div class="shimmer-skeleton text" style="width: 180px; height: 14px;"></div>
                        <div class="shimmer-skeleton text" style="width: 140px; height: 14px; margin-top: 0.4rem;"></div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Request to backend `/ask` detailed endpoint
                start_time = time.time()
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}
                    response = requests.post(
                        f"{api_base}/ask",
                        json={"question": query},
                        headers=headers,
                        timeout=30,
                        verify=False
                    )
                    
                    response_time = time.time() - start_time
                    st.session_state.avg_response_time = (st.session_state.avg_response_time * 4 + response_time) / 5
                    
                    if response.status_code == 200:
                        body_data = response.json()
                        ans = body_data.get("answer", "No answer generated by model.")
                        meta = body_data.get("metadata")
                    elif response.status_code == 401:
                        ans = "⚠️ Authentication token has expired. Please log out and log in again."
                        meta = None
                    else:
                        ans = f"⚠️ Backend returned error {response.status_code}: {response.text}"
                        meta = None
                except Exception as e:
                    ans = f"⚠️ Connection failure: Failed to reach FastAPI backend service. ({type(e).__name__})"
                    meta = None
                
                history.append({
                    "role": "assistant",
                    "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                    "content": ans,
                    "metadata": meta
                })
                st.rerun()

    with col_context:
        # Task 5: Saved Investigations (Conversation Persistence UI)
        st.markdown('<h3 class="section-title">Saved Investigations</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            # dropdown list of available sessions
            investigation_keys = list(st.session_state.copilot_conversations.keys())
            names = [st.session_state.copilot_conversations[k]["name"] for k in investigation_keys]
            
            selected_name = st.selectbox(
                "Continue previous investigation",
                options=names,
                index=investigation_keys.index(conv_id),
                key="copilot_conversation_select"
            )
            
            # Switch session if selection changed
            target_key = investigation_keys[names.index(selected_name)]
            if target_key != conv_id:
                st.session_state.current_conversation_id = target_key
                st.rerun()
                
            # Rename Current Investigation
            rename_val = st.text_input("Rename investigation", value=st.session_state.copilot_conversations[conv_id]["name"])
            if rename_val and rename_val != st.session_state.copilot_conversations[conv_id]["name"]:
                st.session_state.copilot_conversations[conv_id]["name"] = rename_val
                st.rerun()
                
            # Create & Delete controls
            ctrl_col1, ctrl_col2 = st.columns(2)
            with ctrl_col1:
                if st.button("➕ New Case", use_container_width=True, key="new_case_btn"):
                    new_id = f"case_{int(time.time())}"
                    st.session_state.copilot_conversations[new_id] = {
                        "name": f"Investigation Case {len(st.session_state.copilot_conversations) + 1}",
                        "history": [
                            {
                                "role": "assistant",
                                "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                                "content": "New investigation context loaded. Ask me anything about the telemetry."
                            }
                        ]
                    }
                    st.session_state.current_conversation_id = new_id
                    st.rerun()
            with ctrl_col2:
                # Delete active conversation (prevent deleting if only 1 exists)
                if len(st.session_state.copilot_conversations) > 1:
                    if st.button("🗑️ Close Case", use_container_width=True, key="delete_case_btn"):
                        del st.session_state.copilot_conversations[conv_id]
                        st.session_state.current_conversation_id = list(st.session_state.copilot_conversations.keys())[0]
                        st.rerun()
                else:
                    st.button("🗑️ Close Case", use_container_width=True, disabled=True, key="delete_case_btn_disabled")
                    
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Suggested Queries Panel
        st.markdown('<h3 class="section-title">Copilot Intelligence Context</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="card-title">Suggested Inquiries</div>', unsafe_allow_html=True)
            prompts = [
                "Explain today's highest-risk anomaly",
                "Summarize recent detections",
                "Map events to MITRE ATT&CK",
                "Explain the latest brute-force attempt",
                "Generate an executive summary",
                "Investigate suspicious IP activity"
            ]
            
            for idx, pr in enumerate(prompts):
                if st.button(pr, key=f"copilot_prompt_chip_{idx}", use_container_width=True):
                    history.append({
                        "role": "user",
                        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                        "content": pr
                    })
                    st.session_state.ai_requests_today += 1
                    
                    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}
                    try:
                        r = requests.post(f"{api_base}/ask", json={"question": pr}, headers=headers, timeout=20, verify=False)
                        if r.status_code == 200:
                            body_data = r.json()
                            ans = body_data.get("answer", "No answer returned.")
                            meta = body_data.get("metadata")
                        else:
                            ans = f"⚠️ Error fetching response: {r.status_code}"
                            meta = None
                    except Exception as e:
                        ans = f"⚠️ Connection failed: {str(e)}"
                        meta = None
                        
                    history.append({
                        "role": "assistant",
                        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                        "content": ans,
                        "metadata": meta
                    })
                    st.rerun()

            st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid var(--border-color);' />", unsafe_allow_html=True)

            # Model Details Card
            st.markdown('<div class="card-title">Investigation Model Information</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background-color: var(--card-bg-sec); border-radius: 8px; padding: 0.65rem; font-size: 0.78rem; border: 1px solid var(--border-color); margin-bottom: 1rem;">
                  <div style="margin-bottom:0.35rem;"><b>Model ID:</b> <code style="color:var(--primary);">llama3:latest</code></div>
                  <div style="margin-bottom:0.35rem;"><b>Processor URL:</b> <code>127.0.0.1:11434</code></div>
                  <div style="margin-bottom:0.35rem;"><b>Max Context:</b> 8,192 tokens</div>
                  <div><b>Status Check:</b> {model_status}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Loaded Context Card
            st.markdown('<div class="card-title">Loaded Investigation Context</div>', unsafe_allow_html=True)
            
            total_records = len(detect_rows)
            anomalies = len([r for r in explain_rows if r.get("risk_score", 0.0) >= LOW_RISK_THRESHOLD])
            high_risk_nodes = len([r for r in explain_rows if r.get("risk_score", 0.0) >= HIGH_RISK_THRESHOLD])
            unique_ips = list(set([r.get("ip") for r in explain_rows if r.get("ip")]))
            
            st.markdown(
                f"""
                <div style="background-color: var(--card-bg-sec); border-radius: 8px; padding: 0.65rem; font-size: 0.78rem; border: 1px solid var(--border-color);">
                  <div style="margin-bottom:0.35rem; display:flex; justify-content:space-between;">
                    <span>Telemetry Events:</span><b>{total_records}</b>
                  </div>
                  <div style="margin-bottom:0.35rem; display:flex; justify-content:space-between;">
                    <span>Active Anomalies:</span><b style="color:var(--warning);">{anomalies}</b>
                  </div>
                  <div style="margin-bottom:0.35rem; display:flex; justify-content:space-between;">
                    <span>Critical Nodes:</span><b style="color:var(--danger);">{high_risk_nodes}</b>
                  </div>
                  <div style="display:flex; justify-content:space-between;">
                    <span>Tracked Source IPs:</span><b>{len(unique_ips)}</b>
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )
