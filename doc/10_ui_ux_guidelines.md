# UI/UX & Frontend Guidelines

Clean, professional, and trustworthy UI/UX is MANDATORY for OpenMedica. Since we are using Streamlit for the MVP, you must leverage advanced Streamlit features and custom CSS to ensure the application feels like a premium, outstanding clinical SaaS product (similar to OpenEvidence).

## 1. Design System & Color Palette
You MUST inject custom CSS to override default Streamlit styles to achieve an outstanding, modern, and trustworthy aesthetic.
- **Backgrounds**: Use ultra-clean, low-eye-strain backgrounds (e.g., #F8FAFC or #F9FAFB).
- **Primary Accent (Trust Blue/Teal)**: Use clinical, trustworthy blues or teals (e.g., #0EA5E9, #0F766E, or #1E3A8A) for primary buttons, active tabs, and highlights.
- **Card UI**: Wrap content (like PICO results or citations) in soft "cards" with rounded corners (order-radius: 8px;) and very subtle drop shadows (ox-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);).
- **Typography**: Clean, highly legible sans-serif fonts (e.g., Inter, Roboto, or system UI fonts). Use strong font-weight contrasts (e.g., 600 for headers, 400 for body) rather than just making text larger.

## 2. Clinical Data Presentation (OpenEvidence Style)
- **PICO Formatting**: Never present walls of text for medical answers. Break down the synthesis into **P**opulation, **I**ntervention, **C**omparison, and **O**utcome using bold headers, cards, or columns.
- **Evidence Badging**: Clearly distinguish the quality of evidence. Use visual badges with distinct, soft background colors (e.g., Soft Purple for **[Meta-Analysis]**, Soft Green for **[RCT]**) to highlight evidence tiers.
- **Inline Citations**: The LLM must output inline citations (e.g., [1], [2]). The UI must map these numbers to a clear, easily readable sidebar or expander containing the actual PMC/PubMed links and abstracts.

## 3. Core UX Principles
- **Clear Feedback & Transparency**: Show the AI's "thought process". Use st.status() to show MeSH term expansion, hybrid search execution, and multi-agent verification steps so doctors trust the pipeline.
- **Micro-Interactions**: Use hover states on buttons and citation links to make the app feel responsive and "alive".
- **Graceful Error Handling**: Never show raw Python tracebacks. Use st.error() or st.warning() with friendly messaging.
- **Layout Management**: Avoid massive single-column scrolls. Use st.columns, st.tabs, and st.expander to logically group information (e.g., Synthesis on the left, Source Citations on the right).

## 4. Streamlit Specific Rules
- **No Global State Leakage**: Use st.session_state properly to manage chat history, filters, and loaded documents.
- **Separation of Concerns**: Do NOT write raw data fetching or DB logic in pp.py. The UI only communicates with FastAPI endpoints or backend agent interfaces.
- **Custom CSS**: Inject clean, minimal custom CSS via st.markdown("<style>...</style>", unsafe_allow_html=True).

When writing frontend code, your primary goal is to make the user feel they are using a premium, highly trustworthy, evidence-based medical tool.
