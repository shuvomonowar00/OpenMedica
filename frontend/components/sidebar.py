import streamlit as st
from core.api_client import ingest_data, get_cached_database_status
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
        
        # Data Ingestion Section
        st.subheader("Ingest New Data")
        with st.form("ingest_form"):
            topic = st.text_input("PubMed Topic", placeholder="e.g. Asthma, COVID-19")
            max_results = st.number_input("Max Articles", min_value=1, max_value=50, value=5)
            submit_ingest = st.form_submit_button("Ingest")
            
            if submit_ingest:
                if not topic:
                    st.warning("Please enter a topic.")
                else:
                    with st.spinner(f"Fetching {max_results} articles for '{topic}'..."):
                        ingest_res = ingest_data(topic, max_results)
                        if "error" in ingest_res:
                            st.error(f"Error: {ingest_res['error']}")
                        else:
                            st.success(f"Successfully ingested {ingest_res.get('articles_ingested', 0)} articles!")
                            get_cached_database_status.clear() # Clear cache so new count shows up
                            st.rerun() # Refresh to show new count
        
        st.markdown("---")
        
        # Chat Controls
        if st.button("Clear Chat History", use_container_width=True):
            clear_chat()
            st.rerun()
