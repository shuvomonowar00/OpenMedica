"""
OpenMedica - Backend Core API
This module initializes the FastAPI application and includes routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.api import router as api_router

# Initialize FastAPI application
app = FastAPI(
    title="OpenMedica Backend API",
    description="Core REST API engine for the OpenMedica Medical RAG pipeline.",
    version="0.1.0"
)

# Enable CORS for Streamlit frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to restrict to Streamlit's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
# All endpoints in routers/api.py will automatically get the "/api" prefix
app.include_router(api_router, prefix="/api")

# --- System Endpoints ---

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok"}
