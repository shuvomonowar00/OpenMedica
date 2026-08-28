"""
OpenMedica - LLM Factory
Model Agnostic Factory to instantiate and configure Pydantic AI models.
Zero-hardcoding: everything is driven strictly by .env configurations.
"""

import os
import logging
from pydantic_ai.models import Model
from pydantic_ai.models.google import GoogleModel

# Configure logging
logger = logging.getLogger(__name__)

def get_llm() -> Model:
    """
    Factory function to instantiate and return the configured Pydantic AI model.
    Strictly reads from .env without fallbacks.
    """
    provider = os.getenv("ACTIVE_LLM_PROVIDER")
    if not provider:
        raise ValueError("ACTIVE_LLM_PROVIDER is not set in your .env file.")
        
    provider = provider.lower().strip()
    logger.info(f"Initializing LLM Factory with active provider: '{provider}'")
    
    if provider == "gemini":
        model_name = os.getenv("GEMINI_LLM_MODEL")
        api_key = os.getenv("GEMINI_API_KEY")
        if not model_name or not api_key:
            raise ValueError("Missing GEMINI_LLM_MODEL or GEMINI_API_KEY in .env configuration.")
        return GoogleModel(model_name=model_name)
        
    elif provider == "openai":
        from pydantic_ai.models.openai import OpenAIModel
        model_name = os.getenv("OPENAI_LLM_MODEL")
        api_key = os.getenv("OPENAI_API_KEY")
        if not model_name or not api_key:
            raise ValueError("Missing OPENAI_LLM_MODEL or OPENAI_API_KEY in .env configuration.")
        return OpenAIModel(model_name=model_name, api_key=api_key)
        
    elif provider == "anthropic":
        from pydantic_ai.models.anthropic import AnthropicModel
        model_name = os.getenv("ANTHROPIC_LLM_MODEL")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not model_name or not api_key:
            raise ValueError("Missing ANTHROPIC_LLM_MODEL or ANTHROPIC_API_KEY in .env configuration.")
        return AnthropicModel(model_name=model_name, api_key=api_key)
        
    else:
        raise ValueError(f"Unsupported ACTIVE_LLM_PROVIDER: '{provider}'. Please check your .env configuration.")
