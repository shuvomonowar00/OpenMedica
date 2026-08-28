import os
import logging
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from google import genai
from typing import List

from models.schemas import PubMedArticle

logger = logging.getLogger(__name__)

class GeminiEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using the google-genai SDK."""
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
            )
            embeddings.append(response.embeddings[0].values)
        return embeddings

class OpenAIEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using the openai SDK."""
    def __init__(self, model_name: str, api_key: str):
        import openai
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        # Replace newlines for better OpenAI embeddings as per their docs
        cleaned_input = [text.replace("\n", " ") for text in input]
        response = self.client.embeddings.create(
            input=cleaned_input,
            model=self.model_name
        )
        return [data.embedding for data in response.data]

def get_embedding_function() -> EmbeddingFunction:
    """Factory to retrieve the strictly configured embedding function."""
    provider = os.getenv("ACTIVE_EMBEDDING_PROVIDER")
    if not provider:
        raise ValueError("ACTIVE_EMBEDDING_PROVIDER is not set in your .env file.")
        
    provider = provider.lower().strip()
    
    if provider == "gemini":
        model_name = os.getenv("GEMINI_EMBEDDING_MODEL")
        api_key = os.getenv("GEMINI_API_KEY")
        if not model_name or not api_key:
            raise ValueError("Missing GEMINI_EMBEDDING_MODEL or GEMINI_API_KEY in .env configuration.")
        return GeminiEmbeddingFunction(model_name=model_name, api_key=api_key)
        
    elif provider == "openai":
        model_name = os.getenv("OPENAI_EMBEDDING_MODEL")
        api_key = os.getenv("OPENAI_API_KEY")
        if not model_name or not api_key:
            raise ValueError("Missing OPENAI_EMBEDDING_MODEL or OPENAI_API_KEY in .env configuration.")
        return OpenAIEmbeddingFunction(model_name=model_name, api_key=api_key)
        
    else:
        raise ValueError(f"Unsupported ACTIVE_EMBEDDING_PROVIDER: '{provider}'.")

class VectorStore:
    def __init__(self, db_path: str = ".chroma_data", collection_name: str = "pubmed_abstracts"):
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Strictly fetch based on active provider
        self.embedding_fn = get_embedding_function()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        logger.info(f"Initialized ChromaDB at {db_path} with collection {collection_name}")

    def add_articles(self, articles: List[PubMedArticle]) -> None:
        """Add PubMed articles to the vector store."""
        if not articles:
            return

        documents = []
        metadatas = []
        ids = []

        for article in articles:
            text = f"Title: {article.title}\n\nAbstract: {article.abstract}"
            documents.append(text)
            
            metadata = {
                "pmid": article.pmid,
                "title": article.title,
                "authors": ", ".join(article.authors)
            }
            metadatas.append(metadata)
            ids.append(article.pmid)

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(articles)} articles to ChromaDB.")

    def query_articles(self, query: str, n_results: int = 5) -> List[PubMedArticle]:
        """Query the vector store for relevant PubMed articles."""
        if self.collection.count() == 0:
            return []
            
        actual_n = min(n_results, self.collection.count())
            
        results = self.collection.query(
            query_texts=[query],
            n_results=actual_n
        )
        
        articles = []
        if not results["metadatas"] or not results["metadatas"][0]:
            return articles
            
        for idx, metadata in enumerate(results["metadatas"][0]):
            doc_text = results["documents"][0][idx] if results["documents"] else ""
            articles.append(PubMedArticle(
                pmid=str(metadata["pmid"]),
                title=str(metadata["title"]),
                abstract=doc_text,
                authors=str(metadata["authors"]).split(", ") if metadata.get("authors") else []
            ))
            
        return articles

# Singleton instance to be used across the app
DB_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma_data")
vector_store = VectorStore(db_path=DB_DIR)
