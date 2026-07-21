from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Evidence(BaseModel):
    """
    Representation of a single query matching signal mapped across SQL, Graph, or Vector databases.
    """
    origin_plugin: str
    evidence_type: str  # e.g., "overview", "scene", "dialogue", "theme", "relationship"
    score: float
    confidence: float
    matched_entity: str  # Name or identifier
    metadata: Dict[str, Any] = Field(default_factory=dict)
    retrieval_latency: float = 0.0
    raw_document_reference: Optional[str] = None
    citations: List[str] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())

    class Config:
        allow_mutation = False
