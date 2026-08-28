import streamlit as st
from core.state_manager import add_message
from core.api_client import send_chat

def render_chat_messages():
    """
    Iterates through session state chat history and renders each message.
    """
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
            with st.spinner("Analyzing PubMed literature..."):
                res = send_chat(prompt)
                
                if "error" in res:
                    error_msg = f"Sorry, I encountered an error: {res['error']}"
                    st.error(error_msg)
                    add_message("assistant", error_msg)
                else:
                    # Parse Pydantic AI Response (our backend returns structured data)
                    # The response matches the ChatResponse schema in backend
                    answer = res.get("answer", "No answer provided.")
                    citations = res.get("citations", [])
                    
                    st.markdown(answer)
                    add_message("assistant", answer, citations)
                    
                    # Force a rerun to update the citation panel if needed
                    st.rerun()
