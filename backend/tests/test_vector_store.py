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
    from models.schemas import ArticleSection
    
    mock_articles = [
        PubMedArticle(
            pmid="12345",
            pmcid="PMC12345",
            title="Test Medical Article",
            abstract="Fallback abstract",
            authors=["Doctor A", "Doctor B"],
            publication_types=["Randomized Controlled Trial"],
            sections=[
                ArticleSection(section_title="Methods", content="This is the methodology."),
                ArticleSection(section_title="Results", content="These are the results.")
            ]
        )
    ]
    
    # Test adding articles
    mock_vector_store.add_articles(mock_articles)
    
    # Test querying articles
    results = mock_vector_store.query_articles("methodology", n_results=2)
    
    assert len(results) >= 1
    # Check that metadata was reconstructed correctly
    # The exact result order might vary due to dummy embeddings, so we check the first one
    returned_article = results[0]
    assert returned_article.pmid == "12345"
    assert returned_article.pmcid == "PMC12345"
    assert returned_article.title == "Test Medical Article"
    assert "Doctor A" in returned_article.authors
    assert "Randomized Controlled Trial" in returned_article.publication_types
    # Check that the chunk text is formatted properly in the abstract field
    assert "[Methods]" in returned_article.abstract or "[Results]" in returned_article.abstract
