import streamlit as st

def initialize_state():
    """
    Initializes required Streamlit session state variables
    if they are not already present.
    """
    if "chat_history" not in st.session_state:
        # Each message is a dict: {"role": "user"|"assistant", "content": str, "citations": list}
        st.session_state.chat_history = []
    
    if "current_citations" not in st.session_state:
        st.session_state.current_citations = []

def add_message(role: str, content: str, citations: list = None, raw_data: dict = None):
    """
    Appends a message to the chat history.
    """
    if citations is None:
        citations = []
        
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "citations": citations,
        "raw_data": raw_data
    })
    
    if role == "assistant":
        st.session_state.current_citations = citations

def clear_chat():
    """
    Clears the chat history and current citations.
    """
    st.session_state.chat_history = []
    st.session_state.current_citations = []
