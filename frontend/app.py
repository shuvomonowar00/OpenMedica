import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="OpenMedica",
    page_icon="⚕️",
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
    st.toast("Clinical context memory wiped successfully!", icon=":material/check_circle:")
    st.session_state.show_clear_toast = False

selected_page = render_sidebar()

if selected_page == ":material/cloud_download: Data Ingestion":
    render_ingestion_page()

elif selected_page == ":material/chat: Chat Interface":
    # Header and Toggle controls
    col_title, col_toggle = st.columns([4, 1], vertical_alignment="bottom")
    with col_title:
        st.header("OpenMedica AI")
        st.markdown("Ask medical questions. Get zero-hallucination answers strictly grounded in PubMed.")
    with col_toggle:
        show_sources = st.toggle("Show Grounding Panel", value=True, key="toggle_sources")
        
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px; border-color: #E2E8F0;'/>", unsafe_allow_html=True)
    
    if show_sources:
        # Aggressive CSS to force Streamlit's layout engine to allow sticky columns
        st.markdown("""
        <style>
        /* 1. Force ALL parent containers to allow sticky elements (override Streamlit hidden overflows and transforms) */
        .main,
        .main > div,
        .block-container,
        [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlock"] {
            overflow: visible !important;
            transform: none !important;
        }

        /* 2. Apply sticky physics directly to the ENTIRE Right Column */
        [data-testid="stHorizontalBlock"]:nth-of-type(2) > [data-testid="column"]:nth-child(2) {
            position: -webkit-sticky !important;
            position: sticky !important;
            top: 2rem !important;
            align-self: flex-start !important; /* Critical: tells the column not to stretch, allowing it to slide */
            z-index: 100 !important;
        }

        /* 3. Set the max-height and scrollbar on the box inside the sticky column */
        [data-testid="column"]:nth-child(2) div[data-testid="stVerticalBlockBorderWrapper"] {
            max-height: calc(100vh - 220px);
            overflow-y: auto;
            overflow-x: hidden;
            background-color: white; /* Prevent transparency overlap */
        }
        
        /* 4. Style the scrollbars to look sleek globally */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-thumb {
            background-color: #CBD5E1;
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col_chat, col_sources = st.columns([2, 1], gap="large")
        
        with col_chat:
            # Infinite chat scrolling
            render_chat_messages()
            
        with col_sources:
            with st.container(border=True):
                render_citation_panel()
    else:
        # Focus Mode (Full Width)
        render_chat_messages()
        
    # Render chat input at the root level to guarantee it ALWAYS strictly sticks to the bottom of the viewport
    handle_chat_input()

elif selected_page == ":material/local_library: Knowledge Base Explorer":
    render_knowledge_base()
