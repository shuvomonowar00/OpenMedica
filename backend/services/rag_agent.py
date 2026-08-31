import logging
from typing import List
from pydantic_ai import Agent, RunContext
from models.schemas import AgentChatResponse, PubMedArticle, ReviewSchema
from services.llm_factory import get_llm
from services.vector_store import vector_store
from services.query_expansion import expand_query

logger = logging.getLogger(__name__)

# --- SYNTHESIZER AGENT ---
SYSTEM_PROMPT = """
You are a highly precise medical AI assistant named OpenMedica.
Your absolute strict instruction is to answer the user's query ONLY using the provided PubMed context.
Do NOT hallucinate or bring in outside medical knowledge.

Before generating the final answer, you must extract the clinical context using the PICO framework:
1. Population (Patient or Problem)
2. Intervention (or Exposure)
3. Comparison (Control, if applicable)
4. Outcome

If the provided context does not contain the answer, you must state: "I cannot answer this based on the retrieved literature."
You must provide citations to the PMIDs of the sources you used.
Return your answer strictly in the requested JSON structure.
"""

rag_agent = Agent(
    model=get_llm(),
    output_type=AgentChatResponse,
    system_prompt=SYSTEM_PROMPT,
)

# --- REVIEWER AGENT ---
REVIEWER_PROMPT = """
You are a strict, paranoid medical fact-checker. 
Your job is to read a drafted answer and compare it word-for-word against the provided PubMed context.
You must fail the draft (is_grounded=False) if the draft makes ANY clinical claim, mentions any side effect, or provides any data that is NOT explicitly stated in the context.
If it fails, provide detailed feedback on exactly what needs to be removed or changed.
"""

reviewer_agent = Agent(
    model=get_llm(),
    output_type=ReviewSchema,
    system_prompt=REVIEWER_PROMPT,
)

async def generate_answer(query: str, history: List[dict] = None, filters: dict = None, n_results: int = 5) -> AgentChatResponse:
    """
    Retrieves context from the vector store and generates a strict, 
    zero-hallucination response using Pydantic AI's multi-agent loop.
    """
    if history is None:
        history = []
    
    # Format conversational history into a clean transcript for the agent
    history_transcript = ""
    if history:
        history_transcript = "--- Previous Conversation History ---\n"
        for msg in history:
            role = "User" if msg.get("role") == "user" else "AI"
            content = msg.get("content", "")
            history_transcript += f"{role}: {content}\n\n"
        history_transcript += "-------------------------------------\n\n"

    # 1. Expand query for better retrieval recall
    expansion = await expand_query(query)
    search_query = " ".join([query] + expansion.mesh_terms)
    
    # 2. Retrieve context with UI Filters
    articles = vector_store.query_articles(search_query, filters=filters, n_results=n_results)
    
    # 3. Format context
    if not articles:
        context_str = "No relevant PubMed articles found for the given criteria."
    else:
        context_parts = []
        for a in articles:
            pmc_info = f" | PMCID: {a.pmcid}" if a.pmcid else ""
            pub_types = ", ".join(a.publication_types) if a.publication_types else "Unknown Study Type"
            context_parts.append(f"--- PMID: {a.pmid}{pmc_info} | Type: {pub_types} ---\nTitle: {a.title}\nContent:\n{a.abstract}")
        context_str = "\n\n".join(context_parts)
    
    user_prompt = f"{history_transcript}Context from PubMed:\n{context_str}\n\nNew User Query: {query}"
    
    logger.info(f"Running Synthesizer Agent for query: '{query}' with {len(articles)} sources and filters: {filters}")
    
    # 4. Multi-Agent Verification Loop
    synth_result = await rag_agent.run(user_prompt)
    draft = synth_result.output
    
    reviewer_prompt = f"Context from PubMed:\n{context_str}\n\nDraft Answer:\n{draft.answer}"
    logger.info("Running Reviewer Agent...")
    review_result = await reviewer_agent.run(reviewer_prompt)
    review = review_result.output
    
    max_retries = 2
    attempts = 0
    
    while not review.is_grounded and attempts < max_retries:
        logger.warning(f"Reviewer rejected draft. Feedback: {review.feedback}. Retrying... (Attempt {attempts + 1}/{max_retries})")
        
        # Give the Synthesizer the feedback to fix it
        retry_prompt = f"{user_prompt}\n\nYour previous draft was rejected by the medical reviewer for the following reasons:\n{review.feedback}\n\nPlease rewrite your answer to strictly adhere to the context."
        
        synth_result = await rag_agent.run(retry_prompt)
        draft = synth_result.output
        
        reviewer_prompt = f"Context from PubMed:\n{context_str}\n\nDraft Answer:\n{draft.answer}"
        review_result = await reviewer_agent.run(reviewer_prompt)
        review = review_result.output
        attempts += 1
        
    if not review.is_grounded:
        logger.error("Synthesizer failed to produce a grounded answer after max retries.")
        # Fallback to prevent returning dangerous hallucinations
        draft.answer = "⚠️ [WARNING: Our AI reviewer flagged potential inaccuracies in this draft based on the literature. Proceed with caution.]\n\n" + draft.answer
        
    return draft
