# OpenMedica - Current State & Tasks

Use this document to track project progress. Update it whenever a task is completed.

## Phase 1: Planning & Architecture
- [x] Define architecture and tech stack
- [x] Create optimized folder structure
- [x] Initialize documentation

## Phase 2: Environment Setup & Tooling
- [x] Initialize project with `uv` (`uv venv` and `uv pip install`)
- [x] Create `backend/requirements.txt` and `frontend/requirements.txt`
- [x] Set up `.env` for API keys and `LLM_PROVIDER` configuration
- [x] Create `Dockerfile` for Backend and Frontend, and root `docker-compose.yml`

## Phase 3: Backend - Core API & Data
- [x] Set up FastAPI scaffold (`backend/main.py`)
- [x] Implement `backend/pubmed_fetcher.py` using Biopython
- [x] Implement Model Agnostic Factory (`backend/llm_factory.py`)

## Phase 4: Backend - RAG Engine (Pydantic AI) (COMPLETED)
- [x] Implement vector storage with ChromaDB
- [x] Implement `backend/rag_agent.py` using Pydantic AI for strict structured output

## Phase 5: Frontend - Streamlit UI (CURRENT)
- [ ] Implement `frontend/app.py` with REST calls to FastAPI backend

**Current Task**: We have fully completed Phase 4. The backend is perfectly tested, features a multi-provider `.env` architecture (zero hardcoding), and successfully connects ChromaDB to Gemini models. In the next chat session, we MUST immediately begin Phase 5 (Frontend). The goal is to build a beautiful, reliable, and clean Streamlit UI in `frontend/app.py` that connects to the FastAPI backend.
