from typing import Optional
from app.services.adapters.base import LLMAdapter
from app.services.adapters.openai_adapter import OpenAICompatibleAdapter
from app.services.adapters.anthropic_adapter import AnthropicAdapter
from app.services.adapters.gemini_adapter import GeminiAdapter
from app.services.adapters.ollama_adapter import OllamaAdapter
from app.models.schemas import ProviderType
from app.core.config import settings


def create_adapter(
    provider: ProviderType,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    timeout_seconds: float = 30.0,
) -> LLMAdapter:
    """Factory function to create the appropriate LLM adapter."""
    
    # Use settings as defaults
    api_key = api_key or settings.llm_api_key
    base_url = base_url or settings.llm_base_url
    model = model or settings.llm_model

    if provider == ProviderType.OPENAI_COMPATIBLE:
        if not base_url:
            base_url = "https://api.openai.com/v1"
        return OpenAICompatibleAdapter(api_key, base_url, model, timeout_seconds)

    elif provider == ProviderType.ANTHROPIC:
        if not base_url:
            base_url = "https://api.anthropic.com"
        return AnthropicAdapter(api_key, base_url, model, timeout_seconds)

    elif provider == ProviderType.GEMINI:
        if not base_url:
            base_url = "https://generativelanguage.googleapis.com"
        return GeminiAdapter(api_key, base_url, model, timeout_seconds)

    elif provider == ProviderType.OLLAMA:
        if not base_url:
            base_url = "http://localhost:11434"
        return OllamaAdapter(api_key, base_url, model, timeout_seconds)

    else:
        raise ValueError(f"Unsupported provider: {provider}")
