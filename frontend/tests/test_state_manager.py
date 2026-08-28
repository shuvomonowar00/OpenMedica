import pytest
import streamlit as st
from core.state_manager import initialize_state, add_message, clear_chat

# A helper to clear Streamlit's session state before each test
@pytest.fixture(autouse=True)
def reset_session_state():
    st.session_state.clear()

def test_initialize_state():
    """Test that state variables are correctly initialized."""
    initialize_state()
    assert "chat_history" in st.session_state
    assert "current_citations" in st.session_state
    assert st.session_state.chat_history == []
    assert st.session_state.current_citations == []

def test_add_message():
    """Test adding user and assistant messages."""
    initialize_state()
    
    # Add User Message
    add_message("user", "Hello")
    assert len(st.session_state.chat_history) == 1
    assert st.session_state.chat_history[0]["role"] == "user"
    assert st.session_state.chat_history[0]["content"] == "Hello"
    # Citations shouldn't update on user messages
    assert st.session_state.current_citations == []
    
    # Add Assistant Message with citations
    citations = [{"pmid": "123", "title": "Test"}]
    add_message("assistant", "Hi there", citations)
    
    assert len(st.session_state.chat_history) == 2
    assert st.session_state.chat_history[1]["role"] == "assistant"
    # Current citations SHOULD update on assistant messages
    assert st.session_state.current_citations == citations

def test_clear_chat():
    """Test clearing the chat resets the state properly."""
    initialize_state()
    add_message("user", "Blah")
    add_message("assistant", "Blah blah", [{"pmid": "999"}])
    
    assert len(st.session_state.chat_history) == 2
    
    clear_chat()
    assert st.session_state.chat_history == []
    assert st.session_state.current_citations == []
