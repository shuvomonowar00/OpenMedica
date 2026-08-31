import pytest
from unittest.mock import patch, AsyncMock
from models.schemas import ChatResponse, PubMedArticle, QueryExpansionSchema, ReviewSchema
from services.rag_agent import generate_answer

@pytest.mark.asyncio
async def test_generate_answer_success():
    with patch("services.rag_agent.vector_store.query_articles") as mock_query, \
         patch("services.rag_agent.expand_query") as mock_expand, \
         patch("services.rag_agent.rag_agent.run", new_callable=AsyncMock) as mock_rag_run, \
         patch("services.rag_agent.reviewer_agent.run", new_callable=AsyncMock) as mock_reviewer_run:
         
        mock_expand.return_value = QueryExpansionSchema(
            original_query="query", mesh_terms=["mesh"], expanded_search_queries=["query OR mesh"]
        )
        mock_query.return_value = [
            PubMedArticle(pmid="9999", title="Mock Title", abstract="Mock", authors=["Author"])
        ]
        
        mock_rag_run.return_value.output = ChatResponse(answer="Mock answer", sources=["9999"])
        mock_reviewer_run.return_value.output = ReviewSchema(is_grounded=True, feedback="Looks good")
        
        response = await generate_answer("What is the mock title?")
        
        assert isinstance(response, ChatResponse)
        assert response.answer == "Mock answer"
        assert mock_rag_run.call_count == 1
        assert mock_reviewer_run.call_count == 1

@pytest.mark.asyncio
async def test_generate_answer_loop():
    with patch("services.rag_agent.vector_store.query_articles") as mock_query, \
         patch("services.rag_agent.expand_query") as mock_expand, \
         patch("services.rag_agent.rag_agent.run", new_callable=AsyncMock) as mock_rag_run, \
         patch("services.rag_agent.reviewer_agent.run", new_callable=AsyncMock) as mock_reviewer_run:
         
        mock_expand.return_value = QueryExpansionSchema(
            original_query="query", mesh_terms=["mesh"], expanded_search_queries=["query OR mesh"]
        )
        mock_query.return_value = []
        
        mock_rag_run.return_value.output = ChatResponse(answer="Mock answer", sources=[])
        
        class MockFailedReview:
            output = ReviewSchema(is_grounded=False, feedback="Bad")
        class MockPassedReview:
            output = ReviewSchema(is_grounded=True, feedback="Good")
            
        mock_reviewer_run.side_effect = [MockFailedReview(), MockPassedReview()]
        
        response = await generate_answer("What is the mock title?")
        
        assert isinstance(response, ChatResponse)
        assert mock_rag_run.call_count == 2
        assert mock_reviewer_run.call_count == 2
