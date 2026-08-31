import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from services.pubmed_fetcher import fetch_abstracts
from services.vector_store import vector_store

async def main():
    try:
        print("Fetching abstracts...")
        articles = await fetch_abstracts("asthma", 5)
        print(f"Fetched {len(articles)} articles.")
        
        print("Adding to vector store...")
        vector_store.add_articles(articles)
        print("Done!")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
