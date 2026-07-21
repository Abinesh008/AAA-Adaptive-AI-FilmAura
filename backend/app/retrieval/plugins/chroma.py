from typing import List, Dict, Any
from app.api.deps import get_vector_store, get_embedding_provider
from app.retrieval.interfaces.plugin import BaseRetrievalPlugin
from app.retrieval.contracts.contract import ExecutionStep, RetrievalResult, ProvenanceChain
from app.retrieval.query.query_trace import QueryTrace
from app.core.logging import get_logger

logger = get_logger("app.retrieval.plugins.chroma")

class ChromaRetrievalPlugin(BaseRetrievalPlugin):
    """
    Plugin running vector similarity search on ChromaDB.
    """
    @property
    def name(self) -> str:
        return "chromadb"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "supports_vector": True,
            "supports_semantic_search": True
        }

    @property
    def dependencies(self) -> List[str]:
        return ["chromadb", "embeddings"]

    async def search(self, step: ExecutionStep, trace: QueryTrace) -> List[RetrievalResult]:
        vector_store = get_vector_store()
        embedding_provider = get_embedding_provider()
        
        query_str = step.params.get("query", "")
        max_candidates = step.params.get("max_candidates", 5)
        
        if not query_str:
            return []
            
        try:
            # Step 1: Embed query text
            query_vector = embedding_provider.embed_query(query_str)
            
            # Step 2: Query main collection movie_overviews
            matches = vector_store.similarity_search(
                query_embedding=query_vector,
                k=max_candidates,
                collection_name="movie_overviews"
            )
            
            retrieval_results = []
            for match in matches:
                # Chroma similarity matches return 'id', 'document', 'metadata', and distance 'score'
                doc_id = match.get("id")
                score = match.get("score", 1.0)
                document = match.get("document", "")
                metadata = match.get("metadata", {})
                
                tmdb_id = metadata.get("tmdb_id")
                if tmdb_id is None:
                    continue
                    
                prov = ProvenanceChain(
                    database="chromadb",
                    table_or_label="movie_overviews",
                    node_id_or_vector_id=str(doc_id),
                    query_executed="similarity_search",
                    confidence_contribution=0.9
                )
                
                retval = RetrievalResult(
                    source="chromadb",
                    entity_type="movie",
                    entity_id=str(tmdb_id),
                    score=float(score),
                    confidence=0.9,
                    provenance=prov,
                    metadata={
                        "title": metadata.get("title", f"Movie {tmdb_id}"),
                        "distance": float(score)
                    },
                    evidence={"overview": document}
                )
                retrieval_results.append(retval)
                
            return retrieval_results
        except Exception as e:
            logger.error(f"ChromaDB similarity search execution failed: {str(e)}")
            raise e
