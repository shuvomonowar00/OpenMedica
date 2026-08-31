"""
OpenMedica - API Router
Contains the core REST endpoints for the application.
"""
import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import (
    IngestRequest, 
    IngestResponse, 
    ChatRequest, 
    ChatResponse,
    FeedbackRequest
)
from services.pubmed_fetcher import fetch_abstracts
from services.vector_store import vector_store
from services.rag_agent import generate_answer
from services.query_expansion import expand_query

router = APIRouter(tags=["API Endpoints"])

# Define the log file path securely within the backend directory
FEEDBACK_LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "feedback_logs.jsonl")

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Logs user feedback (thumbs up/down) to a local JSONL file for continuous evaluation.
    """
    try:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": request.query,
            "is_positive": request.is_positive,
            "answer": request.answer
        }
        
        with open(FEEDBACK_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return {"message": "Feedback recorded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")

@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(request: IngestRequest) -> IngestResponse:
    """
    Trigger the ingestion pipeline.
    Fetches abstracts from PubMed based on the topic and stores them in ChromaDB.
    """
    try:
        # 1. Expand the query for better PubMed search recall
        expansion = await expand_query(request.topic)
        # Use the first boolean expanded query if available, fallback to original topic
        search_topic = expansion.expanded_search_queries[0] if expansion.expanded_search_queries else request.topic
        
        # 2. Fetch real data using the pubmed_fetcher service
        articles = await fetch_abstracts(
            topic=search_topic, 
            max_results=request.max_results,
            high_evidence_only=request.high_evidence_only
        )
        
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
        filters = {
            "study_type": request.study_type,
            "date_filter": request.date_filter
        }
        # Generate the answer using our Pydantic AI agent and vector store context
        agent_response = await generate_answer(
            query=request.query, 
            history=request.history,
            filters=filters,
            n_results=request.n_results
        )
        
        # Enrich the PMIDs with full citation data for the UI
        pmids = agent_response.sources
        citation_data = vector_store.get_articles_by_pmids(pmids)
        
        return ChatResponse(
            population=agent_response.population,
            intervention=agent_response.intervention,
            comparison=agent_response.comparison,
            outcome=agent_response.outcome,
            answer=agent_response.answer,
            sources=citation_data,
            mesh_terms=agent_response.mesh_terms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")

@router.get("/database")
async def view_database():
    """
    Utility endpoint to peek inside ChromaDB and see what articles are currently stored.
    """
    try:
        # get() fetches ids, metadatas, and documents
        data = vector_store.collection.get(include=["metadatas", "documents"])
        ids = data.get("ids", [])
        metadatas = data.get("metadatas", [])
        documents = data.get("documents", [])
        
        articles = []
        for i in range(len(ids)):
            meta = metadatas[i] if metadatas else {}
            doc = documents[i] if documents else ""
            articles.append({
                "id": ids[i],
                "pmid": meta.get("pmid", ""),
                "title": meta.get("title", ""),
                "authors": meta.get("authors", ""),
                "pub_year": meta.get("pub_year", 0),
                "publication_types": meta.get("publication_types", ""),
                "abstract": doc
            })
            
        return {
            "total_articles": len(ids),
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read database: {str(e)}")

@router.delete("/database/{pmid}")
async def delete_article(pmid: str):
    """
    Deletes an article from ChromaDB using its PMID.
    """
    try:
        vector_store.delete_article(pmid)
        return {"message": f"Successfully deleted article {pmid}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")
