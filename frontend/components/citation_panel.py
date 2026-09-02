import streamlit as st

def render_citation_panel():
    """
    Renders the citations for the current AI response in the right column or bottom area.
    """
    st.subheader(":material/format_quote: Grounding & Sources")
    
    citations = st.session_state.get("current_citations", [])
    
    if not citations:
        st.markdown("""<div style="border: 1px dashed #D1D5DB; border-radius: 12px; padding: 30px 20px; text-align: center; background-color: #F8FAFC; margin-top: 20px; margin-bottom: 20px;">
    <span class="material-symbols-rounded" style="font-size: 2rem; color: #94A3B8; margin-bottom: 10px;">article</span>
    <div style="color: #64748B; font-size: 0.95rem;">Sources will appear here once the AI generates a clinical response.</div>
</div>""", unsafe_allow_html=True)
        return
    
    # Render each citation as an interactive styled card
    html_out = ""
    for cit in citations:
        pmid = cit.get("pmid", "N/A")
        title = cit.get("title", "Unknown Title")
        authors = cit.get("authors", "Unknown Authors")
        pub_types = cit.get("publication_types", [])
        pub_year = cit.get("pub_year", 0)
        year_str = str(pub_year) if pub_year > 0 else "Unknown Year"
        
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
        
        card_html = f"""<div class="citation-card" style="margin-bottom: 12px;">
    <div style="margin-bottom: 8px;">{badges_html}</div>
    <div class="citation-title"><a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}/" target="_blank">{title} <span class="material-symbols-rounded" style="font-size: 1rem; vertical-align: text-bottom; color: #94A3B8;">open_in_new</span></a></div>
    <div class="citation-meta"><strong>PMID:</strong> {pmid} | <strong>Year:</strong> {year_str}</div>
    <div class="citation-meta"><strong>Authors:</strong> {authors}</div>
</div>"""
        html_out += card_html
        
    st.markdown(f"<div style='margin-bottom: -12px;'>{html_out}</div>", unsafe_allow_html=True)
