from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingProvider(ABC):
    """
    Abstract interface for Text Embedding providers.
    """
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single query text.
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for a list of document texts.
        """
        pass
