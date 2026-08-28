import streamlit as st

def render_citation_panel():
    """
    Renders the citations for the current AI response in the right column or bottom area.
    """
    st.subheader("📚 Grounding & Sources")
    
    citations = st.session_state.get("current_citations", [])
    
    if not citations:
        st.info("No sources retrieved for the current conversation yet.")
        return
    
    # Render each citation as a styled card
    for cit in citations:
        pmid = cit.get("pmid", "N/A")
        title = cit.get("title", "Unknown Title")
        authors = cit.get("authors", "Unknown Authors")
        pub_date = cit.get("pub_date", "Unknown Date")
        
        card_html = f"""
        <div class="citation-card">
            <div class="citation-title">{title}</div>
            <div class="citation-meta"><strong>PMID:</strong> {pmid} | <strong>Date:</strong> {pub_date}</div>
            <div class="citation-meta"><strong>Authors:</strong> {authors}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
