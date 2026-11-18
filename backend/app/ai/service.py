from collections.abc import Generator

from app.ai.factory import get_ai_provider


class AIService:
    """
    High-level interface for AI generation.

    The rest of the application should communicate with
    AI providers through this service rather than accessing
    providers directly.
    """

    def __init__(self):
        self.provider = get_ai_provider()

    def generate_response(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        """
        Generate a complete AI response.
        """

        return self.provider.generate(
            messages=messages,
            model=model,
        )

    def generate_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> Generator[str, None, None]:
        """
        Generate an AI response progressively.
        """

        if not hasattr(self.provider, "generate_stream"):
            raise RuntimeError(
                "The selected AI provider does not support streaming."
            )

        yield from self.provider.generate_stream(
            messages=messages,
            model=model,
        )