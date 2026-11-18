from openai import OpenAI

from app.ai.providers.base import AIProvider
from app.core.config import settings


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of the AIProvider interface.
    """

    def __init__(self):
        if not settings.ai_api_key:
            raise ValueError("AI_API_KEY is not configured")

        self.client = OpenAI(
            api_key=settings.ai_api_key
        )

    def generate(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        response = self.client.chat.completions.create(
            model=model or settings.ai_model,
            messages=messages,
        )

        return response.choices[0].message.content or ""