import pytest
import responses
from core.api_client import ingest_data, send_chat, get_database_status, API_BASE_URL

@responses.activate
def test_ingest_data_success():
    """Test successful data ingestion."""
    responses.add(
        responses.POST,
        f"{API_BASE_URL}/ingest",
        json={"message": "Success", "articles_ingested": 5},
        status=200
    )
    
    result = ingest_data("Asthma", 5)
    assert "error" not in result
    assert result["articles_ingested"] == 5

@responses.activate
def test_ingest_data_error():
    """Test data ingestion handling HTTP errors."""
    responses.add(
        responses.POST,
        f"{API_BASE_URL}/ingest",
        json={"detail": "Internal Server Error"},
        status=500
    )
    
    result = ingest_data("Asthma", 5)
    assert "error" in result
    assert "500" in result["error"]

@responses.activate
def test_send_chat_success():
    """Test successful chat response."""
    responses.add(
        responses.POST,
        f"{API_BASE_URL}/chat",
        json={"answer": "Asthma is...", "citations": [{"pmid": "123", "title": "A"}]},
        status=200
    )
    
    result = send_chat("What is Asthma?")
    assert "error" not in result
    assert result["answer"] == "Asthma is..."
    assert len(result["citations"]) == 1

@responses.activate
def test_send_chat_network_failure():
    """Test chat handling a network connection failure."""
    # Since we didn't mock the endpoint, this will simulate a connection error
    # but responses library explicitly raises ConnectionError if not registered
    import requests
    responses.add(
        responses.POST,
        f"{API_BASE_URL}/chat",
        body=requests.exceptions.ConnectionError("Connection refused")
    )
    
    result = send_chat("What is Asthma?")
    assert "error" in result
    assert "Connection refused" in result["error"]

@responses.activate
def test_delete_article_success():
    """Test successful deletion of an article."""
    responses.add(
        responses.DELETE,
        f"{API_BASE_URL}/database/12345",
        json={"message": "Successfully deleted article 12345"},
        status=200
    )
    
    from core.api_client import delete_article
    result = delete_article("12345")
    assert "error" not in result
    assert "message" in result
