import uuid
from typing import List, Dict, Any
import chromadb
from app.core.interfaces.vector import BaseVectorStore
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.providers.vector.chroma")

class ChromaVectorStore(BaseVectorStore):
    """
    ChromaDB provider implementing BaseVectorStore.
    """
    def __init__(self, collection_name: str = "filmaura_movies"):
        self.collection_name = collection_name
        
        # Determine if we should connect to a remote server or run locally
        if settings.CHROMA_HOST:
            logger.info(f"Connecting to remote ChromaDB server at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT
            )
        else:
            logger.info(f"Initializing local persistent ChromaDB client at {settings.CHROMA_PERSIST_DIR}")
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )
            
        # Get or create the default collection
        # We specify embedding_function=None as we manage embeddings outside Chroma for maximum control
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def _get_collection(self, collection_name: str | None = None):
        name = collection_name or self.collection_name
        return self.client.get_or_create_collection(name=name)

    def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]] | None = None, 
        ids: List[str] | None = None,
        collection_name: str | None = None
    ) -> List[str]:
        try:
            # Generate IDs if not provided
            if not ids:
                ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
            # Ensure metadatas is populated
            if not metadatas:
                metadatas = [{} for _ in range(len(texts))]

            target_name = collection_name or self.collection_name
            logger.info(f"Adding {len(texts)} documents to ChromaDB collection: {target_name}")
            
            collection = self._get_collection(collection_name)
            collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            raise

    def similarity_search(
        self, 
        query_embedding: List[float], 
        k: int = 5, 
        filter: Dict[str, Any] | None = None,
        collection_name: str | None = None
    ) -> List[Dict[str, Any]]:
        try:
            target_name = collection_name or self.collection_name
            logger.debug(f"Executing ChromaDB similarity search on {target_name} (k={k}, filter={filter})")
            
            collection = self._get_collection(collection_name)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filter
            )
            
            # Reformat the results for a standardized interface
            formatted = []
            
            # Chroma returns lists of lists. We iterate over index 0 since we queried 1 vector.
            if results and results.get("ids") and len(results["ids"]) > 0:
                ids = results["ids"][0]
                documents = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0] if results.get("distances") else [0.0] * len(ids)
                
                for idx in range(len(ids)):
                    formatted.append({
                        "id": ids[idx],
                        "document": documents[idx] if idx < len(documents) else "",
                        "metadata": metadatas[idx] if idx < len(metadatas) else {},
                        # In Chroma, smaller distances mean higher similarity.
                        "score": float(distances[idx]) if idx < len(distances) else 0.0
                    })
            return formatted
        except Exception as e:
            logger.error(f"ChromaDB similarity search failed: {e}")
            raise

    def delete_documents(self, ids: List[str], collection_name: str | None = None) -> None:
        try:
            target_name = collection_name or self.collection_name
            logger.info(f"Deleting {len(ids)} documents from ChromaDB collection: {target_name}")
            collection = self._get_collection(collection_name)
            collection.delete(ids=ids)
        except Exception as e:
            logger.error(f"Failed to delete documents from ChromaDB: {e}")
            raise

    def count(self, collection_name: str | None = None) -> int:
        try:
            collection = self._get_collection(collection_name)
            return collection.count()
        except Exception as e:
            logger.error(f"Failed to count ChromaDB documents: {e}")
            raise
