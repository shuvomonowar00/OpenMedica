import pytest
from unittest.mock import patch
from pydantic_ai.models.test import TestModel
from models.schemas import ChatResponse, PubMedArticle
from services.rag_agent import rag_agent, generate_answer

@pytest.mark.asyncio
async def test_generate_answer():
    # Mock the vector store so we don't hit the real ChromaDB
    with patch("services.rag_agent.vector_store.query_articles") as mock_query:
        # Provide a fake context
        mock_query.return_value = [
            PubMedArticle(
                pmid="9999",
                title="Mock Title",
                abstract="Mock abstract.",
                authors=["Mock Author"]
            )
        ]
        
        # Override the agent's model with Pydantic AI's built-in TestModel
        # This prevents actual API calls to Gemini while ensuring the schema and flow work.
        with rag_agent.override(model=TestModel()):
            response = await generate_answer("What is the mock title?")
            
            # Verify the response is correctly structured via our Pydantic schema
            assert isinstance(response, ChatResponse)
            assert hasattr(response, "answer")
            assert hasattr(response, "sources")
