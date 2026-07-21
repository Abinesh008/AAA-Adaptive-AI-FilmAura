from typing import Dict, Any, List
from app.database.session import SessionLocal
from app.api.deps import get_knowledge_graph, get_vector_store
from app.models.movie import Movie
from app.core.logging import get_logger

logger = get_logger("app.retrieval.integrity")

class IntegrityValidator:
    """
    Validates database synchronization consistency across PostgreSQL, Neo4j, and ChromaDB.
    """
    def run_integrity_check(self) -> Dict[str, Any]:
        logger.info("Executing periodic database layer integrity validations.")
        db = SessionLocal()
        graph = get_knowledge_graph()
        vector = get_vector_store()
        
        postgres_count = 0
        neo4j_count = 0
        chroma_count = 0
        issues: List[str] = []
        
        try:
            # 1. Fetch counts
            postgres_count = db.query(Movie).count()
            
            # Neo4j count
            neo4j_res = graph.execute_query("MATCH (m:Movie) RETURN count(m) AS cnt")
            if neo4j_res:
                neo4j_count = neo4j_res[0].get("cnt", 0)
                
            # Chroma count
            chroma_count = vector.count(collection_name="movie_overviews")
            
            # 2. Check alignment mismatches
            if postgres_count != neo4j_count:
                issues.append(f"Count mismatch: PostgreSQL has {postgres_count} movies but Neo4j has {neo4j_count} nodes.")
            if postgres_count != chroma_count:
                issues.append(f"Count mismatch: PostgreSQL has {postgres_count} movies but ChromaDB has {chroma_count} vectors.")
                
            # 3. Test sample sync checks
            if postgres_count > 0:
                sample_movie = db.query(Movie).first()
                if sample_movie:
                    tmdb_id = sample_movie.tmdb_id
                    
                    # Validate Neo4j has it
                    n_check = graph.execute_query("MATCH (m:Movie {id: $id}) RETURN m", {"id": tmdb_id})
                    if not n_check:
                        issues.append(f"Missing node: Movie '{sample_movie.title}' (ID {tmdb_id}) exists in PostgreSQL but not in Neo4j.")
                        
        except Exception as e:
            logger.error(f"Integrity check failed: {str(e)}")
            issues.append(f"Validation error occurred during execute: {str(e)}")
        finally:
            db.close()
            
        status = "healthy" if not issues else "unreconciled"
        recommendations = []
        if issues:
            recommendations.append("Recommended action: Trigger admin reindex '/api/v1/admin/reindex' to reconcile sync states.")
            
        return {
            "status": status,
            "postgres_movies_count": postgres_count,
            "neo4j_nodes_count": neo4j_count,
            "chromadb_vectors_count": chroma_count,
            "issues_detected": issues,
            "recommendations": recommendations
        }

# Export singleton instance
integrity_validator = IntegrityValidator()
