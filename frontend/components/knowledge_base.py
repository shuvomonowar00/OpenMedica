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
    
    # Format the abstract nicely
    abstract = article.get("abstract", "")
    if abstract.startswith("Title:"):
        # The backend combines Title and Abstract in the document text, let's just display it nicely.
        # It's "Title: ...\n\nAbstract: ..."
        parts = abstract.split("\n\nAbstract: ")
        if len(parts) > 1:
            abstract = parts[1]
    
    st.markdown("#### Abstract")
    st.markdown(f"<div class='abstract-text'>{abstract}</div>", unsafe_allow_html=True)
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
        
        # Override the session state to clear the selection when the modal is closed
        st.session_state["kb_table"] = {"selection": {"rows": [], "columns": []}}
