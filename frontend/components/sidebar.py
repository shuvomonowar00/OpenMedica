import streamlit as st
from core.api_client import get_cached_database_status
from core.state_manager import clear_chat

def render_sidebar():
    """
    Renders the sidebar for data ingestion, database status, and chat controls.
    """
    with st.sidebar:
        st.title("🔬 OpenMedica")
        st.markdown("---")
        
        # Database Status Section
        st.subheader("Database Status")
        
        status_res = get_cached_database_status()
        
        if "error" in status_res:
            st.error("Backend offline or unreachable.")
        else:
            total_articles = status_res.get("total_articles", 0)
            st.metric(label="Articles in Knowledge Base", value=total_articles)
        
        st.markdown("---")
        

        
        # Search Filters Section
        st.subheader("Search Filters")
        st.session_state.filter_study_type = st.selectbox(
            "Evidence Level", 
            ["All", "RCTs Only", "Meta-Analyses Only"],
            index=0
        )
        st.session_state.filter_date = st.selectbox(
            "Date Range",
            ["All Time", "Last Year", "Last 5 Years"],
            index=0
        )
        
        st.markdown("---")
        
        # Chat Controls
        if st.button("Clear Chat History", use_container_width=True):
            clear_chat()
            st.rerun()
