"""
OpenMedica - Query Expansion Service
Uses Pydantic AI to expand colloquial medical queries into clinical MeSH terms.
"""
import logging
from pydantic_ai import Agent
from models.schemas import QueryExpansionSchema
from services.llm_factory import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert medical vocabularist and search engineer.
Given a user's natural language query or topic, you must:
1. Identify the key medical concepts.
2. Expand them using official MeSH (Medical Subject Headings) terms and synonyms.
3. Formulate expanded search queries optimized for a Boolean search engine (e.g., "heart attack" OR "myocardial infarction").

Return the output strictly in the requested JSON structure.
"""

# Initialize the Pydantic AI Agent for Query Expansion
query_expansion_agent = Agent(
    model=get_llm(),
    output_type=QueryExpansionSchema,
    system_prompt=SYSTEM_PROMPT,
)

async def expand_query(query: str) -> QueryExpansionSchema:
    """
    Expands a raw medical query into MeSH terms and boolean search strings.
    """
    logger.info(f"Running Query Expansion for: '{query}'")
    result = await query_expansion_agent.run(query)
    return result.output
