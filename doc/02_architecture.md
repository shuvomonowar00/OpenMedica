# Architecture & Data Flow

## System Architecture (Dockerized Microservices)
The system is divided into decoupled microservices orchestrated by Docker Compose:

1. **Frontend Service (Streamlit)**: Lightweight UI. Handles user interaction, UI filters, conversational memory, and renders PICO-formatted data and Evidence Grades. Contains ZERO AI or database logic. Communicates with the backend via REST API.
2. **Backend Service (FastAPI)**: The core engine. Exposes REST endpoints (e.g., `/api/chat`, `/api/ingest`). Handles PubMed/PMC fetching, Hybrid Search (ChromaDB + BM25), and Pydantic AI orchestration.
3. **Model Agnostic Factory**: A configuration layer in the backend that reads `.env` variables to dynamically inject the chosen LLM provider (e.g., Gemini, OpenAI) into Pydantic AI, ensuring the system remains plug-and-play.

## RAG Data Flow (OpenEvidence-Style Pipeline)
1. **Query Expansion**: User inputs medical topic -> System expands colloquial terms into clinical MeSH terms.
2. **Ingestion & Processing**: Backend queries PubMed API/PMC -> Downloads abstracts and/or full-text articles -> Applies intelligent chunking.
3. **Embedding & Indexing**: Text chunks are embedded and stored in **ChromaDB** (Semantic search). Simultaneously, text is indexed in a local **BM25 index** (Keyword search).
4. **Hybrid Retrieval**: Expanded query is sent to both ChromaDB and BM25. The two resulting lists are merged and re-ranked (e.g., via Reciprocal Rank Fusion) to fetch the top contextually and keyword-accurate chunks.
5. **Multi-Agent Generation**: 
   - *Synthesizer Agent*: Drafts a strict PICO-formatted response based on the top chunks.
   - *Reviewer Agent*: Verifies the draft against the retrieved text to ensure zero hallucinations.
6. **Response**: FastAPI returns the verified, structured JSON (with PICO elements, citations, and evidence grades) to Streamlit.
7. **UI Render**: Streamlit renders the structured response and provides options for User Feedback (Thumbs Up/Down).
