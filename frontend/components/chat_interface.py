import streamlit as st
from core.state_manager import add_message
from core.api_client import send_chat
from utils.export import generate_markdown_report

def render_chat_messages():
    """
    Iterates through session state chat history and renders each message.
    """
    history = st.session_state.chat_history
    for i, msg in enumerate(history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)
            
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
                    with st.expander("🔍 Search Details"):
                        st.markdown("**Original Query:** " + query)
                        st.markdown("**MeSH Terms Applied:**")
                        for term in mesh_terms:
                            st.markdown(f"- `{term}`")
                
                # Render Export buttons seamlessly inline
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.download_button(
                        label="📥 Download (.md)",
                        data=md_report,
                        file_name="clinical_report.md",
                        mime="text/markdown",
                        key=f"dl_{i}"
                    )
                with col2:
                    with st.popover("📋 View/Copy Note"):
                        st.code(md_report, language="markdown")

def handle_chat_input():
    """
    Handles the chat input box and triggers the backend API call.
    """
    prompt = st.chat_input("Ask a medical question based on PubMed...")
    if prompt:
        # 1. Add user message to state
        add_message("user", prompt)
        
        # 2. Render it immediately
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 3. Call backend and render AI response
        with st.chat_message("assistant"):
            with st.status("Analyzing clinical query...", expanded=True) as status:
                st.write("Expanding MeSH terms...")
                st.write("Retrieving evidence from ChromaDB...")
                st.write("Multi-agent synthesis and review...")
                
                # Fetch filters from session state
                study_type = st.session_state.get("filter_study_type", "All")
                date_filter = st.session_state.get("filter_date", "All Time")
                
                # We need to exclude the newly added user prompt from the history we send
                # because `add_message` just added it. So we slice [:-1]
                history = st.session_state.chat_history[:-1]
                
                res = send_chat(
                    query=prompt, 
                    history=history, 
                    study_type=study_type, 
                    date_filter=date_filter
                )
                
                status.update(label="Analysis complete!", state="complete", expanded=False)
                
            if "error" in res:
                error_msg = f"Sorry, I encountered an error: {res['error']}"
                st.error(error_msg)
                add_message("assistant", error_msg)
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
                
                st.markdown(full_content, unsafe_allow_html=True)
                add_message("assistant", full_content, sources, raw_data=res)
                
                # Force a rerun to update the citation panel if needed
                st.rerun()
