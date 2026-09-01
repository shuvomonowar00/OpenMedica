import streamlit as st
from core.state_manager import add_message
from core.api_client import send_chat, send_feedback
from utils.export import generate_markdown_report

def render_chat_messages():
    """
    Iterates through session state chat history and renders each message.
    """
    history = st.session_state.chat_history
    
    # Check if the user is currently submitting a prompt
    is_submitting = bool(st.session_state.get("main_chat_input"))
    
    # ---------------------------------------------------------
    # DYNAMIC EMPTY STATE (ChatGPT Style Center Search)
    # ---------------------------------------------------------
    # Only render the empty state if there is no history AND they aren't currently submitting
    if not history and not is_submitting:
        st.markdown("""
        <div style="text-align: center; margin-top: 15vh;">
            <span class="material-symbols-rounded" style="font-size: 3.5rem; color: #111827; margin-bottom: 10px;">medical_services</span>
            <h1 style="color: #111827; font-size: 2.2rem; font-weight: 700; margin-bottom: 10px; letter-spacing: -0.5px;">What clinical data do you need?</h1>
            <p style="color: #64748B; font-size: 1.1rem;">Search across clinical trials, guidelines, and PubMed literature.</p>
        </div>
        """, unsafe_allow_html=True)
        
    for i, msg in enumerate(history):
        avatar = ":material/person:" if msg["role"] == "user" else ":material/neurology:"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg["role"] == "user":
                st.markdown(f"<div class='user-message-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-message-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
            
            # If this is an AI message and has raw_data, show export options
            if msg["role"] == "assistant" and msg.get("raw_data"):
                # Find the user's query that prompted this response
                query = "Unknown Query"
                if i > 0 and history[i-1]["role"] == "user":
                    query = history[i-1]["content"]
                    
                md_report = generate_markdown_report(query, msg["raw_data"])
                
                # Render MeSH Search Details for transparency
                mesh_terms = msg["raw_data"].get("mesh_terms", [])
                if mesh_terms:
                    with st.expander(":material/search_insights: Search Details"):
                        st.markdown("**Original Query:** " + query)
                        st.markdown("**MeSH Terms Applied:**")
                        for term in mesh_terms:
                            st.markdown(f"- `{term}`")
                
                # Render Export buttons and Feedback seamlessly inline
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    st.download_button(
                        label=":material/download: Download (.md)",
                        data=md_report,
                        file_name="clinical_report.md",
                        mime="text/markdown",
                        key=f"dl_{i}"
                    )
                with col2:
                    with st.popover(":material/content_copy: View/Copy Note"):
                        st.code(md_report, language="markdown")
                with col3:
                    # Render Streamlit native feedback
                    fb_key = f"fb_{i}"
                    feedback = st.feedback("thumbs", key=fb_key)
                    if feedback is not None and not st.session_state.get(f"fb_submitted_{i}"):
                        is_positive = (feedback == 1)
                        send_feedback(query, msg["content"], is_positive)
                        st.session_state[f"fb_submitted_{i}"] = True
                        st.toast("Feedback recorded. Thank you!")

def handle_chat_input():
    """
    Handles the chat input box and triggers the backend API call.
    """
    prompt = st.chat_input("Ask a medical question based on PubMed...", key="main_chat_input")
    if prompt:
        # 1. Add user message to state
        add_message("user", prompt)
        
        # 2. Render it immediately
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(f"<div class='user-message-bubble'>{prompt}</div>", unsafe_allow_html=True)
            
        # 3. Call backend and render AI response
        with st.chat_message("assistant", avatar=":material/neurology:"):
            with st.status("Analyzing clinical query...", expanded=True) as status:
                st.write("Expanding MeSH terms...")
                st.write("Retrieving evidence from ChromaDB...")
                st.write("Multi-agent synthesis and review...")
                
                # Fetch filters and RAG settings from session state (Cockpit Sidebar)
                study_type = st.session_state.get("filter_study_type", "All")
                date_filter = st.session_state.get("filter_date", "All Time")
                n_results = st.session_state.get("retrieval_depth", 5)
                
                # We need to exclude the newly added user prompt from the history we send
                # because `add_message` just added it. So we slice [:-1]
                history = st.session_state.chat_history[:-1]
                
                res = send_chat(
                    query=prompt, 
                    history=history, 
                    study_type=study_type, 
                    date_filter=date_filter,
                    n_results=n_results
                )
                
                status.update(label="Analysis complete!", state="complete", expanded=False)
                
            if "error" in res:
                error_msg = f"Sorry, I encountered a server error: {res['error']}"
                wrapped_error = f"<div class='ai-message-bubble' style='color: #ef4444;'>{error_msg}</div>"
                st.markdown(wrapped_error, unsafe_allow_html=True)
                add_message("assistant", error_msg)
                st.rerun()
            else:
                # Parse Pydantic AI Response (our backend returns structured data)
                answer = res.get("answer", "No answer provided.")
                sources = res.get("sources", [])
                
                # Render PICO formatted elements if available
                pico_keys = ["population", "intervention", "comparison", "outcome"]
                full_content = ""
                
                if all(k in res for k in pico_keys):
                    pico_html = f'''
                    <div class="pico-container">
                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <div class="pico-card" style="flex: 1;">
                                <div class="pico-header">Population</div>
                                <div class="pico-content">{res["population"]}</div>
                            </div>
                            <div class="pico-card" style="flex: 1;">
                                <div class="pico-header">Intervention</div>
                                <div class="pico-content">{res["intervention"]}</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <div class="pico-card" style="flex: 1;">
                                <div class="pico-header">Comparison</div>
                                <div class="pico-content">{res["comparison"]}</div>
                            </div>
                            <div class="pico-card" style="flex: 1;">
                                <div class="pico-header">Outcome</div>
                                <div class="pico-content">{res["outcome"]}</div>
                            </div>
                        </div>
                    </div>
                    '''
                    full_content += pico_html
                
                full_content += answer
                
                # Wrap it before rendering
                wrapped_content = f"<div class='ai-message-bubble'>{full_content}</div>"
                st.markdown(wrapped_content, unsafe_allow_html=True)
                add_message("assistant", full_content, sources, raw_data=res)
                
                # Force a rerun to update the citation panel if needed
                st.rerun()
