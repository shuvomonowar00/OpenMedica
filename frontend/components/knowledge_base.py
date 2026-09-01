import streamlit as st
import pandas as pd
from core.api_client import get_cached_database_status, delete_article

@st.dialog(":material/local_library: Literature Showcase", width="large")
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

    # 1. Strip out the backend metadata. 
    # Handle BOTH New format (Title:\nSection:\n\n) and Legacy format (Title:\n\nAbstract:)
    match_new = re.search(r"^Title:.*?\nSection:\s*([^\n]+)\n\n(.*)", raw_text, re.DOTALL | re.IGNORECASE)
    match_legacy = re.search(r"^Title:.*?\n\nAbstract:\s*(.*)", raw_text, re.DOTALL | re.IGNORECASE)
    
    if match_new:
        section_name = match_new.group(1).strip()
        clean_text = match_new.group(2).strip()
    elif match_legacy:
        section_name = "Abstract"
        clean_text = match_legacy.group(1).strip()
        
    # If the text itself starts with "Abstract:", strip it to avoid redundancy
    clean_text = re.sub(r"^Abstract:\s*", "", clean_text, flags=re.IGNORECASE)

    # 2. Convert embedded HTML tags from PubMed XML into standard Markdown
    clean_text = re.sub(r"<\/?b>", "**", clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r"<\/?strong>", "**", clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r"<\/?i>", "*", clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r"<\/?em>", "*", clean_text, flags=re.IGNORECASE)

    # 3. Convert ALL-CAPS clinical headers (BACKGROUND:, etc.) into standard Markdown bolding
    clean_text = re.sub(r"\b([A-Z][A-Z\s]{3,25}):\s", r"\n\n**\1:** ", clean_text)
    
    # 4. Normalize all paragraph spacing (ensure max 2 newlines)
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text).strip()

    # 5. Smart Heuristic for Human Readability: 
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
            st.link_button(":material/open_in_new: Read Full Article on PubMed", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
            
    with col2:
        if st.button(":material/delete: Delete Article", type="primary", use_container_width=True):
            with st.spinner("Deleting..."):
                res = delete_article(article.get("pmid"))
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("Deleted successfully!", icon=":material/check_circle:")
                    get_cached_database_status.clear()
                    st.rerun()

def render_knowledge_base():
    """
    Renders an interactive dataframe of all articles stored in the database.
    """
    st.header(":material/local_library: Knowledge Base Explorer")
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
    
    # Extract the Section name from the raw text so users know which chunk they are looking at
    import re
    def extract_section(text):
        if not isinstance(text, str): return "Abstract"
        match = re.search(r"^Title:[^\n]+\nSection:\s*([^\n]+)\n\n", text, re.DOTALL)
        return match.group(1).strip() if match else "Abstract"
        
    if "abstract" in display_df.columns:
        display_df["Section"] = display_df["abstract"].apply(extract_section)

    # Format High-Yield Clinical Columns
    if "pub_year" in display_df.columns:
        display_df["Year"] = display_df["pub_year"].apply(lambda x: str(x) if pd.notnull(x) and x > 0 else "N/A")
        
    if "publication_types" in display_df.columns:
        def simplify_type(pt_str):
            if not isinstance(pt_str, str) or not pt_str: return "Study"
            pt_lower = pt_str.lower()
            if "randomized controlled trial" in pt_lower: return "RCT"
            if "meta-analysis" in pt_lower or "systematic review" in pt_lower: return "Meta-Analysis"
            return "Study"
        display_df["Type"] = display_df["publication_types"].apply(simplify_type)

    # Convert PMID to a valid URL for the LinkColumn
    if "pmid" in display_df.columns:
        display_df["PMID"] = display_df["pmid"].apply(lambda x: f"https://pubmed.ncbi.nlm.nih.gov/{x}/" if x else "")

    # Clean up internal backend columns
    cols_to_drop = ["abstract", "id", "pub_year", "publication_types", "pmid"]
    display_df = display_df.drop(columns=[c for c in cols_to_drop if c in display_df.columns])
        
    # Reorder and rename columns for a premium look
    display_df = display_df.rename(columns={"title": "Title", "authors": "Authors"})
    # Keep track of original index so we can map filtered selections back to the raw JSON article
    display_df["_original_index"] = range(len(articles))
    
    expected_cols = ["Title", "Section", "Year", "Type", "PMID", "Authors", "_original_index"]
    existing_cols = [c for c in expected_cols if c in display_df.columns]
    display_df = display_df[existing_cols]
    
    # -------------------------------------------------------------
    # 1. KPI Metrics Dash
    # -------------------------------------------------------------
    st.markdown("---")
    total_chunks = len(display_df)
    
    # Count unique PMIDs by parsing the URL string back to the ID or skipping empties
    unique_papers = display_df["PMID"].nunique() if "PMID" in display_df.columns else 0
    # Count high-level evidence chunks
    high_evidence = len(display_df[display_df["Type"].isin(["RCT", "Meta-Analysis"])]) if "Type" in display_df.columns else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Unique Papers", unique_papers)
    with col2:
        st.metric("Semantic Database Chunks", total_chunks)
    with col3:
        st.metric("High-Level Evidence (Chunks)", high_evidence)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------
    # 2. Live Search & Contained Data Table
    # -------------------------------------------------------------
    with st.container(border=True):
        # Custom prominent search header
        st.markdown("<div style='font-weight: 600; font-size: 1.1rem; margin-bottom: 5px; color: #111827;'><span class='material-symbols-rounded' style='vertical-align: middle; margin-right: 8px;'>search</span>Search Knowledge Base</div>", unsafe_allow_html=True)
        
        search_query = st.text_input(
            "Search Database", 
            placeholder="Type to instantly filter by keyword, author, or study type...",
            label_visibility="collapsed"
        )
        
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px; border-color: #E5E7EB;'/>", unsafe_allow_html=True)
        if search_query:
            # Create a mask checking if search_query is in any of the text columns
            mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            filtered_df = display_df[mask]
        else:
            filtered_df = display_df
            
        # Display the interactive dataframe with Smart Column Configs
        event = st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key="kb_table",
            column_config={
                "_original_index": None, # Hide internal mapping column from UI
                "Title": st.column_config.TextColumn("Title", width="medium"),
                "Section": st.column_config.TextColumn("Section", width="small"),
                "Year": st.column_config.TextColumn("Year", width="small"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "PMID": st.column_config.LinkColumn("PMID", display_text=r"https://pubmed\.ncbi\.nlm\.nih\.gov/([^/]+)/", width="small"),
                "Authors": st.column_config.TextColumn("Authors", width="medium")
            }
        )
        
    # Check if a row was clicked
    selected_rows = event.selection.rows
    if selected_rows:
        # Get the positional index from the currently filtered dataframe
        selected_pos = selected_rows[0]
        # Map it back to the original index using our hidden tracking column
        original_idx = filtered_df.iloc[selected_pos]["_original_index"]
        
        selected_article = articles[original_idx]
        showcase_literature_modal(selected_article)
