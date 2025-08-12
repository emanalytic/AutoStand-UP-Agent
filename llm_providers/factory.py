from .groq_provider import GroqProvider
from .openai_provider import OpenAIProvider
from .base_provider import BaseLLMProvider
import os


def create_llm_provider(provider_type: str, model: str) -> BaseLLMProvider:
    """
    Factory function to create the appropriate LLM provider.
    
    Args:
        provider_type: Either 'groq' or 'openai'
        model: The model name to use
        
    Returns:
        An instance of the appropriate LLM provider
        
    Raises:
        ValueError: If the provider type is not supported
        ValueError: If the required API key is not found
    """
    provider_type = provider_type.lower()
    
    if provider_type == 'groq':
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return GroqProvider(api_key, model)
    
    elif provider_type == 'openai':
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return OpenAIProvider(api_key, model)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_type}. Supported providers: 'groq', 'openai'")