from app.ai.providers.base import AIProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import settings


def get_ai_provider() -> AIProvider:
    provider = settings.ai_provider.lower()

    if provider == "ollama":
        return OllamaProvider()

    if provider == "openai":
        return OpenAIProvider()

    raise ValueError(
        f"Unsupported AI provider: {settings.ai_provider}"
    )


def get_ai_model() -> str:
    return settings.ai_model