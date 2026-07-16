import hashlib
import json
from typing import Optional, Any
from app.api.deps import get_cache_manager
from app.retrieval.features import features
from app.core.logging import get_logger

logger = get_logger("app.retrieval.cache")

class RetrievalCacheManager:
    """
    Incremental cache manager dividing query execution into independent, cached segments.
    """
    def __init__(self):
        # Local lookup mapping movie IDs to cache keys to support target invalidation
        self._movie_to_keys: Dict[int, Set[str]] = {}
        self._lock = threading.Lock()

    def get_hash(self, text: str, salt: str = "") -> str:
        raw = f"{text}:{salt}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def get_cached_item(self, prefix: str, key_hash: str) -> Optional[Any]:
        if not features.is_enabled("cache"):
            return None
            
        cache = get_cache_manager()
        full_key = f"retrieval:{prefix}:{key_hash}"
        try:
            cached_val = cache.get(full_key)
            if cached_val:
                logger.info(f"Cache HIT for key: {full_key}")
                return json.loads(cached_val)
        except Exception as e:
            logger.error(f"Error reading cache key {full_key}: {str(e)}")
        return None

    async def set_cached_item(self, prefix: str, key_hash: str, value: Any, ttl: int = 3600, linked_movie_ids: List[int] = None) -> None:
        if not features.is_enabled("cache"):
            return
            
        cache = get_cache_manager()
        full_key = f"retrieval:{prefix}:{key_hash}"
        try:
            cache.set(full_key, json.dumps(value), expire=ttl)
            logger.info(f"Cached item under key: {full_key}")
            
            # Map cached keys to movie IDs to support invalidations
            if linked_movie_ids:
                with self._lock:
                    for m_id in linked_movie_ids:
                        if m_id not in self._movie_to_keys:
                            self._movie_to_keys[m_id] = set()
                        self._movie_to_keys[m_id].add(full_key)
        except Exception as e:
            logger.error(f"Error writing cache key {full_key}: {str(e)}")

    async def invalidate_movie(self, movie_id: int) -> None:
        """
        Invalidate only cached queries that reference the updated/deleted movie ID.
        """
        cache = get_cache_manager()
        keys_to_delete = []
        with self._lock:
            if movie_id in self._movie_to_keys:
                keys_to_delete = list(self._movie_to_keys[movie_id])
                del self._movie_to_keys[movie_id]
                
        if keys_to_delete:
            logger.info(f"Invalidating {len(keys_to_delete)} cache keys linked to Movie ID {movie_id}")
            for key in keys_to_delete:
                try:
                    cache.delete(key)
                except Exception as e:
                    logger.error(f"Failed to delete cache key {key}: {str(e)}")

import threading
from typing import Dict, Set, List
# Export singleton cache manager
retrieval_cache = RetrievalCacheManager()
