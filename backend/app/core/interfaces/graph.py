from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseKnowledgeGraph(ABC):
    """
    Abstract interface for Graph Databases (such as Neo4j).
    """
    @abstractmethod
    def execute_query(self, query: str, parameters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """
        Execute a cypher query on the graph database and return results as a list of dicts.
        """
        pass

    @abstractmethod
    def run_transaction(self, cypher_queries: List[Tuple[str, Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        """
        Run multiple queries sequentially inside a single transactional block.
        """
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """
        Run a simple diagnostic query (e.g., 'RETURN 1') to verify database health.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the underlying driver connection cleanly.
        """
        pass
