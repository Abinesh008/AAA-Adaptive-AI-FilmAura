from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.api import deps
from app.schemas.common import StatusResponse
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.vector import BaseVectorStore
from app.core.interfaces.embedding import BaseEmbeddingProvider
from app.services.ingestion import IngestionService

router = APIRouter()

class IngestionRequest(BaseModel):
    movie_ids: List[str] = []
    popular_limit: int = 0
    provider: str = "tmdb"  # tmdb, omdb, etc.

@router.post("/trigger", response_model=StatusResponse, summary="Trigger Ingestion Pipeline")
def trigger_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    graph: BaseKnowledgeGraph = Depends(deps.get_knowledge_graph),
    vector: BaseVectorStore = Depends(deps.get_vector_store),
    embedding: BaseEmbeddingProvider = Depends(deps.get_embedding_provider),
    service: IngestionService = Depends(deps.get_ingestion_service)
) -> StatusResponse:
    """
    Asynchronously trigger the movie ingestion pipeline.
    """
    if not request.movie_ids and request.popular_limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either movie_ids or a popular_limit greater than 0."
        )

    # Delegate backround scheduling to IngestionService
    service.trigger_ingestion(
        movie_ids=request.movie_ids,
        popular_limit=request.popular_limit,
        provider=request.provider,
        db=db,
        graph=graph,
        vector=vector,
        embedding=embedding,
        background_tasks=background_tasks
    )

    return StatusResponse(
        success=True,
        message="Movie ingestion pipeline triggered successfully in the background."
    )
