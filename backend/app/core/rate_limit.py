import time
from fastapi import Request, HTTPException, status
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.rate_limit")

class InMemoryRateLimiter:
    """
    A sliding window rate limiter that tracks client requests in memory.
    """
    def __init__(self, requests_limit: int = 100, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        # client_ip -> list of timestamps
        self.history = {}

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        
        # Initialize IP history
        if client_ip not in self.history:
            self.history[client_ip] = []

        # Filter out requests older than the sliding window
        self.history[client_ip] = [
            timestamp for timestamp in self.history[client_ip]
            if now - timestamp < self.window_seconds
        ]

        # Check if limit is exceeded
        if len(self.history[client_ip]) >= self.requests_limit:
            return False

        # Register current request
        self.history[client_ip].append(now)
        return True

    async def __call__(self, request: Request):
        # We can disable rate limiting during local debugging/testing if specified
        if settings.APP_ENV == "testing":
            return

        client_ip = request.client.host if request.client else "unknown"
        
        if not self.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

# Create a global rate limiter instance from configuration
rate_limiter = InMemoryRateLimiter(
    requests_limit=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW
)
