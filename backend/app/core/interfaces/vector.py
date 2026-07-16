from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseVectorStore(ABC):
    """
    Abstract interface for Vector Databases.
    """
    @abstractmethod
    def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]] | None = None, 
        ids: List[str] | None = None,
        collection_name: str | None = None
    ) -> List[str]:
        """
        Insert documents and their corresponding vector embeddings into the database.
        Returns a list of document IDs.
        """
        pass

    @abstractmethod
    def similarity_search(
        self, 
        query_embedding: List[float], 
        k: int = 5, 
        filter: Dict[str, Any] | None = None,
        collection_name: str | None = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a vector similarity search using a query vector.
        Returns a list of matching documents with metadata and similarity scores.
        """
        pass

    @abstractmethod
    def delete_documents(self, ids: List[str], collection_name: str | None = None) -> None:
        """
        Delete documents by their IDs from the database.
        """
        pass

    @abstractmethod
    def count(self, collection_name: str | None = None) -> int:
        """
        Get the total count of documents in the vector store/collection.
        """
        pass
