from fastapi import APIRouter
from app.api.v1.endpoints import health, ingestion, diagnostics, admin, retrieval, agent

api_router = APIRouter()

# Include version and health check endpoints
api_router.include_router(health.router, prefix="/system", tags=["system"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(diagnostics.router, prefix="/system/diagnostics", tags=["diagnostics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["retrieval"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
