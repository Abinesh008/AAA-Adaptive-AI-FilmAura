import time
from typing import Dict, Tuple
from app.core.interfaces.cache import BaseCacheManager
from app.core.logging import get_logger

logger = get_logger("app.providers.cache.memory")

class InMemoryCacheManager(BaseCacheManager):
    """
    Local in-memory Cache provider implementing BaseCacheManager.
    """
    def __init__(self):
        # Maps key -> (value, expire_timestamp)
        self._store: Dict[str, Tuple[str, float | None]] = {}

    def get(self, key: str) -> str | None:
        if key not in self._store:
            return None
            
        value, expire_at = self._store[key]
        
        # Check for expiration
        if expire_at is not None and time.time() > expire_at:
            logger.debug(f"Cache key '{key}' expired, evicting")
            self.delete(key)
            return None
            
        logger.debug(f"Cache hit for key '{key}'")
        return value

    def set(self, key: str, value: str, expire: int | None = None) -> None:
        expire_at = time.time() + expire if expire is not None else None
        self._store[key] = (value, expire_at)
        logger.debug(f"Cached key '{key}' with TTL={expire}s")

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]
            logger.debug(f"Deleted cache key '{key}'")

    def clear(self) -> None:
        self._store.clear()
        logger.info("Cleared all items in memory cache")
