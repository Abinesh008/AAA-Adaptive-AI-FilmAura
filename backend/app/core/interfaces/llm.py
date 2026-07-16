from abc import ABC, abstractmethod
from typing import AsyncGenerator, Generator

class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM (Large Language Model) providers.
    """
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Synchronously generate text for a given prompt.
        """
        pass

    @abstractmethod
    async def generate_async(self, prompt: str, **kwargs) -> str:
        """
        Asynchronously generate text for a given prompt.
        """
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Asynchronously stream tokens for a given prompt.
        """
        # Yield string tokens
        yield ""
