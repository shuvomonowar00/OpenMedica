import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from models.schemas import ChatResponse

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ingest_endpoint():
    # Mock the external dependencies
    with patch("routers.api.fetch_abstracts") as mock_fetch, \
         patch("routers.api.vector_store.add_articles") as mock_add:
        
        mock_fetch.return_value = [] # Empty list of articles
        
        response = client.post("/api/ingest", json={"topic": "Cancer", "max_results": 2})
        
        assert response.status_code == 200
        assert "Successfully fetched" in response.json()["message"]
        assert response.json()["articles_ingested"] == 0
        mock_fetch.assert_called_once_with(topic="Cancer", max_results=2)

def test_chat_endpoint():
    # Mock the RAG agent response
    with patch("routers.api.generate_answer") as mock_generate:
        # Pydantic schema expects this structure
        mock_generate.return_value = ChatResponse(
            answer="This is a mock answer based on PMIDs.",
            sources=["12345"]
        )
        
        response = client.post("/api/chat", json={"query": "Test query"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "This is a mock answer based on PMIDs."
        assert "12345" in data["sources"]
        mock_generate.assert_called_once_with("Test query")
