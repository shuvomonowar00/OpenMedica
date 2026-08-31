import os
import requests
from typing import Dict, Any

# Allow override for Docker (e.g., http://backend:8000/api)
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000/api")

def ingest_data(topic: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Triggers the ingestion pipeline on the backend.
    """
    url = f"{API_BASE_URL}/ingest"
    payload = {"topic": topic, "max_results": max_results}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def send_chat(query: str, history: list = None, study_type: str = "All", date_filter: str = "All Time") -> Dict[str, Any]:
    """
    Sends a chat query to the backend RAG engine.
    """
    if history is None:
        history = []
        
    url = f"{API_BASE_URL}/chat"
    payload = {
        "query": query,
        "history": history,
        "study_type": study_type,
        "date_filter": date_filter
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_database_status() -> Dict[str, Any]:
    """
    Fetches the current status of the ChromaDB database.
    """
    url = f"{API_BASE_URL}/database"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def delete_article(pmid: str) -> Dict[str, Any]:
    """
    Deletes an article from the backend database by PMID.
    """
    url = f"{API_BASE_URL}/database/{pmid}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

import streamlit as st

@st.cache_data(ttl=10, show_spinner=False)
def get_cached_database_status() -> Dict[str, Any]:
    """
    Cached wrapper to prevent Streamlit from delaying on every UI refresh.
    """
    return get_database_status()
