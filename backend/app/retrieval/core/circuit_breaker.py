import time
import threading
from enum import Enum
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.retrieval.circuit_breaker")

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Thread-safe circuit breaker preventing cascading dependency failures.
    """
    def __init__(self, name: str):
        self.name = name
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0.0
        self._lock = threading.Lock()

    def is_allowed(self) -> bool:
        """
        Check if requests are allowed to pass to this dependency.
        """
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
                
            if self.state == CircuitState.OPEN:
                now = time.time()
                cooldown = settings.CIRCUIT_BREAKER_COOLDOWN
                if now - self.last_failure_time > cooldown:
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN (cooldown expired).")
                    return True
                return False
                
            if self.state == CircuitState.HALF_OPEN:
                return True
                
            return False

    def record_success(self) -> None:
        with self._lock:
            self.failures = 0
            if self.state != CircuitState.CLOSED:
                self.state = CircuitState.CLOSED
                logger.info(f"Circuit breaker '{self.name}' reset to CLOSED after a successful call.")

    def record_failure(self) -> None:
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            max_failures = settings.CIRCUIT_BREAKER_FAILURES
            
            if self.failures >= max_failures and self.state != CircuitState.OPEN:
                self.state = CircuitState.OPEN
                logger.critical(f"Circuit breaker '{self.name}' tripped to OPEN (consecutive failures: {self.failures}).")

# Core circuit breakers singleton registry
circuit_breakers = {
    "postgres": CircuitBreaker("postgres"),
    "neo4j": CircuitBreaker("neo4j"),
    "chromadb": CircuitBreaker("chromadb"),
    "llm": CircuitBreaker("llm"),
    "embedding": CircuitBreaker("embedding")
}
