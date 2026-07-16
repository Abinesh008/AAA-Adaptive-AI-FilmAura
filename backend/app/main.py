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

@app.get("/", summary="Root Entrypoint")
def home():
    """
    Root endpoint welcome greeting.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} 🚀",
        "documentation": "/docs",
        "system_health": f"{settings.API_V1_STR}/system/health"
    }