from typing import List, Dict, Any
from app.database.session import SessionLocal
from app.models.movie import Movie
from app.retrieval.interfaces.plugin import BaseRetrievalPlugin
from app.retrieval.contracts.contract import ExecutionStep, RetrievalResult, ProvenanceChain
from app.retrieval.query.query_trace import QueryTrace

class PostgresRetrievalPlugin(BaseRetrievalPlugin):
    """
    Plugin running query execution directly on PostgreSQL relational store.
    """
    @property
    def name(self) -> str:
        return "postgres"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "supports_sql": True,
            "supports_exact_lookup": True,
            "supports_filters": True,
            "supports_metadata": True
        }

    @property
    def dependencies(self) -> List[str]:
        return ["postgresql"]

    async def search(self, step: ExecutionStep, trace: QueryTrace) -> List[RetrievalResult]:
        db = SessionLocal()
        try:
            query_str = step.params.get("query", "")
            filters = step.params.get("filters", {})
            
            q = db.query(Movie)
            
            # Simple metadata filtering matches
            if "movie_id" in filters:
                q = q.filter(Movie.tmdb_id == int(filters["movie_id"]))
            elif query_str:
                # Basic search by title or overview match
                q = q.filter(
                    Movie.title.ilike(f"%{query_str}%") | 
                    Movie.overview.ilike(f"%{query_str}%")
                )
                
            results = q.limit(10).all()
            
            retrieval_results = []
            for movie in results:
                prov = ProvenanceChain(
                    database="postgres",
                    table_or_label="movies",
                    node_id_or_vector_id=str(movie.id),
                    query_executed=str(q.statement),
                    confidence_contribution=0.9
                )
                
                retval = RetrievalResult(
                    source="postgres",
                    entity_type="movie",
                    entity_id=str(movie.tmdb_id),
                    score=1.0,
                    confidence=0.9,
                    provenance=prov,
                    metadata={
                        "title": movie.title,
                        "release_date": str(movie.release_date) if movie.release_date else None,
                        "vote_average": float(movie.vote_average) if movie.vote_average else 0.0,
                        "popularity": float(movie.popularity) if movie.popularity else 0.0
                    },
                    evidence={"overview": movie.overview, "tagline": movie.tagline}
                )
                retrieval_results.append(retval)
                
            return retrieval_results
        finally:
            db.close()
