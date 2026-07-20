from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import setup_middlewares
from app.core.exceptions import setup_exception_handlers
from app.api.v1.router import api_router
from app.api import deps

# Setup logging immediately
setup_logging()
logger = get_logger("app.main")

# Validate required variables immediately at boot
from app.core.env_validation import validate_environment
validate_environment()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    logger.info(f"Starting {settings.APP_NAME}...")
    logger.info(f"Environment Profile: {settings.APP_ENV}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    # Pre-initialize singletons and pre-warm connections (logged, won't block startup)
    logger.info("Initializing connection pools and client singletons...")
    deps.get_llm_provider()
    deps.get_embedding_provider()
    deps.get_vector_store()
    deps.get_knowledge_graph()
    deps.get_cache_manager()
    
    logger.info("Application initialization complete. Ready to receive requests.")
    yield
    
    # Shutdown Events
    logger.info(f"Shutting down {settings.APP_NAME}...")
    # Cleanly close database and graph sessions
    try:
        deps.get_knowledge_graph().close()
        logger.info("Knowledge Graph driver closed successfully.")
    except Exception as e:
        logger.error(f"Failed to cleanly close Knowledge Graph driver: {e}")
        
    logger.info("Application shutdown complete.")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Adaptive AI FilmAura - Beyond Genres. Into Memories. (Backend platform)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Apply Middlewares
setup_middlewares(app)

# Apply Global Exception Handlers
setup_exception_handlers(app)

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

import time
from fastapi import Response, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.interfaces.vector import BaseVectorStore
from app.core.metrics import get_metrics_payload

@app.get("/", summary="Root Entrypoint")
def home():
    """
    Root endpoint welcome greeting.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} 🚀",
        "documentation": "/docs",
        "system_health": "/health"
    }

@app.get("/live", summary="Liveness Probe")
def liveness():
    """
    Returns alive confirmation for container orchestrators.
    """
    return {"status": "alive"}

@app.get("/ready", summary="Readiness Probe")
def readiness(db: Session = Depends(deps.get_db)):
    """
    Verifies relational database connections are ready to process queries.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check: PostgreSQL is unreachable: {e}")
        raise HTTPException(status_code=503, detail="Database connection refused.")

@app.get("/health", summary="Overall Health Diagnostics Check")
def health_check(
    db: Session = Depends(deps.get_db),
    graph: BaseKnowledgeGraph = Depends(deps.get_knowledge_graph),
    vector: BaseVectorStore = Depends(deps.get_vector_store)
):
    """
    Consolidates connectivity statuses across databases.
    """
    postgres_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        postgres_status = "connected"
    except Exception:
        pass

    neo4j_status = "disconnected"
    try:
        if graph.check_connection():
            neo4j_status = "connected"
    except Exception:
        pass

    chromadb_status = "disconnected"
    try:
        vector.count()
        chromadb_status = "connected"
    except Exception:
        pass

    redis_status = "disconnected"
    try:
        from app.core.providers.cache.redis import RedisCacheManager
        cache_manager = deps.get_cache_manager()
        if isinstance(cache_manager, RedisCacheManager) and cache_manager._client and not cache_manager._fallback:
            cache_manager._client.ping()
            redis_status = "connected"
    except Exception:
        pass

    is_healthy = postgres_status == "connected" and neo4j_status == "connected" and chromadb_status == "connected"
    overall_status = "healthy" if is_healthy else "degraded"

    return {
        "status": overall_status,
        "postgres": postgres_status,
        "neo4j": neo4j_status,
        "chromadb": chromadb_status,
        "redis": redis_status
    }

@app.get("/version", summary="Retrieve Platform Version Metadata")
def version_metadata():
    """
    Returns app release details, git commits, and build timings.
    """
    import subprocess
    git_commit = "unknown"
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except Exception:
        pass

    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "release_version": "v6.0.0",
        "git_commit": git_commit,
        "environment": settings.APP_ENV,
        "timestamp": int(time.time())
    }

@app.get("/metrics", summary="Prometheus Scraping Target")
def metrics():
    """
    Exposes application metrics for Prometheus scraping runs.
    """
    payload, content_type = get_metrics_payload()
    return Response(content=payload, media_type=content_type)