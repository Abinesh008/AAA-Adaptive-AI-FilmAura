from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.api import deps
from app.schemas.common import StatusResponse
from app.ingestion.pipeline import MovieIngestionPipeline
from app.ingestion.providers.tmdb import TMDbMovieProvider
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.vector import BaseVectorStore
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("app.api.v1.endpoints.ingestion")

class IngestionRequest(BaseModel):
    movie_ids: List[str] = []
    popular_limit: int = 0
    provider: str = "tmdb"  # tmdb, omdb, etc.

def run_ingestion_background(
    request: IngestionRequest,
    db: Session,
    graph: BaseKnowledgeGraph,
    vector: BaseVectorStore,
    embedding: BaseEmbeddingProvider
):
    """
    Background worker executing the ingestion process.
    """
    logger.info("Background ingestion task started...")
    
    # 1. Resolve provider (currently only TMDB is implemented)
    if request.provider.lower() == "tmdb":
        movie_provider = deps.get_llm_provider()  # Wait, let's instantiate TMDbMovieProvider directly or resolve it
        movie_provider = TMDbMovieProvider()
    else:
        logger.warning(f"Unknown provider '{request.provider}', defaulting to TMDbProvider.")
        movie_provider = TMDbMovieProvider()

    # 2. Instantiate pipeline
    try:
        pipeline = MovieIngestionPipeline(
            db=db,
            graph_db=graph,
            vector_store=vector,
            embedding_provider=embedding,
            provider=movie_provider
        )

        # 3. Run Ingestion based on parameters
        if request.movie_ids:
            logger.info(f"Ingesting specific movie IDs: {request.movie_ids}")
            for mid in request.movie_ids:
                try:
                    pipeline.ingest_movie_by_id(mid)
                except Exception as e:
                    logger.error(f"Failed to ingest movie ID {mid} in background: {e}")
        elif request.popular_limit > 0:
            logger.info(f"Ingesting popular movies batch (limit={request.popular_limit})")
            pipeline.ingest_popular_movies(limit=request.popular_limit)
        else:
            logger.warning("Ingestion triggered with empty parameters.")
            
        logger.info("Background ingestion task completed successfully.")
    except Exception as e:
        logger.exception(f"Fatal error in background ingestion pipeline: {e}")

@router.post("/trigger", response_model=StatusResponse, summary="Trigger Ingestion Pipeline")
def trigger_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    graph: BaseKnowledgeGraph = Depends(deps.get_knowledge_graph),
    vector: BaseVectorStore = Depends(deps.get_vector_store),
    embedding: BaseEmbeddingProvider = Depends(deps.get_embedding_provider)
) -> StatusResponse:
    """
    Asynchronously trigger the movie ingestion pipeline.
    """
    if not request.movie_ids and request.popular_limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either movie_ids or a popular_limit greater than 0."
        )

    # Add ingestion run to FastAPI BackgroundTasks
    background_tasks.add_task(
        run_ingestion_background,
        request,
        db,
        graph,
        vector,
        embedding
    )

    return StatusResponse(
        success=True,
        message="Movie ingestion pipeline triggered successfully in the background."
    )
