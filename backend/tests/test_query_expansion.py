import pytest
from pydantic_ai.models.test import TestModel
from models.schemas import QueryExpansionSchema
from services.query_expansion import expand_query, query_expansion_agent

@pytest.mark.asyncio
async def test_expand_query():
    # Use TestModel to mock the LLM response. 
    # Pydantic AI's TestModel automatically returns data matching the output_type schema.
    with query_expansion_agent.override(model=TestModel()):
        result = await expand_query("heart attack")
        assert isinstance(result, QueryExpansionSchema)
        assert hasattr(result, "original_query")
        assert hasattr(result, "mesh_terms")
        assert hasattr(result, "expanded_search_queries")
