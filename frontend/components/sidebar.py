import streamlit as st
import os
from core.api_client import get_cached_database_status
from core.state_manager import clear_chat

@st.dialog("Clear Chat Memory")
def clear_memory_dialog():
    st.warning("You are about to delete all conversational history. The AI will lose all context of your current diagnostic session.", icon=":material/warning:")
    st.markdown("This action **cannot be undone**.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button(":material/delete_forever: Yes, Clear Memory", type="primary", use_container_width=True):
            clear_chat()
            st.session_state.show_clear_toast = True
            st.rerun()

def render_sidebar():
    """
    Renders the sidebar as a professional 'Cockpit' for system health, 
    clinical filters, and RAG AI tuning.
    """
    with st.sidebar:
        # Left-align the title and pull it up so it sits exactly on the same line as the toggle button (ChatGPT style)
        st.markdown("<h1 style='text-align: left; margin-bottom: 0; margin-top: -15px; font-size: 1.6rem;'><span class='material-symbols-rounded' style='vertical-align: middle; color: #111827;'>medical_services</span> OpenMedica</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: left; color: #64748b; font-size: 0.9rem; margin-top: -5px;'>AI Clinical Assistant</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # -------------------------------------------------------------
        # 0. Navigation Menu
        # -------------------------------------------------------------
        st.markdown("### :material/explore: Navigation")
        selected_page = st.radio(
            "Go to",
            [":material/cloud_download: Data Ingestion", ":material/chat: Chat Interface", ":material/local_library: Knowledge Base Explorer"],
            label_visibility="collapsed"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        # -------------------------------------------------------------
        # 1. System Health Dashboard
        # -------------------------------------------------------------
        st.markdown("### :material/monitor_heart: System Health")
        
        status_res = get_cached_database_status()
        llm_engine = os.environ.get("ACTIVE_LLM_PROVIDER", "gemini").capitalize()
        
        if "error" in status_res:
            db_status_text = "Offline"
            db_status_color = "#ef4444" # Premium soft red
            total_articles = 0
        else:
            db_status_text = "Online"
            db_status_color = "#22c55e" # Premium soft green
            total_articles = status_res.get("total_articles", 0)
            
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; font-size: 0.9rem;">
            <div style="margin-bottom: 8px;">
                <span style="color: {db_status_color}; font-size: 1.1em;">●</span> <b>Vector Database:</b> {db_status_text}
            </div>
            <div style="margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                <span class="material-symbols-rounded" style="font-size: 1rem; color: #64748b;">description</span> <b>Documents Loaded:</b> {total_articles}
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span class="material-symbols-rounded" style="font-size: 1rem; color: #64748b;">memory</span> <b>AI Engine:</b> {llm_engine}
            </div>
        </div>
        """, unsafe_allow_html=True)
            
        # -------------------------------------------------------------
        # CONDITIONAL CHAT INTERFACE CONTROLS
        # -------------------------------------------------------------
        if selected_page == ":material/chat: Chat Interface":
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. Clinical Filters
            st.markdown("### :material/filter_alt: Clinical Filters")
            st.session_state.filter_study_type = st.selectbox(
                "Evidence Level", 
                ["All", "RCTs Only", "Meta-Analyses Only"],
                index=0,
                help="Strictly limits the AI's search to specific study designs."
            )
            st.session_state.filter_date = st.selectbox(
                "Publication Date",
                ["All Time", "Last Year", "Last 5 Years"],
                index=0,
                help="Restricts the knowledge base search to recent literature."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 3. RAG Tuning (Advanced Settings)
            st.markdown("### :material/tune: AI RAG Tuning")
            if "retrieval_depth" not in st.session_state:
                st.session_state.retrieval_depth = 5
                
            st.slider(
                "Retrieval Depth (Context Size)", 
                min_value=1, 
                max_value=10, 
                value=st.session_state.retrieval_depth,
                step=1,
                key="retrieval_depth",
                help="Controls how many PubMed chunks the AI reads before answering. Lower is faster, higher provides more clinical context."
            )
            
            # 4. Danger Zone (Chat Memory)
            # Add dynamic spacer to push the following content to the absolute bottom
            st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
            
            if st.button(":material/delete: Clear Chat Memory", type="secondary", use_container_width=True):
                clear_memory_dialog()
        else:
            # Add dynamic spacer to push the footer to the absolute bottom when chat controls are hidden
            st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
            
        # Footer
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.75rem; margin-top: 15px; margin-bottom: 0;'>OpenMedica v1.0.0</p>", unsafe_allow_html=True)
        
        return selected_page
