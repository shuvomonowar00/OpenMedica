import logging
from typing import List
from pydantic_ai import Agent, RunContext
from models.schemas import ChatResponse, PubMedArticle
from services.llm_factory import get_llm
from services.vector_store import vector_store
from services.query_expansion import expand_query

logger = logging.getLogger(__name__)

# System prompt emphasizing zero-hallucination
SYSTEM_PROMPT = """
You are a highly precise medical AI assistant named OpenMedica.
Your absolute strict instruction is to answer the user's query ONLY using the provided PubMed context.
Do NOT hallucinate or bring in outside medical knowledge.
If the provided context does not contain the answer, you must state: "I cannot answer this based on the retrieved literature."
You must provide citations to the PMIDs of the sources you used.
Return your answer strictly in the requested JSON structure.
"""

# Initialize the Pydantic AI Agent
rag_agent = Agent(
    model=get_llm(),
    output_type=ChatResponse,
    system_prompt=SYSTEM_PROMPT,
)

async def generate_answer(query: str, n_results: int = 5) -> ChatResponse:
    """
    Retrieves context from the vector store and generates a strict, 
    zero-hallucination response using Pydantic AI.
    """
    # 1. Expand query for better retrieval recall
    expansion = await expand_query(query)
    search_query = " ".join([query] + expansion.mesh_terms)
    
    # 2. Retrieve context
    articles = vector_store.query_articles(search_query, n_results=n_results)
    
    # 3. Format context
    if not articles:
        context_str = "No relevant PubMed articles found."
    else:
        context_parts = []
        for a in articles:
            pmc_info = f" | PMCID: {a.pmcid}" if a.pmcid else ""
            pub_types = ", ".join(a.publication_types) if a.publication_types else "Unknown Study Type"
            context_parts.append(f"--- PMID: {a.pmid}{pmc_info} | Type: {pub_types} ---\nTitle: {a.title}\nContent:\n{a.abstract}")
        context_str = "\n\n".join(context_parts)
    
    user_prompt = f"Context from PubMed:\n{context_str}\n\nUser Query: {query}"
    
    logger.info(f"Running RAG Agent for query: '{query}' with {len(articles)} sources.")
    
    # 3. Run the agent (Pydantic AI handles the async run and parsing)
    result = await rag_agent.run(user_prompt)
    
    return result.output
