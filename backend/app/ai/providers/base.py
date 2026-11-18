from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Base interface for all AI/LLM providers.
    """

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        """
        Generate a text response from the AI provider.
        """
        raise NotImplementedError