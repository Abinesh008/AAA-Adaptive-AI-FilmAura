from typing import Generator
from sqlalchemy.orm import Session
from app.database.session import get_db

# Interface imports
from app.core.interfaces.llm import BaseLLMProvider
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.core.interfaces.vector import BaseVectorStore
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.cache import BaseCacheManager

# Provider imports
from app.core.providers.llm.openai import OpenAILLMProvider
from app.core.providers.llm.gemini import GeminiLLMProvider
from app.core.providers.llm.mock import MockLLMProvider

from app.core.providers.embedding.local import LocalEmbeddingProvider
from app.core.providers.embedding.openai import OpenAIEmbeddingProvider
from app.core.providers.embedding.mock import MockEmbeddingProvider

from app.core.providers.vector.chroma import ChromaVectorStore
from app.core.providers.graph.neo4j import Neo4jKnowledgeGraph

from app.core.providers.cache.memory import InMemoryCacheManager
from app.core.providers.cache.redis import RedisCacheManager

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.api.deps")

# Singleton initializations for reusable connection pools
_llm_provider: BaseLLMProvider | None = None
_embedding_provider: BaseEmbeddingProvider | None = None
_vector_store: BaseVectorStore | None = None
_knowledge_graph: BaseKnowledgeGraph | None = None
_cache_manager: BaseCacheManager | None = None

def get_llm_provider() -> BaseLLMProvider:
    """
    Get the configured LLM Provider singleton.
    """
    global _llm_provider
    if _llm_provider is None:
        provider_name = settings.LLM_PROVIDER.lower().strip()
        logger.info(f"Initializing LLM Provider: {provider_name}")
        if provider_name == "openai":
            _llm_provider = OpenAILLMProvider()
        elif provider_name == "gemini":
            _llm_provider = GeminiLLMProvider()
        elif provider_name == "mock":
            _llm_provider = MockLLMProvider()
        else:
            logger.warning(f"Unknown LLM provider '{provider_name}'. Falling back to MockLLMProvider.")
            _llm_provider = MockLLMProvider()
    return _llm_provider

def get_embedding_provider() -> BaseEmbeddingProvider:
    """
    Get the configured Embedding Provider singleton.
    """
    global _embedding_provider
    if _embedding_provider is None:
        provider_name = settings.EMBEDDING_PROVIDER.lower().strip()
        logger.info(f"Initializing Embedding Provider: {provider_name}")
        if provider_name == "local":
            _embedding_provider = LocalEmbeddingProvider()
        elif provider_name == "openai":
            _embedding_provider = OpenAIEmbeddingProvider()
        elif provider_name == "mock":
            _embedding_provider = MockEmbeddingProvider()
        else:
            logger.warning(f"Unknown embedding provider '{provider_name}'. Falling back to MockEmbeddingProvider.")
            _embedding_provider = MockEmbeddingProvider()
    return _embedding_provider

def get_vector_store() -> BaseVectorStore:
    """
    Get the Vector Store database client.
    """
    global _vector_store
    if _vector_store is None:
        logger.info("Initializing Vector Store")
        _vector_store = ChromaVectorStore()
    return _vector_store

def get_knowledge_graph() -> BaseKnowledgeGraph:
    """
    Get the Graph database client.
    """
    global _knowledge_graph
    if _knowledge_graph is None:
        logger.info("Initializing Graph Database")
        _knowledge_graph = Neo4jKnowledgeGraph()
    return _knowledge_graph

def get_cache_manager() -> BaseCacheManager:
    """
    Get the configured Cache Manager singleton.
    """
    global _cache_manager
    if _cache_manager is None:
        provider_name = settings.CACHE_PROVIDER.lower().strip()
        logger.info(f"Initializing Cache Manager: {provider_name}")
        if provider_name == "redis":
            _cache_manager = RedisCacheManager()
        elif provider_name == "memory":
            _cache_manager = InMemoryCacheManager()
        else:
            logger.warning(f"Unknown cache provider '{provider_name}'. Falling back to InMemoryCacheManager.")
            _cache_manager = InMemoryCacheManager()
    return _cache_manager
