"""
OpenMedica - LLM Factory
Model Agnostic Factory to instantiate and configure Pydantic AI models.
Follows strict clean coding rules and ensures the application remains decoupled from specific AI providers.
"""

import os
import logging
from pydantic_ai.models import Model
from pydantic_ai.models.gemini import GeminiModel

# Configure logging
logger = logging.getLogger(__name__)

def get_llm() -> Model:
    """
    Factory function to instantiate and return the configured Pydantic AI model.
    Reads the 'LLM_PROVIDER' and 'LLM_MODEL_NAME' environment variables.
    
    Returns:
        Model: A fully configured Pydantic AI Model instance.
        
    Raises:
        ValueError: If the required API keys are missing or if the provider is unsupported.
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower().strip()
    model_name = os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash").strip()
    
    logger.info(f"Initializing LLM Factory with provider: '{provider}', model: '{model_name}'")
    
    if provider == "gemini":
        # Pydantic AI uses GEMINI_API_KEY natively. We check for it to provide a clean error.
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Missing API Key for Gemini. Please set 'GEMINI_API_KEY' in your environment variables."
            )
            
        # Return the instantiated Pydantic AI Gemini model
        return GeminiModel(model_name=model_name, api_key=api_key)
        
    # Future-proofing for other providers like OpenAI, Anthropic, etc.
    elif provider == "openai":
        raise NotImplementedError("OpenAI provider is not yet implemented. Please use 'gemini'.")
        
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: '{provider}'. Please check your .env configuration.")
