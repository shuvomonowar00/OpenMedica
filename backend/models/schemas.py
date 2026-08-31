"""
OpenMedica - API Schemas
Contains Pydantic models for request and response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ArticleSection(BaseModel):
    """Schema representing a semantic section of a full-text medical article."""
    section_title: str = Field(..., description="The title of the section (e.g., Introduction, Methods)")
    content: str = Field(..., description="The textual content of this specific section")

class PubMedArticle(BaseModel):
    """Strict schema for a PubMed article to guarantee clean data for ChromaDB."""
    pmid: str = Field(..., description="Unique PubMed ID")
    pmcid: Optional[str] = Field(default=None, description="Optional PMC ID if full text is available")
    title: str = Field(..., description="Title of the medical paper")
    abstract: str = Field(..., description="Full text of the abstract (fallback/summary)")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    sections: List[ArticleSection] = Field(default_factory=list, description="Intelligently chunked sections of the full text")
    publication_types: List[str] = Field(default_factory=list, description="List of study types (e.g., Meta-Analysis, RCT)")

class IngestRequest(BaseModel):
    """Schema for data ingestion requests from PubMed."""
    topic: str = Field(..., description="The medical topic or query to search on PubMed")
    max_results: int = Field(default=10, description="Maximum number of abstracts to fetch")
    high_evidence_only: bool = Field(default=False, description="If true, strictly filters for RCTs and Meta-Analyses")

class IngestResponse(BaseModel):
    """Schema for data ingestion responses."""
    message: str
    articles_ingested: int

class QueryExpansionSchema(BaseModel):
    """Schema for expanded medical queries with MeSH terms."""
    original_query: str = Field(..., description="The original user query")
    mesh_terms: List[str] = Field(default_factory=list, description="List of official MeSH terms")
    expanded_search_queries: List[str] = Field(default_factory=list, description="List of boolean search queries")

class ReviewSchema(BaseModel):
    """Schema for the strict multi-agent reviewer."""
    is_grounded: bool = Field(..., description="True if the draft is 100% grounded in the context, False if there are hallucinations or unsupported claims.")
    feedback: str = Field(..., description="Detailed feedback on what claims are unsupported, or 'Looks good' if grounded.")

class ChatRequest(BaseModel):
    """Schema for user chat queries."""
    query: str = Field(..., description="The user's medical question")

class ChatResponse(BaseModel):
    """Schema for RAG chat responses, ensuring strict structure."""
    answer: str
    sources: list[str] = Field(default_factory=list, description="List of PMIDs used as sources")
