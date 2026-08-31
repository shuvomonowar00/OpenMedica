import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
texts = ["hello", "world", "this is a test"]

try:
    response = client.models.embed_content(
        model=os.getenv("GEMINI_EMBEDDING_MODEL"),
        contents=texts,
    )
    print(f"Got {len(response.embeddings)} embeddings!")
except Exception as e:
    print(f"Error: {e}")
