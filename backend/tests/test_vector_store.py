import pytest
from unittest.mock import patch
from models.schemas import PubMedArticle
from services.vector_store import VectorStore

from chromadb.api.types import Documents, Embeddings, EmbeddingFunction

class DummyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return [[0.0] * 768 for _ in input]
        
    def name(self) -> str:
        return "dummy_embedder"

@pytest.fixture
def mock_vector_store(tmp_path):
    # Use a temporary directory for ChromaDB to isolate tests
    store = VectorStore(db_path=str(tmp_path), collection_name="test_collection")
    
    # Mock the embedding function to return deterministic dummy embeddings
    # to avoid needing a real Gemini API key during testing.
    store.embedding_fn = DummyEmbeddingFunction()
    # Re-initialize collection with the mocked embedding function
    store.collection = store.client.get_or_create_collection(
        name="test_collection",
        embedding_function=store.embedding_fn
    )
    return store

def test_add_and_query_articles(mock_vector_store):
    mock_articles = [
        PubMedArticle(
            pmid="12345",
            title="Test Medical Article",
            abstract="This is a mock abstract for testing.",
            authors=["Doctor A", "Doctor B"]
        )
    ]
    
    # Test adding articles
    mock_vector_store.add_articles(mock_articles)
    
    # Test querying articles
    results = mock_vector_store.query_articles("mock abstract", n_results=1)
    
    assert len(results) == 1
    assert results[0].pmid == "12345"
    assert results[0].title == "Test Medical Article"
    assert "Doctor A" in results[0].authors
