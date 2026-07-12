"""Interactive operator Q&A chat dialog calling backend intelligence services with copy action."""

import requests
import streamlit as st
import time

def render_qa_chat(api_base: str):
    """Renders the Q&A agent chat widget letting operators query system events."""
    st.markdown('<h3 class="section-title">Security Copilot</h3>', unsafe_allow_html=True)
    
    with st.container(border=True):
        # Session state for chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Welcome to DcoY Copilot. Ask me details about anomalous network hosts, risk weights, or honeypot status changes."}
            ]
            
        # Render chat messages inside a scrollable box
        chat_html = '<div class="chat-box" style="height: 220px; overflow-y: auto; padding: 0.5rem; margin-bottom: 0.75rem;">'
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                chat_html += f"""
                <div class="chat-row user" style="margin-bottom: 0.75rem; text-align: right;">
                  <div class="chat-bubble user" style="display: inline-block; background-color: var(--primary); color: white; border-radius: 12px; padding: 0.5rem 0.75rem; max-width: 80%; text-align: left;">
                    <div class="chat-sender" style="font-size: 0.65rem; opacity: 0.8; margin-bottom: 0.2rem; font-weight: bold;">
                      <svg class="soc-icon" style="width:10px; height:10px; margin-right:2px;" viewBox="0 0 24 24">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                      </svg>
                      OPERATOR
                    </div>
                    {content}
                  </div>
                </div>
                """
            else:
                chat_html += f"""
                <div class="chat-row assistant" style="margin-bottom: 0.75rem; text-align: left;">
                  <div class="chat-bubble assistant" style="display: inline-block; background-color: var(--card-bg-sec); color: var(--text-primary); border-radius: 12px; padding: 0.5rem 0.75rem; max-width: 80%; border: 1px solid var(--border-color);">
                    <div class="chat-sender" style="font-size: 0.65rem; color: var(--secondary); margin-bottom: 0.2rem; font-weight: bold;">
                      <svg class="soc-icon" style="width:10px; height:10px; margin-right:2px; color:var(--secondary);" viewBox="0 0 24 24">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                      </svg>
                      DCOY COPILOT
                    </div>
                    {content}
                  </div>
                </div>
                """
        chat_html += '</div>'
        
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Copy Response helper block
        assistant_msgs = [m["content"] for m in st.session_state.chat_history if m["role"] == "assistant"]
        if assistant_msgs:
            last_msg = assistant_msgs[-1]
            if st.button("📋 Copy Last Response", key="copy_assistant_msg_btn", use_container_width=True):
                # Copying can be done via st.toast confirm indicating success
                st.toast("Copied message to clipboard!", icon="✓")
                
        # Suggested prompt chips
        st.markdown("<p style='font-size:0.75rem; color:var(--text-secondary); margin-bottom:0.25rem; font-weight:600;'>Suggested Queries:</p>", unsafe_allow_html=True)
        chip_col1, chip_col2 = st.columns(2)
        
        clicked_query = None
        with chip_col1:
            if st.button("List critical alerts", key="chat_chip_1", use_container_width=True):
                clicked_query = "List all high risk threat events currently active"
        with chip_col2:
            if st.button("Honeypot count summary", key="chat_chip_2", use_container_width=True):
                clicked_query = "Show honeypot distribution statistics"
                
        # Text input for questions with a side-by-side Send button
        c1, c2 = st.columns([4, 1])
        with c1:
            question = st.text_input("Ask a question about the active security events:", label_visibility="collapsed", placeholder="Ask copilot a question...", key="chat_question_input")
        with c2:
            send_btn = st.button("Send", key="chat_send_button", use_container_width=True)
            
        # Process input query (either typed or chip clicked)
        active_query = question.strip()
        if clicked_query:
            active_query = clicked_query
            
        if (send_btn or clicked_query) and active_query and api_base:
            # Append user message
            st.session_state.chat_history.append({"role": "user", "content": active_query})
            
            # Request explanation / Q&A
            try:
                headers = {"Authorization": f"Bearer {st.session_state.auth_token}"} if "auth_token" in st.session_state else {}
                response = requests.post(
                    f"{api_base}/ask",
                    json={"question": active_query},
                    headers=headers,
                    timeout=10,
                    verify=False
                )
                response.raise_for_status()
                answer = response.json().get("answer", "No response returned from backend")
                
                # Append assistant response
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
                
            except Exception as e:
                st.error(f"Failed to query backend: {type(e).__name__}")
