from app.core.interfaces.cache import BaseCacheManager
from app.core.providers.cache.memory import InMemoryCacheManager
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.providers.cache.redis")

class RedisCacheManager(BaseCacheManager):
    """
    Redis Cache provider implementing BaseCacheManager.
    Falls back to InMemoryCacheManager if redis library is missing or server is offline.
    """
    def __init__(self):
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.password = settings.REDIS_PASSWORD
        self._fallback = None
        self._client = None
        
        try:
            import redis
            logger.info(f"Initializing Redis client at {self.host}:{self.port}")
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=2
            )
            self._client.ping()
            logger.info("Successfully connected to Redis cache server")
        except ImportError:
            logger.warning("The 'redis' package is not installed. Falling back to In-Memory cache.")
            self._fallback = InMemoryCacheManager()
        except Exception as e:
            logger.warning(f"Could not connect to Redis server ({e}). Falling back to In-Memory cache.")
            self._fallback = InMemoryCacheManager()

    def get(self, key: str) -> str | None:
        if self._fallback:
            return self._fallback.get(key)
        try:
            value = self._client.get(key)
            return value
        except Exception as e:
            logger.error(f"Redis get operation failed: {e}. Falling back to memory.")
            if not self._fallback:
                self._fallback = InMemoryCacheManager()
            return self._fallback.get(key)

    def set(self, key: str, value: str, expire: int | None = None) -> None:
        if self._fallback:
            self._fallback.set(key, value, expire)
            return
        try:
            self._client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis set operation failed: {e}. Falling back to memory.")
            if not self._fallback:
                self._fallback = InMemoryCacheManager()
            self._fallback.set(key, value, expire)

    def delete(self, key: str) -> None:
        if self._fallback:
            self._fallback.delete(key)
            return
        try:
            self._client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete operation failed: {e}")

    def clear(self) -> None:
        if self._fallback:
            self._fallback.clear()
            return
        try:
            self._client.flushdb()
            logger.info("Flushed all databases in Redis")
        except Exception as e:
            logger.error(f"Redis flushdb operation failed: {e}")
