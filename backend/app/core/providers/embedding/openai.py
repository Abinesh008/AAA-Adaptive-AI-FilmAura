from typing import List
from openai import OpenAI
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.providers.embedding.openai")

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI embedding provider using the openai library.
    """
    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def version(self) -> str:
        return "v1"

    @property
    def provider_name(self) -> str:
        return "openai"

    def embed_query(self, text: str) -> List[float]:
        try:
            logger.debug(f"Calling OpenAI embedding for query: '{text[:25]}...'")
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI query embedding failed: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            logger.debug(f"Calling OpenAI embedding for {len(texts)} documents")
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI documents embedding failed: {e}")
            raise
