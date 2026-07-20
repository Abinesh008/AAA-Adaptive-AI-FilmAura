import time
from fastapi import Request, HTTPException, status
from app.core.config import settings
from app.core.logging import get_logger
from app.api import deps
from app.core.providers.cache.redis import RedisCacheManager

logger = get_logger("app.rate_limit")

class HybridRateLimiter:
    """
    A sliding window rate limiter that utilizes Redis if available, 
    falling back to local memory if Redis is offline or not configured.
    """
    def __init__(self, requests_limit: int = 100, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        # Fallback local memory sliding window: client_ip -> list of timestamps
        self.local_history = {}

    def _is_allowed_redis(self, client_ip: str, cache: RedisCacheManager) -> bool:
        now = time.time()
        key = f"ratelimit:{client_ip}"
        client = cache._client

        try:
            # Multi/exec pipeline to keep operations atomic
            pipeline = client.pipeline()
            # Remove timestamps older than window
            pipeline.zremrangebyscore(key, 0, now - self.window_seconds)
            # Count remaining timestamps
            pipeline.zcard(key)
            # Append current timestamp
            pipeline.zadd(key, {str(now): now})
            # Set key expiration to ensure cleanup
            pipeline.expire(key, self.window_seconds)
            
            results = pipeline.execute()
            cardinality = results[1]

            if cardinality >= self.requests_limit:
                return False
            return True
        except Exception as e:
            logger.error(f"Redis rate limiting failed: {e}. Falling back to memory.")
            return False

    def _is_allowed_local(self, client_ip: str) -> bool:
        now = time.time()
        
        if client_ip not in self.local_history:
            self.local_history[client_ip] = []

        # Filter out old requests
        self.local_history[client_ip] = [
            t for t in self.local_history[client_ip]
            if now - t < self.window_seconds
        ]

        if len(self.local_history[client_ip]) >= self.requests_limit:
            return False

        self.local_history[client_ip].append(now)
        return True

    def is_allowed(self, client_ip: str) -> bool:
        try:
            cache_manager = deps.get_cache_manager()
            # If RedisCacheManager is configured and active (no fallback active)
            if isinstance(cache_manager, RedisCacheManager) and cache_manager._client and not cache_manager._fallback:
                return self._is_allowed_redis(client_ip, cache_manager)
        except Exception as e:
            logger.debug(f"Could not resolve Redis cache manager: {e}")

        # Fallback to local memory sliding window
        return self._is_allowed_local(client_ip)

    async def __call__(self, request: Request):
        if settings.APP_ENV == "testing":
            return

        client_ip = request.client.host if request.client else "unknown"
        
        if not self.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

# Create a global rate limiter instance from configuration settings
rate_limiter = HybridRateLimiter(
    requests_limit=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW
)
