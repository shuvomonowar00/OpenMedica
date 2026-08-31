import os
import logging
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from google import genai
from typing import List
from rank_bm25 import BM25Okapi

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
        
        # Initialize in-memory BM25 index
        self.bm25_corpus = []
        self.bm25_metadatas = []
        self.bm25_ids = []
        self.bm25 = None
        self._initialize_bm25()

    def _initialize_bm25(self):
        """Reads all documents from ChromaDB and initializes the BM25 index."""
        try:
            data = self.collection.get()
            docs = data.get("documents", [])
            metas = data.get("metadatas", [])
            ids = data.get("ids", [])
            
            if docs:
                self.bm25_corpus = docs
                self.bm25_metadatas = metas
                self.bm25_ids = ids
                
                # Tokenize for BM25 (simple whitespace tokenization)
                tokenized_corpus = [doc.lower().split() for doc in self.bm25_corpus]
                self.bm25 = BM25Okapi(tokenized_corpus)
                logger.info(f"Initialized BM25 index with {len(docs)} documents.")
            else:
                self.bm25_corpus = []
                self.bm25_metadatas = []
                self.bm25_ids = []
                self.bm25 = None
        except Exception as e:
            logger.warning(f"Failed to initialize BM25: {e}")

    def add_articles(self, articles: List[PubMedArticle]) -> None:
        """Add PubMed articles to the vector store (chunked by section)."""
        if not articles:
            return

        documents = []
        metadatas = []
        ids = []

        for article in articles:
            # If no sections, fallback to abstract
            sections_to_use = article.sections if article.sections else []
            
            for idx, section in enumerate(sections_to_use):
                text = f"Title: {article.title}\nSection: {section.section_title}\n\n{section.content}"
                documents.append(text)
                
                metadata = {
                    "pmid": article.pmid,
                    "pmcid": article.pmcid if article.pmcid else "",
                    "title": article.title,
                    "authors": ", ".join(article.authors),
                    "section_title": section.section_title,
                    "publication_types": ", ".join(article.publication_types)
                }
                metadatas.append(metadata)
                
                # Create a unique ID for each chunk
                ids.append(f"{article.pmid}_sec_{idx}")

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} chunks from {len(articles)} articles to ChromaDB.")
            
            # Update BM25 incrementally (re-initialize to keep it simple and robust)
            self._initialize_bm25()

    def query_articles(self, query: str, n_results: int = 5) -> List[PubMedArticle]:
        """Hybrid Query: Fuses ChromaDB semantic search with BM25 keyword search using RRF."""
        if self.collection.count() == 0:
            return []
            
        # Fetch more candidates for RRF ranking
        actual_n = min(n_results * 2, self.collection.count())
            
        # 1. ChromaDB Vector Search
        chroma_results = self.collection.query(
            query_texts=[query],
            n_results=actual_n
        )
        chroma_ids = chroma_results.get("ids", [[]])[0]
        
        # 2. BM25 Keyword Search
        bm25_ids_ranked = []
        if self.bm25:
            tokenized_query = query.lower().split()
            doc_scores = self.bm25.get_scores(tokenized_query)
            
            # Get top actual_n indices based on BM25 scores
            # Use sorted to rank indices by score descending
            top_n_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:actual_n]
            bm25_ids_ranked = [self.bm25_ids[i] for i in top_n_indices if doc_scores[i] > 0]
            
        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        k = 60 # RRF constant
        
        for rank, cid in enumerate(chroma_ids):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
            
        for rank, cid in enumerate(bm25_ids_ranked):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
            
        # Sort by RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        top_cids = sorted_cids[:n_results]
        
        # 4. Construct final PubMedArticle objects
        articles = []
        for cid in top_cids:
            try:
                idx = self.bm25_ids.index(cid)
                metadata = self.bm25_metadatas[idx]
                doc_text = self.bm25_corpus[idx]
                
                section_title = metadata.get("section_title", "Unknown Section")
                chunk_content = f"[{section_title}] {doc_text}"
                
                articles.append(PubMedArticle(
                    pmid=str(metadata["pmid"]),
                    pmcid=str(metadata.get("pmcid", "")),
                    title=str(metadata["title"]),
                    abstract=chunk_content,
                    authors=str(metadata["authors"]).split(", ") if metadata.get("authors") else [],
                    publication_types=str(metadata.get("publication_types", "")).split(", ") if metadata.get("publication_types") else []
                ))
            except ValueError:
                # Fallback if somehow CID is not in our BM25 tracker
                continue
                
        return articles

    def delete_article(self, pmid: str) -> None:
        """Deletes an article from the vector store by its PMID and updates BM25."""
        # Note: Delete requires knowing exactly which ids to delete.
        # The chunks are named pmid_sec_0, pmid_sec_1, etc.
        # We need to find all ids that start with pmid
        ids_to_delete = [cid for cid in self.bm25_ids if cid.startswith(f"{pmid}_sec_")]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted article with PMID {pmid} from ChromaDB.")
            self._initialize_bm25()
        else:
            logger.info(f"No chunks found for PMID {pmid} to delete.")

# Singleton instance to be used across the app
DB_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma_data")
vector_store = VectorStore(db_path=DB_DIR)
