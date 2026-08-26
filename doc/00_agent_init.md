# OpenMedica - Agent Initialization Context

**Project**: OpenMedica
**Goal**: A zero-hallucination Medical RAG pipeline that strictly grounds answers in peer-reviewed PubMed literature.

## Tech Stack
**CRITICAL**: You must strictly adhere to the approved tech stack. Read doc/09_tech_stack.md for the exact libraries (ChromaDB, Gemini Embeddings, Streamlit, etc.). Do NOT use FAISS or HuggingFace.

## Strict Rules for AI Agents
1. **Zero Hallucination**: All LLM responses MUST be strictly grounded in the retrieved PubMed abstracts.
2. **Zero-Cost Infrastructure**: Only use free/open-source tools or generous free-tier APIs (Google AI Studio).
3. **Separation of Concerns**: Keep frontend (UI) logic in rontend/ and core data/RAG logic in  ackend/.
4. **Token Optimization**: Do not read other documentation files in doc/ unless explicitly required for the current task (e.g., you MUST read `doc/10_coding_guidelines.md` before generating code).

**Next Step**: Read doc/01_current_state.md to understand your current objective.
