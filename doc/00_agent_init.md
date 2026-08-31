# OpenMedica - Agent Initialization Context

**Project**: OpenMedica
**Goal**: A zero-hallucination Medical RAG pipeline built on an OpenEvidence-style architecture. It strictly grounds answers in peer-reviewed PubMed/PMC literature.

## Tech Stack & Architecture
**CRITICAL**: You must strictly adhere to the approved tech stack. Read `doc/09_tech_stack.md` for the exact libraries. 
- **Architecture**: We use a Hybrid Search approach (ChromaDB Vector + BM25 Keyword) and a Multi-Agent system (Synthesizer & Reviewer) via Pydantic AI.

## Strict Rules for AI Agents
1. **Zero Hallucination**: All LLM responses MUST be strictly grounded in the retrieved evidence.
2. **PICO Format**: When dealing with clinical questions, output generation should follow the PICO framework (Population, Intervention, Comparison, Outcome).
3. **Zero-Cost Infrastructure**: Only use free/open-source tools or generous free-tier APIs (Google AI Studio).
4. **Separation of Concerns**: Keep frontend (UI) logic strictly in `frontend/` and core data/RAG logic strictly in `backend/`.
5. **Token Optimization**: Do not read other documentation files in `doc/` unless explicitly required for the current task (e.g., you MUST read `doc/10_coding_guidelines.md` before generating code, and `doc/02_architecture.md` before altering the RAG pipeline).

**Next Step**: Read `doc/01_current_state.md` to understand your current objective.
