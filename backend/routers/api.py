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
