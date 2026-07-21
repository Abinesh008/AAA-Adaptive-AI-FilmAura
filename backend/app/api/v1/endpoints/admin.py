from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.api import deps
from app.database.session import SessionLocal
from app.models.movie import Movie
from app.services.reconciliation import ReconciliationService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("app.api.admin")

class ReindexRequest(BaseModel):
    movie_ids: Optional[List[str]] = None

@router.post("/reindex")
def trigger_reindex(
    payload: Optional[ReindexRequest] = None,
    background_tasks: BackgroundTasks = None,
    graph_db = Depends(deps.get_knowledge_graph),
    vector_store = Depends(deps.get_vector_store),
    embedding = Depends(deps.get_embedding_provider)
):
    """
    Rebuilds Neo4j Graph nodes/links and ChromaDB vectors using existing PostgreSQL records.
    """
    movie_ids = payload.movie_ids if payload else None
    
    def run_reindex_job():
        bg_db = SessionLocal()
        try:
            bg_recon = ReconciliationService(bg_db, graph_db, vector_store, embedding)
            if movie_ids:
                movies_to_reindex = bg_db.query(Movie).filter(Movie.tmdb_id.in_(movie_ids)).all()
            else:
                movies_to_reindex = bg_db.query(Movie).all()
            
            logger.info(f"Re-indexing batch job started for {len(movies_to_reindex)} movies...")
            for m in movies_to_reindex:
                try:
                    logger.info(f"Re-indexing: '{m.title}' (ID: {m.tmdb_id})")
                    bg_recon.repair_movie(m)
                except Exception as ex:
                    logger.exception(f"Failed to re-index movie '{m.title}': {ex}")
            logger.info("Re-indexing batch job completed.")
        finally:
            bg_db.close()

    background_tasks.add_task(run_reindex_job)
    return {
        "status": "success", 
        "message": f"Reindexing for {len(movie_ids) if movie_ids else 'all'} movies triggered in the background."
    }

@router.delete("/movie/{movie_id}")
def delete_movie(
    movie_id: str,
    db: Session = Depends(deps.get_db),
    graph_db = Depends(deps.get_knowledge_graph),
    vector_store = Depends(deps.get_vector_store)
):
    """
    Completely deletes a movie from PostgreSQL, Neo4j, and ChromaDB.
    """
    logger.info(f"Administrative request to delete movie ID: {movie_id}")
    
    # 1. Query movie from PostgreSQL
    db_movie = db.query(Movie).filter(Movie.tmdb_id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found in PostgreSQL.")
        
    title = db_movie.title
    
    # 2. Delete from PostgreSQL (cascades to all children)
    db.delete(db_movie)
    db.commit()
    logger.info(f"Deleted movie '{title}' from PostgreSQL (cascading complete).")
    
    # 3. Delete from Neo4j
    try:
        graph_db.execute_query("MATCH (m:Movie {id: $movie_id}) DETACH DELETE m", {"movie_id": movie_id})
        
        # Clean up orphaned nodes
        graph_db.execute_query("MATCH (p:Person) WHERE NOT (p)<-[:ACTED_IN|DIRECTED|PRODUCED|WROTE|COMPOSED]-() DELETE p")
        graph_db.execute_query("MATCH (t:Theme) WHERE NOT ()-[:HAS_THEME]->(t) DELETE t")
        graph_db.execute_query("MATCH (mo:Mood) WHERE NOT ()-[:HAS_MOOD]->(mo) DELETE mo")
        graph_db.execute_query("MATCH (e:Emotion) WHERE NOT ()-[:HAS_EMOTION]->(e) DELETE e")
        graph_db.execute_query("MATCH (k:Keyword) WHERE NOT ()-[:HAS_KEYWORD]->(k) DELETE k")
        graph_db.execute_query("MATCH (mc:MemoryCue) WHERE NOT ()-[:HAS_MEMORY_CUE]->(mc) DELETE mc")
        graph_db.execute_query("MATCH (vc:VisualCue) WHERE NOT ()-[:HAS_VISUAL_CUE]->(vc) DELETE vc")
        logger.info(f"Deleted movie '{title}' node and connections from Neo4j.")
    except Exception as e:
        logger.error(f"Failed to delete movie '{title}' from Neo4j: {e}")
        
    # 4. Delete vectors from ChromaDB collections
    collections = ["movie_overviews", "characters", "scenes", "dialogues", "themes", "memory_cues", "visual_cues"]
    for col in collections:
        try:
            if hasattr(vector_store, "_get_collection"):
                collection = vector_store._get_collection(col)
                collection.delete(where={"movie_id": movie_id})
                logger.info(f"Deleted movie '{title}' vectors from ChromaDB collection: {col}")
        except Exception as e:
            logger.error(f"Failed to delete movie '{title}' vectors from collection '{col}': {e}")
            
    return {
        "status": "success", 
        "message": f"Movie '{title}' (ID: {movie_id}) completely removed from all storage layers."
    }

@router.post("/reconcile")
def trigger_reconciliation(
    background_tasks: BackgroundTasks,
    graph_db = Depends(deps.get_knowledge_graph),
    vector_store = Depends(deps.get_vector_store),
    embedding = Depends(deps.get_embedding_provider)
):
    """
    Verifies database consistency across PostgreSQL, Neo4j, and ChromaDB, repairing missing components.
    """
    def run_reconciliation_job():
        bg_db = SessionLocal()
        try:
            bg_recon = ReconciliationService(bg_db, graph_db, vector_store, embedding)
            bg_recon.reconcile_all_movies()
        finally:
            bg_db.close()
            
    background_tasks.add_task(run_reconciliation_job)
    return {
        "status": "success", 
        "message": "Background database reconciliation task started."
    }
