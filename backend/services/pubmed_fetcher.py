"""
OpenMedica - PubMed Fetcher Service
Handles all interactions with the NCBI PubMed database using Biopython.
Follows strict clean coding rules: type hinting, Pydantic schemas, and async IO wrappers.
"""

import asyncio
import os
import logging
import xml.etree.ElementTree as ET
from typing import List, Optional
from Bio import Entrez
from fastapi import HTTPException
from models.schemas import PubMedArticle, ArticleSection

# Configure logging
logger = logging.getLogger(__name__)

# Enforce zero-hardcoding for the NCBI email requirement
_pubmed_email = os.getenv("PUBMED_EMAIL")
if not _pubmed_email:
    raise ValueError("PUBMED_EMAIL environment variable is not set. This is required for NCBI API access.")
Entrez.email = _pubmed_email
Entrez.tool = "OpenMedica_RAG_Pipeline"

# --- Core Logic ---

def _parse_pmc_xml(xml_content: bytes) -> List[ArticleSection]:
    """
    Parses JATS XML from PMC to extract semantic sections.
    """
    sections = []
    try:
        root = ET.fromstring(xml_content)
        # Find all <sec> elements
        for sec in root.iter('sec'):
            title_elem = sec.find('title')
            title = title_elem.text if title_elem is not None and title_elem.text else "Unnamed Section"
            
            # Get all text from paragraphs within this section
            p_elems = sec.findall('.//p')
            texts = []
            for p in p_elems:
                # itertext() extracts text even if there are nested tags like <italic> or <xref>
                p_text = "".join(p.itertext()).strip()
                if p_text:
                    texts.append(p_text)
            
            if texts:
                sections.append(ArticleSection(
                    section_title=title, 
                    content="\n\n".join(texts)
                ))
    except Exception as e:
        logger.warning(f"Failed to parse PMC XML: {e}")
    return sections


def _fetch_pmc_fulltext(pmcid: str) -> List[ArticleSection]:
    """
    Fetches the full text XML from the PMC database and parses it.
    """
    try:
        # Strip 'PMC' prefix if it exists as efetch expects numeric ID or ID with PMC
        id_to_fetch = pmcid if pmcid.startswith("PMC") else pmcid
        fetch_handle = Entrez.efetch(db="pmc", id=id_to_fetch, retmode="xml")
        xml_content = fetch_handle.read()
        fetch_handle.close()
        
        # Biopython's efetch returns bytes in Python 3
        if isinstance(xml_content, str):
            xml_content = xml_content.encode('utf-8')
            
        return _parse_pmc_xml(xml_content)
    except Exception as e:
        logger.warning(f"Failed to fetch or parse PMCID {pmcid}: {e}")
        return []


def _sync_fetch_articles(topic: str, max_results: int, high_evidence_only: bool = False) -> List[PubMedArticle]:
    """
    Synchronous internal function to execute the Biopython network calls.
    Searches PubMed, and if a PMCID is available, fetches the full text from PMC.
    """
    articles: List[PubMedArticle] = []
    
    try:
        # Step 1: Search for PMIDs related to the topic
        search_term = topic
        if high_evidence_only:
            # Append PubMed filters for high-quality evidence
            evidence_filters = ' AND ("Meta-Analysis"[Publication Type] OR "Randomized Controlled Trial"[Publication Type] OR "Systematic Review"[Publication Type])'
            search_term += evidence_filters
            
        search_handle = Entrez.esearch(db="pubmed", term=search_term, retmax=max_results)
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
        pubmed_articles = records.get("PubmedArticle", [])
        
        for record in pubmed_articles:
            try:
                medline_citation = record.get("MedlineCitation", {})
                article_data = medline_citation.get("Article", {})
                
                pmid = str(medline_citation.get("PMID", ""))
                title = str(article_data.get("ArticleTitle", ""))
                
                # Extract abstract text (fallback/summary)
                abstract_data = article_data.get("Abstract", {}).get("AbstractText", [])
                abstract = " ".join([str(text) for text in abstract_data]) if abstract_data else ""
                
                if not abstract:
                    continue  # Still require an abstract as a baseline
                
                # Extract authors
                authors: List[str] = []
                author_list = article_data.get("AuthorList", [])
                for author in author_list:
                    last_name = author.get("LastName", "")
                    initials = author.get("Initials", "")
                    if last_name or initials:
                        authors.append(f"{last_name} {initials}".strip())
                        
                # Extract publication types
                publication_types: List[str] = []
                pub_type_list = article_data.get("PublicationTypeList", [])
                for pt in pub_type_list:
                    publication_types.append(str(pt))
                
                # Attempt to find a PMCID for full-text
                pmcid = None
                pubmed_data = record.get("PubmedData", {})
                article_ids = pubmed_data.get("ArticleIdList", [])
                for aid in article_ids:
                    # Depending on Biopython version, attributes might be accessible via .attributes
                    if hasattr(aid, 'attributes') and aid.attributes.get("IdType") == "pmc":
                        pmcid = str(aid)
                        break
                
                sections = []
                if pmcid:
                    logger.info(f"Found PMCID {pmcid} for PMID {pmid}. Fetching full text...")
                    sections = _fetch_pmc_fulltext(pmcid)
                
                # If we couldn't get sections from PMC, we fallback to just having the abstract chunk
                if not sections:
                    sections.append(ArticleSection(
                        section_title="Abstract",
                        content=abstract
                    ))
                        
                articles.append(
                    PubMedArticle(
                        pmid=pmid,
                        pmcid=pmcid,
                        title=title,
                        abstract=abstract,
                        authors=authors,
                        sections=sections,
                        publication_types=publication_types
                    )
                )
            except Exception as parse_error:
                logger.warning(f"Error parsing an article record: {parse_error}")
                continue
                
        return articles
        
    except Exception as e:
        logger.error(f"Entrez API Error: {str(e)}")
        raise ValueError(f"Failed to fetch data from PubMed: {str(e)}")


async def fetch_abstracts(topic: str, max_results: int = 10, high_evidence_only: bool = False) -> List[PubMedArticle]:
    """
    Asynchronously fetches articles (abstracts and full text if available) from PubMed/PMC.
    Note: kept the function name `fetch_abstracts` to avoid breaking `main.py` routing 
    if it expects this name, but it now fetches full articles.
    """
    try:
        articles = await asyncio.to_thread(_sync_fetch_articles, topic, max_results, high_evidence_only)
        return articles
    except ValueError as ve:
        raise HTTPException(status_code=502, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error during fetching: {str(e)}")
