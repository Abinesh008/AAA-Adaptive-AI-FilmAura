import asyncio
from app.core.config import settings

class RetrievalResourceManager:
    """
    Central manager bounding connection execution concurrency and connection pool resources.
    """
    def __init__(self):
        # Allow at most 20 concurrent retrieval operations
        self._execution_semaphore = asyncio.Semaphore(20)
        
        # Max concurrency semaphores per specific database backend
        self._db_semaphores = {
            "postgres": asyncio.Semaphore(10),
            "neo4j": asyncio.Semaphore(5),
            "chromadb": asyncio.Semaphore(5)
        }

    def get_execution_semaphore(self) -> asyncio.Semaphore:
        return self._execution_semaphore

    def get_db_semaphore(self, db_name: str) -> asyncio.Semaphore:
        return self._db_semaphores.get(db_name.lower(), self._execution_semaphore)

    @property
    def timeout_seconds(self) -> float:
        return settings.PARALLEL_TIMEOUT_MS / 1000.0

# Singleton resource manager instance
resources = RetrievalResourceManager()
