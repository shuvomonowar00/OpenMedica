# OpenMedica - Authorized Tech Stack

Agents MUST strictly use the following technologies. Do not introduce alternative libraries without explicit user permission.

## Infrastructure & Tooling
- **Package Manager**: `uv` (for ultra-fast dependency resolution and virtual environments)
- **Containerization**: Docker & Docker Compose (for isolating microservices)

## Frontend (User Interface)
- **Framework**: Streamlit (`streamlit`)
- **Communication**: HTTP REST calls to backend via `requests`
- **Purpose**: Rapid MVP user interface, completely decoupled from AI logic.

## Backend Service (API & Data)
- **API Framework**: FastAPI (`fastapi`, `uvicorn`)
- **Purpose**: REST API providing endpoints for search and chat.

## Data Ingestion
- **Source**: PubMed API
- **Library**: Biopython (`biopython`)
- **Purpose**: Fetching peer-reviewed medical abstracts.

## RAG & Vector Storage
- **Vector Database**: ChromaDB (`chromadb`)
  *Note: Stores metadata (PMIDs, Authors) alongside vectors.*
- **Agent Framework**: Pydantic AI (`pydantic-ai`)
  *Note: Chosen over LangChain for strict schema enforcement and zero-hallucination guarantees.*

## Artificial Intelligence (Plug & Play)
- **Architecture**: Model Agnostic Factory Pattern.
- **Default LLM**: Gemini 1.5 Flash/Pro via Google AI Studio.
- **Embeddings**: Gemini Embeddings (`text-embedding-004`).
- **Integration**: Handled via Pydantic AI's model providers.
