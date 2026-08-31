import streamlit as st
import pandas as pd
from core.api_client import get_cached_database_status, delete_article

@st.dialog("📚 Literature Showcase", width="large")
def showcase_literature_modal(article: dict):
    """
    Displays a beautiful pop-up modal showcasing the full abstract and metadata,
    along with a delete action.
    """
    st.markdown(f"### {article.get('title', 'Unknown Title')}")
    
    st.markdown(f"**Authors:** {article.get('authors', 'N/A')} | **PMID:** {article.get('pmid', 'N/A')}")
    st.markdown("---")
    
    import re
    # Format the text purely in Markdown for perfect Streamlit rendering
    raw_text = article.get("abstract", "")
    section_name = "Content"
    clean_text = raw_text

    # 1. Strip out the backend metadata (Title & Section injected by ChromaDB)
    match = re.search(r"^Title:[^\n]+\nSection:\s*([^\n]+)\n\n(.*)", raw_text, re.DOTALL)
    if match:
        section_name = match.group(1).strip()
        clean_text = match.group(2).strip()

    # 2. Convert clinical headers (BACKGROUND:, etc.) into standard Markdown bolding
    # This prevents HTML tag breakage and leverages Streamlit's native typography
    clean_text = re.sub(r"\b([A-Z][A-Z\s]{3,25}):\s", r"\n\n**\1:** ", clean_text)
    
    # 3. Normalize all paragraph spacing (ensure max 2 newlines)
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text).strip()

    # 4. Smart Heuristic for Human Readability: 
    # Visually segregate floating captions, glossaries, and short fragments into blockquotes
    paragraphs = clean_text.split('\n\n')
    formatted_paragraphs = []
    for p in paragraphs:
        p_strip = p.strip()
        if not p_strip:
            continue
        # If the paragraph is short (< 130 chars) and isn't already a formatted clinical header
        if len(p_strip) < 130 and "**" not in p_strip:
            formatted_paragraphs.append(f"> *{p_strip}*")
        else:
            formatted_paragraphs.append(p_strip)
            
    clean_text = "\n\n".join(formatted_paragraphs)

    st.markdown(f"#### {section_name}")
    
    # Use Streamlit's native scrollable card container for a flawless layout
    with st.container(height=400, border=True):
        st.markdown(clean_text)
        
    st.markdown("---")
    
    # Action Bar
    col1, col2 = st.columns([4, 1])
    with col1:
        pmid = article.get('pmid')
        if pmid and pmid != "N/A":
            st.link_button("🔗 Read Full Article on PubMed", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
            
    with col2:
        if st.button("🗑️ Delete Article", type="primary", use_container_width=True):
            with st.spinner("Deleting..."):
                res = delete_article(article.get("pmid"))
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("Deleted successfully!")
                    get_cached_database_status.clear()
                    st.rerun()

def render_knowledge_base():
    """
    Renders an interactive dataframe of all articles stored in the database.
    """
    st.header("📚 Knowledge Base Explorer")
    st.markdown("Browse all the peer-reviewed PubMed literature currently stored in the vector database.")
    
    status_res = get_cached_database_status()
    
    if "error" in status_res:
        st.error(f"Could not connect to backend: {status_res['error']}")
        return
        
    articles = status_res.get("articles", [])
    
    if not articles:
        st.info("The Knowledge Base is currently empty. Use the sidebar to ingest some PubMed data!")
        return
        
    # Convert the list of metadata dictionaries into a Pandas DataFrame
    df = pd.DataFrame(articles)
    
    # Clean up dataframe for display
    display_df = df.copy()
    if "abstract" in display_df.columns:
        display_df = display_df.drop(columns=["abstract", "id"])
        
    cols = display_df.columns.tolist()
    if "title" in cols and "pmid" in cols:
        cols.insert(0, cols.pop(cols.index("title")))
        cols.insert(1, cols.pop(cols.index("pmid")))
        display_df = display_df[cols]
        
    # Display the interactive dataframe
    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="kb_table"
    )
    
    # Check if a row was clicked
    selected_rows = event.selection.rows
    if selected_rows:
        # Get the selected article from the original list
        selected_index = selected_rows[0]
        selected_article = articles[selected_index]
        showcase_literature_modal(selected_article)
