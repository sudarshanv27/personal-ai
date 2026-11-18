from collections.abc import Generator

from openai import OpenAI

from app.ai.providers.base import AIProvider
from app.core.config import settings


class OllamaProvider(AIProvider):
    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

    def generate(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:

        response = self.client.chat.completions.create(
            model=model or settings.ai_model,
            messages=messages,
            stream=False,
        )

        if not response.choices:
            raise RuntimeError(
                "Ollama returned no choices in the response."
            )

        message = response.choices[0].message
        content = message.content

        if content is None:
            content = ""

        if not isinstance(content, str):
            content = str(content)

        content = content.strip()

        if not content:
            raise RuntimeError(
                "Ollama returned an empty AI response."
            )

        return content

    def generate_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> Generator[str, None, None]:

        response = self.client.chat.completions.create(
            model=model or settings.ai_model,
            messages=messages,
            stream=True,
        )

        for chunk in response:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta.content:
                yield delta.content