# OpenMedica - Current State & Tasks

Use this document to track project progress. Update it whenever a task is completed.

## Phase 1: Planning & Architecture (COMPLETED)
- [x] Define architecture and tech stack
- [x] Create optimized folder structure
- [x] Initialize documentation

## Phase 2: Environment Setup & Tooling (COMPLETED)
- [x] Initialize project with `uv` (`uv venv` and `uv pip install`)
- [x] Create `backend/requirements.txt` and `frontend/requirements.txt`
- [x] Set up `.env` for API keys and `LLM_PROVIDER` configuration
- [x] Create `Dockerfile` for Backend and Frontend, and root `docker-compose.yml`

## Phase 3: Backend - Core API & Data (COMPLETED)
- [x] Set up FastAPI scaffold (`backend/main.py`)
- [x] Implement `backend/pubmed_fetcher.py` using Biopython
- [x] Implement Model Agnostic Factory (`backend/llm_factory.py`)

## Phase 4: Backend - RAG Engine (Pydantic AI) (COMPLETED)
- [x] Implement vector storage with ChromaDB
- [x] Implement `backend/rag_agent.py` using Pydantic AI for strict structured output

## Phase 5: Streamlit Frontend UI (COMPLETED)
- [x] **Task 5.1: Frontend Scaffolding & Configuration**
- [x] **Task 5.2: UI Layout & Custom Styling**
- [x] **Task 5.3: State Management & API Client**
- [x] **Task 5.4: Core Chat Interface**
- [x] **Task 5.5: Citations & Grounding Display**

## Phase 6: Clinical Evidence Expansion
- [x] **Task 6.1**: Implement Full-Text Ingestion (PMC) and Intelligent Chunking.
- [x] **Task 6.2**: Implement Evidence Hierarchy Filtering (e.g., RCTs, Meta-Analyses).

## Phase 7: Clinical Search & RAG Architecture
- [x] **Task 7.1**: Implement Medical Query Expansion (MeSH term mapping).
- [x] **Task 7.2**: Implement Hybrid Search (Manual fusion of ChromaDB Vector + Python BM25).
- [ ] **Task 7.3**: Implement Multi-Agent Verification Pipeline (Synthesizer + Reviewer).

## Phase 8: OpenEvidence-Style UI/UX
- [ ] **Task 8.1**: Enforce PICO-Formatted Outputs from the LLM.
- [ ] **Task 8.2**: Build Evidence Grading UI (badges for RCTs/Reviews).
- [ ] **Task 8.3**: Add Conversational Memory & UI Filters (Date, Study Type).
- [ ] **Task 8.4**: Add Export & Share functionality.
- [ ] **Task 8.5**: Expose expanded MeSH terms and search queries in the UI.

## Phase 9: Evaluation & Safety
- [ ] **Task 9.1**: Build Automated RAG Evaluation test set.
- [ ] **Task 9.2**: Integrate User Feedback Loop in the UI.

**Current Task**: Starting Task 7.3 (Phase 7). We will implement the Multi-Agent Verification Pipeline (Synthesizer + Reviewer).
