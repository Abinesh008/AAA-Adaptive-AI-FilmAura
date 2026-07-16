from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.api import deps
from app.database.session import get_db
from app.models.movie import *
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.vector import BaseVectorStore
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("app.api.v1.endpoints.diagnostics")

@router.get("/stats", summary="Query Database, Graph, and Vector Statistics")
def get_stats(
    db: Session = Depends(deps.get_db),
    graph: BaseKnowledgeGraph = Depends(deps.get_knowledge_graph),
    vector: BaseVectorStore = Depends(deps.get_vector_store)
) -> Dict[str, Any]:
    """
    Returns diagnostic statistics across all databases: PostgreSQL, Neo4j, and ChromaDB.
    """
    logger.info("Executing diagnostics stats fetch...")
    
    # 1. PostgreSQL Relational Counts
    postgres_stats = {}
    try:
        postgres_stats = {
            "movies_count": db.query(Movie).count(),
            "genres_count": db.query(Genre).count(),
            "keywords_count": db.query(Keyword).count(),
            "people_count": db.query(Person).count(),
            "cast_roles_count": db.query(MovieCast).count(),
            "crew_roles_count": db.query(MovieCrew).count(),
            "studios_count": db.query(Studio).count(),
            "themes_count": db.query(Theme).count(),
            "emotions_count": db.query(Emotion).count(),
            "moods_count": db.query(Mood).count(),
            "scenes_count": db.query(Scene).count(),
            "dialogues_count": db.query(Dialogue).count(),
            "awards_count": db.query(Award).count(),
            "reviews_count": db.query(Review).count()
        }
    except Exception as e:
        logger.error(f"Failed to query Postgres stats: {e}")
        postgres_stats = {"error": str(e)}

    # 2. Neo4j Graph Database Counts
    neo4j_stats = {}
    try:
        # Check node counts by label
        node_counts_query = "MATCH (n) RETURN labels(n)[0] as label, count(n) as count"
        node_counts = graph.execute_query(node_counts_query)
        labels_map = {item.get("label", "Unknown"): item.get("count", 0) for item in node_counts}
        
        # Check relationship counts by type
        rel_counts_query = "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count"
        rel_counts = graph.execute_query(rel_counts_query)
        rels_map = {item.get("type", "Unknown"): item.get("count", 0) for item in rel_counts}
        
        # Total counts
        total_nodes = graph.execute_query("MATCH (n) RETURN count(n) as count")[0].get("count", 0)
        total_rels = graph.execute_query("MATCH ()-[r]->() RETURN count(r) as count")[0].get("count", 0)
        
        neo4j_stats = {
            "total_nodes": total_nodes,
            "total_relationships": total_rels,
            "node_counts_by_label": labels_map,
            "relationship_counts_by_type": rels_map
        }
    except Exception as e:
        logger.error(f"Failed to query Neo4j stats: {e}")
        neo4j_stats = {"error": str(e)}

    # 3. ChromaDB Vector Database Counts
    chroma_stats = {}
    try:
        collections = ["movie_overviews", "characters", "scenes", "dialogues", "themes", "memory_cues", "visual_cues"]
        collection_counts = {}
        for col in collections:
            try:
                collection_counts[col] = vector.count(collection_name=col)
            except Exception as col_err:
                collection_counts[col] = f"Error: {col_err}"
                
        chroma_stats = {
            "collection_counts": collection_counts
        }
    except Exception as e:
        logger.error(f"Failed to query ChromaDB stats: {e}")
        chroma_stats = {"error": str(e)}

    return {
        "status": "success",
        "postgresql": postgres_stats,
        "neo4j": neo4j_stats,
        "chromadb": chroma_stats
    }

@router.get("/history", summary="Query Ingestion Sync History")
def get_history(
    db: Session = Depends(deps.get_db)
) -> Dict[str, Any]:
    """
    Returns history of recently ingested movies and sync timestamps.
    """
    try:
        movies = db.query(Movie).order_by(Movie.last_synced_at.desc()).limit(20).all()
        history = []
        for m in movies:
            history.append({
                "movie_id": m.tmdb_id,
                "title": m.title,
                "release_year": m.release_year,
                "imdb_id": m.imdb_id,
                "wikidata_id": m.wikidata_id,
                "tvdb_id": m.tvdb_id,
                "last_synced_at": m.last_synced_at.isoformat() if m.last_synced_at else None
            })
            
        return {
            "status": "success",
            "count": len(history),
            "ingested_movies": history
        }
    except Exception as e:
        logger.error(f"Failed to query ingestion history: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

from app.retrieval.registry import capability_registry
from app.retrieval.features import features
from app.retrieval.strategy_learning import strategy_learning_engine
from app.retrieval.analytics import retrieval_analytics
from app.retrieval.session_store import session_store
from app.retrieval.integrity import integrity_validator

@router.get("/retrieval", summary="Query Retrieval Layer Diagnostics")
def get_retrieval_diagnostics() -> Dict[str, Any]:
    """
    Returns retrieval analytics, capabilities, health states, feature states, and integrity reports.
    """
    return {
        "status": "success",
        "version_manifest": {
            "retrieval_version": "1.0.0",
            "schema_version": "1.0.0"
        },
        "feature_states": {f: features.get_state(f).value for f in ["query_rewrite", "query_expansion", "graph_search", "vector_search", "sql_search", "reranking", "reasoning", "cache", "diversity", "explainability", "streaming"]},
        "capabilities_matrix": capability_registry.get_all_manifests(),
        "strategy_learning": strategy_learning_engine.get_all_stats(),
        "analytics": retrieval_analytics.get_diagnostics_metrics(),
        "integrity_report": integrity_validator.run_integrity_check(),
        "recent_sessions": [s.trace_id for s in session_store.get_recent_sessions(10)]
    }
