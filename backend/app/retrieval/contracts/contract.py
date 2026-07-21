from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class QueryIntent(BaseModel):
    query: str
    normalized_query: str
    primary_intent: str  # e.g., "identify", "recommend", "comparison", "qa"
    entities: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False

class ExecutionStep(BaseModel):
    plugin_name: str
    capability: str
    params: Dict[str, Any] = Field(default_factory=dict)
    estimated_cost: float = 0.0

    class Config:
        allow_mutation = False

class ExecutionPlan(BaseModel):
    steps: List[ExecutionStep]
    strategy: str
    total_estimated_cost: float

    class Config:
        allow_mutation = False

class ProvenanceChain(BaseModel):
    database: str
    table_or_label: Optional[str] = None
    node_id_or_vector_id: Optional[str] = None
    query_executed: Optional[str] = None
    confidence_contribution: float = 1.0

    class Config:
        allow_mutation = False

class RetrievalResult(BaseModel):
    source: str  # e.g., "postgres", "neo4j", "chromadb"
    entity_type: str  # e.g., "movie", "cast", "scene", "theme"
    entity_id: str  # tmdb_id or internal ID
    score: float
    confidence: float
    provenance: ProvenanceChain
    metadata: Dict[str, Any] = Field(default_factory=dict)
    evidence: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False

class CandidateMovie(BaseModel):
    tmdb_id: int
    title: str
    score: float
    confidence: float
    matched_by_sources: List[str]
    provenance_details: List[ProvenanceChain] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False

class FusionResult(BaseModel):
    candidates: List[CandidateMovie]
    fusion_algorithm: str

    class Config:
        allow_mutation = False

class RankingResult(BaseModel):
    candidates: List[CandidateMovie]
    reranking_strategy: str

    class Config:
        allow_mutation = False

class ReasoningContext(BaseModel):
    prompt: str
    context_str: str
    token_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False

class FinalResponse(BaseModel):
    answer: str
    movies: List[CandidateMovie] = Field(default_factory=list)
    trace_id: str
    api_version: str = "1.0.0"
    retrieval_version: str = "1.0.0"
    confidence_score: float = 1.0
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    explanation: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False
