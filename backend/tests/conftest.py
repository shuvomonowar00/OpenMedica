import os

# These environment variables are explicitly set at import time
# so that our strict zero-hardcoding files (like llm_factory.py and vector_store.py)
# do not crash with a ValueError when they are imported during a pytest run.

os.environ["ACTIVE_LLM_PROVIDER"] = "gemini"
os.environ["GEMINI_LLM_MODEL"] = "test-model"
os.environ["GEMINI_API_KEY"] = "test-key"

os.environ["ACTIVE_EMBEDDING_PROVIDER"] = "gemini"
os.environ["GEMINI_EMBEDDING_MODEL"] = "test-embed"
