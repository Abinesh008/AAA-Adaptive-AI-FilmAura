from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.retrieval.contract import ExecutionStep, RetrievalResult
from app.retrieval.query_trace import QueryTrace

class BaseRetrievalPlugin(ABC):
    """
    Interface definition for all modular search backends.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        pass

    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        pass

    @abstractmethod
    async def search(self, step: ExecutionStep, trace: QueryTrace) -> List[RetrievalResult]:
        pass
