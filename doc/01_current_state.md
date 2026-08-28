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

## Phase 5: Streamlit Frontend UI (COMPLETED)
- [x] **Task 5.1: Frontend Scaffolding & Configuration**: Set up `app.py`, page config (wide layout), and modular directory structure (e.g., `components/`).
- [x] **Task 5.2: UI Layout & Custom Styling**: Implement an OpenEvidence-style clean, minimalist layout using custom CSS (typography, hiding default menus, polished chat interface).
- [x] **Task 5.3: State Management & API Client**: Implement Streamlit session state (chat history, citations) and an `api_client.py` for robust REST communication with the FastAPI backend.
- [x] **Task 5.4: Core Chat Interface**: Build the main conversational UI using `st.chat_message` and `st.chat_input` for seamless user interaction.
- [x] **Task 5.5: Citations & Grounding Display**: Create a beautiful UI component to display PubMed references and metadata, ensuring the zero-hallucination grounding is clearly visible to the user.

**Current Task**: Phase 5 is completed. The frontend has been beautifully styled and integrates modularly with the backend API. Next steps could involve Docker/Local testing and moving to advanced features in Phase 6.
