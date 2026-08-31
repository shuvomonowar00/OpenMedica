import os
import sys
import json
import asyncio
import logging
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_factory import get_llm
from services.rag_agent import generate_answer
from services.pubmed_fetcher import fetch_abstracts
from services.vector_store import vector_store
from models.eval_schemas import EvaluationResult

# Configure logging for the evaluator
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EVALUATOR_PROMPT = """
You are an expert clinical AI evaluator. Your job is to assess the quality of a RAG (Retrieval-Augmented Generation) pipeline.
You will be provided with:
1. The User's Medical Query
2. The PubMed Context Retrieved by the Vector Database
3. The AI's Drafted Answer (including PICO breakdown)

You must carefully evaluate the AI's answer and output your evaluation exactly in the requested JSON format.

CRITICAL RULES:
- Groundedness (1-5): If the AI makes ANY clinical claim that is NOT explicitly supported by the Context, you must deduct points aggressively. 
- Relevance (1-5): Does the AI directly answer the user's question?
- PICO Completeness: Did the AI identify Population, Intervention, and Outcome? (Comparison is optional).
"""

evaluator_agent = Agent(
    model=get_llm(),
    output_type=EvaluationResult,
    system_prompt=EVALUATOR_PROMPT,
)

async def run_evaluation():
    dataset_path = os.path.join(os.path.dirname(__file__), "eval_dataset.json")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
        
    print("\n" + "="*50)
    print("🚀 Starting Automated RAG Evaluation...")
    print("="*50 + "\n")
    
    total_groundedness = 0
    total_relevance = 0
    total_pico = 0
    num_queries = len(dataset)
    
    for item in dataset:
        query = item["query"]
        print(f"\nEvaluating Query: '{query}'")
        
        # 1. Ingest Data (Ensure we have context for this query)
        logger.info("Ingesting PubMed articles to build context...")
        articles = await fetch_abstracts(topic=query, max_results=3, high_evidence_only=False)
        vector_store.add_articles(articles)
        
        # 2. Run the RAG Pipeline
        logger.info("Generating answer via multi-agent RAG pipeline...")
        # (Pass an empty history and no filters)
        agent_response = await generate_answer(query=query)
        
        # Extract the retrieved context from vector store to pass to the evaluator
        # (We duplicate the retrieval here just to see what the agent saw)
        retrieved_articles = vector_store.query_articles(query, n_results=5)
        context_str = "\n".join([a.abstract for a in retrieved_articles])
        
        # 3. Grade the Response
        logger.info("Grading response...")
        eval_prompt = f"""
        User Query: {query}
        
        --- RETRIEVED CONTEXT ---
        {context_str}
        
        --- AI'S GENERATED ANSWER ---
        Population: {agent_response.population}
        Intervention: {agent_response.intervention}
        Comparison: {agent_response.comparison}
        Outcome: {agent_response.outcome}
        Synthesis: {agent_response.answer}
        """
        
        eval_result = await evaluator_agent.run(eval_prompt)
        score: EvaluationResult = eval_result.output
        
        print(f"  ↳ Groundedness: {score.groundedness_score}/5")
        print(f"  ↳ Relevance:    {score.relevance_score}/5")
        print(f"  ↳ PICO Check:   {'✅ Pass' if score.pico_completeness else '❌ Fail'}")
        print(f"  ↳ Reasoning:    {score.reasoning}")
        
        total_groundedness += score.groundedness_score
        total_relevance += score.relevance_score
        if score.pico_completeness:
            total_pico += 1
            
    print("\n" + "="*50)
    print("📊 FINAL EVALUATION REPORT")
    print("="*50)
    print(f"Average Groundedness: {total_groundedness / num_queries:.1f} / 5.0")
    print(f"Average Relevance:    {total_relevance / num_queries:.1f} / 5.0")
    print(f"PICO Accuracy:        {(total_pico / num_queries)*100:.0f}%")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
