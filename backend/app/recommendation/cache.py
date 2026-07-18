from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.logging import get_logger

logger = get_logger("app.recommendation.cache")

class RecommendationCache:
    """
    User recommendation cache manager.
    Stores and evicts recommendation list payloads based on TTL and feedback events.
    """
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        # In-memory storage mapping user_id -> {"timestamp": datetime, "payload": List}
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def get_cached_recommendations(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves active recommendation lists if cache hit and not expired.
        """
        entry = self._cache.get(user_id)
        if not entry:
            return None

        # Verify TTL
        elapsed = datetime.utcnow() - entry["timestamp"]
        if elapsed > timedelta(seconds=self.ttl_seconds):
            logger.info(f"Cache expired for user: {user_id}. Evicting.")
            del self._cache[user_id]
            return None

        logger.info(f"Cache hit for user: {user_id}")
        return entry["payload"]

    async def cache_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]]) -> None:
        """
        Saves fresh recommendations payload.
        """
        logger.info(f"Caching recommendation response for user: {user_id}")
        self._cache[user_id] = {
            "timestamp": datetime.utcnow(),
            "payload": recommendations
        }

    async def invalidate_user_cache(self, user_id: str) -> None:
        """
        Evicts user's entry upon receiving active interaction feedback.
        """
        if user_id in self._cache:
            logger.info(f"Evicting active recommendation cache for user: {user_id}")
            del self._cache[user_id]

# Export cache manager singleton
recommendation_cache = RecommendationCache()
