import time
from typing import Generic, TypeVar, Any
from contextlib import contextmanager
from app.core.logging import get_logger
from app.core.config import settings

RepositoryType = TypeVar("RepositoryType")

class BaseService(Generic[RepositoryType]):
    """
    Base Service layer class encapsulating business rules, configuration,
    and wrapping repository / infrastructure interactions.
    """
    def __init__(self, repository: RepositoryType | None = None):
        self.repo = repository
        self.logger = get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.settings = settings

    @contextmanager
    def time_block(self, block_name: str):
        """Context manager to log the duration of execution blocks."""
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = (time.time() - start_time) * 1000
            self.logger.info(f"Block '{block_name}' completed in {elapsed:.2f}ms")

    def translate_error(self, operation: str, error: Exception) -> Exception:
        """Centralized error handling and transformation helper."""
        self.logger.error(f"Error during '{operation}': {str(error)}")
        return error
