import random
from typing import List
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.core.logging import get_logger

logger = get_logger("app.providers.embedding.mock")

class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Mock embedding provider returning pseudo-random vectors.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    @property
    def model_name(self) -> str:
        return f"mock-{self.dimension}"

    @property
    def version(self) -> str:
        return "v1"

    @property
    def provider_name(self) -> str:
        return "mock"

    def embed_query(self, text: str) -> List[float]:
        logger.info(f"Mock embed_query called for text of length: {len(text)}")
        # Return deterministic mock vector based on text length and random seed
        random.seed(len(text))
        return [random.uniform(-1, 1) for _ in range(self.dimension)]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"Mock embed_documents called for {len(texts)} documents")
        return [self.embed_query(text) for text in texts]
