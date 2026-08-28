"""
OpenMedica - PubMed Fetcher Service
Handles all interactions with the NCBI PubMed database using Biopython.
Follows strict clean coding rules: type hinting, Pydantic schemas, and async IO wrappers.
"""

import asyncio
import os
import logging
from typing import List
from Bio import Entrez
from fastapi import HTTPException
from models.schemas import PubMedArticle

# Configure logging
logger = logging.getLogger(__name__)

# Enforce zero-hardcoding for the NCBI email requirement
_pubmed_email = os.getenv("PUBMED_EMAIL")
if not _pubmed_email:
    raise ValueError("PUBMED_EMAIL environment variable is not set. This is required for NCBI API access.")
Entrez.email = _pubmed_email
Entrez.tool = "OpenMedica_RAG_Pipeline"

# --- Core Logic ---

def _sync_fetch_abstracts(topic: str, max_results: int) -> List[PubMedArticle]:
    """
    Synchronous internal function to execute the Biopython network calls.
    """
    articles: List[PubMedArticle] = []
    
    try:
        # Step 1: Search for PMIDs related to the topic
        search_handle = Entrez.esearch(db="pubmed", term=topic, retmax=max_results)
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        id_list = search_results.get("IdList", [])
        if not id_list:
            return articles  # Return empty list if no results found
            
        # Step 2: Fetch the actual article metadata for those PMIDs
        fetch_handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        # Step 3: Parse the deeply nested Biopython dictionary safely
        # PubMed returns records inside a list under 'PubmedArticle'
        pubmed_articles = records.get("PubmedArticle", [])
        
        for record in pubmed_articles:
            try:
                medline_citation = record.get("MedlineCitation", {})
                article_data = medline_citation.get("Article", {})
                
                pmid = str(medline_citation.get("PMID", ""))
                title = str(article_data.get("ArticleTitle", ""))
                
                # Extract abstract text (can be missing or provided as a list of parts)
                abstract_data = article_data.get("Abstract", {}).get("AbstractText", [])
                abstract = " ".join([str(text) for text in abstract_data]) if abstract_data else ""
                
                # Skip articles that have no abstract (useless for our RAG pipeline)
                if not abstract:
                    continue
                    
                # Extract authors safely
                authors: List[str] = []
                author_list = article_data.get("AuthorList", [])
                for author in author_list:
                    last_name = author.get("LastName", "")
                    initials = author.get("Initials", "")
                    if last_name or initials:
                        authors.append(f"{last_name} {initials}".strip())
                        
                articles.append(
                    PubMedArticle(
                        pmid=pmid,
                        title=title,
                        abstract=abstract,
                        authors=authors
                    )
                )
            except Exception as parse_error:
                # Log the parsing error but continue processing other articles
                logger.warning(f"Error parsing an article record: {parse_error}")
                continue
                
        return articles
        
    except Exception as e:
        logger.error(f"Entrez API Error: {str(e)}")
        raise ValueError(f"Failed to fetch data from PubMed: {str(e)}")


async def fetch_abstracts(topic: str, max_results: int = 10) -> List[PubMedArticle]:
    """
    Asynchronously fetches abstracts from PubMed for a given medical topic.
    Wraps the synchronous Biopython network calls in a non-blocking thread.
    
    Args:
        topic (str): The medical query (e.g., "Type 2 Diabetes").
        max_results (int): The maximum number of abstracts to return.
        
    Returns:
        List[PubMedArticle]: A list of strictly validated article objects.
    """
    try:
        # Use asyncio.to_thread to prevent Biopython from blocking the FastAPI event loop
        articles = await asyncio.to_thread(_sync_fetch_abstracts, topic, max_results)
        return articles
    except ValueError as ve:
        # Re-raise as an HTTP exception for FastAPI to handle cleanly
        raise HTTPException(status_code=502, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error during fetching: {str(e)}")
