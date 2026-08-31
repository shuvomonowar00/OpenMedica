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
        pub_types = cit.get("publication_types", [])
        
        # Build badges HTML
        badges_html = ""
        if not pub_types:
            badges_html = '<span class="badge badge-standard">Study</span>'
        else:
            for pt in pub_types:
                pt_lower = pt.lower()
                if "randomized controlled trial" in pt_lower:
                    badges_html += '<span class="badge badge-rct">RCT</span>'
                elif "meta-analysis" in pt_lower or "systematic review" in pt_lower:
                    badges_html += f'<span class="badge badge-meta">{pt}</span>'
                else:
                    badges_html += f'<span class="badge badge-standard">{pt}</span>'
        
        card_html = f"""
        <div class="citation-card">
            <div style="margin-bottom: 8px;">{badges_html}</div>
            <div class="citation-title">{title}</div>
            <div class="citation-meta"><strong>PMID:</strong> {pmid}</div>
            <div class="citation-meta"><strong>Authors:</strong> {authors}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
