import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="OpenMedica",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Custom CSS ---
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    try:
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS not found.")

load_css()

# --- Imports (Must be after page config) ---
from core.state_manager import initialize_state
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_messages, handle_chat_input
from components.citation_panel import render_citation_panel
from components.knowledge_base import render_knowledge_base
from components.ingestion import render_ingestion_page

# --- Initialize State ---
initialize_state()

# Show success toast if chat was just cleared
if st.session_state.get("show_clear_toast", False):
    st.toast("Clinical context memory wiped successfully!", icon="🧹")
    st.session_state.show_clear_toast = False

selected_page = render_sidebar()

if selected_page == "📥 Data Ingestion":
    render_ingestion_page()

elif selected_page == "💬 Chat Interface":
    col_chat, col_sources = st.columns([2, 1], gap="large")
    
    with col_chat:
        st.header("OpenMedica AI")
        st.markdown("Ask medical questions. Get zero-hallucination answers strictly grounded in PubMed.")
        
        # Render chat history
        render_chat_messages()
        
        # Handle new user input
        handle_chat_input()

    with col_sources:
        render_citation_panel()

elif selected_page == "📚 Knowledge Base Explorer":
    render_knowledge_base()
