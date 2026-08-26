"""
OpenMedica - Backend Core API
This module initializes the FastAPI application and defines the core REST endpoints
for ingestion and chat functionalities.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Initialize FastAPI application
app = FastAPI(
    title="OpenMedica Backend API",
    description="Core REST API engine for the OpenMedica Medical RAG pipeline.",
    version="0.1.0"
)

# Enable CORS for Streamlit frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to restrict to Streamlit's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas ---

class IngestRequest(BaseModel):
    """Schema for data ingestion requests from PubMed."""
    topic: str = Field(..., description="The medical topic or query to search on PubMed")
    max_results: int = Field(default=10, description="Maximum number of abstracts to fetch")

class IngestResponse(BaseModel):
    """Schema for data ingestion responses."""
    message: str
    articles_ingested: int

class ChatRequest(BaseModel):
    """Schema for user chat queries."""
    query: str = Field(..., description="The user's medical question")

class ChatResponse(BaseModel):
    """Schema for RAG chat responses, ensuring strict structure."""
    answer: str
    sources: list[str] = Field(default_factory=list, description="List of PMIDs used as sources")

# --- API Endpoints ---

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok"}

@app.post("/api/ingest", response_model=IngestResponse, tags=["Data Pipeline"])
async def ingest_data(request: IngestRequest) -> IngestResponse:
    """
    Trigger the ingestion pipeline.
    Fetches abstracts from PubMed based on the topic and stores them in ChromaDB.
    """
    try:
        # TODO: Integrate with backend/pubmed_fetcher.py and ChromaDB
        # Placeholder logic
        return IngestResponse(
            message=f"Successfully queued ingestion for topic: '{request.topic}'",
            articles_ingested=request.max_results
        )
    except Exception as e:
        # Catch unexpected errors and raise as HTTP 500
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Submit a medical question to the RAG pipeline.
    Retrieves relevant contexts from ChromaDB and generates an answer via Pydantic AI.
    """
    try:
        # TODO: Integrate with backend/rag_agent.py (ChromaDB + Pydantic AI)
        # Placeholder logic
        return ChatResponse(
            answer=f"This is a placeholder response for: '{request.query}'. True RAG integration pending.",
            sources=["PMID:12345678 (Placeholder)"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")
