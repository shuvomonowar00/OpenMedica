"""
OpenMedica - API Router
Contains the core REST endpoints for the application.
"""
from fastapi import APIRouter, HTTPException
from models.schemas import IngestRequest, IngestResponse, ChatRequest, ChatResponse
from services.pubmed_fetcher import fetch_abstracts
from services.vector_store import vector_store
from services.rag_agent import generate_answer

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
        
        # Store articles in ChromaDB
        if articles:
            vector_store.add_articles(articles)
        
        return IngestResponse(
            message=f"Successfully fetched and stored abstracts for topic: '{request.topic}'.",
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
        # Generate the answer using our Pydantic AI agent and vector store context
        response = await generate_answer(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")
