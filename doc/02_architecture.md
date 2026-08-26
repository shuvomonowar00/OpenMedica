# Architecture & Data Flow

## System Architecture (Dockerized Microservices)
The system is divided into decoupled microservices orchestrated by Docker Compose:

1. **Frontend Service (Streamlit)**: Lightweight UI. Handles user interaction and renders data. Contains ZERO AI or database logic. Communicates with the backend via REST API.
2. **Backend Service (FastAPI)**: The core engine. Exposes REST endpoints (e.g., `/api/chat`, `/api/ingest`). Handles PubMed fetching, ChromaDB queries, and Pydantic AI orchestration.
3. **Model Agnostic Factory**: A configuration layer in the backend that reads `.env` variables to dynamically inject the chosen LLM provider (e.g., Gemini, OpenAI) into Pydantic AI, ensuring the system remains plug-and-play.

## RAG Data Flow
1. **Ingestion**: User inputs medical topic -> FastAPI Backend queries PubMed API via Biopython -> Downloads recent abstracts with metadata (PMID, Authors).
2. **Embedding**: Text is chunked -> Embedding API converts text to vectors -> Vectors & Metadata are stored in the local ChromaDB instance.
3. **Retrieval**: User asks specific question -> FastAPI queries ChromaDB for semantic similarity -> Retrieves top K abstracts.
4. **Generation (Strict Schema)**: Top abstracts + User query passed to Pydantic AI -> Pydantic AI enforces strict output validation -> LLM generates an answer with strict citations to the retrieved PMIDs.
5. **Response**: FastAPI returns the structured JSON to Streamlit -> Streamlit renders the response for the user.
