from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps
from app.schemas.common import HealthResponse, VersionResponse
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.vector import BaseVectorStore
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("app.api.v1.endpoints.health")

@router.get("/health", response_model=HealthResponse, summary="Perform System Diagnostic Checkups")
def get_health(
    db: Session = Depends(deps.get_db),
    graph: BaseKnowledgeGraph = Depends(deps.get_knowledge_graph),
    vector: BaseVectorStore = Depends(deps.get_vector_store)
) -> HealthResponse:
    """
    Check the connectivity status of PostgreSQL, Neo4j, and ChromaDB.
    """
    # 1. Check PostgreSQL connection
    postgres_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        postgres_status = "connected"
    except Exception as e:
        logger.error(f"Health check: PostgreSQL is unreachable: {e}")

    # 2. Check Neo4j connection
    neo4j_status = "disconnected"
    try:
        if graph.check_connection():
            neo4j_status = "connected"
    except Exception as e:
        logger.error(f"Health check: Neo4j is unreachable: {e}")

    # 3. Check ChromaDB connection
    chromadb_status = "disconnected"
    try:
        # Check by executing count
        vector.count()
        chromadb_status = "connected"
    except Exception as e:
        logger.error(f"Health check: ChromaDB is unreachable: {e}")

    # Determine overall status
    is_healthy = (
        postgres_status == "connected" and 
        neo4j_status == "connected" and 
        chromadb_status == "connected"
    )
    overall_status = "healthy" if is_healthy else "degraded"

    return HealthResponse(
        status=overall_status,
        postgres=postgres_status,
        neo4j=neo4j_status,
        chromadb=chromadb_status
    )

@router.get("/version", response_model=VersionResponse, summary="Get Platform Version Information")
def get_version() -> VersionResponse:
    """
    Retrieve application version and current operational environment.
    """
    return VersionResponse(
        app_name=settings.APP_NAME,
        version="1.0.0",
        environment=settings.APP_ENV,
        debug=settings.DEBUG
    )
