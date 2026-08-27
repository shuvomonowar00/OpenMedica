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

**Current Task**: We have completed Phase 4 (Backend - RAG Engine) including ChromaDB and the Pydantic AI agent. The next step is Phase 5 (Frontend - Streamlit UI), which involves building `frontend/app.py` to make REST calls to our backend.
