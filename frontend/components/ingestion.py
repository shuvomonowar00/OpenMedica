import streamlit as st
from core.api_client import ingest_data, get_cached_database_status

def render_ingestion_page():
    """
    Renders the advanced Data Ingestion Command Center as a full-page tab.
    """
    st.header("📥 Data Ingestion Command Center")
    st.markdown("Fetch peer-reviewed medical literature directly from PubMed and embed it into your local vector database.")
    
    with st.container(border=True):
        col1, col2 = st.columns([1.5, 1], gap="large")
        
        with col1:
            st.subheader("Standard Parameters")
            topic = st.text_input(
                "Clinical Topic / Keyword", 
                placeholder="e.g., Asthma, COVID-19, Type 2 Diabetes",
                help="The primary keyword or disease state you want to research."
            )
            
            max_results = st.slider(
                "Maximum Articles to Fetch", 
                min_value=1, 
                max_value=100, 
                value=5, 
                step=1,
                help="Note: Fetching full-text XMLs for many articles may take time and trigger rate limits."
            )
            
        with col2:
            st.subheader("Advanced PubMed Filters")
            st.markdown("<span style='font-size: 0.85rem; color: #64748b;'>Refine your search using native Entrez syntax.</span>", unsafe_allow_html=True)
            
            filter_oa = st.toggle(
                "Open Access Full-Text Only", 
                value=True, 
                help="Only fetches papers that have complete semantic sections available (highly recommended for RAG)."
            )
            
            filter_rct = st.toggle(
                "Clinical Trials & RCTs Only", 
                value=False,
                help="Forces the ingestion of high-level evidence by appending the 'clinical trial' publication type."
            )
            
            filter_5yrs = st.toggle(
                "Published in Last 5 Years", 
                value=True,
                help="Ensures you don't ingest outdated literature."
            )
            
        st.markdown("---")
        
        # Submit Button
        submit_ingest = st.button("🚀 Start Ingestion Pipeline", type="primary", use_container_width=True)
        
        if submit_ingest:
            if not topic.strip():
                st.warning("Please enter a clinical topic to begin ingestion.")
            else:
                # -------------------------------------------------------------
                # ADVANCED QUERY BUILDER
                # -------------------------------------------------------------
                final_query = topic.strip()
                
                if filter_oa:
                    final_query += ' AND free full text[sb]'
                if filter_rct:
                    final_query += ' AND "clinical trial"[pt]'
                if filter_5yrs:
                    final_query += ' AND "last 5 years"[dp]'
                    
                # -------------------------------------------------------------
                # EXECUTE INGESTION
                # -------------------------------------------------------------
                with st.spinner(f"Querying PubMed for: '{final_query}'..."):
                    ingest_res = ingest_data(final_query, max_results)
                    
                    if "error" in ingest_res:
                        st.error(f"Ingestion Pipeline Failed: {ingest_res['error']}")
                    else:
                        articles_added = ingest_res.get('articles_ingested', 0)
                        if articles_added > 0:
                            st.success(f"🎉 Pipeline Complete! Successfully embedded {articles_added} articles into ChromaDB.")
                            get_cached_database_status.clear() # Clear cache so DB count updates
                        else:
                            st.warning("Search completed, but no matching articles were found or successfully parsed.")
