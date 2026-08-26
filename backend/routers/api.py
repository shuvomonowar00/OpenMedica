"""
OpenMedica - API Router
Contains the core REST endpoints for the application.
"""
from fastapi import APIRouter, HTTPException
from schemas import IngestRequest, IngestResponse, ChatRequest, ChatResponse
from pubmed_fetcher import fetch_abstracts

router = APIRouter(tags=["API Endpoints"])

@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(request: IngestRequest) -> IngestResponse:
    """
    Trigger the ingestion pipeline.
    Fetches abstracts from PubMed based on the topic and stores them in ChromaDB.
    """
    try:
        # Fetch real data using the pubmed_fetcher service
        articles = await fetch_abstracts(topic=request.topic, max_results=request.max_results)
        
        # TODO: Store 'articles' in ChromaDB (Phase 4)
        
        return IngestResponse(
            message=f"Successfully fetched abstracts for topic: '{request.topic}'. ChromaDB storage pending.",
            articles_ingested=len(articles)
        )
    except Exception as e:
        # Catch unexpected errors and raise as HTTP 500
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
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
