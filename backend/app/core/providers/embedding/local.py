from typing import List
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.providers.embedding.local")

class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """
    Local embedding provider using SentenceTransformers.
    """
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._model = None

    @property
    def model_name(self) -> str:
        return self.model_name

    @property
    def version(self) -> str:
        return "v1"

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model(self) -> "SentenceTransformer":
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local SentenceTransformer model: {self.model_name} (this may take a moment)")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Local SentenceTransformer model '{self.model_name}' loaded successfully")
        return self._model

    def embed_query(self, text: str) -> List[float]:
        try:
            logger.debug(f"Encoding query text: '{text[:25]}...'")
            embeddings = self.model.encode(text)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Local query embedding generation failed: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            logger.debug(f"Encoding {len(texts)} documents")
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Local documents embedding generation failed: {e}")
            raise
