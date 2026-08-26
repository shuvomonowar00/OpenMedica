"""
OpenMedica - API Schemas
Contains Pydantic models for request and response validation.
"""
from typing import List
from pydantic import BaseModel, Field

class PubMedArticle(BaseModel):
    """Strict schema for a PubMed article to guarantee clean data for ChromaDB."""
    pmid: str = Field(..., description="Unique PubMed ID")
    title: str = Field(..., description="Title of the medical paper")
    abstract: str = Field(..., description="Full text of the abstract")
    authors: List[str] = Field(default_factory=list, description="List of author names")

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
