from pydantic import BaseModel
from typing import Dict, Any

class StatusResponse(BaseModel):
    """
    Standard generic status response shape.
    """
    success: bool
    message: str
    data: Dict[str, Any] | None = None

class VersionResponse(BaseModel):
    """
    Application version info response shape.
    """
    app_name: str
    version: str
    environment: str
    debug: bool

class HealthResponse(BaseModel):
    """
    Diagnostic connection health status shape.
    """
    status: str  # "healthy" or "degraded"
    postgres: str  # "connected" or "disconnected"
    neo4j: str  # "connected" or "disconnected"
    chromadb: str  # "connected" or "disconnected"

class ErrorDetail(BaseModel):
    """
    Error detail mapping.
    """
    code: str
    message: str
    details: Dict[str, Any] | None = None
